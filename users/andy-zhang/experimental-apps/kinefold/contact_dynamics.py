"""Integrate the experimental exact-straight-path VSL with real terrain contact.

Run app .venv Python contact_dynamics.py --request-stdin with the complete JSON
builder (mm/deg/kg/N), runConfig (s/SI torque) and explicit contactConfig. Returns
kinefold/contact-v2 world-mm frames, actual body states/contact impulses and
diagnostics. Pymunk uses metres, kg, seconds, source-horizontal-right/up axes.
Only equal links/2:1 hip ratio, massless bars or two finite uniform rods, uniform disc,
vertical nonpitching chassis and freely backdrivable ideal belts are supported.
The finite branch has four bodies, native pivots/belt gear/hip stops and no
wheel/chassis groove. Rigid Coulomb contact is not a tire/hardware model.
"""
import argparse
import json
import math
import sys

from torque_targets import TargetObservation
from contact_cases import check_motor_step
from dynamic_model import Model, R, mul, validate, finite
from terrain_profiles import circle_contacts, raised_contact
from contact_cases import initial_motion,COMObservation


from contact_cases import (ContactGeometry, validate_contact_request, resolve_case, initial_conditions, terrain_spec,
    CaseController, energy_fields, case_metrics, model_identity, stopping_demand, floor_under_hip, annotate_contact_work)


def _world(v):
    return [-v[0]*1000,0,v[1]*1000]


def simulate_contact(payload, *, stop_at_assessment=False):
    rotors=[]
    try:return _simulate_contact(payload,stop_at_assessment=stop_at_assessment,_rotors=rotors)
    finally:
        for rotor in rotors:rotor.close()


def _simulate_contact(payload, *, stop_at_assessment=False, _rotors):
    import pymunk
    m=validate_contact_request(payload)
    p,c,cc=m.p,m.c,dict(payload['contactConfig'])
    case=resolve_case(payload);controller=CaseController(m,case);observation=TargetObservation(case,c['dt'])
    com_observation=COMObservation()
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
    motion=initial_motion(m,case,m.q0)
    chassis.velocity=(0,motion['chassisVelocity'])
    wheel=pymunk.Body(p['m6'],m.I['6']);wheel.position=(xinitial,zinitial)
    wheel.angle=(m.K*(p['theta2']-p['te'])-p['alpha'])*R
    # qdot is independent guide motion. Legacy flat initialization uses wheel vz=0;
    # v2 follows the conveyor incline normal velocity. Spin remains unlocked.
    wheel.velocity=motion['wheelVelocity']
    ground=pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    spec=terrain_spec(m,case);speed=spec['speed'];ground.velocity=(speed,0)
    space.add(chassis,wheel,ground)
    rotor=None;linkage=None
    if m.finite_links:
        from finite_pymunk_contact import FiniteLinkage
        linkage=FiniteLinkage(space,m,chassis,wheel,m.q0,hinitial,motion['chassisVelocity'],motion['qd'])
    if m.Jref>0 and not linkage:
        from motor_rotor_constraint import attach
        rotor=attach(space,chassis,wheel,m,m.Jref,m.q0,qd0)
        _rotors.append(rotor)
    heave=(pymunk.PivotJoint(space.static_body,chassis,(0,hinitial),(0,0)) if m.pinned
           else pymunk.GrooveJoint(space.static_body,chassis,(0,-1000),(0,1000),(0,0)))
    # Infinite straight guide, terminated at declared working travel; endpoints
    # never introduce an undeclared joint-stop impact response.
    guide=pymunk.GrooveJoint(chassis,wheel,mul(m.axis,min(m.distance(m.lo),m.distance(m.hi))),mul(m.axis,max(m.distance(m.lo),m.distance(m.hi))),(0,0))
    heave.collide_bodies=guide.collide_bodies=False
    space.add(heave)
    if not linkage:space.add(guide)
    wheel_shape=pymunk.Circle(wheel,radius);wheel_shape.friction=cc['friction'];wheel_shape.elasticity=0
    wheel_shape.collision_type=1;wheel_shape.filter=pymunk.ShapeFilter(categories=1,mask=2)
    space.add(wheel_shape)
    height=spec['height'];boxes=spec['boxes'];base=spec['base'];shapes=[]
    for vertices in boxes:shapes.append(pymunk.Poly(ground,vertices,radius=0))
    if 'segments' in spec:
        chain=spec['contour']
        for i,(a,b) in enumerate(spec['segments']):
            shape=pymunk.Segment(ground,a,b,0)
            shape.set_neighbors(chain[max(0,i-1)],chain[min(len(chain)-1,i+2)])
            shapes.append(shape)
    else:shapes.append(pymunk.Segment(ground,*base,0))
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
    max_rotor_position=max_rotor_velocity=0.;max_stop_drift=0.
    motor_loss=0.;motor_coulomb_loss=0.;motor_viscous_loss=0.;coupled_loss=0.;motor_work=0.;stop_dissipation=0.;damping_work=0.;contact_dissipation=0.;terrain_work=0.;external_work=0.;had_contact=False;arrested=False;previous_vh=chassis.velocity.y
    control=controller.torques(m.q0,qd0,time=0.,state=dict(h=hinitial,vh=motion['chassisVelocity'],contacted=False));last_contact=False
    def total_vertical_momentum():
        bodies=(chassis,linkage.upper,linkage.lower,wheel) if linkage else (chassis,wheel)
        return sum(b.mass*b.velocity.y for b in bodies)
    pin_baseline=None;sample_momentum=total_vertical_momentum()
    def state():
        if linkage:return linkage.state()
        relative=wheel.position-chassis.position
        q=m.inverse(relative.dot(pymunk.Vec2d(*m.axis)))
        qd=(wheel.velocity-chassis.velocity).dot(pymunk.Vec2d(*m.axis))/m.jacobian(q)
        exact=m.sites(q)['6'][0]
        residual=math.hypot(relative.x-exact[0],relative.y-exact[1])*1000
        return q,qd,residual
    def actual_energy(q):
        # Native guide residuals are numerical; report actual body energy rather
        # than the ideal reconstructed wheel velocity/height in the partition.
        ee=energy_fields(m,q,chassis.position.y,chassis.velocity.y,(wheel.velocity-chassis.velocity).dot(pymunk.Vec2d(*m.axis)),wheel.angular_velocity)
        ee.update(wheelKineticJ=.5*wheel.mass*wheel.velocity.length_squared+.5*wheel.moment*wheel.angular_velocity**2,
            gravityEnergyJ=p['g']*(chassis.mass*chassis.position.y+wheel.mass*wheel.position.y))
        if linkage:ee.update(linkage.energies())
        if rotor is not None:
            ee.update(rotorKineticJ=.5*m.motor.reflected_inertia*rotor.omega**2,legacyJointRotorKineticJ=.5*c['hipRotorInertiaKgM2']*rotor.omega**2,coggingPotentialJ=m.motor.motor_state(rotor.angle,rotor.omega,0)['coggingPotentialJ'])
        return ee
    def separation():
        if 'segments' in spec:return min(g[0] for g in circle_contacts(spec,t,wheel.position.x,wheel.position.y,radius))*1000
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
        nonlocal sample_time,totalN,totalT,max_residual,max_penetration,max_N,max_T,pin_baseline,sample_momentum
        q,qd,residual=state();spring=m.spring(q);elapsed=t-sample_time
        nf=totalN/elapsed if elapsed>0 else 0.;tf=totalT/elapsed if elapsed>0 else 0.
        fx=-totalJ[0]/elapsed if elapsed>0 else 0.;fz=totalJ[1]/elapsed if elapsed>0 else 0.
        gapmm=separation();penetration=max(0,-gapmm)
        max_residual=max(max_residual,residual);max_penetration=max(max_penetration,penetration)
        max_N=max(max_N,nf);max_T=max(max_T,tf)
        kinetic=.5*chassis.mass*chassis.velocity.length_squared+.5*wheel.mass*wheel.velocity.length_squared+.5*wheel.moment*wheel.angular_velocity**2
        potential=p['g']*(chassis.mass*chassis.position.y+wheel.mass*wheel.position.y)+spring['energy']
        ee=actual_energy(q)
        if linkage:kinetic+=ee['linkKineticJ'];potential=ee['gravityEnergyJ']+spring['energy']
        kinetic+=ee['rotorKineticJ']+ee['legacyJointRotorKineticJ'];potential+=ee['coggingPotentialJ']
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
        if linkage:
            frame.update(B=_world(linkage.upper.local_to_world((p['L2']/2000,0))),constraintAngleErrorDeg=linkage.angle_residual())
            frame['bodyPositionsMm'].update({'2':_world(linkage.upper.position),'3':_world(linkage.lower.position)})
            frame['bodyAnglesDeg'].update({'2':linkage.upper.angle/R,'3':linkage.lower.angle/R})
        row=dict(t=t,theta2=q/R,velocityDegS=qd/R,accelerationDegS2=None,Fs=spring['force'],tauStatic=None,
                 tauApplied=control['motorTorqueNm']+control['jointFrictionNm']-c['dampingNms']*qd,kineticJ=kinetic,potentialJ=potential,energyJ=kinetic+potential,
                 CxMm=C[0],CzMm=C[2],chassisZMm=A[2],chassisVelocityMmS=chassis.velocity.y*1000,chassisAccelerationMmS2=None,
                 wheelZMm=C[2],wheelVelocityXMmS=-wheel.velocity.x*1000,wheelVelocityZMmS=wheel.velocity.y*1000,
                 wheelAngle=wheel.angle/R,wheelAngularVelocityDegS=wheel.angular_velocity/R,theta4=theta4,theta5=theta5,theta6=theta6,
                 requestedInputMm=None,appliedInputMm=None,inputVelocityMmS=None,inputAccelerationMmS2=None,inputReactionN=None,
                 contactNormalForceN=nf,contactTangentialForceN=tf,contactForceXN=fx,contactForceZN=fz,
                 contactNormalImpulseNs=totalN,contactTangentialImpulseNs=totalT,contactCount=len(sample_points),
                 slipMmS=frame['slipMmS'],gapMm=gapmm,penetrationMm=penetration,guideResidualMm=residual,
                 guideForceN=(spring['torque']+control['motorTorqueNm']+control['jointPassiveNm']-c['dampingNms']*qd)/m.jacobian(q),actuatorDampingWorkJ=actuator_work,terrainWorkJ=None,inputWorkJ=None)
        row.update(energy_fields(m,q,chassis.position.y,chassis.velocity.y,(wheel.velocity-chassis.velocity).dot(pymunk.Vec2d(*m.axis)),wheel.angular_velocity))
        row.update(control,motorDissipatedJ=motor_loss,motorCoulombDissipatedJ=motor_coulomb_loss,motorViscousDissipatedJ=motor_viscous_loss,motorDissipationJ=motor_loss,motorFrictionLossJ=motor_loss,motorWorkJ=motor_work,stopDissipationJ=stop_dissipation,dampingWorkJ=damping_work,externalWorkJ=external_work,contactDissipationJ=contact_dissipation,terrainWorkJ=terrain_work,demandTorqueNm=stopping_demand(m,q,qd,chassis.velocity.y,case))
        row.update(ee)
        bodies=(chassis,linkage.upper,linkage.lower,wheel) if linkage else (chassis,wheel)
        row.update(comZMm=sum(b.mass*b.position.y for b in bodies)/m.total_mass*1000,
            comVelocityZMmS=sum(b.mass*b.velocity.y for b in bodies)/m.total_mass*1000)
        # Sample actual native rotor state, not the previous step's held controller diagnostics.
        sample_motor=m.motor.motor_state(rotor.angle if rotor else q,rotor.omega if rotor else qd,control['motorTorqueNm'])
        if controller.actuator:sample_motor.pop('shaftCommandNm')  # keep bounded transmission conversion
        row.update(sample_motor)
        if controller.actuator:row['rideTargetHeightMm']=controller.actuator.target_height(t)*1000
        if rotor is not None:row.update(legacyJointRotorKineticJ=.5*c['hipRotorInertiaKgM2']*rotor.omega**2,idealMotorVelocityRadS=m.motor.total_ratio*qd,rotorConstraintPositionResidualRad=rotor.position_residual,rotorConstraintVelocityResidualRadS=rotor.velocity_residual)
        row['chassisClearanceMm']=A[2]-case['undersideOffsetMm']-floor_under_hip(spec,t)*1000 if case['undersideOffsetMm'] is not None else None
        row['energyBalanceResidualJ']=row['energyJ']-(rows[0]['energyJ'] if rows else row['energyJ'])-motor_work-damping_work-terrain_work-external_work+motor_loss+stop_dissipation+contact_dissipation
        if rotor is not None or linkage:
            row.update(coupledConstraintKineticLossJ=coupled_loss,rotorConstraintImpulseWorkJ=rotor.constraint_work_j if rotor else None,contactDissipationJ=None,stopDissipationJ=None)
            row['energyBalanceResidualJ']=row['energyJ']-(rows[0]['energyJ'] if rows else row['energyJ'])-motor_work-damping_work-terrain_work-external_work+motor_loss+coupled_loss
        row['positionStabilizationJ']=None
        row['motionPhase']='end-stop' if min(abs(m.distance(q)-bounds[0]),abs(m.distance(q)-bounds[1]))<1e-7 and abs(qd)<1e-5 else 'contact' if last_contact else 'free-flight'
        frame.update(controllerPhase=control['controllerPhase'],undersideClearanceMm=row['chassisClearanceMm'])
        momentum=total_vertical_momentum();pin=None;pin_impulse=None
        if m.pinned and elapsed>0:
            pin_impulse=momentum-sample_momentum+(m.total_mass*p['g']-m.force[1])*elapsed-totalJ[1]
            pin=pin_impulse/elapsed
            if pin_baseline is None:pin_baseline=pin
        row.update(pinForceZN=pin,pinForceDeltaZN=pin-pin_baseline if pin is not None else None,
            chassisSupportForceZN=p['m1']*p['g']-pin if pin is not None else None,
            pinImpulseNs=pin_impulse,pinMomentumChangeNs=momentum-sample_momentum if m.pinned and elapsed else None,
            pinGravityImpulseNs=m.total_mass*p['g']*elapsed if m.pinned and elapsed else None,
            pinExternalImpulseNs=m.force[1]*elapsed if m.pinned and elapsed else None,
            pinContactImpulseNs=totalJ[1] if m.pinned and elapsed else None,
            pinPositionErrorMm=(chassis.position-pymunk.Vec2d(0,hinitial)).length*1000 if m.pinned else None,
            pinWorkJ=0. if m.pinned else None)
        frame.update(pinForceZN=pin,pinPositionErrorMm=row['pinPositionErrorMm'])
        sample_momentum=momentum
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
        control=controller.torques(q,qd,last_contact if controller.actuator else had_contact,time=t,state=dict(h=chassis.position.y,vh=chassis.velocity.y,contacted=last_contact))
        if rotor is not None:
            actual_motor=m.motor.motor_state(rotor.angle,rotor.omega,control['motorTorqueNm'])
            actual_motor.pop('rotorKineticJ');actual_motor.pop('coggingPotentialJ')
            if controller.actuator:actual_motor.pop('shaftCommandNm')
            control.update(actual_motor)
        sd=(wheel.velocity-chassis.velocity).dot(pymunk.Vec2d(*m.axis));spos=m.distance(q)
        bounds=sorted((m.distance(m.lo),m.distance(m.hi)))
        if not linkage and case['kind']=='jump' and not controller.extended and sd>1e-10:
            crossing=(max(bounds)-spos)/sd
            if 1e-6<crossing<step:step=crossing
        f=(m.spring(q)['torque']+control['motorTorqueNm']+control['jointPassiveNm']-c['dampingNms']*qd)/m.jacobian(q);force=pymunk.Vec2d(*m.axis)*f
        check_motor_step(m,rotor.omega if rotor is not None else qd,step)
        motor_angle_before=rotor.angle if rotor is not None else q
        if rotor is not None:
            rotor.prepare(step,m.spring(q)['torque']+control['motorTorqueNm']+control['jointPassiveNm']-c['dampingNms']*qd)
            force=pymunk.Vec2d(0,0)
        wheel.force=force+pymunk.Vec2d(*m.force);chassis.force=-force;wheel.torque=m.Mw
        if linkage:
            wheel.force=pymunk.Vec2d(*m.force);chassis.force=(0,0)
            linkage.apply(m.spring(q)['torque']+control['motorTorqueNm']+control['jointPassiveNm']-c['dampingNms']*qd)
        impulse.clear();points.clear();slips.clear();normal_impulses.clear();tangent_impulses.clear()
        before_power=(control['motorTorqueNm']-c['dampingNms']*qd)*qd
        pre_vh=chassis.velocity.y;before_position=(wheel.position.x,wheel.position.y,wheel.angle);event_start=len(events)
        wheel_free=wheel.velocity+wheel.force/p['m6']*step+pymunk.Vec2d(0,-p['g']*step)
        chassis_free=chassis.velocity+chassis.force/p['m1']*step+pymunk.Vec2d(0,-p['g']*step)
        if m.pinned:chassis_free=pymunk.Vec2d(0,0)
        omega_free=wheel.angular_velocity+m.Mw/wheel.moment*step
        if rotor is not None:
            rotor_free=rotor.omega+(m.spring(q)['torque']+control['motorTorqueNm']+control['jointPassiveNm']-c['dampingNms']*qd)/m.Jref*step
            free_ke=.5*p['m1']*chassis_free.length_squared+.5*p['m6']*wheel_free.length_squared+.5*wheel.moment*omega_free**2+.5*m.Jref*rotor_free**2
        if linkage:
            # A bodywise torque kick violates the rigid linkage acceleration
            # constraints and invents O(dt² tau²/Irod) energy. Predict smooth
            # kinetic change in the exact rigid-link tangent space instead.
            from finite_contact_model import kinetic as rigid_kinetic
            terms=m.mass_terms(q);vd=m.jacobian(q)*qd;vh=chassis.velocity.y
            generalized=((-(terms['A'])*p['g']+m.force[1]-terms['Hprime']*vd*vd),
                (m.spring(q)['torque']+control['motorTorqueNm']+control['jointPassiveNm']-c['dampingNms']*qd)/m.jacobian(q)-p['g']*terms['H']+m.axis[0]*m.force[0]+m.axis[1]*m.force[1]-.5*terms['Dprime']*vd*vd,m.Mw)
            acc=[sum(a*b for a,b in zip(row,generalized)) for row in terms['inverse']]
            if m.pinned:acc=[0.,generalized[1]/terms['D'],generalized[2]/m.I['6']]
            velocity=[vh,vd,wheel.angular_velocity];pred=[a+step*b for a,b in zip(velocity,acc)]
            predict_distance=max(min(m.distance(m.lo),m.distance(m.hi)),min(max(m.distance(m.lo),m.distance(m.hi)),m.distance(q)+vd*step))
            free_ke=linkage.kinetic()+rigid_kinetic(m,m.inverse(predict_distance),pred)-rigid_kinetic(m,q,velocity)
        space.step(step);t+=step;steps+=1
        # Snap accumulated clock roundoff at output boundaries. An epsilon
        # remainder must not become another warm-started contact impulse step.
        if abs(t-c['duration'])<1e-10:t=c['duration']
        elif abs(t-next_sample)<1e-10:t=next_sample
        if rotor is not None:
            rotor.check()
            max_rotor_position=max(max_rotor_position,abs(rotor.position_residual))
            max_rotor_velocity=max(max_rotor_velocity,abs(rotor.velocity_residual))
        q2,qd2,residual=state()
        motor_work+=control['motorTorqueNm']*((rotor.angle if rotor is not None else q2)-motor_angle_before)
        damping_work-=c['dampingNms']*.5*(qd*qd+qd2*qd2)*step
        motor_loss+=control['motorLossPowerW']*step
        motor_coulomb_loss+=control['coulombLossPowerW']*step
        motor_viscous_loss+=control['viscousLossPowerW']*step
        contactJ=pymunk.Vec2d(sum(j[0] for j in impulse),sum(j[1] for j in impulse))
        terrain_increment=contactJ.dot(ground.velocity)
        contact_work=contactJ.dot((wheel_free+wheel.velocity)*.5)+wheel.moment*(wheel.angular_velocity-omega_free)*(wheel.angular_velocity+omega_free)*.5
        external_work+=m.force[0]*(wheel.position.x-before_position[0])+m.force[1]*(wheel.position.y-before_position[1])+m.Mw*(wheel.angle-before_position[2])
        terrain_work+=terrain_increment;contact_dissipation+=max(0.,terrain_increment-contact_work)
        if rotor is not None:
            solved_ke=.5*p['m1']*chassis.velocity.length_squared+.5*p['m6']*wheel.velocity.length_squared+.5*wheel.moment*wheel.angular_velocity**2+.5*m.Jref*rotor.omega**2
            coupled_loss+=free_ke+terrain_increment-solved_ke
        if linkage:coupled_loss+=free_ke+terrain_increment-linkage.kinetic()
        if rotor is not None:actuator_work=motor_work+damping_work
        else:actuator_work+=.5*(before_power+(control['motorTorqueNm']-c['dampingNms']*qd2)*qd2)*step
        spos2=m.distance(q2);sd2=qd2*m.jacobian(q2)
        max_stop_drift=max(max_stop_drift,max(bounds[0]-spos2,0,spos2-bounds[1])*1000)
        # At an extension event, transfer relative momentum before the next
        # position update. The floor and compression endpoint remain coupled
        # in Chipmunk's simultaneous contact/finite-groove solve.
        if rotor is None and not linkage and case['kind']=='jump' and not controller.extended and spos2>=bounds[1]-1e-7 and sd2>0:
            M=p['m1']+p['m6'];vz=(p['m1']*chassis.velocity.y+p['m6']*wheel.velocity.y)/M
            chassis.velocity=(0,vz);wheel.velocity=(0,vz);controller.extended=True
            events.append(dict(t=t,type='extension-stop'))
        guideJ=p['m6']*(wheel.velocity-wheel_free)-contactJ
        grooveJ=guideJ
        if rotor is not None:
            # The scalar rotor also kicks the wheel along the guide. Remove
            # its exact signed native impulse before identifying a groove stop.
            # NativeRotor._pre uses this same post-position-update Jacobian.
            grooveJ=guideJ+pymunk.Vec2d(*m.axis)*(rotor.accumulated_impulse/m.jacobian(q2))
        axial_stop_impulse=grooveJ.dot(pymunk.Vec2d(*m.axis))
        if not linkage:
            # Interior groove impulses are perpendicular to the guide; only
            # an endpoint generates an axial impulse. Solving can reverse the
            # relative velocity, so its sign cannot decide whether a stop acted.
            # Keep the existing 1e-6 m endpoint band and native 1e-10 impulse
            # significance cutoff; no change to the constraint solve or motion.
            atlo=spos2<=bounds[0]+1e-6 and axial_stop_impulse>1e-10
            athi=spos2>=bounds[1]-1e-6 and axial_stop_impulse< -1e-10
        if linkage:
            # The solved stop impulse can already reverse qdot. Detect the
            # actual native angular constraint impulse, not the post-impact
            # velocity sign (which previously missed a real bottom-out).
            stop_active=abs(linkage.stop.impulse)>1e-10
            atlo=stop_active and abs(q2-m.hi)<=abs(q2-m.lo)
            athi=stop_active and not atlo
        if atlo or athi:
            # Impulse work isolates the guide constraint from wheel contact.
            # Midpoint pre/post velocities give exact kinetic impulse work;
            # this also includes small solver bias work and needs dt refinement.
            contactJ=pymunk.Vec2d(sum(j[0] for j in impulse),sum(j[1] for j in impulse))
            guideJ=p['m6']*(wheel.velocity-wheel_free)-contactJ
            relavg=((wheel_free-chassis_free)+(wheel.velocity-chassis.velocity))*.5
            stop_dissipation+=max(0.,-guideJ.dot(relavg))
            which='compression-stop' if abs(q2-m.hi)<abs(q2-m.lo) else 'extension-stop'
            if not any(e['type']==which for e in events):
                event=dict(t=t,type=which)
                if linkage:event.update(detection='Native hip-stop impulse',nativeHipStopImpulseNms=abs(linkage.stop.impulse))
                else:event.update(detection='Native groove endpoint axial impulse',
                    nativeGuideStopImpulseNs=abs(axial_stop_impulse),nativeGuideAxialImpulseNs=axial_stop_impulse,
                    nativeGrooveImpulseNs=guide.impulse,rotorImpulseRemoved=rotor is not None)
                events.append(event)
            if which=='extension-stop' and case['kind']=='jump':controller.extended=True
        active=bool(points)
        if active and not had_contact:
            had_contact=True;events.append(dict(t=t,type='first-contact',chassisVelocityMmS=pre_vh*1000,preImpulseChassisVelocityMmS=chassis_free.y*1000,preImpulseWheelVelocityZMmS=wheel_free.y*1000,postImpulseChassisVelocityMmS=chassis.velocity.y*1000,postImpulseWheelVelocityZMmS=wheel.velocity.y*1000,contactGapMm=separation(),contactDetection='Actual Pymunk collision impulse'))
        if last_contact and not active and wheel.position.y>radius+1e-7:
            if not any(e['type']=='takeoff' for e in events):events.append(dict(t=t,type='takeoff'))
        if not linkage and case['kind']=='jump' and pre_vh>0>=chassis.velocity.y and any(e['type']=='takeoff' for e in events) and not any(e['type']=='apex' for e in events):
            events.append(dict(t=t,type='apex',chassisZMm=chassis.position.y*1000))
        if case['kind']=='landing' and had_contact and not arrested and pre_vh<0<=chassis.velocity.y:
            arrested=True;events.append(dict(t=t,type='chassis-arrest',beforeStepChassisVelocityMmS=pre_vh*1000,afterStepChassisVelocityMmS=chassis.velocity.y*1000))
        for event in events[event_start:]:
            if event['type'] in ('first-contact','chassis-arrest','compression-stop','extension-stop'):
                ee=actual_energy(q2)
                event['state']=dict(t=t,theta2=q2/R,chassisVelocityMmS=chassis.velocity.y*1000,wheelVelocityZMmS=wheel.velocity.y*1000,
                    kineticJ=sum(ee[k] for k in ('chassisKineticJ','wheelKineticJ','rotorKineticJ','legacyJointRotorKineticJ','linkKineticJ')),motorTorqueNm=control['motorTorqueNm'],
                    motorWorkJ=motor_work,dampingWorkJ=damping_work,motorDissipatedJ=motor_loss,motorCoulombDissipatedJ=motor_coulomb_loss,motorViscousDissipatedJ=motor_viscous_loss,terrainWorkJ=terrain_work,externalWorkJ=external_work,
                    contactDissipationJ=None if rotor or linkage else contact_dissipation,stopDissipationJ=None if rotor or linkage else stop_dissipation,
                    coupledConstraintKineticLossJ=coupled_loss if rotor or linkage else None,positionStabilizationJ=None,**ee)
                impulse_ledger=coupled_loss if rotor or linkage else stop_dissipation+contact_dissipation
                event['state']['energyBalanceResidualJ']=event['state']['kineticJ']+sum(ee[k] for k in ('springEnergyJ','gravityEnergyJ','coggingPotentialJ'))-rows[0]['energyJ']-motor_work-damping_work-terrain_work-external_work+motor_loss+impulse_ledger
        last_contact=active
        if case['undersideOffsetMm'] is not None and chassis.position.y*1000-case['undersideOffsetMm']-floor_under_hip(spec,t)*1000<=0:
            termination='underside-contact';events.append(dict(t=t,type='underside-contact'))
        totalJ[0]+=sum(j[0] for j in impulse);totalJ[1]+=sum(j[1] for j in impulse)
        totalN+=sum(normal_impulses);totalT+=sum(tangent_impulses);sample_points.extend(points);sample_slips.extend(slips)
        max_residual=max(max_residual,residual);max_penetration=max(max_penetration,max(0,-separation()))
        if first_raised is None and any(raised_contact(spec,t,(-pt[0]/1000,pt[2]/1000)) for pt in points):
            first_raised=t;events.append(dict(t=t,type='first-raised-terrain-contact'))
        if not all(math.isfinite(v) for v in (*chassis.position,*chassis.velocity,*wheel.position,*wheel.velocity,wheel.angle,wheel.angular_velocity)):
            raise ValueError('Pymunk contact diverged; reduce dt and inspect inputs.')
        jam=max(0,-separation())>penetration_limit_mm
        bodies=(chassis,linkage.upper,linkage.lower,wheel) if linkage else (chassis,wheel)
        comvz=sum(b.mass*b.velocity.y for b in bodies)/m.total_mass
        observation.step(t,chassis.position.y,comvz if linkage and case['kind']=='jump' else chassis.velocity.y,wheel.position.y,wheel.velocity.y,radius,active,events)
        if case['kind']=='jump':
            bodies=(chassis,linkage.upper,linkage.lower,wheel) if linkage else (chassis,wheel)
            comz=sum(b.mass*b.position.y for b in bodies)/m.total_mass
            comvz=sum(b.mass*b.velocity.y for b in bodies)/m.total_mass
            if observation.takeoff is not None:com_observation.capture_takeoff(t,comz,comvz)
            com_observation.step(t,comz,comvz,active)
            if linkage and com_observation.apex and not any(e['type']=='apex' for e in events):events.append(dict(t=t,type='apex',chassisZMm=chassis.position.y*1000,comZMm=comz*1000,criterion='whole-body COM vertical velocity'))
        assessment_stop=stop_at_assessment and ((case['kind']=='landing' and (arrested or any(e['type']=='compression-stop' for e in events))) or (case['kind']=='jump' and observation.jump_finished()))
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
                scope=dict(mode='terrain-contact',quarterModel=True,fixture=c['fixture'],wheelTerrainBound=False,coordinates='+x left / +z up / mm',
                           chassis='real m1 body pinned at initial hip height' if m.pinned else 'real m1 body, vertical only, fixed horizontal position/pitch',input=('moving seeded inclined terrain' if m.terrain_config and m.terrain_config['schema']=='kinefold/terrain-v2' else 'moving periodic segmented terrain' if m.terrain_config else 'moving sharp terrain') if case['kind']=='terrain-stability' else 'stationary flat floor; actual unilateral wheel contact'),
                warnings=['Experimental two-body quarter model; no tire compliance, rigid chassis collision shape, link mass or hardware validation; entered underside point-clearance stops are assessed.',
                          'Wheel spin is free; ideal backdriven belts reconstruct indices without added inertia or motor lock.',
                          'Gravity acts once on each actual massive body. No prescribed wheel height or forced gap following.',
                          'Contact forces are interval-averaged impulses; force peaks and penetration require timestep refinement.',
                          'B, horn and belts are exact massless reconstruction; A/C and wheel angle are actual Pymunk transforms.'])
    result['caseConfig']=case
    result['caseMetrics']=case_metrics(rows,events,m,case)
    result['energyEstimate']=result['caseMetrics']['energyEstimate']
    diagnostics['energyBalanceResidualJ']=rows[-1]['energyJ']-rows[0]['energyJ']-motor_work-damping_work-terrain_work-external_work+motor_loss+stop_dissipation+contact_dissipation
    if rotor is not None or linkage:
        diagnostics['coupledConstraintKineticLossMeaning']='Signed free-to-solved total kinetic change including native bias and smooth-force splitting; not a physical dissipation measurement.'
        diagnostics.update(coupledConstraintKineticLossJ=coupled_loss,contactDissipationJ=None,stopDissipationJ=None,energyBalanceResidualJ=rows[-1]['energyBalanceResidualJ'])
    diagnostics['stopDissipationMeaning']='Constraint impulse work from free to solved velocities; includes solver bias work, requires timestep refinement.' if rotor is None else 'Stop/contact partition unavailable with coupled rotor; signed coupledConstraintKineticLossJ includes native constraint bias and force-kick splitting work and requires refinement.'
    if 'terrainConfig' in payload:
        result['terrainConfig']=m.terrain_config
        result['snapshot']['terrainConfig']=m.terrain_config
        if case['kind']=='terrain-stability':result['warnings'].append('Source terrain is a synthesized design envelope represented by a rigid periodic 2D profile. Longitudinal grade is simulated only for terrain-v2. Cross-slope, corridor, soil/snow/water behavior and surface-specific friction are not simulated. The chassis follows a vertical slide, not free vehicle translation; guide reactions alter ordinary incline normal-load formulas.')
    if 'caseConfig' in payload:result['snapshot']['caseConfig']=case
    if 'motorConfig' in payload:
        result['snapshot']['motorConfig']=m.motor.config
        result['motorConfig']=m.motor.config
    if 'actuatorConfig' in payload:
        result['actuatorConfig']=m.actuator_config;result['snapshot']['actuatorConfig']=m.actuator_config
    if linkage:
        diagnostics.update(rigidBodies=4,finiteLinkDynamics=True,pivotConstraints=3,gearConstraints=1,grooveConstraints=1,
            integrator='Pymunk four dynamic bodies, three native pivots, ideal absolute-angle belt gear and native hip stops',
            modelRevision='finite-link-contact-v1',totalBodyMassKg=m.total_mass,linkMomentsKgM2={k:m.I[k] for k in ('2','3')},
            frameSource='Actual native chassis, upper/lower rods and wheel transforms',maxConstraintAngleErrorDeg=max(f.get('constraintAngleErrorDeg',0) for f in frames),
            stopLaw='Native hip RotaryLimitJoint; no direct wheel/chassis guide',stopDissipationJ=None)
        result['warnings'][0]='Experimental four-body finite uniform-link quarter model; no tire compliance, chassis collision shape or hardware validation.'
        result['warnings'][-1]='Native rod positions and angles are returned; spring route and belt indices reconstruct the ideal geometry at the actual upper-link angle.'
        diagnostics['coupledConstraintKineticLossMeaning']='Signed exact rigid-link smooth kinetic predictor minus native solved kinetic energy plus terrain work; includes impulses, native bias and force/position splitting. This is numerical combined accounting, not measured physical absorption or a separate contact/stop loss.'
    diagnostics.update(maxRotorConstraintPositionResidualRad=max_rotor_position,maxRotorConstraintVelocityResidualRadS=max_rotor_velocity,reflectedHipInertiaKgM2=m.Jref,rotorConstraintResidualRadS=rotor.velocity_residual if rotor else 0.,rotorConstraintPositionResidualRad=rotor.position_residual if rotor else 0.,rotorConstraintImpulseWorkJ=rotor.constraint_work_j if rotor else 0.)
    diagnostics.update(chassisPinned=m.pinned,initialPinHeightMm=hinitial*1000 if m.pinned else None,
        maxPinPositionErrorMm=max(r['pinPositionErrorMm'] for r in rows) if m.pinned else None,
        pinForceMeaning='Upward fixture-on-chassis force from interval total-assembly momentum balance; includes rigid-contact impulses and native solver effects, not an impact peak.',
        pinForceDeltaMeaning='Change from first finite output-interval force; t=0 force is unavailable.',pinWorkJ=0. if m.pinned else None)
    result['scope']['rideTargetStepEnabled']=case['kind']=='terrain-stability' and bool((m.actuator_config or {}).get('rideTargetStepMm',0))
    result['scope']['rideTargetStepMeaning']='Desired chassis-height step applies only to floating terrain-stability; saved step fields are inactive in jump and landing. No position or wheel contact is prescribed.'
    if m.pinned:
        diagnostics.update(pivotConstraints=diagnostics['pivotConstraints']+1,grooveConstraints=diagnostics['grooveConstraints']-1)
        result['warnings'].append('Only the chassis is pinned at its initial hip height. Wheel rotation, separation and contact remain free. The unchanged height feedback sees no chassis motion; pin-force response is a diagnostic, not a floating-chassis response time. Ideal fixture work is zero; native bias belongs to numerical accounting.')
    if termination=='travel-limit':result['warnings'].append('Stopped after the first integration step leaving declared working travel; no stop impact or position correction was applied.')
    elif termination=='contact-penetration-limit':result['warnings'].append('Stopped at the declared 1mm penetration limit: terrain/guide constraints may be jammed, or the timestep too coarse. No position correction was applied.')
    json.dumps(result,allow_nan=False)
    if rotor is not None:rotor.close()
    result['targetObservations']=observation.result()
    result['targetObservations'].update(com_observation.result())
    result['caseMetrics'].update(com_observation.result())
    if linkage and case['kind']=='jump':result['targetObservations'].update(flightRiseMm=com_observation.result()['jumpComRiseMm'],apexCriterion='whole-body COM vertical velocity')
    return annotate_contact_work(result,m)


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
