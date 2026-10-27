"""Check signed work and contact/arrest observations in both actual engines.

Run app Python verify_contact_work.py; needs Node and the app Pymunk environment.
Inputs are explicit copied builder mm/deg/kg/N, SI run/motor/contact cases.
Outputs unittest results and numerical first-contact/arrest work evidence.
Checks independent conservative work identities and bookkeeping/refinement only;
experimental rigid quarter models do not establish tire or hardware survival.
"""
import copy
import json
import math
import unittest
from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as pymunk
from contact_cases import CASE_DEFAULTS, validate_contact_request
from motor_model import DEFAULTS as MOTOR_DEFAULTS
import verify_contact


class WorkChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_contact.ContactChecks.setUpClass()

    def request(self, **case):
        request=verify_contact.ContactChecks().payload(dt=.00025,duration=1.,outputHz=17)
        request['caseConfig']={**CASE_DEFAULTS,'kind':'landing','landingDropMm':2000,
            'landingBrakeTorqueNm':260,'landingBrakeLimitNm':400,**case}
        return request

    def engines(self,request):
        for name,engine in (('analytical',analytical),('pymunk',pymunk)):
            yield name,engine({**copy.deepcopy(request),'engine':name})

    def test_actual_contact_does_not_clamp_chassis_and_step_events_survive_sparse_output(self):
        for name,result in self.engines(self.request()):
            with self.subTest(engine=name):
                impact=next(e for e in result['events'] if e['type']=='first-contact')
                arrest=next(e for e in result['events'] if e['type']=='chassis-arrest')
                self.assertGreater(arrest['t']-impact['t'],.05)
                self.assertLess(impact['postImpulseChassisVelocityMmS'],-6000)
                self.assertLess(abs(impact['postImpulseWheelVelocityZMmS']),abs(impact['preImpulseWheelVelocityZMmS']))
                self.assertLess(abs(impact['contactGapMm']),abs(impact['preImpulseWheelVelocityZMmS'])*result['runConfig']['dt']+1e-5)
                self.assertLess(arrest['beforeStepChassisVelocityMmS'],0)
                self.assertGreaterEqual(arrest['afterStepChassisVelocityMmS'],0)
                self.assertGreater(impact['state']['chassisKineticJ'],150)
                self.assertGreater(arrest['sinceContact']['springStoredJ'],0)
                self.assertGreater(arrest['sinceContact']['motorRemovedJ'],100)
                self.assertTrue(result['caseMetrics']['landingSuccess'])
                self.assertTrue(any(abs(r['t']-impact['t'])>1e-7 for r in result['rows']))
                self.assertTrue(all(r['contactSpringStoredJ'] is None for r in result['rows'] if r['t']<impact['t']))
                json.dumps(result,allow_nan=False)
                print(name,'contact/arrest',impact['t'],arrest['t'],'post-contact chassis/wheel mm/s',impact['postImpulseChassisVelocityMmS'],impact['postImpulseWheelVelocityZMmS'],'spring/motor J',arrest['sinceContact']['springStoredJ'],arrest['sinceContact']['motorRemovedJ'])

    def test_independent_force_payout_and_motor_angle_integrals_all_spring_laws(self):
        for law in ('v4','constant','off'):
            request=self.request();request['params'].update(springLaw='v4' if law=='off' else law,springEnabled=law!='off')
            for name,result in self.engines(request):
                with self.subTest(engine=name,law=law):
                    impact=next(e for e in result['events'] if e['type']=='first-contact')
                    arrest=next(e for e in result['events'] if e['type']=='chassis-arrest')
                    a,b=impact['state'],arrest['state'];dl=(b['springCablePayoutMm']-a['springCablePayoutMm'])/1000
                    expected=0 if law=='off' else a['Fs']*dl+.5*(request['params']['springK']*1000 if law=='v4' else 0)*dl*dl
                    self.assertAlmostEqual(arrest['sinceContact']['springStoredJ'],expected,delta=1e-10)
                    self.assertAlmostEqual(arrest['sinceContact']['motorRemovedJ'],260*(b['hipAngleRad']-a['hipAngleRad']),delta=1e-9)
                    kinetic=.5*request['params']['m1']*((b['chassisVelocityMmS']/1000)**2-(a['chassisVelocityMmS']/1000)**2)
                    self.assertAlmostEqual(arrest['sinceContact']['chassisKineticChangeJ'],kinetic,delta=1e-10)

    def test_signed_rebound_releases_storage_and_motor_work_is_not_absolute_travel(self):
        for name,result in self.engines(self.request(landingDropMm=100,landingBrakeTorqueNm=100)):
            changes=[r['springStoredJ'] for r in result['rows']]
            self.assertTrue(any(b<a-1e-4 for a,b in zip(changes,changes[1:])),name)
            self.assertTrue(all(abs(r['motorRemovedJ']+r['motorWorkJ'])<1e-12 for r in result['rows']),name)
            self.assertFalse(result['workIntegrals']['exactChassisGravityCompensation'])

    def test_work_ledger_identity_native_rotor_and_additional_loads(self):
        request=self.request(landingDropMm=100,landingBrakeTorqueNm=40)
        request['params'].update(alpha=15,loadMode='global',Fx=12,Fz=3,beta=20)
        request['motorConfig']={**MOTOR_DEFAULTS,'enabled':True,'gearRatio':5,'rotorInertiaKgM2':.0002,
            'coggingAmplitudeNm':.02,'coulombFrictionNm':.01,'viscousFrictionNms':.002}
        for name,result in self.engines(request):
            self.assertNotEqual(result['rows'][-1]['externalWorkJ'],0)
            for row in result['rows']:
                x=row['sinceContact']
                if not x:continue
                accounted=x['gravityReleasedJ']-x['springStoredJ']-x['coggingStoredJ']-x['motorRemovedJ']-x['dampingRemovedJ']-x['motorLossJ']+x['terrainSuppliedJ']+x['externalSuppliedJ']-(x['coupledNumericalLossJ'] or 0)-(x['contactLossJ'] or 0)-(x['stopLossJ'] or 0)+(x['projectionEnergyJ'] or 0)+x['ledgerResidualJ']
                self.assertAlmostEqual(x['kineticChangeJ'],accounted,delta=2e-12)
                if name=='pymunk':
                    self.assertIsNone(row['contactDissipationJ'])
                    self.assertIsNone(row['stopDissipationJ'])
            if name=='analytical':self.assertGreater(abs(result['rows'][-1]['positionStabilizationJ']),0)

    def test_additional_force_work_is_actual_displacement_before_contact(self):
        request=self.request();request['runConfig']['duration']=.1
        request['params'].update(loadMode='global',Fx=7,Fz=3,beta=20)
        model=validate_contact_request(request)
        for name,result in self.engines(request):
            a,b=result['rows'][0],result['rows'][-1]
            expected=-model.force[0]*(b['CxMm']-a['CxMm'])/1000+model.force[1]*(b['wheelZMm']-a['wheelZMm'])/1000+model.Mw*(b['wheelAngle']-a['wheelAngle'])*math.pi/180
            self.assertAlmostEqual(b['externalWorkJ'],expected,delta=1e-12)

    def test_refinement_and_bottomout_negative_control(self):
        for name,engine in (('analytical',analytical),('pymunk',pymunk)):
            errors=[]
            for dt in (.00025,.000125):
                request=self.request();request['engine']=name;request['runConfig'].update(dt=dt,outputHz=200)
                result=engine(request);errors.append(max(abs(r['energyBalanceResidualJ']) for r in result['rows']))
            self.assertLess(errors[1],errors[0])
            request=self.request(landingBrakeTorqueNm=0);request['engine']=name;result=engine(request)
            self.assertEqual(result['caseMetrics']['outcome'],'bottom-out-before-arrest')
            self.assertFalse(result['caseMetrics']['landingSuccess'])


if __name__=='__main__':
    unittest.main(verbosity=2)
