"""Check analytic guide-belt geometry, no-slip marks and force interpretation.

Run: python -m unittest -v test_guide_belt from the app root.
Inputs: illustrative SI centres/radii, radians, torque and optional pretension.
Outputs: exact tangency/closure/perimeter, material-motion and force/power checks.
Standard library only. Tests certify this massless geometric annotation, not an
engine belt/contact/bearing implementation or hardware tension calibration.
"""
import json
import math
import random
import subprocess
import sys
import unittest

from guide_belt import (build_loop, material_dots, material_phase, point_at,
                        station_at, tension_state)


def sub(a, b):
    return [a[0]-b[0], a[1]-b[1]]


def dot(a, b):
    return a[0]*b[0]+a[1]*b[1]


def cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def add(a, b):
    return [a[0]+b[0], a[1]+b[1]]


def spin(a, speed):
    return [-a[1]*speed, a[0]*speed]


class GuideBeltTests(unittest.TestCase):
    def assertPointEqual(self, actual, expected, tolerance=1e-12):
        self.assertLess(math.hypot(*sub(actual, expected)), tolerance)

    def test_module_is_standard_library_only_and_has_no_engine_side_effects(self):
        code = "import sys; import guide_belt; assert 'pymunk' not in sys.modules; assert 'physics' not in sys.modules; assert 'numpy' not in sys.modules; assert 'scipy' not in sys.modules"
        subprocess.run([sys.executable, '-c', code], check=True)

    def test_exact_common_tangents_at_both_radii(self):
        rng = random.Random(20261010)
        for _ in range(30):
            alpha, length = rng.uniform(-math.pi, math.pi), rng.uniform(.08, .8)
            A = [rng.uniform(-1., 1.), rng.uniform(-1., 1.)]
            B = add(A, [length*math.cos(alpha), length*math.sin(alpha)])
            loop = build_loop(A, B)
            for name in ('plus', 'minus'):
                hip = loop['tangencies']['hip_'+name]
                knee = loop['tangencies']['knee_'+name]
                span = sub(knee, hip)
                self.assertAlmostEqual(math.hypot(*sub(hip, A)), loop['hip_radius'], places=12)
                self.assertAlmostEqual(math.hypot(*sub(knee, B)), loop['knee_radius'], places=12)
                self.assertAlmostEqual(dot(sub(hip, A), span), 0., places=12)
                self.assertAlmostEqual(dot(sub(knee, B), span), 0., places=12)
                self.assertAlmostEqual(math.hypot(*span), loop['span_length'], places=12)

    def test_loop_closure_cw_arcs_and_exact_perimeter(self):
        loop = build_loop((.1, .7), (.3, .5))
        rH, rK, d = loop['hip_radius'], loop['knee_radius'], loop['centre_distance']
        expected = 2*math.sqrt(d*d-(rH-rK)**2)+math.pi*(rH+rK)+2*(rH-rK)*math.asin((rH-rK)/d)
        self.assertAlmostEqual(loop['length'], expected, places=14)
        self.assertEqual(loop['direction'], 'clockwise')
        for segment in loop['segments']:
            self.assertPointEqual(point_at(loop, segment['start']), segment['a'])
            self.assertPointEqual(point_at(loop, segment['start']+segment['length']), segment['b'])
            if segment['kind'] == 'arc':
                self.assertLess(segment['sweep'], 0.)
                middle = station_at(loop, segment['start']+segment['length']/2)
                radius = sub(middle['point'], segment['centre'])
                self.assertAlmostEqual(math.hypot(*radius), segment['radius'], places=13)
                self.assertLess(cross(radius, middle['tangent']), 0.)
        self.assertPointEqual(loop['points'][0], loop['points'][-1])
        self.assertPointEqual(point_at(loop, 0.), point_at(loop, 3*loop['length']))
        self.assertPointEqual(point_at(loop, -.02), point_at(loop, loop['length']-.02))

    def test_station_derivative_is_unit_speed_and_tangent_is_continuous(self):
        loop = build_loop((0., 0.), (.273, 0.))
        eps = 1e-7
        for segment in loop['segments']:
            s = segment['start']+.43*segment['length']
            station = station_at(loop, s)
            a, b = point_at(loop, s-eps), point_at(loop, s+eps)
            derivative = [(b[j]-a[j])/(2*eps) for j in (0, 1)]
            self.assertPointEqual(derivative, station['tangent'], tolerance=1e-8)
            before = station_at(loop, segment['start']-1e-10)['tangent']
            after = station_at(loop, segment['start']+1e-10)['tangent']
            self.assertPointEqual(before, after, tolerance=2e-8)

    def test_no_slip_material_marks_follow_fixed_hip_and_rotating_knee(self):
        A, distance, initial = [.11, .74], .273, -.6
        base = build_loop(A, add(A, [distance*math.cos(initial), distance*math.sin(initial)]))
        hip_segment, knee_segment = base['segments'][3], base['segments'][1]
        h_s = hip_segment['start']+.5*hip_segment['length']
        k_s = knee_segment['start']+.5*knee_segment['length']
        h0 = sub(point_at(base, h_s), A)
        k0 = sub(point_at(base, k_s), base['knee'])
        for delta in (-.12, -.06, .04, .1):
            alpha = initial+delta
            current = build_loop(A, add(A, [distance*math.cos(alpha), distance*math.sin(alpha)]))
            phase = material_phase(alpha, initial)
            hip_mark = sub(point_at(current, h_s+phase), A)
            knee_mark = sub(point_at(current, k_s+phase), current['knee'])
            self.assertPointEqual(hip_mark, h0)
            # Lower-link absolute angle changes by -delta(alpha), even though
            # its rotation relative to the upper carrier changes by -2delta.
            expected_knee = [k0[0]*math.cos(-delta)-k0[1]*math.sin(-delta),
                             k0[0]*math.sin(-delta)+k0[1]*math.cos(-delta)]
            self.assertPointEqual(knee_mark, expected_knee)

    def test_material_phase_is_unwrapped_pose_not_time_and_marks_are_arc_spaced(self):
        loop = build_loop((0., 0.), (.273, 0.))
        phase = material_phase(-7., -.5)
        self.assertAlmostEqual(phase, .028*(-6.5), places=14)
        dots = material_dots(loop, phase, 24)
        for index, point in enumerate(dots):
            self.assertPointEqual(point, point_at(loop, phase+index*loop['length']/24))
        self.assertNotEqual(dots, material_dots(loop, phase+.001, 24))

    def test_signed_tension_difference_and_exact_two_to_one_torques(self):
        for torque in (-1.5, 0., 1.5):
            loop = build_loop((.12, .65), (.31, .43))
            result = tension_state(loop, torque, 25.)
            self.assertAlmostEqual(result['tension_plus_N']-result['tension_minus_N'], torque/.014, places=12)
            self.assertGreaterEqual(result['tension_plus_N'], 25.)
            self.assertGreaterEqual(result['tension_minus_N'], 25.)
            self.assertAlmostEqual(result['knee_torque_Nm'], torque, places=12)
            self.assertAlmostEqual(result['hip_torque_Nm'], -2*torque, places=12)
            self.assertAlmostEqual(result['carrier_torque_Nm'], torque, places=12)
            self.assertTrue(result['pretension_known'])
            self.assertFalse(result['engine_bearing_loads_included'])

    def test_all_span_forces_close_world_force_and_moment_balance(self):
        for angle in (-1.2, -.3, .7):
            A = [.2, .7]
            B = add(A, [.273*math.cos(angle), .273*math.sin(angle)])
            loop = build_loop(A, B)
            for torque in (-2., 0., 2.):
                for base in (None, 0., 100.):
                    result = tension_state(loop, torque, base)
                    arrows = result['force_arrows']
                    total_force = [sum(arrow['force_N'][axis] for arrow in arrows) for axis in (0, 1)]
                    total_moment = sum(cross(arrow['point'], arrow['force_N']) for arrow in arrows)
                    self.assertPointEqual(total_force, (0., 0.))
                    self.assertAlmostEqual(total_moment, 0., places=11)

    def test_no_slip_force_ledger_conserves_virtual_power(self):
        loop = build_loop((.13, .71), (.36, .57))
        hip_spin, carrier_spin = .13, .29
        knee_spin = 2*hip_spin-carrier_spin
        hip_velocity = [.3, -.2]
        knee_velocity = add(hip_velocity, spin(sub(loop['knee'], loop['hip']), carrier_spin))
        for pretension in (None, 0., 50.):
            state = tension_state(loop, 1.7, pretension)
            power = 0.
            for arrow in state['force_arrows']:
                centre = loop[arrow['body']]
                velocity = add(hip_velocity if arrow['body'] == 'hip' else knee_velocity,
                               spin(sub(arrow['point'], centre), hip_spin if arrow['body'] == 'hip' else knee_spin))
                power += dot(arrow['force_N'], velocity)
            self.assertAlmostEqual(power, 0., places=12)
            self.assertAlmostEqual(state['hip_torque_Nm']*hip_spin+state['knee_torque_Nm']*knee_spin
                                   +state['carrier_torque_Nm']*carrier_spin, 0., places=12)

    def test_unknown_pretension_never_becomes_actual_span_or_bearing_load(self):
        loop = build_loop((0., 0.), (.273, 0.))
        unknown = tension_state(loop, 1.4)
        known = tension_state(loop, 1.4, 60.)
        self.assertFalse(unknown['pretension_known'])
        for key in ('pretension_N', 'tension_plus_N', 'tension_minus_N', 'hip_resultant_N', 'knee_resultant_N'):
            self.assertIsNone(unknown[key])
        self.assertTrue(all(arrow['torque_equivalent'] for arrow in unknown['force_arrows']))
        self.assertFalse(any(arrow['torque_equivalent'] for arrow in known['force_arrows']))
        self.assertAlmostEqual(unknown['differential_N'], known['differential_N'], places=12)
        self.assertAlmostEqual(unknown['knee_torque_Nm'], known['knee_torque_Nm'], places=12)
        self.assertNotEqual(unknown['torque_equivalent_hip_resultant_N'], known['hip_resultant_N'])
        self.assertIn('unknown', unknown['legend'].lower())
        json.dumps(unknown, allow_nan=False)
        json.dumps(loop, allow_nan=False)

    def test_invalid_geometry_phase_and_tension_inputs_fail_explicitly(self):
        for args in (((0., 0.), (0., 0.)), ((0., 0.), (.04, 0.)),
                     ((0., 0.), (.273, 0.), -.028), ((0., 0.), (.273, 0.), .028, .01),
                     ((0., 0.), (float('nan'), 0.)), ((0.,), (.273, 0.))):
            with self.subTest(args=args), self.assertRaises(ValueError):
                build_loop(*args)
        loop = build_loop((0., 0.), (.273, 0.))
        for pretension in (-1., float('nan'), True):
            with self.subTest(pretension=pretension), self.assertRaises(ValueError):
                tension_state(loop, 1., pretension)
        for torque in (float('inf'), True):
            with self.assertRaises(ValueError):
                tension_state(loop, torque)
        for count in (0, 1, True, 2.5):
            with self.assertRaises(ValueError):
                material_dots(loop, 0., count)
        with self.assertRaises(ValueError):
            material_phase(float('nan'), 0.)
        with self.assertRaises(ValueError):
            point_at(loop, float('inf'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
