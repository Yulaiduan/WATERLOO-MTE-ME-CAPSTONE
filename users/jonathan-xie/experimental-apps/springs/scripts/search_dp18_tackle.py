"""DP18 2:1 moving-pulley bounded compression-only one-active-spring search.
Run: python -B scripts/search_dp18.py from springs root (numpy/scipy).
Inputs: DP18 in V7 configs, dated catalogue JSON/XLSX; mm,N,N/mm,kg,deg,Nm.
Outputs: candidate JSON in .work/dp18-tackle-20261122; no saved solution writes.
Limits: nominal static multistart fits, no exhaustive/global or fatigue guarantee.
"""
import sys,pathlib,json,copy,math,time,collections
import numpy as np
from scipy.optimize import minimize,linprog
R=pathlib.Path(__file__).resolve().parents[1];V=R.parent/'vsl-solver/v7';sys.path.insert(0,str(V));import spring_lab as lab,vsl_server, spring_store
W=R/'.work/dp18-tackle-20261122';W.mkdir(parents=True,exist_ok=True)
DP=next(x for x in vsl_server.load_library(vsl_server.DEFAULT_BOOK)['rows'] if x['dp']==18);base=DP['snapshot']['parameters'];masses=[sum(base[k] for k in ['m1','m2','m3','m5','m6'])+load/4 for load in [0,70]]
cat=lab.read_catalogue()
cat=[a for a in cat if a['eligible'] and a['type']=='C' and a['lmax']<210 and a['xmax']>0]
for a in cat:a.setdefault('source','MC');a.setdefault('supplier','McMaster-Carr')
unique={}
for a in cat:
 sig=(a['source'],*[round(a[k],5) for k in ['k','free','xmax','fmax']]);unique.setdefault(sig,a)
cat=list(unique.values());print('catalogue',dict(collections.Counter(a['source'] for a in cat)),flush=True)
# Broad position bounds prevent the previous +/-30 mm restriction dominating rs.
settings={**DP['snapshot']['springLab']['settings'],'type':'C','m':2,'payloads':[0,70],'springReduction':2,'circleClearanceMm':15,'rs':20,'rhMin':60,'rhMax':70,'hornR':65,'nu':0,'svMin':0,'svMax':300,'suMin':-300,'suMax':300,'requireInversion':True,'theta2fTarget':-50,'caseSpecificTravel':True,'bulk':0,'requireNesting':False,'solutions':5}
p0={**base,'rs':20,'nu':0,'hornR':65,'springReduction':2,'circleClearanceMm':15,'_caseMasses':masses}

def shapes(v,n=121):
 rad=float(v[0]+35+v[1]);angle=float(v[2])*math.pi/180;p={**p0,'hornR':float(v[0]),'Sv':rad*math.cos(angle),'Su':rad*math.sin(angle)};z=lab.profile(p,n);ix=np.searchsorted(z['theta'],np.linspace(p['te'],p['tc'],n));zi=lab.profile({**p,'te':-50},9);return p,z,ix,zi

def onefit(a,z,ix,zi,case):
 k=a['k'];low=zi['low'] if case==0 else z['workingLow'];high=zi['high'] if case==0 else z['workingHigh'];lo=max(0,-low)*k;hi=(a['xmax']-high)*k
 if hi<lo:return None
 A=z['A'][ix];target=masses[case]*base['g']*z['J'][ix]-z['gravityOffset'][ix]-A*k*z['delta'][ix]
 lp=linprog([0,1],A_ub=np.r_[np.c_[A,-np.ones(len(A))],np.c_[-A,-np.ones(len(A))]],b_ub=np.r_[target,-target],bounds=[(lo,hi),(0,None)],method='highs')
 return (float(lp.fun),float(lp.x[0])) if lp.success else None
# Seed all viable unloaded springs from representative geometries, not just nearest rates.
rng=np.random.default_rng(1800254);geos=[[65,0,10],[60,0,25],[70,0,35],[65,25,20],[65,70,25],[65,150,30]]+[[rng.uniform(60,70),rng.uniform(0,150),rng.uniform(-15,55)] for _ in range(24)]
seeds={}
for v in geos:
 p,z,ix,zi=shapes(v,61)
 for a in cat:
  f=onefit(a,z,ix,zi,0)
  if f and (a['id'] not in seeds or f[0]<seeds[a['id']][0]):seeds[a['id']]=(f[0],v,f[1])
print('viable unloaded',len(seeds),flush=True)
# A generous screened set, retaining candidates across all suppliers.
rank=sorted([a for a in cat if a['id'] in seeds],key=lambda a:seeds[a['id']][0]);selected=rank[:100]
for source in set(a['source'] for a in rank):
 for a in [a for a in rank if a['source']==source][:8]:
  if a not in selected:selected.append(a)
candidates=[]
for no,a in enumerate(selected):
 seed=seeds[a['id']];v=seed[1];start=[*v,seed[2],seed[0]+.01];k=a['k']
 def con(x):
  p,z,ix,zi=shapes(x[:3]);A=z['A'][ix];tau=A*(x[3]+k*z['delta'][ix])-masses[0]*base['g']*z['J'][ix]+z['gravityOffset'][ix]
  return np.r_[x[4]-tau,x[4]+tau,x[3]/k+zi['low'],a['xmax']-x[3]/k-zi['high'],300-p['Sv']]
 best=minimize(lambda x:x[4],start,method='SLSQP',bounds=[(60,70),(0,205),(-70,70),(0,a['fmax']),(0,10000)],constraints=[{'type':'ineq','fun':con}],options={'maxiter':110,'ftol':2e-8})
 if min(con(best.x)) < -1e-5:continue
 p,z,ix,zi=shapes(best.x[:3],241);f0=onefit(a,z,ix,zi,0)
 if not f0:continue
 for category in ['mixed','single']:
  options=[]
  for b in cat:
   if (a['supplier']==b['supplier'])!=(category=='single'):continue
   f1=onefit(b,z,ix,zi,1)
   if f1:options.append((max(f0[0],f1[0]),f1[0],b,f1[1]))
  for score,err,b,pre in sorted(options,key=lambda x:x[:2])[:8]:
   rec=dict(parameters=copy.deepcopy(base),geometry={key:p[key] for key in ['hornR','rs','nu','Sv','Su','springReduction','circleClearanceMm']},bulk=0,payloads=[0,70],masks=[[1,0],[0,1]],springs=[{**a,'p0':f0[1]},{**b,'p0':pre}],settings=copy.deepcopy(settings),sourceDp=18,group='DP18 - '+category+' supplier - 2:1 tackle',mode='swap',campaign='dp18-tackle-20261122',favorite=False,method='Unloaded spring multistart screen/refine; exhaustive payload spring screen at fitted geometry; pair refinement; bounded nominal search',score=score)
   candidates.append(rec)
 if no%10==0:print('fitted',no+1,'/',len(selected),'pairs',len(candidates),flush=True)
(W/'screened.json').write_text(json.dumps({'dp':DP,'settings':settings,'catalogueCount':len(cat),'candidates':candidates},indent=2),encoding='utf8')
print('SCREEN COMPLETE',len(candidates),flush=True)
# Refine the best distinct pair signatures jointly against both payload cases.
final=[]
for category in ['mixed','single']:
 pool=sorted([x for x in candidates if category+' supplier' in x['group']],key=lambda x:x['score']);seen=set();short=[]
 for a in pool:
  sig=tuple(s['id'] for s in a['springs'])
  if sig not in seen:seen.add(sig);short.append(a)
  if len(short)>=35:break
 for i,rec in enumerate(short):
  parts=rec['springs'];ks=np.array([s['k'] for s in parts]);geom=rec['geometry'];v=[geom['hornR'],math.hypot(geom['Sv'],geom['Su'])-geom['hornR']-35,math.degrees(math.atan2(geom['Su'],geom['Sv']))];x=[*v,*[s['p0'] for s in parts],rec['score']+.001]
  def con2(x):
   p,z,ix,zi=shapes(x[:3],241);ans=[300-p['Sv']]
   for j,s in enumerate(parts):
    tau=z['A'][ix]*(x[3+j]+s['k']*z['delta'][ix])-masses[j]*base['g']*z['J'][ix]+z['gravityOffset'][ix];low=zi['low'] if j==0 else z['workingLow'];hi=zi['high'] if j==0 else z['workingHigh'];ans.extend(x[5]-tau);ans.extend(x[5]+tau);ans.extend([x[3+j]/s['k']+low,s['xmax']-x[3+j]/s['k']-hi])
   return np.array(ans)
  opt=minimize(lambda x:x[5],x,method='SLSQP',bounds=[(60,70),(0,205),(-70,70),(0,parts[0]['fmax']),(0,parts[1]['fmax']),(0,10000)],constraints=[{'type':'ineq','fun':con2}],options={'maxiter':160,'ftol':1e-9})
  if min(con2(opt.x))>=-1e-5:
   p,*_=shapes(opt.x[:3]);rec['geometry']={key:p[key] for key in ['hornR','rs','nu','Sv','Su','springReduction','circleClearanceMm']}
   for s,force in zip(parts,opt.x[3:5]):s['p0']=float(force)
  lab.evaluate(rec,6001)
  if rec['metrics']['valid']:
   z=lab.profile({**base,**rec['geometry']},6001);inv=lab.profile({**base,**rec['geometry'],'te':-50},6001)
   rec['springForcePeaks']=[float(s['p0']+s['k']*max(zz['delta'])) for s,zz in zip(parts,[inv,z])];rec['forcePeaks']=[f/2 for f in rec['springForcePeaks']];rec['workingForcePeaks']=[float(s['p0']+s['k']*max(z['delta']))/2 for s in parts];final.append(rec)
  if i%10==0:print('refined',category,i+1,'/',len(short),flush=True)
for category in ['mixed','single']:
 group=sorted([x for x in final if category+' supplier' in x['group']],key=lambda x:(x['metrics']['worstNm'],x['cases'][0]['maxAbs']))[:5]
 for j,x in enumerate(group,1):x['rank']=j
 assert len(group)==5,(category,len(group))
 (W/(category+'.json')).write_text(json.dumps(group,indent=2),encoding='utf8');print(category,[(x['rank'],[s['id'] for s in x['springs']],round(x['metrics']['worstNm'],3),[round(f) for f in x['forcePeaks']]) for x in group],flush=True)