"""Verify the one-unit replacement spring/damper and visible ideal 2:1 guide.

Run: .venv/Scripts/python.exe -m unittest -v test_replacement_suspension.
Inputs: SI factory profile, actual Pymunk poses and independent SciPy states.
Outputs: force-site, neutral-support, sensor-body, unchanged dynamics, guide
ratio/tension metadata and impulse-closure assertions. Requires SciPy/Pymunk.
Limitations: sensors and ideal angular guide; no belt bearing force, pretension,
stretch, tire contact, coil packaging or hardware/canonical robot validation.
"""
import json
import math
import unittest

from pymunk import Vec2d

from math_model import config as math_config, derivative, parameters, simulate_math
from physics import build, config, drive, simulate
from spring_mechanisms import (CATALOG, equal_poses, force_pair_power, generalized,
                               geometry_from_bodies)
from suspension_architecture import constant_lift_profile


class ReplacementSuspensionTests(unittest.TestCase):
    def test_factory_replaces_tip_strut_with_one_upper_to_chassis_unit(self):
        c = constant_lift_profile()
        self.assertEqual(c['spring_topology'], 'gravity_balance')
        self.assertEqual(c['spring_force_law'], 'zero_effective')
        self.assertEqual(c['damping'], 100.)
        self.assertFalse(c['aux_spring_enabled'])
        self.assertEqual(c['knee_kp'], 0.)
        self.assertEqual(c['knee_kd'], 0.)
        m = build(c)
        self.assertFalse(m['auxiliary']['enabled'])
        self.assertIsNone(m['spring'])
        geom = geometry_from_bodies({key: m[key] for key in ('hip', 'upper', 'lower')}, c)
        self.assertEqual({site['body'] for site in geom['force_sites']}, {'hip', 'upper'})
        self.assertEqual(geom['anchors']['a']['body'], 'hip')
        self.assertEqual(geom['anchors']['b']['body'], 'upper')
        drive(m, c, 0., c['dt'])
        self.assertEqual(m['spring_loads']['lower'], Vec2d(0., 0.))
        self.assertNotIn('auxiliary_state', m)
        self.assertGreater(m['spring_state']['elastic_tension'], 0.)

    def test_single_unit_exactly_balances_gravity_without_ride_stiffness(self):
        c = math_config(constant_lift_profile())
        p = parameters(c)
        lifts = []
        for degrees in (16., 25., 45., 65., 79.):
            q = math.radians(degrees)
            spring = generalized(q, 0., p['spring_config'], p['input_ref'])
            self.assertAlmostEqual(derivative(0., (q, 0.), c, p)[1], 0., places=11)
            lifts.append(spring['generalized_elastic_force']/(2*c['length']*math.cos(q)))
            for speed in (-.4, .3):
                moving = generalized(q, speed, p['spring_config'], p['input_ref'])
                law = moving['law']
                self.assertGreater(law['dissipation_rate'], 0.)
                bodies = equal_poses(q, c, theta_speed=speed, base_speed=.2)
                geometry = geometry_from_bodies(bodies, c)
                self.assertAlmostEqual(force_pair_power(geometry['force_sites'], bodies, law['tension']),
                                       moving['generalized_force']*speed, places=10)
        self.assertLess(max(lifts)-min(lifts), 1e-10)

    def test_real_sensor_pulleys_have_correct_carrier_bodies_and_no_inertia(self):
        c = constant_lift_profile()
        m = build(c)
        bare = build(config(dict(c, chassis_shape_enabled=False, guide_pulleys_visible=False)))
        self.assertEqual(len(m['space'].shapes), 6)
        self.assertEqual(len(m['space'].constraints), 6)
        self.assertEqual(len(bare['space'].shapes), 3)
        self.assertIs(m['shapes']['chassis'].body, m['hip'])
        self.assertIs(m['shapes']['guide_hip_pulley'].body, m['hip'])
        self.assertIs(m['shapes']['guide_knee_pulley'].body, m['lower'])
        for key in ('hip', 'upper', 'lower', 'wheel'):
            self.assertEqual(m[key].mass, bare[key].mass)
            self.assertEqual(m[key].moment, bare[key].moment)
        for key in ('chassis', 'guide_hip_pulley', 'guide_knee_pulley'):
            self.assertEqual(m['shapes'][key].mass, 0.)
            self.assertTrue(m['shapes'][key].sensor)
        hp, kp = m['shapes']['guide_hip_pulley'], m['shapes']['guide_knee_pulley']
        self.assertEqual(hp.radius, 2*kp.radius)
        self.assertLess((m['hip'].local_to_world(hp.offset)-m['hip'].local_to_world(m['j1'].anchor_a)).length, 1e-12)
        self.assertLess((m['lower'].local_to_world(kp.offset)-m['lower'].local_to_world(m['j2'].anchor_b)).length, 1e-12)
        speed = .37
        for key, pose in equal_poses(math.radians(c['theta']), c, theta_speed=speed).items():
            m[key].velocity = pose['velocity']
            m[key].angular_velocity = pose['angular_velocity']
        hip_relative = m['hip'].angular_velocity-m['upper'].angular_velocity
        knee_relative = m['lower'].angular_velocity-m['upper'].angular_velocity
        self.assertAlmostEqual(knee_relative, 2*hip_relative)
        self.assertAlmostEqual(hp.radius*hip_relative, kp.radius*knee_relative)

    def test_visibility_sensors_preserve_dynamic_rows_and_all_legacy_defaults(self):
        for backend in (simulate, simulate_math):
            c = dict(constant_lift_profile(), duration=1.2, position_amplitude=.008)
            visible = backend(c)
            bare = backend(dict(c, chassis_shape_enabled=False, guide_pulleys_visible=False))
            self.assertEqual(visible['rows'], bare['rows'])
            self.assertIn('guide_pulleys', visible['frames'][0])
            self.assertNotIn('guide_pulleys', bare['frames'][0])
            self.assertTrue(all('auxiliary_spring_geometry' not in frame for frame in visible['frames']))
        for topology in CATALOG:
            resolved = config({'spring_topology': topology})
            self.assertFalse(resolved['chassis_shape_enabled'])
            self.assertFalse(resolved['guide_pulleys_visible'])
            self.assertEqual(len(build(resolved)['space'].shapes), 3)

    def test_frame_geometry_and_torque_implied_difference_close_without_belt_forces(self):
        c = dict(constant_lift_profile(), duration=1.2, position_amplitude=.008)
        for backend in (simulate, simulate_math):
            result = backend(c)
            self.assertLess(result['diagnostics']['max_force_check_N'], 1e-7)
            self.assertLess(result['diagnostics']['max_torque_check_Nm'], 1e-7)
            self.assertTrue(all(error < 1e-7 for error in result['equation_check_errors'].values()))
            for row in result['rows']:
                guide = row.get('guide_link_torque', -row['guide_hip_reaction']/2)
                self.assertAlmostEqual(row['guide_tension_difference_N'], guide/(c['guide_hip_radius']/2))
                self.assertAlmostEqual(row['guide_tension_difference_N'], -row['guide_hip_reaction']/c['guide_hip_radius'])
                self.assertAlmostEqual(row['guide_belt_speed_relative'], -c['guide_hip_radius']*row['upper_speed'])
                self.assertEqual(row['aux_spring_tension'], 0.)
                self.assertEqual(row['spring_lower_fx'], 0.)
                self.assertEqual(row['spring_lower_fy'], 0.)
            for frame in result['frames']:
                guide = frame['guide_pulleys']
                self.assertEqual(guide['ratio'], 2.)
                self.assertEqual(guide['hip']['body'], 'hip')
                self.assertEqual(guide['knee']['body'], 'lower')
                self.assertEqual(guide['carrier_angle'], frame['upper_angle'])
                self.assertEqual(guide['hip']['angle'], 0.)
                self.assertEqual(guide['knee']['angle'], frame['lower_angle'])
                self.assertEqual(guide['hip']['radius'], 2*guide['knee']['radius'])
                self.assertIn('not an applied belt force', guide['scope'])
                self.assertAlmostEqual(guide['hip']['center'][0], frame['hip'][0])
                self.assertAlmostEqual(guide['hip']['center'][1], frame['hip'][1])
                # Engine knee circle follows the lower pin site; its centre can
                # differ slightly from the upper pin as finite-step drift.
                self.assertLess(math.dist(guide['knee']['center'], frame['knee']), .0001)
            json.dumps(result, allow_nan=False)

    def test_new_visual_parameters_reject_nonphysical_or_nonboolean_values(self):
        for normalize in (config, math_config):
            for values in ({'guide_hip_radius': 0.}, {'guide_hip_radius': .2},
                           {'guide_hip_radius': float('nan')}, {'guide_hip_radius': True},
                           {'chassis_shape_enabled': 1}, {'guide_pulleys_visible': 'yes'}):
                with self.subTest(normalize=normalize, values=values), self.assertRaises(ValueError):
                    normalize(values)


if __name__ == '__main__':
    unittest.main(verbosity=2)
