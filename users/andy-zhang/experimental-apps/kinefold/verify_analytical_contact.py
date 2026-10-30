"""Check independent analytical contact mechanics in SI and returned mm frames.

Run Python verify_analytical_contact.py; uses Node for unchanged builder defaults.
Outputs unittest results; no Pymunk import required. Tests reduced experimental
quarter model only, not hardware, tires or canonical robot performance.
"""
import json
import math
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from analytical_contact import simulate_contact
from dynamic_model import defaults
from contact_cases import CASE_DEFAULTS
from contact_cases import terrain_spec as actual_terrain_spec

ROOT=Path(__file__).resolve().parent
JS="const fs=require('fs'),vm=require('vm');vm.runInThisContext(fs.readFileSync('reference-v4.js','utf8'));vm.runInThisContext(fs.readFileSync('model.js','utf8'));console.log(JSON.stringify(Kinefold.defaults));"


class AnalyticalContactChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads(subprocess.check_output(['node','-e',JS],cwd=ROOT,text=True));cls.base['m6']=1.5
    def request(self,case=None,**config):
        req=dict(engine='analytical',params=dict(self.base),runConfig={**defaults(), 'duration':.5,'inputHeightMm':0,'hipTorqueNm':-.027168833380,**config},contactConfig=dict(mode='terrain-contact',friction=.8,restitution=0,drive='free'))
        if case:req['caseConfig']={**CASE_DEFAULTS,**case}
        return req
    def test_flat_normal_spin_and_frictionless(self):
        req=self.request();r=simulate_contact(req);tail=r['rows'][-10:]
        self.assertAlmostEqual(sum(a['contactNormalForceN'] for a in tail)/len(tail),10.25*9.81,delta=.01)
        self.assertAlmostEqual(tail[-1]['wheelAngularVelocityDegS'],.1/.2*180/math.pi,delta=.01)
        req['contactConfig']['friction']=0;r=simulate_contact(req)
        self.assertEqual(r['rows'][-1]['wheelAngularVelocityDegS'],0)
        self.assertEqual(len(r['rows']),len(r['frames']))
    def test_freefall_landing_hold(self):
        r=simulate_contact(self.request(dict(kind='landing',landingDropMm=1000),duration=.1,dt=.00025))
        a,b=r['rows'][0],r['rows'][-1]
        self.assertAlmostEqual(b['chassisVelocityMmS'],-981,delta=1e-7)
        self.assertAlmostEqual(b['chassisZMm']-a['chassisZMm'],-49.05,delta=1e-7)
        self.assertAlmostEqual(b['theta2'],a['theta2'],delta=1e-8)
        self.assertAlmostEqual(b['energyJ'],a['energyJ'],delta=1e-8)
    def test_jump_stop_and_energy_fields(self):
        r=simulate_contact(self.request(dict(kind='jump',jumpTorqueNm=100),duration=.5))
        self.assertTrue(all(a['stopDissipationJ']>=0 for a in r['rows']))
        self.assertTrue(all(a['kineticJ']>=0 for a in r['rows']))
        self.assertTrue(any(e['type']=='extension-stop' for e in r['events']))
    def test_actual_raised_mesh_refinement(self):
        runs=[simulate_contact(self.request(duration=2,inputHeightMm=150,dt=dt)) for dt in (.001,.0005,.00025)]
        self.assertTrue(all(r['diagnostics']['firstRaisedContactTimeS'] is not None for r in runs))
        self.assertLess(runs[-1]['diagnostics']['maxPenetrationMm'],runs[0]['diagnostics']['maxPenetrationMm'])
        self.assertGreater(len(runs[-1]['terrain']['polygonsMm']),1)
    def test_spring_off_jump_work_and_negative_control(self):
        request=self.request(dict(kind='jump',jumpTorqueNm=100),duration=.8,dt=.00025)
        request['params']['springEnabled']=False;r=simulate_contact(request)
        self.assertTrue(any(e['type']=='takeoff' for e in r['events']))
        self.assertAlmostEqual(r['rows'][-1]['motorWorkJ'],100*(self.base['tc']-self.base['te'])*math.pi/180,delta=1e-8)
        self.assertGreater(r['rows'][-1]['stopDissipationJ'],0)
        stop=next(e for e in r['events'] if e['type']=='extension-stop')
        self.assertAlmostEqual(stop['verticalMomentumBeforeKgMS'],stop['verticalMomentumAfterKgMS'],delta=1e-10)
        request['caseConfig']['jumpTorqueNm']=0;r=simulate_contact(request)
        self.assertFalse(any(e['type']=='takeoff' for e in r['events']))
    def test_landing_bottom_out_and_arrest(self):
        request=self.request(dict(kind='landing',landingBrakeTorqueNm=0,undersideOffsetMm=50),duration=.7,dt=.0005)
        request['params']['springEnabled']=False;r=simulate_contact(request)
        self.assertFalse(r['caseMetrics']['landingSuccess'])
        self.assertEqual(r['caseMetrics']['outcome'],'bottom-out-before-arrest')
        self.assertIsNotNone(r['caseMetrics']['minimumUndersideClearanceMm'])
        request['caseConfig'].update(landingBrakeTorqueNm=100,undersideOffsetMm=None);r=simulate_contact(request)
        self.assertTrue(r['caseMetrics']['landingSuccess'])
        self.assertIsNone(r['caseMetrics']['minimumUndersideClearanceMm'])
    def test_coupled_pgs_compression_impulse_cannot_count_as_motor_arrest(self):
        # Retained 2026-10-30 table fixture: old event logic falsely passed
        # 97 Nm at q=164.9999897 after the coupled floor/stop impulse arrested A.
        profile=json.loads((ROOT/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text())
        p={**profile['params'],'theta2':100,'m1':11.25,'m2':0,'m3':0,'m6':.5,
            'springK':profile['params']['springK']*11.25/8.75,
            'p0':profile['params']['p0']*11.25/8.75}
        request=dict(engine='analytical',params=p,
            runConfig={**profile['solverConfig'],'duration':1.5,'dt':.000125,'outputHz':1000,
                'hipTorqueNm':0,'inputRiseMm':0,'iterations':160},
            contactConfig=dict(mode='terrain-contact',drive='free',friction=.8,restitution=0),
            caseConfig={**CASE_DEFAULTS,'kind':'landing','landingDropMm':1000,'landingOpenFraction':1,
                'landingBrakeTorqueNm':97,'landingBrakeLimitNm':1000})
        result=simulate_contact(request,stop_at_assessment=True)
        self.assertFalse(result['caseMetrics']['landingSuccess'])
        self.assertEqual(result['caseMetrics']['outcome'],'bottom-out-before-arrest')
        stop=next(e for e in result['events'] if e['type']=='compression-stop')
        self.assertEqual(stop['detection'],'Accumulated unilateral PGS stop impulse')
        self.assertGreater(stop['guideStopImpulseNs'],.1)
        self.assertGreater(stop['angularStopImpulseNms'],0)
        self.assertAlmostEqual(stop['t'],.681875,delta=1e-9)
        self.assertAlmostEqual(stop['verticalMomentumBeforeKgMS'],stop['verticalMomentumAfterKgMS'],delta=1e-10)
        self.assertLessEqual(stop['guideStopGapMm'],stop['guideStopActivationToleranceMm'])
        arrest=result['caseMetrics']['firstArrestTimeS']
        self.assertTrue(arrest is None or stop['t']<=arrest)
        # A real motor arrest comfortably inside the stroke stays a pass;
        # finite-link/tilted geometry must not turn ordinary braking into a stop.
        for alpha,link_mass in ((0,0),(20,0),(20,1)):
            request['params']={**p,'alpha':alpha,'m2':link_mass,'m3':link_mass}
            request['caseConfig']['landingBrakeTorqueNm']=300
            request['runConfig']['outputHz']=50
            with self.subTest(alpha=alpha,link_mass=link_mass):
                normal=simulate_contact(request,stop_at_assessment=True)
                self.assertTrue(normal['caseMetrics']['landingSuccess'])
                self.assertFalse(any(e['type']=='compression-stop' for e in normal['events']))
                self.assertLess(normal['caseMetrics']['maxCompressionDeg'],160)
    def test_landing_event_and_energy_refinement(self):
        residuals=[];impacts=[]
        for dt in (.001,.0005,.00025):
            r=simulate_contact(self.request(dict(kind='landing'),duration=.6,dt=dt));a,b=r['rows'][0],r['rows'][-1]
            residuals.append(abs(b['energyJ']-a['energyJ']-b['motorWorkJ']-b['dampingWorkJ']-b['terrainWorkJ']+b['stopDissipationJ']+b['contactDissipationJ']-b['positionStabilizationJ']))
            impacts.append(abs(r['caseMetrics']['impactTimeS']-math.sqrt(.2/9.81)))
        self.assertLess(residuals[2],residuals[1]);self.assertLess(residuals[1],residuals[0])
        self.assertLess(impacts[2],impacts[1]);self.assertLess(impacts[1],impacts[0])
    def test_impossible_vertical_wall_stops_before_projection(self):
        request=self.request(duration=1,inputHeightMm=150,dt=.00025);request['params']['rw']=100
        r=simulate_contact(request)
        self.assertEqual(r['diagnostics']['termination'],'contact-penetration-limit')
        self.assertLess(r['diagnostics']['elapsedSeconds'],.52)
        self.assertGreater(r['rows'][-1]['preProjectionPenetrationMm'],1.)
        self.assertGreater(r['rows'][-1]['postProjectionPenetrationMm'],1.)
        self.assertEqual(r['events'][-1]['stage'],'before-position-projection')
        self.assertLess(abs(r['rows'][-1]['CxMm']-r['rows'][0]['CxMm']),1e-8)
    def test_initial_overlap_and_initial_clearance_guards(self):
        def overlapping(m,case):
            spec=actual_terrain_spec(m,case);spec['boxes']=[[( -1.,0.),(1.,0.),(1.,1.),(-1.,1.)]];return spec
        with patch('analytical_contact.terrain_spec',overlapping),self.assertRaisesRegex(ValueError,'Initial wheel overlaps'):
            simulate_contact(self.request())
        with self.assertRaisesRegex(ValueError,'Initial chassis underside'):
            simulate_contact(self.request(dict(kind='landing',undersideOffsetMm=900)))
    def test_sustained_bottom_out_remains_supported(self):
        request=self.request(dict(kind='landing',landingBrakeTorqueNm=0),duration=.8,dt=.00025)
        request['params']['springEnabled']=False;r=simulate_contact(request);tail=r['rows'][-10:]
        self.assertFalse(r['caseMetrics']['landingSuccess'])
        self.assertAlmostEqual(tail[-1]['theta2'],self.base['tc'],delta=1e-8)
        self.assertAlmostEqual(sum(a['contactNormalForceN'] for a in tail)/len(tail),10.25*9.81,delta=.001)
        self.assertLess(max(abs(a['chassisVelocityMmS']) for a in tail),.001)
        self.assertLess(max(a['penetrationMm'] for a in tail),1e-5)
        self.assertLess(r['diagnostics']['maxTravelStopDriftMm'],1e-8)
        self.assertEqual(r['diagnostics']['energyBalanceResidualJ'],tail[-1]['energyBalanceResidualJ'])
        self.assertEqual(r['energyEstimate'],r['caseMetrics']['energyEstimate'])
    def test_tilted_stop_momentum_energy_refinement(self):
        errors=[]
        for dt in (.001,.0005,.00025):
            request=self.request(dict(kind='jump',jumpTorqueNm=100),duration=.5,dt=dt)
            request['params'].update(springEnabled=False,alpha=17);r=simulate_contact(request)
            stop=next(e for e in r['events'] if e['type']=='extension-stop')
            self.assertAlmostEqual(stop['verticalMomentumBeforeKgMS'],stop['verticalMomentumAfterKgMS'],delta=1e-10)
            self.assertGreaterEqual(stop['dissipatedEnergyJ'],0)
            self.assertLess(r['diagnostics']['maxTravelStopDriftMm'],1e-8)
            errors.append(abs(r['diagnostics']['energyBalanceResidualJ']))
        self.assertLess(errors[2],errors[1]);self.assertLess(errors[1],errors[0])


if __name__=='__main__':unittest.main(verbosity=2)
