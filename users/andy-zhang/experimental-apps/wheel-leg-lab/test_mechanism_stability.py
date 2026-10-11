"""Check local passive stability and six-second suspension demo envelopes.

Run: .venv/Scripts/python.exe -m unittest -v test_mechanism_stability.
Inputs: exact editable catalog profiles, 30/45/60 degree poses, 30 mm C2 wheel
steps and square waves; SI units. Outputs: stability, finite state, travel,
engagement, momentum balance and independent-backend refinement assertions.
Requires SciPy/Pymunk; local stability and a finite tested envelope do not prove
global stability, unilateral ground contact, packaging or hardware performance.
"""
import math
import unittest
from math_model import config as math_config, parameters, simulate_math
from physics import DEFAULTS, build, config, simulate
from spring_mechanisms import CATALOG, apply_preset, passive_stability


class MechanismStabilityTests(unittest.TestCase):
    def test_resolvers_seed_demo_rates_and_preserve_explicit_overrides(self):
        for topology, entry in CATALOG.items():
            for resolve in (config, math_config):
                c = resolve({'spring_topology': topology})
                expected = apply_preset(DEFAULTS, topology)
                for key in entry['defaults']:
                    self.assertEqual(c[key], expected[key])
                explicit = resolve({'spring_topology': topology, 'stiffness': 12345., 'damping': 222.})
                self.assertEqual(explicit['stiffness'], 12345.)
                self.assertEqual(explicit['damping'], 222.)
        self.assertEqual(config()['stiffness'], 20000.)
        self.assertEqual(config()['damping'], 500.)
        self.assertEqual(config()['spring_integration'], 'point_force')

    def test_all_demo_local_stabilities_and_force_balance(self):
        for topology in CATALOG:
            for angle in (30., 45., 60.):
                with self.subTest(topology=topology, angle=angle):
                    c = math_config(dict(apply_preset(DEFAULTS, topology), theta=angle))
                    p = parameters(c)
                    report = passive_stability(c, p['rest'], p['input_ref'], p['auxiliary'])
                    self.assertEqual(report['classification'], 'neutral' if topology == 'gravity_balance' else 'restoring')
                    self.assertLess(abs(report['initial_force_balance_residual_N']), 1e-9)
                    m = build(config(c))
                    actual = passive_stability(c, m['rest'], m['spring_input_reference'], m['auxiliary'])
                    self.assertAlmostEqual(report['net_ride_stiffness_N_m'], actual['net_ride_stiffness_N_m'], delta=1e-7)

    def test_known_unsafe_edit_is_warned_and_fixed_fixture_not_classified(self):
        values = {'spring_topology': 'hip_pulley', 'spring_pulley_radius': .04,
                  'stiffness': 8000., 'damping': 100., 'duration': .2, 'knee_kp': 500.}
        for solve in (simulate, simulate_math):
            result = solve(values)
            self.assertEqual(result['passive_stability']['classification'], 'unstable')
            self.assertTrue(result['passive_stability']['active_controller_excluded'])
            self.assertTrue(any('locally unstable' in warning for warning in result['warnings']))
        self.assertEqual(simulate({'fixture': 'hip', 'duration': .2})['passive_stability']['classification'], 'not_applicable')

    def test_native_legacy_is_explicit_diagnostic_only(self):
        c = config({'spring_integration': 'native_legacy', 'duration': .2})
        self.assertIsNotNone(build(c)['spring'])
        self.assertTrue(any('splitting' in s for s in simulate(c)['warnings']))
        for topology in CATALOG:
            if topology != 'legacy_tip':
                with self.assertRaises(ValueError): config({'spring_topology': topology, 'spring_integration': 'native_legacy'})

    def test_all_catalog_profiles_complete_six_second_step_and_square_envelope(self):
        summary = []
        for topology in CATALOG:
            for angle in (30., 45., 60.):
                for wave in ('step', 'square'):
                    values = dict(apply_preset(DEFAULTS, topology), theta=angle, wave=wave)
                    for solve in (simulate, simulate_math):
                        with self.subTest(topology=topology, theta=angle, wave=wave, backend=solve.__name__):
                            result = solve(values)
                            self.assertAlmostEqual(result['rows'][-1]['t'], 6., places=8)
                            self.assertEqual(result['diagnostics']['stop_steps'], 0)
                            self.assertTrue(all(math.isfinite(v) for row in result['rows'] for v in row.values()))
                            self.assertGreater(min(r['theta_deg'] for r in result['rows']), values['theta_min'])
                            self.assertLess(max(r['theta_deg'] for r in result['rows']), values['theta_max'])
                            self.assertEqual(max(r['spring_slack'] for r in result['rows']), 0.)
                            self.assertEqual(max(abs(r['actuator_torque']) for r in result['rows']), 0.)
                            self.assertLess(result['diagnostics']['max_force_check_N'], 1e-7)
                            self.assertLess(result['diagnostics']['max_torque_check_Nm'], 1e-7)
                            support = min(r['driver_force'] for r in result['rows'])
                            self.assertGreater(support, 0., 'Accepted demo requires positive prescribed support; unilateral tire contact is still not solved.')
                            summary.append((topology, angle, wave, solve.__name__, support,
                                            min(r['theta_deg'] for r in result['rows']),
                                            max(r['theta_deg'] for r in result['rows'])))
        print('Six-second 108-backend-case envelope passes; minimum support N:', min(summary, key=lambda x: x[4]))

    def test_repaired_candidates_refine_toward_scipy(self):
        errors = {}
        for topology in ('legacy_tip', 'hip_pulley', 'hip_bellcrank', 'knee_bellcrank'):
            values = dict(apply_preset(DEFAULTS, topology), wave='square', theta=30.)
            ref = simulate_math(values)['rows'][-1]['theta_deg']
            series = [abs(simulate(dict(values, dt=dt))['rows'][-1]['theta_deg']-ref) for dt in (.001, .0005, .00025)]
            self.assertLess(series[-1], series[0]/2)
            self.assertLess(series[-1], .15)
            errors[topology] = series
        print('Six-second repaired-demo refinement errors degrees:', errors)


if __name__ == '__main__': unittest.main(verbosity=2)
