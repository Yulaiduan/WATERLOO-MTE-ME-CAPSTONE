"""Verify sheet-derived periodic geometry, persistence and actual contact engines.

Run app .venv Python verify_terrain_profiles.py [--engines] [--gui]. Inputs: offline
catalog estimates mm/m/percent and independent V4 defaults; writes only ignored
.preview evidence. Outputs assertions/engine timing and size summaries. Checks
experimental numerics only, not terrain statistics, soil or hardware fidelity.
--gui opens and automatically closes one actual Tk terrain playback window.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import subprocess
import time
import unittest

from terrain_profiles import CATALOG, contour, validate_terrain, circle_contacts
from dynamic_model import defaults
from contact_cases import CASE_DEFAULTS, validate_contact_request, terrain_spec, initial_conditions
from profile_service import _project

ROOT=Path(__file__).resolve().parent
JS="const fs=require('fs'),vm=require('vm');for(const f of ['reference-v4.js','model.js','variables.js','terrain-profiles.js','project-store.js','preset-store.js'])vm.runInThisContext(fs.readFileSync(f,'utf8'));KinefoldTerrainProfiles.init(JSON.parse(fs.readFileSync('terrain-catalog.json','utf8')));"


def config(profile=0,tier='typical',mode='obstacles',period=None):
    p=CATALOG['profiles'][profile];spacing=p['obstacleSpacingM'][tier]
    if spacing is None and tier=='extreme':spacing=p['obstacleSpacingM']['difficult']
    return dict(schema='kinefold/terrain-v1',catalogRevision=CATALOG['revision'],profileId=p['id'],severity=tier,representation=mode,periodMm=period if period is not None else spacing*1000,heightMm=p['obstacleMm'][tier],rmsMm=p['rmsMm'][tier])


class TerrainChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project=json.loads(subprocess.check_output(['node','-e',JS+"console.log(JSON.stringify(KinefoldProjects.baseline()));"],cwd=ROOT,text=True,encoding='utf-8'))

    def test_catalog_and_unknowns(self):
        self.assertEqual(len(CATALOG['profiles']),16)
        self.assertEqual(CATALOG['profiles'][0]['obstacleMm'],dict(typical=300,difficult=500,extreme=600))
        self.assertEqual(CATALOG['profiles'][14]['obstacleSpacingM'],dict(typical=50,difficult=20,extreme=None))
        snow=CATALOG['profiles'][-1]
        self.assertTrue(all(v is None for v in snow['rmsMm'].values()))
        self.assertTrue(all(v is None for v in snow['obstacleSpacingM'].values()))
        self.assertIn('misaligned',snow['sourceWarning'])
        for bad in [dict(config(),periodMm=math.nan),dict(config(),periodMm=True),dict(config(),extra=1),dict(config(),profileId='unknown'),dict(config(15,period=3000),representation='roughness')]:
            with self.assertRaises(ValueError):validate_terrain(bad)

    def test_all_contours_parity_and_integrals(self):
        configs=[config(i,tier,mode) for i in range(15) for tier in ('typical','difficult','extreme') for mode in ('obstacles','roughness')]+[config(15,period=3000)]
        request=json.dumps(configs)
        code=JS+"const inputs=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(inputs.map(KinefoldTerrainProfiles.contour)));"
        actual=json.loads(subprocess.check_output(['node','-e',code],cwd=ROOT,text=True,input=request,encoding='utf-8'))
        for c,j in zip(configs,actual):
            py=contour(c)
            for key in ('peakMm','meanMm','rmsMm','periodMm','maxLocalGradePercent'):
                self.assertAlmostEqual(j[key],py[key],delta=1e-9)
            for a,b in zip(j['pointsMm'],py['pointsMm']):
                self.assertAlmostEqual(a[0],b[0],delta=1e-10);self.assertAlmostEqual(a[1],b[1],delta=1e-10)
            self.assertEqual(py['pointsMm'][0][1],0)
            self.assertAlmostEqual(py['pointsMm'][-1][1],0,delta=1e-10)
            if c['representation']=='roughness':self.assertAlmostEqual(py['rmsMm'],c['rmsMm'],delta=1e-10)
            else:self.assertAlmostEqual(py['peakMm'],c['heightMm'],delta=1e-10)

    def test_project_and_preset_roundtrip(self):
        p=copy.deepcopy(self.project);p['terrainConfig']=config(12)
        self.assertEqual(_project(p)['terrainConfig'],p['terrainConfig'])
        from preset_service import validate_record
        # Native input validator reuses complete saved-project validation.
        value=dict(solverConfig=p['solverConfig'],terrainConfig=p['terrainConfig'])
        record=dict(id='preset-terrain-test',kind='input',name='Test terrain',version=1,createdAt='2026-10-29T00:00:00.000Z',updatedAt='2026-10-29T00:00:00.000Z',values=value)
        self.assertEqual(validate_record(record)['values']['terrainConfig'],p['terrainConfig'])

    def test_segment_endpoint_clearance(self):
        spec=dict(speed=0.,xs=[-2.,-.1,0.,2.],segments=[((-2.,0.),(-.1,0.)),((-.1,0.),(0.,.6)),((0.,.6),(2.,.6))])
        # An approaching circle does not penetrate a distant endpoint merely
        # because it lies below the infinite continuation of a slope.
        result=circle_contacts(spec,0,-.5,.2,.2)
        self.assertGreaterEqual(min(a[0] for a in result),-1e-12)

    def test_native_snapshot_and_translated_mesh(self):
        from desktop_viewer import simulate_snapshot, contact_mesh
        from viewer_service import ViewerService
        c=config(12,period=1000)
        request=dict(action='open',params={**self.project['params'],'m6':1.5},
            runConfig=dict(defaults(),duration=.25,dt=.0005,inputSpeedMmS=2000,inputDelayS=.05),
            contactConfig=dict(mode='terrain-contact',friction=.8,restitution=0,drive='free'),terrainConfig=c)
        snapshot=ViewerService._validate(request)
        self.assertEqual(snapshot['terrainConfig'],c)
        out=simulate_snapshot(snapshot);frame=out['frames'][-1]
        polygons,top=contact_mesh(out,frame)
        self.assertEqual(polygons,[])
        self.assertGreater(len(top),96)
        for expected,actual in zip(out['terrain']['contourMm'],top):
            self.assertAlmostEqual(actual[0],expected[0]+frame['terrainOffsetMm'][0])
            self.assertAlmostEqual(actual[1],expected[2])
        self.assertEqual(out['snapshot']['terrainConfig'],c)
        # A retained inactive surface does not enter the prescribed benchmark.
        bench=simulate_snapshot(dict(params=self.project['params'],runConfig=dict(defaults(),duration=.05),terrainConfig=c))
        self.assertNotEqual(bench['scope'].get('mode'),'terrain-contact')

    def test_no_epsilon_final_force_spike(self):
        import contact_dynamics
        p={**self.project['params'],'m6':1.5}
        # Flat constant support has no final impact. A 20 Hz output clock
        # previously left a ~1e-12 s warm-start step and a false 36 GN force.
        out=contact_dynamics.simulate_contact(dict(engine='pymunk',params=p,
            runConfig=dict(defaults(),duration=6.5,dt=.0005,outputHz=20,inputHeightMm=0,inputSpeedMmS=100),
            contactConfig=dict(mode='terrain-contact',friction=.8,restitution=0,drive='free')))
        self.assertEqual(len(out['rows']),131)
        self.assertEqual(out['rows'][-1]['t'],6.5)
        expected=(p['m1']+p['m6'])*p['g']
        for row in out['rows'][-5:]:
            self.assertAlmostEqual(row['contactNormalForceN'],expected,delta=.1)

    def test_geometric_query_matches_independent_native_segments(self):
        import pymunk
        from terrain_profiles import surface_height
        # The geometry distance oracle is independent of contact impulses.
        for heights in ([0,.6,0],[.6,0,.6],[0,0,.6]):
            points=list(zip([-1.,0.,1.],heights))
            spec=dict(speed=0.,xs=[p[0] for p in points],segments=list(zip(points,points[1:])))
            body=pymunk.Body(body_type=pymunk.Body.STATIC)
            native=[pymunk.Segment(body,a,b,0) for a,b in spec['segments']]
            for shape in native:shape.cache_bb()
            for x in (-.9,-.5,-.05,0,.05,.5,.9):
                for z in (.7,.9,1.2):
                    actual=min(v[0] for v in circle_contacts(spec,0,x,z,.2))
                    expected=min(s.point_query((x,z)).distance for s in native)-.2
                    self.assertAlmostEqual(actual,expected,delta=1e-12)


def engines(project):
    import analytical_contact,contact_dynamics
    reports=[]
    for index,mode in [(12,'obstacles'),(12,'roughness'),(0,'obstacles')]:
        c=config(index,mode=mode);run=dict(defaults(),duration=6.5,dt=.0005,outputHz=100,inputSpeedMmS=c['periodMm']/6,inputDelayS=.5)
        payload=dict(engine='analytical',params={**project['params'],'m6':1.5},runConfig=run,contactConfig=dict(mode='terrain-contact',friction=.8,restitution=0,drive='free'),terrainConfig=c)
        outputs=[]
        for engine,fn in [('analytical',analytical_contact.simulate_contact),('pymunk',contact_dynamics.simulate_contact)]:
            payload['engine']=engine;start=time.perf_counter();out=fn(copy.deepcopy(payload));elapsed=time.perf_counter()-start
            encoded=json.dumps(out,allow_nan=False).encode();assert len(encoded)<16*1024*1024
            assert out['terrainConfig']==c and out['snapshot']['terrainConfig']==c
            assert out['diagnostics']['elapsedSeconds']>.5
            assert out['diagnostics']['maxPenetrationMm']<2
            assert out['diagnostics']['firstRaisedContactTimeS'] is not None
            assert elapsed<90
            outputs.append(out)
            reports.append(dict(profile=c['profileId'],representation=mode,engine=engine,seconds=elapsed,bytes=len(encoded),samples=len(out['rows']),termination=out['diagnostics']['termination'],maxPenetrationMm=out['diagnostics']['maxPenetrationMm'],firstRaisedContactS=out['diagnostics']['firstRaisedContactTimeS']))
        if index==12:
            assert outputs[0]['diagnostics']['termination']=='duration'
            assert outputs[1]['diagnostics']['termination']=='duration'
            assert max(abs(a['chassisZMm']-b['chassisZMm']) for a,b in zip(outputs[0]['rows'],outputs[1]['rows']))<5
    (ROOT/'.preview').mkdir(exist_ok=True)
    (ROOT/'.preview'/'terrain-engine-evidence.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(reports,indent=2))


def gui(project):
    import os
    from desktop_viewer import PlaybackWindow, simulate_snapshot
    states=[]
    class Writer:
        def write(self,**state):states.append(state)
    c=config(12,period=1000)
    result=simulate_snapshot(dict(params={**project['params'],'m6':1.5},runConfig=dict(defaults(),duration=.8,dt=.0005,inputSpeedMmS=2000,inputDelayS=.05),contactConfig=dict(mode='terrain-contact',friction=.8,restitution=0,drive='free'),terrainConfig=c))
    window=PlaybackWindow(result,'Periodic terrain / native verification',Writer(),os.getpid(),self_test=True)
    window.root.update_idletasks()
    # Native canvas must draw the actual segmented contour, not a flat substitute.
    expected_coordinates=2*len(result['terrain']['contourMm'])
    assert any(window.canvas.type(item)=='line' and len(window.canvas.coords(item))==expected_coordinates for item in window.canvas.find_all())
    window.run()
    assert states[-1]['state']=='closed' and states[-1]['selfTestPassed']
    print('PASS actual Tk periodic contour, playback advance, pause, scrub, replay and automatic close.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--engines',action='store_true');parser.add_argument('--gui',action='store_true');args,rest=parser.parse_known_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(TerrainChecks);result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():raise SystemExit(1)
    if args.engines:engines(TerrainChecks.project)
    if args.gui:gui(TerrainChecks.project)
