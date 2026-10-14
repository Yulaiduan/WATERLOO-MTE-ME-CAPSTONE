"""Independently check force/travel evidence and coordinate/work identities.

Run: .venv/Scripts/python.exe -m unittest -v test_force_travel
Inputs: mm/radian geometry, retained selected evidence and explicit N load.
Outputs: unittest assertions; NumPy/SciPy only. Limits: analytical consistency,
not a motor rating, collision/contact, impact or canonical robot validation.
"""
import json
import math
from pathlib import Path
import unittest
import numpy as np
from scipy.integrate import quad
from force_travel_search import curve, force_metrics, evaluate, accepted, F45, R


class ForceTravelTests(unittest.TestCase):
    def test_derivative_and_vertical_virtual_work(self):
        # Independent original V2 trigonometric expression, not curve derivatives.
        for a,b,r,phase in [(350,350,1.75,0),(322.5,375,1.7375,0),(300,300,2,-25)]:
            def pos(q):
                lower=phase*R+(math.pi-q)*(r-1)
                return np.array([-a*math.cos(q)-b*math.cos(lower),-a*math.sin(q)-b*math.sin(lower)])
            for q in np.linspace(100*R,260*R,51):
                fd=(pos(q+1e-6)-pos(q-1e-6))/(2e-6)
                analytical=np.array(curve(q,a,b,r,phase)[2:])
                np.testing.assert_allclose(fd,analytical,rtol=1e-8,atol=1e-6)

    def test_height_buffers_and_quadrature(self):
        c=evaluate('example',350,350,1.75,115,325)
        f=c['force'];lo,hi=[v*R for v in f['usable_angle_bounds_deg']]
        start=c['config']['te']*R;end=c['config']['tc']*R
        z=lambda q:float(curve(q,350,350,1.75)[1])
        j=lambda q:float(curve(q,350,350,1.75)[3])/1000
        self.assertAlmostEqual(z(lo)-z(start),20,places=8)
        self.assertAlmostEqual(z(end)-z(hi),20,places=8)
        rms=math.sqrt(quad(lambda q:j(q)**3,lo,hi,epsabs=1e-12)[0]/.285)
        self.assertAlmostEqual(rms,f['rms_Jz_uniform_height_m_rad'],places=7)
        self.assertAlmostEqual(quad(lambda q:F45*j(q),lo,hi)[0],F45*.285,places=9)
        self.assertLess(abs(f['work_integral_45kg_J']-f['ideal_lift_work_45kg_J']),1e-5)

    def test_exact_peak_and_knee_mapping(self):
        for a,b,r in [(350,350,1.75),(450,450,1.7925)]:
            c=evaluate('example',a,b,r,115 if a==350 else 120,325)
            f=c['force'];last=f['usable_angle_bounds_deg'][1]*R
            peak=float(curve(last,a,b,r)[3])/1000
            self.assertAlmostEqual(peak,f['max_Jz_m_rad'],places=12)
            self.assertAlmostEqual(f['min_force_per_hip_N_Nm']*peak,1,places=12)
            self.assertAlmostEqual(f['peak_45kg_relative_knee_Nm']*r,f['peak_45kg_hip_Nm'],places=12)
            speed=.7;hip=f['peak_45kg_hip_Nm'];knee=-hip/r
            self.assertAlmostEqual(hip*speed,knee*(-r*speed),places=12)
            self.assertGreaterEqual(peak, .285/((f['hip_ROM_deg'])*R))

    def test_rejected_geometries_not_promoted(self):
        good=evaluate('example',350,350,1.75,115,325)
        self.assertTrue(accepted(good))
        self.assertFalse(good['full_inversion']['coplanar_clearance_pass'])
        with self.assertRaises(ValueError):evaluate('too_short',100,100,1.75,115,325)
        with self.assertRaises(ValueError):force_metrics(350,350,1.75,100,100)

    def test_retained_metrics_and_acceptance(self):
        data=json.loads((Path(__file__).parent/'docs/force-travel-results.json').read_text())
        for c in data['selected']:
            p=c['config'];new=evaluate(c['id'],p['L2'],p['L3'],p['qab'],p['te'],c['total_mm'],p['phi0'],
                 2 if c['id'].endswith('bow2') else 3)
            for key in ['max_Jz_m_rad','min_force_per_hip_N_Nm','rms_Jz_uniform_height_m_rad','hip_ROM_deg']:
                self.assertAlmostEqual(new['force'][key],c['force'][key],places=10)
            self.assertEqual(new['acceptance'],c['acceptance'])
            self.assertFalse(c['full_inversion']['coplanar_clearance_pass'])
            self.assertTrue(c['full_inversion']['ideal_height_invertible'])
        for r in data['refinement']:
            if r['dense_accepted']:
                self.assertTrue(accepted(next(c for c in data['selected'] if c['id']==r['id'])))


if __name__=='__main__':unittest.main()
