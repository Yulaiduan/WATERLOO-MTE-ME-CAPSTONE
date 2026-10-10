"""Verify independent energy dynamics and comparison with the Pymunk fixture.

Invocation: python -m unittest -v test_math_model from the app root.
Inputs: experimental SI configs and mild smooth wheel displacement, no files.
Outputs: assertions and refinement diagnostics. Requires NumPy/SciPy and Pymunk
for cross-model tests only. Agreement verifies ideal equations/numerics, not
hardware, unilateral tire contact or stop-impact loads.
"""
import json
import math
import subprocess
import sys
import unittest

import numpy as np

from math_model import config, parameters, simulate_math


class MathModelTests(unittest.TestCase):
    def test_model_import_does_not_load_pymunk(self):
        script = "import sys; import math_model; assert 'pymunk' not in sys.modules; assert 'physics' not in sys.modules"
        subprocess.run([sys.executable, '-c', script], check=True)

    def test_static_equilibrium_and_total_support(self):
        result = simulate_math({'duration': .4})
        expected = sum(result['config'][key] for key in
                       ('upper_mass', 'lower_mass', 'wheel_mass', 'chassis_mass'))*result['config']['gravity']
        for row in result['rows']:
            self.assertAlmostEqual(row['theta_deg'], 45., places=10)
            self.assertAlmostEqual(row['driver_force'], expected, places=9)
            self.assertAlmostEqual(row['chassis_ay'], 0., places=10)
        self.assertLess(result['diagnostics']['max_torque_check_Nm'], 1e-10)
        self.assertTrue(all(value < 1e-10 for value in result['equation_check_errors'].values()))
        json.dumps(result, allow_nan=False)

    def test_independent_preload_matches_geometric_equilibrium(self):
        c = config({'length': .35, 'extension': .08, 'theta': 38., 'chassis_mass': 12., 'stiffness': 12000.})
        rest = parameters(c)['rest']
        q = math.radians(c['theta'])
        A = np.array([0., 2*c['length']*math.sin(q)])
        E = (c['length']+c['extension'])*np.array([math.cos(q), math.sin(q)])
        s = np.linalg.norm(E-A)
        tension = c['stiffness']*(s-rest)
        spring_virtual_work = tension*2*c['length']*c['extension']*math.sin(2*q)/s
        gravity_virtual_work = c['gravity']*math.cos(q)*(1.5*c['upper_mass']*c['length']
                               +.5*c['lower_mass']*(c['length']+c['extension'])
                               +2*c['chassis_mass']*c['length'])
        self.assertAlmostEqual(spring_virtual_work, gravity_virtual_work, places=10)

    def test_zero_damping_energy_conservation_and_damped_decay(self):
        values = {'duration': .5, 'position_amplitude': 0., 'gravity': 0.,
                  'balance_spring': False, 'rest_length': .26, 'damping': 0.}
        free = simulate_math(values)
        energy = [row['mechanical_energy_J'] for row in free['rows']]
        self.assertLess(max(energy)-min(energy), 1e-7)
        damped = simulate_math({**values, 'damping': 100.})
        energy_damped = [row['mechanical_energy_J'] for row in damped['rows']]
        self.assertLess(energy_damped[-1], energy_damped[0]-.05)
        self.assertLess(max(np.diff(energy_damped)), 1e-7)

    def test_smooth_position_energy_work_and_solver_tolerance(self):
        coarse = simulate_math({'duration': 1.2}, rtol=1e-6, atol=1e-8, max_step=.01)
        fine = simulate_math({'duration': 1.2}, rtol=1e-10, atol=1e-12, max_step=.001)
        # The deliberately loose 1e-6 solve stays within 0.0001 degree of the
        # tighter solve across the joins of the C2 input trajectory.
        self.assertAlmostEqual(coarse['rows'][-1]['theta_deg'], fine['rows'][-1]['theta_deg'], delta=1e-4)
        self.assertAlmostEqual(fine['rows'][-1]['theta_deg'], 48.02864444, delta=1e-6)
        self.assertLess(abs(fine['diagnostics']['energy_balance_error_J']), 1e-6)
        self.assertEqual(fine['diagnostics']['max_position_error_m'], 0.)
        self.assertGreater(abs(fine['rows'][-1]['chassis_displacement']), .001)
        self.assertTrue(all(value < 1e-9 for value in fine['equation_check_errors'].values()))

    def test_pymunk_response_and_loads_converge_toward_independent_math(self):
        from physics import simulate
        math_result = simulate_math({'duration': 1.2})
        reference = math_result['rows'][-1]
        errors = []
        for dt in (.001, .0005, .00025):
            physical = simulate({'duration': 1.2, 'dt': dt})
            actual = physical['rows'][-1]
            self.assertAlmostEqual(physical['actual_rest_length'], math_result['actual_rest_length'], places=12)
            errors.append(abs(actual['theta_deg']-reference['theta_deg']))
            if dt == .00025:
                self.assertAlmostEqual(actual['chassis_displacement'], reference['chassis_displacement'], delta=.0004)
                self.assertAlmostEqual(actual['driver_force'], reference['driver_force'], delta=.1)
                self.assertAlmostEqual(actual['j2_force'], reference['j2_force'], delta=1.)
                self.assertAlmostEqual(actual['guide_hip_reaction'], reference['guide_hip_reaction'], delta=.1)
        print('Independent SciPy/Pymunk final-angle errors, 1/.5/.25 ms:', errors)
        self.assertLess(errors[-1], .05)
        self.assertLess(errors[-1], errors[0]/3)

    def test_locked_wheel_and_impedance_are_actual_dynamic_terms(self):
        free = simulate_math({'duration': .9})
        locked = simulate_math({'duration': .9, 'wheel_drive_locked': True})
        self.assertGreater(abs(free['rows'][-1]['theta_deg']-locked['rows'][-1]['theta_deg']), .001)
        self.assertLess(locked['diagnostics']['max_torque_check_Nm'], 1e-9)
        self.assertGreater(max(abs(row['wheel_drive_reaction']) for row in locked['rows']), .001)
        controlled = simulate_math({'duration': .9, 'knee_kp': 500., 'knee_kd': 10., 'torque_limit': .1})
        self.assertGreater(controlled['diagnostics']['clipped_steps'], 0)
        self.assertLessEqual(max(abs(row['actuator_torque']) for row in controlled['rows']), .1)
        self.assertGreater(abs(free['rows'][-1]['theta_deg']-controlled['rows'][-1]['theta_deg']), .001)

    def test_square_pulse_and_bias_do_not_change_shape_input(self):
        a = simulate_math({'duration': 1.5, 'wave': 'square'})
        b = simulate_math({'duration': 1.5, 'wave': 'square', 'bias_force': 20., 'bias_force_x': 10.})
        self.assertEqual(a['rows'][-1]['theta_deg'], b['rows'][-1]['theta_deg'])
        self.assertAlmostEqual(a['rows'][-1]['driver_force']-20., b['rows'][-1]['driver_force'])
        self.assertAlmostEqual(a['rows'][-1]['driver_fx']-10., b['rows'][-1]['driver_fx'])
        pulse = simulate_math({'duration': 1.5, 'wave': 'pulse'})
        self.assertAlmostEqual(pulse['rows'][-1]['position_command'], 0.)
        self.assertAlmostEqual(a['rows'][-1]['position_command'], 0.)

    def test_stop_event_ends_before_unmodelled_impact(self):
        result = simulate_math({'duration': 1., 'position_amplitude': .25,
                                'start': .1, 'rise': .04})
        self.assertIsNotNone(result['solver']['stop_event'])
        self.assertLess(result['diagnostics']['actual_duration_s'], 1.)
        event = result['solver']['stop_event']
        self.assertAlmostEqual(event['theta_deg'], result['config']['theta_min'] if event['limit'] == 'lower'
                               else result['config']['theta_max'], places=7)
        self.assertTrue(any('impact' in warning for warning in result['warnings']))
        self.assertEqual(result['rows'][-1]['stop_knee_torque'], 0.)

    def test_unsupported_boundary_conditions_fail_explicitly(self):
        for values in ({'fixture': 'hip'}, {'fixture': 'wheel'}, {'target': 'force'},
                       {'ramp_shape': 'linear'}, {'wave': 'impulse'}, {'load_point': 'contact'},
                       {'rise': 0.}, {'unknown': 1}, {'theta': float('nan')},
                       {'stiffness': 0., 'balance_spring': True}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                simulate_math(values)


if __name__ == '__main__':
    unittest.main(verbosity=2)
