"""Check finite uniform-link actual-contact mechanics independently in SI.

Run app Python verify_finite_contact.py (Node/Pymunk required). Reads tracked
V4.5 and retained V4 statics, reports unittest results plus refinement numbers.
Inputs metres/kg/radians internally, builder mm/deg. Tests exact kinetic/COM
derivatives, gravity, freefall, native constraints and actual jump/landing/terrain.
Numerical consistency is experimental; no hardware or canonical robot proof.
"""
import copy
import json
import math
from pathlib import Path
import subprocess
import unittest
from contact_cases import CASE_DEFAULTS,validate_contact_request,energy_fields
from finite_contact_model import kinetic,gravity
from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as native

ROOT=Path(__file__).resolve().parent
PROFILE=json.loads((ROOT/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text())


def request(kind='landing',alpha=0,dt=.00025,**case):
    return dict(engine='analytical',params={**PROFILE['params'],'alpha':alpha},
        runConfig={**PROFILE['solverConfig'],'inputRiseMm':0,'dt':dt,'duration':.9,'outputHz':50},
        contactConfig=dict(mode='terrain-contact',drive='free',friction=.8,restitution=0),
        caseConfig={**CASE_DEFAULTS,'kind':kind,'landingDropMm':2000,'landingBrakeTorqueNm':300,'landingBrakeLimitNm':1000,'jumpTorqueNm':250,**case})


class FiniteChecks(unittest.TestCase):
    def test_exact_matrix_com_and_kinetic_derivatives(self):
        for alpha in (0,20):
            m=validate_contact_request(request(alpha=alpha));m.Jref=.03
            for degrees in (101,120,145,164):
                q=math.radians(degrees);a=m.mass_terms(q);eps=1e-6
                for vh,vd,w in ((.7,-.4,3),(-2,1.5,-2)):
                    qd=vd/m.jacobian(q);K=.5*m.p['m1']*vh**2+.5*m.Jref*qd**2+.5*m.I['6']*w*w
                    for key,rate in (('2',1),('3',m.k3),('6',0)):
                        plus=m.sites(q+eps)[key][0];minus=m.sites(q-eps)[key][0]
                        v=[(plus[i]-minus[i])/(2*eps)*qd for i in (0,1)];v[1]+=vh
                        K+=.5*m.p['m'+key]*(v[0]**2+v[1]**2)+.5*m.I[key]*(rate*qd)**2
                    self.assertAlmostEqual(K,kinetic(m,q,(vh,vd,w)),delta=2e-8)
                d=m.distance(q);de=1e-7;qp=m.inverse(d+de);qm=m.inverse(d-de)
                for field,deriv in (('H','Hprime'),('D','Dprime')):
                    numerical=(m.mass_terms(qp)[field]-m.mass_terms(qm)[field])/(2*de)
                    self.assertAlmostEqual(a[deriv],numerical,delta=2e-6)
                self.assertAlmostEqual((gravity(m,q+eps,.8)-gravity(m,q-eps,.8))/(2*eps),m.p['g']*a['B'],delta=2e-8)

    def test_retained_v4_static_and_both_flat_holding_runs(self):
        r=request('terrain-stability',dt=.0001);r['runConfig'].update(inputHeightMm=0,duration=.15);r['contactConfig']['friction']=0
        m=validate_contact_request(r);q=m.q0
        expected=m.grounded_gravity(q)-m.spring(q)['torque']
        js="const fs=require('fs'),vm=require('vm');vm.runInThisContext(fs.readFileSync('reference-v4.js','utf8'));const p=JSON.parse(process.argv[1]);p.Fy=0;p.Fz=['m1','m2','m3','m5','m6'].reduce((a,k)=>a+p[k],0)*p.g;p.loadMode='yz';console.log(JSON.stringify(VSLStatic.solve(p,p.theta2,true)));"
        oracle=json.loads(subprocess.check_output(['node','-e',js,json.dumps(r['params'])],cwd=ROOT,text=True))
        self.assertAlmostEqual(expected,oracle['tau2'],delta=1e-10)
        r['runConfig']['hipTorqueNm']=expected
        for sim in (analytical,native):
            s=sim(r)
            self.assertLess(max(abs(row['theta2']-r['params']['theta2']) for row in s['rows']),1e-3)
            self.assertAlmostEqual(s['rows'][-1]['contactNormalForceN'],m.total_mass*m.p['g'],delta=.002)

    def test_freefall_hold_all_body_energy(self):
        for alpha in (0,20):
            r=request(alpha=alpha);r['runConfig']['duration']=.1
            for sim in (analytical,native):
                s=sim(r);first=s['rows'][0]
                self.assertLess(max(abs(row['theta2']-first['theta2']) for row in s['rows']),1e-8)
                self.assertAlmostEqual(s['rows'][-1]['chassisVelocityMmS'],-981,delta=1e-6)
                self.assertGreater(s['rows'][-1]['linkKineticJ'],0)

    def test_landing_native_constraints_and_refinement(self):
        reports={}
        for alpha in (0,20):
            reports[alpha]={}
            for sim in (analytical,native):
                values=[]
                for dt in (.00025,.000125):
                    s=sim(request(alpha=alpha,dt=dt),stop_at_assessment=True);d=s['diagnostics']
                    self.assertTrue(s['caseMetrics']['landingSuccess'])
                    self.assertLess(d['maxPenetrationMm'],1)
                    self.assertLess(d['maxConstraintPositionErrorMm'],1)
                    self.assertEqual(d['rigidBodies'],4)
                    values.append(dict(dt=dt,arrest=s['caseMetrics']['firstArrestTimeS'],residual=abs(d['energyBalanceResidualJ']),penetration=d['maxPenetrationMm'],constraint=d['maxConstraintPositionErrorMm']))
                self.assertLess(values[1]['residual'],values[0]['residual'])
                reports[alpha][sim.__module__]=values
        print('FINITE_LANDING_REFINEMENT '+json.dumps(reports))

    def test_jump_stop_momentum_and_free_wheel_terrain(self):
        for alpha in (0,20):
            for sim in (analytical,native):
                r=request('jump',alpha=alpha,dt=.000125);r['runConfig']['duration']=1.1
                s=sim(r,stop_at_assessment=True)
                self.assertIsNotNone(s['caseMetrics']['takeoffTimeS'])
                observed=s['targetObservations'];self.assertIsNotNone(observed['jumpComRiseMm'])
                takeoff=observed['takeoffCOM'];apex=observed['apexCOM'];flight=apex['t']-takeoff['t']
                self.assertAlmostEqual(apex['vz'],takeoff['vz']-9.81*flight,delta=.003)
                self.assertAlmostEqual(observed['jumpComRiseMm'],takeoff['vz']**2/(2*9.81)*1000,delta=1.)
                self.assertLess(s['diagnostics']['maxPenetrationMm'],1)
                if sim==analytical:
                    stop=next(e for e in s['events'] if e['type']=='extension-stop')
                    self.assertAlmostEqual(stop['verticalMomentumBeforeKgMS'],stop['verticalMomentumAfterKgMS'],delta=1e-10)
                r=request('terrain-stability',alpha=alpha,dt=.000125);r['runConfig'].update(duration=.7,inputHeightMm=10,inputDelayS=.1)
                s=sim(r)
                self.assertEqual(s['diagnostics']['termination'],'duration')
                self.assertGreater(max(abs(row['wheelAngularVelocityDegS']) for row in s['rows']),1)
                self.assertLess(s['diagnostics']['maxPenetrationMm'],1)

    def test_no_phantom_mass_legacy_and_guards(self):
        r=request();r['params'].update(m2=0,m3=0);m=validate_contact_request(r)
        self.assertFalse(m.finite_links);self.assertEqual(m.I['2'],0)
        for edit in ({'m2':1,'m3':0},{'m2':0,'m3':1},{'m2':1,'m3':1,'m5':.1}):
            bad=copy.deepcopy(r);bad['params'].update(edit)
            with self.assertRaises(ValueError):validate_contact_request(bad)

    def test_native_bottom_out_is_detected_after_velocity_reversal(self):
        r=request(landingBrakeTorqueNm=150)
        r['runConfig'].update(duration=.85,dt=.000125,hipRotorInertiaKgM2=.08250280529250277)
        result=native(r,stop_at_assessment=True)
        bottom=next(e for e in result['events'] if e['type']=='compression-stop')
        self.assertGreater(bottom['nativeHipStopImpulseNms'],0)
        self.assertFalse(result['caseMetrics']['landingSuccess'])
        self.assertLess(bottom['t'],.8)


if __name__=='__main__':unittest.main(verbosity=2)
