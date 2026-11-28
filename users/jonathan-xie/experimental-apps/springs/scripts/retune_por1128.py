"""Retune fixed S0110 FOX pair on corrected DP20. Run python -B scripts/retune_por1128.py from the springs folder.
Inputs: DP20 and preserved S0110, kg/mm/N/Nm/deg. Outputs candidate JSON, no app writes.
Model: 2:1, one spring per payload, taut inversion, catalogue/clearance bounds.
"""
import pathlib,json,copy,sys,math,time,importlib.util
import numpy as np
from scipy.optimize import differential_evolution,minimize,linprog
R=pathlib.Path(__file__).resolve().parents[1];V=R.parent/'vsl-solver/v7';sys.path.insert(0,str(V));import spring_lab as lab,spring_store,vsl_server
W=R/'.work/por-20261128';W.mkdir(parents=True,exist_ok=True)
ref=next(x for x in spring_store.read()['solutions'] if x['id']=='S0110');dp=next(x for x in vsl_server.load_library(vsl_server.DEFAULT_BOOK)['rows'] if x['dp']==20);base=copy.deepcopy(dp['snapshot']['parameters']);base.update(m2=1.98,m3=.92);parts=ref['springs'];rh=ref['geometry']['hornR'];ks=np.array([x['k'] for x in parts]);masses=[sum(base[k] for k in ['m1','m2','m3','m5','m6'])+payload/4 for payload in [0,70]];start=time.monotonic();records=[]
for hand,no in [('cw',201),('ccw',202)]:
 calls=[0]
 def geo(x):
  rad=rh+35+float(x[0]);a=float(x[1])*math.pi/180;return {**base,**ref['geometry'],'Sv':rad*math.cos(a),'Su':rad*math.sin(a),'pulleyWrap':hand}
 def shapes(x,n=241):
  p=geo(x);z=lab.profile(p,n);inv=lab.profile({**p,'te':-50},9);ix=np.searchsorted(z['theta'],np.linspace(base['te'],base['tc'],n));return p,z,inv,ix
 def fitted(x,n=161,details=False):
  calls[0]+=1
  try:p,z,inv,ix=shapes(x,n)
  except ValueError:return None if details else 1e5
  if p['Sv']>300:return None if details else 1e4+p['Sv']
  lo=np.array([max(0.,-inv['low'])*ks[0]+1e-5,max(0.,-z['workingLow'])*ks[1]+1e-5]);hi=np.array([(parts[0]['xmax']-inv['high'])*ks[0],(parts[1]['xmax']-z['workingHigh'])*ks[1]])
  if np.any(hi<lo):return None if details else 10000+max(lo-hi)
  A=z['A'][ix];target=np.array([m*base['g']*z['J'][ix]-z['gravityOffset'][ix]-A*k*z['delta'][ix] for m,k in zip(masses,ks)])
  matrix=np.zeros((2*len(A),2));matrix[:len(A),0]=A;matrix[len(A):,1]=A
  lp=linprog([0,0,1],A_ub=np.r_[np.c_[matrix,-np.ones(len(matrix))],np.c_[-matrix,-np.ones(len(matrix))]],b_ub=np.r_[target.ravel(),-target.ravel()],bounds=[*zip(lo,hi),(0,None)],method='highs')
  if not lp.success:return None if details else 1e5
  return (float(lp.fun),lp.x[:2],p,z,inv,ix) if details else float(lp.fun)
 bounds=[(0,205),((.00001 if hand=='cw' else -70),(70 if hand=='cw' else -.00001))]
 opt=differential_evolution(fitted,bounds,seed=1128201+no,popsize=14,maxiter=100,tol=1e-8,polish=False,updating='immediate');seed=opt.x;f=fitted(seed,601,True)
 if f is None:raise RuntimeError('No feasible '+hand+' fit')
 x0=[*seed,*f[1],f[0]+.00001]
 def constraints(x,n=601):
  try:p,z,inv,ix=shapes(x[:2],n)
  except ValueError:return np.full(4*n+5,-1e6)
  out=[300-p['Sv']]
  for j in range(2):
   tau=z['A'][ix]*(x[2+j]+ks[j]*z['delta'][ix])-masses[j]*base['g']*z['J'][ix]+z['gravityOffset'][ix];low=inv['low'] if j==0 else z['workingLow'];high=inv['high'] if j==0 else z['workingHigh'];out.extend(x[4]-tau);out.extend(x[4]+tau);out.extend([x[2+j]/ks[j]+low-1e-7,parts[j]['xmax']-x[2+j]/ks[j]-high])
  return np.array(out)
 final=minimize(lambda x:x[4],x0,method='SLSQP',bounds=[*bounds,(0,parts[0]['fmax']),(0,parts[1]['fmax']),(0,10000)],constraints=[{'type':'ineq','fun':constraints}],options={'maxiter':250,'ftol':1e-11})
 best=final.x if min(constraints(final.x))>=-1e-6 else np.array(x0);p=geo(best[:2]);r=copy.deepcopy(ref);r.update(id='S'+str(no).zfill(4),group='11/28 POR',sourceDp=20,parameters=base,geometry={k:p[k] for k in [*ref['geometry'].keys(),'pulleyWrap']},campaign='por-20261128',method='Fixed S0110 FOX pair and horn; two-dimensional global screen then constrained minimax refinement',favorite=no==201);r['settings'].update({**r['geometry'],'rhMin':rh,'rhMax':rh,'hornR':rh,'suMin':0 if hand=='cw' else -300,'suMax':300 if hand=='cw' else 0,'svMin':0,'svMax':300,'pulleyWrap':hand});r['linkMassConvention']='m2-femur-m3-tibia/v1'
 for spring,force in zip(r['springs'],best[2:4]):spring['p0']=float(force)
 lab.evaluate(r,20001);r['score']=r['metrics']['worstNm'];r['settings']['p0']=r['cases'][0]['p0'];r.pop('savedAt',None);zz=lab.profile(p,20001);ii=lab.profile({**p,'te':-50},20001);r['springForcePeaks']=[float(part['p0']+part['k']*(ii['high'] if j==0 else zz['workingHigh'])) for j,part in enumerate(r['springs'])];r['forcePeaks']=[force/2 for force in r['springForcePeaks']];r['workingForcePeaks']=[float(part['p0']+part['k']*zz['workingHigh'])/2 for part in r['springs']];r['settings']['p0']=r['springs'][0]['p0'];r['rank']=no-200;r['routeName']='Right / clockwise' if hand=='cw' else 'Left / counterclockwise';records.append(r);(W/f'S{no:04}.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps({'id':r['id'],'route':hand,'geometry':r['geometry'],'preloads':[s['p0'] for s in r['springs']],'cases':r['cases'],'metrics':r['metrics'],'calls':calls[0],'seconds':time.monotonic()-start}),flush=True)
(W/'solutions.json').write_text(json.dumps(records,indent=2),encoding='utf8')
