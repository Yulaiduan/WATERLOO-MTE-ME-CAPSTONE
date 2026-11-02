"""Catalogue cartridge search. mm, N, N/mm, kg, deg, Nm; SciPy required.

One cable and fixed common/per-spring preloads; cases change only enabled slots.
Bounded catalogue/geometry search + exact linear minimax preload solves. Not an
exhaustive global optimum or a fatigue/dynamic spring qualification.
"""
from __future__ import annotations
import hashlib,json,math,pathlib,time,zipfile,xml.etree.ElementTree as ET
import numpy as np
from scipy.optimize import linprog,nnls,minimize

HERE=pathlib.Path(__file__).resolve().parent
CATALOGUE=HERE.parent.parent/'springs'/'outputs'/'2026-10-28-mmc-springs'/'mmc-spring-catalogue.xlsx'
R=math.pi/180; TAU=2*math.pi

def read_catalogue(path=CATALOGUE):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    records=[]
    with zipfile.ZipFile(path) as z:
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        for typ,index in [('C',1),('E',2)]:
            rows=[]
            for row in ET.fromstring(z.read(f'xl/worksheets/sheet{index}.xml')).findall('m:sheetData/m:row',ns):
                cells={}
                for c in row:
                    key=''.join(x for x in c.get('r','') if x.isalpha());v=c.find('m:v',ns)
                    val=''.join(c.find('m:is',ns).itertext()) if c.get('t')=='inlineStr' else ss[int(v.text)] if c.get('t')=='s' and v is not None else v.text if v is not None else None
                    if c.get('t') not in ('s','inlineStr') and val is not None:
                        try:val=float(val)
                        except ValueError:pass
                    cells[key]=val
                rows.append(cells)
            headers=rows[0]; statuscol=next((k for k,v in headers.items() if 'status' in str(v).lower()),None)
            for row in rows[1:]:
                keys=['id','part','url','energy','k','travel','fmax','lmin','lmax','free','initial','od']
                d=dict(zip(keys,[row.get(chr(65+i)) for i in range(12)]));d['type']=typ;d['status']=str(row.get(statuscol,''))
                d['url']='https://www.mcmaster.com/'+str(d['part'])+'/'
                if typ=='C':d['initial']=0.
                numeric=['energy','k','travel','fmax','lmin','lmax','free','initial']
                d['eligible']=all(isinstance(d[k],(int,float)) and math.isfinite(d[k]) for k in numeric) and d['k']>0 and d['travel']>0 and d['fmax']>d['initial']>=0 and d['energy']>0 and not any(s in d['status'].lower() for s in ['rubber','cut','assort','nonlinear','overload'])
                if d['eligible']:
                    d['xmax']=min(d['travel'],d['free']-d['lmin'] if typ=='C' else d['lmax']-d['free'],(d['fmax']-d['initial'])/d['k'],(math.sqrt(d['initial']**2+2000*d['k']*d['energy'])-d['initial'])/d['k'])
                    d['eligible']=d['xmax']>0
                records.append(d)
    return records

def roots(p,A,B,c):
    mag=math.hypot(A,B);out=[]
    if mag<1e-10 or abs(c)>mag+1e-10:return out
    phase=math.atan2(B,A);a=math.acos(max(-1,min(1,c/mag)))
    for x in [phase+a,phase-a]:
        for j in range(math.ceil(((p['te']+p['nu'])*R-x)/TAU),math.floor(((p['tc']+p['nu'])*R-x)/TAU)+1):out.append((x+j*TAU)/R-p['nu'])
    return out

def geometry(p,theta):
    t=np.asarray(theta,dtype=float);phi=(t+p['nu'])*R;r=p['hornR'];u=p['Su'];v=p['Sv'];rs=p['rs']
    hx=r*np.cos(phi);hy=r*np.sin(phi);vx=hx-u;vy=hy-v;d=np.hypot(vx,vy)
    if np.any(d<=rs+1e-8):raise ValueError('Horn pin lies inside/on S at the reference or working travel.')
    if rs==0:return d,hy*(-vx/d)-hx*(-vy/d),np.zeros_like(t),d
    if math.hypot(u,v)<r:polar=phi+np.arctan2(u*np.sin(phi)-v*np.cos(phi),r-u*np.cos(phi)-v*np.sin(phi))
    else:
        center=math.atan2(-v,-u);raw=np.arctan2(vy,vx);polar=center+np.arctan2(np.sin(raw-center),np.cos(raw-center))
    psi=polar-np.arccos(rs/d);a=np.sqrt(d*d-rs*rs);qx=u+rs*np.cos(psi);qy=v+rs*np.sin(psi)
    return a+rs*psi,hy*(qx-hx)/a-hx*(qy-hy)/a,psi,d

def profile(p,count=161):
    rad=math.hypot(p['Su'],p['Sv']);ts=[p['te'],p['tc']]
    for A,B,c in [(-p['Sv'],p['Su'],p['rs']),(-p['Sv'],p['Su'],-p['rs']),(p['Su'],p['Sv'],rad),(p['Su'],p['Sv'],-rad),(p['Su'],p['Sv'],p['hornR']-p['rs']),(p['Su'],p['Sv'],p['hornR']+p['rs'])]:ts+=roots(p,A,B,c)
    critical=np.array(sorted(set(ts)));c0,_,psi0,d0=geometry(p,[90]);cs,_,ps,_=geometry(p,critical)
    if p['rs']>0 and np.ptp(ps)>TAU+1e-8:raise ValueError('Working range requires more than one full wrap.')
    theta=np.unique(np.r_[np.linspace(p['te'],p['tc'],count),critical]);c,a,_,_=geometry(p,theta);delta=c-c0[0]
    q=p['ra']/p['rb'];b=(p['phi0']+(180-theta)*(q-1))*R;du=p['L2']*np.sin(theta*R)+p['L3']*(1-q)*np.sin(b);dv=-p['L2']*np.cos(theta*R)-p['L3']*(1-q)*np.cos(b)
    J=(-math.sin(p['alpha']*R)*du+math.cos(p['alpha']*R)*dv)/1000
    JB=(-math.sin(p['alpha']*R)*p['L2']*np.sin(theta*R)-math.cos(p['alpha']*R)*p['L2']*np.cos(theta*R))/1000
    offset=p['g']*((.5*p['m2']+.5*p['m3']+p['m5'])*JB+(.5*p['m3']+p['m6'])*J)
    return dict(theta=theta,delta=delta,A=a/1000,J=J,gravityOffset=offset,low=min(0,float(min(cs)-c0[0])),high=max(0,float(max(cs)-c0[0])),stroke=float(np.ptp(cs)),l0=float(d0[0]),le=float(geometry(p,[p['te']])[3][0]),deltae=float(geometry(p,[p['te']])[0][0]-c0[0]))

def normalized(raw):
    out=json.loads(json.dumps(raw));p=out['parameters'];s=out['settings']
    for k in ['L2','L3','ra','rb','phi0','alpha','te','tc','g','m1','m2','m3','m5','m6']:
        if not isinstance(p.get(k),(int,float)) or not math.isfinite(p[k]):raise ValueError('Invalid system value '+k)
    if not (90<=p['te']<p['tc']<=270 and p['g']>0 and p['L2']>0 and p['L3']>0 and p['ra']>0 and p['rb']>0 and all(p[k]>=0 for k in ['m1','m2','m3','m5','m6'])):raise ValueError('Invalid mass / leg geometry / working angle.')
    for k in ['hornR','rs','nu','Sv','Su','bulk','svMin','svMax','suMin','suMax']:
        if not isinstance(s.get(k),(int,float)) or not math.isfinite(s[k]):raise ValueError('Invalid lab value '+k)
    if s['hornR']<=0 or s['rs']<0 or s['bulk']<0 or not 0<=s['svMin']<=s['svMax'] or s['suMin']>s['suMax']:raise ValueError('Invalid spring geometry / bounds.')
    if s['type'] not in ['C','E'] or not isinstance(s['m'],int) or not 1<=s['m']<=12:raise ValueError('Use 1–12 physical spring slots.')
    if not 1<=len(s['payloads'])<=8 or any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 for x in s['payloads']):raise ValueError('Use 1–8 nonnegative payload cases.')
    if not isinstance(s.get('solutions'),int) or not 1<=s['solutions']<=50:raise ValueError('Request 1–50 solutions.')
    s['trials']=max(50,min(2000,int(s.get('trials',300))))
    return out

def preload_fit(p,parts,masks,bulk,count=161):
    z=profile(p,count);ks=np.array([x['k'] for x in parts]);initial=np.array([x['initial'] for x in parts]);E=np.array(masks,dtype=float);masses=np.array(p['_caseMasses'])
    lo=np.maximum(bulk,-z['low'])*ks+initial;hi=(np.array([x['xmax'] for x in parts])-z['high'])*ks+initial
    if np.any(hi<lo-1e-8):return None
    A=np.vstack([z['A'][:,None]*row for row in E]);target=np.concatenate([mass*p['g']*z['J']-z['gravityOffset']-z['A']*z['delta']*float(row@ks) for mass,row in zip(masses,E)])
    result=linprog(np.r_[np.zeros(len(parts)),1.],A_ub=np.vstack([np.c_[A,-np.ones(len(A))],np.c_[-A,-np.ones(len(A))]]),b_ub=np.r_[target,-target],bounds=[*zip(lo,hi),(0,None)],method='highs')
    if not result.success:return None
    return float(result.fun),result.x[:-1],z

def evaluate(record,count=1201):
    p={**record['parameters'],**record['geometry']};mT=4*sum(p[k] for k in ['m1','m2','m3','m5','m6']);p['_caseMasses']=[(mT+x)/4 for x in record['payloads']];z=profile(p,count)
    slots=record['springs'];ks=np.array([x['k'] for x in slots]);p0=np.array([x['p0'] for x in slots]);x0=(p0-np.array([x['initial'] for x in slots]))/ks
    valid=True;violations=[]
    for i,(s,x) in enumerate(zip(slots,x0)):
        if x<record['bulk']-1e-6 or x+z['low']<-1e-6 or x+z['high']>s['xmax']+1e-6:valid=False;violations.append(f'Slot {i+1} exceeds a catalogue/preload limit.')
        s.update(x0=float(x),individualMm=float(x-record['bulk']),pe=float(s['p0']+s['k']*z['deltae']),l0=float(s['free']+(-1 if s['type']=='C' else 1)*x),le=float(s['free']+(-1 if s['type']=='C' else 1)*(x+z['deltae'])),usedTravelMm=float(x+z['high']),marginMm=float(s['xmax']-x-z['high']))
    cases=[];worst=0
    for mass,mask,payload in zip(p['_caseMasses'],record['masks'],record['payloads']):
        row=np.array(mask);F=float(row@p0)+float(row@ks)*z['delta'];tau=F*z['A']-mass*p['g']*z['J']+z['gravityOffset'];worst=max(worst,float(max(abs(tau))))
        cases.append(dict(payload=payload,mL=mass,p0=float(row@p0),pe=float(row@p0+row@ks*z['deltae']),positive=max(0,float(max(tau))),negative=min(0,float(min(tau))),minimum=float(min(tau)),maximum=float(max(tau)),maxAbs=float(max(abs(tau))),rms=float(np.sqrt(np.mean(tau*tau)))))
    record.update(cases=cases,metrics=dict(worstNm=worst,l0=z['l0'],le=z['le'],stroke=z['stroke'],valid=valid,violations=violations,verificationPoses=len(z['theta'])))
    return record

def solve(raw,catalogue=None):
    req=normalized(raw);s=req['settings'];base=req['parameters'];mT=4*sum(base[k] for k in ['m1','m2','m3','m5','m6']);masses=[(mT+x)/4 for x in s['payloads']]
    if any(x<=0 for x in masses):raise ValueError('Each payload case must have positive per-leg mass.')
    cat=[x for x in (catalogue or read_catalogue()) if x['type']==s['type'] and x['eligible']];rng=np.random.default_rng(64061);n=len(masses);m=s['m'];best={};start=time.monotonic();candidates=0
    for trial in range(s['trials']):
        sv=float(np.clip(s['Sv'],s['svMin'],s['svMax'])) if trial==0 else float(rng.uniform(s['svMin'],s['svMax']));su=float(np.clip(s['Su'],s['suMin'],s['suMax'])) if trial==0 else float(rng.uniform(s['suMin'],s['suMax']))
        p={**base,**{k:s[k] for k in ['hornR','rs','nu']},'Sv':sv,'Su':su,'_caseMasses':masses}
        try:z=profile(p,81)
        except ValueError:continue
        matrix=np.c_[z['A']*z['delta'],z['A']];targets=np.array([np.linalg.lstsq(matrix,mass*p['g']*z['J']-z['gravityOffset'],rcond=None)[0] for mass in masses]);K=np.maximum(.001,targets[:,0]);P=np.maximum(0,targets[:,1])
        feasible=[x for x in cat if x['xmax']>=max(s['bulk'],-z['low'])+z['high']-1e-8]
        if not feasible:continue
        slots=min(m, max(1,n)) if trial%5==0 else m
        if trial%3==0:
            # Baseline subset shared by all cases, increments enabled by mass order.
            order=np.argsort(masses);E=np.zeros((n,slots));groups=np.array_split(np.arange(slots),min(n,slots))
            for rank,j in enumerate(order):
                for group in groups[:min(rank+1,len(groups))]:E[j,group]=1
        elif trial%3==1:
            E=(rng.random((n,slots))<.6).astype(float)
            for j in range(n):E[j,rng.integers(slots)]=1
            for i in range(slots):
                if not E[:,i].any():E[rng.integers(n),i]=1
        else:
            E=np.zeros((n,slots))
            for i in range(slots):E[i%n,i]=1
            for j in range(n):
                if not E[j].any():E[j,rng.integers(slots)]=1
        desired=nnls(E,K)[0];desiredP=nnls(E,P)[0];parts=[]
        for i in range(slots):
            rate=max(.001,desired[i]);pre=desiredP[i];ranked=sorted(feasible,key=lambda x:abs(math.log(x['k']/rate))+.2*max(0,pre-(x['initial']+x['k']*(x['xmax']-z['high'])))/max(1,pre))
            pool=ranked[:min(len(ranked),8)];parts.append(pool[int(rng.integers(len(pool)))])
        result=preload_fit(p,parts,E.tolist(),s['bulk'],81);candidates+=1
        if result is None:continue
        score,preloads,_=result;signature=json.dumps(sorted((x['id'],tuple(E[:,i])) for i,x in enumerate(parts)))
        record=dict(parameters=base,geometry={k:p[k] for k in ['hornR','rs','nu','Sv','Su']},bulk=s['bulk'],payloads=s['payloads'],masks=E.astype(int).tolist(),springs=[{**x,'p0':float(preloads[i])} for i,x in enumerate(parts)],settings=s,favorite=False,method='Bounded catalogue/geometry search + minimax linear preload fit',score=score)
        if signature not in best or score<best[signature]['score']:best[signature]=record
    shortlist=sorted(best.values(),key=lambda x:x['score'])[:max(s['solutions']*2,8)]
    for record in shortlist:
        parts=record['springs'];E=record['masks'];p={**base,**record['geometry'],'_caseMasses':masses};baseline=preload_fit(p,parts,E,s['bulk'],1201)
        def objective(x):
            try:r=preload_fit({**p,'Sv':float(x[0]),'Su':float(x[1])},parts,E,s['bulk'],161)
            except ValueError:return 1e6
            return r[0] if r else 1e6
        bounds=[(s['svMin'],s['svMax']),(s['suMin'],s['suMax'])];seed=[p['Sv'],p['Su']];free=[j for j,(lo,hi) in enumerate(bounds) if hi>lo]
        if free:
            def coordinates(x):
                full=seed.copy()
                for j,v in zip(free,x):full[j]=float(v)
                return full
            refined=minimize(lambda x:objective(coordinates(x)),[seed[j] for j in free],method='Powell',bounds=[bounds[j] for j in free],options={'maxiter':12,'maxfev':220,'xtol':.002,'ftol':1e-5})
            fitted=coordinates(refined.x);p.update(Sv=fitted[0],Su=fitted[1])
        r=preload_fit(p,parts,E,s['bulk'],1201)
        if r is not None and (baseline is None or r[0]<=baseline[0]):
            record['geometry'].update(Sv=p['Sv'],Su=p['Su'])
            for part,force in zip(parts,r[1]):part['p0']=float(force)
        elif baseline is not None:
            for part,force in zip(parts,baseline[1]):part['p0']=float(force)
        evaluate(record)
    valid=sorted([x for x in shortlist if x['metrics']['valid']],key=lambda x:x['metrics']['worstNm'])[:s['solutions']]
    return dict(solutions=valid,elapsedSeconds=time.monotonic()-start,trials=s['trials'],preloadFits=candidates,catalogueEligible=len(cat),message=f'{len(valid)} feasible cartridges; bounded search, not a certified global optimum. Catalogue force, travel, length and energy limits enforced.')
