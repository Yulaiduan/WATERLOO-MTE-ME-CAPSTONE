"""Verify shared scenario laws and actual Pymunk contact/stop cases.

Run app Python verify_contact_cases.py; requires Node, NumPy and Pymunk.
Inputs are unchanged JS geometry plus explicit 1.5 kg wheel, SI scenario controls.
Outputs unittest evidence for ballistic hold, torque work, brakes and refinement.
Experimental numerical checks do not certify hardware impact force or motor peaks.
"""
import math
import unittest
from contact_cases import (CASE_DEFAULTS, resolve_case, initial_conditions, energy_estimate,
                           CaseController, minimum_required_torque, stopping_demand, usable_compression)
from contact_dynamics import simulate_contact, validate_contact_request
import verify_contact
from dynamic_model import R


class ScenarioChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):verify_contact.ContactChecks.setUpClass()
    def request(self,kind,params=None,**case):
        p=verify_contact.ContactChecks().payload(params,dt=.00025,duration=.8)
        p['caseConfig']={**CASE_DEFAULTS,'kind':kind,**case}
        return p
    def test_strict_cases_and_energy_geometry_guard(self):
        request=self.request('landing')
        for key,value in [('landingDropMm',5001),('landingOpenFraction',0),('energyMethod',1),('undersideOffsetMm',-1)]:
            bad={**request,'caseConfig':{**request['caseConfig'],key:value}}
            with self.subTest(key=key),self.assertRaises(ValueError):resolve_case(bad)
        tilted=self.request('landing',{'alpha':15},brakeStrategy='energy-sized')
        with self.assertRaisesRegex(ValueError,'vertical guide'):validate_contact_request(tilted)
        tilted['caseConfig']['brakeStrategy']='entered';validate_contact_request(tilted)
    def test_ballistic_hold_impact_and_reported_torque(self):
        req=self.request('landing');result=simulate_contact(req);m=validate_contact_request(req)
        q,h,x,z=initial_conditions(m,req['caseConfig']);g=m.p['g']
        before=[r for r in result['rows'] if r['t']<.14]
        self.assertLess(max(abs(r['theta2']-q/R) for r in before),1e-8)
        self.assertLess(max(abs(r['wheelZMm']-(z-.5*g*r['t']**2)*1000) for r in before),.18)
        for r in before:self.assertAlmostEqual(r['holdTorqueNm'],-m.spring(q)['torque'],delta=1e-7)
        impact=result['caseMetrics']['impactTimeS'];self.assertAlmostEqual(impact,math.sqrt(.2/g),delta=.0005)
        self.assertTrue(result['caseMetrics']['landingSuccess'])
        self.assertEqual(result['terrain']['polygonsMm'],[])
        self.assertEqual(result['terrain']['translationVelocityMmS'],[0,0,0])
    def test_tilted_hold_cancels_relative_external_force(self):
        req=self.request('landing',{'alpha':15,'loadMode':'global','Fx':12,'Fz':3})
        m=validate_contact_request(req);q,h,x,z=initial_conditions(m,req['caseConfig'])
        controller=CaseController(m,req['caseConfig']);tau=controller.torques(q,0)['motorTorqueNm']
        f=(m.spring(q)['torque']+tau)/m.jacobian(q)
        ax,az=m.axis;fx,fz=m.force;M=m.p['m1']+m.p['m6']
        self.assertAlmostEqual(f+ax*fx+az*fz-m.p['m6']*az*fz/M,0,delta=1e-12)
    def test_springoff_jump_work_cutoff_and_negative_control(self):
        req=self.request('jump',{'springEnabled':False},jumpTorqueNm=100);req['runConfig']['duration']=.5
        r=simulate_contact(req);p=req['params'];expected=100*(p['tc']-p['te'])*R
        self.assertAlmostEqual(r['rows'][-1]['motorWorkJ'],expected,delta=.001)
        self.assertIsNotNone(r['caseMetrics']['takeoffTimeS']);self.assertGreater(r['rows'][-1]['stopDissipationJ'],0)
        self.assertEqual(r['rows'][-1]['motorTorqueNm'],0)
        self.assertAlmostEqual(r['diagnostics']['chassisBodyMassKg'],p['m1'])
        self.assertAlmostEqual(r['diagnostics']['wheelBodyMassKg'],p['m6'])
        req['caseConfig']['jumpTorqueNm']=0;r=simulate_contact(req)
        self.assertIsNone(r['caseMetrics']['takeoffTimeS']);self.assertEqual(r['rows'][-1]['motorWorkJ'],0)
    def test_energy_average_and_bottomout_failure(self):
        req=self.request('landing',{'springEnabled':False},landingBrakeTorqueNm=0)
        m=validate_contact_request(req);case=req['caseConfig'];q,h,x,z=initial_conditions(m,case)
        stroke=m.sites(m.hi)['6'][0][1]-m.sites(q)['6'][0][1]
        expected=m.p['m1']*m.p['g']*(case['landingDropMm']/1000+stroke)/(m.hi-q)
        self.assertAlmostEqual(energy_estimate(m,case)['averageTorqueNm'],expected,delta=1e-10)
        r=simulate_contact(req);self.assertFalse(r['caseMetrics']['landingSuccess'])
        self.assertEqual(r['caseMetrics']['outcome'],'bottom-out-before-arrest')
        req['caseConfig']['landingBrakeTorqueNm']=100;r=simulate_contact(req)
        self.assertTrue(r['caseMetrics']['landingSuccess'])
        req['caseConfig']['landingBrakeLimitNm']=0;r=simulate_contact(req)
        self.assertFalse(r['caseMetrics']['landingSuccess'])
    def test_energy_refinement_and_clearance(self):
        errors=[]
        for dt in (.0005,.00025,.000125):
            req=self.request('jump',{'springEnabled':False},jumpTorqueNm=100);req['runConfig'].update(dt=dt,duration=.5)
            r=simulate_contact(req);errors.append(abs(r['diagnostics']['energyBalanceResidualJ']))
            for row in r['rows']:self.assertAlmostEqual(row['chassisKineticJ'],.5*req['params']['m1']*(row['chassisVelocityMmS']/1000)**2,delta=1e-10)
        self.assertGreater(errors[0],errors[1]);self.assertGreater(errors[1],errors[2])
        req=self.request('landing',undersideOffsetMm=900)
        with self.assertRaisesRegex(ValueError,'Initial chassis'):simulate_contact(req)
        req=self.request('landing',undersideOffsetMm=600);r=simulate_contact(req)
        self.assertEqual(r['diagnostics']['termination'],'underside-contact');self.assertFalse(r['caseMetrics']['landingSuccess'])
        req=self.request('landing',undersideOffsetMm=None);r=simulate_contact(req)
        self.assertIsNone(r['caseMetrics']['minimumUndersideClearanceMm'])
    def test_review_guards_and_usable_energy_stroke(self):
        tilted=self.request('landing',{'alpha':15})
        model=validate_contact_request(tilted)
        self.assertIsNone(stopping_demand(model,model.q0,.1,-1,tilted['caseConfig']))
        reversed_branch=self.request('jump',{'springEnabled':False,'phi0':30,'te':90,'theta2':95,'tc':100})
        with self.assertRaisesRegex(ValueError,'compressed endpoint'):validate_contact_request(reversed_branch)
        req=self.request('landing',{'springEnabled':False},undersideOffsetMm=600)
        model=validate_contact_request(req);q,_,_,_=initial_conditions(model,req['caseConfig'])
        target=usable_compression(model,q,req['caseConfig']);estimate=energy_estimate(model,req['caseConfig'])
        self.assertLess(target,model.hi)
        self.assertAlmostEqual((model.p['rw']/1000-model.sites(target)['6'][0][1])*1000,600,delta=1e-8)
        self.assertAlmostEqual(estimate['availableCompressionRad'],target-q,delta=1e-10)
        with self.assertRaises(ValueError):resolve_case({'caseConfig':None})

    def test_assessment_early_stop_matches_full_first_arrest(self):
        from analytical_contact import simulate_contact as analytical
        for engine,simulate in [('analytical',analytical),('pymunk',simulate_contact)]:
            for torque in (10.9375,12.5):
                req=self.request('landing',landingBrakeTorqueNm=torque)
                req['engine']=engine
                full=simulate(req)
                early=simulate(req,stop_at_assessment=True)
                self.assertLess(early['rows'][-1]['t'],full['rows'][-1]['t'])
                arrest=next((event['t'] for event in full['events'] if event['type']=='chassis-arrest'),None)
                failures=[event['t'] for event in full['events'] if event['type'] in ('compression-stop','underside-contact')]
                criterion=arrest is not None and not any(time<=arrest for time in failures)
                self.assertEqual(early['caseMetrics']['landingSuccess'],criterion)
                self.assertEqual(early['diagnostics']['termination'],'assessment-outcome')
                self.assertEqual(early['caseMetrics']['landingSuccess'],torque==12.5)

    def test_bounded_search_reports_tested_bracket(self):
        req=self.request('landing',{'springEnabled':False});result=minimum_required_torque(req,simulate_contact,iterations=3)
        self.assertTrue(result['feasible']);self.assertGreaterEqual(result['torqueNm'],result['lowerBoundNm'])
        self.assertEqual(result['evaluations'],8);self.assertEqual(len(result['trials']),8)
        req['caseConfig']['landingBrakeLimitNm']=0;result=minimum_required_torque(req,simulate_contact,iterations=3)
        self.assertFalse(result['feasible']);self.assertIsNone(result['torqueNm'])


if __name__=='__main__':unittest.main(verbosity=2)
