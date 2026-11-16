"""Verify saved inversion cartridges, independent of the interactive viewer.

Run python -B verify-inversion.py [campaign.json]. Inputs local catalogue and
solution records, units mm/N/Nm/kg/deg. Outputs assertions; never writes Excel.
Checks each enabled case's travel, continuous extrema and dense torque/limits.
"""
import copy,json,math,pathlib,sys
import numpy as np
import spring_lab as lab

def verify(records):
    checks=0
    for record in records:
        before=copy.deepcopy(record)
        checked=lab.evaluate(copy.deepcopy(record),count=20001)
        assert checked['metrics']['valid'],(record['id'],checked['metrics']['violations'])
        p={**record['parameters'],**record['geometry']}
        assert p['Sv']-p['hornR']>=2*p['rs']-1e-7
        assert 50-1e-7<=p['hornR']<=95+1e-7 and p['rs']==12.7
        assert p['Sv']<=150+1e-6 and abs(p['Su'])<=30+1e-6
        assert record['payloads']==[0,70]
        assert record['masks']==([[1,0],[1,1]] if record['mode']=='parallel' else [[1,0],[0,1]])
        reference=lab.geometry(p,[90])[0][0]
        for i,part in enumerate(record['springs']):
            low=-50 if record['masks'][0][i] else p['te']
            angles=np.linspace(low,p['tc'],20001)
            c=lab.geometry(p,angles)[0]
            x=(part['p0']-part['initial'])/part['k']+c-reference
            F=part['initial']+part['k']*x
            length=part['free']+(-1 if part['type']=='C' else 1)*x
            energy=(part['initial']*x+.5*part['k']*x*x)/1000
            assert float(x.min())>=-1e-6
            assert float(F.min())>0
            assert float(F.max())<=part['fmax']+1e-5
            assert float(length.min())>=part['lmin']-1e-5
            assert float(length.max())<=part['lmax']+1e-5
            assert float(energy.max())<=part['energy']+1e-5
            assert float(x.max())<=part['travel']+1e-5
            assert isinstance(part['od'],(float,int)) and part['od']>0
            # The analytic extrema must enclose the dense samples.
            z=lab.case_travel(p,low)
            assert min(0,float(c.min()-reference))>=z['low']-1e-7
            assert max(0,float(c.max()-reference))<=z['high']+1e-7
            checks+=11
        inv=checked['metrics']['inversion']
        assert inv['valid'] and inv['theta2fAchievable']<=-50+1e-5
        assert lab.inversion_state(p,[record['springs'][0]],inv['theta2fAchievable'])[0]
        if not inv['fullTurn']:
            assert not lab.inversion_state(p,[record['springs'][0]],inv['theta2fAchievable']-.0001)[0]
        for a,b in zip(checked['cases'],record['cases']):
            assert abs(a['maxAbs']-b['maxAbs'])<2e-5
        assert before==record
        checks+=8
    return checks

if __name__=='__main__':
    if len(sys.argv)>1:doc=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf8'))
    else:
        import spring_store
        doc=spring_store.read()
    records=[r for r in doc['solutions'] if r.get('campaign')=='dp9-inversion-2026-11-11']
    assert len(records)==20
    assert all(sum(r['group']==group for r in records)==5 for group in {r['group'] for r in records})
    print(json.dumps({'solutions':len(records),'checks':verify(records),'scope':'Analytical spring and cable limits; no hardware or fatigue certification'}))
