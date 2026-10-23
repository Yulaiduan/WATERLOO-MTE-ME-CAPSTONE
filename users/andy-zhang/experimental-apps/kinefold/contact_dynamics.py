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


from contact_cases import (ContactGeometry, validate_contact_request, resolve_case, initial_conditions, terrain_spec,
    CaseController, energy_fields, case_metrics, model_identity, stopping_demand, floor_under_hip)


def _world(v):
    return [-v[0]*1000,0,v[1]*1000]


def simulate_contact(payload, *, stop_at_assessment=False):
    import pymunk
    m=validate_contact_request(payload)
    p,c,cc=m.p,m.c,dict(payload['contactConfig'])
    case=resolve_case(payload);controller=CaseController(m,case)
    qinitial,hinitial,xinitial,zinitial=initial_conditions(m,case);m.q0=qinitial
    space=pymunk.Space();space.gravity=(0,-p['g']);space.iterations=int(c['iterations'])
    # SI tolerances are explicit, not epsilon masses or tire compliance.
    space.collision_slop=1e-6
    space.collision_bias=(1-.2)**60
    radius=p['rw']/1000
    C0=m.sites(m.q0)['6'][0]
    chassis=pymunk.Body(p['m1'],math.inf)
    chassis.position=(0,hinitial)
    qd0=c['initialVelocityDegS']*R if case['kind']=='terrain-stability' else 0.
    chassis.velocity=(0,-m.sites(m.q0)['6'][1][1]*qd0)
    wheel=pymunk.Body(p['m6'],m.I['6']);wheel.position=(xinitial,zinitial)
    wheel.angle=(m.K*(p['theta2']-p['te'])-p['alpha'])*R
    # qdot is independent relative-guide motion. Initially wheel z velocity=0;
    # guide tangent sets the horizontal wheel component without locking spin.
    wheel.velocity=(m.sites(m.q0)['6'][1][0]*qd0,0)
    ground=pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    spec=terrain_spec(m,case);speed=spec['speed'];ground.velocity=(speed,0)
    space.add(chassis,wheel,ground)
    heave=pymunk.GrooveJoint(space.static_body,chassis,(0,-1000),(0,1000),(0,0))
    # Infinite straight guide, terminated at declared working travel; endpoints
    # never introduce an undeclared joint-stop impact response.
    guide=pymunk.GrooveJoint(chassis,wheel,mul(m.axis,min(m.distance(m.lo),m.distance(m.hi))),mul(m.axis,max(m.distance(m.lo),m.distance(m.hi))),(0,0))
    heave.collide_bodies=guide.collide_bodies=False
    space.add(heave,guide)
    wheel_shape=pymunk.Circle(wheel,radius);wheel_shape.friction=cc['friction'];wheel_shape.elasticity=0
    wheel_shape.collision_type=1;wheel_shape.filter=pymunk.ShapeFilter(categories=1,mask=2)
    space.add(wheel_shape)
    height=spec['height'];boxes=spec['boxes'];base=spec['base'];shapes=[]
    for vertices in boxes:shapes.append(pymunk.Poly(ground,vertices,radius=0))
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
    terrain=spec['terrain']
    bounds=sorted((m.distance(m.lo),m.distance(m.hi)))
    rows=[];frames=[];events=[];t=0.;next_sample=1/c['outputHz'];steps=0;termination='duration'
    sample_time=0.;totalJ=[0.,0.];totalN=0.;totalT=0.;sample_points=[];sample_slips=[]
    actuator_work=0.;max_residual=0.;max_penetration=0.;max_N=0.;max_T=0.;first_raised=None
    penetration_limit_mm=1.
    max_stop_drift=0.
    motor_work=0.;stop_dissipation=0.;damping_work=0.;contact_dissipation=0.;terrain_work=0.;had_contact=False;arrested=False;previous_vh=chassis.velocity.y
    control=controller.torques(m.q0,qd0);last_contact=False
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
                 tauApplied=control['motorTorqueNm']-c['dampingNms']*qd,kineticJ=kinetic,potentialJ=potential,energyJ=kinetic+potential,
                 CxMm=C[0],CzMm=C[2],chassisZMm=A[2],chassisVelocityMmS=chassis.velocity.y*1000,chassisAccelerationMmS2=None,
                 wheelZMm=C[2],wheelVelocityXMmS=-wheel.velocity.x*1000,wheelVelocityZMmS=wheel.velocity.y*1000,
                 wheelAngle=wheel.angle/R,wheelAngularVelocityDegS=wheel.angular_velocity/R,theta4=theta4,theta5=theta5,theta6=theta6,
                 requestedInputMm=None,appliedInputMm=None,inputVelocityMmS=None,inputAccelerationMmS2=None,inputReactionN=None,
                 contactNormalForceN=nf,contactTangentialForceN=tf,contactForceXN=fx,contactForceZN=fz,
                 contactNormalImpulseNs=totalN,contactTangentialImpulseNs=totalT,contactCount=len(sample_points),
                 slipMmS=frame['slipMmS'],gapMm=gapmm,penetrationMm=penetration,guideResidualMm=residual,
                 guideForceN=(spring['torque']+control['motorTorqueNm']-c['dampingNms']*qd)/m.jacobian(q),actuatorDampingWorkJ=actuator_work,terrainWorkJ=None,inputWorkJ=None)
        row.update(energy_fields(m,q,chassis.position.y,chassis.velocity.y,(wheel.velocity-chassis.velocity).dot(pymunk.Vec2d(*m.axis)),wheel.angular_velocity))
        row.update(control,motorWorkJ=motor_work,stopDissipationJ=stop_dissipation,dampingWorkJ=damping_work,contactDissipationJ=contact_dissipation,terrainWorkJ=terrain_work,demandTorqueNm=stopping_demand(m,q,qd,chassis.velocity.y,case))
        row['chassisClearanceMm']=A[2]-case['undersideOffsetMm']-floor_under_hip(spec,t)*1000 if case['undersideOffsetMm'] is not None else None
        row['energyBalanceResidualJ']=row['energyJ']-(rows[0]['energyJ'] if rows else row['energyJ'])-motor_work-damping_work-terrain_work+stop_dissipation+contact_dissipation
        row['positionStabilizationJ']=None
        row['motionPhase']='end-stop' if min(abs(m.distance(q)-bounds[0]),abs(m.distance(q)-bounds[1]))<1e-7 and abs(qd)<1e-5 else 'contact' if last_contact else 'free-flight'
        frame.update(controllerPhase=control['controllerPhase'],undersideClearanceMm=row['chassisClearanceMm'])
        rows.append(row);frames.append(frame)
        sample_time=t;totalJ[:]=[0.,0.];totalN=totalT=0.;sample_points.clear();sample_slips.clear()
    append()
    if rows[0]['chassisClearanceMm'] is not None and rows[0]['chassisClearanceMm']<=0:
        raise ValueError('Initial chassis underside clearance is nonpositive; reduce the underside offset or change the initial case pose/drop.')
    if rows[0]['penetrationMm']>1e-7:
        raise ValueError('Initial wheel overlaps terrain; adjust initial pose/terrain delay.')
    while t<c['duration']-1e-12:
        q,qd,residual=state()
        if not m.lo-1e-2<=q<=m.hi+1e-2:
            raise ValueError(f'Unilateral travel-stop position drift exceeds tolerance at t={t},q={q/R}; refine dt.')
        step=min(c['dt'],c['duration']-t,next_sample-t)
        control=controller.torques(q,qd,had_contact)
        sd=(wheel.velocity-chassis.velocity).dot(pymunk.Vec2d(*m.axis));spos=m.distance(q)
        bounds=sorted((m.distance(m.lo),m.distance(m.hi)))
        if case['kind']=='jump' and not controller.extended and sd>1e-10:
            crossing=(max(bounds)-spos)/sd
            if 1e-6<crossing<step:step=crossing
        f=(m.spring(q)['torque']+control['motorTorqueNm']-c['dampingNms']*qd)/m.jacobian(q);force=pymunk.Vec2d(*m.axis)*f
        wheel.force=force+pymunk.Vec2d(*m.force);chassis.force=-force;wheel.torque=m.Mw
        impulse.clear();points.clear();slips.clear();normal_impulses.clear();tangent_impulses.clear()
        before_power=(control['motorTorqueNm']-c['dampingNms']*qd)*qd
        pre_vh=chassis.velocity.y
        wheel_free=wheel.velocity+(force+pymunk.Vec2d(*m.force))/p['m6']*step+pymunk.Vec2d(0,-p['g']*step)
        chassis_free=chassis.velocity-force/p['m1']*step+pymunk.Vec2d(0,-p['g']*step)
        omega_free=wheel.angular_velocity+m.Mw/wheel.moment*step
        space.step(step);t+=step;steps+=1
        q2,qd2,residual=state()
        motor_work+=control['motorTorqueNm']*(q2-q)
        damping_work-=c['dampingNms']*.5*(qd*qd+qd2*qd2)*step
        contactJ=pymunk.Vec2d(sum(j[0] for j in impulse),sum(j[1] for j in impulse))
        terrain_increment=contactJ.dot(ground.velocity)
        contact_work=contactJ.dot((wheel_free+wheel.velocity)*.5)+wheel.moment*(wheel.angular_velocity-omega_free)*(wheel.angular_velocity+omega_free)*.5
        terrain_work+=terrain_increment;contact_dissipation+=max(0.,terrain_increment-contact_work)
        actuator_work+=.5*(before_power+(control['motorTorqueNm']-c['dampingNms']*qd2)*qd2)*step
        spos2=m.distance(q2);sd2=qd2*m.jacobian(q2)
        max_stop_drift=max(max_stop_drift,max(bounds[0]-spos2,0,spos2-bounds[1])*1000)
        # At an extension event, transfer relative momentum before the next
        # position update. The floor and compression endpoint remain coupled
        # in Chipmunk's simultaneous contact/finite-groove solve.
        if case['kind']=='jump' and not controller.extended and spos2>=bounds[1]-1e-7 and sd2>0:
            M=p['m1']+p['m6'];vz=(p['m1']*chassis.velocity.y+p['m6']*wheel.velocity.y)/M
            chassis.velocity=(0,vz);wheel.velocity=(0,vz);controller.extended=True
            events.append(dict(t=t,type='extension-stop'))
        free_sd=(wheel_free-chassis_free).dot(pymunk.Vec2d(*m.axis))
        atlo=spos2<=bounds[0]+1e-6 and free_sd<0
        athi=spos2>=bounds[1]-1e-6 and free_sd>0
        if atlo or athi:
            # Impulse work isolates the guide constraint from wheel contact.
            # Midpoint pre/post velocities give exact kinetic impulse work;
            # this also includes small solver bias work and needs dt refinement.
            contactJ=pymunk.Vec2d(sum(j[0] for j in impulse),sum(j[1] for j in impulse))
            guideJ=p['m6']*(wheel.velocity-wheel_free)-contactJ
            relavg=((wheel_free-chassis_free)+(wheel.velocity-chassis.velocity))*.5
            stop_dissipation+=max(0.,-guideJ.dot(relavg))
            which='compression-stop' if abs(q2-m.hi)<abs(q2-m.lo) else 'extension-stop'
            if not any(e['type']==which for e in events):events.append(dict(t=t,type=which))
            if which=='extension-stop' and case['kind']=='jump':controller.extended=True
        active=bool(points)
        if active and not had_contact:
            had_contact=True;events.append(dict(t=t,type='first-contact',chassisVelocityMmS=pre_vh*1000))
        if last_contact and not active and wheel.position.y>radius+1e-7:
            if not any(e['type']=='takeoff' for e in events):events.append(dict(t=t,type='takeoff'))
        if case['kind']=='jump' and pre_vh>0>=chassis.velocity.y and any(e['type']=='takeoff' for e in events) and not any(e['type']=='apex' for e in events):
            events.append(dict(t=t,type='apex',chassisZMm=chassis.position.y*1000))
        if case['kind']=='landing' and had_contact and not arrested and pre_vh<0<=chassis.velocity.y:
            arrested=True;events.append(dict(t=t,type='chassis-arrest'))
        last_contact=active
        if case['undersideOffsetMm'] is not None and chassis.position.y*1000-case['undersideOffsetMm']-floor_under_hip(spec,t)*1000<=0:
            termination='underside-contact';events.append(dict(t=t,type='underside-contact'))
        totalJ[0]+=sum(j[0] for j in impulse);totalJ[1]+=sum(j[1] for j in impulse)
        totalN+=sum(normal_impulses);totalT+=sum(tangent_impulses);sample_points.extend(points);sample_slips.extend(slips)
        max_residual=max(max_residual,residual);max_penetration=max(max_penetration,max(0,-separation()))
        if first_raised is None and any(pt[2]>1e-4 for pt in points):
            first_raised=t;events.append(dict(t=t,type='first-raised-terrain-contact'))
        if not all(math.isfinite(v) for v in (*chassis.position,*chassis.velocity,*wheel.position,*wheel.velocity,wheel.angle,wheel.angular_velocity)):
            raise ValueError('Pymunk contact diverged; reduce dt and inspect inputs.')
        jam=max(0,-separation())>penetration_limit_mm
        assessment_stop=stop_at_assessment and case['kind']=='landing' and (arrested or any(e['type']=='compression-stop' for e in events))
        if t>=next_sample-1e-10 or t>=c['duration']-1e-10 or termination=='underside-contact' or jam or assessment_stop:
            append()
            if t>=next_sample-1e-10:next_sample+=1/c['outputHz']
        if jam:
            termination='contact-penetration-limit'
            events.append(dict(t=t,type='contact-penetration-limit',penetrationMm=rows[-1]['penetrationMm'],limitMm=penetration_limit_mm,
                               reason='Moving terrain/guide constraints cannot resolve this contact within the penetration limit; no wall-through-wheel continuation.'))
            break
        if termination=='underside-contact':break
        if assessment_stop:termination='assessment-outcome';break
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
                     modelRevision='straight-guide-contact-cases-v2',stopLaw='Pymunk finite groove endpoints, unilateral inelastic travel stops; interval impulse-work dissipation',stopDissipationJ=stop_dissipation,maxTravelStopDriftMm=max_stop_drift)
    result=dict(schema='kinefold/contact-v2',engine='pymunk',params=p,runConfig=c,contactConfig=cc,
                snapshot=dict(params=p,solverConfig=c,contactConfig=cc),designHash=model_identity(m,cc,case),rows=rows,frames=frames,events=events,
                diagnostics=diagnostics,terrain=terrain,
                scope=dict(mode='terrain-contact',quarterModel=True,fixture='floating-chassis',coordinates='+x left / +z up / mm',
                           chassis='real m1 body, vertical only, fixed horizontal position/pitch',input='moving sharp terrain' if case['kind']=='terrain-stability' else 'stationary flat floor; actual unilateral wheel contact'),
                warnings=['Experimental two-body quarter model; no tire compliance, rigid chassis collision shape, link mass or hardware validation; entered underside point-clearance stops are assessed.',
                          'Wheel spin is free; ideal backdriven belts reconstruct indices without added inertia or motor lock.',
                          'Gravity acts once on each actual massive body. No prescribed wheel height or forced gap following.',
                          'Contact forces are interval-averaged impulses; force peaks and penetration require timestep refinement.',
                          'B, horn and belts are exact massless reconstruction; A/C and wheel angle are actual Pymunk transforms.'])
    result['caseConfig']=case
    result['caseMetrics']=case_metrics(rows,events,m,case)
    result['energyEstimate']=result['caseMetrics']['energyEstimate']
    diagnostics['energyBalanceResidualJ']=rows[-1]['energyJ']-rows[0]['energyJ']-motor_work-damping_work-terrain_work+stop_dissipation+contact_dissipation
    diagnostics['stopDissipationMeaning']='Constraint impulse work from free to solved velocities; includes solver bias work, requires timestep refinement.'
    if 'caseConfig' in payload:result['snapshot']['caseConfig']=case
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
