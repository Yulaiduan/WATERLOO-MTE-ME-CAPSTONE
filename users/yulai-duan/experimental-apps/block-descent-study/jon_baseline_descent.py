"""Reproduce October 19 8.75kg/20deg passive block exits and heave controls.

Run: python jon_baseline_descent.py from this app; Node.js required on PATH.
Inputs: pinned inputs/, SI kg/m/s dynamics, screenshot spring in mm/N units.
Outputs: ignored results/ with 22 integrations, five figures and checks.
Limits: starts at edge q=135deg; no commanded vertical motion, motor or full vehicle.
"""
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import csv
import hashlib
import json
import math
import inspect
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

import jon_single_leg_descent as old
import mujoco
import numpy as np

ROOT = old.ROOT
RAW = ROOT/'results/2026-10-19-jon-baseline-descent'
OUT = RAW/'plots'
BENCH = RAW/'record'
SOURCE = RAW/'source'
HEIGHTS = [100, 150, 250, 300]
P = dict(old.PRESET, m1=8.75, alpha=20., rw=200., te=100., tc=180.,
         springK=5., hornR=90.350954, Sv=100., rs=10.,
         p0=90.6633100698, Su=6.99890652166, nu=0., Fz=85.8375, Fn=85.8375)
SPRING = old.Spring(P)
COLORS = ['#007d8a', '#cc7018', '#7954ad', '#be3e61']


@dataclass
class Case(old.Case):
    name: str='held-100mm'
    # Jon labels front/travel as -global y. Our spatial x is his global y.
    speed: float=-.5
    radius: float=.2
    chassis_mass: float=8.75
    alpha_deg: float=20.
    qmax_deg: float=180.
    # Wheel centre begins exactly above the block edge. x0 remains a record of
    # the wheel position, while the chassis is shifted for the inclined path.
    x0: float=0.
    duration: float=1.
    flat_control: bool=False


def offset(q, c):
    a=math.radians(c.alpha_deg)
    return np.array([-2*c.L*np.sin(q)*math.sin(a), 0*q, -2*c.L*np.sin(q)*math.cos(a)])


def jacobian(q, c):
    a=math.radians(c.alpha_deg)
    return np.array([-2*c.L*np.cos(q)*math.sin(a), 0*q, -2*c.L*np.cos(q)*math.cos(a)])


def model_xml(c):
    # Reuse established contact/mass primitives, but build the tilted reference
    # frame explicitly. Tilt is chassis-fixed; q and the spring stay local.
    tree=ET.fromstring(old.model_xml(c))
    if c.flat_control:
        world=tree.find('worldbody')
        world.remove(world.find("geom[@name='block']"))
    else:
        tree.find("./worldbody/geom[@name='block']").set('pos',f'1 0 {c.height/2}')
    chassis=tree.find("./worldbody/body[@name='chassis']")
    rel=offset(c.q0,c)
    chassis.set('pos', f'{c.x0-rel[0]} 0 {c.height+c.radius-rel[2]}')
    femur=chassis.find("body[@name='femur']")
    chassis.remove(femur)
    a=math.radians(c.alpha_deg)
    mount=ET.SubElement(chassis,'body',name='mount',quat=f'{math.cos(a/2)} 0 {math.sin(a/2)} 0')
    mount.append(femur)
    femur.find("joint[@name='hip']").set('range',f'{math.radians(100)} {math.radians(c.qmax_deg)}')
    return ET.tostring(tree,encoding='unicode')


def make(c):
    xml=model_xml(c);m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m)
    d.joint('hip').qpos[0]=c.q0
    d.joint('knee').qpos[0]=math.pi-2*c.q0
    d.joint('wheel_spin').qpos[0]=c.q0-math.pi+math.radians(c.alpha_deg)
    d.joint('carriage').qvel[0]=c.speed
    d.joint('wheel_spin').qvel[0]=-c.speed/c.radius
    d.ctrl[0]=c.speed
    mujoco.mj_forward(m,d)
    return m,d,xml


def available(c):
    return -offset(math.radians(100),c)[2]+offset(c.q0,c)[2]


def verify():
    c=Case();m,d,_=make(c);v=old.direction(m)
    paths=[];jerrs=[];inverse=[];energy=[];ports=[];ratios=[]
    ref=json.loads((SOURCE/'spring-reference.json').read_text())
    for row in ref:
        f,t,u,dc=SPRING.state(math.radians(row['q_deg']))
        ports.append(max(abs(f-row['force']),abs(t-row['tauS']),abs(u-row['energy']),abs(dc-row['delta']/1000)))
    for alpha in [20.,-20.]:
        cc=replace(c,alpha_deg=alpha);mm,dd,_=make(cc)
        for q in np.linspace(math.radians(100),math.pi,801):
            dd.joint('hip').qpos[0]=q;dd.joint('knee').qpos[0]=math.pi-2*q
            mujoco.mj_forward(mm,dd)
            rel=dd.body('wheel').xpos-dd.body('chassis').xpos
            paths.append(float(np.linalg.norm(rel-offset(q,cc))))
            J=np.zeros((3,mm.nv));mujoco.mj_jacBody(mm,dd,J,None,mm.body('wheel').id)
            jerrs.append(float(np.max(abs(J@old.direction(mm)-jacobian(q,cc)))))
            inverse.append(abs(math.pi-math.asin(np.clip(-rel[2]/(.6*math.cos(math.radians(alpha))),-1,1))-q))
            e=1e-6
            energy.append(abs((SPRING.state(q+e)[2]-SPRING.state(q-e)[2])/(2*e)+SPRING.state(q)[1]))
            ratios.append(-SPRING.state(q)[1]/jacobian(q,cc)[2]/(8.75*9.81))
    # Exact circle/box corner-distance check with the tilted kinematic map.
    corners=[]
    for x in [0,-.03,-.08,-.14,-.19]:
        z=c.height+math.sqrt(c.radius*c.radius-x*x)-.0001
        hipz=m.body_pos[m.body('chassis').id,2]
        q=math.pi-math.asin((hipz-z)/(.6*math.cos(math.radians(c.alpha_deg))))
        d.joint('hip').qpos[0]=q;d.joint('knee').qpos[0]=math.pi-2*q
        d.joint('carriage').qpos[0]=x-m.body_pos[m.body('chassis').id,0]-offset(q,c)[0]
        mujoco.mj_forward(m,d)
        distances=[co.dist for co in d.contact if {int(co.geom1),int(co.geom2)}=={m.geom('block').id,m.geom('tire').id}]
        assert distances
        corners.append(abs(min(distances)-(math.hypot(x,z-c.height)-c.radius)))
    assert max(paths)<1e-12 and max(jerrs)<1e-12 and max(inverse)<1e-12
    assert max(ports)<1e-8 and max(energy)<2e-7 and max(corners)<1e-10
    assert max(abs(np.array(ratios)-1))<.00057
    # Independent rigid-coupling airborne ODE, including the tilted gravity map.
    mf,mt,mw,L=c.femur_mass,c.tibia_mass,c.wheel_mass,c.L
    If=m.body_inertia[m.body('femur').id,1];It=m.body_inertia[m.body('tibia').id,1]
    a=math.radians(c.alpha_deg)
    def rhs(y):
        q,w=y
        mass=If+It+.25*(mf+mt)*L*L+(2*mt+4*mw)*L*L*math.cos(q)**2
        mp=-(2*mt+4*mw)*L*L*math.sin(2*q)
        gravity=9.81*L*(-(.5*mf+mt)*math.cos(q-a)+.5*mt*math.cos(math.pi-q-a)-2*mw*math.cos(q)*math.cos(a))
        return np.array([w,(SPRING.state(q)[1]-.5*mp*w*w-gravity)/mass])
    m,d,_=make(c);m.body_pos[m.body('chassis').id,2]+=2
    m.opt.timestep=c.dt/4
    q=c.q0;qd=-.4;v=old.direction(m)
    d.joint('hip').qpos[0]=q;d.joint('knee').qpos[0]=math.pi-2*q
    d.qvel[:]=v*qd;d.ctrl[0]=0
    d.eq_active[m.equality('horizontal_fixture').id]=1
    d.qfrc_applied[m.joint('hip').dofadr[0]]=SPRING.state(q)[1]
    mujoco.mj_forward(m,d)
    accel_error=abs(float(d.joint('hip').qacc[0])-rhs([q,qd])[1])
    y=np.array([q,qd]);ode_dt=1e-6
    for _ in range(round(.02/ode_dt)):
        k1=rhs(y);k2=rhs(y+ode_dt*k1/2);k3=rhs(y+ode_dt*k2/2);k4=rhs(y+ode_dt*k3)
        y+=ode_dt*(k1+2*k2+2*k3+k4)/6
    for _ in range(round(.02/m.opt.timestep)):
        d.qfrc_applied[:]=0;d.qfrc_applied[m.joint('hip').dofadr[0]]=SPRING.state(float(d.joint('hip').qpos[0]))[1]
        mujoco.mj_step(m,d)
    flight_error=abs(float(d.joint('hip').qpos[0])-y[0])
    assert accel_error/abs(rhs([q,qd])[1])<.001
    assert flight_error<1e-4
    return dict(max_path_error_m=max(paths),max_jacobian_error_m_per_rad=max(jerrs),
                max_height_inverse_error_rad=max(inverse),max_source_port_error=max(ports),
                max_energy_derivative_error_Nm=max(energy),max_corner_distance_error_m=max(corners),
                max_ideal_support_error_percent=float(max(abs(np.array(ratios)-1))*100),
                independent_airborne_accel_relative_error=accel_error/abs(rhs([q,qd])[1]),
                independent_airborne_20ms_angle_error_rad=flight_error,
                mirrored_mounts_checked=True)


def run(c):
    folder=RAW/c.name;folder.mkdir(parents=True,exist_ok=True)
    m,d,xml=make(c);digest=hashlib.sha256(xml.encode()).hexdigest()
    signature=hashlib.sha256((xml+json.dumps(P,sort_keys=True)+inspect.getsource(run)+inspect.getsource(old.Spring)).encode()).hexdigest()
    if (folder/'results.json').exists():
        r=json.loads((folder/'results.json').read_text())
        if r.get('signature')==signature and r['case']==asdict(c):return r
        raise RuntimeError(f'Changed cached case: preserve or move {folder} before rerunning')
    rows=[];warn=[];wall=time.perf_counter();v=old.direction(m)
    tire=m.geom('tire').id;floor=m.geom('floor').id;block=-1 if c.flat_control else m.geom('block').id
    for i in range(round(c.duration/c.dt)+1):
        q=float(d.joint('hip').qpos[0]);qd=float(d.joint('hip').qvel[0])
        f,ts,u,dc=SPRING.state(q)
        d.qfrc_applied[:]=0;d.qfrc_applied[m.joint('hip').dofadr[0]]=ts-c.damping*qd
        d.ctrl[0]=c.speed;mujoco.mj_forward(m,d)
        if i%max(1,round(.0005/c.dt))==0:
            loads={'floor':0.,'block':0.}
            for j in range(d.ncon):
                co=d.contact[j];ids={int(co.geom1),int(co.geom2)}
                if tire not in ids:continue
                force=np.zeros(6);mujoco.mj_contactForce(m,d,j,force)
                if floor in ids:loads['floor']+=max(0,float(force[0]))
                if block in ids:loads['block']+=max(0,float(force[0]))
            wheel=d.body('wheel').xpos.copy();hip=d.body('chassis').xpos.copy()
            J=np.zeros((3,m.nv));mujoco.mj_jacBody(m,d,J,None,m.body('wheel').id)
            wvel=J@d.qvel;hv=float(d.joint('heave').qvel[0]) if c.heave else 0.
            # Project gravity alone into the exact coupled coordinate. This is
            # a quasi-static gravity term, not a dynamic motor-demand estimate.
            grav=0.
            for bodyname in ['femur','tibia','wheel']:
                bid=m.body(bodyname).id;JC=np.zeros((3,m.nv))
                mujoco.mj_jacBodyCom(m,d,JC,None,bid)
                grav+=m.body_mass[bid]*9.81*(JC@v)[2]
            rel=wheel-hip
            rows.append(dict(time_s=float(d.time),wheel_x_m=wheel[0],wheel_z_m=wheel[2],
                hip_x_m=hip[0],hip_z_m=hip[2],extension_m=-rel[2],
                extension_speed_mps=hv-wvel[2],wheel_down_speed_mps=-wvel[2],
                hip_vz_mps=hv,theta2_deg=math.degrees(q),joint_speed_radps=qd,
                spring_force_N=f,spring_torque_Nm=ts,spring_energy_J=u,
                gravity_hold_torque_Nm=grav,airborne_quasistatic_hold_Nm=grav-ts,
                spring_power_W=ts*qd,damper_torque_Nm=-c.damping*qd,
                floor_load_N=loads['floor'],block_load_N=loads['block'],
                coupling_error_rad=float(d.joint('knee').qpos[0])-(math.pi-2*q),
                path_error_m=float(np.linalg.norm(rel-offset(q,c))),
                stop_margin_deg=min(math.degrees(q)-100,c.qmax_deg-math.degrees(q))))
        if not np.isfinite(d.qpos).all() or any(w.number for w in d.warning):
            warn=[int(w.number) for w in d.warning];break
        mujoco.mj_step(m,d)
    assert not warn, (c.name,warn)
    h={k:np.array([r[k] for r in rows]) for k in rows[0]}
    landed=np.flatnonzero(h['floor_load_N']>1);land=int(landed[0]) if len(landed) else None
    stop=np.flatnonzero(h['theta2_deg']<=100)
    contact=h['floor_load_N']+h['block_load_N']>1
    initialhip=c.height+c.radius-offset(c.q0,c)[2]
    # The finite mass on a free chassis needs dynamic contact; a spring tuned
    # for 8.75kg massless links is not an exact static balance after adding mass.
    met=dict(floor_arrival_ms=None if land is None else float(1000*h['time_s'][land]),
        landing_down_speed_mps=None if land is None else float(h['wheel_down_speed_mps'][max(0,land-1)]),
        peak_extension_speed_mps=float(max(h['extension_speed_mps'])),
        peak_abs_joint_speed_radps=float(max(abs(h['joint_speed_radps']))),
        max_chassis_descent_mm=float(1000*(initialhip-min(h['hip_z_m']))),
        chassis_descent_at_landing_mm=None if land is None else float(1000*(initialhip-h['hip_z_m'][land])),
        extension_at_landing_mm=None if land is None else float(1000*(h['extension_m'][land]-h['extension_m'][0])),
        first_stop_ms=None if not len(stop) else float(1000*h['time_s'][stop[0]]),
        max_spring_torque_Nm=float(max(abs(h['spring_torque_Nm']))),
        peak_floor_load_N=float(max(h['floor_load_N'])),
        geometric_remaining_travel_mm=float(1000*available(c)),
        held_hip_nominal_gap_mm=float(1000*max(0,c.height-available(c))),
        max_path_error_m=float(max(h['path_error_m'])),
        max_coupling_error_rad=float(max(abs(h['coupling_error_rad']))),
        final_floor_clearance_mm=float(1000*(h['wheel_z_m'][-1]-c.radius)),
        minimum_hip_angle_deg=float(min(h['theta2_deg'])),
        max_carriage_error_m=float(max(abs(h['hip_x_m']-(h['hip_x_m'][0]+c.speed*h['time_s'])))),
        no_contact_ms=float(np.sum(~contact)*.5),warnings=warn,wall_s=time.perf_counter()-wall)
    with (folder/'history.csv').open('w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    (folder/'model.xml').write_text(xml)
    result=dict(case=asdict(c),metrics=met,model_sha256=digest,signature=signature)
    old.dump(folder/'results.json',result)
    print(c.name,json.dumps(met),flush=True)
    return result


def history(name):
    return np.genfromtxt(RAW/name/'history.csv',delimiter=',',names=True)


def savefig(fig,name):
    fig.savefig(OUT/f'{name}.png',dpi=180,facecolor='white')
    fig.savefig(OUT/f'{name}.pdf',facecolor='white')
    shutil.copy2(OUT/f'{name}.png',BENCH/f'{name}.png')
    old.plt.close(fig)


def style(ax,ylabel,xlabel='Time from wheel-centre edge passage (ms)'):
    ax.set(xlabel=xlabel,ylabel=ylabel);ax.grid(alpha=.22)


def plots(results):
    plt=old.plt
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(2,2,figsize=(13,8))
    for height,color,ls in zip(HEIGHTS,COLORS,['-','-','--',':']):
        h=history(f'held-{height}mm');t=1000*h['time_s']
        series=[1000*(h['wheel_z_m'][0]-h['wheel_z_m']),h['extension_speed_mps'],h['joint_speed_radps'],h['floor_load_N']>1]
        for ax,y in zip(axs.flat,series):ax.plot(t,y,color=color,lw=1.8,ls=ls,label=f'{height} mm')
        r=next(r for r in results if r['case']['name']==f'held-{height}mm')
        if r['metrics']['floor_arrival_ms'] is not None:
            tt=r['metrics']['floor_arrival_ms'];axs[0,0].plot(tt,height,'o',color=color,ms=5)
    axs[0,0].axhline(1000*available(Case()),ls='--',color='#333333',label=f'{1000*available(Case()):.1f} mm available travel')
    labels=['Wheel descent (mm)','Downward extension speed (m/s)','Hip angular velocity (rad/s)','Lower-floor contact (>1 N)']
    for ax,label in zip(axs.flat,labels):style(ax,label);ax.set_xlim(0,700)
    axs[1,1].set_yticks([0,1],['No','Yes']);axs[0,0].legend(ncol=2,fontsize=9)
    fig.suptitle('What happens after the edge? | Jon’s 8.75 kg, 20° baseline\nHip held; 0.5 m/s carriage; 200 mm wheel radius; initial θ₂ = 135°; passive spring')
    fig.tight_layout(rect=[0,0,1,.93]);savefig(fig,'01-descent-comparison')

    fig,axs=plt.subplots(2,2,figsize=(13,8))
    flat=history('heave-flat-control')
    for height,color in zip(HEIGHTS,COLORS):
        for heave,ls in [(False,'--'),(True,'-')]:
            h=history(f'{"heave" if heave else "held"}-{height}mm');t=1000*h['time_s']
            z0=h['hip_z_m'][0]
            series=[1000*(z0-h['hip_z_m']),1000*(h['wheel_z_m'][0]-h['wheel_z_m']),h['extension_speed_mps'],h['joint_speed_radps']]
            for ax,y in zip(axs.flat,series):ax.plot(t,y,color=color,ls=ls,lw=1.7,label=f'{height} mm, {"heave free" if heave else "hip held"}')
    axs[0,0].plot(1000*flat['time_s'],1000*(flat['hip_z_m'][0]-flat['hip_z_m']),color='black',ls=':',lw=2,label='Flat ground: mass-mismatch drift')
    for ax,label in zip(axs.flat,['Chassis descent (mm)','Wheel descent (mm)','Relative extension speed (m/s)','Hip angular velocity (rad/s)']):style(ax,label);ax.set_xlim(0,700)
    axs[0,0].legend(ncol=2,fontsize=8)
    fig.suptitle('Does the body react? | Solid: chassis heave free; dashed: hip held\n8.75 kg chassis share + assumed 0.6 / 0.65 / 1.5 kg links/wheel; pitch and horizontal fixture retained')
    fig.tight_layout(rect=[0,0,1,.93]);savefig(fig,'02-chassis-reaction')

    c=Case();qs=np.linspace(math.radians(100),math.pi,801)
    ts=np.array([SPRING.state(q)[1] for q in qs]);J=jacobian(qs,c)[2]
    gravity=[];m,d,_=make(c);v=old.direction(m)
    for q in qs:
        d.joint('hip').qpos[0]=q;d.joint('knee').qpos[0]=math.pi-2*q;mujoco.mj_forward(m,d)
        G=0
        for n in ['femur','tibia','wheel']:
            JC=np.zeros((3,m.nv));mujoco.mj_jacBodyCom(m,d,JC,None,m.body(n).id)
            G+=m.body_mass[m.body(n).id]*9.81*(JC@v)[2]
        gravity.append(G)
    gravity=np.array(gravity);deg=np.degrees(qs)
    fig,axs=plt.subplots(1,3,figsize=(15,5.4))
    axs[0].plot(deg,100*(-ts/J/(8.75*9.81)-1),color='#007d8a');axs[0].axhline(0,color='gray',lw=1)
    style(axs[0],'Ideal support error (%)','Hip angle θ₂ (degrees)')
    axs[0].set_title('Grounded load: spring ≈ chassis weight')
    axs[1].plot(deg,ts,label='Spring: extends',color='#007d8a')
    axs[1].plot(deg,-gravity,label='Moving-body gravity: extends',color='#cc7018')
    axs[1].plot(deg,-gravity+ts,label='Net airborne drive',color='#7954ad',lw=2.4)
    style(axs[1],'Generalized hip torque (N m)','Hip angle θ₂ (degrees)');axs[1].legend(fontsize=8)
    axs[1].set_title('Airborne, hip held: both drive extension')
    axs[2].plot(deg,gravity-ts,label='Airborne quasi-static hold',color='#be3e61',lw=2)
    axs[2].plot(deg,-8.75*9.81*J-ts,label='Grounded, ideal massless links',color='#007d8a')
    style(axs[2],'Applied CCW torque to hold (N m)','Hip angle θ₂ (degrees)');axs[2].legend(fontsize=8)
    axs[2].set_title('Restraint differs between load cases')
    for ax in axs:ax.axvline(135,color='gray',ls=':',lw=1)
    fig.suptitle('Why gravity compensation does not cancel airborne extension\nQuasi-static torque explanation; no motor/gearbox model or dynamic motor rating')
    fig.tight_layout(rect=[0,0,1,.88]);savefig(fig,'03-grounded-versus-airborne')

    fig,axs=plt.subplots(1,3,figsize=(15,5.4))
    rel=offset(qs,c)
    axs[0].plot(1000*rel[0],1000*rel[2],color='#007d8a',label='Analytic hub path')
    for q in qs[::50]:
        d.joint('hip').qpos[0]=q;d.joint('knee').qpos[0]=math.pi-2*q;mujoco.mj_forward(m,d)
        rr=d.body('wheel').xpos-d.body('chassis').xpos
        axs[0].plot(rr[0]*1000,rr[2]*1000,'o',mfc='none',mec='#cc7018',ms=4)
    style(axs[0],'Hub z relative to hip (mm)','Hub global y relative to hip (mm)');axs[0].axis('equal');axs[0].legend(fontsize=8)
    axs[1].plot(deg,-1000*rel[2],color='#007d8a',label='Vertical hip-to-hub drop')
    axs[1].axvline(135,color='gray',ls=':',label='Initial pose');style(axs[1],'Vertical drop (mm)','Hip angle θ₂ (degrees)');axs[1].legend(fontsize=8)
    axs[2].plot(deg,J,color='#007d8a',label='Vertical Jacobian')
    axs[2].plot(deg,jacobian(qs,c)[0],color='#7954ad',label='Global-y Jacobian (forward = −y)')
    style(axs[2],'Wheel motion per hip radian (m/rad)','Hip angle θ₂ (degrees)');axs[2].legend(fontsize=8)
    fig.suptitle('555 mm full stroke is not 555 mm remaining travel\n100–180° full range; initial 135° pose leaves only %.1f mm downward travel with a held hip' % (1000*available(c)))
    fig.tight_layout(rect=[0,0,1,.88]);savefig(fig,'04-geometry-and-travel')

    fig,axs=plt.subplots(1,2,figsize=(13,5.5))
    for height,color in zip(HEIGHTS,COLORS):
        h=history(f'heave-{height}mm')
        extra=1000*((h['hip_z_m'][0]-h['hip_z_m'])-(flat['hip_z_m'][0]-flat['hip_z_m']))
        axs[0].plot(1000*h['time_s'],extra,color=color,label=f'{height} mm block')
        r=next(r for r in results if r['case']['name']==f'heave-{height}mm')
        land=r['metrics']['floor_arrival_ms']
        k=int(np.argmin(abs(1000*h['time_s']-land)))
        axs[0].plot(land,extra[k],'o',color=color)
    style(axs[0],'Extra chassis descent vs flat control (mm)');axs[0].set_xlim(0,700);axs[0].legend(fontsize=8)
    axs[0].set_title('Subtract flat-ground drift at equal times')
    # This is a geometric knee/rim screen, not a CAD collision check.
    knee_above_hub=1000*c.L*np.sin(qs+math.radians(c.alpha_deg))
    axs[1].plot(deg,knee_above_hub,label='Knee centre above hub',color='#007d8a')
    axs[1].plot(deg,knee_above_hub+200-15,label='Assumed 15 mm tube above wheel bottom',color='#7954ad')
    axs[1].axhline(0,color='gray',lw=1);axs[1].axvline(160,color='gray',ls=':')
    style(axs[1],'Vertical distance (mm)','Hip angle θ₂ (degrees)');axs[1].legend(fontsize=8)
    axs[1].set_title('Below hub ≠ below a 200 mm-radius wheel')
    fig.suptitle('Two interpretation checks for the team\nHeave remains a one-corner fixture; tube envelope is illustrative and body collisions are disabled')
    fig.tight_layout(rect=[0,0,1,.88]);savefig(fig,'05-drift-and-clearance')


def main():
    for folder in [RAW,OUT,BENCH,SOURCE]:folder.mkdir(parents=True,exist_ok=True)
    old.dump(SOURCE/'screenshot-baseline.json',dict(schema='general-vsl/v4-pulley',parameters=P,
        provenance='Read from Jonathan’s Discord image, October 19 21:57 Toronto; horn radius displayed to 6 decimals.',
        message_url='https://discord.com/channels/1527561241831276715/1558281627170381885/1561921319518609450'))
    for fname in ['v4-pulley.html','v4-model.md','verify-pulley.cjs']:
        shutil.copy2(old.INPUTS/fname,SOURCE/fname)
    # Check against the actual embedded analytical spring, not another Python port.
    node=shutil.which('node')
    if not node:raise RuntimeError('Install Node.js or add its executable directory to PATH before running this study.')
    export=r'''const fs=require('fs'),vm=require('vm'),p=process.argv[1];
const html=fs.readFileSync(p+'/v4-pulley.html','utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const sp=vm.runInNewContext(scripts.slice(0,3).join('\n')+';VSLSpring;');
const par=JSON.parse(fs.readFileSync(p+'/screenshot-baseline.json')).parameters;
const rows=[];for(let i=0;i<=800;i++){let q=100+i/10,z=sp.state(par,q);if(!z.valid)throw Error(z.reason);rows.push({q_deg:q,force:z.force,tauS:z.tauS,energy:z.energy,delta:z.delta});}
fs.writeFileSync(p+'/spring-reference.json',JSON.stringify(rows));'''
    (SOURCE/'export-reference.cjs').write_text(export)
    subprocess.run([str(node),'-e',export,str(SOURCE)],check=True)
    checks=verify()
    cases=[Case(name=f'{mode}-{h}mm',height=h/1000,heave=mode=='heave') for mode in ['held','heave'] for h in HEIGHTS]
    cases += [replace(c,name=c.name+'-half-dt',dt=.0000625) for c in cases]
    cases += [Case(name=f'{mode}-{h}mm-half-contact',height=h/1000,heave=mode=='heave',contact_time=.002) for mode in ['held','heave'] for h in [150,300]]
    cases += [Case(name='heave-flat-control',height=0.,heave=True,flat_control=True),
              Case(name='heave-flat-control-half-dt',height=0.,heave=True,flat_control=True,dt=.0000625)]
    results=[run(c) for c in cases]
    for r in results:
        assert r['metrics']['max_path_error_m']<1e-4
        assert r['metrics']['max_coupling_error_rad']<1e-4
        if not r['case']['heave']:
            assert (r['metrics']['floor_arrival_ms'] is not None)==(r['case']['height']<=available(Case()))
    sensitivity=[]
    for r in results[8:]:
        if r['case']['flat_control']:continue
        base=next(z for z in results[:8] if z['case']['height']==r['case']['height'] and z['case']['heave']==r['case']['heave'])
        bm=base['metrics'];rm=r['metrics']
        entry=dict(case=r['case']['name'],speed_change_pct=100*(rm['peak_extension_speed_mps']/bm['peak_extension_speed_mps']-1),
            arrival_change_ms=None if rm['floor_arrival_ms'] is None or bm['floor_arrival_ms'] is None else rm['floor_arrival_ms']-bm['floor_arrival_ms'],
            floor_peak_change_pct=None if bm['peak_floor_load_N']==0 else 100*(rm['peak_floor_load_N']/bm['peak_floor_load_N']-1))
        assert (rm['floor_arrival_ms'] is None)==(bm['floor_arrival_ms'] is None)
        assert abs(entry['speed_change_pct'])<3,entry
        sensitivity.append(entry)
    shutil.copy2(Path(__file__),SOURCE/Path(__file__).name)
    shutil.copy2(Path(old.__file__),SOURCE/Path(old.__file__).name)
    sourcehash={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.iterdir() if p.is_file()}
    study=dict(source_commit=old.COMMIT,screenshot_parameters=P,cases=results,checks=checks,sensitivity=sensitivity,
        source_sha256=sourcehash,experiment_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        runtime=dict(python=sys.version,mujoco=mujoco.__version__,numpy=np.__version__),
        start='Wheel centre at edge, q=135deg, zero joint/heave velocities, 0.5m/s forward along Jon’s -global y.',
        moving_masses_kg=[.6,.65,1.5],chassis_share_kg=8.75,
        assumptions=['Single leg; fixed chassis pitch and prescribed horizontal carriage speed.',
            'No suspension motor, gearbox, rotor inertia, damping, frictional cable losses or calibrated tire/stop compliance.',
            'Link/wheel masses are additional to 8.75kg chassis share; Jon’s static screenshot sets their masses to zero.',
            'Spatial x is Jon’s global y; forward is -global y; block occupies positive global y. Opposite mount verified kinematically.',
            'Body collisions disabled; clearance assessed geometrically, not collision-validated.'])
    old.dump(RAW/'study.json',study);old.dump(BENCH/'results.json',study)
    plots(results)
    print('CHECKS',json.dumps(checks),flush=True)
    print('SENSITIVITY',json.dumps(sensitivity),flush=True)


if __name__=='__main__':main()
