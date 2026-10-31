"""Check bounded gear-response requests, weighted metrics and qualified results.

Run app Python: python verify_gear_response_study.py. Inputs synthetic saved
mm/second response rows and exact catalogue designs; outputs unittest evidence,
no files or physics integrations. Construction checks require updated pinned
contact backend; they skip explicitly until that backend is integrated. No GUI,
profile writes, hardware qualification or invented contact trajectory.
"""
import argparse
import copy
import json
import math
import unittest

import gear_response_study as response
from actuation_limits import ACTUATOR_DEFAULTS
from motor_model import Motor

BACKEND_READY='rideTargetStepMm' in ACTUATOR_DEFAULTS


def rows(end=.8,contact=True):
    result=[]
    for i in range(round(end*100)+1):
        t=i/100;fraction=min(1.,max(0.,(t-.1)/.2))
        result.append(dict(t=t,rideTargetHeightMm=600. if t<.1 else 625.,
            chassisZMm=600+25*fraction,contactNormalForceN=100. if contact else 0.))
    return result


class GearResponseStudy(unittest.TestCase):
    def test_strict_small_plan_and_unknowns(self):
        c=response.default_config();self.assertEqual(response.validate_config(c),c)
        a=argparse.Namespace(case=None,speed=None,engine=None)
        planned=list(response.jobs(c,[dict(id=k) for k in c['candidateIds']],a))
        self.assertEqual(len(planned),36)
        self.assertEqual(sum(x[1]=='floating-terrain' for x in planned),24)
        self.assertEqual(sum(x[1]=='pinned-terrain' for x in planned),6)
        self.assertEqual(sum(x[1]=='height-step' for x in planned),6)
        for key,value in [('speedsMps',[1,2,3,4,5]),('speedsMps',[1,1]),
            ('candidateIds',['invented']),('hipBeltRatio',3.01),
            ('retainFloatingSpeedsMps',[1,3,6]),('heightStepTimeS',1.9),
            ('thresholds',dict(c['thresholds'],minContactFraction=1.1))]:
            bad=copy.deepcopy(c);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):response.validate_config(bad)

    def test_step_crossings_and_sustained_settling(self):
        c=response.default_config();c['stepDurationS']=.8
        m=response.step_metrics(rows(),c)
        self.assertEqual(m['status'],'settled')
        self.assertAlmostEqual(m['delayTo10PercentS'],.02)
        self.assertAlmostEqual(m['riseTime10To90S'],.16)
        self.assertAlmostEqual(m['timeTo90PercentS'],.18)
        self.assertAlmostEqual(m['settlingTimeS'],.196)
        self.assertEqual(m['overshootPercent'],0)
        self.assertEqual(m['settlingBandMm'],.5)

    def test_step_metrics_do_not_pass_incomplete_contact_loss_or_short_hold(self):
        c=response.default_config();c['stepDurationS']=.8
        for data,resolved,status in [(rows(.5),True,'incomplete-window'),
            (rows(contact=False),True,'contact-loss'),(rows(),False,'numerical-failure')]:
            m=response.step_metrics(data,c,resolved)
            self.assertEqual(m['status'],status);self.assertIsNone(m['riseTime10To90S'])
            self.assertIsNone(m['settlingTimeS'])
        c['stepDurationS']=.35
        short=response.step_metrics(rows(.35),c)
        self.assertEqual(short['status'],'not-settled-within-observation')
        self.assertIsNone(short['settlingTimeS'])

    def test_unreached_step_and_overshoot_are_observed_not_extrapolated(self):
        c=response.default_config();c['stepDurationS']=.8
        limited=rows()
        for r in limited:r['chassisZMm']=600+(r['chassisZMm']-600)/2
        m=response.step_metrics(limited,c)
        self.assertEqual(m['status'],'target-not-reached');self.assertIsNone(m['riseTime10To90S'])
        self.assertIsNone(m['settlingTimeS'])
        no_command=rows()
        for r in no_command:r['rideTargetHeightMm']=600
        m=response.step_metrics(no_command,c)
        self.assertEqual(m['status'],'step-command-not-applied');self.assertIsNone(m['riseTime10To90S'])
        over=rows();over[40]['chassisZMm']=630
        m=response.step_metrics(over,c)
        self.assertAlmostEqual(m['overshootPercent'],20)
        self.assertTrue(m['settlingObserved'])

    def test_signed_force_integral_keeps_absolute_and_dynamic_offset(self):
        data=[dict(t=0,pin=10),dict(t=.1,pin=11),dict(t=1,pin=20)]
        m=response.signed_moments(data,0,1,lambda r:r['pin'])
        self.assertAlmostEqual(m['mean'],15)
        self.assertEqual(m['minimum'],10);self.assertEqual(m['maximum'],20)
        d=response.signed_moments(data,0,1,lambda r:r['pin']-15)
        self.assertAlmostEqual(d['rms'],math.sqrt(100/12))
        self.assertGreater(m['rms'],d['rms'])

    def test_highest_tested_speed_requires_both_engines_and_exposes_holes(self):
        c=response.default_config();c['candidateIds']=['gear-10'];c['speedsMps']=[1.,3.,6.,9.];records=[]
        for v in c['speedsMps']:
            for engine in response.study.ENGINES:
                records.append(dict(candidateId='gear-10',case='floating-terrain',speedMps=v,
                    engine=engine,metrics=dict(numericallyResolved=True,responseMetrics=dict(passes=v!=6,
                        failureReasons=['contact-fraction'] if v==6 else []))))
        m=response.rank_tested_speeds(records,c)[0]
        self.assertEqual(m['highestPassingTestedSpeedMps'],9)
        self.assertEqual(m['nonpassingTestedSpeedsBelowHighestPass'],[6])
        records=[r for r in records if not(r['speedMps']==9 and r['engine']=='pymunk')]
        m=response.rank_tested_speeds(records,c)[0]
        self.assertEqual(m['highestPassingTestedSpeedMps'],3)
        self.assertEqual(m['nextHigherNonpassingTestedSpeedMps'],6)
        self.assertEqual(m['unresolvedOrIncompleteSpeedsMps'],[9])
        self.assertEqual(m['tested'][-1]['status'],'incomplete-pair')

    def test_capture_and_output_guard(self):
        h=response.fingerprints()
        for name in ('gear_response_study.py','terrain_speed_study.py','motor_model.py',
            'actuation_limits.py','analytical_contact.py','contact_dynamics.py'):
            self.assertEqual(len(h[name]),64)
        with self.assertRaises(ValueError):response.app_local(response.ROOT.parent/'outside')

    @unittest.skipUnless(BACKEND_READY,'Pinned contact backend has not been integrated in this worktree.')
    def test_exact_source_hardware_requests_and_real_contact(self):
        c=response.default_config();catalog=json.loads((response.ROOT/'motor-gearbox-catalog.json').read_text())
        for key,total in [('gear-5',10),('gear-10',20),('gear-20',40)]:
            candidate=response.selected_hardware(c,catalog,key)
            self.assertEqual(candidate['totalReduction'],total)
            self.assertAlmostEqual(candidate['hardware']['reflectedInertiaKgM2'],
                total**2*(candidate['hardware']['rotorInertiaKgM2']+candidate['hardware']['gearboxInputInertiaKgM2']))
            for case in response.CASES:
                p=response.make_payload(c,candidate,case,'analytical',3 if case!='height-step' else None)
                native=response.make_payload(c,candidate,case,'pymunk',3 if case!='height-step' else None)
                a=copy.deepcopy(p);b=copy.deepcopy(native);a.pop('engine');b.pop('engine');self.assertEqual(a,b)
                self.assertEqual(p['contactConfig']['mode'],'terrain-contact')
                self.assertEqual(p['contactConfig']['drive'],'free')
                self.assertEqual(p['runConfig']['fixture'],'pinned-chassis' if case=='pinned-terrain' else 'floating-chassis')
                self.assertEqual(p['actuatorConfig']['rideTargetStepMm'],25 if case=='height-step' else 0)
                self.assertEqual(p['runConfig']['inputSpeedMmS'],0 if case=='height-step' else 3000)
                self.assertAlmostEqual(Motor.resolve(p['motorConfig']).reflected_inertia,candidate['hardware']['reflectedInertiaKgM2'])


if __name__=='__main__':unittest.main()
