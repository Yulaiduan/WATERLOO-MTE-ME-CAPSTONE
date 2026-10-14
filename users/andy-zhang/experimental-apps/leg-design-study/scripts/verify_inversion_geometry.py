"""Validate selected alpha-zero paths using actual Pymunk constraints.

Run: .venv/Scripts/python.exe scripts/verify_inversion_geometry.py
Inputs: retained selected geometries in mm/deg, explicit positive legacy body
masses, zero gravity/contact force, fixed hip and prescribed ideal motor motion.
Outputs: compact verification JSON in docs/inversion-engine-checks.json and
summary on stdout. Uses NumPy/SciPy/Pymunk from requirements.txt.
Limits: stepped ideal pivots/gears with self-collision disabled; no ground flip,
wheel/chassis collision, spring, motor rating or hardware inversion certification.
"""
from pathlib import Path
import json
import sys
import math
import hashlib
import platform
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import generalized_leg as g
from inversion_search import curve, R


def engine_run(c, start, end, dt):
    """Observe actual constrained wheel position versus independent V2 geometry."""
    import pymunk
    initial=g.kinematics(start*R,c);masses,moments=g.body_properties(c)
    space=pymunk.Space();space.gravity=(0,0);space.iterations=800;space.damping=1
    bodies={}
    for key in g.BODY_KEYS:
        b=pymunk.Body(body_type=pymunk.Body.STATIC) if key=='hip' else pymunk.Body(masses[key],moments[key])
        b.position=tuple(initial['positions'][key]);b.angle=initial['angles'][key]
        space.add(b);bodies[key]=b
    l2,l3=c['L2']/1000,c['L3']/1000
    pivots=[pymunk.PivotJoint(bodies['hip'],bodies['upper'],(0,0),(-l2/2,0)),
            pymunk.PivotJoint(bodies['upper'],bodies['lower'],(l2/2,0),(-l3/2,0)),
            pymunk.PivotJoint(bodies['lower'],bodies['wheel'],(l3/2,0),(0,0)),
            pymunk.PivotJoint(bodies['upper'],bodies['compound'],(l2/2,0),(0,0))]
    gears=[]
    for key in ['lower','compound','wheel']:
        slope=initial['angular_jacobian'][key]
        gears.append(pymunk.GearJoint(space.static_body,bodies[key],bodies[key].angle,1) if abs(slope)<1e-12
            else pymunk.GearJoint(bodies[key],bodies['upper'],slope*bodies['upper'].angle-bodies[key].angle,slope))
    motor=pymunk.SimpleMotor(bodies['upper'],bodies['hip'],0)
    for con in pivots+gears+[motor]:con.collide_bodies=False;con.error_bias=(1-.2)**60
    space.add(*(pivots+gears+[motor]))
    duration=2.;steps=round(duration/dt);max_path=max_pin=max_phase=max_tracking=0.;trace=[]
    def command(t):
        u=t/duration;return (start+(end-start)*(10*u**3-15*u**4+6*u**5))*R
    for i in range(steps):
        q0,q1=command(i*dt),command((i+1)*dt)
        motor.rate=(q1-q0)/dt;space.step(dt)
        actual_q=bodies['upper'].angle-math.pi
        expected=np.array(curve(actual_q,c['L2'],c['L3'],c['qab'],c['phi0'])[:2])
        actual=np.array(tuple(bodies['wheel'].position))*1000
        max_path=max(max_path,float(np.linalg.norm(actual-expected)))
        max_tracking=max(max_tracking,abs(actual_q-q1))
        for p in pivots:max_pin=max(max_pin,(p.a.local_to_world(p.anchor_a)-p.b.local_to_world(p.anchor_b)).length*1000)
        for p in gears:max_phase=max(max_phase,abs(p.b.angle*p.ratio-p.a.angle-p.phase))
        if i%max(1,steps//80)==0:trace.append(dict(q_deg=actual_q/R,x_mm=float(actual[0]),z_mm=float(actual[1])))
    passed=max_path<.1 and max_pin<.1 and max_phase<1e-4 and max_tracking<.01
    return dict(dt_s=dt,steps=steps,max_path_error_mm=max_path,max_pin_error_mm=max_pin,
                max_guide_error_rad=max_phase,max_command_tracking_error_rad=max_tracking,
                actual_endpoint_q_deg=actual_q/R,actual_endpoint_z_mm=float(actual[1]),passed=passed,
                trace=trace,engine='Pymunk '+pymunk.version)


def main():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'docs/inversion-path-results.json').read_text(encoding='utf-8'))
    rows=[]
    wanted=['equal_325','within5_325','size700_325']
    cases=[]
    for key in wanted:
        c=next((x for x in data['selected'] if x['id']==key or key in x.get('aliases',[])),None)
        if c and c not in cases:cases.append(c)
    cases.append(data['practical'][0])
    cases.append(next(x for x in data['examples'] if x['id']=='phase_near_equal_12p5'))
    for case in cases:
        cfg=case['config'];a,b=case['full_inversion']['angle_bounds_deg']
        c=g.physical_allocation(g.config(dict(L2=cfg['L2'],L3=cfg['L3'],ra=cfg['ra'],rb=60,
            alpha=0,phi0=cfg['phi0'],te=a,tc=b,g=0,Fy=0,Fz=0)))
        runs=[engine_run(c,a,b,dt) for dt in [.002,.001,.0005]]
        converges=runs[-1]['max_path_error_mm']<runs[0]['max_path_error_mm']*.8
        row=dict(id=case['id'],passed=all(run['passed'] for run in runs[1:]) and converges,
            resolved_config=c,
            refinement=runs,coarse_step_accepted=runs[0]['passed'],
            acceptance='Both 1ms and0.5ms satisfy0.1mm path/pin,1e-4rad guide,0.01rad tracking;0.5ms error improves over2ms. Coarse failures remain recorded.',
            scope='2s full angular inversion; actual Space.step, motor/pivot/gear constraints, positive masses, zero gravity/contact and no collision geometry.')
        rows.append(row);print(json.dumps(dict(id=row['id'],passed=row['passed'],
            refinement=[{k:v for k,v in run.items() if k!='trace'} for run in runs])),flush=True)
    output=dict(schema='camel/alpha-zero-inversion-engine/v1',all_passed=all(x['passed'] for x in rows),cases=rows,
        python=platform.python_version(),source_sha256={name:hashlib.sha256((root/name).read_bytes()).hexdigest()
          for name in ['scripts/verify_inversion_geometry.py','inversion_search.py','generalized_leg.py']})
    (root/'docs/inversion-engine-checks.json').write_bytes((json.dumps(output,separators=(',',':'))+'\n').encode())
    return 0 if output['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
