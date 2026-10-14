"""Check lateral excursion, inversion symmetry, force and buffered ROM.

Run from app: .venv/Scripts/python.exe -m unittest -v test_curved_paths
Inputs: explicit ideal mm/degree/N examples and retained search evidence.
Outputs: unittest assertions; pinned NumPy/SciPy. Limits: no measured
compliance, physical collision, impact, hardware or canonical validation.
"""
from pathlib import Path
import json
import unittest
import numpy as np
from curved_path_search import candidate,path_metrics,curve,R,F45


class CurvedPathTests(unittest.TestCase):
    def test_vertical_baseline_is_not_curved(self):
        c=candidate('vertical',300,300,2,100)
        for side in ['normal','useful','full']:
            self.assertAlmostEqual(c[side]['lateral_excursion_mm'],0,places=9)
            self.assertEqual(c[side]['turning_q_deg'],[])
            self.assertTrue(c[side]['monotone_lateral'])

    def test_inversion_returns_laterally_despite_excursion(self):
        c=candidate('curved',190,190,1.8,100)
        self.assertAlmostEqual(c['normal']['lateral_excursion_mm'],49.980753,places=5)
        self.assertAlmostEqual(c['full']['signed_drift_mm'],0,places=9)
        self.assertGreater(c['full']['lateral_excursion_mm'],50)
        self.assertEqual(c['full']['turning_q_deg'],[180.])
        self.assertTrue(c['full_ideal_inverse'])
        self.assertFalse(c['normal_coplanar220_pass'])
        self.assertFalse(c['full_coplanar220_pass'])

    def test_height_roots_and_work(self):
        c=candidate('curved',190,190,1.8,100)
        p=c['config'];lo,hi=c['force']['usable_angle_bounds_deg']
        z=lambda q:float(curve(q*R,190,190,1.8)[1])
        self.assertAlmostEqual(z(p['tc'])-z(p['te']),325,places=8)
        self.assertAlmostEqual(z(lo)-z(p['te']),20,places=8)
        self.assertAlmostEqual(z(p['tc'])-z(hi),20,places=8)
        self.assertAlmostEqual(c['force']['work_integral_45kg_J'],F45*.285,places=5)
        self.assertAlmostEqual(c['force']['relative_knee_ROM_deg'],1.8*(hi-lo),places=9)

    def test_lateral_derivatives_and_stiffness_mapping(self):
        for q in np.linspace(100*R,260*R,41):
            def original(v):
                lower=(np.pi-v)*.8
                return np.array([-190*np.cos(v)-190*np.cos(lower),-190*np.sin(v)-190*np.sin(lower)])
            j=(original(q+1e-6)-original(q-1e-6))/(2e-6)
            np.testing.assert_allclose(j,curve(q,190,190,1.8)[2:],rtol=1e-8,atol=1e-6)
            C=np.outer(j/1000,j/1000)/100
            self.assertAlmostEqual(np.linalg.det(C),0,places=15)
            self.assertGreaterEqual(np.linalg.eigvalsh(C)[0],-1e-15)

    def test_continuous_metrics_against_dense_reference(self):
        c=candidate('curved',195,200,1.68,100)
        for side,bounds in [('normal',[100,c['config']['tc']]),('full',[100,260])]:
            q=np.linspace(*[v*R for v in bounds],10001);x,z,jx,jz=curve(q,195,200,1.68)
            self.assertAlmostEqual(c[side]['lateral_excursion_mm'],float(np.ptp(x)),places=6)
            self.assertAlmostEqual(c[side]['min_hip_distance_mm'],float(np.min(np.hypot(x,z))),places=5)
            self.assertAlmostEqual(c[side]['max_Jz_mm_rad'],float(np.max(jz)),places=6)
        self.assertGreaterEqual(c['force']['robust_abs_Fx_over_Fz_0p3_peak_Nm'],
                                max(c['force']['side_load_peak_Nm'].values())-1e-9)

    def test_retained_band_and_clearance_flags(self):
        d=json.loads((Path(__file__).parent/'docs/curved-path-results.json').read_text())
        for c in d['selected']:
            self.assertTrue(c['full_ideal_inverse']);self.assertTrue(c['guide_pitch_pass'])
            self.assertGreaterEqual(c['fold_guard_deg'],5-1e-7)
            self.assertAlmostEqual(c['normal']['vertical_mm'],325,places=7)
            self.assertAlmostEqual(c['useful']['vertical_mm'],285,places=7)
            self.assertFalse(c['full_coplanar220_pass'])
            if c['id'].startswith('w'):
                target=int(c['id'].split('_')[0][1:])
                self.assertLessEqual(abs(c['normal']['lateral_excursion_mm']-target),2.5+1e-7)
                self.assertTrue(c['normal']['monotone_lateral'])
                if 'normal220' in c['id']:self.assertTrue(c['normal_coplanar220_pass'])
            if c['config']['te']<100:
                self.assertLessEqual(c['full_bounds_deg'][0],c['config']['te'])
                self.assertGreaterEqual(c['full_bounds_deg'][1],360-c['config']['te'])


if __name__=='__main__':unittest.main()
