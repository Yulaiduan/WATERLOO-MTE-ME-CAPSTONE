"""Validate table-study capture and AB load reconstruction against Jon V4 statics.

Run app Python verify_table_landing_study.py. Inputs retained V4 geometry in
mm/deg/kg and stationary-flat-floor actual analytical/Pymunk fixtures in SI.
Outputs unittest evidence; no files/profile writes or impact-peak certification.
Static oracle and interval body momentum check signs, lever units and inertia
subtraction independently of the study's numerical torque-search comparison.
"""
import copy
import json
import math
from pathlib import Path
import subprocess
import unittest

import table_landing_study as study
from contact_cases import validate_contact_request

ROOT=Path(__file__).resolve().parent
BASE=json.loads((ROOT/'saved-configurations/vsl-v4-nominal-alpha0.json').read_text())


class StudyChecks(unittest.TestCase):
    def test_exact_table_cases_full_stroke_and_explicit_inputs(self):
        for case in study.CASES:
            for engine in study.ENGINES:
                p=study.payload(BASE,case,engine,'off',.000125,1000,.5,.8,1.5)
                self.assertEqual(p['params']['m1']*4,45)
                self.assertEqual(p['params']['m6'],.5)
                self.assertEqual(p['caseConfig']['landingOpenFraction'],1)
                self.assertEqual(p['params']['tc']-p['params']['te'],65)
                self.assertEqual(p['caseConfig']['landingDropMm'],case[1])
                self.assertEqual(p['params']['alpha'],case[2])
                self.assertFalse(p['params']['springEnabled'])
                self.assertNotIn('actuatorConfig',p)

    def test_gcomp_scales_force_law_without_rotating_or_altering_route(self):
        before=copy.deepcopy(BASE)
        for case in study.CASES:
            p=study.payload(BASE,case,'analytical','gcomp',.000125,1000,.5,.8,1.5)['params']
            ratio=(11.25/8.75)*math.cos(math.radians(case[2]))
            self.assertAlmostEqual(p['springK']/BASE['params']['springK'],ratio)
            self.assertAlmostEqual(p['p0']/BASE['params']['p0'],ratio)
            for k in ('Su','Sv','hornR','rs','nu'):self.assertEqual(p[k],BASE['params'][k])
        self.assertEqual(BASE,before)

    def test_both_actual_static_engines_match_original_ab_spans_and_momentum(self):
        for alpha in (0,20):
            for engine,sim in study.ENGINES.items():
                with self.subTest(alpha=alpha,engine=engine):
                    case=('static',0,alpha,0,0)
                    p=study.payload(BASE,case,engine,'off',.000125,1000,.5,0,.12)
                    p['params']['theta2']=135;p['caseConfig']['kind']='terrain-stability'
                    p['runConfig']['inputHeightMm']=0
                    m=validate_contact_request(p);p['runConfig']['hipTorqueNm']=m.grounded_gravity(m.q0)
                    result=sim(p);intervals=study.belt_intervals(p,result)
                    oracle={**p['params'],'loadMode':'yz','Fy':0,'Fz':m.total_mass*m.p['g']}
                    js="const fs=require('fs'),vm=require('vm');vm.runInThisContext(fs.readFileSync('reference-v4.js','utf8'));const p=JSON.parse(process.argv[1]);const s=VSLStatic.solve(p,p.theta2);console.log(JSON.stringify({tight:Math.max(s.ab.U,s.ab.L),torque:s.tau2}));"
                    expected=json.loads(subprocess.check_output(['node','-e',js,json.dumps(oracle)],cwd=ROOT,text=True))
                    stable=[r for r in intervals if r['startS']>=.02]
                    self.assertTrue(stable)
                    self.assertLess(max(abs(r['tightN']-expected['tight']) for r in stable),.1)
                    self.assertLess(max(abs(r['verticalMomentumResidualN']) for r in stable),.001)
                    # Native contact has finite positional slop/bias. Verify a
                    # physical 10-micrometre holding bound, not exact pose parity.
                    start=result['rows'][0]
                    self.assertLess(max(abs(r['chassisZMm']-start['chassisZMm']) for r in result['rows']),.01)
                    self.assertLess(max(abs(r['wheelZMm']-start['wheelZMm']) for r in result['rows']),.01)
                    self.assertAlmostEqual(p['runConfig']['hipTorqueNm'],expected['torque'],delta=1e-10)


if __name__=='__main__':unittest.main(verbosity=2)
