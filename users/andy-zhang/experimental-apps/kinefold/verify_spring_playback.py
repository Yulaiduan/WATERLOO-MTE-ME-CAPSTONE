"""Check actual constant-force dynamics and spring playback reconstruction.

Run with app .venv Python verify_spring_playback.py from this app directory.
Inputs: explicit V4 baseline, constant cable law, 330.869282809 N tension,
0.3 s flat prescribed/contact runs at dt=0.00025 s; contact wheel 1.5 kg,
mu=0.8, no bounce/free drive. Outputs unittest evidence, JSON findings and
ignored .preview SVG illustrations via the companion Node drawing check.
Tests exact virtual work, actual Pymunk effect and same-case analytical
comparison. No real browser/native visual inspection or hardware validation.
"""
import json
import math
from pathlib import Path
import subprocess
import unittest

from dynamic_model import Model, R, defaults
from dynamics import simulate
from contact_dynamics import simulate_contact
from analytical_contact import simulate_contact as analytical_contact
from desktop_viewer import spring_drawing

ROOT = Path(__file__).resolve().parent


class SpringPlaybackChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = "const fs=require('fs'),vm=require('vm');for(const f of ['reference-v4.js','model.js'])vm.runInThisContext(fs.readFileSync(f,'utf8'));console.log(JSON.stringify(Kinefold.defaults));"
        cls.base = json.loads(subprocess.check_output(['node', '-e', source], cwd=ROOT, text=True))
        cls.config = {**defaults(), 'duration': .3, 'inputHeightMm': 0, 'dt': .00025}
        cls.results, cls.report = {}, {}
        for mode in ('prescribed', 'contact'):
            for engine in ('pymunk', 'analytical'):
                for enabled in (True, False):
                    params = {**cls.base, 'springLaw': 'constant', 'springEnabled': enabled, 'm6': 1.5 if mode == 'contact' else 0}
                    payload = dict(engine=engine, params=params, runConfig=cls.config)
                    if mode == 'contact':
                        payload['contactConfig'] = dict(mode='terrain-contact', friction=.8, restitution=0, drive='free')
                        result = (simulate_contact if engine == 'pymunk' else analytical_contact)(payload)
                    else:
                        result = simulate(payload)
                    cls.results[mode, engine, enabled] = result

    def test_constant_tension_variable_torque_and_independent_virtual_work(self):
        report = []
        for law in ('constant', 'v4'):
            model = Model({**self.base, 'springLaw': law}, self.config)
            forces, torques, errors = [], [], []
            for angle in (105, 120, 132.5, 145, 160):
                q, eps = angle * R, 1e-6
                z = model.spring(q)
                virtual = -(model.spring(q + eps)['energy'] - model.spring(q - eps)['energy']) / (2 * eps)
                self.assertAlmostEqual(z['torque'], virtual, delta=3e-7)
                forces.append(z['force']); torques.append(z['torque']); errors.append(abs(z['torque'] - virtual))
            self.assertGreater(max(torques) - min(torques), 1)
            if law == 'constant':
                self.assertEqual(min(forces), self.base['p0']); self.assertEqual(max(forces), self.base['p0'])
            else:
                self.assertGreater(max(forces) - min(forces), 1)
            report.append(dict(law=law, forceRangeN=[min(forces), max(forces)], torqueRangeNm=[min(torques), max(torques)], maxVirtualWorkErrorNm=max(errors)))
        self.report['geometrySweep'] = report

    def test_actual_pymunk_force_effect_and_analytical_comparison(self):
        evidence = []
        for mode in ('prescribed', 'contact'):
            on = self.results[mode, 'pymunk', True]; off = self.results[mode, 'pymunk', False]
            analytical = self.results[mode, 'analytical', True]
            self.assertEqual(on['diagnostics']['termination'], 'duration')
            self.assertTrue(all(row['Fs'] == self.base['p0'] for row in on['rows']))
            self.assertTrue(all(row['Fs'] == 0 for row in off['rows']))
            common_on = next(row for row in on['rows'] if abs(row['t'] - .2) < 1e-10)
            common_off = next(row for row in off['rows'] if abs(row['t'] - .2) < 1e-10)
            self.assertGreater(abs(common_on['chassisZMm'] - common_off['chassisZMm']), 50)
            self.assertGreater(on['rows'][-1]['theta2'] - on['rows'][0]['theta2'], 20)
            error = max(abs(a['chassisZMm'] - b['chassisZMm']) for a, b in zip(on['rows'], analytical['rows']))
            self.assertLess(error, .3)
            model = Model({**on['params'], 'm6': 0}, self.config)
            payouts = [model.spring(row['theta2'] * R)['payout'] for row in on['rows']]
            self.assertGreater(max(payouts) - min(payouts), 5)
            evidence.append(dict(mode=mode, durationS=.3, dtS=.00025, tensionRangeN=[min(r['Fs'] for r in on['rows']), max(r['Fs'] for r in on['rows'])],
                                 thetaRangeDeg=[min(r['theta2'] for r in on['rows']), max(r['theta2'] for r in on['rows'])],
                                 payoutChangeMm=payouts[-1] - payouts[0], finalChassisOnMm=on['rows'][-1]['chassisZMm'], finalChassisOffMm=off['rows'][-1]['chassisZMm'],
                                 offTermination=off['diagnostics']['termination'], offEndTimeS=off['rows'][-1]['t'], comparisonTimeS=.2,
                                 chassisOnAtComparisonMm=common_on['chassisZMm'], chassisOffAtComparisonMm=common_off['chassisZMm'],
                                 maxAnalyticalVsPymunkChassisDifferenceMm=error))
        self.report['actualRuns'] = evidence

    def test_native_geometry_and_node_svg_from_actual_frames(self):
        fixtures = []
        for mode in ('prescribed', 'contact'):
            result = self.results[mode, 'pymunk', True]
            model = Model({**result['params'], 'm6': 0}, self.config)
            for frame in (result['frames'][0], result['frames'][len(result['frames']) // 2], result['frames'][-1]):
                drawing = spring_drawing(model, frame)
                for key in ('D', 'Q'):
                    for actual, expected in zip(drawing[key], frame[key]):
                        self.assertAlmostEqual(actual, expected, delta=2e-10)
                self.assertAlmostEqual(math.dist(drawing['arc'][0], drawing['Q']), 0, delta=1e-10)
                self.assertAlmostEqual(math.dist(drawing['arc'][-1], drawing['out']), 0, delta=1e-10)
                shifted = {**frame, 'actualA': [frame['A'][0] + 37, 0, frame['A'][2] + 93]}
                moved = spring_drawing(model, shifted)
                for key in ('D', 'S', 'out', 'remote'):
                    self.assertAlmostEqual(moved[key][0] - drawing[key][0], 37, delta=1e-10)
                    self.assertAlmostEqual(moved[key][2] - drawing[key][2], 93, delta=1e-10)
                self.assertEqual(moved['forceN'], drawing['forceN'])
            fixtures.append(result)
        output = subprocess.check_output(['node', 'verify-spring-playback.cjs'], input=json.dumps(fixtures), cwd=ROOT, text=True)
        self.report['svgChecks'] = json.loads(output)

    @classmethod
    def tearDownClass(cls):
        print(json.dumps(cls.report, indent=2, allow_nan=False))
        (ROOT / '.preview').mkdir(exist_ok=True)
        (ROOT / '.preview' / 'spring-audit-evidence.json').write_text(json.dumps(cls.report, indent=2, allow_nan=False), encoding='utf-8')


if __name__ == '__main__':
    unittest.main(verbosity=2)
