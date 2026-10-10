"""Verify preset geometry, physical virtual work and passive spring routing.

Run: python -m unittest -v test_spring_mechanisms from the app root.
Inputs: explicit demo SI dimensions, angles/speeds and coil law combinations.
Outputs: assertions only; standard library, no files or rigid-body imports.
Limitations: tests ideal geometry/energy, not real cable/bearing/coil hardware.
"""
import math
import unittest
from types import SimpleNamespace

from spring_mechanisms import (CATALOG, MECHANISM_DEFAULTS, apply_preset,
                               direct_anchors, equal_poses, force_pair_power,
                               generalized, geometry, geometry_from_bodies,
                               spring_law)


BASE = {'length': .273, 'extension': .05, 'theta': 45., 'stiffness': 8000.,
        'damping': 100., 'rest_length': .20}


class SpringMechanismTests(unittest.TestCase):
    def test_catalog_presets_are_distinct_and_explicit_demos(self):
        self.assertEqual(set(CATALOG), {'legacy_tip', 'hip_pulley', 'knee_pulley',
                                       'direct_scissor', 'hip_bellcrank',
                                       'knee_bellcrank', 'chassis_direct', 'knee_capture', 'gravity_balance'})
        for name in CATALOG:
            c = apply_preset(BASE, name)
            self.assertEqual(c['spring_topology'], name)
            self.assertIn('not confirmed hardware', CATALOG[name]['status'])
        self.assertNotIn('spring_topology', BASE)
        captured = apply_preset(BASE, 'knee_capture')
        self.assertEqual(captured['spring_mode'], 'compression')
        self.assertEqual(captured['spring_transmission'], 'pullrod')
        self.assertEqual(apply_preset(BASE, 'knee_bellcrank')['spring_bellcrank_offset_deg'], 180.)

    def test_every_jacobian_matches_finite_difference(self):
        eps = 1e-6
        for name in CATALOG:
            for sign in (-1., 1.):
                c = {**apply_preset(BASE, name), 'spring_direction': sign}
                for degrees in (20., 37., 55., 75.):
                    q = math.radians(degrees)
                    with self.subTest(name=name, sign=sign, angle=degrees):
                        g = geometry(q, c)
                        fd = (geometry(q+eps, c)['input_length']-geometry(q-eps, c)['input_length'])/(2*eps)
                        self.assertAlmostEqual(g['jacobian'], fd, delta=1e-8)

    def test_direct_local_anchors_transform_on_actual_body_poses(self):
        c = apply_preset(BASE, 'legacy_tip')
        q = math.radians(42.)
        poses = equal_poses(q, c, theta_speed=.3, base_height=.12, base_speed=-.4)
        bodies = {key: SimpleNamespace(**value) for key, value in poses.items()}
        g = geometry_from_bodies(bodies, c)
        expected = math.sqrt(c['length']**2+c['extension']**2+2*c['length']*c['extension']*math.cos(2*q))
        self.assertAlmostEqual(g['input_length'], expected, places=12)
        self.assertAlmostEqual(g['input_speed'], g['jacobian']*.3, places=12)
        anchor = direct_anchors(c)['b']
        self.assertEqual(anchor['body'], 'lower')
        self.assertEqual(anchor['local'], [-(c['length']+c['extension'])/2, 0.])
        # Actual direct geometry follows supplied body drift rather than
        # silently replacing the coordinates with ideal equal-link poses.
        shifted = {key: dict(value) for key, value in poses.items()}
        shifted['lower']['position'] = [poses['lower']['position'][0]+.02, poses['lower']['position'][1]]
        self.assertGreater(abs(geometry_from_bodies(shifted, c)['input_length']-expected), .005)

    def test_every_force_pair_matches_virtual_work(self):
        for name in CATALOG:
            for sign in (-1., 1.):
                c = {**apply_preset(BASE, name), 'spring_direction': sign}
                for degrees, speed in ((25., .7), (45., -.3), (72., .4)):
                    q = math.radians(degrees)
                    bodies = equal_poses(q, c, theta_speed=speed, base_speed=.42)
                    g = geometry_from_bodies(bodies, c)
                    for tension in (123., -40.):
                        with self.subTest(name=name, sign=sign, angle=degrees, tension=tension):
                            power = force_pair_power(g['force_sites'], bodies, tension)
                            self.assertAlmostEqual(power, -tension*g['jacobian']*speed, places=10)
                            self.assertAlmostEqual(g['input_speed'], g['jacobian']*speed, places=11)
                    fx = sum(site['direction'][0] for site in g['force_sites'])
                    fy = sum(site['direction'][1] for site in g['force_sites'])
                    self.assertAlmostEqual(fx, 0., places=12)
                    self.assertAlmostEqual(fy, 0., places=12)

    def test_pulley_payout_and_force_moments_have_correct_ratios(self):
        q, qref = math.radians(55.), math.radians(BASE['theta'])
        for name, ratio in (('hip_pulley', 1), ('knee_pulley', 2), ('knee_capture', 2)):
            c = apply_preset(BASE, name)
            r = c['spring_pulley_radius']
            g = geometry(q, c)
            self.assertAlmostEqual(g['input_length'], c['spring_input_ref']-ratio*r*(q-qref))
            self.assertAlmostEqual(g['jacobian'], -ratio*r)
            sites = g['force_sites']
            self.assertEqual(sites[0]['body'], 'upper' if ratio == 1 else 'lower')
            # Moment about the physical joint from the actual tangent force.
            A = [0., 2*c['length']*math.sin(q)]
            B = [c['length']*math.cos(q), c['length']*math.sin(q)]
            center = A if ratio == 1 else B
            offset = [sites[0]['world'][j]-center[j] for j in (0, 1)]
            force = sites[0]['direction']
            moment = offset[0]*force[1]-offset[1]*force[0]
            self.assertAlmostEqual(moment, -r if ratio == 1 else r, places=12)

    def test_force_is_energy_derivative_in_every_law_and_routing(self):
        eps = 1e-7
        for mode in ('compression', 'extension', 'captured'):
            for route in ('direct', 'pullrod', 'ideal_rope'):
                c = {**BASE, **MECHANISM_DEFAULTS, 'spring_mode': mode,
                     'spring_transmission': route, 'spring_input_ref': .20,
                     'spring_coil_ref': .20}
                for length in (.17, .23):
                    with self.subTest(mode=mode, route=route, length=length):
                        law = spring_law(length, 0., c, input_reference=.20)
                        ep = spring_law(length+eps, 0., c, input_reference=.20)['energy']
                        em = spring_law(length-eps, 0., c, input_reference=.20)['energy']
                        self.assertAlmostEqual((ep-em)/(2*eps), law['denergy_dinput'], delta=2e-6)
                        self.assertAlmostEqual(law['tension'], law['denergy_dinput'], places=10)

    def test_increasing_pullrod_input_compresses_coil_and_creates_tension(self):
        c = {**apply_preset(BASE, 'knee_capture'), 'damping': 0.}
        a = spring_law(.20, 0., c, input_reference=.20)
        b = spring_law(.23, 0., c, input_reference=.20)
        self.assertAlmostEqual(a['coil_length'], .20)
        self.assertAlmostEqual(b['coil_length'], .17)
        self.assertAlmostEqual(b['coil_tension'], -240.)
        self.assertAlmostEqual(b['tension'], 240.)
        self.assertAlmostEqual(b['energy'], .5*8000*.03**2)
        self.assertGreater(b['tension'], a['tension'])

    def test_slack_one_sided_coils_do_not_create_damper_force(self):
        for mode, length in (('compression', .23), ('extension', .17)):
            c = {**BASE, **MECHANISM_DEFAULTS, 'spring_mode': mode}
            for velocity in (-10., 10.):
                law = spring_law(length, velocity, c)
                self.assertTrue(law['slack'])
                self.assertFalse(law['engaged'])
                self.assertEqual(law['tension'], 0.)
                self.assertEqual(law['energy'], 0.)
                self.assertEqual(law['damper_tension'], 0.)
                self.assertEqual(law['coil_length'], c['rest_length'])

    def test_one_sided_damping_and_rope_are_passive_and_never_push(self):
        for mode in ('compression', 'extension', 'captured'):
            for route in ('direct', 'pullrod', 'ideal_rope'):
                c = {**BASE, **MECHANISM_DEFAULTS, 'spring_mode': mode,
                     'spring_transmission': route}
                for length in (.17, .20, .23):
                    for velocity in (-20., -.1, 0., .1, 20.):
                        with self.subTest(mode=mode, route=route, length=length, velocity=velocity):
                            law = spring_law(length, velocity, c, input_reference=.20)
                            self.assertGreaterEqual(law['dissipation_rate'], -1e-10)
                            if route == 'ideal_rope':
                                self.assertGreaterEqual(law['tension'], 0.)
                                self.assertEqual(law['transmission_efficiency'], 1.)
                                self.assertEqual(law['rope_stretch'], 0.)

    def test_generalized_force_matches_energy_gradient(self):
        eps = 1e-6
        for name in CATALOG:
            c = apply_preset(BASE, name)
            for degrees in (35., 50., 70.):
                q = math.radians(degrees)
                result = generalized(q, 0., c)
                ep = generalized(q+eps, 0., c)['law']['energy']
                em = generalized(q-eps, 0., c)['law']['energy']
                with self.subTest(name=name, angle=degrees):
                    self.assertAlmostEqual(result['generalized_force'], -(ep-em)/(2*eps), delta=2e-6)

    def test_missing_velocities_are_not_silently_assumed_static(self):
        c = apply_preset(BASE, 'hip_pulley')
        bodies = equal_poses(math.radians(45.), c)
        for body in bodies.values():
            del body['velocity']
            del body['angular_velocity']
        g = geometry_from_bodies(bodies, c)
        self.assertIsNone(g['input_speed'])
        with self.assertRaises(ValueError):
            force_pair_power(g['force_sites'], bodies, 12.)

    def test_invalid_or_degenerate_geometry_fails_explicitly(self):
        for edits in ({'spring_topology': 'unknown'}, {'spring_direction': 0.},
                      {'spring_pulley_radius': 0.}, {'spring_upper_fraction': 2.},
                      {'spring_transmission': 'magic'}, {'spring_mode': 'magic'}):
            with self.subTest(edits=edits), self.assertRaises(ValueError):
                geometry(math.radians(45.), {**BASE, **MECHANISM_DEFAULTS, **edits})
        with self.assertRaises(ValueError):
            spring_law(.6, 0., {**apply_preset(BASE, 'knee_capture')}, input_reference=.20)
        with self.assertRaises(ValueError):
            direct_anchors(apply_preset(BASE, 'hip_pulley'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
