"""Validate experimental linkage mechanics and reference equations.

Run: python -m unittest -v test_physics test_equation_checks from app root.
Inputs: explicit SI test fixtures; degree reference angles are converted to radians.
Outputs: unittest diagnostics; no files. Requires pinned Pymunk.
Limitations: numerical/analytical checks, not canonical robot or hardware validation.
"""
import math
import unittest
from equation_checks import screenshot_reference
from physics import simulate

class EquationChecks(unittest.TestCase):
    def test_reported_torques_match_inferred_400_mm_links(self):
        for T0 in [0.,70.,300.]:
            for radius in [.015,.04]:
                for angle,expected in [(0.,83.752875),(42.,60.8231567152)]:
                    r=screenshot_reference(angle,.4,.4,27.590625,111.58875,radius,r_w=.2,T0=T0)
                    self.assertAlmostEqual(r['M_act'],expected,places=9)

    def test_locked_contact_case_agrees_with_independent_energy_model(self):
        from test_physics import reference
        values={'wave':'impulse','impulse':.15,'pulse_width':.12,'start':.15,'duration':.8,
                'bias_force_x':27.590625,'load_point':'contact','wheel_drive_locked':True}
        angle,_=reference(values)
        a=simulate({**values,'dt':.001})
        b=simulate({**values,'dt':.00025})
        self.assertLess(abs(b['rows'][-1]['theta_deg']-angle),.025)
        self.assertLess(abs(b['rows'][-1]['theta_deg']-angle),abs(a['rows'][-1]['theta_deg']-angle))

    def test_visible_reference_chain_reduces_to_moment_identity(self):
        for theta in [-10,0,42,60,85]:
            for Fy,Fz in [(20,100),(-40,60),(70,-20)]:
                for radius in [.015,.04]:
                    r=screenshot_reference(theta,.3,.2,Fy,Fz,radius,r_w=.2,T0=40.,extra_min=2.)
                    a=math.radians(theta)
                    expected=(.3+.2)*Fz*math.cos(a)+(.3-.2)*Fy*math.sin(a)-Fy*.2-2.
                    self.assertAlmostEqual(r['M_act'],expected,places=10)
                    self.assertAlmostEqual(r['identity_error_Nm'],0,places=10)
                    self.assertAlmostEqual(r['g1_identity_error_N'],0,places=10)
                    self.assertAlmostEqual(r['g2_identity_error_N'],0,places=10)
                    self.assertGreaterEqual(r['T'],0)

    def test_zero_moment_uses_continuous_force_limit(self):
        r=screenshot_reference(0,.3,.2,20,100,.02,r_w=.2,T0=30.,extra_min=16.)
        self.assertEqual(r['T'],0)
        self.assertIsNone(r['beta_deg'])
        self.assertEqual(r['B_y'],-10)
        self.assertEqual(r['B_z'],100)
        self.assertAlmostEqual(r['M_act'],30)

    def test_pulley_radius_domain(self):
        for radius in [0,-.02,.31]:
            with self.assertRaises(ValueError):screenshot_reference(42,.3,.2,20,100,radius,r_w=.2,T0=30.)

    def test_T0_changes_bearings_but_not_hip_moment(self):
        a=screenshot_reference(42,.3,.2,20,100,.02,r_w=.2,T0=0.)
        b=screenshot_reference(42,.3,.2,20,100,.02,r_w=.2,T0=180.)
        self.assertAlmostEqual(a['M_act'],b['M_act'])
        self.assertNotAlmostEqual(a['B_r'],b['B_r'])
        self.assertAlmostEqual(b['g1'],67+180*math.cos(math.radians(42)))
        self.assertAlmostEqual(b['g2'],50-180*math.sin(math.radians(42)))

    def test_contact_torque_spins_free_wheel_or_loads_locked_drive(self):
        values={'duration':.4,'amplitude':0.,'bias_force_x':27.590625,'load_point':'contact'}
        free=simulate(values);locked=simulate({**values,'wheel_drive_locked':True})
        f,l=free['rows'][-1],locked['rows'][-1]
        expected=27.590625*.2
        self.assertAlmostEqual(f['wheel_external_moment'],expected)
        self.assertEqual(f['wheel_drive_reaction'],0.)
        self.assertGreater(f['wheel_speed'],70.)
        self.assertAlmostEqual(l['wheel_drive_reaction'],expected,delta=.001)
        self.assertLess(abs(l['wheel_speed']),.001)
        self.assertTrue(all(x<1e-7 for x in locked['equation_check_errors'].values()))

    def test_screenshot_load_values(self):
        self.assertAlmostEqual(35*1.3/4*9.81,111.58875)
        self.assertAlmostEqual(.25*45/4*9.81,27.590625)

    def test_coordinate_and_full_balance_checks_in_both_fixtures(self):
        for fixture in ['hip','wheel']:
            r=simulate({'fixture':fixture,'duration':.9,'bias_force':80. if fixture=='hip' else 0.,'bias_force_x':27.590625})
            for key,value in r['equation_check_errors'].items():self.assertLess(value,1e-7,key)

    def test_lateral_force_is_resisted_without_vertical_work(self):
        a=simulate({'duration':.8,'amplitude':0.})
        b=simulate({'duration':.8,'amplitude':0.,'bias_force_x':27.590625})
        self.assertLess(abs(a['rows'][-1]['theta_deg']-b['rows'][-1]['theta_deg']),.002)
        self.assertAlmostEqual(b['rows'][-1]['j3_fx'],-27.590625,places=3)
        self.assertGreater(abs(b['rows'][-1]['guide_hip_reaction']-a['rows'][-1]['guide_hip_reaction']),1.)

if __name__=='__main__':unittest.main(verbosity=2)
