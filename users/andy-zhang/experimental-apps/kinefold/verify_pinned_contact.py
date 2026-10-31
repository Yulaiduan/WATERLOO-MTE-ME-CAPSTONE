"""Verify real-contact chassis pin and desired-height step boundary conditions.

Run app Python verify_pinned_contact.py from Kinefold. Inputs retained V4.5
geometry (mm/deg/kg), SI motor properties and short actual engine integrations.
Outputs unittest evidence only; no saved designs or files. Pin forces are
interval momentum-balance reactions, not hardware impact peaks. No GUI, tire
compliance, thermal, full-body or canonical robot validation is claimed.
"""
import copy
import json
import math
import sys
import tempfile
from pathlib import Path
import unittest

import nonideal_study as study
from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as pymunk
from contact_cases import validate_contact_request
from actuation_limits import ACTUATOR_DEFAULTS,validate_actuator_config
from actuation_limits import torque_limit
from dynamic_model import Model
from actuation_limits import ActuatorController
from comparison_service import ComparisonService


def request(*,pinned=True,finite=False):
    c=study.default_config();c.update(upperLinkKg=1. if finite else 0.,lowerLinkKg=1. if finite else 0.,
        alphaDeg=0.,terrainDurationS=.08,terrainSpeedMmS=.1,outputHz=100.,dt=.00025)
    p=study.make_payload(c,'terrain-stability',10.,'losses','analytical',c['terrains'][0])
    p['params'].update(phi0=0.,springEnabled=False)
    p['runConfig'].update(fixture='pinned-chassis' if pinned else 'floating-chassis',inputSpeedMmS=0.)
    p.pop('actuatorConfig');p['motorConfig']['enabled']=False
    return p


class PinnedContact(unittest.TestCase):
    def test_numerical_rest_preserves_holding_torque_for_either_velocity_sign(self):
        c={**ACTUATOR_DEFAULTS,'ratio':10.,'hipBeltRatio':2.,'peakShaftNm':6.64,
            'forwardEfficiency':.97,'reverseEfficiency':.9,'gearboxPeakNm':300.,'regenAcceptance':False}
        for command in (-4.6476976754,4.6476976754):
            for velocity in (-1e-15,0.,1e-15):
                out=torque_limit(c,velocity,command)
                self.assertEqual(out['motorTorqueNm'],command)
                self.assertEqual(out['actuatorMode'],'motoring-or-hold')
                self.assertFalse(out['actuatorLimited'])
        # Genuine backdrive still obeys the disabled regeneration acceptance.
        self.assertEqual(torque_limit(c,.1,-4.6476976754)['motorTorqueNm'],0.)
        for sign in (-1.,1.):
            n=c['ratio']*c['hipBeltRatio'];command=sign*4.
            self.assertEqual(torque_limit(c,-sign*.5e-12/n,command)['motorTorqueNm'],command)
            self.assertEqual(torque_limit(c,-sign*2e-12/n,command)['motorTorqueNm'],0.)

    def test_resolved_quadrants_retain_shaft_and_regeneration_power_caps(self):
        c={**ACTUATOR_DEFAULTS,'ratio':10.,'hipBeltRatio':2.,'peakShaftNm':6.64,
            'forwardEfficiency':.97,'reverseEfficiency':.9,'gearboxPeakNm':300.,
            'motoringPowerW':2.5,'brakingPowerW':2.5,'regenPowerW':2.5}
        for velocity in (-.1,.1):
            for command in (-1000.,1000.):
                out=torque_limit(c,velocity,command)
                self.assertLessEqual(abs(out['shaftMechanicalPowerW']),2.5+1e-12)
                self.assertLessEqual(out['regenPowerW'],2.5+1e-12)
                self.assertGreaterEqual(out['gearboxLossPowerW'],0.)
                self.assertEqual(out['actuatorMode'],'braking' if command*velocity<0 else 'motoring-or-hold')
        self.assertEqual(torque_limit(c,.1,-1000.,regen_used_j=c['regenEnergyJ'])['motorTorqueNm'],0.)

    def test_real_coil_and_bounded_static_feedforward_have_no_false_pin_bias(self):
        import terrain_speed_study as speed
        c=speed.default_config();catalog=json.loads((speed.ROOT/'motor-gearbox-catalog.json').read_text())
        hardware=speed.selected_hardware(c,catalog,'odrive-8325')
        for solver in (analytical,pymunk):
            p=speed.make_payload(c,hardware,'terrain-stability','analytical',3.)
            p['runConfig'].update(fixture='pinned-chassis',duration=.06,outputHz=500.)
            p['terrainConfig']=study.terrain_config(study.default_config()['terrains'][0])
            r=solver(p);steady=[z for z in r['rows'] if z['t']>=.02]
            self.assertTrue(p['params']['springEnabled'])
            self.assertEqual(r['diagnostics']['termination'],'duration')
            self.assertLess(max(abs(z['pinForceZN']) for z in steady),.02)
            self.assertAlmostEqual(steady[-1]['contactForceZN'],13.75*9.81,delta=.02)
            for z in steady:self.assertAlmostEqual(z['motorTorqueNm'],z['actuatorRequestedNm'],delta=1e-9)

    def test_legacy_optional_fields_and_case_guards(self):
        old=dict(ACTUATOR_DEFAULTS)
        for key in ('hipBeltRatio','rideTargetStepMm','rideTargetStepTimeS'):old.pop(key)
        self.assertEqual(validate_actuator_config(old),old)
        p=request();validate_contact_request(p)
        with self.assertRaisesRegex(ValueError,'prescribed-height'):Model(p['params'],p['runConfig'])
        for kind in ('jump','landing'):
            bad=copy.deepcopy(p);bad['caseConfig']['kind']=kind
            with self.assertRaisesRegex(ValueError,'Pinned chassis'):validate_contact_request(bad)
        bad=copy.deepcopy(p);bad['actuatorConfig']={**ACTUATOR_DEFAULTS,'rideTargetStepMm':25}
        with self.assertRaisesRegex(ValueError,'floating chassis'):validate_contact_request(bad)
        for key,value in (('rideTargetStepMm',501),('rideTargetStepTimeS',31),('rideTargetStepMm',True)):
            with self.assertRaises(ValueError):validate_actuator_config({**ACTUATOR_DEFAULTS,key:value})
        for kind in ('jump','landing'):
            inactive=request(pinned=False);inactive['caseConfig']['kind']=kind
            inactive['actuatorConfig']={**ACTUATOR_DEFAULTS,'rideTargetStepMm':25}
            m=validate_contact_request(inactive)
            controller=ActuatorController(m,inactive['caseConfig'],inactive['actuatorConfig'])
            self.assertEqual(controller.target_height(.5),controller.target_h)

    def test_pinned_all_case_comparison_rejects_before_job_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            service=ComparisonService(Path(directory),sys.executable)
            try:
                with self.assertRaisesRegex(ValueError,'separate pinned terrain diagnostic'):
                    service.handle(dict(action='start',project=dict(schema='kinefold/project-v3',solverConfig=dict(fixture='pinned-chassis'))))
                self.assertFalse(service.busy)
                self.assertFalse(list(Path(directory).glob('comparisons/*/request.json')))
            finally:service.close()

    def test_static_pin_support_and_signs_both_engines(self):
        for solver in (analytical,pymunk):
            for support in (0.,20.,200.):
                p=request();m=validate_contact_request(p)
                p['runConfig']['hipTorqueNm']=-support*m.jacobian(m.q0)/m.axis[1]
                r=solver(p);rows=r['rows'][1:];weight=p['params']['m1']*p['params']['g']
                self.assertEqual(r['diagnostics']['termination'],'duration')
                self.assertTrue(r['diagnostics']['chassisPinned'])
                self.assertFalse(r['scope']['wheelTerrainBound'])
                self.assertLess(r['diagnostics']['maxPinPositionErrorMm'],1e-5)
                self.assertIsNone(r['rows'][0]['pinForceZN'])
                self.assertAlmostEqual(sum(z['pinForceZN'] for z in rows)/len(rows),weight-support,delta=.02)
                self.assertAlmostEqual(rows[-1]['chassisSupportForceZN'],support,delta=.02)
                self.assertEqual(rows[0]['pinForceDeltaZN'],0.)
                for z in rows:
                    self.assertEqual(z['pinWorkJ'],0.)
                    self.assertAlmostEqual(z['pinImpulseNs'],z['pinMomentumChangeNs']+z['pinGravityImpulseNs']-z['pinExternalImpulseNs']-z['pinContactImpulseNs'],delta=1e-12)

    def test_pinned_chassis_does_not_pin_wheel_to_ground(self):
        for solver in (analytical,pymunk):
            p=request();p['runConfig'].update(hipTorqueNm=3.,duration=.05)
            r=solver(p)
            self.assertLess(r['diagnostics']['maxPinPositionErrorMm'],1e-5)
            self.assertGreater(r['rows'][-1]['gapMm'],1.)
            self.assertEqual(r['rows'][-1]['contactNormalForceN'],0.)
            self.assertGreater(r['rows'][-1]['wheelVelocityZMmS'],0.)

    def test_finite_link_pin(self):
        final=[]
        for solver in (analytical,pymunk):
            p=request(finite=True);p['params']['alpha']=20.
            p['motorConfig'].update(enabled=True,hipBeltRatio=2)
            p['runConfig']['hipTorqueNm']=-15.
            r=solver(p);self.assertEqual(r['diagnostics']['termination'],'duration')
            self.assertTrue(r['diagnostics']['finiteLinkDynamics'])
            self.assertLess(r['diagnostics']['maxPinPositionErrorMm'],.001)
            self.assertTrue(all(math.isfinite(z['pinForceZN']) for z in r['rows'][1:]))
            final.append(r['rows'][-1]['pinForceZN'])
        self.assertAlmostEqual(*final,delta=1.)

    def test_pinned_free_wheel_spins_on_moving_ground_and_refines(self):
        endings=[]
        for solver in (analytical,pymunk):
            finer=[]
            for dt in (.00025,.000125):
                p=request(finite=True);p['runConfig'].update(inputSpeedMmS=1000.,dt=dt,hipTorqueNm=-15.)
                r=solver(p);self.assertEqual(r['diagnostics']['termination'],'duration')
                self.assertLess(r['diagnostics']['maxPinPositionErrorMm'],.001)
                self.assertGreater(abs(r['rows'][-1]['wheelAngularVelocityDegS']),100.)
                self.assertGreater(r['rows'][-1]['contactNormalForceN'],0.)
                finer.append(r['rows'][-1]['pinForceZN'])
            self.assertAlmostEqual(*finer,delta=.5);endings.append(finer[-1])
        self.assertAlmostEqual(*endings,delta=.5)

    def test_floating_actual_height_step_has_no_teleport(self):
        for solver in (analytical,pymunk):
            p=request(pinned=False,finite=True);p['runConfig']['duration']=.24
            p['actuatorConfig']={**ACTUATOR_DEFAULTS,'peakShaftNm':100.,'gearboxPeakNm':500.,
                'rideTargetStepMm':25.,'rideTargetStepTimeS':.1}
            r=solver(p);rows=r['rows'];a=next(z for z in rows if z['t']>=.1-1e-9)
            before=max((z for z in rows if z['t']<.1-1e-9),key=lambda z:z['t'])
            self.assertAlmostEqual(a['rideTargetHeightMm']-before['rideTargetHeightMm'],25.)
            self.assertLess(abs(a['chassisZMm']-before['chassisZMm']),1.)
            self.assertGreater(rows[-1]['chassisZMm']-a['chassisZMm'],1.)
            self.assertTrue(all(z['pinForceZN'] is None for z in rows))
            self.assertTrue(r['diagnostics']['wheelSpinFree'])
            self.assertFalse(r['scope']['wheelTerrainBound'])


if __name__=='__main__':unittest.main()
