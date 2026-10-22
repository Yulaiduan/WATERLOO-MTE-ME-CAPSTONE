"""Verify experimental Kinefold builder-linked dynamics, without a server/UI.

Run .venv/Scripts/python.exe verify_dynamics.py from this app root. Inputs:
vendored JS V4 reference and varied mm/deg/kg/N fixtures, SI run settings.
Outputs assertion counts and measured parity/convergence errors on stdout.
Requires Node, SciPy and Pymunk; tests mathematical/engine consistency only,
not hardware, terrain contact, manufacturing or canonical robot validation.
"""
import json
import math
from pathlib import Path
import subprocess
import unittest

from dynamic_model import Model, R, defaults
from dynamics import simulate

ROOT = Path(__file__).resolve().parent
JS = r"""
const fs=require('fs'),vm=require('vm');
vm.runInThisContext(fs.readFileSync('reference-v4.js','utf8'));
vm.runInThisContext(fs.readFileSync('model.js','utf8'));
const base=Kinefold.defaults;
const variants=[{}, {L2:340,L3:280,ra:47,rb:27,rc:31,rd:39,re:22,rf:29,alpha:13,phi0:17,beta:28,loadMode:'contact',Fn:90,Ft:12,m2:.5,m3:.5,m5:.2,m6:1},
 {springLaw:'constant',alpha:25,beta:40,loadMode:'global',Fx:-7,Fz:65,m2:.3,m3:.8,m6:1.2}, {rs:0,Su:0,nu:8}, {springEnabled:false}];
console.log(JSON.stringify(variants.map(v=>{const p={...base,...v};return {p,rows:[101,120,140,164].map(theta=>{const s=Kinefold.evaluate({...p,theta2:theta});if(!s.valid)throw Error(s.errors);return {theta,tau:s.raw.tau2,Fs:s.spring.force,energy:s.spring.energy,B:s.B,C:s.C};})};})));
"""


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.references = json.loads(subprocess.check_output(['node', '-e', JS], cwd=ROOT, text=True))
        cls.base = cls.references[0]['p']
        cls.dynamic = {**cls.base, 'm2': .5, 'm3': .5, 'm5': .2, 'm6': 1}
        cls.report = {}

    def test_exact_source_parity_and_energy_derivatives(self):
        errors = []
        for variant in self.references:
            model = Model(variant['p'], defaults())
            for row in variant['rows']:
                q = row['theta'] * R
                errors.append(abs(-model.generalized(q) - row['tau']))
                self.assertAlmostEqual(-model.generalized(q), row['tau'], delta=2e-10)
                self.assertAlmostEqual(model.spring(q)['force'], row['Fs'], delta=2e-9)
                self.assertAlmostEqual(model.spring(q)['energy'], row['energy'], delta=2e-10)
                self.assertAlmostEqual(-model.sites(q)['6'][0][0] * 1000, row['C'][0], delta=2e-10)
                self.assertAlmostEqual(model.sites(q)['6'][0][1] * 1000, row['C'][2], delta=2e-10)
                eps = 1e-6
                fd = -(model.potential(q + eps) - model.potential(q - eps)) / (2 * eps)
                self.assertAlmostEqual(model.generalized(q), fd, delta=1e-6)
                M, dM = model.mass(q)
                self.assertGreater(M, 0)
                self.assertAlmostEqual(dM, (model.mass(q + eps)[0] - model.mass(q - eps)[0]) / (2 * eps), delta=1e-7)
        self.report['max_static_parity_Nm'] = max(errors)

    def test_equilibrium_in_both_engines(self):
        maxima = {}
        for p in (self.dynamic, self.references[1]['p'], {**self.dynamic, 'springLaw': 'constant'}):
            config = {**defaults(), 'duration': .2, 'dt': .0005, 'dampingNms': 0}
            model = Model(p, config)
            config['hipTorqueNm'] = -model.generalized(model.q0)
            for engine in ('analytical', 'pymunk'):
                result = simulate(dict(engine=engine, params=p, runConfig=config))
                drift = max(abs(row['theta2'] - p['theta2']) for row in result['rows'])
                maxima[engine] = max(maxima.get(engine, 0), drift)
                self.assertLess(drift, .002 if engine == 'pymunk' else 1e-7)
                if engine == 'pymunk':
                    self.assertEqual(result['diagnostics']['rigidBodies'], 4)
                    self.assertLess(result['diagnostics']['maxConstraintPositionErrorMm'], .02)
                    self.assertIn('bodyAnglesDeg', result['frames'][1])
        self.report['equilibrium_max_drift_deg'] = maxima

    def test_convergence_and_work_energy(self):
        # Start from actual equilibrium then give an explicit perturbation.
        p = self.references[1]['p']
        config = {**defaults(), 'duration': .4, 'outputHz': 100, 'initialVelocityDegS': 12, 'dampingNms': 0}
        model = Model(p, config)
        config['hipTorqueNm'] = -model.generalized(model.q0)
        reference = simulate(dict(engine='analytical', params=p, runConfig=config))
        self.assertLess(reference['diagnostics']['maxWorkEnergyResidualJ'], 1e-7)
        errors, residuals = [], []
        for dt in (.002, .001, .0005):
            result = simulate(dict(engine='pymunk', params=p, runConfig={**config, 'dt': dt}))
            self.assertEqual(result['diagnostics']['termination'], 'duration')
            errors.append(max(abs(a['theta2'] - b['theta2']) for a, b in zip(reference['rows'], result['rows'])))
            residuals.append(result['diagnostics']['maxWorkEnergyResidualJ'])
        self.assertLess(errors[-1], errors[0] * .75)
        self.assertLess(errors[-1], .2)
        self.assertLess(residuals[-1], residuals[0] * .8)
        self.report['refinement_dt_seconds'] = [.002, .001, .0005]
        self.report['pymunk_max_angle_error_deg'] = errors
        self.report['pymunk_max_work_energy_residual_J'] = residuals

    def test_validation_and_zero_mass(self):
        p, c = self.base, defaults()
        with self.assertRaisesRegex(ValueError, 'positive builder'):
            simulate(dict(engine='pymunk', params=p, runConfig=c))
        for bad in ({**p, 'm2': -1}, {**p, 'ra': 300}, {**p, 'theta2': float('nan')}, {**p, 'unknown': 1}):
            with self.assertRaises(ValueError):
                Model(bad, c)
        for config in ({**c, 'dt': 0}, {**c, 'duration': 30, 'dt': .0001}, {**c, 'iterations': 10.5}, {**c, 'I2': -1}):
            with self.assertRaises(ValueError):
                Model(p, config)
        # No m1 moving inertia is invented; analytical requires explicit rotor.
        with self.assertRaisesRegex(ValueError, 'Moving inertia is zero'):
            Model(p, {**c, 'hipRotorInertiaKgM2': 0})
        # A massless knee disc is omitted, never silently given inertial mass.
        no_disc = simulate(dict(engine='pymunk', params={**self.dynamic, 'm5': 0},
                                runConfig={**c, 'duration': .05}))
        self.assertEqual(no_disc['diagnostics']['rigidBodies'], 3)

    def test_stdin_cli(self):
        payload = dict(engine='analytical', params=self.base, runConfig={**defaults(), 'duration': .05})
        import sys
        result = subprocess.run([sys.executable, 'dynamics.py', '--request-stdin'], cwd=ROOT,
                                input=json.dumps(payload), text=True, capture_output=True, check=True)
        data = json.loads(result.stdout)
        self.assertEqual(data['engine'], 'analytical')
        self.assertEqual(data['params'], self.base)
        self.assertTrue(data['rows'])
        invalid = subprocess.run([sys.executable, 'dynamics.py', '--request-stdin'], cwd=ROOT,
                                 input='{}', text=True, capture_output=True)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn('error', json.loads(invalid.stdout))

    def test_travel_termination_and_actual_frames(self):
        p = {**self.dynamic, 'theta2': 164}
        c = {**defaults(), 'initialVelocityDegS': 100, 'duration': .1, 'dt': .0005}
        for engine in ('analytical', 'pymunk'):
            result = simulate(dict(engine=engine, params=p, runConfig=c))
            self.assertEqual(result['diagnostics']['termination'], 'travel-limit')
            for row, frame in zip(result['rows'], result['frames']):
                self.assertTrue(p['te'] <= row['theta2'] <= p['tc'])
                self.assertAlmostEqual(row['CxMm'], frame['C'][0])
                self.assertAlmostEqual(row['CzMm'], frame['C'][2])


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps(Checks.report, indent=2))
    raise SystemExit(not outcome.wasSuccessful())
