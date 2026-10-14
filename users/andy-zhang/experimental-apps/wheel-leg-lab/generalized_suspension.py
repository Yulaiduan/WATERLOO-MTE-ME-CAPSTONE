"""Extend the original suspension fixture to Jonathan's general carrier geometry.

Invocation: existing physics.simulate/build/drive and math_model.simulate_math.
Inputs: validated original SI profile, generalized lengths/radii/masses/angles.
Outputs: existing run/frame channels, actual Pymunk debug primitives or SciPy ODE.
Uses the original spring laws, point-force runtime, smooth position input and UI.
Limits: floating bilateral wheel support, held chassis pitch, ideal equivalent
angular constraints; belt pretensions are reference diagnostics, not added forces.
SciPy stops before impact; Pymunk resolves original-style rotary travel stops.
"""
import math
import numpy as np
from scipy.integrate import solve_ivp
import linkage_geometry as geo
from motion_input import position_state
from spring_mechanisms import geometry,geometry_from_bodies,spring_law,mechanism_metadata,auxiliary_parameters,auxiliary_metadata,calibrate_zero_effective_rate

def parameters(c):
    q=math.radians(c['theta']);_,_,Gy=geo.energy_terms(q,c)
    needed=Gy*c['gravity']+geo.coefficient(c)*geo.loads(c)[4]
    initial=geometry(q,c);ref=initial['input_length'];rest=c['rest_length'];J=initial['jacobian']
    if c['spring_force_law']=='zero_effective':
        if c['balance_spring']:calibrate_zero_effective_rate(c,needed,initial)
    elif c['balance_spring']:
        if abs(J)<1e-10 or c['stiffness']<=0:raise ValueError('Initial spring cannot balance the generalized load; change leverage/rate or select manual preload.')
        eta=1. if c['spring_transmission']=='direct' else -1.;tension=-needed/J;coil=tension/eta
        if (c['spring_mode']=='compression' and coil>1e-9 or c['spring_mode']=='extension' and coil<-1e-9 or c['spring_transmission']=='ideal_rope' and tension<-1e-9):raise ValueError('Spring law/routing cannot provide the required initial load direction.')
        rest=(ref if eta==1 else c['spring_coil_ref'])-coil/c['stiffness']
        if rest<=.005:raise ValueError('Generalized preload needs a positive physical free length; change spring rate/mounts.')
    spring_law(ref,0.,dict(c,rest_length=rest),ref)
    return {'q0':q,'rest':rest,'input_ref':ref,'spring_config':dict(c,rest_length=rest),'auxiliary':auxiliary_parameters(c)}

def spring(q,v,c,p):
    g=geometry_from_bodies(geo.poses(q,c,v),c)
    law=spring_law(g['input_length'],g['input_speed'],p['spring_config'],p['input_ref'])
    return g,law

def derivative(t,state,c,p):
    q,v=state;M,Mp,Gy=geo.energy_terms(q,c);g,law=spring(q,v,c,p)
    ratio=geo.ratios(c)[0];raw=c['knee_kp']*ratio*(p['q0']-q)-c['knee_kd']*ratio*v
    torque=max(-c['torque_limit'],min(c['torque_limit'],raw))
    _,_,base_accel=position_state(t,c)
    Q=-law['tension']*g['jacobian']+ratio*torque-geo.coefficient(c)*geo.loads(c)[4]
    return v,(Q-Gy*(c['gravity']+base_accel)-.5*Mp*v*v)/M

def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])

def observe(t,q,v,a,c,p):
    z,zv,za=position_state(t,c);sites,angles,rates=geo.points(q,c);ms=geo.masses(c);Is=geo.inertias(c)
    pos={key:np.array(value[0])+[0,z] for key,value in sites.items()}
    vel={key:np.array(value[1])*v+[0,zv] for key,value in sites.items()}
    acc={key:np.array(value[1])*a+np.array(value[2])*v*v+[0,za] for key,value in sites.items()}
    g,law=spring(q,v,c,p);forces={key:np.zeros(2) for key in ('hip','upper','lower')};moments={key:0. for key in forces}
    for site in g['force_sites']:
        force=law['tension']*np.array(site['direction']);key=site['body'];forces[key]+=force;moments[key]+=cross(np.array(site['world'])+np.array([0,z])-pos[key],force)
    gravity=np.array([0.,-c['gravity']]);f1=forces['hip']-ms['hip']*(acc['hip']-gravity)
    f5=ms['compound']*(acc['compound']-gravity)
    f2=f1+forces['upper']-ms['upper']*(acc['upper']-gravity)-f5
    f3=f2+forces['lower']-ms['lower']*(acc['lower']-gravity)
    fx,fy,fn,ft,Mw=geo.loads(c);external=np.array([fx,fy]);driver=ms['wheel']*(acc['hub']-gravity)-external-f3
    ab,cd,ef=geo.ratios(c);k=ab-1;K=geo.coefficient(c)
    raw=c['knee_kp']*ab*(p['q0']-q)-c['knee_kd']*ab*v;torque=max(-c['torque_limit'],min(c['torque_limit'],raw))
    lower_moment=cross(pos['knee']-pos['lower'],f2)+cross(pos['hub']-pos['lower'],-f3)+moments['lower']
    guide=Is['lower']*k*a-lower_moment-torque
    wheel_couple=Is['wheel']*(-K)*a-Mw;compound_couple=Is['compound']*(cd-1)*a
    upper_moment=cross(pos['hip']-pos['upper'],f1)+cross(pos['knee']-pos['upper'],-f2-f5)+moments['upper']
    angular_error=abs(-Is['upper']*a-(upper_moment-torque+k*guide+(cd-1)*compound_couple-K*wheel_couple))
    KE=.5*sum(ms[key]*float(vel[key]@vel[key])+Is[key]*(rates[key]*v)**2 for key in ms)
    PE=c['gravity']*sum(ms[key]*pos[key][1] for key in ms)+law['energy']
    initial=geo.points(p['q0'],c)[0]['hip'][0];dh=pos['hip'][1]-initial[1]
    row={'t':float(t),'input':z,'input_mm':z*1000,'theta_deg':math.degrees(q),'height':pos['hip'][1]-pos['hub'][1],
         'theta2_deg':180-math.degrees(q),'theta3_deg':c['link_phase']+k*math.degrees(q),
         'theta5_deg':math.degrees(angles['compound'])+c['mount_angle'],'theta6_deg':math.degrees(angles['wheel'])+c['mount_angle'],
         'driver_force':driver[1],'driver_fx':driver[0],'driver_check':0.,'chassis_displacement':dh,'chassis_displacement_mm':dh*1000,
         'chassis_dx_mm':(pos['hip'][0]-initial[0])*1000,'spring_length':g['input_length'],'spring_tension':law['tension'],
         'spring_elastic_tension':law['elastic_tension'],'spring_damper_tension':law['damper_tension'],
         'spring_coil_length':law['coil_length'],'spring_coil_load':law['coil_load'],'spring_coil_tension':law['coil_tension'],
         'spring_engaged':float(law['engaged']),'spring_slack':float(law['slack']),'spring_energy_J':law['energy'],
         'spring_input_speed':g['input_speed'],'spring_generalized_force':-law['tension']*g['jacobian'],
         'spring_knee_moment':moments['lower'],'actuator_torque':torque,'actuator_command':raw,
         'guide_link_torque':guide,'guide_hip_reaction':-ab*guide,'guide_tension_difference_N':guide/c['guide_knee_radius'],
         'guide_belt_speed_relative':c['guide_hip_radius']*v,'stop_knee_torque':0.,'wheel_external_moment':Mw,
         'wheel_drive_reaction':-wheel_couple,'wheel_drive_check':0.,'wheel_speed':-K*v,'wheel_accel':-K*a,
         'upper_speed':-v,'lower_speed':k*v,'upper_accel':-a,'lower_accel':k*a,'knee_speed':ab*v,'knee_accel':ab*a,
         'leg_motor_equivalent_Nm':-ab*torque,'drive_motor_reaction_Nm':Is['compound']*cd*(cd-1)*a-Is['wheel']*cd*ef*K*a-Mw*cd*ef,
         'pin_error':0.,'phase_error':0.,'reaction_check':0.,'angular_check':angular_error,
         'position_command':z,'position_actual':z,'position_actual_mm':z*1000,'position_error':0.,'position_velocity_command':zv,'position_accel_command':za,
         'kinetic_energy_J':KE,'potential_energy_J':PE,'mechanical_energy_J':KE+PE,
         'driver_power_W':float(driver@vel['hub']),'bias_power_W':float(external@vel['hub'])+Mw*(-K*v),
         'actuator_power_W':ab*torque*v,'dissipation_power_W':law['dissipation_rate'],'total_mass_kg':sum(ms.values()),
         'Fn_N':fn,'Ft_N':ft,'Fy_N':fx,'Fz_N':fy,
         'hip_mount_fx':-f1[0]+forces['hip'][0],'hip_mount_fy':-f1[1]+forces['hip'][1]}
    for label,key in (('hub','hub'),('chassis','hip')):
        for i,axis in enumerate(('x','y')):row[label+'_v'+axis]=vel[key][i];row[label+'_a'+axis]=acc[key][i]
    for i,(f,key) in enumerate(((f1,'hip'),(f2,'knee'),(f3,'hub')),1):
        row.update({f'j{i}_fx':f[0],f'j{i}_fy':f[1],f'j{i}_force':float(np.linalg.norm(f)),f'j{i}_vx':vel[key][0],f'j{i}_vy':vel[key][1],f'j{i}_ax':acc[key][0],f'j{i}_ay':acc[key][1]})
    for key in forces:
        for i,axis in enumerate(('x','y')):row['spring_'+key+'_f'+axis]=forces[key][i];row['primary_spring_'+key+'_f'+axis]=forces[key][i];row['aux_spring_'+key+'_f'+axis]=0.
    heightJ=sites['hip'][1][1]
    if abs(heightJ)>1e-10:
        lift=-law['tension']*g['jacobian']/heightJ
        row.update(spring_equivalent_lift_N=lift,spring_elastic_equivalent_lift_N=-law['elastic_tension']*g['jacobian']/heightJ,
                   spring_gravity_equivalent_N=geo.energy_terms(q,c)[2]*c['gravity']/heightJ,
                   spring_balance_residual_N=lift-geo.energy_terms(q,c)[2]*c['gravity']/heightJ)
    row={key:float(value) for key,value in row.items()}
    frame={'t':float(t),'hip':pos['hip'].tolist(),'knee':pos['knee'].tolist(),'hub':pos['hub'].tolist(),'tip':pos['tip'].tolist(),
           'upper_angle':angles['upper'],'lower_angle':angles['lower'],'wheel_angle':angles['wheel'],'compound_angle':angles['compound'],
           'position_target':pos['hub'].tolist(),'debug_draw':[],'spring_geometry':geometry_from_bodies(geo.poses(q,c,v,z,zv),c),'spring_coil_length':law['coil_length']}
    return row,frame

def result(c,p,rows,frames,engine,model,diagnostics,warnings):
    keys=('j1_force','j2_force','j3_force','spring_tension','actuator_torque','guide_hip_reaction','stop_knee_torque','driver_force','chassis_vy','chassis_ay','knee_speed','knee_accel')
    peaks={key:{'value':max(rows,key=lambda r:abs(r[key]))[key],'t':max(rows,key=lambda r:abs(r[key]))['t']} for key in keys}
    return {'backend':'pymunk' if engine.startswith('Pymunk') else 'math','config':c,'engine':engine,'model':model,'rows':rows,'frames':frames,'peaks':peaks,
            'actual_rest_length':p['rest'],'position_origin':[0.,0.],'spring_mechanism':mechanism_metadata(p['spring_config'],p['input_ref']),
            'auxiliary_spring':{'enabled':False},'passive_stability':stability(c,p),
            'diagnostics':diagnostics,'warnings':warnings,'equation_check_errors':{},
            'scope':'Original floating-chassis wheel-position fixture and spring catalog, extended with exact general carrier-belt geometry. Independent SciPy integration / actual Pymunk Space.step. Ideal equivalent rotational constraints do not resolve physical belt-span bearing forces; Jon fixed-A statics are separate reference diagnostics. No unilateral contact/rolling/3D packaging.'}

def stability(c,p):
    q=p['q0'];eps=1e-5
    def values(theta):
        g,law=spring(theta,0.,c,p);sites=geo.points(theta,c)[0];h=sites['hip'][0][1];J=sites['hip'][1][1]
        Q=-law['elastic_tension']*g['jacobian']-geo.energy_terms(theta,c)[2]*c['gravity']-geo.coefficient(c)*geo.loads(c)[4]
        return h,J,Q
    h,J,Q=values(q)
    if abs(J)<1e-9:return {'classification':'not_applicable','reason':'Initial height Jacobian is zero; height-coordinate ride stiffness is undefined.','notes':[]}
    hm,Jm,Qm=values(q-eps);hp,Jp,Qp=values(q+eps)
    if min(abs(Jm),abs(Jp),abs(h-hm),abs(hp-h))<1e-12:return {'classification':'not_applicable','reason':'Initial pose is too close to a height-path turning point for finite height stiffness.','notes':[]}
    left=-(Q/J-Qm/Jm)/(h-hm);right=-(Qp/Jp-Q/J)/(hp-h)
    classification='unstable' if min(left,right)<-1e-3 else 'restoring' if min(left,right)>1e-3 else 'neutral'
    notes=['Generalized preload balances only the initial pose; edited ratios/mounting need not retain exact constant lift.']
    return {'classification':classification,'net_ride_stiffness_N_m':(left+right)/2,'left_ride_stiffness_N_m':left,'right_ride_stiffness_N_m':right,
            'initial_force_balance_residual_N':Q/J,'theta_deg':c['theta'],'active_controller_excluded':True,
            'scope':'Local spring/gravity/wheel-couple derivative along the actual general linkage path; held wheel, fixed chassis pitch. Excludes damping/feedback/contact and whole-range stability.','notes':notes}

def simulate_math(c,rtol=1e-9,atol=1e-11,max_step=None):
    if not all(math.isfinite(x) and 0<x<1 for x in (rtol,atol)):raise ValueError('Solver tolerances must be finite and between zero and one.')
    if max_step is not None and (not math.isfinite(max_step) or max_step<=0):raise ValueError('Maximum step must be positive finite seconds.')
    p=parameters(c)
    if c['aux_spring_enabled']:raise ValueError('General geometry retains one original primary spring; disable the historical auxiliary strut.')
    def low(t,y):return y[0]-math.radians(c['theta_min'])
    def high(t,y):return math.radians(c['theta_max'])-y[0]
    low.terminal=high.terminal=True;low.direction=high.direction=-1
    sol=solve_ivp(lambda t,y:derivative(t,y,c,p),(0,c['duration']),(p['q0'],0.),method='DOP853',rtol=rtol,atol=atol,max_step=max_step or min(.01,4*c['dt']),dense_output=True,events=(low,high))
    if not sol.success:raise ValueError(sol.message)
    times=np.arange(1,math.floor(sol.t[-1]/c['dt']+1e-10)+1)*c['dt'];rows=[];frames=[]
    for i,t in enumerate(times):
        q,v=sol.sol(t);a=derivative(t,(q,v),c,p)[1];row,frame=observe(t,q,v,a,c,p);rows.append(row)
        if i%max(1,math.ceil(1/(120*c['dt'])))==0 or i==len(times)-1:frame['index']=i;frames.append(frame)
    if not rows:raise ValueError('Generalized run reached a travel stop before its first output sample.')
    if any(not all(math.isfinite(x) for x in row.values()) for row in rows):raise ValueError('Non-finite general mathematical state.')
    return result(c,p,rows,frames,'SciPy DOP853 / generalized original suspension',{'renderer':'independent general kinematics','bodies':[],'constraints':[],'shapes':[],'debug_scale':600},
                  {'max_angular_balance_Nm':max(r['angular_check'] for r in rows)},['Travel limit reached; independent mathematical run ends before impact.'] if sol.status==1 else [])

def build(c):
    import pymunk
    from pymunk import Vec2d
    p=parameters(c);q=p['q0'];sites,angles,rates=geo.points(q,c);ms=geo.masses(c);Is=geo.inertias(c)
    space=pymunk.Space();space.gravity=(0,-c['gravity']);space.iterations=int(c['iterations']);bodies={}
    for key in ('hip','upper','lower','wheel')+ (('compound',) if ms['compound']>0 else ()):
        b=pymunk.Body(ms[key],float('inf') if key=='hip' else Is[key]);b.position=sites[key][0];b.angle=angles[key];bodies[key]=b;space.add(b)
    hip,u,l,w=(bodies[key] for key in ('hip','upper','lower','wheel'));L,L3,e=c['length'],c['lower_length'],c['extension']
    shapes={'upper_link':pymunk.Segment(u,(-L/2,0),(L/2,0),.009),'lower_link':pymunk.Segment(l,(-(L3+e)/2,0),((L3+e)/2,0),.009),'wheel':pymunk.Circle(w,c['radius'])}
    if c['chassis_shape_enabled']:shapes['chassis']=pymunk.Poly.create_box(hip,(.14,.055))
    if c['guide_pulleys_visible']:
        shapes['guide_hip_pulley']=pymunk.Circle(hip,c['guide_hip_radius'])
        shapes['guide_knee_pulley']=pymunk.Circle(l,c['guide_knee_radius'],(-(L3-e)/2,0))
    for i,shape in enumerate(shapes.values()):shape.sensor=True;shape.filter=pymunk.ShapeFilter(group=1);shape.color=((52,152,219,255),(39,174,96,255),(241,196,15,130),(112,121,134,230))[min(i,3)]
    space.add(*shapes.values())
    j1=pymunk.PivotJoint(hip,u,(0,0),(-L/2,0));j2=pymunk.PivotJoint(u,l,(L/2,0),(-(L3-e)/2,0));j3=pymunk.PivotJoint(l,w,((L3+e)/2,0),(0,0))
    def gear(target,rate):
        if abs(rate)<1e-12:return pymunk.GearJoint(hip,target,target.angle,1)
        ratio=-1/rate;return pymunk.GearJoint(u,target,target.angle*ratio-u.angle,ratio)
    guide=gear(l,rates['lower']);wheel_drive=gear(w,rates['wheel']);ab=geo.ratios(c)[0];phi=math.radians(c['link_phase'])
    stop=pymunk.RotaryLimitJoint(u,l,ab*math.radians(c['theta_min'])+phi-math.pi,ab*math.radians(c['theta_max'])+phi-math.pi)
    carriage=pymunk.Body(body_type=pymunk.Body.KINEMATIC);carriage.position=w.position;driver=pymunk.PivotJoint(carriage,w,(0,0),(0,0));space.add(carriage)
    constraints=[j1,j2,j3,guide,wheel_drive,stop,driver];compound_joint=compound_gear=None
    if 'compound' in bodies:
        compound_joint=pymunk.PivotJoint(u,bodies['compound'],(L/2,0),(0,0));compound_gear=gear(bodies['compound'],rates['compound']);constraints.extend((compound_joint,compound_gear))
    for joint in constraints:joint.collide_bodies=False
    space.add(*constraints)
    return {'space':space,**bodies,'moving':w,'j1':j1,'j2':j2,'j3':j3,'guide':guide,'stop':stop,'wheel_drive':wheel_drive,'spring':None,'driver':driver,'carriage':carriage,
            'driver_origin':Vec2d(*w.position),'shapes':shapes,'manual_spring':True,'rest':p['rest'],'spring_input_reference':p['input_ref'],'cache':{},'auxiliary':{'enabled':False},
            'general_parameters':p,'compound_joint':compound_joint,'compound_gear':compound_gear}

def drive(m,c,t,dt):
    from pymunk import Vec2d
    import suspension_runtime as suspension
    z,_,_=position_state(t,c);z1,v1,a1=position_state(t+dt,c);m['carriage'].velocity=(0,(z1-z)/dt);m['position_command']=(z1,v1,a1)
    q=-m['upper'].angle-math.radians(c['mount_angle']);v=-m['upper'].angular_velocity;ab=geo.ratios(c)[0]
    raw=c['knee_kp']*ab*(m['general_parameters']['q0']-q)-c['knee_kd']*ab*v;torque=max(-c['torque_limit'],min(c['torque_limit'],raw))
    m['upper'].torque=-torque;m['lower'].torque=torque;fx,fy,fn,ft,Mw=geo.loads(c);force=Vec2d(fx,fy);point=m['wheel'].position
    if c['load_point']=='contact':point-=c['radius']*Vec2d(math.sin(math.radians(c['contact_beta'])),math.cos(math.radians(c['contact_beta'])))
    m['wheel'].apply_force_at_world_point(force,point);m['wheel_external_moment']=Mw;suspension.update(m,c)
    return z,torque,raw,force

def simulate_physics(c):
    import pymunk
    from debug_view import capture,describe
    m=build(c);p=m['general_parameters'];dt=c['dt'];rows=[];frames=[];pin_error=0.;tracking=0.;guide_error=0.;force_error=0.;angular_error=0.
    for i in range(math.ceil(c['duration']/dt)):
        keys=[key for key in ('hip','upper','lower','wheel','compound') if m.get(key)]
        old_vel={key:np.array(m[key].velocity) for key in keys};old_spin={key:m[key].angular_velocity for key in keys}
        old=-m['upper'].angular_velocity;_,applied_torque,applied_command,_=drive(m,c,i*dt,dt);m['space'].step(dt);t=(i+1)*dt
        q=-m['upper'].angle-math.radians(c['mount_angle']);v=-m['upper'].angular_velocity;a=(v-old)/dt
        row,frame=observe(t,q,v,a,c,p)
        row.update(actuator_torque=applied_torque,actuator_command=applied_command,leg_motor_equivalent_Nm=-geo.ratios(c)[0]*applied_torque)
        for key,joint in (('hip',m['j1']),('knee',m['j2']),('hub',m['j3'])):
            point=joint.b.local_to_world(joint.anchor_b);frame[key]=list(point);pin_error=max(pin_error,(joint.a.local_to_world(joint.anchor_a)-point).length)
        L3=c['lower_length'];frame['tip']=list(m['lower'].local_to_world((-(L3+c['extension'])/2,0)))
        frame['upper_angle']=m['upper'].angle;frame['lower_angle']=m['lower'].angle;frame['wheel_angle']=m['wheel'].angle
        frame['compound_angle']=m['compound'].angle if m.get('compound') else geo.points(q,c)[1]['compound']
        frame['spring_geometry']=geometry_from_bodies({key:m[key] for key in ('hip','upper','lower')},c)
        frame['spring_coil_length']=m['spring_state']['coil_length'];frame['debug_draw']=capture(m['space'])
        acc={key:(np.array(m[key].velocity)-old_vel[key])/dt for key in keys};rot={key:(m[key].angular_velocity-old_spin[key])/dt for key in keys}
        gravity=np.array([0.,-c['gravity']]);sf={key:np.array(value) for key,value in m['spring_loads'].items()}
        f1=sf['hip']-c['chassis_mass']*(acc['hip']-gravity)
        f5=c['compound_mass']*(acc['compound']-gravity) if m.get('compound') else np.zeros(2)
        f2=f1+sf['upper']-c['upper_mass']*(acc['upper']-gravity)-f5
        f3=f2+sf['lower']-c['lower_mass']*(acc['lower']-gravity)
        fx,fy,_,_,Mw=geo.loads(c);driver=c['wheel_mass']*(acc['wheel']-gravity)-np.array([fx,fy])-f3
        for j,force in enumerate((f1,f2,f3),1):
            row.update({f'j{j}_fx':force[0],f'j{j}_fy':force[1],f'j{j}_force':float(np.linalg.norm(force))})
            force_error=max(force_error,abs(float(np.linalg.norm(force))-m[f'j{j}'].impulse/dt))
        row.update(driver_fx=driver[0],driver_force=driver[1],driver_check=abs(float(np.linalg.norm(driver))-m['driver'].impulse/dt),
                   chassis_vx=m['hip'].velocity.x,chassis_vy=m['hip'].velocity.y,chassis_ax=acc['hip'][0],chassis_ay=acc['hip'][1],
                   hub_vx=m['wheel'].velocity.x,hub_vy=m['wheel'].velocity.y,hub_ax=acc['wheel'][0],hub_ay=acc['wheel'][1],reaction_check=force_error)
        A,B,C=(np.array(frame[key]) for key in ('hip','knee','hub'));U=np.array(m['upper'].position);D=np.array(m['lower'].position)
        upper_moment=cross(A-U,f1)+cross(B-U,-f2-f5)+m['spring_torques']['upper']
        lower_moment=cross(B-D,f2)+cross(C-D,-f3)+m['spring_torques']['lower']
        ab,cd,ef=geo.ratios(c);k=ab-1;K=geo.coefficient(c);torque=row['actuator_torque']
        wheel_couple=m['wheel'].moment*rot['wheel']-Mw;compound_couple=m['compound'].moment*rot['compound'] if m.get('compound') else 0.
        ru=m['upper'].moment*rot['upper']-upper_moment+torque-(cd-1)*compound_couple+K*wheel_couple
        rl=m['lower'].moment*rot['lower']-lower_moment-torque;guide=(ru+rl)/ab;stop=rl-guide
        angular_error=max(angular_error,abs(abs(guide)-abs(m['guide'].impulse/dt)),abs(abs(stop)-abs(m['stop'].impulse/dt)))
        row.update(guide_link_torque=guide,guide_hip_reaction=-ab*guide,guide_tension_difference_N=guide/c['guide_knee_radius'],
                   stop_knee_torque=stop,angular_check=angular_error,wheel_drive_reaction=-wheel_couple,
                   drive_motor_reaction_Nm=cd*compound_couple+cd*ef*wheel_couple)
        actual_geometry=frame['spring_geometry'];actual_law=spring_law(actual_geometry['input_length'],actual_geometry['input_speed'],p['spring_config'],p['input_ref'])
        kinetic=.5*sum(m[key].mass*m[key].velocity.length_squared+(0 if key=='hip' else m[key].moment*m[key].angular_velocity**2) for key in keys)
        potential=c['gravity']*sum(m[key].mass*m[key].position.y for key in keys)+actual_law['energy']
        row.update(kinetic_energy_J=kinetic,potential_energy_J=potential,mechanical_energy_J=kinetic+potential,
                   spring_length=actual_geometry['input_length'],spring_energy_J=actual_law['energy'],spring_coil_length=actual_law['coil_length'],
                   spring_input_speed=actual_geometry['input_speed'],wheel_speed=m['wheel'].angular_velocity,wheel_accel=rot['wheel'],
                   upper_speed=m['upper'].angular_velocity,lower_speed=m['lower'].angular_velocity,upper_accel=rot['upper'],lower_accel=rot['lower'],
                   knee_speed=m['lower'].angular_velocity-m['upper'].angular_velocity,knee_accel=rot['lower']-rot['upper'],
                   driver_power_W=float(driver@np.array(m['wheel'].velocity)),bias_power_W=float(np.array([fx,fy])@np.array(m['wheel'].velocity))+Mw*m['wheel'].angular_velocity,
                   actuator_power_W=applied_torque*(m['lower'].angular_velocity-m['upper'].angular_velocity),
                   chassis_displacement=m['hip'].position.y-geo.points(p['q0'],c)[0]['hip'][0][1],chassis_dx_mm=(m['hip'].position.x-geo.points(p['q0'],c)[0]['hip'][0][0])*1000)
        row['chassis_displacement_mm']=row['chassis_displacement']*1000
        error=frame['hub'][1]-row['position_command'];tracking=max(tracking,abs(error));guide_error=max(guide_error,abs(m['lower'].angle-geo.points(q,c)[1]['lower']))
        row.update(position_actual=frame['hub'][1],position_actual_mm=frame['hub'][1]*1000,position_error=error,pin_error=pin_error,phase_error=guide_error,
                   )
        if not all(math.isfinite(value) for value in row.values()):raise ValueError('Non-finite general Pymunk state; refine the timestep.')
        rows.append(row)
        if i%max(1,math.ceil(1/(120*dt)))==0 or i==math.ceil(c['duration']/dt)-1:frame['index']=i;frames.append(frame)
    warnings=[]
    if tracking>.0005 or pin_error>.0005 or guide_error>.001:warnings.append('Generalized constraint/position drift elevated; refine timestep/iterations.')
    if force_error>.01 or angular_error>.01:warnings.append('Generalized force/torque reconstruction differs from solver impulses; refine timestep before interpreting peak loads.')
    return result(c,p,rows,frames,'Pymunk '+pymunk.version+' / generalized original suspension',describe(m),
                  {'max_pin_error_m':pin_error,'max_position_error_m':tracking,'max_guide_error_rad':guide_error,'max_force_check_N':force_error,'max_torque_check_Nm':angular_error},warnings)
