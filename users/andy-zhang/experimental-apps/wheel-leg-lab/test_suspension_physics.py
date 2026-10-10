"""Check actual Pymunk spring presets against independent energy dynamics.

Run: .venv/Scripts/python.exe -m unittest -v test_suspension_physics.
Inputs: illustrative SI masses, anchors, coil laws and smooth wheel-height steps.
Outputs: equilibrium, geometry, virtual-work, energy and refinement assertions.
Requires Pymunk and SciPy. These checks validate this ideal bilateral fixture,
not hardware, tire contact, pulley friction, structural stress or stop impacts.
"""
import math
import unittest

from pymunk import Vec2d

from math_model import config as math_config, derivative, parameters, simulate_math
from physics import build, config, drive, simulate
from spring_mechanisms import (CATALOG, force_pair_power, geometry,
                               geometry_from_bodies, spring_law)
import suspension_runtime as suspension


BODY_KEYS = ('hip', 'upper', 'lower')


def mechanical_energy(model, c):
    """Actual rigid-body kinetic energy plus independently sampled coil energy."""
    bodies = {key: model[key] for key in BODY_KEYS}
    geom = geometry_from_bodies(bodies, c)
    law = spring_law(geom['input_length'], geom['input_speed'],
                     dict(c, rest_length=model['rest']), model['spring_input_reference'])
    kinetic = sum(.5*model[key].mass*model[key].velocity.length_squared
                  + (.5*model[key].moment*model[key].angular_velocity**2
                     if math.isfinite(model[key].moment) else 0.)
                  for key in (*BODY_KEYS, 'wheel'))
    potential = sum(model[key].mass*c['gravity']*model[key].position.y
                    for key in (*BODY_KEYS, 'wheel'))
    return kinetic+potential+law['energy']


class SuspensionPhysicsTests(unittest.TestCase):
    def test_all_presets_static_preload_and_solver_impulse_balance(self):
        for topology in CATALOG:
            with self.subTest(topology=topology):
                values = {'spring_topology': topology, 'duration': .3}
                result = simulate(values)
                analytical = simulate_math(values)
                c = result['config']
                expected = sum(c[key] for key in ('upper_mass', 'lower_mass',
                                                'wheel_mass', 'chassis_mass'))*c['gravity']
                self.assertAlmostEqual(result['actual_rest_length'],
                                       analytical['actual_rest_length'], places=12)
                # Preload is analytically exact. Pymunk applies gravity and
                # spring forces in finite steps, producing a small startup
                # transient and pin drift; it should stay within 0.005 degree,
                # 0.5 N and 20 micrometres at the declared 1 ms timestep.
                for row in result['rows']:
                    self.assertAlmostEqual(row['theta_deg'], c['theta'], delta=.005)
                    self.assertAlmostEqual(row['driver_force'], expected, delta=.5)
                    self.assertAlmostEqual(row['actuator_torque'], 0., places=12)
                self.assertLess(result['diagnostics']['max_pin_error_m'], .00002)
                self.assertLess(result['diagnostics']['max_force_check_N'], 1e-8)
                self.assertLess(result['diagnostics']['max_torque_check_Nm'], 1e-8)
                self.assertTrue(all(error < 1e-8 for error in result['equation_check_errors'].values()))

    def test_actual_body_anchors_and_force_pairs_preserve_virtual_work(self):
        for topology in CATALOG:
            for direction in (1., -1.):
                with self.subTest(topology=topology, direction=direction):
                    c = config({'spring_topology': topology, 'spring_direction': direction,
                                'balance_spring': False, 'gravity': 0., 'rest_length': .2})
                    model = build(c)
                    bodies = {key: model[key] for key in BODY_KEYS}
                    q = math.radians(c['theta'])
                    rate = .37
                    L, e = c['length'], c['extension']
                    model['hip'].velocity = (0., 2*L*math.cos(q)*rate)
                    model['upper'].velocity = (-.5*L*math.sin(q)*rate,
                                               1.5*L*math.cos(q)*rate)
                    model['lower'].velocity = (-(L+e)/2*math.sin(q)*rate,
                                               (L+e)/2*math.cos(q)*rate)
                    model['upper'].angular_velocity = -rate
                    model['lower'].angular_velocity = rate
                    actual = geometry_from_bodies(bodies, c)
                    ideal = geometry(q, c)
                    self.assertAlmostEqual(actual['input_length'], ideal['input_length'], places=12)
                    self.assertAlmostEqual(actual['input_speed'], ideal['jacobian']*rate, places=10)
                    for anchor in actual['anchors'].values():
                        expected = bodies[anchor['body']].local_to_world(anchor['local'])
                        self.assertLess((Vec2d(*anchor['world'])-expected).length, 1e-12)
                    power = force_pair_power(actual['force_sites'], bodies, 73.)
                    self.assertAlmostEqual(power, -73.*actual['input_speed'], places=9)
                    suspension.update(model, c)
                    net = sum(model['spring_loads'].values(), Vec2d(0., 0.))
                    self.assertLess(net.length, 1e-10)
                    for key in BODY_KEYS:
                        self.assertLess((model[key].force-model['spring_loads'][key]).length, 1e-10)
                        self.assertAlmostEqual(model[key].torque, model['spring_torques'][key], places=10)

    def test_presets_are_engine_forces_and_shapes_with_one_shared_guide(self):
        for topology in CATALOG:
            with self.subTest(topology=topology):
                c = config({'spring_topology': topology})
                model = build(c)
                self.assertEqual(len(model['space'].shapes), 3)
                self.assertEqual(len(model['space'].constraints), 7 if topology == 'legacy_tip' else 6)
                self.assertEqual(model['guide'].ratio, -1.)
                self.assertEqual(model['guide'].phase, math.pi)
                self.assertEqual(model['manual_spring'], topology != 'legacy_tip')
                self.assertEqual(model['spring'] is None, topology != 'legacy_tip')
                self.assertTrue(all(shape.sensor for shape in model['space'].shapes))

    def test_all_presets_timestep_refinement_toward_independent_scipy(self):
        reports = {}
        for topology in CATALOG:
            with self.subTest(topology=topology):
                values = {'spring_topology': topology, 'duration': 1.2,
                          'position_amplitude': .008}
                reference = simulate_math(values)['rows'][-1]
                errors = []
                for dt in (.001, .0005, .00025):
                    result = simulate(dict(values, dt=dt))
                    row = result['rows'][-1]
                    errors.append(abs(row['theta_deg']-reference['theta_deg']))
                    self.assertEqual(result['diagnostics']['stop_steps'], 0)
                    self.assertLess(result['diagnostics']['max_force_check_N'], 1e-7)
                    self.assertLess(result['diagnostics']['max_torque_check_Nm'], 1e-7)
                    if dt == .00025:
                        self.assertAlmostEqual(row['j2_force'], reference['j2_force'], delta=.25)
                        self.assertAlmostEqual(row['driver_force'], reference['driver_force'], delta=.1)
                        self.assertAlmostEqual(row['guide_hip_reaction'], reference['guide_hip_reaction'], delta=.02)
                self.assertLess(errors[1], errors[0])
                self.assertLess(errors[2], errors[1])
                self.assertLess(errors[2], errors[0]/2)
                self.assertLess(errors[2], .035)
                reports[topology] = errors
        print('Preset final-angle errors (degrees), Pymunk 1 / .5 / .25 ms vs SciPy:', reports)

    def test_pullthrough_coil_compresses_with_identical_external_compliance(self):
        values = {'duration': 1.2, 'position_amplitude': .008, 'dt': .0005}
        extension = simulate(dict(values, spring_topology='knee_pulley'))
        pullrod = simulate(dict(values, spring_topology='knee_capture'))
        rope = simulate(dict(values, spring_topology='knee_capture', spring_transmission='ideal_rope'))
        captured = simulate(dict(values, spring_topology='knee_capture', spring_mode='captured'))
        for result in (pullrod, rope, captured):
            for key in ('theta_deg', 'driver_force', 'j2_force', 'guide_hip_reaction'):
                self.assertAlmostEqual(result['rows'][-1][key], extension['rows'][-1][key], places=8)
        e0, e1 = extension['rows'][0], extension['rows'][-1]
        p0, p1 = pullrod['rows'][0], pullrod['rows'][-1]
        self.assertAlmostEqual(p1['spring_coil_length']-p0['spring_coil_length'],
                               -(e1['spring_coil_length']-e0['spring_coil_length']), places=10)
        for row in rope['rows']:
            self.assertGreaterEqual(row['spring_tension'], 0.)
            self.assertEqual(row['spring_slack'], 0.)

    def test_disengaged_one_sided_coil_transmits_no_damper_or_force(self):
        for values in ({'spring_topology': 'direct_scissor', 'rest_length': .1},
                       {'spring_topology': 'legacy_tip', 'spring_mode': 'extension', 'rest_length': .4},
                       {'spring_topology': 'knee_capture', 'spring_transmission': 'ideal_rope', 'rest_length': .1}):
            with self.subTest(values=values):
                c = config(dict(values, balance_spring=False, gravity=0., damping=500.))
                model = build(c)
                model['upper'].angular_velocity = -.3
                model['lower'].angular_velocity = .3
                suspension.update(model, c)
                self.assertTrue(model['spring_state']['slack'])
                self.assertEqual(model['spring_state']['tension'], 0.)
                self.assertEqual(model['spring_state']['dissipation_rate'], 0.)
                self.assertEqual(model['spring_state']['energy'], 0.)
                self.assertTrue(all(force.length == 0. for force in model['spring_loads'].values()))

    def test_manual_force_energy_converges_without_external_work(self):
        # With fixed wheel height, zero gravity/damping and no actuator, the
        # imposed support performs no work. Use actual body energy rather than
        # inverse joint balances; explicit spring integration should converge.
        values = {'spring_topology': 'knee_bellcrank', 'gravity': 0., 'damping': 0.,
                  'balance_spring': False, 'position_amplitude': 0., 'duration': .5}
        initial = config(values)
        span = geometry(math.radians(initial['theta']), initial)['input_length']
        errors = []
        for dt in (.001, .0005, .00025):
            c = config(dict(values, rest_length=span-.01, dt=dt))
            model = build(c)
            start = mechanical_energy(model, c)
            maximum = 0.
            for i in range(round(c['duration']/dt)):
                drive(model, c, i*dt, dt)
                model['space'].step(dt)
                maximum = max(maximum, abs(mechanical_energy(model, c)-start))
                self.assertLess(model['stop'].impulse, 1e-10)
            errors.append(maximum)
        print('Actual Pymunk conservative-energy errors (J), 1 / .5 / .25 ms:', errors)
        self.assertLess(errors[1], errors[0]*.55)
        self.assertLess(errors[2], errors[1]*.55)
        self.assertLess(errors[2], .0015)

    def test_hip_demo_passive_instability_is_not_hidden_by_a_hold_motor(self):
        values = {'spring_topology': 'hip_pulley', 'duration': 2., 'position_amplitude': .002}
        c = math_config(values)
        p = parameters(c)
        eps = 1e-6
        slope = (derivative(0., (p['q0']+eps, 0.), c, p)[1]
                 - derivative(0., (p['q0']-eps, 0.), c, p)[1])/(2*eps)
        self.assertGreater(slope, 10.)
        reference = simulate_math(values)['rows'][-1]
        coarse = simulate(dict(values, dt=.001))
        fine = simulate(dict(values, dt=.00025))
        self.assertLess(reference['theta_deg'], 30.)
        self.assertLess(fine['rows'][-1]['theta_deg'], 30.)
        self.assertEqual(fine['diagnostics']['stop_steps'], 0)
        self.assertTrue(all(row['actuator_torque'] == 0. for row in fine['rows']))
        self.assertLess(abs(fine['rows'][-1]['theta_deg']-reference['theta_deg']),
                        abs(coarse['rows'][-1]['theta_deg']-reference['theta_deg'])/2)

    def test_incompatible_automatic_preload_rejects_instead_of_hiding_slack(self):
        for values in ({'spring_topology': 'hip_pulley', 'spring_direction': -1.},
                       {'spring_topology': 'direct_scissor', 'spring_mode': 'extension'},
                       {'spring_topology': 'knee_capture', 'spring_direction': -1., 'spring_transmission': 'ideal_rope'}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                build(config(values))

    def test_dead_center_can_be_studied_with_explicit_manual_preload(self):
        values={'spring_topology':'hip_bellcrank','spring_chassis_x':0.,'spring_chassis_y':0.,'rest_length':.05}
        with self.assertRaises(ValueError):build(config(values))
        model=build(config(dict(values,balance_spring=False)))
        self.assertAlmostEqual(model['rest'],.05)
        self.assertEqual(len(model['space'].shapes),3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
