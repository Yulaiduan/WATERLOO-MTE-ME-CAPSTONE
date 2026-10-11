"""Verify gravity-counterbalance equations and independent/physical dynamics.

Run: .venv/Scripts/python.exe -m unittest -v test_counterbalance from app root.
Inputs: illustrative SI lever/payload/coil profiles; no source or output files.
Outputs: geometry, equilibrium, energy, impulse and timestep-refinement checks.
Requires SciPy/Pymunk; ideal-model agreement does not validate hardware routing,
coil friction, contacts, stress, stop impact or a wheel-leg implementation.
"""
import json
import math
import subprocess
import sys
import unittest

import numpy as np

from counterbalance import (angle_state, build, config, forces, frame, geometry,
                            parameters, simulate, spring_state, static_screen)


class CounterbalanceTests(unittest.TestCase):
    def test_math_import_and_run_do_not_import_pymunk(self):
        script = "import sys; from counterbalance import simulate; simulate({'duration':.1}, 'math'); assert 'pymunk' not in sys.modules; assert 'physics' not in sys.modules"
        subprocess.run([sys.executable, '-c', script], check=True)

    def test_zero_length_lever_support_is_flat_and_balances_distributed_mass(self):
        c = config()
        p = parameters(c)
        self.assertAlmostEqual(c['stiffness'], 215.7463, places=8)
        self.assertAlmostEqual(p['required_support_N'], (c['payload_mass']+.5*c['lever_mass'])*c['gravity'], places=12)
        rows = static_screen(c)
        support = [row['equivalent_support_N'] for row in rows]
        tensions = [row['spring_force_N'] for row in rows]
        self.assertLess(max(support)-min(support), 1e-12)
        self.assertGreater(max(tensions)-min(tensions), 50.)
        self.assertLess(max(abs(row['hold_torque_Nm']) for row in rows), 1e-12)
        for row in rows:
            self.assertAlmostEqual(row['equivalent_support_N'], p['required_support_N'], places=11)
            self.assertAlmostEqual(row['coil_length_m'], c['physical_free_length']+row['span_m'], places=12)

    def test_ordinary_free_length_breaks_constant_balance_and_can_go_slack(self):
        c = config({'law': 'ordinary'})
        rows = static_screen(c)
        support = [row['equivalent_support_N'] for row in rows]
        self.assertGreater(max(support)-min(support), 10.)
        self.assertGreater(max(abs(row['hold_torque_Nm']) for row in rows), 3.)
        self.assertTrue(any(row['engaged'] == 0. and row['spring_force_N'] == 0. for row in rows))
        slack = spring_state(.1, 1., dict(c, damping=100.))
        self.assertEqual(slack['spring_force_N'], 0.)
        self.assertEqual(slack['dissipation_W'], 0.)
        self.assertEqual(slack['spring_energy_J'], 0.)
        result = simulate({'law': 'ordinary', 'duration': .1}, 'math')
        self.assertTrue(any('does not provide constant' in warning for warning in result['warnings']))

    def test_geometry_virtual_work_and_energy_derivative_are_independent(self):
        c = config({'stiffness_auto': False, 'stiffness': 170., 'law': 'ordinary',
                    'effective_free_length': .02})
        p = parameters(c)
        eps = 1e-6
        for q in np.deg2rad(np.linspace(-70, 70, 17)):
            geom = geometry(q, c)
            fd = (geometry(q+eps, c)['span']-geometry(q-eps, c)['span'])/(2*eps)
            self.assertAlmostEqual(geom['span_jacobian'], fd, delta=1e-10)
            state = forces(q, .37, c)
            moment_from_force = geom['attach'][0]*state['spring_fy']-geom['attach'][1]*state['spring_fx']
            self.assertAlmostEqual(moment_from_force, state['spring_moment_Nm'], places=12)
            energy = lambda angle: spring_state(geometry(angle, c)['span'], 0., c)['spring_energy_J']+c['gravity']*p['first_moment']*math.sin(angle)
            energy_gradient = (energy(q+eps)-energy(q-eps))/(2*eps)
            # Central differences of ~10 J energies incur a few nanonewton
            # metres of roundoff at a 1 microradian increment.
            self.assertAlmostEqual(-energy_gradient, forces(q, 0., c)['net_passive_moment_Nm'], delta=1e-8)

    def test_actual_aggregate_body_inertia_and_geometry(self):
        c = config({'mode': 'prescribed'})
        p = parameters(c)
        expected_com_inertia = (c['lever_mass']*c['length']**2/12
                                + c['lever_mass']*(c['length']/2-p['com_radius'])**2
                                + c['payload_mass']*(c['length']-p['com_radius'])**2)
        self.assertAlmostEqual(p['com_inertia'], expected_com_inertia, places=12)
        model = build(c)
        self.assertAlmostEqual(model['lever'].mass, c['payload_mass']+c['lever_mass'])
        self.assertAlmostEqual(model['lever'].moment, expected_com_inertia, places=12)
        self.assertEqual(len(model['space'].bodies), 1)
        self.assertEqual(len(model['space'].constraints), 2)
        self.assertEqual(len(model['space'].shapes), 3)
        actual = frame(model, c, 0.)
        ideal = geometry(math.radians(c['initial_angle_deg']), c)
        for key in ('pivot', 'anchor', 'attach', 'tip'):
            np.testing.assert_allclose(actual[key], ideal[key], atol=1e-14)
        self.assertTrue(actual['debug_draw'])
        free = build(config({'mode': 'free'}))
        self.assertIsNone(free['motor'])
        self.assertEqual(len(free['space'].constraints), 1)

    def test_free_neutral_balance_has_no_hidden_holding_motor(self):
        c = {'mode': 'free', 'duration': 1., 'initial_speed_deg': 12.}
        result = simulate(c, 'math')
        self.assertAlmostEqual(result['rows'][-1]['theta_deg'], 42., places=10)
        self.assertLess(abs(result['diagnostics']['energy_balance_error_J']), 1e-10)
        self.assertTrue(all(row['driver_torque_Nm'] == 0. for row in result['rows']))
        # Neutral equilibrium is not restoring stiffness: an initial velocity
        # persists when damping is absent, whereas damping removes energy.
        damped = simulate(dict(c, damping=5.), 'math')
        self.assertLess(damped['rows'][-1]['mechanical_energy_J'], damped['rows'][0]['mechanical_energy_J']-.001)
        self.assertTrue(all(row['dissipation_W'] >= -1e-12 for row in damped['rows']))

    def test_free_ordinary_coil_physics_loads_and_energy_converge_to_scipy(self):
        values = {'mode': 'free', 'law': 'ordinary', 'effective_free_length': .02, 'duration': .5}
        reference = simulate(values, 'math')
        self.assertAlmostEqual(reference['rows'][-1]['theta_deg'], 14.5333810223, delta=1e-7)
        errors, energy_errors = [], []
        for dt in (.001, .0005, .00025):
            physical = simulate(dict(values, dt=dt), 'pymunk')
            row = physical['rows'][-1]
            errors.append(abs(row['theta_deg']-reference['rows'][-1]['theta_deg']))
            energy_errors.append(abs(physical['diagnostics']['energy_balance_error_J']))
            self.assertLess(physical['diagnostics']['max_force_check_N'], 1e-8)
            self.assertLess(physical['diagnostics']['max_moment_check_Nm'], 1e-8)
            self.assertEqual(row['driver_torque_Nm'], 0.)
            self.assertIsNone(physical['diagnostics']['stop_event'])
            if dt == .00025:
                self.assertAlmostEqual(row['joint_force_N'], reference['rows'][-1]['joint_force_N'], delta=.05)
        print('Counterbalance free-angle errors (degrees), 1/.5/.25 ms:', errors)
        print('Counterbalance physical conservative energy errors (J):', energy_errors)
        self.assertLess(errors[1], errors[0]*.55)
        self.assertLess(errors[2], errors[1]*.55)
        self.assertLess(errors[-1], .02)
        self.assertLess(energy_errors[1], energy_errors[0]*.55)
        self.assertLess(energy_errors[2], energy_errors[1]*.55)
        self.assertLess(energy_errors[-1], .001)

    def test_prescribed_position_is_real_speed_motor_with_timestep_convergence(self):
        values = {'mode': 'prescribed', 'duration': 1.2}
        reference = simulate(values, 'math')
        q0 = config()['initial_angle_deg']
        self.assertAlmostEqual(reference['rows'][-1]['theta_deg'], q0+30., places=11)
        self.assertGreater(max(abs(row['driver_torque_Nm']) for row in reference['rows']), 10.)
        errors = []
        work_errors = []
        for dt in (.001, .0005, .00025):
            physical = simulate(dict(values, dt=dt), 'pymunk')
            self.assertEqual(physical['model']['constraints'][1]['class'], 'SimpleMotor')
            errors.append(physical['diagnostics']['max_angle_error_deg'])
            work_errors.append(abs(physical['diagnostics']['energy_balance_error_J']))
            self.assertLess(physical['diagnostics']['max_force_check_N'], 1e-8)
            self.assertLess(physical['diagnostics']['max_moment_check_Nm'], 1e-8)
            self.assertAlmostEqual(physical['rows'][-1]['theta_deg'], 60., places=8)
        self.assertLess(errors[1], errors[0]*.55)
        self.assertLess(errors[2], errors[1]*.55)
        self.assertLess(errors[-1], .06)
        self.assertLess(work_errors[2], work_errors[0]/2)

    def test_square_and_pulse_are_finite_c2_angular_position_inputs(self):
        for wave in ('square', 'pulse'):
            c = config({'mode': 'prescribed', 'wave': wave, 'duration': 1.5})
            self.assertEqual(angle_state(0., c)[1:], (0., 0.))
            self.assertAlmostEqual(angle_state(1.5, c)[0], math.radians(c['initial_angle_deg']))
            for t in (c['start'], c['start']+c['rise'],
                      c['start']+(c['period']*c['duty'] if wave == 'square' else c['pulse_width'])):
                self.assertAlmostEqual(angle_state(t, c)[1], 0., delta=1e-10)
                self.assertAlmostEqual(angle_state(t, c)[2], 0., delta=1e-9)
            for backend in ('math', 'pymunk'):
                result = simulate(c, backend)
                self.assertAlmostEqual(result['rows'][-1]['theta_deg'], 30., delta=.01)
                json.dumps(result, allow_nan=False)

    def test_vertical_equivalent_force_is_flagged_and_travel_stops_are_explicit(self):
        c = config({'anchor_height': .25})
        vertical = forces(math.pi/2, 0., c)
        self.assertEqual(vertical['equivalent_defined'], 0.)
        self.assertEqual(vertical['equivalent_support_N'], 0.)
        self.assertAlmostEqual(vertical['spring_moment_Nm'], 0., delta=1e-12)
        for backend in ('math', 'pymunk'):
            result = simulate({'mode': 'free', 'law': 'ordinary', 'duration': 2.}, backend)
            self.assertIsNotNone(result['diagnostics']['stop_event'])
            self.assertLess(result['diagnostics']['actual_duration_s'], 2.)
            self.assertTrue(any('impact' in warning for warning in result['warnings']))

    def test_config_rejects_unsupported_and_nonfinite_inputs(self):
        for values in ({'unknown': 1.}, {'stiffness_auto': 1}, {'payload_mass': float('nan')},
                       {'law': 'constant_tension'}, {'mode': 'controller'}, {'spring_radius': .5},
                       {'rise': 0.}, {'initial_speed_deg': 5.}, {'angle_amplitude_deg': 60.},
                       {'theta_max_deg': 110., 'angle_amplitude_deg': 70.}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                config(dict({'mode': 'prescribed'}, **values))
        manual = config({'stiffness_auto': False, 'stiffness': 123.})
        self.assertEqual(manual['stiffness'], 123.)
        self.assertNotEqual(config({'payload_mass': 3.})['stiffness'], config()['stiffness'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
