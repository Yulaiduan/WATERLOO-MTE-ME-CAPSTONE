"""Read-only numerical/catalogue verification. Run python verify-spring-lab.py.
Writes only an optional --output report; never changes a user workbook.
"""
from pathlib import Path
import json,math,subprocess,sys,tempfile
import numpy as np
import spring_lab as lab
HERE=Path(__file__).resolve().parent
def verify():
 checks=0
 def near(a,b,tol=1e-7):
  nonlocal checks
  assert math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol,(a,b);checks+=1
 html=(HERE/'v6-springlab.html').read_text(encoding='utf8')
 import re
 scripts=[s for attrs,s in re.findall(r'<script\b([^>]*)>([\s\S]*?)</script>',html) if 'src=' not in attrs]
 cat=lab.read_catalogue();eligible={x['id']:x for x in cat if x['eligible']};assert len(eligible)>6000
 p=json.loads((HERE/'v6-default-library.json').read_text(encoding='utf8'))['rows'][0]['snapshot']['parameters'];rng=np.random.default_rng(43);fixtures=[]
 for rs in [0,.1,10,25]:
  for _ in range(12):
   pp={**p,'hornR':float(rng.uniform(40,100)),'Sv':float(rng.uniform(90,300)),'Su':float(rng.uniform(-40,40)),'nu':float(rng.uniform(-15,15)),'rs':rs,'te':100,'tc':165,'m2':1,'m3':.8,'m5':.2,'m6':.6,'alpha':20}
   try:z=lab.profile(pp,51)
   except ValueError:continue
   fixtures.append(dict(p=pp,t=z['theta'].tolist()))
 code='const fs=require("fs"),vm=require("vm");const a=JSON.parse(fs.readFileSync(process.argv[1],"utf8")),core=fs.readFileSync(process.argv[2],"utf8");const {s,b}=vm.runInNewContext(core+";({s:VSLSpring,b:VSLStatic})");console.log(JSON.stringify(a.map(f=>{const r=s.geometry(f.p,90),pp=b.resolveLoads({...f.p,springEnabled:false,loadMode:"yz",beta:0,Fy:0,Fz:s.totalMass(f.p)*f.p.g});return f.t.map(t=>{const z=s.state({...f.p,springEnabled:true,springK:0,p0:0},t);return [z.payout-r.payout,z.derivative,z.Jz,z.valid,b.solve(pp,t,false).tauG]})})));'
 with tempfile.TemporaryDirectory() as folder:
  src=Path(folder)/'fixtures.json';src.write_text(json.dumps(fixtures));core=Path(folder)/'core.js';core.write_text('\n'.join(scripts[:2]),encoding='utf8');ref=json.loads(subprocess.check_output(['node','-e',code,str(src),str(core)],text=True))
 for f,rows in zip(fixtures,ref):
  z=lab.profile(f['p'],51)
  for j,row in enumerate(rows):
   assert row[3];near(z['delta'][j],row[0]);near(z['A'][j]*1000,row[1]);near(z['J'][j]*1000,row[2]);mass=sum(f['p'][k] for k in ['m1','m2','m3','m5','m6']);near(mass*f['p']['g']*z['J'][j]-z['gravityOffset'][j],row[4]);t=f['t'][j];eps=1e-5;c=lab.geometry(f['p'],[t-eps,t+eps])[0];near((c[1]-c[0])/(2*eps*lab.R),row[1],2e-5)
 # Exact ideal point-pulley law and per-leg mass adaptation.
 pp={**p,'hornR':60,'Sv':110,'Su':0,'rs':0,'nu':0,'te':100,'tc':165,'alpha':20,'m1':11.25,'m2':0,'m3':0,'m5':0,'m6':0};mass=11.25;k=2*mass*pp['g']*pp['L2']*math.cos(20*lab.R)/(60*110);z=lab.profile(pp);d0=abs(pp['Sv']-pp['hornR']);F=k*(d0+z['delta']);near(float(max(abs(F*z['A']-mass*pp['g']*z['J']))),0,1e-10)
 # Real C and E searches must obey every limit and share all installed data.
 results={}
 for typ in ['C','E']:
  request=dict(parameters={**p,'m1':11.25,'m2':0,'m3':0,'m5':0,'m6':0},settings=dict(hornR=62.22694951186731,rs=10,nu=0,Sv=100,Su=9.4,bulk=0,svMin=70,svMax=400,suMin=-100,suMax=100,type=typ,m=3,payloads=[0,70],solutions=2,trials=150))
  result=lab.solve(request,cat);assert result['solutions'],typ;results[typ]=[]
  for record in result['solutions']:
   lab.evaluate(record,4001);assert record['metrics']['valid'];assert len(record['springs'])<=3;assert len(record['masks'])==2
   pp={**record['parameters'],**record['geometry']};z=lab.profile(pp,4001)
   for s in record['springs']:
    assert s['id'] in eligible
    x=s['x0']+z['delta'];F=s['initial']+s['k']*x;L=s['free']+(-x if typ=='C' else x);energy=(s['initial']*x+.5*s['k']*x*x)/1000
    assert float(min(x))>=-1e-6 and float(max(x))<=s['travel']+1e-6
    assert float(max(F))<=s['fmax']+1e-5 and float(max(energy))<=s['energy']+1e-5
    assert float(min(L))>=s['lmin']-1e-6 and float(max(L))<=s['lmax']+1e-6
    checks+=6
   near(record['cases'][0]['mL'],11.25);near(record['cases'][1]['mL'],28.75)
   results[typ].append(dict(worstNm=record['metrics']['worstNm'],parts=[s['part'] for s in record['springs']],geometry=record['geometry']))
 return dict(checks=checks,catalogueRows=len(cat),eligible=len(eligible),geometryFixtures=len(fixtures),results=results,scope='Numerical gravity-compensation screening; limits exact over continuous cable travel, torque extrema sampled at 4001+ poses; no fatigue or hardware certification.')
if __name__=='__main__':
 result=verify();print(json.dumps(result,indent=2))
 if '--output' in sys.argv:(HERE/'v6-spring-verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
