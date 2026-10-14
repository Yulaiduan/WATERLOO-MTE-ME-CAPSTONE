"""Cross-check generalized V2 sizing against legacy math and actual Pymunk.

Invocation: python -m unittest -v test_generalized_leg in this app root.
Inputs: explicit experimental mm/degrees/kg/N and SI spring fixtures.
Outputs: unittest assertions covering geometry, passive work, motor scaling,
positive mass allocation and actual constraint-impulse timestep refinement.
Requires installed NumPy/SciPy/Pymunk. No hardware/contact/rolling certification;
original equal-link lower-extension distributed mass differs from V2 rods.
"""
import json
import math
import unittest

import numpy as np

import generalized_leg as g
import math_model as legacy_math
import spring_mechanisms as legacy_springs


def candidate(physical=True):
    c = g.config(dict(L2=180., L3=340., ra=106.5, rb=60., alpha=4.375,
                      tc=159.81088834775142))
    return g.physical_allocation(c) if physical else c


class GeneralizedLegTests(unittest.TestCase):
    def test_screenshot_fixed_a_and_m1_invariance(self):
        c = g.config(); q = math.radians(100.135)
        d = g.inverse_dynamics(q, 0., 0., c)
        self.assertAlmostEqual(d['tau_q_Nm'], -25.629659700646762, places=10)
        self.assertAlmostEqual(d['tau4_Nm'], -14.778491130835423, places=10)
        c2 = g.config(dict(m1=90.))
        self.assertEqual(d['tau_q_Nm'], g.inverse_dynamics(q, 0., 0., c2)['tau_q_Nm'])
        travel = g.interval(c)
        self.assertAlmostEqual(travel['total_capacity_mm'], 338.6159307494501, places=9)
        self.assertAlmostEqual(travel['lateral_travel_mm'], 101.157121828179, places=9)

    def test_all_absolute_rotor_slopes_against_v2_open_carriers(self):
        c = g.config(dict(L2=290., L3=235., ra=96., rb=60., rc=30., rd=35., re=36., rf=32., alpha=17., phi0=10.))
        q = math.radians(140.); e = 1e-6
        kin = g.kinematics(q, c)
        slopes = dict(hip=0., upper=1., lower=1-c['ra']/c['rb'], compound=1-c['rc']/c['rd'])
        # Wheel open belt carried by lower link: theta6'=h3+qef*(h5-h3).
        slopes['wheel'] = slopes['lower']+c['re']/c['rf']*(slopes['compound']-slopes['lower'])
        plus, minus = g.kinematics(q+e, c), g.kinematics(q-e, c)
        for key, expected in slopes.items():
            self.assertAlmostEqual(kin['angular_jacobian'][key], expected, places=12)
            self.assertAlmostEqual((plus['angles'][key]-minus['angles'][key])/(2*e), expected, places=8)
        self.assertAlmostEqual(g.kinematics(q, g.config())['angular_jacobian']['compound'], 0.)

    def test_finite_difference_body_geometry(self):
        c = g.config(dict(L2=290., L3=235., ra=96., rb=60., alpha=17., phi0=10.))
        q = 2.3; e = 1e-5
        for fixture in ('fixed_a', 'supported_chassis'):
            state = g.kinematics(q, c, fixture)
            plus, minus = g.kinematics(q+e, c, fixture), g.kinematics(q-e, c, fixture)
            for key in g.BODY_KEYS:
                np.testing.assert_allclose((plus['positions'][key]-minus['positions'][key])/(2*e), state['jacobians'][key], atol=1e-9)
                np.testing.assert_allclose((plus['jacobians'][key]-minus['jacobians'][key])/(2*e), state['curvature'][key], atol=1e-9)

    def test_all_nine_against_existing_andy_2d_geometry_law(self):
        c = g.config(dict(L2=273., L3=273., ra=28., rb=14., alpha=0., te=100.))
        for topology in g.CATALOG:
            s = g.resolved_spring(c, topology)
            legacy = {**legacy_math.DEFAULTS, **s, 'length': .273, 'extension': .05,
                      'theta': 180-c['te'], 'balance_spring': False, 'damping': 0.}
            for theta_deg in (20., 40., 60., 75.):
                theta = math.radians(theta_deg); q = math.pi-theta
                old = legacy_springs.geometry(theta, legacy)
                new = g.spring_geometry(q, c, s, 'supported_chassis')
                self.assertAlmostEqual(old['input_length'], new['input_length'], places=12, msg=topology)
                self.assertAlmostEqual(old['jacobian'], -new['jacobian'], places=12, msg=topology)
                for oldsite, newsite in zip(old['force_sites'], new['force_sites']):
                    self.assertEqual(oldsite['body'], newsite['body'])
                    np.testing.assert_allclose(oldsite['world'], newsite['world'], atol=1e-12)
                    np.testing.assert_allclose(oldsite['direction'], newsite['direction'], atol=1e-12)
                reference = legacy_springs.geometry(math.radians(legacy['theta']), legacy)['input_length']
                oldlaw = legacy_springs.spring_law(old['input_length'], old['jacobian']*.3, legacy, reference)
                newstate = g.spring_state(q, -.3, c, s, 'supported_chassis')
                self.assertAlmostEqual(oldlaw['energy'], newstate['law']['energy'], places=10)
                self.assertAlmostEqual(-oldlaw['tension']*old['jacobian'], -newstate['generalized_force'], places=10)

    def test_existing_andy_math_energy_terms_common_mass_fixture(self):
        # The V2 tibia is knee→hub; old Andy tibia includes extension in its
        # distributed mass. Set lower mass zero to compare their common model
        # exactly rather than silently pretending these COM conventions match.
        c = g.config(dict(L2=273., L3=273., ra=28., rb=14., m1=8.3, m2=.35, m3=0., m5=0., m6=.9))
        s = g.resolved_spring(c, 'legacy_tip')
        old = {**legacy_math.DEFAULTS, **s, 'length': .273, 'extension': .05,
               'chassis_mass': 8.3, 'upper_mass': .35, 'lower_mass': 0., 'wheel_mass': .9,
               'gravity': c['g'], 'theta': 80., 'balance_spring': False, 'damping': 0.}
        params = legacy_math.parameters(old)
        for theta_deg in (25., 45., 70.):
            theta = math.radians(theta_deg); q = math.pi-theta
            M, Mp, _, J, elastic, _, _, _ = legacy_math.terms(theta, -.3, old, params)
            old_required = M*(-.4)+.5*Mp*.3**2+params['S']*c['g']*math.cos(theta)+elastic*J
            new = g.inverse_dynamics(q, .3, .4, c, 'supported_chassis', s)
            self.assertAlmostEqual(M, new['inertia_kg_m2'], places=12)
            self.assertAlmostEqual(-old_required, new['tau_q_Nm'], places=10)

    def test_all_nine_unequal_alpha_passive_work_and_fit_constraints(self):
        c = candidate(); qs = np.linspace(math.radians(108), math.radians(157), 81)
        for topology in g.CATALOG:
            fitted = g.fit_spring(c, topology, qs)
            self.assertTrue(fitted['feasible'], (topology, fitted.get('reason')))
            self.assertGreaterEqual(fitted['stiffness_N_mm'], 0.)
            self.assertGreater(fitted['physical_free_length_mm'], 0.)
            check = g.virtual_work_checks(c, fitted['config'], qs[::10])
            self.assertTrue(check['passed'], (topology, check))
            if fitted['config']['spring_transmission']=='ideal_rope':
                self.assertTrue(all(g.spring_state(q, 0., c, fitted['config'])['law']['tension']>=0 for q in qs))
            self.assertFalse(fitted['exact_constant_lift'])

    def test_motor_coordinate_scaling_and_quintic_endpoints(self):
        c = candidate(); rows, travel = g.trajectory(c, 1., 201)
        self.assertAlmostEqual(travel['total_capacity_mm'], 325., places=8)
        self.assertAlmostEqual(travel['usable_lift_mm'], 285., places=8)
        for row in (rows[0], rows[-1]):
            self.assertAlmostEqual(row['qdot_rad_s'], 0., places=10)
            self.assertAlmostEqual(row['qddot_rad_s2'], 0., places=10)
        hip = g.size_fixture(c, rows, 'supported_chassis')
        knee = g.size_fixture(c, rows, 'supported_chassis', actuator_coordinate='relative_knee', reduction=10., efficiency=.85)
        i = 70
        self.assertAlmostEqual(knee['trajectory'][i]['tau_motor_Nm'], -hip['trajectory'][i]['tau_q_Nm']/c['qab']/10/.85)
        self.assertAlmostEqual(knee['trajectory'][i]['motor_speed_rad_s'], -rows[i]['qdot_rad_s']*c['qab']*10)

    def test_mass_allocation_and_massless_engine_refusal(self):
        self.assertAlmostEqual(sum(candidate()[k] for k in ('m1','m2','m3','m5','m6')), 10.)
        with self.assertRaisesRegex(ValueError, 'positive dynamic body masses'):
            g.verify_pymunk(g.config(), None)

    def test_json_manual_preload_and_no_duplicate_fit_mutation(self):
        c = candidate()
        result = g.study(dict(config=c, spring=dict(topology='hip_pulley', stiffness=5000., preload_mm=12.)))
        json.dumps(result, allow_nan=False)
        selected = result['selected_spring']
        fitted = next(x for x in result['spring_comparisons'] if x['topology']=='hip_pulley')
        self.assertAlmostEqual(selected['stiffness_N_mm'], 5.)
        self.assertAlmostEqual(selected['preload_N'], 60., places=8)
        self.assertNotEqual(selected['config']['stiffness'], fitted['config']['stiffness'])
        self.assertEqual(len(result['impact_cases']['cases']), 8)

    def test_actual_pymunk_dynamic_refinement_generalized_rotors(self):
        c = g.physical_allocation(g.config(dict(L2=290., L3=235., ra=96., rb=60., rc=30., rd=35., re=36., rf=32., alpha=17., phi0=10.)))
        rows, _ = g.trajectory(c, 1., 51)
        fit = g.fit_spring(c, 'knee_pulley', [row['q_rad'] for row in rows])
        check = g.verify_pymunk(c, fit['config'])
        self.assertTrue(check['passed'], [(x['max_torque_error_Nm'],x['rms_torque_error_Nm']) for x in check['refinement']])
        self.assertGreater(check['error_reduction'], 1.5)

    def test_actual_pymunk_all_nine_final_candidate_impulses(self):
        c = candidate(); qs = np.linspace(math.radians(108), math.radians(157), 81)
        for topology in g.CATALOG:
            fitted = g.fit_spring(c, topology, qs)
            check = g.verify_pymunk(c, fitted['config'], duration_s=.12, hold_q=math.radians(130.))
            self.assertTrue(check['passed'], (topology, [(x['max_torque_error_Nm'],x['rms_torque_error_Nm']) for x in check['refinement']]))

    def test_bidirectional_chassis_raise_actual_dynamics(self):
        c = candidate(); rows, _ = g.trajectory(c, 1., 81)
        fitted = g.fit_spring(c, 'hip_bellcrank', [row['q_rad'] for row in rows])
        up = g.reverse_trajectory(rows)
        self.assertLess(up[len(up)//2]['qdot_rad_s'], 0.)
        self.assertGreater(g.kinematics(up[-1]['q_rad'], c, 'supported_chassis')['points']['A'][1],
                           g.kinematics(up[0]['q_rad'], c, 'supported_chassis')['points']['A'][1])
        check = g.verify_pymunk(c, fitted['config'], direction='extension')
        self.assertTrue(check['passed'], [(x['max_torque_error_Nm'],x['rms_torque_error_Nm']) for x in check['refinement']])


if __name__ == '__main__':
    unittest.main()
