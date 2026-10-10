"""Verify passive gravity support plus an independent original-tip ride strut.

Run: .venv/Scripts/python.exe -m unittest -v test_suspension_architecture.
Inputs: declared SI demo masses, spring rates/damping and smooth wheel heights.
Outputs: equilibrium, restoring-force, real point-force, energy and refinement
assertions for independent SciPy/Pymunk models. Requires SciPy and Pymunk.
Limitations: ideal bilateral wheel fixture and captured spring; no tire contact,
coil packaging/solid height, structural stress, hardware or canonical validation.
"""
import json
import math
import unittest

from pymunk import Vec2d
from scipy.integrate import solve_ivp

from math_model import config as math_config, derivative, observe, parameters, simulate_math
from physics import build, config, drive, simulate
from spring_mechanisms import (CATALOG, auxiliary_metadata, equal_poses,
                               force_pair_power, generalized, geometry_from_bodies,
                               spring_law)
import suspension_runtime as suspension


ARCHITECTURE = {'spring_topology': 'gravity_balance', 'damping': 0.,
                'aux_spring_enabled': True}
BODY_KEYS = ('hip', 'upper', 'lower')


def mechanical_energy(model, c):
    """Actual body energy plus both coils sampled from current real anchor sites."""
    energy = sum(.5*model[key].mass*model[key].velocity.length_squared
                 + (.5*model[key].moment*model[key].angular_velocity**2
                    if math.isfinite(model[key].moment) else 0.)
                 + model[key].mass*c['gravity']*model[key].position.y
                 for key in (*BODY_KEYS, 'wheel'))
    bodies = {key: model[key] for key in BODY_KEYS}
    stages = [(dict(c, rest_length=model['rest']), model['spring_input_reference'])]
    if model['auxiliary']['enabled']:
        stages.append((model['auxiliary']['config'], model['auxiliary']['input_ref']))
    for stage, reference in stages:
        geom = geometry_from_bodies(bodies, stage)
        energy += spring_law(geom['input_length'], geom['input_speed'], stage, reference)['energy']
    return energy


class SuspensionArchitectureTests(unittest.TestCase):
    def test_auto_rest_has_zero_ride_elastic_load_and_static_gravity_support(self):
        c = math_config(ARCHITECTURE)
        p = parameters(c)
        self.assertAlmostEqual(derivative(0., (p['q0'], 0.), c, p)[1], 0., places=12)
        row, _ = observe(0., p['q0'], 0., c, p)
        self.assertAlmostEqual(row['aux_spring_elastic_tension'], 0., places=12)
        self.assertAlmostEqual(row['aux_spring_energy_J'], 0., places=12)
        self.assertAlmostEqual(row['actuator_torque'], 0., places=12)
        result = simulate(dict(ARCHITECTURE, duration=.3))
        self.assertFalse(result['auxiliary_spring']['active_control'])
        self.assertTrue(result['auxiliary_spring']['automatic_rest'])
        self.assertAlmostEqual(result['auxiliary_spring']['initial_elastic_tension_N'], 0.)
        expected = sum(c[key] for key in ('chassis_mass', 'upper_mass', 'lower_mass', 'wheel_mass'))*c['gravity']
        for sample in result['rows']:
            self.assertAlmostEqual(sample['theta_deg'], c['theta'], delta=.006)
            self.assertAlmostEqual(sample['driver_force'], expected, delta=.5)
            self.assertEqual(sample['actuator_torque'], 0.)
        model = build(config(ARCHITECTURE))
        self.assertEqual(len(model['space'].shapes), 4)
        self.assertEqual(len(model['space'].constraints), 6)
        self.assertIsNone(model['spring'])
        self.assertEqual(model['hip'].mass, c['chassis_mass'])
        self.assertTrue(math.isinf(model['hip'].moment))
        self.assertEqual(model['shapes']['chassis'].mass, 0.)
        self.assertTrue(model['shapes']['chassis'].sensor)

    def test_captured_ride_stage_restores_both_sides_and_damping_is_passive(self):
        c = math_config(ARCHITECTURE)
        p = parameters(c)
        aux = p['auxiliary']
        for offset in (-10., -1., 1., 10.):
            q = p['q0']+math.radians(offset)
            rest = generalized(q, 0., aux['config'], aux['input_ref'])
            self.assertLess(rest['generalized_elastic_force']*offset, 0.)
            for speed in (-.4, .3):
                result = generalized(q, speed, aux['config'], aux['input_ref'])
                law, geom = result['law'], result['geometry']
                self.assertGreaterEqual(law['dissipation_rate'], 0.)
                self.assertAlmostEqual(law['dissipation_rate'], c['aux_damping']*(geom['jacobian']*speed)**2)
                bodies = equal_poses(q, c, theta_speed=speed, base_speed=.2)
                actual = geometry_from_bodies(bodies, aux['config'])
                self.assertAlmostEqual(force_pair_power(actual['force_sites'], bodies, law['tension']),
                                       result['generalized_force']*speed, places=10)

    def test_both_actual_force_pairs_and_com_torques_reach_the_solver(self):
        c = config(ARCHITECTURE)
        model = build(c)
        poses = equal_poses(math.radians(c['theta']), c, theta_speed=.37)
        for key, pose in poses.items():
            model[key].velocity = pose['velocity']
            model[key].angular_velocity = pose['angular_velocity']
        suspension.update(model, c)
        self.assertLess(sum(model['spring_loads'].values(), Vec2d(0., 0.)).length, 1e-10)
        # COM moments plus COM force arms must close about any world origin.
        world_moment = 0.
        for key in BODY_KEYS:
            expected = model['primary_spring_loads'][key]+model['auxiliary_loads'][key]
            moment = model['primary_spring_torques'][key]+model['auxiliary_torques'][key]
            self.assertLess((model[key].force-expected).length, 1e-10)
            self.assertAlmostEqual(model[key].torque, moment, places=10)
            world_moment += model['spring_torques'][key]+model[key].position.cross(model['spring_loads'][key])
        self.assertAlmostEqual(world_moment, 0., places=10)
        self.assertGreater(abs(model['auxiliary_state']['damper_tension']), 0.)
        self.assertEqual(model['spring_state']['damper_tension'], 0.)

    def test_manual_preload_is_declared_and_primary_rate_is_not_retuned(self):
        automatic = math_config(ARCHITECTURE)
        pa = parameters(automatic)
        manual = math_config(dict(ARCHITECTURE, aux_auto_rest=False, aux_rest_length=.25))
        pm = parameters(manual)
        self.assertEqual(automatic['stiffness'], manual['stiffness'])
        self.assertEqual(pm['auxiliary']['rest'], .25)
        self.assertNotEqual(derivative(0., (pm['q0'], 0.), manual, pm)[1], 0.)
        metadata = auxiliary_metadata(manual, pm['auxiliary'])
        self.assertGreater(metadata['initial_elastic_tension_N'], 0.)
        self.assertTrue(any('not silently retuned' in note for note in metadata['notes']))
        self.assertFalse(auxiliary_metadata(automatic, pa['auxiliary'])['notes'])

    def test_unilateral_ride_modes_and_invalid_configuration_are_explicit(self):
        for mode in ('extension', 'compression'):
            c = math_config(dict(ARCHITECTURE, aux_mode=mode))
            p = parameters(c)
            aux = p['auxiliary']
            forces = [generalized(p['q0']+math.radians(offset), 0., aux['config'], aux['input_ref'])['law']['elastic_tension']
                      for offset in (-5., 5.)]
            self.assertEqual(sum(abs(force) > 1e-9 for force in forces), 1)
            self.assertTrue(auxiliary_metadata(c, aux)['notes'])
        for edits in ({'spring_topology': 'legacy_tip'}, {'aux_stiffness': -1.},
                      {'aux_damping': float('nan')}, {'aux_spring_enabled': 'yes'},
                      {'aux_auto_rest': 1}, {'aux_mode': 'unknown'}, {'aux_rest_length': 0.}):
            for normalize in (config, math_config):
                with self.subTest(edits=edits, normalize=normalize), self.assertRaises(ValueError):
                    normalize(dict(ARCHITECTURE, **edits))

    def test_disabled_stage_preserves_each_preset_trajectory_exactly(self):
        for topology in CATALOG:
            values = {'spring_topology': topology, 'duration': .12}
            for backend in (simulate, simulate_math):
                with self.subTest(topology=topology, backend=backend):
                    default = backend(values)
                    disabled = backend(dict(values, aux_spring_enabled=False))
                    self.assertEqual(default['rows'], disabled['rows'])
                    self.assertEqual(default['frames'], disabled['frames'])
                    self.assertFalse(default['auxiliary_spring']['enabled'])
                    self.assertTrue(all(row['aux_spring_tension'] == 0. for row in default['rows']))

    def test_undamped_two_stage_body_energy_converges_with_step_refinement(self):
        values = dict(ARCHITECTURE, aux_damping=0., position_amplitude=0., duration=1.)
        c = math_config(values)
        p = parameters(c)
        reference = solve_ivp(lambda t, y: derivative(t, y, c, p), (0., 1.), (p['q0'], .2),
                              rtol=1e-11, atol=1e-13, max_step=.002)
        self.assertTrue(reference.success)
        energies = [observe(t, q, speed, c, p)[0]['mechanical_energy_J']
                    for t, q, speed in zip(reference.t, *reference.y)]
        self.assertLess(max(energies)-min(energies), 1e-8)
        errors, angle_errors = [], []
        for dt in (.001, .0005, .00025):
            physical_c = config(dict(values, dt=dt))
            model = build(physical_c)
            for key, pose in equal_poses(p['q0'], physical_c, theta_speed=.2).items():
                model[key].velocity = pose['velocity']
                model[key].angular_velocity = pose['angular_velocity']
            if physical_c['wheel_drive_locked']:
                model['wheel'].angular_velocity = .2
            initial_energy = mechanical_energy(model, physical_c)
            for index in range(round(1./dt)):
                drive(model, physical_c, index*dt, dt)
                model['space'].step(dt)
            errors.append(abs(mechanical_energy(model, physical_c)-initial_energy))
            angle_errors.append(abs(-model['upper'].angle-reference.y[0, -1]))
        print('Two-stage free oscillation energy errors (J), 1/.5/.25 ms:', errors)
        self.assertLess(errors[1], errors[0]*.6)
        self.assertLess(errors[2], errors[1]*.6)
        self.assertLess(errors[2], .001)
        self.assertLess(angle_errors[2], angle_errors[0]/2)

    def test_floating_step_loads_converge_and_full_energy_ledger_closes(self):
        values = dict(ARCHITECTURE, duration=1.2, position_amplitude=.008)
        reference = simulate_math(values)
        self.assertLess(abs(reference['diagnostics']['energy_balance_error_J']), 1e-7)
        self.assertTrue(all(row['aux_spring_dissipation_W'] >= 0. for row in reference['rows']))
        self.assertGreater(max(row['aux_spring_energy_J'] for row in reference['rows']), 0.)
        errors = []
        for dt in (.001, .0005, .00025):
            result = simulate(dict(values, dt=dt))
            errors.append(abs(result['rows'][-1]['theta_deg']-reference['rows'][-1]['theta_deg']))
            self.assertEqual(result['config']['stiffness'], reference['config']['stiffness'])
            self.assertEqual(result['diagnostics']['stop_steps'], 0)
            self.assertLess(result['diagnostics']['max_force_check_N'], 1e-7)
            self.assertLess(result['diagnostics']['max_torque_check_Nm'], 1e-7)
            self.assertTrue(all(error < 1e-7 for error in result['equation_check_errors'].values()))
            for row in result['rows']:
                self.assertAlmostEqual(row['total_spring_energy_J'], row['spring_energy_J']+row['aux_spring_energy_J'])
                for body in BODY_KEYS:
                    for axis in ('fx', 'fy'):
                        self.assertAlmostEqual(row[f'spring_{body}_{axis}'],
                                               row[f'primary_spring_{body}_{axis}']+row[f'aux_spring_{body}_{axis}'])
            self.assertIn('auxiliary_spring_geometry', result['frames'][0])
            self.assertGreater(result['frames'][0]['auxiliary_spring_coil_length'], 0.)
            if dt == .00025:
                for key, tolerance in (('j2_force', .1), ('driver_force', .05),
                                       ('guide_hip_reaction', .01), ('aux_spring_tension', .1)):
                    self.assertAlmostEqual(result['rows'][-1][key], reference['rows'][-1][key], delta=tolerance)
            json.dumps(result, allow_nan=False)
        print('Two-stage final-angle errors (degrees), Pymunk 1/.5/.25 ms vs SciPy:', errors)
        self.assertLess(errors[1], errors[0]*.6)
        self.assertLess(errors[2], errors[1]*.6)
        self.assertLess(errors[2], .003)


if __name__ == '__main__':
    unittest.main(verbosity=2)
