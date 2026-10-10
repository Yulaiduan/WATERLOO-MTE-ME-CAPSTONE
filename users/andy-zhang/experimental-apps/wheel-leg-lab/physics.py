"""Build and run the experimental SI Pymunk wheel-leg fixture.

Invocation: imported by server.py/debug_gui.py; call simulate(config) for a trace.
Inputs: explicit config in m, kg, s, rad, N and N m; UI angles convert from degrees.
Outputs: solver rows, debug-draw frames, reference checks and diagnostics.
Requires pinned Pymunk; no terrain contact, belt elasticity or hardware calibration.
Grounded 2:1 carrier guide uses absolute GearJoint ratio -1, phase pi.
"""
from __future__ import annotations
import math
from copy import deepcopy
import pymunk
from pymunk import Vec2d
from debug_view import capture, describe
from equation_checks import SCREENSHOT, moment_checks

DEFAULTS = {
    "length": .273, "extension": .05, "radius": .2, "theta": 45.,
    "load_point":"hub", "wheel_drive_locked":False,
    "theta_min": 15., "theta_max": 80., "upper_mass": .6, "lower_mass": .65,
    "wheel_mass": 1.5, "chassis_mass": 8., "gravity": 9.80665,
    "fixture": "hip", "stiffness": 8000., "damping": 100., "rest_length": .23,
    "balance_spring": True, "bias_force": 80., "bias_force_x":0., "knee_kp": 0., "knee_kd": 0.,
    "torque_limit": 80., "target": "force", "wave": "square", "amplitude": 5.,
    "impulse": 2., "start": .5, "period": 1.5, "duty": .5,
    "pulse_width": .12, "rise": .05, "fall": .05,
    "duration": 6., "dt": .001, "iterations": 80,
}

def config(values=None):
    c = deepcopy(DEFAULTS)
    if values:
        if not isinstance(values, dict): raise ValueError("Configuration must be an object.")
        if set(values) - set(c): raise ValueError("Unknown configuration field.")
        c.update(values)
    for k, default in DEFAULTS.items():
        if isinstance(default, bool):
            if not isinstance(c[k], bool): raise ValueError(f"{k} must be boolean.")
        elif isinstance(default, (float, int)):
            if isinstance(c[k], bool) or not isinstance(c[k], (float, int)) or not math.isfinite(c[k]):
                raise ValueError(f"{k} must be finite.")
    limits = {"length":(.08,.8),"extension":(.005,.15),"radius":(.05,.4),
              "upper_mass":(.01,20),"lower_mass":(.01,20),"wheel_mass":(.01,30),
              "chassis_mass":(.01,100),"gravity":(0,20),"stiffness":(0,100000),
              "damping":(0,2000),"rest_length":(.005,1),"knee_kp":(0,2000),
              "knee_kd":(0,200),"torque_limit":(.01,2000),"duration":(.1,20),
              "dt":(.00025,.004),"iterations":(20,300),"start":(0,20),
              "period":(.02,10),"duty":(.01,.99),"pulse_width":(.001,5),
              "rise":(0,5),"fall":(0,5),"amplitude":(-10000,10000),
              "impulse":(-1000,1000),"bias_force":(-5000,5000),"bias_force_x":(-5000,5000)}
    for k,(lo,hi) in limits.items():
        if not lo <= c[k] <= hi: raise ValueError(f"{k} must be between {lo} and {hi} (SI units).")
    if c["extension"] >= c["length"]: raise ValueError("Extension must be shorter than the knee-to-hub link.")
    if not 3 <= c["theta_min"] < c["theta"] < c["theta_max"] <= 87:
        raise ValueError("Use 3° ≤ minimum < initial angle < maximum ≤ 87°.")
    if c["duration"] / c["dt"] > 30000: raise ValueError("Limit each run to 30,000 solver steps.")
    if c["iterations"] != int(c["iterations"]): raise ValueError("Iterations must be an integer.")
    for k, choices in {"fixture":["hip","wheel"],"target":["force","knee"],"wave":["square","impulse"],"load_point":["hub","contact"]}.items():
        if c[k] not in choices: raise ValueError(f"Invalid {k}.")
    if c['fixture']=='wheel' and (c['load_point']=='contact' or c['wheel_drive_locked']):
        raise ValueError('Tire-bottom loading and wheel-drive locking require the fixed-hip fixture.')
    width = c["period"]*c["duty"] if c["wave"] == "square" else c["pulse_width"]
    if c["rise"] + c["fall"] > width + 1e-12:
        raise ValueError("Rise + fall must fit within on-time / pulse width.")
    return c

def trapezoid_area(t, width, rise, fall):
    """Integral of unit-height trapezoid from time 0 to t."""
    t = min(width, max(0., t))
    area = 0.
    if rise:
        s = min(t, rise); area += s*s/(2*rise)
    plateau = max(0., min(t, width-fall)-rise)
    area += plateau
    if fall and t > width-fall:
        s = t-(width-fall); area += s-s*s/(2*fall)
    return area

def excitation_area(t, c):
    t -= c["start"]
    if t <= 0: return 0.
    if c["wave"] == "impulse":
        width=c["pulse_width"]
        return c["impulse"]*trapezoid_area(t,width,c["rise"],c["fall"])/(width-(c["rise"]+c["fall"])/2)
    width=c["period"]*c["duty"]
    cycles=math.floor(t/c["period"])
    return c["amplitude"]*(cycles*trapezoid_area(width,width,c["rise"],c["fall"])+trapezoid_area(t-cycles*c["period"],width,c["rise"],c["fall"]))

def input_average(t, dt, c):
    return (excitation_area(t+dt,c)-excitation_area(t,c))/dt

def body(mass, length, position, angle):
    b = pymunk.Body(mass, mass*length*length/12)
    b.position = position; b.angle = angle
    return b

def build(c):
    L,e=c["length"],c["extension"]; theta=math.radians(c["theta"])
    A=Vec2d(0,0 if c["fixture"]=="hip" else 2*L*math.sin(theta))
    B=A+Vec2d(L*math.cos(theta),-L*math.sin(theta))
    C=B+Vec2d(-L*math.cos(theta),-L*math.sin(theta))
    space=pymunk.Space(); space.gravity=(0,-c["gravity"]); space.iterations=int(c["iterations"])
    upper=body(c["upper_mass"],L,(A+B)/2,-theta)
    lower=body(c["lower_mass"],L+e,B+Vec2d(-math.cos(theta),-math.sin(theta))*(L-e)/2,theta-math.pi)
    if c["fixture"]=="hip":
        hip=space.static_body
        wheel=pymunk.Body(c["wheel_mass"],.5*c["wheel_mass"]*c["radius"]**2);wheel.position=C
        moving=wheel
    else:
        # Torso orientation is held fixed; heave is free. The guide determines x.
        hip=pymunk.Body(c["chassis_mass"],float('inf'));hip.position=A
        wheel=space.static_body; moving=hip
    space.add(upper,lower,moving)
    # Real engine shapes for debugging/querying. Existing prescribed-load bench
    # has no contact response: sensors and supplied body inertias preserve it.
    upper_shape=pymunk.Segment(upper,(-L/2,0),(L/2,0),.009)
    lower_shape=pymunk.Segment(lower,(-(L+e)/2,0),((L+e)/2,0),.009)
    wheel_shape=pymunk.Circle(wheel,c["radius"],wheel.world_to_local(C))
    shapes={'upper_link':upper_shape,'lower_link':lower_shape,'wheel':wheel_shape}
    for shape,shade in [(upper_shape,(52,152,219,255)),(lower_shape,(39,174,96,255)),(wheel_shape,(241,196,15,130))]:
        shape.sensor=True;shape.filter=pymunk.ShapeFilter(group=1);shape.color=shade
    space.add(*shapes.values())
    j1=pymunk.PivotJoint(hip,upper,hip.world_to_local(A),(-L/2,0))
    j2=pymunk.PivotJoint(upper,lower,(L/2,0),(-(L-e)/2,0))
    j3=pymunk.PivotJoint(lower,wheel,((L+e)/2,0),wheel.world_to_local(C))
    guide=pymunk.GearJoint(upper,lower,math.pi,-1.)
    stop=pymunk.RotaryLimitJoint(upper,lower,2*math.radians(c["theta_min"])-math.pi,2*math.radians(c["theta_max"])-math.pi)
    E=lower.local_to_world((-(L+e)/2,0)); s=(E-A).length
    rest=c["rest_length"]
    if c["balance_spring"]:
        if c["stiffness"]<=0: raise ValueError("Automatic spring balance requires positive spring stiffness.")
        if c["fixture"]=="hip":
            gravity_arm=c["gravity"]*(c["upper_mass"]*L/2+c["lower_mass"]*(3*L-e)/2+c["wheel_mass"]*2*L)
            needed=(2*L*c["bias_force"]-gravity_arm)*math.cos(theta)
        else:
            gravity_arm=c["gravity"]*(c["upper_mass"]*3*L/2+c["lower_mass"]*(L+e)/2+c["chassis_mass"]*2*L)
            needed=(gravity_arm-2*L*c["bias_force"])*math.cos(theta)
        leverage=2*L*e*math.sin(2*theta)/s
        if c['fixture']=='hip' and c['load_point']=='contact' and c['wheel_drive_locked']:
            needed-=c['bias_force_x']*c['radius']
        rest=s-needed/(c["stiffness"]*leverage)
        if rest<.005: raise ValueError("Spring cannot balance this load with the selected stiffness and geometry; increase stiffness or use manual free length.")
    spring=pymunk.DampedSpring(hip,lower,hip.world_to_local(A),(-(L+e)/2,0),rest,c["stiffness"],c["damping"])
    cache={}
    def spring_force(spring, distance):
        a=spring.a.local_to_world(spring.anchor_a); b=spring.b.local_to_world(spring.anchor_b)
        cache["n"]=(b-a).normalized();cache["distance"]=distance
        return (spring.rest_length-distance)*spring.stiffness
    spring.force_func=spring_force
    for joint in (j1,j2,j3,guide,stop,spring):
        joint.collide_bodies=False
    space.add(j1,j2,j3,guide,stop,spring)
    wheel_drive=None
    if c['wheel_drive_locked']:
        wheel_drive=pymunk.GearJoint(lower,wheel,wheel.angle-lower.angle,1.)
        wheel_drive.collide_bodies=False;space.add(wheel_drive)
    return {"space":space,"hip":hip,"upper":upper,"lower":lower,"wheel":wheel,"moving":moving,
            "j1":j1,"j2":j2,"j3":j3,"guide":guide,"stop":stop,"spring":spring,"wheel_drive":wheel_drive,"cache":cache,"rest":rest,"shapes":shapes}

def drive(model, c, t, dt):
    """Shared force/torque input for offline traces and the live native viewer."""
    u,l=model['upper'],model['lower']
    command=input_average(t,dt,c)
    opening=l.angle-u.angle+math.pi;opening_speed=l.angular_velocity-u.angular_velocity
    torque_raw=c['knee_kp']*(2*math.radians(c['theta'])-opening)-c['knee_kd']*opening_speed+(command if c['target']=='knee' else 0.)
    torque=max(-c['torque_limit'],min(c['torque_limit'],torque_raw))
    u.torque=-torque;l.torque=torque
    external=Vec2d(c['bias_force_x'],c['bias_force']+(command if c['target']=='force' else 0.))
    moving=model['moving'];moving.force=(0,0);moving.torque=0.
    point=moving.position
    if c['fixture']=='hip' and c['load_point']=='contact':point+=Vec2d(0,-c['radius'])
    moving.apply_force_at_world_point(external,point)
    model['wheel_external_moment']=external.x*c['radius'] if c['fixture']=='hip' and c['load_point']=='contact' else 0.
    return command,torque,torque_raw,external

def simulate(values=None):
    c=config(values); m=build(c); s=m["space"]; u=m["upper"]; l=m["lower"]; h=m["hip"]; w=m["wheel"]
    L,e=c["length"],c["extension"]; g=Vec2d(0,-c["gravity"]);dt=c["dt"];model_info=describe(m)
    rows=[];frames=[];peaks={}; max_pin_error=0.;max_phase_error=0.;max_impulse_error=0.;max_angular_error=0.
    input_integral=0.; limit_steps=0; clipped_steps=0
    n=math.ceil(c["duration"]/dt)
    frame_stride=max(1,math.ceil(1/(120*dt)))
    for i in range(n):
        t=i*dt
        old_v={key:Vec2d(*m[key].velocity) for key in ("upper","lower","moving")}
        old_wu,old_wl=u.angular_velocity,l.angular_velocity
        old_ww=w.angular_velocity
        old_pin_v=[joint.b.velocity_at_local_point(joint.anchor_b) for joint in (m["j1"],m["j2"],m["j3"])]
        command,torque,torque_raw,external=drive(m,c,t,dt)
        input_integral+=command*dt;clipped_steps+=abs(torque-torque_raw)>1e-9
        s.step(dt)
        au=(u.velocity-old_v["upper"])/dt;al=(l.velocity-old_v["lower"])/dt;am=(m["moving"].velocity-old_v["moving"])/dt
        angular_u=(u.angular_velocity-old_wu)/dt;angular_l=(l.angular_velocity-old_wl)/dt
        angular_w=(w.angular_velocity-old_ww)/dt
        wheel_drive_on_wheel=w.moment*angular_w-m['wheel_external_moment'] if c['wheel_drive_locked'] else 0.
        wheel_drive_reaction=-wheel_drive_on_wheel
        wheel_drive_check=abs(abs(wheel_drive_on_wheel)-m['wheel_drive'].impulse/dt) if m['wheel_drive'] else 0.
        fs=m["cache"]["n"]*(m["spring"].impulse/dt)
        if c["fixture"]=="hip":
            f3=w.mass*(am-g)-external # lower -> wheel
            f2=l.mass*(al-g)-fs+f3 # upper -> lower
            f1=u.mass*(au-g)+f2 # hip -> upper
        else:
            f_on_hip=h.mass*(am-g)-external+fs
            f1=-f_on_hip
            f2=f1-u.mass*(au-g)
            f3=f2+fs-l.mass*(al-g)
        A=h.local_to_world(m["j1"].anchor_a);B=u.local_to_world(m["j2"].anchor_a)
        C=w.local_to_world(m["j3"].anchor_b);E=l.local_to_world(m["spring"].anchor_b)
        u_mom=(u.local_to_world(m["j1"].anchor_b)-u.position).cross(f1)+(u.local_to_world(m["j2"].anchor_a)-u.position).cross(-f2)
        l_mom=(l.local_to_world(m["j2"].anchor_b)-l.position).cross(f2)+(l.local_to_world(m["j3"].anchor_a)-l.position).cross(-f3)+(E-l.position).cross(fs)
        residual_u=u.moment*angular_u-u_mom+torque
        residual_l=l.moment*angular_l-l_mom-torque-wheel_drive_reaction
        guide_torque=(residual_u+residual_l)/2
        stop_torque=(residual_l-residual_u)/2
        angular_error=max(abs(abs(guide_torque)-m["guide"].impulse/dt),abs(abs(stop_torque)-m["stop"].impulse/dt))
        max_angular_error=max(max_angular_error,angular_error)
        limit_steps+=m["stop"].impulse>1e-10
        magnitude_error=max(abs(f.length-m[key].impulse/dt) for f,key in [(f1,"j1"),(f2,"j2"),(f3,"j3")])
        max_impulse_error=max(max_impulse_error,magnitude_error)
        phase=abs(l.angle*m["guide"].ratio-u.angle-m["guide"].phase);max_phase_error=max(max_phase_error,phase)
        pin_error=max((joint.a.local_to_world(joint.anchor_a)-joint.b.local_to_world(joint.anchor_b)).length for joint in (m["j1"],m["j2"],m["j3"]))
        max_pin_error=max(max_pin_error,pin_error)
        vc=w.velocity_at_local_point(m["j3"].anchor_b) if c["fixture"]=="hip" else Vec2d(0,0)
        vh=h.velocity_at_local_point(m["j1"].anchor_a) if c["fixture"]=="wheel" else Vec2d(0,0)
        theta=(l.angle-u.angle+math.pi)/2
        row={"t":(i+1)*dt,"input":command,"theta_deg":math.degrees(theta),"height":A.y-C.y,
             "hub_vx":vc.x,"hub_vy":vc.y,"chassis_vx":vh.x,"chassis_vy":vh.y,
             "hub_ax":am.x if c["fixture"]=="hip" else 0.,"hub_ay":am.y if c["fixture"]=="hip" else 0.,
             "chassis_ax":am.x if c["fixture"]=="wheel" else 0.,"chassis_ay":am.y if c["fixture"]=="wheel" else 0.,
             "knee_speed":l.angular_velocity-u.angular_velocity,"knee_accel":angular_l-angular_u,
             "upper_speed":u.angular_velocity,"lower_speed":l.angular_velocity,
             "upper_accel":angular_u,"lower_accel":angular_l,
             "j1_fx":f1.x,"j1_fy":f1.y,"j1_force":m["j1"].impulse/dt,
             "j2_fx":f2.x,"j2_fy":f2.y,"j2_force":m["j2"].impulse/dt,
             "j3_fx":f3.x,"j3_fy":f3.y,"j3_force":m["j3"].impulse/dt,
             "spring_tension":-m["spring"].impulse/dt,"spring_length":m["cache"]["distance"],
             "spring_elastic_tension":c["stiffness"]*(m["cache"]["distance"]-m["rest"]),
             "spring_damper_tension":-m["spring"].impulse/dt-c["stiffness"]*(m["cache"]["distance"]-m["rest"]),
             "spring_knee_moment":(E-l.local_to_world(m["j2"].anchor_b)).cross(fs),
             "actuator_torque":torque,"actuator_command":torque_raw,"guide_link_torque":guide_torque,
             "wheel_external_moment":m['wheel_external_moment'],"wheel_drive_reaction":wheel_drive_reaction,
             "wheel_speed":w.angular_velocity,"wheel_accel":angular_w,"wheel_drive_check":wheel_drive_check,
             "guide_hip_reaction":-2*guide_torque,"stop_knee_torque":stop_torque,
             "hip_mount_fx":-f1.x-fs.x,"hip_mount_fy":-f1.y-fs.y,
             "pin_error":pin_error,"phase_error":phase,"reaction_check":magnitude_error,
             "angular_check":angular_error}
        row.update(moment_checks(m,c,f1,f2,f3,fs,au,al,angular_u,angular_l,torque,guide_torque,stop_torque,wheel_drive_reaction))
        row['check_Br_N']=row['ref_Br']-row['j2_force']
        for j,(joint,old) in enumerate(zip((m["j1"],m["j2"],m["j3"]),old_pin_v),1):
            velocity=joint.b.velocity_at_local_point(joint.anchor_b)
            acceleration=(velocity-old)/dt
            row.update({f"j{j}_vx":velocity.x,f"j{j}_vy":velocity.y,f"j{j}_ax":acceleration.x,f"j{j}_ay":acceleration.y})
        if not all(math.isfinite(value) for value in row.values()): raise ValueError("Non-finite solver state; reduce input/stiffness or timestep.")
        rows.append(row)
        for key in ("j1_force","j2_force","j3_force","spring_tension","actuator_torque","guide_hip_reaction","stop_knee_torque","hub_vy","hub_ay","chassis_vy","chassis_ay","knee_speed","knee_accel"):
            if key not in peaks or abs(row[key])>abs(peaks[key]["value"]): peaks[key]={"value":row[key],"t":row["t"]}
        if i%frame_stride==0 or i==n-1:
            frames.append({"index":i,"t":row["t"],"hip":[A.x,A.y],"knee":[B.x,B.y],"hub":[C.x,C.y],"tip":[E.x,E.y],"upper_angle":u.angle,"lower_angle":l.angle,"debug_draw":capture(s)})
    warnings=[]
    if limit_steps: warnings.append(f"Travel stops engaged on {limit_steps} steps. Stop torque is a solver constraint reaction; its peak depends on dt and stop rigidity.")
    if clipped_steps: warnings.append(f"Knee actuator clipped to its torque limit on {clipped_steps} steps; delivered torque differs from command.")
    if max_pin_error>.0005 or max_phase_error>.001: warnings.append("Constraint drift is elevated; reduce dt or increase solver iterations before using peak loads.")
    if max_impulse_error>.01 or max_angular_error>.01: warnings.append("Reaction reconstruction differs from solver impulse readings; review diagnostics before using directional loads.")
    equation_errors={key:max(abs(row[key]) for row in rows) for key in ['check_lower_moment_Nm','check_contact_moment_Nm','check_upper_moment_Nm','check_lower_balance_Nm','check_upper_balance_Nm','check_Br_N','wheel_drive_check']}
    return {"config":c,"engine":pymunk.version,"model":model_info,"equation_reference":SCREENSHOT,"equation_check_errors":equation_errors,"actual_rest_length":m["rest"],"rows":rows,"frames":frames,"peaks":peaks,
            "diagnostics":{"max_pin_error_m":max_pin_error,"max_guide_error_rad":max_phase_error,
                           "max_force_check_N":max_impulse_error,"max_torque_check_Nm":max_angular_error,
                           "input_integral":input_integral,"stop_steps":limit_steps,"clipped_steps":clipped_steps},"warnings":warnings,
            "scope":"Ideal rigid links, grounded 2:1 no-slip guide, linear spring-damper, no tire contact or belt elasticity. Reactions are solver-step mean loads; acceleration is a COM velocity difference / dt. Grounded guide torque excludes tooth/shaft load distribution."}
