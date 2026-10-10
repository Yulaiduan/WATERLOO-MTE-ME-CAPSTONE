"""Verify the wheel-leg zero-effective-length constant-lift adaptation.

Run: .venv/Scripts/python.exe -m unittest -v test_gravity_balance in this app.
Inputs: declared SI demo masses, mount/arm dimensions and smooth wheel heights.
Outputs: analytical geometry/energy, actual force-ledger and refinement checks.
Requires SciPy/Pymunk. Tests ideal passive emulation, not real coil/cable hardware,
ground contact, structural stress or constant dynamic support including damping.
"""
import json
import math
import unittest

from math_model import config as math_config, parameters, simulate_math
from physics import build, config, drive, simulate
from spring_mechanisms import (equal_poses, force_pair_power, generalized, geometry,
                               geometry_from_bodies, mechanism_metadata, spring_law)


class GravityBalanceTests(unittest.TestCase):
    def test_span_jacobian_and_constant_lift_follow_independent_geometry(self):
        c = config({'spring_topology': 'gravity_balance'})
        build(c)
        H, R, L = -c['spring_chassis_y'], c['spring_upper_fraction']*c['length'], c['length']
        expected = c['stiffness']*H*R/(2*L)
        for degrees in range(15, 81):
            q = math.radians(degrees)
            result = generalized(q, 0., c)
            span = math.sqrt(H*H+R*R-2*H*R*math.sin(q))
            self.assertAlmostEqual(result['geometry']['input_length'], span, places=13)
            self.assertAlmostEqual(result['geometry']['jacobian'], -H*R*math.cos(q)/span, places=13)
            self.assertAlmostEqual(result['law']['elastic_tension'], c['stiffness']*span, places=10)
            self.assertAlmostEqual(result['generalized_force']/(2*L*math.cos(q)), expected, places=10)

    def test_calibrated_rate_cancels_shape_gravity_potential_across_rom(self):
        c = math_config({'spring_topology': 'gravity_balance', 'stiffness': 1.})
        p = parameters(c)
        H, R = -c['spring_chassis_y'], c['spring_upper_fraction']*c['length']
        self.assertAlmostEqual(c['stiffness'], p['S']*c['gravity']/(H*R), places=10)
        self.assertEqual(p['rest'], .23)
        values = []
        for degrees in (15., 25., 45., 65., 80.):
            q = math.radians(degrees)
            law = generalized(q, 0., p['spring_config'])['law']
            values.append(law['energy']+p['S']*c['gravity']*math.sin(q))
        self.assertLess(max(values)-min(values), 1e-12)
        meta = mechanism_metadata(c, p['input_ref'])
        self.assertEqual(meta['automatic_balance'], 'rate_calibration')
        self.assertTrue(meta['constant_lift_eligible'])
        self.assertAlmostEqual(meta['constant_elastic_lift_N'], p['S']*c['gravity']/(2*c['length']))

    def test_physical_coil_positive_lengths_and_passive_routing_virtual_work(self):
        c = config({'spring_topology': 'gravity_balance'})
        build(c)
        for route, modes in (('direct', ('extension', 'captured')),
                             ('pullrod', ('compression', 'captured')),
                             ('ideal_rope', ('compression', 'captured'))):
            for mode in modes:
                values = dict(c, spring_transmission=route, spring_mode=mode)
                for degrees in (15., 45., 80.):
                    q = math.radians(degrees)
                    for speed in (-20., -.3, 0., .4, 20.):
                        result = generalized(q, speed, values)
                        law, geom = result['law'], result['geometry']
                        eta = 1. if route == 'direct' else -1.
                        self.assertAlmostEqual(law['coil_length'], c['rest_length']+eta*geom['input_length'])
                        self.assertGreater(law['coil_length'], 0.)
                        self.assertGreaterEqual(law['dissipation_rate'], -1e-10)
                        bodies = equal_poses(q, c, theta_speed=speed, base_speed=.2)
                        physical = geometry_from_bodies(bodies, values)
                        power = force_pair_power(physical['force_sites'], bodies, law['tension'])
                        self.assertAlmostEqual(power, result['generalized_force']*speed, delta=1e-9)
                        if route == 'ideal_rope':
                            self.assertGreaterEqual(law['tension'], 0.)
                            self.assertEqual(law['transmission_efficiency'], 1.)
                            self.assertEqual(law['rope_stretch'], 0.)

    def test_incompatible_modes_slack_or_reject_and_coil_geometry_is_checked(self):
        for edits in ({'spring_mode': 'compression'},
                      {'spring_transmission': 'pullrod', 'spring_mode': 'extension'},
                      {'spring_transmission': 'ideal_rope', 'spring_mode': 'extension'}):
            values = dict(edits, spring_topology='gravity_balance')
            with self.assertRaises(ValueError):
                build(config(values))
            with self.assertRaises(ValueError):
                parameters(math_config(values))
            c = config(dict(values, balance_spring=False))
            state = generalized(math.radians(c['theta']), .3, c)['law']
            self.assertTrue(state['slack'])
            self.assertEqual(state['tension'], 0.)
            self.assertEqual(state['energy'], 0.)
        with self.assertRaises(ValueError):
            build(config({'spring_topology': 'gravity_balance', 'spring_transmission': 'pullrod',
                          'spring_mode': 'compression', 'rest_length': .05}))

    def test_effective_offset_or_nonvertical_mount_break_constant_lift_claim(self):
        for edits in ({'spring_effective_free_length': .01}, {'spring_chassis_x': .03},
                      {'spring_force_law': 'hooke'}):
            c = math_config(dict(edits, spring_topology='gravity_balance'))
            p = parameters(c)
            meta = mechanism_metadata(c, p['input_ref'])
            self.assertFalse(meta['constant_lift_eligible'])
            self.assertTrue(meta['notes'])
            lifts = []
            for degrees in (25., 45., 70.):
                q = math.radians(degrees)
                lifts.append(generalized(q, 0., p['spring_config'])['generalized_elastic_force']/(2*c['length']*math.cos(q)))
            self.assertGreater(max(lifts)-min(lifts), 1.)

    def test_actual_point_force_balance_and_pretension_are_recorded(self):
        result = simulate({'spring_topology': 'gravity_balance', 'duration': 1.2,
                           'position_amplitude': .008})
        self.assertEqual(result['actual_rest_length'], .23)
        self.assertEqual(result['spring_mechanism']['automatic_balance'], 'rate_calibration')
        self.assertEqual(result['diagnostics']['stop_steps'], 0)
        self.assertLess(result['diagnostics']['max_force_check_N'], 1e-7)
        self.assertLess(result['diagnostics']['max_torque_check_Nm'], 1e-7)
        self.assertTrue(all(error < 1e-7 for error in result['equation_check_errors'].values()))
        self.assertGreater(min(row['spring_elastic_tension'] for row in result['rows']), 100.)
        self.assertTrue(all(row['spring_coil_length'] > .23 for row in result['rows']))
        self.assertGreater(result['peaks']['j1_force']['value'], 0.)
        json.dumps(result, allow_nan=False)

    def test_dynamic_refinement_matches_independent_energy_and_damping_ledger(self):
        values = {'spring_topology': 'gravity_balance', 'duration': 1.2, 'position_amplitude': .008}
        reference = simulate_math(values)
        self.assertLess(abs(reference['diagnostics']['energy_balance_error_J']), 1e-7)
        elastic = reference['spring_mechanism']['constant_elastic_lift_N']
        self.assertTrue(all(abs(row['spring_elastic_equivalent_lift_N']-elastic)<1e-9 for row in reference['rows']))
        errors = []
        for dt in (.001, .0005, .00025):
            physical = simulate(dict(values, dt=dt))
            errors.append(abs(physical['rows'][-1]['theta_deg']-reference['rows'][-1]['theta_deg']))
            self.assertEqual(physical['config']['stiffness'], reference['config']['stiffness'])
            self.assertLess(physical['diagnostics']['max_force_check_N'], 1e-7)
        print('Constant-lift final-angle errors, Pymunk 1/.5/.25 ms vs SciPy (degrees):', errors)
        self.assertLess(errors[1], errors[0]*.6)
        self.assertLess(errors[2], errors[1]*.6)
        self.assertLess(errors[2], .006)


if __name__ == '__main__':
    unittest.main(verbosity=2)
