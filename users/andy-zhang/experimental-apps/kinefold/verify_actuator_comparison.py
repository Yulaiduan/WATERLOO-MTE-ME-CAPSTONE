"""Headless unit/source/job checks for automatic actuator comparison.

Run: .venv/Scripts/python.exe verify_actuator_comparison.py [--engine-root DIR].
Uses source catalog kg/m/rad/Nm and temporary local job folders; optional engine
root runs genuine finite-link analytical/Pymunk contact smoke cases. Outputs
unittest counts only; never edits live profiles or opens an app/server. Unit
fixtures are analytical expectations, not hardware or full design validation.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import time
import unittest

import actuator_comparison as ac
from actuation_limits import ACTUATOR_DEFAULTS,ActuatorController,torque_limit,validate_actuator_config
from comparison_service import ComparisonService,atomic_write,read_json

ENGINE_ROOT=None


class Limits(unittest.TestCase):
    def setUp(self):self.c={**ACTUATOR_DEFAULTS,'ratio':10.,'peakShaftNm':2.,'forwardEfficiency':.8,'reverseEfficiency':.5,'gearboxPeakNm':1000.}
    def test_four_quadrants_energy(self):
        for direction in (-1,1):
            mot=torque_limit(self.c,direction,direction*100)
            self.assertAlmostEqual(mot['motorTorqueNm'],direction*16)
            self.assertAlmostEqual(mot['shaftCommandNm'],direction*2)
            self.assertAlmostEqual(mot['shaftMechanicalPowerW']-mot['jointMechanicalPowerW'],4)
            brake=torque_limit(self.c,direction,-direction*100)
            self.assertAlmostEqual(brake['motorTorqueNm'],-direction*40)
            self.assertAlmostEqual(brake['shaftCommandNm'],-direction*2)
            self.assertAlmostEqual(brake['gearboxLossPowerW'],20)
    def test_current_speed_and_peak_duration(self):
        c={**self.c,'torqueConstantNmPerA':.1,'peakPhaseCurrentA':5.,'continuousPhaseCurrentA':2.}
        self.assertAlmostEqual(torque_limit(c,0.,100)['motorTorqueNm'],4.)
        self.assertAlmostEqual(torque_limit(c,0.,100,peak_elapsed_s=3)['motorTorqueNm'],1.6)
        self.assertEqual(torque_limit(c,c['noLoadRpm']*math.pi/30/c['ratio'],100)['motorTorqueNm'],0.)
        self.assertAlmostEqual(torque_limit(c,c['noLoadRpm']*.75*math.pi/30/c['ratio'],100)['motorTorqueNm'],2.)
    def test_power_regen_energy_acceptance(self):
        c={**self.c,'regenPowerW':5.}
        self.assertAlmostEqual(torque_limit(c,1.,-100)['motorTorqueNm'],-10.)
        self.assertEqual(torque_limit(c,1.,-100,regen_used_j=c['regenEnergyJ'])['motorTorqueNm'],0.)
        self.assertEqual(torque_limit({**c,'regenAcceptance':False},1.,-100)['motorTorqueNm'],0.)
        self.assertGreater(torque_limit({**c,'regenAcceptance':False},0.,-100)['actuatorAvailableNm'],0.)
    def test_strict_payload(self):
        self.assertIsNone(validate_actuator_config(None))
        self.assertEqual(validate_actuator_config(self.c),self.c)
        for change in ({'junk':0},{'ratio':0},{'forwardEfficiency':0},{'noLoadRpm':float('nan')}):
            with self.assertRaises(ValueError):validate_actuator_config({**self.c,**change})
    def test_last_step_regen_energy_budget(self):
        c={**self.c,'regenEnergyJ':1.}
        actual=torque_limit(c,1.,-100,regen_used_j=.999,dt_s=.01)
        self.assertLessEqual(actual['regenPowerW']*.01,.001+1e-12)


class SourceAndScreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=ac.load_catalog();cls.project=json.loads((ac.ROOT/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text(encoding='utf-8'))
        cls.geometry=ac.prepare_geometry(cls.project,ac.ASSUMPTIONS)
        cls.rows=ac.enumerate_candidates(cls.catalog,cls.geometry,ac.ASSUMPTIONS)
    def test_complete_exact_enumeration(self):
        self.assertEqual(len(self.rows),2198);self.assertEqual(len({r['id'] for r in self.rows}),2198)
        source={g['id']:g for g in self.catalog['gearboxes']}
        for row in self.rows:
            self.assertEqual(row['ratio'],source[row['gearboxId']]['ratio'])
            self.assertTrue(all(v['status']=='not-run' for engine in ('analytical','pymunk') for v in row[engine].values()))
        self.assertLess(len(ac.canonical(self.rows).encode()),16*1024*1024)
    def test_missing_vs_assumed(self):
        missing=ac.missing_metrics(self.catalog)
        self.assertEqual((missing['motorSpeedMissing'],missing['continuousTorqueMissing'],missing['torqueConstantMissing'],missing['gearboxInputInertiaMissing']),(14,11,10,145))
        hw=next(r['hardware'] for r in self.rows if 'hardware' in r)
        self.assertIsNone(hw['actuatorConfig']['torqueConstantNmPerA'])
        self.assertTrue(any('not measured' in s for s in hw['assumptionFlags']))
        self.assertEqual(hw['actuatorConfig']['noLoadRpm'],6000)
    def test_input_equivalent_inertia_once(self):
        m=self.catalog['motors'][0];g=next(g for g in self.catalog['gearboxes'] if g['inputInertiaKgM2'] is not None)
        hw=ac.candidate_hardware(m,g,ac.ASSUMPTIONS)
        self.assertAlmostEqual(g['inputInertiaKgM2'],g['inputInertiaKgCm2']*1e-4)
        self.assertAlmostEqual(hw['reflectedInertiaKgM2'],g['ratio']**2*(m['rotorInertiaKgM2']+g['inputInertiaKgM2']))
        self.assertEqual(hw['gearboxOutputInertiaKgM2'],0)
        project=copy.deepcopy(self.project);project['solverConfig']['hipRotorInertiaKgM2']=.017
        payload=ac.contact_payload(project,hw,ac.ASSUMPTIONS,'terrain','analytical')
        self.assertAlmostEqual(payload['motorConfig']['gearboxInputInertiaKgM2'],g['inputInertiaKgM2'])
        self.assertAlmostEqual(payload['runConfig']['hipRotorInertiaKgM2'],.017)
        from motor_model import Motor
        total=Motor.resolve(payload['motorConfig']).reflected_inertia+payload['runConfig']['hipRotorInertiaKgM2']
        self.assertAlmostEqual(total,.017+hw['reflectedInertiaKgM2'])
    def test_landing_drop_energy_and_saved_geometry(self):
        row=next(r for r in self.rows if 'hardware' in r)
        low=ac.fast_screen(self.geometry,row['hardware'],{**ac.ASSUMPTIONS,'dropHeightMm':1000})
        high=ac.fast_screen(self.geometry,row['hardware'],ac.ASSUMPTIONS)
        change=high['landing']['metrics']['energyRequiredJ']-low['landing']['metrics']['energyRequiredJ']
        self.assertAlmostEqual(change,self.geometry['totalMassKg']*9.81)
        self.assertGreater(self.geometry['compressionStopClearanceMm'],300)
        self.assertEqual(self.geometry['totalMassKg'],11.25)
        self.assertEqual(self.project['params']['m2'],1)
    def test_ranking_unknown_never_pass(self):
        ordered=ac.rank_candidates(self.rows)
        self.assertNotEqual(ordered[0]['status'],'unknown')
        self.assertTrue(all(r['paretoFront'] is None for r in self.rows if r['massKg'] is None))
        self.assertTrue(any(r['paretoFront'] is True for r in self.rows))
    def test_resolved_payload_does_not_mutate(self):
        before=ac.digest(self.project);row=next(r for r in self.rows if 'hardware' in r)
        payload=ac.contact_payload(self.project,row['hardware'],ac.ASSUMPTIONS,'landing','analytical')
        self.assertEqual(ac.digest(self.project),before)
        self.assertEqual(payload['params']['m2'],1);self.assertEqual(payload['runConfig']['inputRiseMm'],0)
        self.assertEqual(payload['caseConfig']['landingDropMm'],2000)
        self.assertEqual(payload['actuatorConfig']['minClearanceMm'],50)
    def test_tilted_rolling_screen_and_grade_tracking(self):
        from contact_cases import CASE_DEFAULTS
        p=copy.deepcopy(self.project);p['params']['alpha']=20
        geometry=ac.prepare_geometry(p,ac.ASSUMPTIONS);m=geometry['model']
        point=geometry['samples'][50];q=point['q']
        wheel=m.p['m6'];rw=m.p['rw']/1000
        cpx=2*m.p['L2']/1000*math.cos(q)*math.sin(math.radians(20))
        expected=m.coefficients(q)[0]-m.I['6']*m.K**2+.5*wheel*rw**2*(cpx/rw)**2
        self.assertAlmostEqual(point['J'],expected,delta=1e-12)
        m.terrain_config={'gradePercent':10};m.c['inputSpeedMmS']=100
        controller=ActuatorController(m,{**CASE_DEFAULTS,'kind':'terrain-stability'},ACTUATOR_DEFAULTS)
        h=controller.target_h+.01
        r=controller.command(m.q0,0,True,time=1.,state={'h':h,'vh':.01})
        self.assertAlmostEqual(r['rideTargetHeightMm'],h*1000,delta=1e-10)
        self.assertAlmostEqual(r['rideTargetVelocityMmS'],10)


class Verdicts(unittest.TestCase):
    def fixture(self):
        rows=[]
        for i in range(11):
            rows.append(dict(t=i/10,theta2=135,chassisZMm=500,chassisAccelerationMmS2=0.,
                chassisClearanceMm=450,motorTorqueNm=2,shaftCommandNm=1,contactCount=1,energyBalanceResidualJ=0))
        return dict(rows=rows,events=[dict(type='chassis-arrest',t=.2)],
            params=dict(te=100,tc=165),diagnostics=dict(termination='duration'),
            caseMetrics=dict(minimumUndersideClearanceMm=450))
    def test_no_short_hold_or_later_crash_pass(self):
        r=self.fixture();self.assertEqual(ac.dynamic_metrics(r,ac.ASSUMPTIONS,'landing')['status'],'pass')
        r['events'][0]['t']=.9;self.assertEqual(ac.dynamic_metrics(r,ac.ASSUMPTIONS,'landing')['status'],'unknown')
        r['events'].append(dict(type='compression-stop',t=.95));self.assertEqual(ac.dynamic_metrics(r,ac.ASSUMPTIONS,'landing')['status'],'fail')
    def test_unknown_acceleration_not_zero(self):
        r=self.fixture()
        for row in r['rows']:row.pop('chassisAccelerationMmS2')
        metrics=ac.dynamic_metrics(r,ac.ASSUMPTIONS,'terrain')
        self.assertIsNone(metrics['metrics']['rmsBodyAccelerationMS2']);self.assertEqual(metrics['status'],'unknown')
    def test_interval_acceleration_and_backdrive_overspeed(self):
        r=self.fixture()
        for row in r['rows']:
            row['chassisAccelerationMmS2']=None
            row['chassisVelocityMmS']=2000*row['t']
            row['shaftRpm']=1000.
        r['snapshot']={'actuatorConfig':{'ratio':10.,'maxInputRpm':2000.}}
        v=ac.dynamic_metrics(r,ac.ASSUMPTIONS,'terrain')
        self.assertAlmostEqual(v['metrics']['rmsBodyAccelerationMS2'],2.)
        self.assertAlmostEqual(v['metrics']['peakBodyAccelerationMS2'],2.)
        self.assertIn('interval',v['metrics']['accelerationBasis'])
        r['snapshot']['actuatorConfig']['maxInputRpm']=900.
        self.assertEqual(ac.dynamic_metrics(r,ac.ASSUMPTIONS,'terrain')['status'],'fail')
    def test_com_required_not_chassis(self):
        r=self.fixture();r['caseMetrics']['jumpHeightMm']=3000
        self.assertEqual(ac.dynamic_metrics(r,ac.ASSUMPTIONS,'jump')['status'],'unknown')
        r['caseMetrics']['jumpComRiseMm']=2100
        self.assertEqual(ac.dynamic_metrics(r,ac.ASSUMPTIONS,'jump')['status'],'pass')


class Jobs(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.shared=threading.Lock()
        self.s=ComparisonService(self.root,sys.executable,self.shared)
        (self.root/'actuator_comparison.py').write_text('''import argparse,json,time,pathlib
p=argparse.ArgumentParser();p.add_argument('--request');p.add_argument('--output');a=p.parse_args()
d=pathlib.Path(a.output);r=json.loads(pathlib.Path(a.request).read_text());time.sleep(.15)
(d/'result.json').write_text(json.dumps({'candidates':[],'project':r['project']}))
''',encoding='utf-8')
    def tearDown(self):self.s.close();self.tmp.cleanup()
    def test_save_atomic_and_no_library(self):
        reply=self.s.handle(dict(action='save',assumptions=dict(dropHeightMm=1234)))
        self.assertEqual(reply['assumptions']['dropHeightMm'],1234)
        path=self.root/'profiles/actuator-comparison.json';before=path.read_bytes()
        with self.assertRaises(ValueError):self.s.handle(dict(action='save',assumptions=dict(junk=2)))
        self.assertEqual(before,path.read_bytes());self.assertFalse((self.root/'profiles/library.json').exists())
    def test_start_results_and_lock(self):
        reply=self.s.handle(dict(action='start',project=dict(schema='kinefold/project-v3')));job=reply['job']['id']
        self.assertTrue(self.shared.locked())
        with self.assertRaises(ValueError):self.s.handle(dict(action='start'))
        deadline=time.monotonic()+3
        while self.s.handle(dict(action='status',jobId=job))['job']['state']=='running' and time.monotonic()<deadline:time.sleep(.02)
        self.assertEqual(self.s.handle(dict(action='results',jobId=job))['job']['state'],'complete')
        self.assertFalse(self.shared.locked())
        saved=self.s.handle(dict(action='export',jobId=job));self.assertTrue((self.root/saved['savedPath']).exists())
        with self.assertRaises(ValueError):self.s.handle(dict(action='status',jobId='../escape'))
    def test_cancel_and_close_release(self):
        job=self.s.handle(dict(action='start'))['job']['id']
        self.s.handle(dict(action='cancel',jobId=job));self.s.close()
        self.assertFalse(self.shared.locked());self.assertFalse(self.s.busy)
        self.assertEqual(self.s.handle(dict(action='status',jobId=job))['job']['state'],'cancelled')
    def test_restart_marks_orphan_not_running(self):
        directory=self.root/'.preview/actuator-comparisons'/('a'*32);atomic_write(directory/'status.json',dict(id='a'*32,state='running'))
        other=ComparisonService(self.root,sys.executable)
        self.assertEqual(other.handle(dict(action='status',jobId='a'*32))['job']['state'],'failed');other.close()


class ActualFinite(unittest.TestCase):
    def test_independent_finite_rollouts(self):
        if not ENGINE_ROOT:self.skipTest('optional finite-engine root not supplied')
        sys.path.insert(0,str(ENGINE_ROOT))
        try:
            from analytical_contact import simulate_contact as analytical
            from contact_dynamics import simulate_contact as pymunk
            project=json.loads((ac.ROOT/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text(encoding='utf-8'))
            a={**ac.ASSUMPTIONS,'dynamicDurationS':.08,'dynamicDt':.00025,'dynamicOutputHz':50.,'dropHeightMm':20.}
            catalog=ac.load_catalog();hardware=ac.candidate_hardware(catalog['motors'][0],catalog['gearboxes'][0],a)
            for engine,simulate in (('analytical',analytical),('pymunk',pymunk)):
                p=ac.contact_payload(project,hardware,a,'landing',engine)
                result=simulate(p)
                self.assertGreater(len(result['rows']),1)
                self.assertEqual(result['params']['m2'],1)
                self.assertIn('linkKineticJ',result['rows'][-1])
                self.assertIn('comZMm',result['rows'][-1])
                self.assertIn('actuatorConfig',result['snapshot'])
                self.assertNotEqual(ac.dynamic_metrics(result,a,'landing')['status'],'pass')
        finally:sys.path.remove(str(ENGINE_ROOT))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--engine-root',type=Path);args,rest=parser.parse_known_args()
    ENGINE_ROOT=args.engine_root
    unittest.main(argv=[sys.argv[0],*rest])
