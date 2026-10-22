"""Verify floating Kinefold quarter mechanics and cross-engine trajectories.

Run app .venv Python verify_dynamics.py here. Inputs: vendored JS V4 baseline,
varied mm/deg/kg/N geometry and explicit SI run profiles. Outputs unittest and
error/convergence evidence. Requires Node, SciPy, Pymunk. No hardware or contact
validation; the Pymunk chassis uses exact condensed ideal linkage kinematics.
"""
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest
from dynamic_model import Model, R, defaults
from dynamics import simulate
ROOT = Path(__file__).resolve().parent
JS = r"""
const fs=require('fs'),vm=require('vm');
vm.runInThisContext(fs.readFileSync('reference-v4.js','utf8'));
vm.runInThisContext(fs.readFileSync('model.js','utf8'));
const variants=[{}, {L2:340,L3:280,ra:47,rb:27,rc:31,rd:39,re:22,rf:29,alpha:13,phi0:17,m2:.5,m3:.5,m5:.2,m6:1},
{springLaw:'constant',alpha:25,m2:.3,m3:.8,m6:1.2},{rs:0,Su:0,nu:8},{springEnabled:false}];
console.log(JSON.stringify(variants.map(v=>{const p={...Kinefold.defaults,...v};return{p,rows:[101,120,140,164].map(theta=>{const s=Kinefold.evaluate({...p,theta2:theta});if(!s.valid)throw Error(s.errors);return{theta,tau:s.raw.tau2,Fs:s.spring.force,energy:s.spring.energy,C:s.C};})};})));
"""
class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.refs=json.loads(subprocess.check_output(['node','-e',JS],cwd=ROOT,text=True));cls.base=cls.refs[0]['p'];cls.report={}
    def run_model(self,engine,params=None,**settings):
        return simulate(dict(engine=engine,params=params or self.base,runConfig={**defaults(),**settings}))
    def test_source_parity_potential_and_mass(self):
        errors=[]
        for case in self.refs:
            p=case['p'];m=Model(p,{**defaults(),'inputRiseMm':10})
            for row in case['rows']:
                q,e=row['theta']*R,1e-6
                errors.append(abs(-m.generalized(q)-row['tau']))
                self.assertAlmostEqual(-m.generalized(q),row['tau'],delta=2e-10)
                self.assertAlmostEqual(m.spring(q)['force'],row['Fs'],delta=2e-9)
                self.assertAlmostEqual(m.spring(q)['energy'],row['energy'],delta=2e-10)
                self.assertAlmostEqual(-m.sites(q)['6'][0][0]*1000,row['C'][0],delta=2e-10)
                self.assertAlmostEqual(m.generalized(q),-(m.potential(q+e)-m.potential(q-e))/(2*e),delta=1e-6)
                M,dM,B,_=m.coefficients(q)
                self.assertGreater(M,0)
                self.assertAlmostEqual(dM,(m.mass(q+e)[0]-m.mass(q-e)[0])/(2*e),delta=1e-7)
                v,rd=.3,.07
                direct=sum(.5*p['m'+k]*((s[1][0]*v)**2+(rd+s[1][1]*v)**2) for k,s in m.floating_sites(q).items())
                direct+=sum(.5*m.I[k]*(m.rates[k]*v)**2 for k in m.I)
                self.assertAlmostEqual(direct,.5*M*v*v+B*v*rd+.5*m.total_mass*rd*rd,delta=1e-12)
        self.report['source_weight_mode_max_parity_Nm']=max(errors)
    def test_independent_heave_equation_and_reaction(self):
        p={**self.refs[1]['p'],'loadMode':'global','Fx':3,'Fz':8};m=Model(p,{**defaults(),'inputRiseMm':10});errors=[]
        for t in (.1,.51,.54,.58,1.96,2.1):
            for theta in (110,132.5,155):
                q,v=theta*R,.17;a=m.acceleration(q,v,t);h,hd,ha=m.chassis(t,q,v,a);iq,iv,ia=m.heave_acceleration(t,h,hd)
                self.assertAlmostEqual(iq,q,delta=1e-12);self.assertAlmostEqual(iv,v,delta=1e-12);self.assertAlmostEqual(ia,ha,delta=1e-9);errors.append(abs(ia-ha))
                direct=sum(p['m'+k]*(ha+s[1][1]*a+s[2][1]*v*v+p['g']) for k,s in {**m.sites(q),'1':((0,0),(0,0),(0,0))}.items())
                self.assertAlmostEqual(m.reaction(t,q,v,a),direct-m.force[1],delta=1e-9)
        self.report['independent_heave_max_accel_error_m_s2']=max(errors)
    def test_default_exact_square_both_full_cycles(self):
        results={}
        for engine in ('analytical','pymunk'):
            r=self.run_model(engine);results[engine]=r;d=r['diagnostics']
            self.assertEqual(d['termination'],'duration');self.assertAlmostEqual(d['elapsedSeconds'],6.5,places=9)
            self.assertEqual(r['params'],self.base);self.assertEqual(d['builderMassesKg'],{'1':8.75,'2':0,'3':0,'5':0,'6':0});self.assertEqual(set(d['resolvedInertiasKgM2'].values()),{0})
            self.assertEqual([round(e['t'],8) for e in r['events']],[.5,2,3.5,5,6.5]);self.assertEqual([e['inputJumpMm'] for e in r['events']],[150,-150,150,-150,150])
            for e in r['events']:
                self.assertLess(abs(e['chassisPositionJumpMm']),1e-8);self.assertLess(abs(e['chassisVelocityJumpMmS']),1e-8)
                self.assertAlmostEqual(e['energyJumpJ'],e['inputWorkJumpJ']+e['actuatorWorkJumpJ'],delta=1e-10)
                a=e['after'];expected=math.pi-math.asin((a['chassisZMm']-a['wheelZMm'])/600)
                self.assertAlmostEqual(a['theta2']*R,expected,delta=1e-12)
            for row,f in zip(r['rows'],r['frames']):
                self.assertEqual(row['requestedInputMm'],row['appliedInputMm']);self.assertIn(row['appliedInputMm'],(0,150))
                self.assertAlmostEqual(f['A'][2],row['chassisZMm'],places=9);self.assertAlmostEqual(f['C'][2],row['wheelZMm'],places=9)
            self.assertLess(d['maxWorkEnergyResidualJ'],1e-5)
            if engine=='pymunk':
                self.assertEqual(d['chassisBodyMassKg'],8.75);self.assertEqual(d['rigidBodies'],1);self.assertLess(d['maxConstraintPositionErrorMm'],1e-8)
        self.assertEqual(len(results['analytical']['rows']),len(results['pymunk']['rows']))
        error=max(abs(a['chassisZMm']-b['chassisZMm']) for a,b in zip(results['analytical']['rows'],results['pymunk']['rows']))
        self.assertLess(error,.02);self.report['baseline_max_heave_difference_mm']=error;self.report['baseline_energy_residual_J']={k:r['diagnostics']['maxWorkEnergyResidualJ'] for k,r in results.items()}
    def test_gravity_once_and_equilibrium(self):
        for engine in ('analytical','pymunk'):
            r=self.run_model(engine,{**self.base,'springEnabled':False},duration=.05,inputHeightMm=0)
            self.assertAlmostEqual(r['rows'][0]['chassisAccelerationMmS2'],-9810,delta=1e-8);self.assertAlmostEqual(r['rows'][-1]['chassisVelocityMmS'],-490.5,delta=1e-5)
            self.assertLess(max(abs(row['inputReactionN']) for row in r['rows']),1e-8)
            m=Model(self.base,defaults());r=self.run_model(engine,duration=.2,inputHeightMm=0,hipTorqueNm=-m.generalized(m.q0))
            self.assertLess(max(abs(row['theta2']-self.base['theta2']) for row in r['rows']),1e-8)
    def test_nonzero_mass_finite_rise_convergence(self):
        p={**self.base,'m2':.5,'m3':.4,'m5':.2,'m6':1};c=dict(duration=.85,inputHeightMm=30,inputRiseMm=20,inputDelayS=.2,dampingNms=.1,initialVelocityDegS=1)
        ref=self.run_model('analytical',p,**c);self.assertEqual(ref['diagnostics']['termination'],'duration');self.assertLess(ref['diagnostics']['maxWorkEnergyResidualJ'],1e-7)
        errors,residuals=[],[]
        for dt in (.002,.001,.0005):
            r=self.run_model('pymunk',p,**c,dt=dt);self.assertEqual(r['diagnostics']['termination'],'duration');self.assertEqual(len(ref['rows']),len(r['rows']))
            errors.append(max(abs(a['chassisZMm']-b['chassisZMm']) for a,b in zip(ref['rows'],r['rows'])));residuals.append(r['diagnostics']['maxWorkEnergyResidualJ'])
        self.assertLess(errors[-1],errors[0]*.7);self.assertLess(residuals[-1],residuals[0]*.7)
        self.report['finite_rise_dt_s']=[.002,.001,.0005];self.report['finite_rise_heave_errors_mm']=errors;self.report['finite_rise_energy_residuals_J']=residuals
    def test_input_validation_travel_and_cli(self):
        c=defaults();m=Model(self.base,c)
        self.assertEqual([m.input(t)['applied'] for t in (.5,2,3.5)],[.15,0,.15]);self.assertEqual(m.input(2,'left')['applied'],.15)
        smooth=Model({**self.base,'m2':.1},{**c,'inputRiseMm':10});self.assertEqual(smooth.input(.5)['applied'],0);self.assertAlmostEqual(smooth.input(.55)['applied'],.075,places=12);self.assertAlmostEqual(smooth.input(.6)['applied'],.15,places=12)
        for p in ({**self.base,'m1':0},{**self.base,'m2':-.1},{**self.base,'ra':300},{**self.base,'unknown':1}):
            with self.assertRaises(ValueError):Model(p,c)
        for bad in ({**c,'inputRiseMm':-1},{**c,'inputRiseMm':100},{**c,'inputSpeedMmS':0},{**c,'dampingNms':.1},{**c,'hipRotorInertiaKgM2':.05}):
            with self.assertRaises(ValueError):Model(self.base,bad)
        with self.assertRaisesRegex(ValueError,'Exact square jumps'):Model({**self.base,'m6':1},c)
        for engine in ('analytical','pymunk'):
            r=self.run_model(engine,duration=.6,inputHeightMm=800);self.assertEqual(r['diagnostics']['termination'],'input-jump-travel-limit');self.assertAlmostEqual(r['rows'][-1]['t'],.5,places=8);self.assertEqual(r['rows'][-1]['appliedInputMm'],0)
        r=self.run_model('analytical',duration=.6,hipTorqueNm=.2);e=r['events'][0];self.assertAlmostEqual(e['actuatorWorkJumpJ'],.2*e['theta2JumpDeg']*R,places=12);self.assertLess(r['diagnostics']['maxWorkEnergyResidualJ'],1e-7)
        payload=dict(engine='analytical',params=self.base,runConfig={**c,'duration':.05})
        cli=subprocess.run([sys.executable,'dynamics.py','--request-stdin'],cwd=ROOT,input=json.dumps(payload),text=True,capture_output=True,check=True)
        self.assertEqual(json.loads(cli.stdout)['scope']['fixture'],'floating-chassis')
        bad=subprocess.run([sys.executable,'dynamics.py','--request-stdin'],cwd=ROOT,input='{}',text=True,capture_output=True);self.assertNotEqual(bad.returncode,0);self.assertIn('error',json.loads(bad.stdout))
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks));print(json.dumps(Checks.report,indent=2));raise SystemExit(not result.wasSuccessful())
