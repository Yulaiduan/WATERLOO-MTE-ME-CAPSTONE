"""Check unequal-leg inversion, wheel projection and buffered force metrics.

Run from app: .venv/Scripts/python.exe -m unittest -v test_unequal_inversion
Inputs: explicit mm/degree cases and retained search JSON; NumPy/SciPy.
Outputs: unittest assertions. Limits: geometric projection and analytical
force only; no axial packaging, collision/contact or hardware certification.
"""
from pathlib import Path
import json
import unittest
import numpy as np
from unequal_inversion_search import evaluate,wheel_segment_distance,curve,R


class UnequalInversionTests(unittest.TestCase):
    def test_lower_long_clearance_bound(self):
        q=np.linspace(100*R,260*R,16001)
        for a,b,r in [(150,375,1.45),(160,500,1.4),(250,600,1.8)]:
            d=wheel_segment_distance(q,a,b,r)
            self.assertGreaterEqual(float(np.min(d)),b-a-1e-9)
            self.assertAlmostEqual(float(wheel_segment_distance(np.pi,a,b,r)),b-a,places=10)
            x,z=curve(q,a,b,r)[:2]
            self.assertAlmostEqual(float(np.min(np.hypot(x,z))),b-a,places=9)

    def test_upper_long_hip_test_is_insufficient(self):
        c=evaluate('upper',400,175,1.5,100)
        self.assertGreaterEqual(c['projection']['wheel_hip_min_mm'],220)
        self.assertAlmostEqual(c['projection']['wheel_upper_segment_min_mm'],0)
        self.assertFalse(c['projection']['point_segment_clear'])
        self.assertFalse(c['projection']['hip_pitch_circle_clear'])

    def test_pitch_pulley_and_guide_reserves(self):
        c=evaluate('tight',150,375,1.45,100);p=c['projection']
        self.assertTrue(p['point_segment_clear']);self.assertFalse(p['hip_pitch_circle_clear'])
        self.assertAlmostEqual(p['guide_pitch_surplus_mm'],3)
        self.assertFalse(p['recommended_guide_surplus'])
        c=evaluate('clear',160,500,1.4,100);p=c['projection']
        self.assertTrue(p['hip_pitch_circle_clear']);self.assertTrue(p['knee_pitch_circle_clear'])
        self.assertTrue(p['recommended_guide_surplus'])
        self.assertTrue(p['rods_overlap_at_fold']);self.assertFalse(p['physical_full_inversion_validated'])

    def test_height_inverse_through_fold(self):
        c=evaluate('clear',160,500,1.4,100)
        self.assertTrue(c['full_ideal_inverse']);self.assertGreater(c['full']['min_Jz_mm_rad'],5)
        self.assertAlmostEqual(c['full']['signed_drift_mm'],0,places=9)
        self.assertAlmostEqual(c['normal']['vertical_mm'],325,places=8)
        self.assertAlmostEqual(c['useful']['vertical_mm'],285,places=8)
        for z in [-1e-4,0,1e-4]:
            from inversion_search import inverse_height
            q=inverse_height(z,160,500,1.4,0,(100,260))
            self.assertAlmostEqual(float(curve(q,160,500,1.4)[1]),z,places=8)

    def test_source_jacobian_and_virtual_work(self):
        a,b,r=160,500,1.4
        for q in np.linspace(100*R,260*R,41):
            def original(v):
                lower=(np.pi-v)*(r-1)
                return np.array([-a*np.cos(v)-b*np.cos(lower),-a*np.sin(v)-b*np.sin(lower)])
            jac=(original(q+1e-6)-original(q-1e-6))/(2e-6)
            np.testing.assert_allclose(jac,curve(q,a,b,r)[2:],atol=1e-6,rtol=1e-8)
            force=np.array([30.,110.3625]);dq=1e-6
            work=float(force@(original(q+dq)-original(q-dq))/1000)
            expected=float(force@np.array(curve(q,a,b,r)[2:])/1000*2*dq)
            self.assertAlmostEqual(work,expected,places=11)

    def test_selected_continuous_acceptance(self):
        d=json.loads((Path(__file__).parent/'docs/unequal-inversion-results.json').read_text())
        for c in d['selected']:
            self.assertTrue(c['full_ideal_inverse'])
            self.assertAlmostEqual(c['normal']['vertical_mm'],325,places=7)
            self.assertAlmostEqual(c['useful']['vertical_mm'],285,places=7)
            if c['id'].startswith('w') and c['id'].split('_')[0][1:].isdigit():
                target=float(c['id'].split('_')[0][1:])
                self.assertLessEqual(abs(c['normal']['lateral_excursion_mm']-target),2.5+1e-7)
                self.assertTrue(c['normal']['monotone_lateral'])
                self.assertTrue(c['projection']['recommended_guide_surplus'])
                if 'pitch_circle' in c['id']:self.assertTrue(c['projection']['hip_pitch_circle_clear'])
                if 'segment220' in c['id']:self.assertTrue(c['projection']['point_segment_clear'])
            self.assertFalse(c['projection']['physical_full_inversion_validated'])


if __name__=='__main__':unittest.main()
