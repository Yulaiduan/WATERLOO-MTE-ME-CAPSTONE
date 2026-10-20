"""Reproduce the October 18 passive single-leg block-exit fixture.

Run: python jon_single_leg_descent.py [--check] [--render] from this app.
Inputs: pinned inputs/, SI dynamics, assumed kg masses and finite-idler spring.
Outputs: local ignored results/ CSV/model/plots, checks and optional PNG frames.
Limits: prescribed horizontal carriage; no motor/gearbox or full vehicle.
"""
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / 'inputs'
RAW = ROOT / 'results/2026-10-18-jon-single-leg-descent'
OUT = RAW / 'plots'
BENCH = RAW / 'record'
os.environ.setdefault('MPLCONFIGDIR', str(RAW/'.mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PRESET = json.loads((INPUTS/'v4-textbook-10mm.json').read_text())['parameters']
COMMIT = 'e91897a9cf9bb36ff3f20afc4c92ea5315cc46b7'

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2)+'\n')

class Spring:
    """Port of VSLSpring geometry/state; metres, radians, newtons, joules."""
    def __init__(self, p=PRESET):
        self.r=p['hornR']/1000; self.su=p['Su']/1000; self.sv=p['Sv']/1000
        self.rho=p['rs']/1000; self.k=p['springK']*1000; self.p0=p['p0']
        self.nu=math.radians(p['nu']); self.c0=self.geometry(math.pi/2)[0]

    def geometry(self, q):
        phi=q+self.nu; dx=self.r*math.cos(phi); dz=self.r*math.sin(phi)
        vx=dx-self.su; vz=dz-self.sv; d=math.hypot(vx,vz)
        assert d>self.rho, 'Invalid cable tangent'
        def polar(angle):
            x=self.r*math.cos(angle)-self.su; z=self.r*math.sin(angle)-self.sv
            center=math.atan2(-self.sv,-self.su)
            return center+math.atan2(math.sin(math.atan2(z,x)-center),math.cos(math.atan2(z,x)-center))
        d0=math.hypot(self.r*math.cos(math.pi/2+self.nu)-self.su,self.r*math.sin(math.pi/2+self.nu)-self.sv)
        psi=polar(phi)-math.acos(self.rho/d)
        psi0=polar(math.pi/2+self.nu)-math.acos(self.rho/d0)
        turns=math.ceil((math.pi/2-psi0-1e-12)/(2*math.pi))
        wrap=psi-math.pi/2+turns*2*math.pi
        assert -1e-8<=wrap<=2*math.pi+1e-8, 'Cable route lost wrap'
        Q=(self.su+self.rho*math.cos(psi),self.sv+self.rho*math.sin(psi))
        tangent=math.sqrt(d*d-self.rho*self.rho)
        ux=(Q[0]-dx)/tangent; uz=(Q[1]-dz)/tangent
        cp=dz*ux-dx*uz
        return tangent+self.rho*wrap, cp, (dx,dz), Q, psi, wrap

    def state(self,q):
        c,cp,*_=self.geometry(q)
        f=max(0,self.p0+self.k*(c-self.c0))
        return f, -f*cp, f*f/(2*self.k), c-self.c0

@dataclass
class Case:
    name: str='fixed-v05-b0'
    speed: float=.5
    height: float=.1
    damping: float=0.
    mass_scale: float=1.
    heave: bool=False
    dt: float=.000125
    contact_time: float=.004
    L: float=.3
    radius: float=.1
    femur_mass: float=.6
    tibia_mass: float=.65
    wheel_mass: float=1.5
    chassis_mass: float=13.
    q0: float=math.radians(135)
    settle: float=0.
    ramp: float=0.
    x0: float=-.25

def translation(t,c):
    if c.ramp==0:return c.x0+c.speed*t,c.speed
    u=np.clip((t-c.settle)/c.ramp,0,1)
    blend=10*u**3-15*u**4+6*u**5
    integral=2.5*u**4-3*u**5+u**6
    extra=max(0,t-c.settle-c.ramp)
    return c.x0+c.speed*(c.ramp*integral+extra),c.speed*blend

def model_xml(c):
    upper=math.radians(165); lower=math.radians(100)
    hipz=c.height+c.radius+2*c.L*math.sin(c.q0)
    heave='<joint name="heave" type="slide" axis="0 0 1"/>' if c.heave else ''
    # Axis -y makes positive joint rotation CCW in the x/z drawing, as in Jon.
    return f'''<mujoco model="Jon V4 one-leg block-exit test fixture">
    <compiler angle="radian"/><option timestep="{c.dt}" gravity="0 0 -9.81" integrator="implicitfast" iterations="100" tolerance="1e-12"/>
    <size njmax="200" nconmax="100"/><visual><global offwidth="960" offheight="680"/><quality shadowsize="2048"/></visual>
    <default><joint armature="0" damping="0"/><geom friction="0.8 0.001 0.00001" condim="3" solref="{c.contact_time} 1" solimp=".95 .99 .001"/>
    </default><worldbody><light pos="0 -2 3" diffuse=".8 .8 .8"/><light pos="-1 2 2"/>
    <geom name="floor" type="plane" size="4 1 .1" rgba=".25 .32 .36 1"/>
    <geom name="block" type="box" pos="-1 0 {c.height/2}" size="1 .35 {c.height/2}" rgba=".88 .52 .14 1"/>
    <body name="chassis" pos="{c.x0} 0 {hipz}"><joint name="carriage" type="slide" axis="1 0 0"/>{heave}
    <geom name="frame" type="box" size=".14 .09 .045" mass="{c.chassis_mass}" rgba=".20 .36 .48 1" contype="0" conaffinity="0"/>
    <body name="femur"><joint name="hip" type="hinge" axis="0 -1 0" limited="true" range="{lower} {upper}" solreflimit=".002 1"/>
      <geom name="upper" type="capsule" fromto="0 0 0 {-c.L} 0 0" size=".015" mass="{c.femur_mass*c.mass_scale}" rgba=".15 .55 .95 1" contype="0" conaffinity="0"/>
      <body name="tibia" pos="{-c.L} 0 0"><joint name="knee" type="hinge" axis="0 -1 0"/>
        <geom name="lower" type="capsule" fromto="0 0 0 {-c.L} 0 0" size=".013" mass="{c.tibia_mass*c.mass_scale}" rgba=".95 .58 .12 1" contype="0" conaffinity="0"/>
        <body name="wheel" pos="{-c.L} 0 0"><joint name="wheel_spin" type="hinge" axis="0 -1 0"/>
          <geom name="wheel_shell" type="cylinder" size="{c.radius} .025" quat=".7071067812 .7071067812 0 0" mass="{c.wheel_mass*c.mass_scale}" rgba=".07 .09 .11 1" contype="0" conaffinity="0"/>
          <geom name="tire" type="sphere" size="{c.radius}" mass="0" group="3" rgba="0 0 0 0"/>
          <geom type="box" size="{c.radius*.7} .027 .006" rgba=".65 .78 .82 1" contype="0" conaffinity="0" mass="0"/>
        </body>
      </body>
    </body></body></worldbody>
    <equality><joint name="coupling" joint1="knee" joint2="hip" polycoef="{math.pi} -2 0 0 0" solref=".0005 1" solimp=".9999 .9999 .00001"/>
    <joint name="horizontal_fixture" active="false" joint1="carriage" polycoef="0 0 0 0 0" solref=".0005 1" solimp=".9999 .9999 .00001"/></equality>
    <actuator><velocity name="horizontal_drive" joint="carriage" kv="1000000"/></actuator>
    </mujoco>'''

def make(c):
    xml=model_xml(c);m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m)
    d.joint('hip').qpos[0]=c.q0;d.joint('knee').qpos[0]=math.pi-2*c.q0
    d.joint('wheel_spin').qpos[0]=-(math.pi-c.q0)
    d.joint('carriage').qvel[0]=c.speed
    d.joint('wheel_spin').qvel[0]=-c.speed/c.radius
    mujoco.mj_forward(m,d)
    return m,d,xml

def direction(m):
    v=np.zeros(m.nv)
    for n,f in [('hip',1),('knee',-2),('wheel_spin',1)]:v[m.joint(n).dofadr[0]]=f
    return v

def verify():
    s=Spring(); c=Case();m,d,_=make(c);v=direction(m)
    patherr=[];jerr=[];inverse=[];energy=[];port=[];sratio=[]
    ref=json.loads((INPUTS/'spring-reference.json').read_text())
    for row in ref:
        f,t,u,dc=s.state(math.radians(row['q_deg']))
        port.append(max(abs(f-row['force']),abs(t-row['tauS']),abs(u-row['energy']),abs(dc-row['delta']/1000)))
    for q in np.linspace(math.radians(100),math.radians(165),201):
        d.joint('hip').qpos[0]=q;d.joint('knee').qpos[0]=math.pi-2*q;d.joint('wheel_spin').qpos[0]=q-math.pi
        mujoco.mj_forward(m,d)
        rel=d.body('wheel').xpos-d.body('chassis').xpos
        patherr.append(np.linalg.norm(rel-[0,0,-2*c.L*math.sin(q)]))
        J=np.zeros((3,m.nv));mujoco.mj_jacBody(m,d,J,None,m.body('wheel').id)
        jerr.append(np.max(np.abs(J@v-[0,0,-2*c.L*math.cos(q)])))
        inverse.append(abs((math.pi-math.asin(-rel[2]/(2*c.L)))-q))
        eps=1e-6;energy.append(abs((s.state(q+eps)[2]-s.state(q-eps)[2])/(2*eps)+s.state(q)[1]))
        sratio.append(-s.state(q)[1]/(-2*c.L*math.cos(q))/(13*9.81))
    assert max(patherr)<1e-12 and max(jerr)<1e-12 and max(inverse)<1e-12
    assert max(energy)<2e-7 and max(port)<1e-8
    assert max(abs(np.array(sratio)-1))<.000621
    # The sphere collision proxy is an exact circle in the 2D travel plane;
    # retain cylindrical wheel mass/inertia. Check corner distance independently.
    corner_errors=[]
    for x in [0,.02,.04,.06,.08,.095]:
        z=c.height+math.sqrt(c.radius*c.radius-x*x)-.0001
        d.joint('carriage').qpos[0]=x-c.x0
        q=math.pi-math.asin((m.body_pos[m.body('chassis').id,2]-z)/(2*c.L))
        d.joint('hip').qpos[0]=q;d.joint('knee').qpos[0]=math.pi-2*q
        mujoco.mj_forward(m,d)
        contacts=[co.dist for co in d.contact if {int(co.geom1),int(co.geom2)}=={m.geom('block').id,m.geom('tire').id}]
        assert contacts, ('Missing analytic corner contact',x,z)
        exact=math.hypot(x,max(0,z-c.height))-c.radius
        corner_errors.append(abs(min(contacts)-exact))
    assert max(corner_errors)<1e-10
    # Independent constrained flight ODE. Use actual compiled COM/inertia;
    # wheel's free world spin is constant; no floor/contact or hip translation.
    q=math.radians(135);qd=-.4;c=Case(height=.1)
    mf=c.femur_mass;mt=c.tibia_mass;mw=c.wheel_mass;L=c.L
    If=m.body_inertia[m.body('femur').id,1];It=m.body_inertia[m.body('tibia').id,1]
    def rhs(t,y):
        q,w=y;M=If+It+.25*(mf+mt)*L*L+(2*mt+4*mw)*L*L*math.cos(q)**2
        Mp=-(2*mt+4*mw)*L*L*math.sin(2*q)
        G=-9.81*L*math.cos(q)*(.5*mf+1.5*mt+2*mw)
        return [w,(s.state(q)[1]-.5*Mp*w*w-G)/M]
    d=mujoco.MjData(m);d.joint('hip').qpos[0]=q;d.joint('knee').qpos[0]=math.pi-2*q;d.joint('wheel_spin').qpos[0]=q-math.pi
    # Move fixture high enough that no collision can enter this check.
    m.body_pos[m.body('chassis').id,2]+=2;d.qvel[:]=v*qd
    d.eq_active[m.equality('horizontal_fixture').id]=1
    d.ctrl[0]=0
    d.qfrc_applied[m.joint('hip').dofadr[0]]=s.state(q)[1]
    mujoco.mj_forward(m,d)
    expected_acceleration=rhs(0,[q,qd])[1]
    acceleration_error=abs(float(d.joint('hip').qacc[0])-expected_acceleration)
    # MuJoCo equality constraints have finite impedance. At the highest allowed
    # impedance the independent rigid-coupling acceleration must agree to 0.1%.
    assert acceleration_error/abs(expected_acceleration)<.001,acceleration_error
    y=np.array([q,qd]);ode_dt=1e-6
    for _ in range(round(.02/ode_dt)):
        a=np.array(rhs(0,y));b=np.array(rhs(0,y+ode_dt*a/2))
        cc=np.array(rhs(0,y+ode_dt*b/2));dd=np.array(rhs(0,y+ode_dt*cc))
        y+=ode_dt*(a+2*b+2*cc+dd)/6
    m.opt.timestep=c.dt/4
    for _ in range(round(.02/m.opt.timestep)):
        d.qfrc_applied[:]=0;d.qfrc_applied[m.joint('hip').dofadr[0]]=s.state(float(d.joint('hip').qpos[0]))[1]
        mujoco.mj_step(m,d)
    flight_position_error=abs(float(d.joint('hip').qpos[0])-y[0])
    assert flight_position_error<.0001,flight_position_error
    return dict(max_wheel_path_error_m=max(patherr),max_jacobian_error_m_per_rad=max(jerr),max_inverse_error_rad=max(inverse),
        max_spring_energy_derivative_error_Nm=max(energy),max_port_error=max(port),max_corner_contact_distance_error_m=max(corner_errors),
        static_support_min=min(sratio),static_support_max=max(sratio),
        independent_flight_accel_error_radps2=acceleration_error,
        independent_flight_accel_relative_error=acceleration_error/abs(expected_acceleration),independent_flight_angle_error_rad=flight_position_error,
        independent_flight_check_timestep_s=float(m.opt.timestep))

def run(c):
    folder=RAW/c.name;folder.mkdir(parents=True,exist_ok=True)
    if (folder/'results.json').exists():
        existing=json.loads((folder/'results.json').read_text());assert existing['case']==asdict(c)
        assert existing['model_sha256']==hashlib.sha256(model_xml(c).encode()).hexdigest(), 'Cached model changed; use a fresh case folder.'
        return existing
    m,d,xml=make(c);s=Spring(); tire=m.geom('tire').id;block=m.geom('block').id;floor=m.geom('floor').id
    edge=c.settle+c.ramp/2-c.x0/c.speed;duration=edge+1.5
    samples=[];poses=[];pose_t=[];vel=[];warn=[];wall=time.perf_counter()
    for i in range(math.ceil(duration/c.dt)+1):
        _,vx=translation(d.time,c);d.ctrl[0]=vx
        q=float(d.joint('hip').qpos[0]);qd=float(d.joint('hip').qvel[0]);f,ts,u,dc=s.state(q)
        d.qfrc_applied[:]=0;d.qfrc_applied[m.joint('hip').dofadr[0]]=ts-c.damping*qd
        mujoco.mj_forward(m,d)
        if i%max(1,round(.0005/c.dt))==0:
            loads={'floor':0.,'block':0.}
            for j in range(d.ncon):
                co=d.contact[j];ids={int(co.geom1),int(co.geom2)}
                if tire not in ids:continue
                force=np.zeros(6);mujoco.mj_contactForce(m,d,j,force)
                if floor in ids:loads['floor']+=max(0,float(force[0]))
                if block in ids:loads['block']+=max(0,float(force[0]))
            wheel=d.body('wheel').xpos.copy();hip=d.body('chassis').xpos.copy()
            J=np.zeros((3,m.nv));mujoco.mj_jacBody(m,d,J,None,m.body('wheel').id);wvel=J@d.qvel
            qk=float(d.joint('knee').qpos[0]);hipvz=float(d.joint('heave').qvel[0]) if c.heave else 0.
            samples.append(dict(time_s=float(d.time),edge_time_s=edge,x_m=wheel[0],wheel_z_m=wheel[2],hip_z_m=hip[2],
                extension_m=hip[2]-wheel[2],wheel_vz_mps=wvel[2],extension_speed_mps=hipvz-wvel[2],
                theta2_deg=math.degrees(q),joint_speed_radps=qd,spring_force_N=f,spring_torque_Nm=ts,
                damper_torque_Nm=-c.damping*qd,spring_energy_J=u,payout_from_reference_m=dc,
                floor_load_N=loads['floor'],block_load_N=loads['block'],coupling_error_rad=qk-(math.pi-2*q),
                path_error_m=abs(wheel[0]-hip[0]),stop_margin_deg=min(math.degrees(q)-100,165-math.degrees(q)),
                hip_vz_mps=hipvz))
        if i%max(1,round(1/600/c.dt))==0:
            pose_t.append(float(d.time));poses.append(d.qpos.copy());vel.append(d.qvel.copy())
        if not np.isfinite(d.qpos).all() or any(w.number for w in d.warning):
            warn=[str(w.number) for w in d.warning];break
        mujoco.mj_step(m,d)
    assert not warn,warn
    h={k:np.array([r[k] for r in samples]) for k in samples[0]};t=h['time_s'];active=t>=edge-.2
    contact=h['floor_load_N']+h['block_load_N']>1.
    # Detect the final departure from block before first lower-floor loading.
    landing=np.flatnonzero((h['floor_load_N']>1)&(t>edge-.1))
    land=int(landing[0]) if len(landing) else None
    lastblock=np.flatnonzero((h['block_load_N']>1)&(t<=(t[land] if land is not None else t[-1])))
    leave=int(lastblock[-1]) if len(lastblock) else None
    metrics=dict(edge_time_s=edge,block_departure_s=float(t[leave]) if leave is not None else None,
        floor_recontact_s=float(t[land]) if land is not None else None,
        flight_s=float(t[land]-t[leave]) if land is not None and leave is not None else None,
        recontact_downward_speed_mps=float(-h['wheel_vz_mps'][max(0,land-1)]) if land is not None else None,
        peak_extension_speed_mps=float(max(h['extension_speed_mps'][active])),
        peak_abs_joint_speed_radps=float(max(abs(h['joint_speed_radps'][active]))),
        peak_spring_force_N=float(max(h['spring_force_N'][active])),peak_floor_normal_N=float(max(h['floor_load_N'][active])),
        contact_loss_s=float(np.sum(~contact[active])*.0005),
        max_coupling_error_rad=float(max(abs(h['coupling_error_rad']))),max_path_error_m=float(max(h['path_error_m'])),
        minimum_stop_margin_deg=float(min(h['stop_margin_deg'])),hip_drop_m=float(h['hip_z_m'][0]-min(h['hip_z_m'])),
        final_extension_m=float(h['extension_m'][-1]),duration_s=float(t[-1]),wall_seconds=time.perf_counter()-wall,
        compiled_mass_kg=float(m.body_mass.sum()),warnings=warn)
    with (folder/'history.csv').open('w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=samples[0]);writer.writeheader();writer.writerows(samples)
    np.savez_compressed(folder/'poses.npz',time_s=pose_t,qpos=poses,qvel=vel)
    (folder/'model.xml').write_text(xml)
    result=dict(case=asdict(c),metrics=metrics,model_sha256=hashlib.sha256(xml.encode()).hexdigest())
    dump(folder/'results.json',result)
    print(c.name,json.dumps(metrics),flush=True)
    return result

def history(name):
    return np.genfromtxt(RAW/name/'history.csv',delimiter=',',names=True)

def report(results):
    OUT.mkdir(parents=True,exist_ok=True);BENCH.mkdir(parents=True,exist_ok=True)
    colors=['#087e8b','#d56824','#7857a8']
    fig,axes=plt.subplots(3,2,figsize=(13,10),sharex=True)
    for color,name,label in zip(colors,['fixed-v05-b0','fixed-v05-b15','heave-balanced-v05-b0'],['Hip held: spring only','Hip held: + assumed damping','Heave: matched static load']):
        h=history(name);x=h['time_s']-h['edge_time_s']
        values=[1000*(h['wheel_z_m'][0]-h['wheel_z_m']),h['extension_speed_mps'],h['theta2_deg'],h['joint_speed_radps'],h['floor_load_N']+h['block_load_N'],1000*(h['hip_z_m'][0]-h['hip_z_m'])]
        for ax,y in zip(axes.flat,values):ax.plot(x,y,color=color,label=label,lw=1.6)
    labels=['Wheel descent from initial height (mm)','Extension speed (m/s)','Hip angle theta2 (deg)','Hip angular velocity (rad/s)','Total tire contact normal (N)','Chassis descent (mm)']
    for ax,label in zip(axes.flat,labels):
        ax.axvline(0,color='k',ls=':',lw=1);ax.grid(alpha=.2);ax.set_ylabel(label);ax.set_xlim(-.25,.9)
    axes[0,0].axhline(100,color='gray',ls='--',lw=1);axes[0,0].legend(fontsize=8)
    for ax in axes[-1]:ax.set_xlabel('Time relative to wheel centre crossing block edge (s)')
    fig.suptitle('Jon V4 spring | 100 mm block exit at 0.5 m/s\nSimulated contact dynamics; masses and damping assumed; horizontal carriage prescribed')
    fig.tight_layout();fig.savefig(OUT/'descent-profile.png',dpi=170);fig.savefig(BENCH/'descent-profile.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    for speed,color in zip([.25,.5,1.],colors):
        h=history(f'fixed-v{str(speed).replace(".","")}-b0' if speed!=.25 else 'fixed-v025-b0')
        x=h['time_s']-h['edge_time_s'];axes[0].plot(x,1000*(h['wheel_z_m'][0]-h['wheel_z_m']),label=f'{speed} m/s',color=color)
        axes[1].plot(x,h['extension_speed_mps'],label=f'{speed} m/s',color=color)
    for ax in axes:ax.set_xlim(-.25,.5);ax.grid(alpha=.2);ax.set_xlabel('Time from centre crossing edge (s)');ax.legend()
    axes[0].set_ylabel('Wheel descent (mm)');axes[1].set_ylabel('Extension speed (m/s)')
    fig.suptitle('Spring-only speed sensitivity | fixed-height hip fixture');fig.tight_layout();fig.savefig(OUT/'speed-sensitivity.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),sharex=True)
    for name,color,label in [('fixed-v05-b0',colors[0],'Jon spring only'),('fixed-v05-b15',colors[1],'+ assumed damper')]:
        h=history(name);x=1000*(h['time_s']-h['edge_time_s'])
        axes[0].plot(x,1000*(h['wheel_z_m'][0]-h['wheel_z_m']),color=color,label=label,lw=2)
        axes[1].plot(x,h['extension_speed_mps'],color=color,label=label,lw=2)
    axes[0].axhline(100,color='gray',ls=':',label='100 mm lower floor')
    axes[0].set_ylabel('Wheel descent (mm)');axes[1].set_ylabel('Downward extension speed (m/s)')
    for ax in axes:
        ax.set_xlim(-10,280);ax.grid(alpha=.2);ax.set_xlabel('Time after wheel centre passes edge (ms)');ax.legend(fontsize=9)
        ax.axvline(205.5,color='gray',ls=':',lw=1)
    fig.suptitle('Computed descent profile: 100 mm block, 0.5 m/s\nHip height held; no commanded vertical trajectory or suspension motor')
    fig.tight_layout();fig.savefig(OUT/'descent-closeup.png',dpi=180);fig.savefig(BENCH/'descent-closeup.png',dpi=180);plt.close(fig)

def render():
    OUT.mkdir(parents=True,exist_ok=True);frames=RAW/'frames-1x';frames.mkdir(exist_ok=True)
    cases=[]
    for name in ['fixed-v05-b0','fixed-v05-b15']:
        r=json.loads((RAW/name/'results.json').read_text());m=mujoco.MjModel.from_xml_path(str(RAW/name/'model.xml'))
        cases.append(dict(name=name,result=r,m=m,d=mujoco.MjData(m),pose=np.load(RAW/name/'poses.npz'),h=history(name),renderer=mujoco.Renderer(m,height=650,width=960)))
    fonts={n:ImageFont.truetype(str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'),n) for n in [22,25,30,36]}
    fps=60;end=min(x['result']['metrics']['duration_s'] for x in cases);errors=[]
    for frame in range(math.floor(end*fps)+1):
        t=frame/fps;canvas=Image.new('RGB',(1920,1080),'#10252d');draw=ImageDraw.Draw(canvas)
        draw.text((24,18),'Single leg leaving a 100 mm block | Jon V4 finite-pulley spring',font=fonts[36],fill='white')
        draw.text((24,68),'ACTUAL SPEED 1x | 0.5 m/s horizontal test carriage | 300 mm links / 100 mm wheel radius',font=fonts[25],fill='#bddde4')
        for col,item in enumerate(cases):
            p=item['pose'];k=int(np.argmin(abs(p['time_s']-t)));d=item['d'];m=item['m'];d.qpos[:]=p['qpos'][k];d.qvel[:]=p['qvel'][k];mujoco.mj_forward(m,d)
            errors.append(abs(p['time_s'][k]-t));cam=mujoco.MjvCamera();cam.lookat[:]=[d.body('chassis').xpos[0]-.1,0,.33];cam.distance=1.6;cam.azimuth=90;cam.elevation=-10
            ren=item['renderer'];ren.update_scene(d,camera=cam)
            # Source-routed cable, idler and horn are visual overlays of the
            # equivalent energy-derived spring torque, not additional forces.
            q=float(d.joint('hip').qpos[0]);_,_,D,Q,psi,wrap=Spring().geometry(q);hip=d.body('chassis').xpos
            def pt(xz):return hip+np.array([xz[0],-.055,xz[1]])
            def line(a,b,rgb,width=.002):
                scene=ren.scene;geom=scene.geoms[scene.ngeom]
                mujoco.mjv_initGeom(geom,mujoco.mjtGeom.mjGEOM_CAPSULE,np.zeros(3),np.zeros(3),np.eye(3).flatten(),np.array([*rgb,1.]))
                mujoco.mjv_connector(geom,mujoco.mjtGeom.mjGEOM_CAPSULE,width,np.array(a),np.array(b));scene.ngeom+=1
            s=Spring();line(pt((0,0)),pt(D),(.8,.25,.65),.004);line(pt(D),pt(Q),(.9,.45,.8))
            arc=np.linspace(psi,psi-wrap,24)
            pts=[pt((s.su+s.rho*math.cos(a),s.sv+s.rho*math.sin(a))) for a in arc]
            for a,b in zip(pts,pts[1:]):line(a,b,(.9,.45,.8))
            line(pts[-1],pt((s.su+.09,s.sv+s.rho)),(.9,.45,.8))
            # Spring shown schematically; real installed length not specified.
            for j in range(16):
                a=(s.su+.09+j*.005,s.sv+s.rho+(.008 if j%2 else -.008));b=(s.su+.09+(j+1)*.005,s.sv+s.rho+(.008 if (j+1)%2 else -.008));line(pt(a),pt(b),(.9,.45,.8))
            canvas.paste(Image.fromarray(ren.render()),(col*960,150))
            label='Spring only; no suspension motor' if col==0 else 'Same spring + assumed 1.5 N m s/rad damper'
            draw.text((col*960+24,112),label,font=fonts[30],fill='white')
            h=item['h'];j=int(np.argmin(abs(h['time_s']-t)));contact=h['floor_load_N'][j]+h['block_load_N'][j]>1
            draw.text((col*960+24,810),f't = {t:.3f} s | '+('CONTACT' if contact else 'AIRBORNE'),font=fonts[30],fill='#ffcf82')
            draw.text((col*960+24,855),f'Extension speed {h["extension_speed_mps"][j]:+.2f} m/s | hip {h["theta2_deg"][j]:.1f} deg',font=fonts[25],fill='white')
            draw.text((col*960+24,895),f'Spring tension {h["spring_force_N"][j]:.0f} N | tire normal {h["floor_load_N"][j]+h["block_load_N"][j]:.0f} N',font=fonts[25],fill='white')
        draw.text((24,960),'Hip height held by fixture; wheel vertical motion and contact are solved by MuJoCo.',font=fonts[25],fill='#bddde4')
        draw.text((24,1002),'Assumed link/wheel masses; ideal frictionless cable. Spring drawing schematic; hardware behavior unverified.',font=fonts[22],fill='#bddde4')
        canvas.save(frames/f'{frame:05d}.png')
        if frame in [30,40,42,43,60]:canvas.save(OUT/f'preview-{frame}.png')
    for item in cases:item['renderer'].close()
    dump(OUT/'render-provenance.json',dict(fps=fps,frames=frame+1,duration_s=(frame+1)/fps,playback_rate=1,max_pose_time_error_s=float(max(errors)),source_commit=COMMIT))
    print('Rendered',frame+1,'actual-speed frames',flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args()
    if args.render:render();return
    checks=verify();dump(RAW/'checks.json',checks);print('CHECKS',checks,flush=True)
    if args.check:return
    cases=[Case(),Case(name='fixed-v025-b0',speed=.25),Case(name='fixed-v10-b0',speed=1.),
        Case(name='fixed-v05-b15',damping=1.5),Case(name='heave-v05-b0',heave=True),
        Case(name='heave-balanced-v05-b0',heave=True,chassis_mass=13-.75*.6-.25*.65),
        Case(name='heave-balanced-v05-b15',heave=True,chassis_mass=13-.75*.6-.25*.65,damping=1.5),
        Case(name='fixed-v05-m05',mass_scale=.5),Case(name='fixed-v05-m2',mass_scale=2.),
        Case(name='fixed-v05-half-dt',dt=.0000625),Case(name='fixed-v05-half-contact',contact_time=.002)]
    results=[run(c) for c in cases]
    dump(RAW/'study.json',dict(source_commit=COMMIT,source_preset='v4-textbook-10mm.json',mujoco=mujoco.__version__,python=sys.version,cases=results,checks=checks,
        assumptions=['Horizontal carriage path prescribed; wheel height never prescribed.','Base hip height held; separate heave case retains 13kg chassis and same spring.','Moving masses .6/.65/1.5kg assumed from prior Andy bench; not CAD measurements.','No motor or rotor inertia; base zero damping; comparison 1.5Nms/rad assumed.','Ideal cable spring torque from source energy; no cable friction/stretch or physical spring packaging.']))
    report(results)

if __name__=='__main__':main()
