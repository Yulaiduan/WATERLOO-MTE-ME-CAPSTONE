"""Validate merged original-backend geometry/dynamics against Jonathan's code.

Run: .venv/Scripts/python.exe -m unittest -v test_generalized_linkage.
Inputs: deterministic varied SI profiles; Node runs original mm/deg reference.
Outputs: assertions and compact refinement evidence on stdout; no retained runs.
Limits: analytical/fixture agreement, not canonical contact/hardware/GPU evidence.
"""
import json
import math
from pathlib import Path
import random
import subprocess
import unittest
from unittest.mock import patch
import numpy as np
import linkage_geometry as geo
import generalized_suspension as general
from math_model import DEFAULTS,simulate_math,config as math_config
from physics import simulate,config as physics_config
from spring_mechanisms import apply_preset,geometry

ROOT=Path(__file__).resolve().parent

def demo():
    c=apply_preset(DEFAULTS,'gravity_balance');c.update(linkage_design='general',lower_length=c['length'],duration=.7,dt=.0005,start=.1,rise=.15,position_amplitude=.004,iterations=200)
    return c

class GeneralizedLinkage(unittest.TestCase):
    def test_original_johnathan_geometry_angles_forces_and_inertias(self):
        rng=random.Random(14026);cases=[];profiles=[]
        for _ in range(32):
            c=demo();c.update(length=rng.uniform(.25,.6),lower_length=rng.uniform(.25,.6),extension=0.,mount_angle=rng.uniform(0,45),link_phase=rng.uniform(0,30),guide_knee_radius=rng.uniform(.01,.025),drive_hip_radius=rng.uniform(.02,.04),drive_knee_radius=rng.uniform(.02,.04),drive_output_radius=rng.uniform(.02,.04),wheel_pulley_radius=rng.uniform(.02,.04),compound_mass=rng.uniform(0,1),contact_beta=rng.uniform(0,90),bias_force_x=rng.uniform(-100,100),bias_force=rng.uniform(-100,100),load_point='contact')
            c['guide_hip_radius']=c['guide_knee_radius']*rng.uniform(.7,3)
            p={'L2':c['length']*1000,'L3':c['lower_length']*1000,'ra':c['guide_hip_radius']*1000,'rb':c['guide_knee_radius']*1000,'rc':c['drive_hip_radius']*1000,'rd':c['drive_knee_radius']*1000,'re':c['drive_output_radius']*1000,'rf':c['wheel_pulley_radius']*1000,'rw':c['radius']*1000,'alpha':c['mount_angle'],'phi0':c['link_phase'],'te':180-c['theta_max'],'tc':180-c['theta_min'],'m1':c['chassis_mass'],'m2':c['upper_mass'],'m3':c['lower_mass'],'m5':c['compound_mass'],'m6':c['wheel_mass'],'g':c['gravity'],'r5I':c['compound_inertia_radius']*1000,'beta':c['contact_beta'],'loadMode':'yz','Fy':c['bias_force_x'],'Fz':c['bias_force'],'Fn':0.,'Ft':0.,'Tab0':0.,'Tcd0':0.,'Tef0':0.}
            for q in np.linspace(math.radians(c['theta_min']),math.radians(c['theta_max']),9):cases.append({'parameters':p,'theta2':180-math.degrees(q)});profiles.append((c,q))
        run=subprocess.run(['node','scripts/jon_reference_fixtures.cjs'],cwd=ROOT,input=json.dumps(cases),text=True,capture_output=True,check=True)
        refs=json.loads(run.stdout)
        for (c,q),ref in zip(profiles,refs):
            self.assertTrue(ref['valid']);sites,angles,_=geo.points(q,c)
            C=-np.array(sites['hip'][0])*1000;B=(np.array(sites['knee'][0])-np.array(sites['hip'][0]))*1000
            np.testing.assert_allclose(C,ref['C'],rtol=0,atol=1e-10);np.testing.assert_allclose(B,ref['B'],rtol=0,atol=1e-10)
            self.assertAlmostEqual(math.degrees(angles['lower']+math.pi)+c['mount_angle'],ref['t3'],10)
            self.assertAlmostEqual(math.degrees(angles['compound'])+c['mount_angle'],ref['t5'],10);self.assertAlmostEqual(math.degrees(angles['wheel'])+c['mount_angle'],ref['t6'],10)
            fx,fy,fn,ft,Mw=geo.loads(c)
            np.testing.assert_allclose([fx,fy,fn,ft],[ref[k] for k in ('Fy','Fz','Fn','Ft')],rtol=0,atol=1e-10)
            Cq=-np.array(sites['hip'][1]);fixed_hip_gravity=c['gravity']*sum(m*(sites[key][1][1]-sites['hip'][1][1]) for key,m in geo.masses(c).items())
            independent_hold=float(np.array([fx,fy])@Cq)-fixed_hip_gravity-geo.coefficient(c)*Mw
            self.assertAlmostEqual(independent_hold,ref['tau2'],9)
            cd,ef=geo.ratios(c)[1:];self.assertAlmostEqual(-Mw*cd*ef,ref['tau4'],10)
            I=geo.inertias(c);np.testing.assert_allclose([I['upper'],I['lower'],I['compound'],I['wheel']],[ref['inertia'][k] for k in ('I2','I3','I5','I6')],rtol=0,atol=1e-12)
            self.assertLess(ref['forceResidual'],1e-9);self.assertLess(ref['momentResidual'],1e-9);self.assertLess(ref['virtualWorkError'],1e-9)

    def test_original_2_to_1_math_is_recovered(self):
        c=demo();a=simulate_math(dict(c,linkage_design='original'));b=simulate_math(c)
        self.assertEqual(len(a['rows']),len(b['rows']))
        for key in ('theta_deg','chassis_displacement','spring_tension','driver_force','mechanical_energy_J'):
            self.assertLess(max(abs(x[key]-y[key]) for x,y in zip(a['rows'],b['rows'])),1e-6,key)

    def test_general_jacobian_and_energy_gradient(self):
        c=demo();c.update(lower_length=.32,guide_knee_radius=.018,mount_angle=12.,link_phase=8.,compound_mass=.2)
        eps=1e-6
        for q in np.linspace(.3,1.1,19):
            sites,_,_=geo.points(q,c);plus=geo.points(q+eps,c)[0];minus=geo.points(q-eps,c)[0]
            for key in sites:np.testing.assert_allclose(sites[key][1],(np.array(plus[key][0])-np.array(minus[key][0]))/(2*eps),rtol=0,atol=1e-9)
            g=geometry(q,c);fd=(geometry(q+eps,c)['input_length']-geometry(q-eps,c)['input_length'])/(2*eps);self.assertAlmostEqual(g['jacobian'],fd,8)
            def V(theta):return sum(m*geo.points(theta,c)[0][key][0][1] for key,m in geo.masses(c).items())*c['gravity']
            self.assertAlmostEqual((V(q+eps)-V(q-eps))/(2*eps),geo.energy_terms(q,c)[2]*c['gravity'],7)

    def test_scipy_has_no_pymunk_import_and_angular_balance_closes(self):
        c=demo();c.update(lower_length=.3,guide_knee_radius=.016,drive_knee_radius=.025,drive_output_radius=.04,compound_mass=.2,mount_angle=10.,link_phase=5.,load_point='contact',contact_force_mode='nt',contact_normal_force=20.,contact_tangent_force=4.,contact_beta=25.)
        import builtins
        original=builtins.__import__
        def guarded(name,*a,**kw):
            if name=='pymunk' or name.startswith('pymunk.'):raise AssertionError('Math imported Pymunk')
            return original(name,*a,**kw)
        with patch('builtins.__import__',guarded):r=simulate_math(c)
        self.assertLess(max(x['angular_check'] for x in r['rows']),1e-8)
        self.assertTrue(all(math.isfinite(v) for row in r['rows'] for v in row.values()))

    def test_pymunk_refinement_and_real_unequal_bodies(self):
        c=demo();c.update(lower_length=.3,guide_knee_radius=.016,drive_knee_radius=.025,drive_output_radius=.04,compound_mass=.2,mount_angle=10.,link_phase=5.)
        errors=[]
        for dt in (.001,.0005,.00025):
            cfg=dict(c,dt=dt);a=simulate_math(cfg);b=simulate(cfg);errors.append(abs(a['rows'][-1]['theta_deg']-b['rows'][-1]['theta_deg']))
            self.assertLess(b['diagnostics']['max_pin_error_m'],1e-5);self.assertLess(b['diagnostics']['max_position_error_m'],1e-4);self.assertLess(b['diagnostics']['max_guide_error_rad'],1e-5)
            self.assertLess(b['diagnostics']['max_force_check_N'],1e-8);self.assertLess(b['diagnostics']['max_torque_check_Nm'],.001)
            self.assertIn('compound',[x['name'] for x in b['model']['bodies']]);self.assertIn('compound_gear',[x['name'] for x in b['model']['constraints']])
        self.assertGreater(errors[0],errors[1]);self.assertGreater(errors[1],errors[2]);self.assertLess(errors[-1],.02)
        print('Generalized original-plant refinement, 1/.5/.25 ms final angle errors:',errors)

    def test_unity_guide_and_spin_cancellation(self):
        for ab in (1.,2.):
            c=demo();c.update(guide_knee_radius=c['guide_hip_radius']/ab,drive_hip_radius=.035,drive_knee_radius=.035,drive_output_radius=.035,wheel_pulley_radius=.035,balance_spring=False,stiffness=0.,gravity=0.,duration=.2,start=.05,rise=.05)
            r=simulate(c);self.assertTrue(all(math.isfinite(v) for row in r['rows'] for v in row.values()));self.assertAlmostEqual(geo.coefficient(c),0.)

    def test_general_geometry_for_all_original_spring_mechanisms(self):
        eps=1e-6
        for topology in ('legacy_tip','hip_pulley','knee_pulley','direct_scissor','hip_bellcrank','knee_bellcrank','chassis_direct','knee_capture','gravity_balance'):
            c=apply_preset(DEFAULTS,topology);c.update(linkage_design='general',lower_length=.3,guide_knee_radius=.016,mount_angle=10.,link_phase=5.)
            for q in np.linspace(.45,1.05,13):
                analytic=geometry(q,c)['jacobian'];finite=(geometry(q+eps,c)['input_length']-geometry(q-eps,c)['input_length'])/(2*eps)
                self.assertAlmostEqual(analytic,finite,7,topology)

    def test_general_conservative_energy_from_actual_bodies_refines(self):
        c=demo();c.update(lower_length=.3,guide_knee_radius=.016,drive_knee_radius=.025,drive_output_radius=.04,compound_mass=.2,mount_angle=10.,link_phase=5.,position_amplitude=0.,balance_spring=False,stiffness=2000.,duration=.25)
        a=simulate_math(c);initial=a['rows'][0]['mechanical_energy_J']
        self.assertLess(max(abs(r['mechanical_energy_J']-initial) for r in a['rows']),1e-8)
        errors=[]
        for dt in (.001,.0005,.00025):
            b=simulate(dict(c,dt=dt));self.assertTrue(all(c['theta_min']<r['theta_deg']<c['theta_max'] for r in b['rows']));self.assertLess(max(abs(r['stop_knee_torque']) for r in b['rows']),.001);start=b['rows'][0]['mechanical_energy_J'];errors.append(max(abs(r['mechanical_energy_J']-start) for r in b['rows']))
        self.assertGreater(errors[0],errors[1]);self.assertGreater(errors[1],errors[2]);self.assertLess(errors[-1],.01)
        print('Generalized actual-body conservative energy drift J, 1/.5/.25 ms:',errors)

    def test_invalid_geometry_fails_before_run(self):
        c=demo()
        for validator in (math_config,physics_config):self.assertEqual(validator(dict(c,guide_hip_radius=.12))['guide_hip_radius'],.12)
        for changes in ({'guide_knee_radius':0},{'compound_mass':-1},{'contact_beta_min':80,'contact_beta_max':10},{'drive_hip_radius':.3},{'wheel_drive_locked':True},{'aux_spring_enabled':True}):
            for validator in (math_config,physics_config):
                with self.assertRaises(ValueError):validator(dict(c,**changes))

if __name__=='__main__':unittest.main()
