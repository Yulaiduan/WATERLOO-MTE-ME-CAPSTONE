"""Check nonideal-study assumptions, physical signs and honest terrain metrics.

Run app Python verify_nonideal_study.py; optional --real executes short matched
analytical/native flat heave runs. Inputs are explicit SI motor examples and
mm/degree synthetic metrics. Outputs unittest results, no live profile writes.
These checks do not certify measured hardware, contact shock or vehicle stability.
"""
import copy
import math
import sys
import unittest

import nonideal_study as study
from motor_model import Motor, DEFAULTS

REAL='--real' in sys.argv
if REAL:sys.argv.remove('--real')


class StudyChecks(unittest.TestCase):
    def test_config_requires_explicit_inputs_and_bounds(self):
        c=study.default_config();self.assertEqual(study.validate_config(c),c)
        for name,value in (('dt',float('nan')),('alphaDeg',46),('ratios',[20,20]),('terrains',[]),('evaluationStartS',10)):
            changed=copy.deepcopy(c);changed[name]=value
            with self.subTest(name=name),self.assertRaises(ValueError):study.validate_config(changed)
        c.pop('shaftCoulombNm')
        with self.assertRaises(ValueError):study.validate_config(c)

    def test_constant_coulomb_opposes_motion_and_viscous_scales_with_speed(self):
        c={**DEFAULTS,'enabled':True,'gearRatio':20.,'rotorInertiaKgM2':.000825,
            'coggingAmplitudeNm':0.,'coulombFrictionNm':.05,'viscousFrictionNms':.0008,'frictionVelocityScaleRadS':.01}
        motor=Motor.resolve(c)
        for qd in (-2.,-1.,1.,2.):
            a=motor.motor_state(.5,qd,0);b=motor.motor_state(1.25,qd,0)
            self.assertAlmostEqual(a['jointFrictionNm'],b['jointFrictionNm'])
            self.assertLess(a['jointFrictionNm']*qd,0)
            self.assertAlmostEqual(a['coulombLossPowerW'],.05*abs(20*qd))
            self.assertAlmostEqual(a['viscousLossPowerW'],.0008*(20*qd)**2)
            self.assertEqual(a['jointCoggingNm'],0)
        slow=motor.motor_state(0,1,0);fast=motor.motor_state(0,2,0)
        self.assertAlmostEqual(fast['viscousLossPowerW']/slow['viscousLossPowerW'],4)
        self.assertAlmostEqual(motor.reflected_inertia,400*.000825)

    @unittest.skipUnless('gearboxInputInertiaKgM2' in DEFAULTS,'Requires integrated explicit gearbox inertia motor schema')
    def test_exact_pair_full_stroke_and_no_doublecounted_gear_inertia(self):
        c=study.default_config()
        for kind in ('jump','landing','terrain-stability'):
            a=study.make_payload(c,kind,20.,'losses','analytical',c['terrains'][2] if kind=='terrain-stability' else None)
            b=study.make_payload(c,kind,20.,'losses','pymunk',c['terrains'][2] if kind=='terrain-stability' else None)
            a.pop('engine');b.pop('engine');self.assertEqual(a,b)
            self.assertEqual(a['runConfig']['hipRotorInertiaKgM2'],0)
            self.assertEqual(a['caseConfig']['landingOpenFraction'],1)
            self.assertEqual(a['params']['tc']-a['params']['te'],65)
            self.assertEqual(4*(a['params']['m1']+a['params']['m2']+a['params']['m3']+a['params']['m6']),55)
            self.assertAlmostEqual(Motor.resolve(a['motorConfig']).reflected_inertia,20**2*(.000825+.0001))
            self.assertEqual(a['motorConfig']['coggingAmplitudeNm'],0)

    def fixture(self):
        c=study.default_config();c.update(evaluationStartS=1.,terrainDurationS=3.,outputHz=10.)
        request=study.make_payload(c,'terrain-stability',20.,'reference','analytical',c['terrains'][3])
        rows=[]
        for t in (0.,1.,2.,3.):
            rows.append(dict(t=t,chassisZMm=600+20*t,rideTargetHeightMm=600+20*t,chassisClearanceMm=500.,
                chassisVelocityMmS=20.,velocityDegS=0.,motorWorkJ=0.,motorDissipatedJ=0.,springEnergyJ=0.,gravityEnergyJ=0.,
                rotorKineticJ=0.,motorTorqueNm=0.,contactNormalForceN=130.,actuatorLimited=False))
        result=dict(rows=rows,events=[],diagnostics=dict(termination='duration',finiteLinkDynamics=True,reflectedHipInertiaKgM2=0.,energyBalanceResidualJ=0.,maxPenetrationMm=0.,maxConstraintPositionErrorMm=0.),
            caseMetrics=dict(outcome='completed-observation',minimumUndersideClearanceMm=500.,landingSuccess=None),targetObservations={})
        return c,request,result

    def test_grade_world_variance_does_not_equal_tracking_variance(self):
        c,request,result=self.fixture();m=study.summarize(request,result,c)['terrainMetrics']
        self.assertTrue(m['fullWindowObserved']);self.assertTrue(m['heaveTestPassed'])
        self.assertAlmostEqual(m['heightMm']['variance'],800/3)
        self.assertEqual(m['trackingErrorMm']['variance'],0)
        self.assertEqual(m['trackingErrorMm']['rms'],0)
        self.assertEqual(m['saturationFraction'],0)

    def test_partial_or_numerical_failure_is_not_stable_comparison(self):
        c,request,result=self.fixture();result['rows'].pop()
        m=study.summarize(request,result,c)['terrainMetrics']
        self.assertFalse(m['usableComparison']);self.assertFalse(m['heaveTestPassed']);self.assertEqual(m['status'],'incomplete-window')
        c,request,result=self.fixture();result['diagnostics']['termination']='contact-penetration-limit'
        m=study.summarize(request,result,c)['terrainMetrics']
        self.assertEqual(m['status'],'numerical-failure');self.assertFalse(m['usableComparison'])
        c,request,result=self.fixture();result['events']=[dict(type='compression-stop',t=2.)]
        m=study.summarize(request,result,c)['terrainMetrics']
        self.assertEqual(m['status'],'physical-limit');self.assertFalse(m['heaveTestPassed'])

    @unittest.skipUnless(REAL,'Use --real for actual paired finite-link flat runs')
    def test_actual_pair_holds_flat_height_and_captures_hardware_limits(self):
        c=study.default_config();c.update(terrainDurationS=.3,evaluationStartS=.1,outputHz=100.,dt=.00025)
        captured=[]
        for engine,sim in study.ENGINES.items():
            request=study.make_payload(c,'terrain-stability',20.,'reference',engine,c['terrains'][0])
            result=sim(request);m=study.summarize(request,result,c)
            self.assertTrue(m['finiteLinkDynamics']);self.assertTrue(m['numericallyResolved'])
            self.assertTrue(m['terrainMetrics']['fullWindowObserved'])
            self.assertLess(m['terrainMetrics']['trackingErrorMm']['maximumAbsolute'],.1)
            self.assertLessEqual(m['peakDeliveredTorqueNm'],250)
            self.assertEqual(request['motorConfig']['coggingAmplitudeNm'],0)
            captured.append(result)
        for r in captured:self.assertIn('actuatorConfig',r['snapshot'])


if __name__=='__main__':unittest.main()
