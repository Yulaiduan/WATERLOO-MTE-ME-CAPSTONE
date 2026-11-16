"""Verify nominal nested V6 spring solutions; run python -B verify-nested.py.
Inputs installed solution workbook/catalogue, mm,N,Nm,kg,deg. Read-only checks of
catalogued diameters, signed torques, full inverted travel, ratings and reload.
No manufacturing, winding-hand, buckling or hardware qualification is implied.
"""
import copy,json,pathlib,sys
import numpy as np
import spring_lab as lab
import spring_store as store

def verify(records):
    checks=0
    for saved in records:
        r=store.canonical(saved)
        assert r['metrics']['valid'] and r['metrics']['inversion']['valid']
        n=r['metrics']['nesting'];assert n['valid']
        assert n['diametralClearance']>=1 and abs(n['radialClearance']*2-n['diametralClearance'])<1e-8
        assert not n['manufacturingVerified']
        assert n['outerId']==r['springs'][n['outerSlot']-1]['coilId']
        assert n['innerOd']==r['springs'][n['innerSlot']-1]['od']
        p={**r['parameters'],**r['geometry']}
        assert p['Sv']<=150+1e-6 and abs(p['Su'])<=30+1e-6
        assert 50-1e-6<=p['hornR']<=95+1e-6 and p['rs']==12.7
        assert p['Sv']-p['hornR']>=25.4-1e-6
        assert r['masks']==[[1,0],[1,1]] and r['payloads']==[0,70]
        assert r['metrics']['inversion']['theta2fAchievable']<=-50+1e-5
        ref=lab.geometry(p,[90])[0][0]
        for i,part in enumerate(r['springs']):
            theta=np.linspace(-50 if i==0 else p['te'],p['tc'],30001)
            c=lab.geometry(p,theta)[0];x=part['p0']/part['k']+c-ref;F=part['k']*x
            length=part['free']-x;energy=.5*part['k']*x*x/1000
            assert min(x)>=-1e-6 and min(F)>0
            assert max(x)<=part['xmax']+1e-5 and max(F)<=part['fmax']+1e-5
            assert min(length)>=part['lmin']-1e-5 and max(length)<=part['lmax']+1e-5
            assert max(energy)<=part['energy']+1e-5
            checks+=7
        checked=lab.evaluate(copy.deepcopy(r),count=30001)
        for a,b in zip(checked['cases'],saved['cases']):assert abs(a['maxAbs']-b['maxAbs'])<.0001
        assert checked['cases'][1]['maxAbs']<5
        bad=copy.deepcopy(r['springs']);bad[n['outerSlot']-1]['coilId']=n['innerOd']
        assert not lab.nesting_metrics(bad)['valid']
        bad[n['outerSlot']-1]['coilId']=None
        assert not lab.nesting_metrics(bad)['valid']
        bad_record=copy.deepcopy(r);bad_record['springs']=bad
        assert not lab.evaluate(bad_record)['metrics']['valid']
        checks+=16
    assert len(records)==5 and len({tuple(s['id'] for s in r['springs']) for r in records})==5
    return checks+2

if __name__=='__main__':
    doc=store.read() if len(sys.argv)<2 else json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf8'))
    rows=[r for r in doc['solutions'] if r.get('campaign')=='dp9-nested-2026-11-11']
    print(json.dumps(dict(solutions=len(rows),checks=verify(rows),scope='Nominal nesting and analytical spring/cable limits')))
