"""Integrate the experimental exact-straight-path VSL with real terrain contact.

Run app .venv Python contact_dynamics.py --request-stdin with the complete JSON
builder (mm/deg/kg/N), runConfig (s/SI torque) and explicit contactConfig. Returns
kinefold/contact-v1 world-mm frames, actual two-body states/contact impulses and
diagnostics. Pymunk uses metres, kg, seconds, source-horizontal-right/up axes.
Only equal links/2:1 hip ratio, massless links, uniform positive-mass disc wheel,
vertical nonpitching chassis and freely backdrivable ideal belts are supported.
Rigid sharp terrain/Coulomb friction is experimental, not a tire/hardware model.
"""
import argparse
import json
import math
import sys

from dynamic_model import Model, R, mul, validate, finite


class ContactGeometry(Model):
    """Reuse exact VSL geometry/spring helpers, never prescribed-input dynamics."""

    def __init__(self, params, config):
        validate(params, config)
        p, c = dict(params), dict(config)
        if p['m1'] <= 0 or p['m6'] <= 0:
            raise ValueError('Terrain contact requires positive explicit m1 and m6; no mass is substituted.')
        if any(p[k] != 0 for k in ('m2', 'm3', 'm5')):
            raise ValueError('Terrain contact supports massless links/idler only: m2=m3=m5=0.')
        if c['inertiaModel'] != 'uniform-rods-discs' or any(c[k] != 0 for k in ('I2', 'I3', 'I5', 'I6', 'hipRotorInertiaKgM2')):
            raise ValueError('Terrain contact requires uniform wheel-disc inertia and zero additional/custom/rotor inertia.')
        if abs(p['L2'] - p['L3']) > 1e-10 or abs(p['ra'] / p['rb'] - 2) > 1e-12:
            raise ValueError('Terrain contact requires certified straight travel: equal L2/L3 and ra/rb=2. Curved guide geometry is unsupported.')
        if c['inputRiseMm'] != 0:
            raise ValueError('Terrain contact uses sharp square polygons; inputRiseMm must be zero.')
        if p['loadMode'] == 'contact':
            raise ValueError('Prescribed contact loads are unsupported with actual contact. Use weight or explicit global additional loads.')
        if p['te'] == p['tc']:
            raise ValueError('Terrain contact requires a nonempty monotonic working range.')
        self.p, self.c = p, c
        self.q0, self.lo, self.hi = p['theta2'] * R, p['te'] * R, p['tc'] * R
        self.ab, self.dc, self.fe = p['ra'] / p['rb'], p['rd'] / p['rc'], p['rf'] / p['re']
        self.k3, self.k5 = 1-self.ab, 1-1/self.dc
        self.K = 1-self.ab+(self.ab-1/self.dc)/self.fe
        self.mean = (math.pi + p['phi0']*R)/2
        # C(q) = axis * 2L cos(q-mean), identically, including alpha/phi0.
        self.axis = self.rotate((-math.cos(self.mean), -math.sin(self.mean)))
        for n in range(-2, 4):
            if self.lo-1e-10 <= self.mean+n*math.pi <= self.hi+1e-10:
                raise ValueError('Straight-path Jacobian is singular or changes sign in the working range; move te/tc away from the turning point.')
        self.branch = 1 if self.q0-self.mean > 0 else -1
        self.jacobian_min = min(abs(self.jacobian(q)) for q in (self.lo,self.hi))
        if self.jacobian_min < 1e-7:
            raise ValueError('Straight guide Jacobian is too close to zero for this contact model.')
        self.route = self.exit_route() if p['springEnabled'] else dict(applied=0, shift=0)
        self.reference_payout = self.geometry(math.pi/2, reference=True)['payout'] if p['springEnabled'] else 0
        if p['springEnabled']:
            for q in self.candidates(self.lo,self.hi):
                self.geometry(q)
        self.force, self.Mw = self.loads()
        self.I = {'2':0., '3':0., '5':0., '6':.5*p['m6']*(p['rw']/1000)**2}

    def distance(self,q):
        return 2*self.p['L2']/1000*math.cos(q-self.mean)

    def jacobian(self,q):
        return -2*self.p['L2']/1000*math.sin(q-self.mean)

    def inverse(self,distance):
        u = distance/(2*self.p['L2']/1000)
        if abs(u) > 1+1e-12:
            raise ValueError('Actual wheel/chassis separation exceeds the exact VSL geometric domain.')
        return self.mean+self.branch*math.acos(max(-1,min(1,u)))

    def internal_force(self,q,qd):
        """Actual equal/opposite guide force, no gravity or contact duplication."""
        Q = self.spring(q)['torque']+self.c['hipTorqueNm']-self.c['dampingNms']*qd
        return Q/self.jacobian(q)


def validate_contact_request(payload):
    if not isinstance(payload,dict) or set(payload) != {'engine','params','runConfig','contactConfig'}:
        raise ValueError('Contact request requires exactly engine, params, runConfig and contactConfig.')
    if payload['engine'] != 'pymunk':
        raise ValueError('Terrain contact is available only in Pymunk.')
    cc = payload['contactConfig']
    if not isinstance(cc,dict) or set(cc) != {'mode','friction','restitution','drive'}:
        raise ValueError('contactConfig requires exactly mode, friction, restitution and drive.')
    if cc['mode'] != 'terrain-contact' or cc['drive'] != 'free':
        raise ValueError('Contact mode must be terrain-contact with freely backdrivable drive=free.')
    if not finite(cc['friction']) or not 0 <= cc['friction'] <= 2:
        raise ValueError('Contact friction must be finite within [0,2].')
    if not finite(cc['restitution']) or cc['restitution'] != 0:
        raise ValueError('This contact model requires zero restitution.')
    return ContactGeometry(payload['params'],payload['runConfig'])


def _world(v):
    return [-v[0]*1000,0,v[1]*1000]


def simulate_contact(payload):
    import pymunk
    m=validate_contact_request(payload)
    p,c,cc=m.p,m.c,dict(payload['contactConfig'])
    space=pymunk.Space();space.gravity=(0,-p['g']);space.iterations=int(c['iterations'])
    # SI tolerances are explicit, not epsilon masses or tire compliance.
    space.collision_slop=1e-6
    space.collision_bias=(1-.2)**60
    radius=p['rw']/1000
    C0=m.sites(m.q0)['6'][0]
    chassis=pymunk.Body(p['m1'],math.inf)
    chassis.position=(0,radius-C0[1])
    qd0=c['initialVelocityDegS']*R
    chassis.velocity=(0,-m.sites(m.q0)['6'][1][1]*qd0)
    wheel=pymunk.Body(p['m6'],m.I['6']);wheel.position=(C0[0],radius)
    wheel.angle=(m.K*(p['theta2']-p['te'])-p['alpha'])*R
    # qdot is independent relative-guide motion. Initially wheel z velocity=0;
    # guide tangent sets the horizontal wheel component without locking spin.
    wheel.velocity=(m.sites(m.q0)['6'][1][0]*qd0,0)
    ground=pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    speed=c['inputSpeedMmS']/1000;ground.velocity=(speed,0)
    space.add(chassis,wheel,ground)
    heave=pymunk.GrooveJoint(space.static_body,chassis,(0,-1000),(0,1000),(0,0))
    # Infinite straight guide, terminated at declared working travel; endpoints
    # never introduce an undeclared joint-stop impact response.
    guide=pymunk.GrooveJoint(chassis,wheel,mul(m.axis,-1000),mul(m.axis,1000),(0,0))
    heave.collide_bodies=guide.collide_bodies=False
    space.add(heave,guide)
    wheel_shape=pymunk.Circle(wheel,radius);wheel_shape.friction=cc['friction'];wheel_shape.elasticity=0
    wheel_shape.collision_type=1;wheel_shape.filter=pymunk.ShapeFilter(categories=1,mask=2)
    space.add(wheel_shape)
    height=c['inputHeightMm']/1000;width=c['inputPlateauMm']/1000;gap=c['inputGapMm']/1000
    corner=math.sqrt(max(0,2*radius*height-height*height)) if height<=2*radius else 0
    clearance=0 if height==0 else (radius if height>=radius else corner)
    front=C0[0]-clearance-speed*c['inputDelayS']
    count=math.ceil((speed*c['duration']+4*radius)/(width+gap))+3
    boxes=[];shapes=[]
    for i in range(count):
        if height==0:break
        right=front-i*(width+gap);left=right-width
        vertices=[(left,0),(right,0),(right,height),(left,height)]
        shape=pymunk.Poly(ground,vertices,radius=0);boxes.append(vertices);shapes.append(shape)
    extent=abs(C0[0])+speed*c['duration']+count*(width+gap)+10
    base=[(-extent,0),(extent,0)]
    shapes.append(pymunk.Segment(ground,*base,0))
    for shape in shapes:
        shape.friction=1;shape.elasticity=0;shape.collision_type=2
        shape.filter=pymunk.ShapeFilter(categories=2,mask=1)
        space.add(shape)
    impulse=[];points=[];slips=[];normal_impulses=[];tangent_impulses=[]
    def post_solve(arbiter,_space,_data):
        # Handler ordering is wheel first; total_impulse acts on first body.
        J=arbiter.total_impulse;n=arbiter.normal
        impulse.append((J.x,J.y));normal_impulses.append(abs(J.dot(n)))
        tangent_impulses.append(abs(J.cross(n)))
        for cp in arbiter.contact_point_set.points:
            point=cp.point_a;points.append(_world(point))
            v=wheel.velocity_at_world_point(point)-ground.velocity_at_world_point(point)
            slips.append(v.dot(pymunk.Vec2d(-n.y,n.x))*1000)
    space.on_collision(1,2,post_solve=post_solve)
    terrain=dict(polygonsMm=[[_world(v) for v in box] for box in boxes],baseSegmentMm=[_world(v) for v in base],
                 translationVelocityMmS=[-speed*1000,0,0],cornerRadiusMm=0,
                 firstContactClearanceMm=clearance*1000,upperCornerClearanceMm=corner*1000,
                 initialFrontEdgeXMm=-front*1000,initialPossibleContactTimeS=c['inputDelayS'],
                 heightMm=height*1000,plateauMm=width*1000,gapMm=gap*1000,
                 wheelAngleZeroDirection='-x',coordinates='Kinefold +x left / +z up, mm')
    rows=[];frames=[];events=[];t=0.;next_sample=1/c['outputHz'];steps=0;termination='duration'
    sample_time=0.;totalJ=[0.,0.];totalN=0.;totalT=0.;sample_points=[];sample_slips=[]
    actuator_work=0.;max_residual=0.;max_penetration=0.;max_N=0.;max_T=0.;first_raised=None
    penetration_limit_mm=1.
    def state():
        relative=wheel.position-chassis.position
        q=m.inverse(relative.dot(pymunk.Vec2d(*m.axis)))
        qd=(wheel.velocity-chassis.velocity).dot(pymunk.Vec2d(*m.axis))/m.jacobian(q)
        exact=m.sites(q)['6'][0]
        residual=math.hypot(relative.x-exact[0],relative.y-exact[1])*1000
        return q,qd,residual
    def separation():
        # Signed closest distance to the exact union of base and raised boxes.
        pos=wheel.position;offset=ground.position.x
        distance=pos.y
        for box in boxes:
            left,right=box[0][0]+offset,box[1][0]+offset
            dx=max(left-pos.x,0,pos.x-right);dy=max(-pos.y,0,pos.y-height)
            if dx==0 and dy==0:
                d=-min(pos.x-left,right-pos.x,pos.y,height-pos.y)
            else:d=math.hypot(dx,dy)
            distance=min(distance,d)
        return (distance-radius)*1000
    def append():
        nonlocal sample_time,totalN,totalT,max_residual,max_penetration,max_N,max_T
        q,qd,residual=state();spring=m.spring(q);elapsed=t-sample_time
        nf=totalN/elapsed if elapsed>0 else 0.;tf=totalT/elapsed if elapsed>0 else 0.
        fx=-totalJ[0]/elapsed if elapsed>0 else 0.;fz=totalJ[1]/elapsed if elapsed>0 else 0.
        gapmm=separation();penetration=max(0,-gapmm)
        max_residual=max(max_residual,residual);max_penetration=max(max_penetration,penetration)
        max_N=max(max_N,nf);max_T=max(max_T,tf)
        kinetic=.5*chassis.mass*chassis.velocity.length_squared+.5*wheel.mass*wheel.velocity.length_squared+.5*wheel.moment*wheel.angular_velocity**2
        potential=p['g']*(chassis.mass*chassis.position.y+wheel.mass*wheel.position.y)+spring['energy']
        theta6=wheel.angle/R+p['alpha'];theta4=m.dc*m.fe*(theta6-m.K*(q/R-p['te']))
        theta5=(1-1/m.dc)*(q/R-p['te'])+theta4/m.dc
        A,C=_world(chassis.position),_world(wheel.position)
        translated=lambda point:_world((point[0]+chassis.position.x,point[1]+chassis.position.y))
        frame=dict(t=t,theta2=q/R,A=A,B=translated(m.sites(q)['5'][0]),C=C,actualA=A,actualC=C,
                   chassisZMm=A[2],wheelZMm=C[2],wheelAngle=wheel.angle/R,theta4=theta4,theta5=theta5,theta6=theta6,
                   bodyPositionsMm={'1':A,'6':C},bodyAnglesDeg={'1':chassis.angle/R,'6':wheel.angle/R},
                   indexAnglesDeg={'a':0,'b':p['phi0']+(180-q/R)*(m.ab-1),'c':theta4,'d':theta5,'e':theta5,'f':theta6},
                   terrainOffsetMm=_world(ground.position),
                   terrainPolygonsMm=[[_world((v[0]+ground.position.x,v[1]+ground.position.y)) for v in box] for box in boxes],
                   contactPointsMm=list(sample_points),contactNormalForceN=nf,contactTangentialForceN=tf,
                   slipMmS=max(sample_slips,key=abs) if sample_slips else None,gapMm=gapmm,penetrationMm=penetration,
                   guideResidualMm=residual,constraintPositionErrorMm=max(abs(chassis.position.x)*1000,residual),constraintAngleErrorDeg=abs(chassis.angle)/R)
        if p['springEnabled']:
            frame.update(D=translated(mul(m.rotate(spring['D']),.001)),Q=translated(mul(m.rotate(spring['Q']),.001)))
        row=dict(t=t,theta2=q/R,velocityDegS=qd/R,accelerationDegS2=None,Fs=spring['force'],tauStatic=None,
                 tauApplied=c['hipTorqueNm']-c['dampingNms']*qd,kineticJ=kinetic,potentialJ=potential,energyJ=kinetic+potential,
                 CxMm=C[0],CzMm=C[2],chassisZMm=A[2],chassisVelocityMmS=chassis.velocity.y*1000,chassisAccelerationMmS2=None,
                 wheelZMm=C[2],wheelVelocityXMmS=-wheel.velocity.x*1000,wheelVelocityZMmS=wheel.velocity.y*1000,
                 wheelAngle=wheel.angle/R,wheelAngularVelocityDegS=wheel.angular_velocity/R,theta4=theta4,theta5=theta5,theta6=theta6,
                 requestedInputMm=None,appliedInputMm=None,inputVelocityMmS=None,inputAccelerationMmS2=None,inputReactionN=None,
                 contactNormalForceN=nf,contactTangentialForceN=tf,contactForceXN=fx,contactForceZN=fz,
                 contactNormalImpulseNs=totalN,contactTangentialImpulseNs=totalT,contactCount=len(sample_points),
                 slipMmS=frame['slipMmS'],gapMm=gapmm,penetrationMm=penetration,guideResidualMm=residual,
                 guideForceN=m.internal_force(q,qd),actuatorDampingWorkJ=actuator_work,terrainWorkJ=None,inputWorkJ=None)
        rows.append(row);frames.append(frame)
        sample_time=t;totalJ[:]=[0.,0.];totalN=totalT=0.;sample_points.clear();sample_slips.clear()
    append()
    if rows[0]['penetrationMm']>1e-7:
        raise ValueError('Initial wheel overlaps terrain; adjust initial pose/terrain delay.')
    while t<c['duration']-1e-12:
        q,qd,residual=state()
        if not m.lo-1e-11<=q<=m.hi+1e-11:
            termination='travel-limit';break
        step=min(c['dt'],c['duration']-t,next_sample-t)
        f=m.internal_force(q,qd);force=pymunk.Vec2d(*m.axis)*f
        wheel.force=force+pymunk.Vec2d(*m.force);chassis.force=-force;wheel.torque=m.Mw
        impulse.clear();points.clear();slips.clear();normal_impulses.clear();tangent_impulses.clear()
        before_power=(c['hipTorqueNm']-c['dampingNms']*qd)*qd
        space.step(step);t+=step;steps+=1
        q2,qd2,residual=state()
        actuator_work+=.5*(before_power+(c['hipTorqueNm']-c['dampingNms']*qd2)*qd2)*step
        totalJ[0]+=sum(j[0] for j in impulse);totalJ[1]+=sum(j[1] for j in impulse)
        totalN+=sum(normal_impulses);totalT+=sum(tangent_impulses);sample_points.extend(points);sample_slips.extend(slips)
        max_residual=max(max_residual,residual);max_penetration=max(max_penetration,max(0,-separation()))
        if first_raised is None and any(pt[2]>1e-4 for pt in points):
            first_raised=t;events.append(dict(t=t,type='first-raised-terrain-contact'))
        if not all(math.isfinite(v) for v in (*chassis.position,*chassis.velocity,*wheel.position,*wheel.velocity,wheel.angle,wheel.angular_velocity)):
            raise ValueError('Pymunk contact diverged; reduce dt and inspect inputs.')
        jam=max(0,-separation())>penetration_limit_mm
        if t>=next_sample-1e-10 or t>=c['duration']-1e-10 or not m.lo<=q2<=m.hi or jam:
            append()
            if t>=next_sample-1e-10:next_sample+=1/c['outputHz']
        if jam:
            termination='contact-penetration-limit'
            events.append(dict(t=t,type='contact-penetration-limit',penetrationMm=rows[-1]['penetrationMm'],limitMm=penetration_limit_mm,
                               reason='Moving terrain/guide constraints cannot resolve this contact within the penetration limit; no wall-through-wheel continuation.'))
            break
        if not m.lo<=q2<=m.hi:
            termination='travel-limit';break
    if t>rows[-1]['t']+1e-10:append()
    diagnostics=dict(termination=termination,elapsedSeconds=t,steps=steps,dt=c['dt'],iterations=space.iterations,
                     integrator='Pymunk two real dynamic bodies with real unilateral collision impulses',rigidBodies=2,
                     chassisBodyMassKg=chassis.mass,wheelBodyMassKg=wheel.mass,wheelMomentKgM2=wheel.moment,
                     chassisPitchLocked=True,wheelSpinFree=True,grooveConstraints=2,pivotConstraints=0,gearConstraints=0,
                     maxConstraintPositionErrorMm=max_residual,maxConstraintAngleErrorDeg=0,maxGuideResidualMm=max_residual,
                     maxPenetrationMm=max_penetration,maxContactNormalForceN=max_N,maxContactTangentialForceN=max_T,
                     firstRaisedContactTimeS=first_raised,minimumGuideJacobianMPerRad=m.jacobian_min,
                     collisionSlopMm=space.collision_slop*1000,collisionBias=space.collision_bias,
                     penetrationTerminationLimitMm=penetration_limit_mm,effectiveFriction=wheel_shape.friction*shapes[0].friction,
                     restitution=0,substeps=1,
                     contactForces='impulse sum / elapsed output interval; refine dt for impact peaks',
                     frameSource='actual Pymunk chassis and wheel; B/horn/belt indices exact massless reconstruction',
                     wheelCoefficientK=m.K,resolvedInertiasKgM2=m.I,builderMassesKg={k:p['m'+k] for k in ('1','2','3','5','6')},
                     refinement='No automatic refinement. Compare dt, dt/2 and dt/4; sharp-corner impulse peaks depend on timestep.',
                     modelRevision='straight-guide-contact-v1')
    result=dict(schema='kinefold/contact-v1',engine='pymunk',params=p,runConfig=c,contactConfig=cc,
                snapshot=dict(params=p,solverConfig=c,contactConfig=cc),designHash=m.hash(),rows=rows,frames=frames,events=events,
                diagnostics=diagnostics,terrain=terrain,
                scope=dict(mode='terrain-contact',quarterModel=True,fixture='floating-chassis',coordinates='+x left / +z up / mm',
                           chassis='real m1 body, vertical only, fixed horizontal position/pitch',input='moving sharp terrain; actual unilateral wheel contact'),
                warnings=['Experimental two-body quarter model; no tire compliance, chassis collision, link mass or hardware validation.',
                          'Wheel spin is free; ideal backdriven belts reconstruct indices without added inertia or motor lock.',
                          'Gravity acts once on each actual massive body. No prescribed wheel height or forced gap following.',
                          'Contact forces are interval-averaged impulses; force peaks and penetration require timestep refinement.',
                          'B, horn and belts are exact massless reconstruction; A/C and wheel angle are actual Pymunk transforms.'])
    if termination=='travel-limit':result['warnings'].append('Stopped after the first integration step leaving declared working travel; no stop impact or position correction was applied.')
    elif termination=='contact-penetration-limit':result['warnings'].append('Stopped at the declared 1mm penetration limit: terrain/guide constraints may be jammed, or the timestep too coarse. No position correction was applied.')
    json.dumps(result,allow_nan=False)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--request-stdin',action='store_true',required=True)
    parser.parse_args()
    try:
        print(json.dumps(simulate_contact(json.load(sys.stdin)),allow_nan=False,separators=(',',':')))
        return 0
    except (ValueError,KeyError,TypeError,ArithmeticError,ImportError) as error:
        print(json.dumps({'error':str(error)}));return 1


if __name__=='__main__':
    raise SystemExit(main())
