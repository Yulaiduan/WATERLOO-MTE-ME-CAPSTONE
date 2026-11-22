"""Validate/publish the DP18 campaign to V7's isolated solution workbook.
Run: python -B scripts/publish_dp18.py (springs root); numpy/scipy and writer runtime.
Inputs: .work/dp18-20261122 mixed/single JSON; units mm/N/Nm/deg/kg.
Outputs: V7 solution workbook, dated campaign evidence; preserves V6 and DP libraries.
Limits: numerical static checks only, FOX force is derived from marked travel.
"""
import pathlib,sys,json,copy,hashlib,datetime,csv,shutil
import numpy as np
R=pathlib.Path(__file__).resolve().parents[1];V=R.parent/'vsl-solver/v7';sys.path.insert(0,str(V));import spring_lab as lab,spring_store as store
W=R/'.work/dp18-20261122';D=R/'research/2026-11-22-dp18-search';D.mkdir(parents=True,exist_ok=True)
paths=[R/'v6-spring-solutions.xlsx',V/'v7-configs.xlsx'];before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};newbook=store.BOOK;store.BOOK=paths[0];old=store.read();store.BOOK=newbook
reference=next(copy.deepcopy(x) for x in old['solutions'] if x['id']=='S0075');reference['group']='Reference · S0075';reference['favorite']=True
rows=[];summary=[]
for category in ['mixed','single']:
 for rec in json.loads((W/(category+'.json')).read_text(encoding='utf8')):
  assert rec['sourceDp']==18 and rec['parameters']['tc']==190 and rec['parameters']['m6']==0
  checked=store.canonical(copy.deepcopy(rec));lab.evaluate(checked,20001);assert checked['metrics']['valid'],checked['metrics']
  assert checked['masks']==[[1,0],[0,1]] and checked['payloads']==[0,70]
  assert 40-1e-7<=checked['geometry']['hornR']<=42+1e-7 and checked['geometry']['rs']==25.4
  assert all(s['type']=='C' and s['lmax']<210 for s in checked['springs'])
  assert (checked['springs'][0].get('supplier','McMaster-Carr')==checked['springs'][1].get('supplier','McMaster-Carr'))==(category=='single')
  assert checked['metrics']['inversion']['valid'] and checked['metrics']['inversion']['clearanceValid']
  checked['id']='S'+str(old['nextId']+len(rows)).zfill(4);checked['savedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();checked['favorite']=checked['rank']==1;checked['catalogueHash']=hashlib.sha256(lab.CATALOGUE.read_bytes()).hexdigest()
  rows.append(checked);g=checked['geometry'];summary.append(dict(id=checked['id'],group=category,rank=checked['rank'],part_unloaded=checked['springs'][0]['part'],part_loaded=checked['springs'][1]['part'],supplier_unloaded=checked['springs'][0].get('supplier','McMaster-Carr'),supplier_loaded=checked['springs'][1].get('supplier','McMaster-Carr'),rh_mm=g['hornR'],rs_mm=g['rs'],Su_mm=g['Su'],Sv_mm=g['Sv'],unloaded_peak_Nm=checked['cases'][0]['maxAbs'],loaded_peak_Nm=checked['cases'][1]['maxAbs'],unloaded_force_N=checked['forcePeaks'][0],loaded_force_N=checked['forcePeaks'][1],lmax_unloaded_mm=checked['springs'][0]['lmax'],lmax_loaded_mm=checked['springs'][1]['lmax'],rated_force_basis_loaded=checked['springs'][1].get('ratingBasis','Published McMaster ratings')))
doc={**old,'nextId':old['nextId']+len(rows),'solutions':[reference,*rows],'cataloguePath':str(lab.CATALOGUE)+' + dated supplier JSON','catalogueHash':hashlib.sha256(lab.CATALOGUE.read_bytes()).hexdigest()}
(D/'campaign.json').write_text(json.dumps(rows,indent=2),encoding='utf8');(W/'publish.json').write_text(json.dumps(doc),encoding='utf8')
with (D/'ranked-solutions.csv').open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
store.write(doc);again=store.read();assert len(again['solutions'])==21 and [x['id'] for x in again['solutions']]==[reference['id']]+[x['id'] for x in rows]
for p in paths:assert hashlib.sha256(p.read_bytes()).hexdigest()==before[str(p)],p
(D/'validation.json').write_text(json.dumps({'solutions':20,'poses_each':20001,'baseline_retained':'S0075','v6_and_dp18_libraries_unchanged':before,'v7_workbook':str(store.BOOK),'checks':'Canonical catalogue remap, force/travel/length/energy limits, one-only masks, supplier groups, rh/rs, exact inversion extrema, continuous clearance; 21 solution roundtrip'},indent=2),encoding='utf8')
print('SAVED',store.BOOK);print(json.dumps(summary,indent=2))