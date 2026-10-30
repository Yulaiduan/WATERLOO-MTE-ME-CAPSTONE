"""Verify optional geared motor laws and both real prescribed-height engines.

Run with the app SciPy/Pymunk Python: python verify_motor_bench.py. Inputs use
the source V4 builder fixture, SI motor properties and finite-rise bench runs.
Outputs unittest evidence and cross-engine numerical errors. These checks cover
an ideal experimental motor model, not measured hardware or tire contact.
"""
import json
import math
from pathlib import Path
import subprocess
import unittest

from dynamic_model import Model, R, defaults
from dynamics import simulate
from motor_model import DEFAULTS, Motor

ROOT = Path(__file__).resolve().parent


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = "const fs=require('fs'),vm=require('vm');for(const f of ['reference-v4.js','model.js'])vm.runInThisContext(fs.readFileSync(f,'utf8'));console.log(JSON.stringify(Kinefold.defaults));"
        cls.p = json.loads(subprocess.check_output(['node', '-e', script], cwd=ROOT, text=True))

    def test_ratio_command_and_independent_inertia(self):
        c = {**defaults(), 'inputHeightMm': 0, 'hipRotorInertiaKgM2': .03}
        base = Model(self.p, c)
        for n in (1, 10):
            motor = {**DEFAULTS, 'enabled': True, 'gearRatio': n, 'rotorInertiaKgM2': .002, 'commandBasis': 'motor'}
            m = Model(self.p, c, motor)
            self.assertAlmostEqual(m.mass(m.q0)[0] - base.mass(base.q0)[0], n*n*.002, places=13)
            self.assertEqual(m.motor.joint_command(20), 20*n)
            self.assertAlmostEqual(m.I['2'], .03+n*n*.002)
            row, _ = m.observe(0, m.q0, .7, 0)
            self.assertAlmostEqual(row['rotorKineticJ'], .5*.002*(n*.7)**2)
            self.assertAlmostEqual(row['legacyJointRotorKineticJ'], .5*.03*.7**2)

    def test_cogging_potential_and_cycle(self):
        motor = Motor.resolve({**DEFAULTS, 'enabled': True, 'gearRatio': 10, 'coggingAmplitudeNm': .3,
                               'coggingPeriodsPerRev': 7, 'coggingPhaseDeg': 28})
        for q in (0, .23, 1.7, 2.5):
            e = 1e-7
            derivative = (motor.motor_state(q+e, 0, 0)['coggingPotentialJ'] - motor.motor_state(q-e, 0, 0)['coggingPotentialJ'])/(2*e)
            self.assertAlmostEqual(-derivative, motor.motor_state(q, 0, 0)['jointCoggingNm'], delta=1e-8)
        cycle = 2*math.pi/70
        self.assertAlmostEqual(motor.motor_state(.23, 0, 0)['coggingPotentialJ'], motor.motor_state(.23+cycle, 0, 0)['coggingPotentialJ'], places=14)
        work = sum(motor.motor_state(.23+(i+.5)*cycle/10000, 0, 0)['jointCoggingNm']*cycle/10000 for i in range(10000))
        self.assertLess(abs(work), 1e-14)
        with self.assertRaisesRegex(ValueError, 'underresolved'):
            motor.check_step(10, .001)

    def test_gearbox_input_inertia_and_legacy_capture(self):
        config={**DEFAULTS,'enabled':True,'gearRatio':20,'rotorInertiaKgM2':.0008,'gearboxInputInertiaKgM2':.0001}
        motor=Motor.resolve(config)
        self.assertAlmostEqual(motor.reflected_inertia,400*.0009)
        self.assertAlmostEqual(motor.motor_state(1,2,0)['rotorKineticJ'],.5*400*.0009*4)
        legacy=dict(config);legacy.pop('gearboxInputInertiaKgM2')
        resolved=Motor.resolve(legacy)
        self.assertEqual(resolved.config,legacy)
        self.assertNotIn('gearboxInputInertiaKgM2',resolved.config)
        self.assertAlmostEqual(resolved.reflected_inertia,400*.0008)
        for value in (-1, True, float('nan')):
            with self.assertRaises(ValueError):Motor.resolve({**config,'gearboxInputInertiaKgM2':value})

    def test_friction_sign_dissipation_and_disabled(self):
        motor = Motor.resolve({**DEFAULTS, 'enabled': True, 'gearRatio': 10, 'coulombFrictionNm': .2, 'viscousFrictionNms': .03})
        for v in (-3, -.01, 0, .01, 3):
            s = motor.motor_state(2, v, 20)
            self.assertGreaterEqual(s['motorLossPowerW'], 0)
            self.assertAlmostEqual(s['jointFrictionNm']*v, -s['motorLossPowerW'])
            self.assertAlmostEqual(s['shaftCommandNm'], 2)
        disabled = Motor.resolve({**motor.config, 'enabled': False, 'commandBasis': 'motor'})
        self.assertEqual(disabled.joint_command(20), 20)
        self.assertEqual(disabled.reflected_inertia, 0)
        self.assertEqual(disabled.motor_state(2, 3, 20)['jointPassiveNm'], 0)

    def test_friction_resolution_guard(self):
        motor=Motor.resolve(dict(DEFAULTS,enabled=True,gearRatio=50,coulombFrictionNm=.01))
        with self.assertRaisesRegex(ValueError,'friction is underresolved'):
            motor.check_friction_step(.1,.001)
        motor.check_friction_step(.1,1e-7)

    def test_both_finite_rise_engines_and_ledger(self):
        motor = {**DEFAULTS, 'enabled': True, 'gearRatio': 10, 'rotorInertiaKgM2': .002,
                 'coggingAmplitudeNm': .01, 'coggingPeriodsPerRev': 2,
                 'coulombFrictionNm': .003, 'viscousFrictionNms': .001}
        c = {**defaults(), 'duration': .85, 'inputHeightMm': 30, 'inputRiseMm': 20,
             'inputDelayS': .2, 'dt': .0005, 'initialVelocityDegS': 1}
        results = [simulate(dict(engine=e, params=self.p, runConfig=c, motorConfig=motor)) for e in ('analytical', 'pymunk')]
        for result in results:
            self.assertEqual(result['diagnostics']['termination'], 'duration')
            self.assertGreater(result['rows'][-1]['motorFrictionLossJ'], 0)
            self.assertTrue(all(b['motorFrictionLossJ'] >= a['motorFrictionLossJ'] for a,b in zip(result['rows'], result['rows'][1:])))
            self.assertLess(result['diagnostics']['maxWorkEnergyResidualJ'], .03)
        self.assertLess(results[0]['diagnostics']['maxWorkEnergyResidualJ'], 1e-7)
        error = max(abs(a['chassisZMm']-b['chassisZMm']) for a,b in zip(results[0]['rows'],results[1]['rows']))
        self.assertLess(error, .2)
        print('motor finite-rise max heave difference mm:', error, 'ledger J:', [r['diagnostics']['maxWorkEnergyResidualJ'] for r in results])

    def test_guards_and_legacy_ideal(self):
        for field in ('rotorInertiaKgM2', 'gearboxInputInertiaKgM2', 'coulombFrictionNm', 'viscousFrictionNms'):
            with self.assertRaisesRegex(ValueError, 'Exact square'):
                Model(self.p, defaults(), {**DEFAULTS, 'enabled': True, field: .01})
        with self.assertRaises(ValueError):
            Motor.resolve({'enabled': True})
        for engine in ('analytical', 'pymunk'):
            c = {**defaults(), 'duration': .1, 'inputHeightMm': 0}
            plain = simulate(dict(engine=engine, params=self.p, runConfig=c))
            disabled = simulate(dict(engine=engine, params=self.p, runConfig=c, motorConfig=DEFAULTS))
            self.assertNotIn('motorConfig', plain)
            for a,b in zip(plain['rows'], disabled['rows']):
                for key in a:
                    self.assertAlmostEqual(a[key], b[key], delta=1e-10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
