"""Verify seeded terrain-v2 shape/grade mechanics without computer or GUI use.

Run app .venv Python verify_terrain_variation.py [--engines]. Inputs: captured
sheet catalog, mm profiles, seed uint32, variation/grade percent and V4 geometry.
Outputs unittest assertions and ignored .preview numerical engine evidence.
Limitations: experimental vertical-slide quarter-model numerics; no soil,
four-leg, freely translating vehicle, hardware or visual certification.
"""
import copy
import json
import math
from pathlib import Path
import subprocess
import time
import unittest

from terrain_profiles import CATALOG, contour, sequence, validate_terrain, periodic_spec, circle_contacts, surface_height, random_unit
from contact_cases import initial_conditions, initial_motion, validate_contact_request, terrain_spec, CASE_DEFAULTS
from dynamic_model import defaults
from profile_service import _project

ROOT=Path(__file__).resolve().parent
JS="const fs=require('fs'),vm=require('vm');for(const f of ['reference-v4.js','model.js','variables.js','terrain-profiles.js','project-store.js','preset-store.js'])vm.runInThisContext(fs.readFileSync(f,'utf8'));KinefoldTerrainProfiles.init(JSON.parse(fs.readFileSync('terrain-catalog.json','utf8')));"


def config(mode='roughness',grade=0,variation=20,seed=481):
    return dict(schema='kinefold/terrain-v2',catalogRevision='2026-10-29',profileId='gravel-service-fire-road',
        severity='typical',representation=mode,periodMm=600.,heightMm=25.,rmsMm=15.,
        seed=seed,variationPercent=variation,gradePercent=grade)


def payload(base,config_value,alpha=0,rate=0,duration=.5,dt=.0005,speed=300):
    return dict(engine='analytical',params={**base,'m6':1.5,'alpha':alpha},
        runConfig=dict(defaults(),duration=duration,dt=dt,outputHz=100,inputSpeedMmS=speed,inputDelayS=.05,initialVelocityDegS=rate),
        contactConfig=dict(mode='terrain-contact',friction=.8,restitution=0,drive='free'),terrainConfig=config_value)


class VariationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project=json.loads(subprocess.check_output(['node','-e',JS+"console.log(JSON.stringify(KinefoldProjects.baseline()));"],cwd=ROOT,text=True,encoding='utf-8'))
        cls.base=cls.project['params']

    def test_js_python_seed_cycle_grade_parity(self):
        cases=[dict(config(mode,grade,var,seed),cycle=cycle) for mode in ('obstacles','roughness') for grade in (-20,0,20) for var in (0,20,50) for seed in (0,481,0xffffffff) for cycle in (-2,-1,0,1,3)]
        code=JS+"const cases=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(cases.map(({cycle,...c})=>KinefoldTerrainProfiles.contour(c,cycle))));"
        actual=json.loads(subprocess.check_output(['node','-e',code],input=json.dumps(cases),cwd=ROOT,text=True,encoding='utf-8'))
        for case,node in zip(cases,actual):
            cycle=case.pop('cycle');py=contour(case,cycle)
            for key in ('peakMm','meanMm','rmsMm','gradeDegrees','maxLocalGradePercent'):
                self.assertAlmostEqual(py[key],node[key],delta=1e-9)
            for key in ('pointsMm','roughnessPointsMm','baselinePointsMm'):
                for a,b in zip(py[key],node[key]):
                    self.assertAlmostEqual(a[0],b[0],delta=1e-10);self.assertAlmostEqual(a[1],b[1],delta=1e-9)
        request=dict(config(grade=-15),count=4,start=-2)
        code=JS+"const {count,start,...c}=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(KinefoldTerrainProfiles.sequence(c,count,start)));"
        node=json.loads(subprocess.check_output(['node','-e',code],input=json.dumps(request),cwd=ROOT,text=True,encoding='utf-8'))
        py=sequence(config(grade=-15),4,-2)
        self.assertAlmostEqual(node['detrendedRmsMm'],py['detrendedRmsMm'],delta=1e-10)
        self.assertEqual(len(node['pointsMm']),385)

    def test_determinism_diversity_and_zero_legacy(self):
        c=config();s=sequence(c,4,-1)
        self.assertEqual(s,sequence(c,4,-1))
        self.assertNotEqual(s['roughnessPointsMm'],sequence(config(seed=482),4,-1)['roughnessPointsMm'])
        self.assertGreater(len({cell['peakMm'] for cell in s['cells']}),1)
        for mode in ('obstacles','roughness'):
            c=config(mode,variation=0);old={k:v for k,v in c.items() if k not in ('seed','variationPercent','gradePercent')};old['schema']='kinefold/terrain-v1'
            self.assertEqual(contour(c)['pointsMm'],contour(old)['pointsMm'])
            for cycle in (-1,0,1):
                self.assertEqual(contour(c,cycle)['roughnessPointsMm'],contour(old)['pointsMm'])
        for cell,next_cell in zip(s['cells'],s['cells'][1:]):
            self.assertEqual(cell['pointsMm'][-1][1],next_cell['pointsMm'][0][1])
            self.assertEqual(cell['roughnessPointsMm'][:2],[[0.,0.],[600/96,0.]])
            self.assertEqual(cell['roughnessPointsMm'][-2:],[[(95)*600/96,0.],[600.,0.]])

    def test_exact_detrended_stats_and_signed_slope(self):
        for grade in (-20,0,20):
            c=config(grade=grade);s=sequence(c,3)
            points=s['roughnessPointsMm'];total=points[-1][0]-points[0][0]
            mean=sum((b[0]-a[0])*(a[1]+b[1])/2 for a,b in zip(points,points[1:]))/total
            second=sum((b[0]-a[0])*(a[1]**2+a[1]*b[1]+b[1]**2)/3 for a,b in zip(points,points[1:]))/total
            self.assertAlmostEqual(s['rmsMm'],math.sqrt(second-mean*mean),delta=1e-10)
            self.assertAlmostEqual(s['gradeDegrees'],math.degrees(math.atan(grade/100)))
            self.assertAlmostEqual(s['baselinePointsMm'][-1][1],grade/100*1800)
            for cell in s['cells']:
                self.assertAlmostEqual(cell['rmsMm'],15*cell['shape']['amplitudeFactor'],delta=1e-10)
        self.assertEqual(sequence(config(grade=-20))['roughnessPointsMm'],sequence(config(grade=20))['roughnessPointsMm'])

    def test_safe_stance_normal_velocity_and_duration_prefix(self):
        for grade in (-20,0,20):
            for alpha in (0,20):
                for rate in (-4,0,4):
                    request=payload(self.base,config(grade=grade),alpha,rate)
                    m=validate_contact_request(request);case=dict(CASE_DEFAULTS);q,h,x,z=initial_conditions(m,case);motion=initial_motion(m,case,q)
                    self.assertAlmostEqual(z,.2*math.sqrt(1+(grade/100)**2),delta=1e-14)
                    speed=request['runConfig']['inputSpeedMmS']/1000;vx,vz=motion['wheelVelocity'];g=grade/100
                    self.assertAlmostEqual(g*(vx-speed)+vz,0.,delta=1e-14)
                    self.assertAlmostEqual(motion['chassisVelocity']+m.sites(q)['6'][1][1]*motion['qd'],vz)
                    spec=terrain_spec(m,case)
                    self.assertGreaterEqual(min(v[0] for v in circle_contacts(spec,0,x,z,.2)),-1e-12)
                    self.assertAlmostEqual(surface_height(spec,.1)-surface_height(spec,0),g*speed*.1,delta=1e-12)
                    longer=copy.deepcopy(request);longer['runConfig']['duration']=3.;m2=validate_contact_request(longer);other=terrain_spec(m2,case)
                    for d in (0,.15,.4):
                        u=x-.2-speed*.05-d
                        self.assertAlmostEqual(surface_height(spec,0,u),surface_height(other,0,u),delta=1e-12)
                    for kind in ('jump','landing'):
                        inactive={**case,'kind':kind};q0,h0,x0,z0=initial_conditions(m,inactive)
                        self.assertAlmostEqual(z0,.2+(inactive['landingDropMm']/1000 if kind=='landing' else 0))
                        self.assertEqual(initial_motion(m,inactive,q0)['chassisVelocity'],0.)

    def test_strict_configuration_and_roundtrip(self):
        for patch in [dict(seed=True),dict(seed=-1),dict(seed=2**32),dict(seed=.5),dict(variationPercent=True),dict(variationPercent=math.nan),dict(variationPercent=51),dict(gradePercent=True),dict(gradePercent=math.inf),dict(gradePercent=-101),dict(extra=1)]:
            with self.assertRaises(ValueError):validate_terrain({**config(),**patch})
        p=copy.deepcopy(self.project);p['terrainConfig']=config(grade=20)
        self.assertEqual(_project(p)['terrainConfig'],p['terrainConfig'])
        from preset_service import validate_record
        r=dict(id='preset-varied-terrain',kind='input',name='Varied grade',version=1,createdAt='2026-10-29T00:00:00.000Z',updatedAt='2026-10-29T00:00:00.000Z',values=dict(solverConfig=p['solverConfig'],terrainConfig=p['terrainConfig']))
        self.assertEqual(validate_record(r)['values']['terrainConfig'],p['terrainConfig'])


def engines(base):
    import analytical_contact,contact_dynamics
    from desktop_viewer import visible_terrain_heights
    report=[];coarse_tilt_error=None
    for grade,alpha in [(0,0),(15,0),(-15,20)]:
        request=payload(base,config(grade=grade),alpha,duration=2.6)
        pair=[]
        for engine,fn in [('analytical',analytical_contact.simulate_contact),('pymunk',contact_dynamics.simulate_contact)]:
            request['engine']=engine;start=time.perf_counter();out=fn(copy.deepcopy(request));elapsed=time.perf_counter()-start;size=len(json.dumps(out,allow_nan=False).encode())
            assert size<16*1024*1024 and elapsed<90
            assert out['terrainConfig']==request['terrainConfig']
            assert out['diagnostics']['termination']=='duration',out['diagnostics']
            assert out['diagnostics']['maxPenetrationMm']<1
            assert abs(out['rows'][0]['chassisVelocityMmS']-grade/100*300)<1e-8
            assert max(abs(r['contactNormalForceN']) for r in out['rows'])<10000
            visible=visible_terrain_heights(out,-500,500)
            if grade:assert max(map(abs,visible))<max(abs(p[2]) for p in out['terrain']['contourMm'])
            report.append(dict(engine=engine,gradePercent=grade,alpha=alpha,seconds=elapsed,bytes=size,samples=len(out['rows']),termination=out['diagnostics']['termination'],maxPenetrationMm=out['diagnostics']['maxPenetrationMm'],endChassisMm=out['rows'][-1]['chassisZMm']))
            pair.append(out)
        assert pair[0]['designHash']==pair[1]['designHash']
        assert len(pair[0]['rows'])==len(pair[1]['rows'])
        difference=max(abs(a['chassisZMm']-b['chassisZMm']) for a,b in zip(pair[0]['rows'],pair[1]['rows']));assert difference<10
        if alpha==20:coarse_tilt_error=difference
    fine=[]
    for engine,fn in [('analytical',analytical_contact.simulate_contact),('pymunk',contact_dynamics.simulate_contact)]:
        request=payload(base,config(grade=-15),20,duration=2.6,dt=.00025);request['engine']=engine;out=fn(request);fine.append(out)
        assert out['diagnostics']['termination']=='duration'
        report.append(dict(engine=engine,case='tilted-downhill-refinement',dt=.00025,endChassisMm=out['rows'][-1]['chassisZMm'],maxPenetrationMm=out['diagnostics']['maxPenetrationMm'],energyResidualJ=out['rows'][-1]['energyBalanceResidualJ']))
    fine_error=max(abs(a['chassisZMm']-b['chassisZMm']) for a,b in zip(fine[0]['rows'],fine[1]['rows']))
    assert fine_error<coarse_tilt_error
    report.append(dict(case='tilted-downhill-refinement',coarseMaxHeaveDifferenceMm=coarse_tilt_error,fineMaxHeaveDifferenceMm=fine_error))
    # Pure incline: horizontal guide reaction means N ~= Mg / cos(beta), not Mg cos(beta).
    request=payload(base,{**config(grade=10,variation=0),'heightMm':0.,'rmsMm':0.},duration=6.5,dt=.002,speed=100)
    request['runConfig']['outputHz']=20
    weight=(base['m1']+1.5)*base['g'];expected=weight*math.sqrt(1+.1**2)
    for engine,fn in [('analytical',analytical_contact.simulate_contact),('pymunk',contact_dynamics.simulate_contact)]:
        request['engine']=engine;out=fn(copy.deepcopy(request));last=out['rows'][-1]
        assert abs(last['t']-6.5)<1e-10
        assert .9*expected<last['contactNormalForceN']<1.1*expected
        assert max(abs(r['contactNormalForceN']) for r in out['rows'])<1000
        report.append(dict(engine=engine,case='pure-grade-final-clock',lastTime=last['t'],lastNormalN=last['contactNormalForceN'],verticalSlideNormalReferenceN=expected))
    (ROOT/'.preview').mkdir(exist_ok=True);(ROOT/'.preview'/'terrain-v2-engine-evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--engines',action='store_true');args=parser.parse_args()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(VariationChecks))
    if not result.wasSuccessful():raise SystemExit(1)
    if args.engines:engines(VariationChecks.base)
