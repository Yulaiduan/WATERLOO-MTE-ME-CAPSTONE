"""Check the bounded workflow example's source limits and honest comparison rules.

Run app Python: python verify_workflow_example.py. Inputs are the three retained
catalogue examples and small synthetic paired metrics (mm, Nm, kg m2). Outputs
unittest results; no physics runs, GUI or profile writes. Tests validate data and
ranking contracts, not real motor performance or globally optimal control.
"""
import copy
import json
import unittest

import workflow_example as example
from actuation_limits import torque_limit
from motor_model import Motor


class WorkflowExampleTests(unittest.TestCase):
    def test_config_is_small_explicit_and_bounded(self):
        c=example.default_config();self.assertEqual(example.validate_config(c),c)
        self.assertEqual(len(c['candidateIds']),3)
        self.assertEqual(c['terrain']['seed'],481)
        for key,value in (('candidateIds',['strong-10','strong-10']),('candidateIds',['unknown']),
            ('exampleCandidateId','unknown'),('dt',float('nan')),('terrainTieRmsMm',-.1)):
            changed=copy.deepcopy(c);changed[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):example.validate_config(changed)
        changed=copy.deepcopy(c);changed.pop('gearboxInputInertiaKgM2')
        with self.assertRaises(ValueError):example.validate_config(changed)

    def test_source_caps_and_reflected_inertia_are_applied_once(self):
        c=example.default_config();catalog=json.loads((example.ROOT/'motor-gearbox-catalog.json').read_text(encoding='utf-8'))
        expected={'light-10':87.3,'strong-10':164.9,'strong-20':250.}
        for candidate_id in c['candidateIds']:
            candidate=example.selected_hardware(c,catalog,candidate_id);hw=candidate['hardware']
            for kind in example.KINDS:
                a=example.make_payload(c,candidate,kind,'analytical');b=example.make_payload(c,candidate,kind,'pymunk')
                a.pop('engine');b.pop('engine');self.assertEqual(a,b)
                self.assertEqual(a['params']['m1'],45/4)
                self.assertEqual(a['params']['m2'],1);self.assertEqual(a['params']['m3'],1);self.assertEqual(a['params']['m6'],.5)
                self.assertEqual(a['caseConfig']['landingOpenFraction'],1)
                self.assertEqual(a['params']['tc']-a['params']['te'],65)
                self.assertEqual(a['motorConfig']['coggingAmplitudeNm'],0)
                self.assertEqual(a['motorConfig']['coulombFrictionNm'],.05)
                self.assertEqual(a['runConfig']['hipRotorInertiaKgM2'],0)
                self.assertAlmostEqual(Motor.resolve(a['motorConfig']).reflected_inertia,hw['reflectedInertiaKgM2'])
                self.assertEqual(a['actuatorConfig']['peakShaftNm'],candidate['source']['shaftPeakNm'])
            limit=torque_limit(hw['actuatorConfig'],0,1e8)['actuatorAvailableNm']
            self.assertAlmostEqual(limit,expected[candidate_id])
            self.assertAlmostEqual(hw['gearboxInputInertiaKgM2'],.0001)
            self.assertIn('Missing gearbox input inertia explicitly substituted',hw['assumptionFlags'])

    def fixture(self,candidate_id,kind,values,*,resolved=True,passes=True):
        records=[]
        for engine,value in zip(example.study.ENGINES,values):
            m=dict(numericallyResolved=resolved,jumpObserved=True,jumpCOMRiseMm=value,jumpTargetReached=value>=2000,
                landingSuccessAboveClearance=passes,minClearanceMm=value,
                terrainMetrics=dict(heaveTestPassed=passes,trackingErrorMm=dict(rms=value)))
            records.append(dict(candidateId=candidate_id,case=kind,engine=engine,metrics=m))
        return records

    def test_both_engines_required_and_worse_engine_sets_rank(self):
        c=example.default_config();r=self.fixture('light-10','jump',[3000,500])+self.fixture('strong-10','jump',[1000,990])
        out=example.conditional_leaders(r,c)
        self.assertEqual(out['jump']['leaderIds'],['strong-10'])
        self.assertEqual(out['jump']['eligible'][0]['score'],990)
        self.assertEqual(out['jump']['targetMetIds'],[])
        self.assertEqual(out['allTargets']['passingIds'],[])
        r.pop();out=example.conditional_leaders(r,c)
        self.assertEqual(out['jump']['leaderIds'],['light-10'])
        self.assertIn('Matched engine pair not completed',[x['reason'] for x in out['jump']['excluded']])

    def test_unresolved_and_failed_cases_cannot_win(self):
        c=example.default_config()
        r=self.fixture('light-10','landing',[500,510],passes=False)
        r+=self.fixture('strong-10','landing',[1000,1010],resolved=False)
        r+=self.fixture('strong-20','landing',[300,310])
        out=example.conditional_leaders(r,c)['landing']
        self.assertEqual(out['leaderIds'],['strong-20'])
        self.assertEqual(out['targetMetIds'],['strong-20'])
        self.assertEqual(len(out['excluded']),2)

    def test_small_terrain_differences_remain_a_tie(self):
        c=example.default_config()
        r=self.fixture('light-10','terrain-stability',[1.65,1.66])
        r+=self.fixture('strong-10','terrain-stability',[1.68,1.69])
        r+=self.fixture('strong-20','terrain-stability',[1.70,1.72])
        out=example.conditional_leaders(r,c)['terrain-stability']
        self.assertEqual(out['status'],'tie-within-resolution-band')
        self.assertEqual(set(out['leaderIds']),set(c['candidateIds']))
        self.assertEqual(out['eligible'][0]['score'],1.66)

    def test_all_failed_landings_have_no_leader(self):
        c=example.default_config();r=[]
        for candidate_id in c['candidateIds']:r+=self.fixture(candidate_id,'landing',[500,500],passes=False)
        out=example.conditional_leaders(r,c)
        self.assertEqual(out['landing']['status'],'no-eligible-combination')
        self.assertEqual(out['landing']['leaderIds'],[])
        self.assertEqual(out['allTargets']['status'],'none-demonstrated')


if __name__=='__main__':unittest.main()
