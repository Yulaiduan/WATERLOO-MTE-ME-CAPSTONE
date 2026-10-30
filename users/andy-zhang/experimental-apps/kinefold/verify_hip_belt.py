"""Check the configurable ideal gearbox-output to hip belt stage.

Run app Python verify_hip_belt.py. Inputs are synthetic SI motor/gear properties
and existing finite-link mm/kg geometry; outputs unittest evidence, no files.
Checks transformations and two actual engines, not hardware belt compliance,
efficiency, packaging, impact strength or full-vehicle stability.
"""
import copy
import json
import math
import unittest

import actuator_comparison as ac
from actuation_limits import ACTUATOR_DEFAULTS, torque_limit, validate_actuator_config
from motor_model import DEFAULTS, Motor


class HipBelt(unittest.TestCase):
    def test_motor_legacy_shapes_and_scaling(self):
        c={**DEFAULTS,'enabled':True,'gearRatio':10,'rotorInertiaKgM2':.002,
           'gearboxInputInertiaKgM2':.001,'coulombFrictionNm':.05,
           'viscousFrictionNms':.002,'commandBasis':'motor'}
        legacy=dict(c);legacy.pop('hipBeltRatio')
        a=Motor.resolve(legacy);b=Motor.resolve(c)
        self.assertEqual(a.config,legacy)
        self.assertEqual(a.motor_state(.3,2,40),b.motor_state(.3,2,40))
        oldest=dict(legacy);oldest.pop('gearboxInputInertiaKgM2')
        self.assertEqual(Motor.resolve(oldest).config,oldest)
        belt_only=dict(oldest,hipBeltRatio=2)
        self.assertEqual(Motor.resolve(belt_only).config,belt_only)
        d=Motor.resolve(dict(c,hipBeltRatio=2))
        self.assertEqual(d.total_ratio,20)
        self.assertEqual(d.joint_command(3),60)
        self.assertAlmostEqual(d.reflected_inertia,4*a.reflected_inertia)
        state=d.motor_state(.3,2,40)
        self.assertEqual(state['motorVelocityRadS'],40)
        self.assertAlmostEqual(state['viscousLossPowerW'],4*a.motor_state(.3,2,40)['viscousLossPowerW'])
        for value in (0,3.1,True,None,float('nan')):
            with self.assertRaises(ValueError):Motor.resolve(dict(c,hipBeltRatio=value))

    def test_limits_before_belt_and_four_quadrant_power(self):
        c={**ACTUATOR_DEFAULTS,'ratio':10,'hipBeltRatio':2,'peakShaftNm':10,
           'forwardEfficiency':.8,'reverseEfficiency':.5,'gearboxPeakNm':30,
           'gearboxContinuousNm':20,'continuousShaftNm':10}
        legacy=dict(c);legacy.pop('hipBeltRatio')
        self.assertEqual(validate_actuator_config(legacy),legacy)
        self.assertEqual(validate_actuator_config(c),c)
        for qd,request in ((1,1000),(-1,-1000),(1,-1000),(-1,1000)):
            out=torque_limit(c,qd,request)
            self.assertEqual(abs(out['motorTorqueNm']),60)
            self.assertEqual(abs(out['gearboxOutputTorqueNm']),30)
            self.assertAlmostEqual(out['gearboxOutputRpm'],2*30/math.pi)
            self.assertEqual(out['totalReduction'],20)
            self.assertGreaterEqual(out['gearboxLossPowerW'],0)
        self.assertEqual(abs(torque_limit(c,1,1000,peak_elapsed_s=3)['motorTorqueNm']),40)
        # 1 rad/s hip = 19.1 rpm at the gearbox output: not 9.55 rpm.
        self.assertEqual(torque_limit(dict(c,maxOutputRpm=15),1,1000)['motorTorqueNm'],0)
        self.assertEqual(torque_limit(dict(c,maxInputRpm=150),1,1000)['motorTorqueNm'],0)
        for value in (0,3.1,True,None):
            with self.assertRaises(ValueError):validate_actuator_config(dict(c,hipBeltRatio=value))

    def test_hardware_capture_and_hip_side_inertia_once(self):
        catalog=ac.load_catalog();motor=catalog['motors'][0];gear=catalog['gearboxes'][0]
        a={**ac.ASSUMPTIONS,'hipBeltRatio':2,'unknownGearboxInputInertiaKgM2':.0001,
           'additionalOutputInertiaKgM2':.017}
        hw=ac.candidate_hardware(motor,gear,a)
        n=gear['ratio']*2
        self.assertAlmostEqual(hw['reflectedInertiaKgM2'],n*n*(hw['rotorInertiaKgM2']+hw['gearboxInputInertiaKgM2'])+.017)
        project=json.loads((ac.ROOT/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text(encoding='utf-8'))
        p=ac.contact_payload(project,hw,a,'terrain','analytical')
        self.assertEqual(p['motorConfig']['gearRatio'],gear['ratio'])
        self.assertEqual(p['actuatorConfig']['ratio'],gear['ratio'])
        self.assertEqual(p['motorConfig']['hipBeltRatio'],2)
        self.assertAlmostEqual(Motor.resolve(p['motorConfig']).reflected_inertia+p['runConfig']['hipRotorInertiaKgM2'],hw['reflectedInertiaKgM2']+project['solverConfig']['hipRotorInertiaKgM2'])
        self.assertAlmostEqual(p['motorConfig']['coulombFrictionNm']*n,hw['outputCoulombNm'])
        self.assertAlmostEqual(p['motorConfig']['viscousFrictionNms']*n*n,hw['outputViscousNms'])

    def test_equivalent_total_ratio_finite_both_engines(self):
        from analytical_contact import simulate_contact as analytical
        from contact_dynamics import simulate_contact as pymunk
        catalog=ac.load_catalog();project=json.loads((ac.ROOT/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text(encoding='utf-8'))
        a={**ac.ASSUMPTIONS,'hipBeltRatio':2,'dynamicDurationS':.08,'dynamicDt':.00025,
           'dynamicOutputHz':50,'dropHeightMm':20}
        hw=ac.candidate_hardware(catalog['motors'][0],catalog['gearboxes'][0],a)
        p=ac.contact_payload(project,hw,a,'landing','analytical')
        equivalent=copy.deepcopy(p)
        equivalent['motorConfig']['gearRatio']*=2;equivalent['motorConfig'].pop('hipBeltRatio')
        equivalent['actuatorConfig']['ratio']*=2;equivalent['actuatorConfig'].pop('hipBeltRatio')
        for key in ('gearboxPeakNm','gearboxContinuousNm'):
            if equivalent['actuatorConfig'][key] is not None:equivalent['actuatorConfig'][key]*=2
        for solver in (analytical,pymunk):
            r=solver(p);s=solver(equivalent)
            self.assertEqual(r['diagnostics']['termination'],'duration')
            self.assertEqual(r['snapshot']['motorConfig']['hipBeltRatio'],2)
            self.assertNotIn('hipBeltRatio',s['snapshot']['motorConfig'])
            self.assertEqual(len(r['rows']),len(s['rows']))
            for x,y in zip(r['rows'],s['rows']):
                for key in ('chassisZMm','theta2','rotorKineticJ','motorTorqueNm','shaftCommandNm'):
                    self.assertAlmostEqual(x[key],y[key],delta=1e-9)


if __name__=='__main__':unittest.main()
