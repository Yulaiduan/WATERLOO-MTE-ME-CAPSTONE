"""Verify standalone lever end-force dynamics, release and portable live state.

Run: python -m unittest -v test_counterbalance_force from the app root.
Inputs: ideal single-link SI profiles and signed vertical point loads in N.
Outputs: neutral rest, force/torque/work, release continuity, bounds, replay and
SciPy/Pymunk refinement assertions. No controller/damping, contact, hardware
spring characterization or stop impacts are certified by these tests.
"""
import math
import unittest

import numpy as np

from counterbalance import (DEFAULTS, acceleration, advance, build, config,
                            end_force, math_observe, parameters, simulate)


class LeverEndForceTests(unittest.TestCase):
    def test_default_is_one_free_link_without_motor_or_damping(self):
        self.assertEqual(DEFAULTS['mode'], 'free')
        self.assertEqual(DEFAULTS['damping'], 0.)
        model = build(config())
        self.assertIsNone(model['motor'])
        self.assertEqual(len(model['space'].constraints), 1)
        self.assertEqual(len(model['space'].bodies), 1)
        for angle in (-65., 0., 60.):
            for backend in ('math', 'pymunk'):
                result = simulate({'initial_angle_deg': angle, 'duration': .4}, backend)
                self.assertAlmostEqual(result['rows'][-1]['theta_deg'], angle, delta=1e-8)

    def test_up_down_force_torque_acceleration_and_pin_balance(self):
        for force in (-3., 3.):
            c = config({'mode': 'force', 'force_history': [{'start': 0., 'end': 1., 'force_N': force}]})
            q = math.radians(30.)
            alpha = acceleration(0., q, 0., c)
            self.assertAlmostEqual(alpha, force*c['length']*math.cos(q)/parameters(c)['pivot_inertia'], places=12)
            row = math_observe(0., q, 0., alpha, c)
            self.assertAlmostEqual(row['end_force_moment_Nm'], force*c['length']*math.cos(q), places=12)
            self.assertEqual(row['driver_torque_Nm'], 0.)
            self.assertEqual(row['dissipation_W'], 0.)
            result = simulate(dict(c, duration=.1), 'pymunk')
            self.assertGreater(force*(result['rows'][-1]['theta_deg']-30.), 0.)
            self.assertLess(result['diagnostics']['max_force_check_N'], 1e-8)
            self.assertLess(result['diagnostics']['max_moment_check_Nm'], 1e-8)

    def test_pulse_release_coasts_and_external_work_matches_energy(self):
        c = {'mode': 'force', 'wave': 'pulse', 'force_amplitude_N': 2.,
             'start': .1, 'rise': .05, 'fall': .05, 'pulse_width': .3, 'duration': 1.}
        run = simulate(c, 'math')
        after = [row for row in run['rows'] if row['t'] > .401]
        self.assertTrue(all(row['end_force_N'] == 0. for row in after))
        self.assertGreater(after[0]['angular_velocity_rad_s'], .4)
        self.assertLess(max(row['angular_velocity_rad_s'] for row in after)-min(row['angular_velocity_rad_s'] for row in after), 1e-10)
        self.assertGreater(after[-1]['theta_deg'], after[0]['theta_deg']+10.)
        self.assertLess(abs(run['diagnostics']['energy_balance_error_J']), 1e-8)
        self.assertGreater(run['rows'][-1]['external_work_J'], .04)

    def test_opposite_force_brakes_instead_of_implicit_velocity_reset(self):
        c = {'mode': 'force', 'initial_speed_deg': 20., 'duration': .15,
             'force_history': [{'start': 0., 'end': .15, 'force_N': -2.}]}
        run = simulate(c, 'math')
        last = run['rows'][-1]
        self.assertGreater(last['angular_velocity_rad_s'], 0.)
        self.assertLess(last['angular_velocity_rad_s'], math.radians(20.))
        self.assertLess(last['external_work_J'], 0.)

    def test_live_release_preserves_state_and_replays_press_hold_history(self):
        state = {'t': 0., 'theta_deg': 30., 'angular_velocity_rad_s': 0.}
        history = []
        for force in (2., 2., 0., 0., -2., 0.):
            start = state['t']
            chunk = advance({'config': {}, 'state': state, 'force_N': force, 'advance_s': .1})
            history.append({'start': start, 'end': chunk['next_state']['t'], 'force_N': force})
            if force == 0.:
                self.assertAlmostEqual(chunk['next_state']['angular_velocity_rad_s'], state['angular_velocity_rad_s'], delta=1e-10)
            state = chunk['next_state']
        replay = simulate({'mode': 'force', 'force_history': history, 'duration': state['t']}, 'math')
        self.assertAlmostEqual(replay['rows'][-1]['theta_deg'], state['theta_deg'], delta=2e-6)
        self.assertAlmostEqual(replay['rows'][-1]['angular_velocity_rad_s'], state['angular_velocity_rad_s'], delta=1e-7)
        self.assertEqual(end_force(.35, replay['config']), 0.)
        self.assertEqual(end_force(.45, replay['config']), -2.)

    def test_physical_point_force_response_refines_to_independent_math(self):
        c = {'mode': 'force', 'wave': 'pulse', 'force_amplitude_N': 2.,
             'start': .1, 'rise': .05, 'fall': .05, 'pulse_width': .3, 'duration': 1.}
        reference = simulate(c, 'math')
        errors = []
        for dt in (.001, .0005, .00025):
            run = simulate(dict(c, dt=dt), 'pymunk')
            errors.append(abs(run['rows'][-1]['theta_deg']-reference['rows'][-1]['theta_deg']))
            self.assertIsNone(run['diagnostics']['stop_event'])
            self.assertTrue(all(row['driver_torque_Nm'] == 0. and row['dissipation_W'] == 0. for row in run['rows']))
            self.assertLess(run['diagnostics']['max_force_check_N'], 1e-8)
            self.assertLess(run['diagnostics']['max_moment_check_Nm'], 1e-8)
        print('Lever end-force final angle errors (degrees), 1/.5/.25 ms:', errors)
        self.assertLess(errors[1], errors[0]*.55)
        self.assertLess(errors[2], errors[1]*.55)
        self.assertLess(errors[-1], .08)

    def test_force_bounds_end_run_before_an_impact_or_singularity(self):
        for backend in ('math', 'pymunk'):
            run = simulate({'mode': 'force', 'wave': 'step', 'start': 0.,
                            'rise': 0., 'force_amplitude_N': 30., 'duration': 2.}, backend)
            self.assertIsNotNone(run['diagnostics']['stop_event'])
            self.assertLess(run['diagnostics']['actual_duration_s'], 1.)
            self.assertTrue(all(np.isfinite(list(row.values())).all() for row in run['rows']))
        with self.assertRaisesRegex(ValueError, '±89'):
            config({'mode': 'force', 'theta_max_deg': 110.})

    def test_history_and_live_values_are_bounded_validated_and_damping_explicit(self):
        for history in ([{'start': 0., 'end': .5, 'force_N': float('nan')}],
                        [{'start': .5, 'end': .1, 'force_N': 2.}],
                        [{'start': 0., 'end': 1., 'force_N': 2.}, {'start': .5, 'end': 2., 'force_N': 2.}],
                        [{'start': 0., 'end': 1., 'force_N': 501.}]):
            with self.assertRaises(ValueError):
                config({'mode': 'force', 'force_history': history})
        values = {'config': {}, 'state': {'t': 0., 'theta_deg': 30., 'angular_velocity_rad_s': 0.}, 'force_N': 2., 'advance_s': .1}
        for invalid in (dict(values, advance_s=1.), dict(values, force_N=501.),
                        dict(values, config={'damping': 1.}), dict(values, state={'t': float('nan'), 'theta_deg': 30., 'angular_velocity_rad_s': 0.})):
            with self.assertRaises(ValueError):
                advance(invalid)


if __name__ == '__main__':
    unittest.main(verbosity=2)
