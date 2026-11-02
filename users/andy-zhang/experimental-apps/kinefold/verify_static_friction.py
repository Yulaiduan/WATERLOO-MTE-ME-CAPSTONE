"""Verify experimental shaft static/breakaway friction and coupled reactions.

Run app .venv Python verify_static_friction.py. Inputs are tracked V5 profiles
(mm/deg/kg/N), copied explicit shaft thresholds (N m), SI inertia and time.
Outputs unittest results and selected diagnostic summaries to stdout; no files,
profiles, servers or user state are written. Requires installed SciPy/Pymunk.
Tests numerical stick/slip, internal momentum and work, not measured hardware
friction, an independently known kinetic coefficient or canonical robot physics.
"""
import copy
import json
import math
from pathlib import Path
import unittest
from types import SimpleNamespace

from motor_model import Motor,DEFAULTS,FRICTION_CONVENTION
from dynamic_model import Model
from contact_cases import validate_contact_request
from dynamics import simulate as bench
from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as native

ROOT=Path(__file__).resolve().parent


def request(alpha=0,cap=.05,contact=False,engine='analytical',duration=.15):
    p=json.loads((ROOT/f'saved-configurations/v5-alpha{alpha}-4to1.json').read_text())
    r=dict(engine=engine,params=p['params'],runConfig={**p['solverConfig'],
        'duration':duration,'dt':.0005,'outputHz':20,'inputHeightMm':0,
        'inputRiseMm':0,'inputSpeedMmS':0,'inputDelayS':0},
        motorConfig={**p['motorConfig'],'enabled':True,'coulombFrictionNm':cap})
    if contact:r.update(contactConfig=p['contactConfig'],caseConfig=p['caseConfig'])
    return r


def run(r):
    if 'contactConfig' not in r:return bench(r)
    return (analytical if r['engine']=='analytical' else native)(r)


class StaticFrictionChecks(unittest.TestCase):
    def test_native_exact_threshold_can_stick_without_work(self):
        import pymunk
        from motor_rotor_constraint import NativeDryFriction
        space=pymunk.Space();a=pymunk.Body(2,math.inf);b=pymunk.Body(1,1.)
        space.add(a,b)
        motor=Motor.resolve({**DEFAULTS,'enabled':True,'coulombFrictionNm':.05})
        m=SimpleNamespace(motor=motor,jacobian=lambda q:1.,distance=lambda q:1.,axis=(0.,1.))
        dry=NativeDryFriction(space,a,b,m,SimpleNamespace(upper=b))
        try:
            for _ in range(20):
                before=b.angle;b.torque=.05;dry.prepare(.001,0.);space.step(.001)
                self.assertEqual(b.angular_velocity,0.)
                self.assertEqual(dry.state,'sticking')
                self.assertAlmostEqual(dry.torque,-.05)
                self.assertEqual(dry.torque*(b.angle-before),0.)
            b.torque=.051;dry.prepare(.001,0.);space.step(.001)
            self.assertGreater(b.angular_velocity,0.)
            self.assertEqual(dry.state,'sliding')
        finally:dry.close()

    def test_scalar_inclusion_and_geared_separate_passives(self):
        m=Motor.resolve({**DEFAULTS,'enabled':True,'gearRatio':3,'hipBeltRatio':2,
            'coulombFrictionNm':.05,'viscousFrictionNms':.02,'rotorInertiaKgM2':.003})
        self.assertAlmostEqual(m.static_capacity,.3)
        self.assertAlmostEqual(m.reflected_inertia,.108)
        self.assertEqual(m.dry_torque(0,.2),-.2)
        self.assertAlmostEqual(m.dry_torque(0,.4),-.3)
        self.assertAlmostEqual(m.dry_torque(1,-100),-.3)
        self.assertAlmostEqual(m.dry_torque(-1,100),.3)
        self.assertAlmostEqual(m.dry_torque(.001,0,2,.1),-.02)
        # Force helper deliberately excludes dry: the solver owns its impulse.
        s=m.motor_state(1,2,0)
        self.assertEqual(s['jointDryFrictionNm'],0)
        self.assertAlmostEqual(s['jointViscousFrictionNm'],-1.44)
        self.assertAlmostEqual(s['viscousLossPowerW'],2.88)
        self.assertEqual(m.motor_state(1,0,0,-.2,'sticking')['motorLossPowerW'],0)

    def test_v5_static_flat_bench_and_actual_both_engines(self):
        reports=[]
        for alpha,expected in ((0,-.03418816296118621),(20,-.02718772409853898)):
            for contact in (False,True):
                for engine in ('analytical','pymunk'):
                    r=request(alpha,contact=contact,engine=engine);s=run(r)
                    self.assertEqual(s['diagnostics']['termination'],'duration')
                    self.assertLess(max(abs(row['theta2']-135) for row in s['rows']),1e-9)
                    self.assertEqual(s['rows'][-1]['motorDissipatedJ'],0.)
                    self.assertEqual(s['rows'][-1]['frictionState'],'sticking')
                    self.assertAlmostEqual(s['rows'][-1]['jointDryFrictionNm'],expected,delta=2e-6)
                    self.assertEqual(s['rows'][-1]['jointElectromagneticNm'],0)
                    self.assertEqual(s['scope']['frictionConvention'],FRICTION_CONVENTION)
                    if contact:
                        self.assertAlmostEqual(s['rows'][-1]['contactNormalForceN'],11.25*9.81,delta=.01)
                    reports.append((alpha,contact,engine,s['rows'][-1]['jointDryFrictionNm']))
        print('STATIC_V5 '+json.dumps(reports))

    def test_below_capacity_slips_and_zero_is_original_motor_off(self):
        for contact in (False,True):
            for engine in ('analytical','pymunk'):
                r=request(cap=.01,contact=contact,engine=engine);s=run(r)
                self.assertGreater(s['rows'][-1]['theta2']-135,1e-5)
                self.assertEqual(s['rows'][-1]['frictionState'],'sliding')
                self.assertAlmostEqual(s['rows'][-1]['jointDryFrictionNm'],-.01,delta=2e-8)
                self.assertGreater(s['rows'][-1]['motorDissipatedJ'],0)
                r=request(cap=0,contact=contact,engine=engine);zero=run(r)
                r['motorConfig']['enabled']=False;r['motorConfig']['coulombFrictionNm']=.05
                off=run(r)
                self.assertEqual([row['theta2'] for row in zero['rows']],[row['theta2'] for row in off['rows']])
                self.assertEqual(off['rows'][-1]['jointDryFrictionNm'],0)

    def test_command_breakaway_and_dry_plus_viscous_work(self):
        for contact in (False,True):
            for engine in ('analytical','pymunk'):
                r=request(contact=contact,engine=engine);r['runConfig']['hipTorqueNm']=.2
                r['motorConfig']['viscousFrictionNms']=.002;s=run(r);last=s['rows'][-1]
                self.assertGreater(last['theta2']-135,1e-4)
                self.assertAlmostEqual(last['jointDryFrictionNm'],-.05,delta=2e-7)
                self.assertAlmostEqual(last['jointElectromagneticNm'],.2)
                self.assertAlmostEqual(last['jointFrictionNm'],last['jointDryFrictionNm']+last['jointViscousFrictionNm'])
                self.assertGreater(last['motorDissipatedJ'],0)
                self.assertGreater(last['chassisVelocityMmS']**2,1e-8)
                if contact:
                    self.assertAlmostEqual(last['motorDissipatedJ'],last['motorCoulombDissipatedJ']+last['motorViscousDissipatedJ'],delta=1e-12)

    def test_motion_stops_and_resticks(self):
        for contact in (False,True):
            for engine in ('analytical','pymunk'):
                r=request(cap=.5,contact=contact,engine=engine,duration=.4)
                r['runConfig']['initialVelocityDegS']=1
                s=run(r);last=s['rows'][-1]
                self.assertGreater(last['theta2'],135)
                self.assertLess(abs(last['velocityDegS']),1e-9)
                self.assertEqual(last['frictionState'],'sticking')
                self.assertGreater(last['motorDissipatedJ'],0)
                self.assertAlmostEqual(last['motorDissipatedJ'],s['rows'][-2]['motorDissipatedJ'],delta=1e-10)

    def test_gear_capacity_and_legacy_massless_rotor_support(self):
        for engine in ('analytical','pymunk'):
            r=request(cap=.01,engine=engine);r['motorConfig'].update(gearRatio=3,hipBeltRatio=2)
            self.assertLess(abs(run(r)['rows'][-1]['theta2']-135),1e-9)
            for rotor in (0,.002):
                r=request(contact=True,engine=engine);r['params'].update(m2=0,m3=0)
                r['motorConfig']['rotorInertiaKgM2']=rotor
                m=validate_contact_request(r)
                r['runConfig']['hipTorqueNm']=m.grounded_gravity(m.q0)-m.spring(m.q0)['torque']+.02
                s=run(r)
                self.assertLess(abs(s['rows'][-1]['theta2']-135),1e-7)
                self.assertAlmostEqual(s['rows'][-1]['jointDryFrictionNm'],-.02,delta=2e-6)
                self.assertLess(s['rows'][-1]['motorDissipatedJ'],1e-10)

    def test_freeflight_internal_friction_preserves_com_momentum(self):
        for engine in ('analytical','pymunk'):
            for finite in (False,True):
                r=request(contact=True,engine=engine,duration=.1)
                if not finite:r['params'].update(m2=0,m3=0)
                r['motorConfig']['rotorInertiaKgM2']=.002
                r['caseConfig'].update(kind='landing',landingDropMm=2000)
                s=run(r)
                first,last=s['rows'][0],s['rows'][-1]
                self.assertAlmostEqual((last['comVelocityZMmS']-first['comVelocityZMmS'])/1000,-.981,delta=1e-8)
                self.assertEqual(last['motorDissipatedJ'],0)

    def test_smoothing_is_ignored_and_request_is_not_mutated(self):
        r=request();before=copy.deepcopy(r);s=run(r);self.assertEqual(r,before)
        r['motorConfig']['frictionVelocityScaleRadS']=1000
        other=run(r)
        self.assertEqual([row['theta2'] for row in s['rows']],[row['theta2'] for row in other['rows']])
        model=Model(r['params'],r['runConfig'],r['motorConfig'])
        self.assertEqual(model.motor.static_capacity,.05)


if __name__=='__main__':unittest.main()
