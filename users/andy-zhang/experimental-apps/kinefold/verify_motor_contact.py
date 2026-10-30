"""Verify motor/contact coupling with independent mass and energy calculations.

Run app Python verify_motor_contact.py (Node/Pymunk required). Inputs are SI motor
parameters and the existing experimental mm geometry; outputs unittest evidence.
Checks numerical rigid-contact behavior, not hardware performance or tire impact.
"""
import copy
import math
import unittest
from motor_model import DEFAULTS
from contact_cases import CASE_DEFAULTS, validate_contact_request, CaseController, energy_fields, check_motor_step
from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as pymunk
import verify_contact

class MotorContactChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):verify_contact.ContactChecks.setUpClass()
    def request(self,kind='landing',**motor):
        req=verify_contact.ContactChecks().payload({'springEnabled':False},duration=.25,dt=.00025,inputHeightMm=0,inputSpeedMmS=.1)
        req['caseConfig']={**CASE_DEFAULTS,'kind':kind,'landingDropMm':100,'landingBrakeTorqueNm':0,'undersideOffsetMm':None}
        req['motorConfig']={**DEFAULTS,'enabled':True,**motor}
        return req
    def test_reflected_mass_and_energy(self):
        req=self.request(gearRatio=7,rotorInertiaKgM2=.003)
        m=validate_contact_request(req);q=m.q0;qd=1.7;sd=m.jacobian(q)*qd
        self.assertAlmostEqual(m.Jref,49*.003)
        e=energy_fields(m,q,.8,.1,sd,.2)
        self.assertAlmostEqual(e['rotorKineticJ'],.5*49*.003*qd**2)
        self.assertAlmostEqual(m.I['6'],.5*req['params']['m6']*(req['params']['rw']/1000)**2)
    def test_joint_and_motor_commands_and_hold(self):
        req=self.request('jump',gearRatio=5,commandBasis='motor');m=validate_contact_request(req)
        ctl=CaseController(m,req['caseConfig']);self.assertEqual(ctl.torques(m.hi,0)['motorTorqueNm'],-100)
        req=self.request(coggingAmplitudeNm=.3,coggingPhaseDeg=40,gearRatio=5)
        m=validate_contact_request(req);ctl=CaseController(m,req['caseConfig']);tor=ctl.torques(m.q0,0)
        self.assertAlmostEqual(tor['motorTorqueNm']+tor['jointPassiveNm'],0,delta=1e-12)

    def test_gearbox_inertia_matches_equivalent_legacy_both_engines(self):
        req=self.request(gearRatio=4,rotorInertiaKgM2=.002,gearboxInputInertiaKgM2=.001)
        req['runConfig']['duration']=.2
        equivalent=copy.deepcopy(req);equivalent['motorConfig'].pop('gearboxInputInertiaKgM2')
        equivalent['motorConfig']['rotorInertiaKgM2']=.003
        for solver in (analytical,pymunk):
            a,b=solver(req),solver(equivalent)
            self.assertEqual(a['motorConfig'],req['motorConfig'])
            self.assertEqual(b['motorConfig'],equivalent['motorConfig'])
            self.assertNotIn('gearboxInputInertiaKgM2',b['snapshot']['motorConfig'])
            self.assertGreater(max(x['rotorKineticJ'] for x in a['rows']),.001)
            for x,y in zip(a['rows'],b['rows']):
                self.assertAlmostEqual(x['chassisZMm'],y['chassisZMm'],delta=1e-9)
                self.assertAlmostEqual(x['rotorKineticJ'],y['rotorKineticJ'],delta=1e-9)
    def test_conservative_cogging_and_loss(self):
        req=self.request(gearRatio=4,coggingAmplitudeNm=.2,coggingPeriodsPerRev=3,coulombFrictionNm=.1,viscousFrictionNms=.02)
        m=validate_contact_request(req);q=m.q0;eps=1e-6
        s=m.motor.motor_state(q,.7,0)
        du=(m.motor.motor_state(q+eps,0,0)['coggingPotentialJ']-m.motor.motor_state(q-eps,0,0)['coggingPotentialJ'])/(2*eps)
        self.assertAlmostEqual(-du,s['jointCoggingNm'],delta=1e-8)
        self.assertGreater(s['motorLossPowerW'],0)
        self.assertAlmostEqual(s['jointFrictionNm']*.7,-s['motorLossPowerW'])
    def test_phase_and_friction_resolution_guards(self):
        req=self.request(gearRatio=50,rotorInertiaKgM2=0,coulombFrictionNm=.01)
        m=validate_contact_request(req)
        with self.assertRaisesRegex(ValueError,'friction is underresolved'):check_motor_step(m,1,.00025)
        check_motor_step(m,1,1e-8)
        req=self.request(gearRatio=100,coggingAmplitudeNm=.1,coggingPeriodsPerRev=100)
        with self.assertRaisesRegex(ValueError,'cogging is underresolved'):check_motor_step(validate_contact_request(req),10,.00025)

    def test_nonzero_inertia_changes_actual_impact(self):
        req=self.request(rotorInertiaKgM2=.03,gearRatio=3)
        for solver in (analytical,pymunk):
            with self.subTest(solver=solver.__module__):
                r=solver(req);ideal=copy.deepcopy(req);ideal.pop('motorConfig');old=solver(ideal)
                self.assertGreater(max(x['rotorKineticJ'] for x in r['rows']),.001)
                self.assertGreater(abs(r['rows'][-1]['chassisVelocityMmS']-old['rows'][-1]['chassisVelocityMmS']),1)
                self.assertLess(r['diagnostics']['maxPenetrationMm'],1)
    def test_jump_stop_and_motor_losses(self):
        req=self.request('jump',rotorInertiaKgM2=.003,gearRatio=3,coulombFrictionNm=.02,viscousFrictionNms=.001)
        req['caseConfig']['jumpTorqueNm']=100;req['runConfig']['duration']=.8
        for solver in (analytical,pymunk):
            with self.subTest(solver=solver.__module__):
                r=solver(req)
                self.assertTrue(any(e['type']=='extension-stop' for e in r['events']))
                self.assertGreater(r['rows'][-1]['motorDissipationJ'],0)
                self.assertLess(r['diagnostics']['maxTravelStopDriftMm'],1)
                self.assertGreater(max(x['rotorKineticJ'] for x in r['rows']),.001)

    def test_separate_loss_integrals_actual_state_and_bounded_shaft(self):
        from actuation_limits import ACTUATOR_DEFAULTS
        for finite in (False,True):
            for limited in (False,True):
                req=self.request('jump',rotorInertiaKgM2=.002,gearboxInputInertiaKgM2=.001,
                    gearRatio=4,coulombFrictionNm=.05,viscousFrictionNms=.002,frictionVelocityScaleRadS=10)
                req['runConfig']['duration']=.4;req['caseConfig']['jumpTorqueNm']=100
                if finite:req['params'].update(m2=1,m3=1)
                if limited:req['actuatorConfig']={**ACTUATOR_DEFAULTS,'ratio':4,'peakShaftNm':25}
                for solver in (analytical,pymunk):
                    r=solver(req);rows=r['rows']
                    self.assertGreater(rows[-1]['motorCoulombDissipatedJ'],0)
                    self.assertGreater(rows[-1]['motorViscousDissipatedJ'],0)
                    for key in ('motorCoulombDissipatedJ','motorViscousDissipatedJ'):
                        self.assertTrue(all(b[key]>=a[key] for a,b in zip(rows,rows[1:])))
                    for row in rows+[e['state'] for e in r['events'] if 'state' in e]:
                        self.assertAlmostEqual(row['motorCoulombDissipatedJ']+row['motorViscousDissipatedJ'],row['motorDissipatedJ'],delta=1e-10)
                    for row in rows:
                        speed=row['motorVelocityRadS']
                        self.assertAlmostEqual(row['viscousLossPowerW'],.002*speed*speed,delta=1e-9)
                        self.assertAlmostEqual(row['coulombLossPowerW'],.05*math.tanh(speed/10)*speed,delta=1e-9)
                        self.assertAlmostEqual(row['rotorKineticJ'],.5*.003*speed*speed,delta=1e-8)
                        if limited:
                            n=4;eta=.9
                            expected=row['motorTorqueNm']*eta/n if row['actuatorMode']=='braking' else row['motorTorqueNm']/(n*eta)
                            self.assertAlmostEqual(row['shaftCommandNm'],expected,delta=1e-9)

    def test_actual_native_rotor_motor_work(self):
        from contact_cases import energy_estimate
        req=self.request('jump',rotorInertiaKgM2=.003,gearRatio=3,coggingAmplitudeNm=.02,coggingPeriodsPerRev=2)
        req['caseConfig']['jumpTorqueNm']=100
        req['runConfig']['duration']=.05
        result=pymunk(req)
        first,last=result['rows'][0],result['rows'][-1]
        # Constant pre-cutoff command: shaft torque times actual shaft angle change.
        expected=first['shaftCommandNm']*(last['motorAngleRad']-first['motorAngleRad'])
        self.assertGreater(abs(expected),.001)
        self.assertAlmostEqual(last['motorWorkJ'],expected,delta=1e-9)
        model=validate_contact_request(req)
        estimate=energy_estimate(model,req['caseConfig'])
        expected_cog=model.motor.motor_state(model.hi,0,0)['coggingPotentialJ']-model.motor.motor_state(model.lo,0,0)['coggingPotentialJ']
        self.assertAlmostEqual(estimate['coggingReleaseToExtensionJ'],expected_cog)

    def test_legacy_joint_inertia_matches_reflected_motor(self):
        req=self.request(rotorInertiaKgM2=.02,gearRatio=3)
        legacy=copy.deepcopy(req);legacy.pop('motorConfig');legacy['runConfig']['hipRotorInertiaKgM2']=.18
        for solver in (analytical,pymunk):
            a=solver(req);b=solver(legacy)
            for x,y in zip(a['rows'],b['rows']):
                self.assertAlmostEqual(x['chassisZMm'],y['chassisZMm'],delta=1e-9)
                self.assertAlmostEqual(x['rotorKineticJ'],y['legacyJointRotorKineticJ'],delta=1e-9)
                self.assertEqual(y['rotorKineticJ'],0)

    def test_nonzero_inertia_refinement(self):
        req=self.request(rotorInertiaKgM2=.02,gearRatio=3);errors=[]
        for dt in (.0005,.00025,.000125):
            req['runConfig']['dt']=dt;a=analytical(req);b=pymunk(req)
            errors.append(max(abs(x['chassisZMm']-y['chassisZMm']) for x,y in zip(a['rows'],b['rows'])))
        print('motor impact engine heave errors mm',errors)
        self.assertLess(errors[-1],errors[0])

if __name__=='__main__':unittest.main()
