"""Quick S0075 pulley-radius sensitivity using the existing V7 static backend.
Run: python -B scripts/pulley_radius_s0075.py from springs root; numpy/scipy.
Inputs: saved solution, mm/N/deg/kg; fixed springs, horn radius and preloads.
Outputs: JSON and CSV in .work/radius-s0075; no workbook or solver writes.
Limit: bounded multistart nominal static fit, not a global or hardware validation.
"""
import sys,pathlib,copy,json,hashlib,csv
import numpy as np
from scipy.optimize import minimize
R=pathlib.Path(__file__).resolve().parents[1];V=R.parent/'vsl-solver/v7';sys.path.insert(0,str(V))
import spring_lab as lab,spring_store as store
r=next(x for x in store.read()['solutions'] if x['id']=='S0075');W=R/'.work/radius-s0075';W.mkdir(parents=True,exist_ok=True)
hash0=hashlib.sha256(store.BOOK.read_bytes()).hexdigest();base=copy.deepcopy(r);lab.evaluate(base,6001)
p={**r['parameters'],**r['geometry']};mass=[4*sum(p[k] for k in ['m1','m2','m3','m5','m6'])/4+x/4 for x in r['payloads']]
ks=np.array([s['k'] for s in r['springs']]);pre=np.array([s['p0'] for s in r['springs']]);masks=np.array(r['masks']);p['_caseMasses']=mass

def taus(q,n=401):
 z=lab.profile(q,n);ix=np.searchsorted(z['theta'],np.linspace(q['te'],q['tc'],n));return np.array([(row@pre+row@ks*z['delta'])*z['A']-m*q['g']*z['J']+z['gravityOffset'] for m,row in zip(mass,masks)])[:,ix],z

def constraints(q):
 ans=[]
 for i,s in enumerate(r['springs']):
  a=lab.profile({**q,'te':r['settings']['theta2fTarget'] if masks[0,i] else q['te']},9)
  low=a['low'] if masks[0,i] else a['workingLow'];hi=a['high'] if masks[0,i] else a['workingHigh'];x=s['p0']/s['k']
  ans.extend([x+low,s['xmax']-x-hi])
 return np.array(ans)

def solve(rs,svmax=150,sumax=30):
 q={**p,'rs':rs};svmin=q['hornR']+2*rs
 def par(x):return {**q,'Sv':float(x[0]),'Su':float(x[1])}
 def con(x):
  qq=par(x);t,z=taus(qq);return np.r_[x[2]-t.ravel(),x[2]+t.ravel(),constraints(qq)]
 rng=np.random.default_rng(51);seeds=[[svmin,r['geometry']['Su']],[svmax,0],[svmin,-30],[svmin,30]]+[[rng.uniform(svmin,svmax),rng.uniform(-sumax,sumax)] for _ in range(8)]
 fits=[]
 for seed in seeds:
  x=np.r_[seed,max(abs(taus(par(seed))[0]).ravel())+1];fit=minimize(lambda x:x[2],x,method='SLSQP',bounds=[(svmin,svmax),(-sumax,sumax),(0,10000)],constraints=[{'type':'ineq','fun':con}],options={'ftol':1e-9,'maxiter':200})
  if min(con(fit.x))>=-1e-5:fits.append(fit)
 if not fits:return {'rs':rs,'feasible':False}
 best=min(fits,key=lambda x:x.fun);rec=copy.deepcopy(r);rec['geometry'].update(rs=rs,Sv=float(best.x[0]),Su=float(best.x[1]));lab.evaluate(rec,6001)
 return {'record':rec,'objective':float(best.fun),'starts':len(seeds),'success':bool(best.success),'message':best.message,'constraints':constraints(par(best.x)).tolist()}

def relaxed():
 q={**p,'rs':38.1};svmin=q['hornR']+2*q['rs']
 def unpack(x):return {**q,'Sv':float(x[0]),'Su':float(x[1])}
 def constraints2(x):
  qq=unpack(x);z=lab.profile(qq,401);ix=np.searchsorted(z['theta'],np.linspace(qq['te'],qq['tc'],401));pp=np.array(x[2:4]);t=np.array([(row@pp+row@ks*z['delta'])*z['A']-m*qq['g']*z['J']+z['gravityOffset'] for m,row in zip(mass,masks)])[:,ix]
  ans=[x[4]-t.ravel(),x[4]+t.ravel()]
  for i,s in enumerate(r['springs']):
   a=lab.profile({**qq,'te':-50 if masks[0,i] else qq['te']},9);low=a['low'] if masks[0,i] else a['workingLow'];hi=a['high'] if masks[0,i] else a['workingHigh'];xx=pp[i]/ks[i];ans.append([xx+low,s['xmax']-xx-hi])
  return np.concatenate(ans)
 fits=[]
 for sv,su in [(svmin,38.1),(svmin,70),(180,50),(250,50)]:
  x=[sv,su,*pre,100];fit=minimize(lambda x:x[4],x,method='SLSQP',bounds=[(svmin,400),(-150,150),(0,4000),(0,8000),(0,10000)],constraints=[{'type':'ineq','fun':constraints2}],options={'ftol':1e-9,'maxiter':200})
  if min(constraints2(fit.x))>=-1e-5:fits.append(fit)
 best=min(fits,key=lambda x:x.fun);rec=copy.deepcopy(r);rec['geometry'].update(rs=38.1,Sv=float(best.x[0]),Su=float(best.x[1]));
 for s,p0 in zip(rec['springs'],best.x[2:4]):s['p0']=float(p0)
 lab.evaluate(rec,6001);return {'record':rec,'objective':float(best.fun),'diagnostic':'Preloads allowed to change; not the requested Su/Sv-only fit','starts':4}
results={'baseline':base,'fixed_preload_1p5':solve(38.1),'free_position_1p5':solve(38.1,400,150),'preload_refit_diagnostic':relaxed()}
for name,res in results.items():
 rec=res if name=='baseline' else res.get('record')
 if rec:print(name,json.dumps({'geometry':rec['geometry'],'cases':rec['cases'],'metrics':rec['metrics']},indent=2))
 else:print(name,res)
(W/'results.json').write_text(json.dumps(results,indent=2),encoding='utf8');assert hash0==hashlib.sha256(store.BOOK.read_bytes()).hexdigest()