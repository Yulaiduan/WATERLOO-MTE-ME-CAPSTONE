"""Verify full-inversion geometry, search feasibility and phase identities.

Run: .venv/Scripts/python.exe -m unittest -v test_inversion_search
Inputs: mm/radian analytical fixtures and a small deterministic search grid.
Outputs: assertions for parity, derivatives, inversion/clearance classification,
exact phase-generated lines and un-clipped height solutions. NumPy/SciPy needed.
Limits: consistency of ideal planar kinematics, not hardware/contact validation.
"""
import math
import unittest
import numpy as np
import inversion_search as s


class InversionGeometryTests(unittest.TestCase):
    def test_direct_v2_formula_and_derivatives_beyond_normal_side(self):
        for l2,l3,r,phase in [(250,250,5/3,0),(315,300,1.82,0),(275,250,2,-25)]:
            for q in np.linspace(100*s.R,260*s.R,19):
                x,z,dx,dz=s.curve(q,l2,l3,r,phase)
                t3=phase*s.R+(math.pi-q)*(r-1)
                np.testing.assert_allclose([x,z],[-l2*math.cos(q)-l3*math.cos(t3),-l2*math.sin(q)-l3*math.sin(t3)],atol=2e-12)
                h=1e-6;plus=np.array(s.curve(q+h,l2,l3,r,phase)[:2]);minus=np.array(s.curve(q-h,l2,l3,r,phase)[:2])
                np.testing.assert_allclose((plus-minus)/(2*h),[dx,dz],atol=2e-7)

    def test_parity_fold_and_nonzero_fold_jacobian(self):
        for l2,l3,r in [(250,250,5/3),(275,250,2),(440,425,1.82)]:
            for t in [.1,.5,1.2]:
                a=s.curve(math.pi+t,l2,l3,r);b=s.curve(math.pi-t,l2,l3,r)
                np.testing.assert_allclose([a[0],a[1],a[2],a[3]],[b[0],-b[1],-b[2],b[3]],atol=2e-12)
            c=s.curve(math.pi,l2,l3,r)
            np.testing.assert_allclose(c,[l2-l3,0,0,l2+(r-1)*l3],atol=1e-12)

    def test_exact_phase_line_and_near_equal_example(self):
        phase=-25;d=phase*s.R/2
        for q in np.linspace(150*s.R,210*s.R,71):
            amplitude=500*math.sin(q-math.pi-d)
            np.testing.assert_allclose(s.curve(q,250,250,2,phase)[:2],amplitude*np.array([-math.sin(d),math.cos(d)]),atol=2e-12)
        m=s.metrics(275,250,2,160,200,-25)
        u0,u1=-7.5*s.R,32.5*s.R
        dz=25*(math.cos(u1)-math.cos(u0))*math.sin(d)+525*(math.sin(u1)-math.sin(u0))*math.cos(d)
        dx=25*(math.cos(u1)-math.cos(u0))*math.cos(d)-525*(math.sin(u1)-math.sin(u0))*math.sin(d)
        self.assertAlmostEqual(m['vertical_mm'],dz,places=10)
        self.assertAlmostEqual(m['chord_tilt_deg'],math.degrees(math.atan2(dx,dz)),places=10)
        self.assertLess(m['max_chord_error_mm'],1.55)
        self.assertFalse(m['projected_clearance_pass'])

    def test_symmetric_inversion_and_asymmetric_chord_not_constant_tangent(self):
        m=s.metrics(250,250,1.8,100,260)
        self.assertAlmostEqual(m['chord_tilt_deg'],0,places=10)
        self.assertTrue(m['crosses_hip_height']);self.assertEqual(m['minimum_hip_distance_mm'],0)
        partial=s.metrics(250,250,1.8,100,160)
        self.assertTrue(10<partial['chord_tilt_deg']<15)
        self.assertGreater(partial['tangent_spread_deg'],20)

    def test_small_search_never_clips_requested_capacity(self):
        result=s.search(True)
        self.assertGreater(result['counts']['normal_grid'],60000)
        for key,pool in result['pools'].items():
            for row in pool:
                a=s.curve(row['start']*s.R,row['L2'],row['L3'],row['ratio'])[1]
                b=s.curve(row['end']*s.R,row['L2'],row['L3'],row['ratio'])[1]
                self.assertAlmostEqual(b-a,row['target'],delta=2e-5,msg=key)


if __name__=='__main__':unittest.main()
