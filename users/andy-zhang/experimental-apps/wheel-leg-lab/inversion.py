"""Invertible wheel-leg torque studies with independent SciPy and Pymunk.

Invocation: config(), preview(), simulate(values, backend='pymunk'); server
routes /api/inversion/*. Inputs SI, configured angles degrees and clockwise
femur torque positive. Outputs rows/geometry, contact/pin impulses and energy.
Ground fixture: free heave/translation, held chassis pitch, frictionless floor;
wheel/chassis contacts are real, self-collision disabled for staggered planes.
SciPy and comparable Pymunk fixture hold J1, without floor/contact. Neither
model certifies 3D clearance, strength, rope winding history or hardware limits.
"""
import math
from copy import deepcopy
import numpy as np
import pymunk
from scipy.integrate import solve_ivp
from debug_view import capture
import invertible_spring as springs
from angle_stops import integrate as integrate_stops

DEFAULTS={'preset':'dual_rope','fixture':'ground','start_inverted':True,'initial_angle_deg':45.,
 'angle_limit_enabled':True,'angle_min_deg':-80.,'angle_max_deg':80.,
 'length':.273,'extension':.05,'radius':.2,'upper_mass':.6,'lower_mass':.65,'wheel_mass':1.5,'chassis_mass':8.,
 'gravity':9.80665,'stiffness':5000.,'auto_rate':True,'ride_angle_deg':45.,'damping':0.,'preload':.01,
 'coil_free_length':.12,'cap_reference_distance':.1,'rod_length':.12,'pulley_radius':.03,'routing_radius':.01,'routing_distance':.06,'routing_offset':.0101,
 'rope_routing':'central_wrap','rope_eye_offset':.00002,
 'attachment_offset_deg':5.,'femur_anchor_distance':.05,'crank_radius':.05,
 'femur_torque':100.,'torque_start':.1,'torque_width':.24,'torque_rise':.04,'torque_fall':.04,
 'duration':1.,'dt':.00025,'iterations':400}

def config(values=None):
    c=deepcopy(DEFAULTS)
    if values:
        if not isinstance(values,dict) or set(values)-set(c):raise ValueError('Unknown inversion configuration field.')
        c.update(values)
        if c['preset']=='knee_bellcrank' and 'torque_width' not in values:c['torque_width']=.17
        if not c['start_inverted'] and 'initial_angle_deg' not in values:c['initial_angle_deg']=45.
    for key,default in DEFAULTS.items():
        if isinstance(default,bool):
            if not isinstance(c[key],bool):raise ValueError(key+' must be boolean.')
        elif isinstance(default,(int,float)):
            if isinstance(c[key],bool) or not isinstance(c[key],(int,float)) or not math.isfinite(c[key]):raise ValueError(key+' must be finite.')
    if c['preset'] not in ('dual_rope','knee_bellcrank'):raise ValueError('Select dual_rope or knee_bellcrank.')
    if c['fixture'] not in ('ground','hip_fixed'):raise ValueError('Select ground or hip_fixed fixture.')
    if c['rope_routing'] not in ('central_wrap','central_face','outer_rim'):raise ValueError('Select central_wrap routing, or an explicit archived route.')
    limits={'length':(.15,.8),'extension':(.005,.15),'radius':(.05,.4),'initial_angle_deg':(5,175),'ride_angle_deg':(10,80),
      'angle_min_deg':(-89,-5),'angle_max_deg':(5,89),
      'upper_mass':(.01,20),'lower_mass':(.01,20),'wheel_mass':(.01,30),'chassis_mass':(.1,100),'gravity':(0,20),
      'stiffness':(0,100000),'damping':(0,2000),'preload':(0,.1),'coil_free_length':(.02,1),
      'pulley_radius':(.005,.1),'routing_radius':(.003,.04),'routing_distance':(.01,.2),'routing_offset':(.003,.15),
      'rope_eye_offset':(0,.02),
      'attachment_offset_deg':(0,30),'femur_anchor_distance':(.005,.15),'cap_reference_distance':(.01,.3),'rod_length':(.02,.6),'crank_radius':(.005,.15),
      'femur_torque':(-500,500),'torque_start':(0,10),'torque_width':(.02,10),'torque_rise':(.001,2),'torque_fall':(.001,2),
      'duration':(.1,10),'dt':(.000125,.002),'iterations':(30,1000)}
    for key,(lo,hi) in limits.items():
        if not lo<=c[key]<=hi:raise ValueError(f'{key} must be in [{lo}, {hi}] SI.')
    if c['extension']>=c['length'] or c['femur_anchor_distance']>=c['length']:raise ValueError('Extension and femur attachment distance must be shorter than the link.')
    if c['preset']=='dual_rope' and (c['cap_reference_distance']>=c['length'] or c['rod_length']<c['coil_free_length']-c['preload']+.005):
        raise ValueError('The rod eye must remain outside the coil housing, and its reference location must lie along the femur.')
    if c['torque_rise']+c['torque_fall']>c['torque_width']:raise ValueError('Torque rise/fall must fit in pulse width.')
    if c['duration']/c['dt']>30000:raise ValueError('Limit each run to 30000 steps.')
    if c['iterations']!=int(c['iterations']):raise ValueError('Iterations must be integral.')
    signed_initial=c['initial_angle_deg']*(-1 if c['start_inverted'] else 1)
    if c['angle_limit_enabled'] and not c['angle_min_deg']<=signed_initial<=c['angle_max_deg']:
        raise ValueError('Initial angle must lie inside the enabled knee-right limits.')
    p=springs.prepare(c)
    if c['auto_rate']:
        q=math.radians(c['ride_angle_deg']);trial=springs.state(q,0.,dict(c,stiffness=1.,damping=0.),p)
        needed=c['gravity']*(2*c['length']*c['chassis_mass']+1.5*c['length']*c['upper_mass']+.5*(c['length']+c['extension'])*c['lower_mass'])*math.cos(q)
        if trial['torque']<=1e-10:raise ValueError('This geometry cannot support the normal ride pose with positive compression; disable auto rate or change mounts.')
        c['stiffness']=needed/trial['torque']
        if c['stiffness']>100000:raise ValueError('Required automatic spring rate exceeds the demo bound.')
    # Check a full revolution, not just the initial pose.
    for q in np.linspace(-math.pi,math.pi,181):springs.state(float(q),0.,c,p)
    return c

def torque(t,c):
    z=t-c['torque_start'];width=c['torque_width']
    if z<=0 or z>=width:return 0.
    ramp=min(1,z/c['torque_rise'],(width-z)/c['torque_fall'])
    return c['femur_torque']*(10*ramp**3-15*ramp**4+6*ramp**5)

def initial(c):
    q=math.radians(c['initial_angle_deg'])*(-1 if c['start_inverted'] else 1)
    H=.055/2 if c['start_inverted'] else c['radius']+2*c['length']*math.sin(q)
    if c['fixture']=='ground' and H-2*c['length']*math.sin(q)<c['radius']-1e-10:
        raise ValueError('Chassis-ground start places the wheel through the floor; use a larger inverted angle.')
    return q,H

def build(c):
    q,H=initial(c);L,e=c['length'],c['extension'];A=pymunk.Vec2d(0,H)
    B=A+pymunk.Vec2d(L*math.cos(q),-L*math.sin(q));C=A+pymunk.Vec2d(0,-2*L*math.sin(q))
    space=pymunk.Space();space.gravity=(0,-c['gravity']);space.iterations=int(c['iterations']);space.collision_slop=.0001
    hip=pymunk.Body(c['chassis_mass'],float('inf')) if c['fixture']=='ground' else pymunk.Body(body_type=pymunk.Body.STATIC);hip.position=A
    upper=pymunk.Body(c['upper_mass'],c['upper_mass']*L*L/12);upper.position=(A+B)/2;upper.angle=-q
    lower=pymunk.Body(c['lower_mass'],c['lower_mass']*(L+e)**2/12);lower.angle=q-math.pi;lower.position=B+pymunk.Vec2d(-math.cos(q),-math.sin(q))*(L-e)/2
    wheel=pymunk.Body(c['wheel_mass'],.5*c['wheel_mass']*c['radius']**2);wheel.position=C
    space.add(hip,upper,lower,wheel)
    shapes=[pymunk.Segment(upper,(-L/2,0),(L/2,0),.009),pymunk.Segment(lower,(-(L+e)/2,0),((L+e)/2,0),.009),pymunk.Circle(wheel,c['radius']),pymunk.Poly.create_box(hip,(.14,.055))]
    for i,shape in enumerate(shapes):
        shape.filter=pymunk.ShapeFilter(group=1);shape.sensor=i<2 or c['fixture']!='ground';shape.friction=0.;shape.elasticity=0.
        shape.color=[(52,152,219,255),(39,174,96,255),(241,196,15,150),(112,121,134,230)][i]
    shapes[2].collision_type=1;shapes[3].collision_type=2
    if c['preset']=='dual_rope':
        pulley=pymunk.Circle(lower,c['pulley_radius'],(-(L-e)/2,0));pulley.sensor=True;pulley.filter=pymunk.ShapeFilter(group=1);pulley.color=(210,165,76,230);shapes.append(pulley)
        for sign,colour in [(1,(225,80,90,255)),(-1,(70,145,235,255))]:
            pulley=pymunk.Circle(upper,c['routing_radius'],(L/2-c['routing_distance'],sign*c['routing_offset']));pulley.sensor=True;pulley.filter=pymunk.ShapeFilter(group=1);pulley.color=colour;shapes.append(pulley)
    floor=pymunk.Segment(space.static_body,(-20,0),(20,0),0);floor.collision_type=3;floor.friction=0.;floor.elasticity=0.;floor.color=(130,130,130,255)
    if c['fixture']=='ground':space.add(floor)
    space.add(*shapes)
    joints=[pymunk.PivotJoint(hip,upper,(0,0),(-L/2,0)),pymunk.PivotJoint(upper,lower,(L/2,0),(-(L-e)/2,0)),pymunk.PivotJoint(lower,wheel,((L+e)/2,0),(0,0))]
    guide=pymunk.GearJoint(upper,lower,math.pi,-1.)
    for joint in [*joints,guide]:joint.collide_bodies=False
    space.add(*joints,guide)
    stop=None
    if c['angle_limit_enabled']:
        stop=pymunk.RotaryLimitJoint(hip,upper,-math.radians(c['angle_max_deg']),-math.radians(c['angle_min_deg']))
        stop.collide_bodies=False;space.add(stop)
    m={'space':space,'hip':hip,'upper':upper,'lower':lower,'wheel':wheel,'joints':joints,'guide':guide,'stop':stop,'prepared':springs.prepare(c),'contacts':{'wheel':0.,'chassis':0.},'steps':0,'t':0.,'work':0.,'dissipated':0.,'H0':H}
    def contact(key):
        def capture_contact(arbiter,space,data):m['contacts'][key]+=abs(arbiter.total_impulse.y)
        return capture_contact
    if c['fixture']=='ground':
        space.on_collision(1,3,post_solve=contact('wheel'));space.on_collision(2,3,post_solve=contact('chassis'))
    return m

def coordinates(m,c):
    q=(m['lower'].angle-m['upper'].angle+math.pi)/2
    omega=(m['lower'].angular_velocity-m['upper'].angular_velocity)/2
    A=m['hip'].position;B=m['lower'].local_to_world((-(c['length']-c['extension'])/2,0));C=m['wheel'].position
    return q,omega,A,B,C

def step(m,c):
    q,w,A,B,C=coordinates(m,c);s=springs.state(q,w,c,m['prepared']);g=s['geometry'];au=m['upper'].angle
    def point(local):return tuple(B+pymunk.Vec2d(*springs.rot(local,au)))
    if c['preset']=='dual_rope' and g['active']!='none':
        route=g['routes'][g['active']];direction=springs.rot(route['direction'],au);F=springs.mul(direction,s[g['active']+'_tension'])
        m['lower'].apply_force_at_world_point(F,point(route['lower_contact']));m['upper'].apply_force_at_world_point(springs.mul(F,-1),point(route['upper_contact']))
    elif c['preset']=='knee_bellcrank':
        a=point(g['femur_anchor']);b=point(g['crank_tip']);direction=springs.unit(springs.sub(a,b));F=springs.mul(direction,s['cap_force'])
        m['lower'].apply_force_at_world_point(F,b);m['upper'].apply_force_at_world_point(springs.mul(F,-1),a)
    command=torque(m['t']+c['dt']/2,c);m['upper'].torque-=command
    if c['fixture']=='ground':m['hip'].torque+=command
    m['contacts']={'wheel':0.,'chassis':0.};m['space'].step(c['dt']);m['t']+=c['dt'];m['steps']+=1
    newq,neww,newA,newB,_=coordinates(m,c)
    if c['angle_limit_enabled'] and newB.x<=newA.x:raise ValueError('Stop overshoot moved the knee left; reduce timestep/input or increase stop margin.')
    m['work']+=command*(w+neww)/2*c['dt'];m['dissipated']+=s['dissipation']*c['dt']
    return command

def frame(q,A,c,s,upper_angle=None,lower_angle=None,B=None,C=None):
    L=c['length'];A=tuple(A);B=B or springs.add(A,(L*math.cos(q),-L*math.sin(q)));C=C or springs.add(A,(0,-2*L*math.sin(q)))
    return {'hip':A,'knee':tuple(B),'hub':tuple(C),'theta_deg':math.degrees(q),'upper_angle':-q if upper_angle is None else upper_angle,'lower_angle':q-math.pi if lower_angle is None else lower_angle,'spring':s,'preset':c['preset']}

def energy(m,c,s):
    return sum(.5*b.mass*b.velocity.length_squared+(.5*b.moment*b.angular_velocity**2 if math.isfinite(b.moment) else 0)+b.mass*c['gravity']*b.position.y for b in [m['upper'],m['lower'],m['wheel']]+([m['hip']] if c['fixture']=='ground' else []))+s['energy']

def channels(t,q,w,s,command,displacement=0):
    return {'t':t,'theta_deg':math.degrees(q),'knee_opening_deg':2*math.degrees(q),'femur_torque_Nm':command,'hip_motor_reaction_Nm':-command,'spring_torque_Nm':s['torque'],'spring_knee_torque_Nm':s['torque']/2,
      'red_tension_N':s['red_tension'],'blue_tension_N':s['blue_tension'],'cap_force_N':s['cap_force'],
      'red_tension_kgf':s['red_tension']/9.80665,'blue_tension_kgf':s['blue_tension']/9.80665,'compression_m':s['compression'],'coil_length_m':s['coil_length'],
      'spring_energy_J':s['energy'],'spring_dissipation_W':s['dissipation'],'angular_velocity_rad_s':w,
      'chassis_displacement':displacement,'active_red':int(s['geometry']['active']=='red'),'active_blue':int(s['geometry']['active']=='blue'),
      'red_lead_angle_deg':math.degrees(math.acos(max(-1,min(1,s['geometry'].get('routes',{}).get('red',{}).get('cap_projection',1.))))),
      'blue_lead_angle_deg':math.degrees(math.acos(max(-1,min(1,s['geometry'].get('routes',{}).get('blue',{}).get('cap_projection',1.))))),
      'red_slack_m':s['geometry']['slack'].get('red',0.),'blue_slack_m':s['geometry']['slack'].get('blue',0.)}

UNITS={'t':'s','theta_deg':'deg','knee_opening_deg':'deg','femur_torque_Nm':'N·m','hip_motor_reaction_Nm':'N·m','spring_torque_Nm':'N·m','spring_knee_torque_Nm':'N·m','red_tension_N':'N','blue_tension_N':'N','cap_force_N':'N',
 'red_tension_kgf':'kgf','blue_tension_kgf':'kgf','compression_m':'m','coil_length_m':'m','spring_energy_J':'J','spring_dissipation_W':'W','angular_velocity_rad_s':'rad/s',
 'angular_acceleration_rad_s2':'rad/s²','chassis_displacement':'m','chassis_velocity_m_s':'m/s','chassis_acceleration_m_s2':'m/s²','wheel_ground_force_N':'N','chassis_ground_force_N':'N',
 'j1_force_N':'N','j2_force_N':'N','j3_force_N':'N','guide_torque_Nm':'N·m','guide_error_rad':'rad','motor_work_J':'J','mechanical_energy_J':'J','energy_balance_error_J':'J',
 'active_red':'0/1','active_blue':'0/1','red_slack_m':'m','blue_slack_m':'m',
 'red_lead_angle_deg':'deg','blue_lead_angle_deg':'deg','angle_stop_torque_Nm':'N·m','stop_dissipated_energy_J':'J','mechanical_energy_minus_work_J':'J'}

def package(c,rows,frames,backend):
    flipped=next((r['t'] for r in rows if math.sin(math.radians(r['theta_deg']))*(1 if c['start_inverted'] else -1)>.5),None)
    return {'backend':'inversion_'+backend,'model':'invertible wheel leg','engine':'Pymunk '+pymunk.version if backend=='pymunk' else 'independent SciPy angle ODE',
      'config':c,'units':UNITS,'rows':rows,'frames':frames,'diagnostics':{'flip_time_s':flipped,'max_compression_m':max(r['compression_m'] for r in rows),
      'red_samples':sum(r['active_red'] for r in rows),'blue_samples':sum(r['active_blue'] for r in rows)},
      'scope':('Knee-right angle stops are enabled. ' if c['angle_limit_enabled'] else 'Unrestricted archived angle study. ')+'Experimental fixed-pitch inversion study. Ground mode has real frictionless wheel/chassis floor contacts; self-collision disabled for staggered lateral planes. Math/fixed-J1 comparison has no floor. Ideal shortest cable paths; rope winding history, grooves, strength and 3D clearance are unverified.'}

def preview(values=None):
    c=config(values);q,H=initial(c);s=springs.state(q,0.,c,springs.prepare(c))
    return {'kind':'inversion-preview','solver_steps':0,'config':c,'frame':frame(q,(0,H),c,s),'scope':'Geometry only. No solved forces or contact reactions.'}

def simulate(values=None,backend='pymunk'):
    c=config(values);q0,H=initial(c);p=springs.prepare(c)
    if backend=='math':
        if c['fixture']!='hip_fixed':raise ValueError('Independent inversion mathematics uses fixed J1 without floor; select hip_fixed for matched comparisons.')
        L,e=c['length'],c['extension'];mu,ml,mw=c['upper_mass'],c['lower_mass'],c['wheel_mass'];I=mu*L*L/12+ml*(L+e)**2/12+mu*L*L/4
        a=ml*(L+e)**2/4;b=ml*(3*L-e)**2/4+4*mw*L*L;G=c['gravity']*(mu*L/2+ml*(3*L-e)/2+2*mw*L)
        def evaluate(t,y):
            q,w=y[:2];s=springs.state(float(q),float(w),c,p);M=I+a*math.sin(q)**2+b*math.cos(q)**2;Mp=(a-b)*math.sin(2*q);T=torque(t,c)
            return [w,(T+s['torque']+G*math.cos(q)-.5*Mp*w*w)/M,T*w,s['dissipation']]
        times=np.linspace(0,c['duration'],round(c['duration']/c['dt'])+1)
        if c['angle_limit_enabled']:
            states,stop_losses,_=integrate_stops(evaluate,lambda q:I+a*math.sin(q)**2+b*math.cos(q)**2,
              times,(q0,0.,0.,0.),(math.radians(c['angle_min_deg']),math.radians(c['angle_max_deg'])))
        else:
            solved=solve_ivp(evaluate,(0,c['duration']),(q0,0.,0.,0.),t_eval=times,max_step=c['dt'],rtol=2e-8,atol=1e-10)
            if not solved.success:raise ValueError(solved.message)
            states=solved.y;stop_losses=np.zeros(len(times))
        rows=[];frames=[];first=None
        for i,t in enumerate(times):
            q,w,work,diss=map(float,states[:,i]);s=springs.state(q,w,c,p);r=channels(float(t),q,w,s,torque(float(t),c));free_accel=evaluate(float(t),(q,w,work,diss))[1]
            held=c['angle_limit_enabled'] and abs(w)<1e-10 and ((abs(q-math.radians(c['angle_min_deg']))<1e-10 and free_accel<0) or (abs(q-math.radians(c['angle_max_deg']))<1e-10 and free_accel>0))
            r['angular_acceleration_rad_s2']=0. if held else free_accel
            r['angle_stop_torque_Nm']=-(torque(float(t),c)+s['torque']+G*math.cos(q)) if held else 0.
            E=.5*(I+a*math.sin(q)**2+b*math.cos(q)**2)*w*w+c['gravity']*(mu+ml+mw)*H-G*math.sin(q)+s['energy'];first=E if first is None else first
            r.update(motor_work_J=work,mechanical_energy_J=E,stop_dissipated_energy_J=float(stop_losses[i]),energy_balance_error_J=E-first-work+diss+stop_losses[i]);rows.append(r)
            if i%max(1,round(.01/c['dt']))==0 or i==len(times)-1:frames.append({'t':float(t),**frame(q,(0,H),c,s)})
        return package(c,rows,frames,'math')
    m=build(c);rows=[];frames=[];previous_w=0.;previous_v=0.;E0=None
    for i in range(round(c['duration']/c['dt'])+1):
        command=step(m,c) if i else 0.;q,w,A,B,C=coordinates(m,c);s=springs.state(q,w,c,p);r=channels(m['t'],q,w,s,command,A.y-H)
        E=energy(m,c,s);E0=E if E0 is None else E0
        r.update(angular_acceleration_rad_s2=(w-previous_w)/c['dt'] if i else 0.,chassis_velocity_m_s=m['hip'].velocity.y,
                 chassis_acceleration_m_s2=(m['hip'].velocity.y-previous_v)/c['dt'] if i else 0.,motor_work_J=m['work'],mechanical_energy_J=E,
                 wheel_ground_force_N=m['contacts']['wheel']/c['dt'],chassis_ground_force_N=m['contacts']['chassis']/c['dt'],
                 guide_torque_Nm=m['guide'].impulse/c['dt'],guide_error_rad=m['upper'].angle+m['lower'].angle+math.pi)
        stop_sign=1 if abs(math.degrees(q)-c['angle_min_deg'])<abs(math.degrees(q)-c['angle_max_deg']) else -1
        r['angle_stop_torque_Nm']=stop_sign*abs(m['stop'].impulse)/c['dt'] if m['stop'] else 0.
        if c['fixture']=='hip_fixed':
            key='mechanical_energy_minus_work_J' if c['angle_limit_enabled'] else 'energy_balance_error_J'
            r[key]=E-E0-m['work']+m['dissipated']
        for j,joint in enumerate(m['joints'],1):r[f'j{j}_force_N']=joint.impulse/c['dt']
        if not all(math.isfinite(v) for v in r.values()):raise ValueError('Nonfinite inversion state; reduce torque/timestep.')
        rows.append(r);previous_w=w;previous_v=m['hip'].velocity.y
        if i%max(1,round(.01/c['dt']))==0 or i==round(c['duration']/c['dt']):frames.append({'t':m['t'],**frame(q,A,c,s,m['upper'].angle,m['lower'].angle,B,C),'debug_draw':capture(m['space'])})
    return package(c,rows,frames,'pymunk')
