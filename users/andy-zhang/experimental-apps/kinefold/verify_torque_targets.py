"""Verify target sizing semantics with controlled outcomes and real engines.

Run app .venv Python verify_torque_targets.py. Inputs saved V4 + explicit1.5kg
wheel, target mm and torque Nm; outputs unittest results. Tests observation
sampling independence, engine-specific feasibility and non-proven boundaries;
they do not certify motor peaks, global minima or post-arrest safety.
"""
import copy
import unittest
from torque_targets import TargetObservation, resolve_targets, target_torque_search
from contact_cases import CASE_DEFAULTS
from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as pymunk
import verify_contact


class TargetChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_contact.ContactChecks.setUpClass()

    def request(self, kind):
        p=verify_contact.ContactChecks().payload(dt=.00025,duration=2)
        p['caseConfig']={**CASE_DEFAULTS,'kind':kind}
        p['torqueTargetConfig']=resolve_targets()
        return p

    def test_strict_targets_and_unknown_failures(self):
        for value in ({}, {'jumpHeightMm':float('nan')}, {**resolve_targets(),'landingClearanceMm':-1}):
            with self.assertRaises(ValueError):resolve_targets(value)
        p=self.request('jump');p['torqueTargetConfig']=None
        with self.assertRaises(ValueError):target_torque_search(p,lambda p:None)
        p=self.request('landing')
        def broken(_):raise ValueError('Unresolved numerical contact')
        r=target_torque_search(p,broken)
        self.assertEqual(r['status'],'indeterminate');self.assertIsNone(r['lowerBoundNm'])
        self.assertTrue(all(t['status']=='numerical-failure' for t in r['trials']))

    def test_observation_freezes_and_excludes_chatter(self):
        c={**CASE_DEFAULTS,'kind':'jump'};o=TargetObservation(c,.001)
        o.step(0,.5,0,.2,0,.2,True,[])
        o.step(.001,.501,1,.20000001,1,.2,False,[])
        self.assertIsNone(o.takeoff)
        o.step(.01,.51,1,.21,1,.2,False,[])
        o.step(.02,.515,-.1,.215,-.1,.2,False,[])
        frozen=o.result();o.step(.1,1,1,1,1,.2,False,[])
        self.assertEqual(o.result(),frozen);self.assertAlmostEqual(frozen['flightRiseMm'],5)
        o=TargetObservation(c,.001);o.step(0,.5,0,.2,0,.2,True,[])
        o.step(.01,.51,1,.21,1,.2,False,[]);o.step(.015,.511,.1,.2,0,.2,True,[])
        o.step(.02,.52,-1,.22,-1,.2,False,[])
        self.assertFalse(o.result()['genuineFirstFlight'])

    def test_adaptive_exploration_without_false_failing_boundary(self):
        p=self.request('jump')
        def fake(request):
            torque=request['caseConfig']['jumpTorqueNm']
            return dict(diagnostics={'termination':'duration'},caseMetrics={},targetObservations={
                'genuineFirstFlight':torque>=10,'flightRiseMm':100 if torque>=10 else None})
        r=target_torque_search(p,fake)
        self.assertLess(r['torqueNm'],20);self.assertIsNone(r['lowerBoundNm'])
        self.assertTrue(any(t['status']=='insufficient-duration' for t in r['trials']))

    def test_step_observations_full_early_and_output_schedule_agreement(self):
        for engine in (analytical,pymunk):
            for kind in ('jump','landing'):
                p=self.request(kind);p.pop('torqueTargetConfig')
                full=engine(p);early=engine(p,stop_at_assessment=True)
                q=copy.deepcopy(p);q['runConfig']['outputHz']=7
                sparse=engine(q,stop_at_assessment=True)
                with self.subTest(engine=engine.__module__,kind=kind):
                    self.assertEqual(full['targetObservations'],early['targetObservations'])
                    a,b=sparse['targetObservations'],early['targetObservations']
                    self.assertEqual(a['genuineFirstFlight'],b['genuineFirstFlight'])
                    if kind=='jump':
                        self.assertLess(abs(a['flightRiseMm']-b['flightRiseMm']),1.)
                        self.assertEqual(a['flightRiseMm']>=100,b['flightRiseMm']>=100)
                        print(engine.__module__,kind,'7Hz-vs-100Hz rise difference mm',abs(a['flightRiseMm']-b['flightRiseMm']))
                    else:
                        self.assertLess(abs(a['minimumClearanceThroughArrestMm']-b['minimumClearanceThroughArrestMm']),1.)
                        self.assertEqual(a['minimumClearanceThroughArrestMm']>=50,b['minimumClearanceThroughArrestMm']>=50)
                        print(engine.__module__,kind,'7Hz-vs-100Hz clearance difference mm',abs(a['minimumClearanceThroughArrestMm']-b['minimumClearanceThroughArrestMm']))
                    if kind=='jump':
                        o=early['targetObservations'];self.assertTrue(o['genuineFirstFlight']);self.assertGreater(o['flightRiseMm'],100)
                        # Chassis follows a ballistic arc after extension/takeoff.
                        self.assertAlmostEqual(o['firstFlightApex']['chassisZMm']-o['takeoff']['chassisZMm'],o['flightRiseMm'])
                    else:self.assertGreater(early['targetObservations']['minimumClearanceThroughArrestMm'],50)

    def test_motor_basis_search_preserves_joint_equivalence(self):
        from motor_model import DEFAULTS
        for engine in (analytical,pymunk):
            joint=self.request('jump')
            shaft=copy.deepcopy(joint)
            shaft['motorConfig']={**DEFAULTS,'enabled':True,'gearRatio':10,'commandBasis':'motor'}
            shaft['torqueTargetConfig']['jumpTorqueLimitNm']=20
            a=target_torque_search(joint,lambda r:engine(r,stop_at_assessment=True),iterations=1)
            b=target_torque_search(shaft,lambda r:engine(r,stop_at_assessment=True),iterations=1)
            self.assertTrue(a['feasible'] and b['feasible'])
            self.assertEqual(b['commandBasis'],'motor')
            self.assertAlmostEqual(a['torqueNm'],10*b['torqueNm'])
            self.assertAlmostEqual(a['bestTrial']['achievedMm'],b['bestTrial']['achievedMm'])

    def test_actual_bounded_sizing_both_engines_and_clearance(self):
        for engine in (analytical,pymunk):
            for kind in ('jump','landing'):
                p=self.request(kind)
                result=target_torque_search(p,lambda r:engine(r,stop_at_assessment=True),iterations=2)
                with self.subTest(engine=engine.__module__,kind=kind):
                    self.assertTrue(result['feasible']);self.assertLessEqual(result['evaluations'],7)
                    self.assertGreaterEqual(result['bestTrial']['achievedMm'],100 if kind=='jump' else 50)
                    if kind=='landing':
                        p['torqueTargetConfig']['landingClearanceMm']=1000
                        failed=target_torque_search(p,lambda r:engine(r,stop_at_assessment=True),iterations=0)
                        self.assertFalse(failed['feasible'])

    def test_short_horizon_is_indeterminate_in_both_engines(self):
        for engine in (analytical,pymunk):
            for kind in ('jump','landing'):
                p=self.request(kind);p['runConfig']['duration']=.05
                r=target_torque_search(p,lambda q:engine(q,stop_at_assessment=True),iterations=0)
                self.assertFalse(r['feasible'])
                self.assertEqual(r['status'],'indeterminate')
                self.assertIsNone(r['lowerBoundNm'])
                self.assertTrue(all(t['status']=='insufficient-duration' for t in r['trials']))


if __name__=='__main__':unittest.main()
