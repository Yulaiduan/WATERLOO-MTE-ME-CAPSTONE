/** Generalized VSL analytical design study. Load as a browser script, or import
 * in Node (globalThis.DesignStudyModel). Inputs: mm, deg, kg, N; outputs: signed
 * Nm, ideal belt tensions/reactions, profiles and bounded design alternatives.
 * Experimental open-belt planar statics; no spring, inertia, rolling, thermal,
 * structural or 3D clearance prediction. Search winners are domain-limited.
 */
(() => {
  'use strict';
  const R = Math.PI / 180;
  const add = (...vs) => vs.reduce((a, b) => [a[0] + b[0], a[1] + b[1]], [0, 0]);
  const mul = (v, s) => [v[0] * s, v[1] * s];
  const sub = (a, b) => add(a, mul(b, -1));
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
  const cross = (a, b) => a[0] * b[1] - a[1] * b[0];
  const norm = v => Math.hypot(...v);
  const clone = p => JSON.parse(JSON.stringify(p));
  const DEFAULT_CONFIG = Object.freeze({
    L2:250,L3:250,ra:100,rb:60,rc:35,rd:35,re:35,rf:35,rw:200,
    phi0:0,te:100,tc:165,alpha:0,beta:13.5,
    m1:10,m2:0,m3:0,m5:0,m6:0,g:9.81,r5I:35,
    loadMode:'yz',Fy:100,Fz:100,Fn:0,Ft:0,Tab0:0,Tcd0:0,Tef0:0,
    startBuffer:Object.freeze({value:20,unit:'mm'}),endBuffer:Object.freeze({value:20,unit:'mm'}),
    targetTotal:325,targetMin:300,targetMax:350,minUsableTravel:200,preferredUsableTravel:250,chassisDepth:200,
    minClearance:20,enforceHipRim:true,maxDrift:150,minJacobian:5,samples:181,
    weighting:'time',cycleSeconds:2,objective:'peak',loadCases:'lateral-envelope'
  });
  function ratios(p) { return {q23:p.L2/p.L3,qab:p.ra/p.rb,qcd:p.rc/p.rd,qef:p.re/p.rf}; }
  function resolveLoads(p) {
    const s=Math.sin(p.beta*R),c=Math.cos(p.beta*R);
    return p.loadMode==='yz'?{...p,Fn:p.Fy*s+p.Fz*c,Ft:p.Fy*c-p.Fz*s}:
      {...p,Fy:p.Fn*s+p.Ft*c,Fz:p.Fn*c-p.Ft*s};
  }
  function global(p,v) {const a=p.alpha*R;return [Math.cos(a)*v[0]+Math.sin(a)*v[1],-Math.sin(a)*v[0]+Math.cos(a)*v[1]];}
  function local(p,v) {return global({...p,alpha:-p.alpha},v);}
  function raw(p,theta2) {
    const q=ratios(p),t3=p.phi0+(180-theta2)*(q.qab-1),a=theta2*R,b=t3*R;
    const B=[-p.L2*Math.cos(a),-p.L2*Math.sin(a)];
    const C=add(B,[-p.L3*Math.cos(b),-p.L3*Math.sin(b)]);
    const dB=[p.L2*Math.sin(a),-p.L2*Math.cos(a)],d3=1-q.qab;
    const dC=add(dB,[d3*p.L3*Math.sin(b),-d3*p.L3*Math.cos(b)]);
    return {B,C,dB,dC,t3};
  }
  function kinematics(p,theta2=p.te) {
    const q=ratios(p),s=raw(p,theta2),e=raw(p,p.te),dt=theta2-p.te;
    const K=1-q.qab+q.qef*(q.qab-q.qcd),Cg=global(p,s.C),Bg=global(p,s.B);
    const nb=[Math.sin(p.beta*R),Math.cos(p.beta*R)],Pg=add(Cg,mul(nb,-p.rw));
    const [du,dv]=sub(s.C,e.C),[dy,dz]=global(p,[du,dv]);
    const direction=(h,v)=>Math.hypot(h,v)<1e-9?null:Math.atan2(h,v)/R;
    return {...s,...q,A:[0,0],P:local(p,Pg),Ag:[0,0],Bg,Cg,Pg,
      t2:theta2,t4:0,t5:(1-q.qcd)*dt,t6:K*dt,K,du,dv,dy,dz,
      dBg:global(p,s.dB),dCg:global(p,s.dC),
      gammaUV:direction(du,dv),gammaYZ:direction(dy,dz),
      groundGap:-Cg[1]+p.rw-p.chassisDepth,
      hipRimGap:norm(Cg)-p.rw
    };
  }
  function validateConfig(p) {
    const errors=[];
    for(const k of ['L2','L3','ra','rb','rc','rd','re','rf','rw','r5I','cycleSeconds'])
      if(!Number.isFinite(p[k])||p[k]<=0) errors.push(`${k} must be positive and finite.`);
    for(const k of ['m1','m2','m3','m5','m6','g','Tab0','Tcd0','Tef0','chassisDepth','minClearance','maxDrift','minJacobian','minUsableTravel','preferredUsableTravel'])
      if(!Number.isFinite(p[k])||p[k]<0) errors.push(`${k} must be nonnegative and finite.`);
    for(const k of ['te','tc'])if(!Number.isFinite(p[k])||p[k]<90||p[k]>180)errors.push(`${k} must be in [90,180] degrees.`);
    if(!(p.tc>p.te))errors.push('tc must be greater than te.');
    if(!Number.isFinite(p.alpha)||p.alpha<0||p.alpha>45)errors.push('alpha must be in [0,45] degrees.');
    if(!Number.isFinite(p.beta)||p.beta<0||p.beta>90)errors.push('beta must be in [0,90] degrees.');
    if(!Number.isFinite(p.phi0)||Math.abs(p.phi0)>180)errors.push('phi0 must be in [-180,180] degrees.');
    if(!['yz','nt'].includes(p.loadMode))errors.push('Unknown force convention.');
    for(const k of p.loadMode==='yz'?['Fy','Fz']:['Fn','Ft'])if(!Number.isFinite(p[k]))errors.push(`${k} must be finite.`);
    for(const k of ['startBuffer','endBuffer'])if(!p[k]||!['mm','deg'].includes(p[k].unit)||!Number.isFinite(p[k].value)||p[k].value<0)errors.push(`${k} requires nonnegative mm or deg.`);
    if(!Number.isFinite(p.targetMin)||!Number.isFinite(p.targetMax)||p.targetMin<=0||p.targetMax<p.targetMin)errors.push('Total-travel bounds must be positive and ordered.');
    if(!Number.isFinite(p.targetTotal)||p.targetTotal<p.targetMin||p.targetTotal>p.targetMax)errors.push('targetTotal must be inside the total-travel bounds.');
    if(!Number.isInteger(p.samples)||p.samples<31||p.samples>4001)errors.push('samples must be an integer in [31,4001].');
    if(!['angle','travel','time'].includes(p.weighting))errors.push('Unknown RMS weighting.');
    if(!['peak','rms'].includes(p.objective))errors.push('Unknown objective.');
    if(typeof p.enforceHipRim!=='boolean')errors.push('enforceHipRim must be boolean.');
    if(!['nominal','lateral-envelope'].includes(p.loadCases))errors.push('Unknown load-case policy.');
    if(p.loadCases==='lateral-envelope'&&p.loadMode!=='yz')errors.push('The lateral envelope requires global Fy/Fz driving inputs.');
    for(const [a,b,L] of [['ra','rb','L2'],['rc','rd','L2'],['re','rf','L3']])if(p[a]+p[b]>=p[L])errors.push(`${a}/${b} pitch circles overlap or touch.`);
    return errors;
  }
  function belt(O,C,r1,r2,side,delta,preload,name) {
    const D=norm(sub(C,O));if(!(D>r1+r2))return null;
    const e=mul(sub(C,O),1/D),n=[-e[1],e[0]],k=(r1-r2)/D,h=Math.sqrt(1-k*k);
    const U=preload+Math.max(delta,0),L=preload+Math.max(-delta,0),spans=[];
    for(const [tag,sgn,T] of [['U',side,U],['L',-side,L]]) {
      const normal=add(mul(e,k),mul(n,sgn*h)),dir=add(mul(e,h),mul(n,-sgn*k));
      spans.push({tag,T,normal,dir,left:{pos:add(O,mul(normal,r1)),vec:mul(dir,T)},right:{pos:add(C,mul(normal,r2)),vec:mul(dir,-T)}});
    }
    return {name,O,C,r1,r2,side,delta,U,L,active:Math.abs(delta)<1e-10?'balanced':delta>0?'U':'L',
      spans,Fleft:add(...spans.map(s=>s.left.vec)),Fright:add(...spans.map(s=>s.right.vec)),
      Mleft:-side*r1*delta/1000,Mright:side*r2*delta/1000};
  }
  function statics(config,theta2=config.te) {
    const p=resolveLoads(config),s=kinematics(p,theta2),q=ratios(p),{A,B,C,dB,dC}=s,l3=sub(C,B);
    const weight=m=>local(p,[0,-m*p.g]),W1=weight(p.m1),W2=weight(p.m2),W3=weight(p.m3),W5=weight(p.m5),W6=weight(p.m6);
    const FcontactG=[p.Fy,p.Fz],Fcontact=local(p,FcontactG),Mw=p.rw*p.Ft/1000;
    const ef=belt(B,C,p.re,p.rf,-1,p.rw*p.Ft/p.rf,p.Tef0,'ef');
    const cd=belt(A,B,p.rc,p.rd,1,-p.re/p.rd*(ef?.delta??0),p.Tcd0,'cd');
    if(!ef||!cd||p.ra+p.rb>=p.L2)return {...s,valid:false,reason:'Overlapping pulley pitch circles.'};
    const Fw=add(Fcontact,W6,ef.Fright),M3=cross(l3,Fw)+cross(mul(l3,.5),W3);
    const ab=belt(A,B,p.ra,p.rb,1,-M3/p.rb,p.Tab0,'ab');
    const F32=add(Fw,W3,ab.Fright),F25=mul(add(cd.Fright,ef.Fleft,W5),-1);
    const F12=mul(add(F32,mul(F25,-1),W2),-1),F14=mul(cd.Fleft,-1);
    const tau2=-(cross(B,add(F32,mul(F25,-1)))+cross(mul(B,.5),W2))/1000,tau4=p.rc*cd.delta/1000;
    const gravityWork=dot(W2,mul(dB,.5))+dot(W3,mul(add(dB,dC),.5))+dot(W5,dB)+dot(W6,dC);
    const tau2VW=-(dot(Fcontact,dC)+gravityWork)/1000-Mw*s.K;
    const Fground=add(F12,F14,mul(ab.Fleft,-1),mul(W1,-1));
    return {...s,valid:true,Fn:p.Fn,Ft:p.Ft,Fy:p.Fy,Fz:p.Fz,Fcontact,FcontactG,Mw,
      tau2,tau4,tau2VW,tau4VW:-Mw*q.qcd*q.qef,
      virtualWorkError:Math.abs(tau2-tau2VW),ab,cd,ef,Fw,F32,F25,F12,F14,Fground,
      W1,W2,W3,W5,W6,combinedTorque:Math.hypot(tau2,tau4)};
  }
  function inverseHeight(p,z,lo=p.te,hi=p.tc) {
    for(let i=0;i<55;i++){const m=(lo+hi)/2;if(kinematics(p,m).dz<z)lo=m;else hi=m;}return (lo+hi)/2;
  }
  function bufferAngle(p,key) {
    const b=p[key],start=key==='startBuffer';
    if(b.unit==='deg')return start?p.te+b.value:p.tc-b.value;
    const total=kinematics(p,p.tc).dz;
    if(b.value>=total)return start?p.tc:p.te;
    return inverseHeight(p,start?b.value:total-b.value);
  }
  function convertBuffer(config,key,unit) {
    if(!['startBuffer','endBuffer'].includes(key)||!['mm','deg'].includes(unit))throw Error('Unknown buffer or unit.');
    if(config[key].unit===unit)return config[key].value;
    const t=bufferAngle(config,key);
    return unit==='deg'?(key==='startBuffer'?t-config.te:config.tc-t):
      (key==='startBuffer'?kinematics(config,t).dz:kinematics(config,config.tc).dz-kinematics(config,t).dz);
  }
  function profile(config) {
    const p=clone(config),errors=validateConfig(p);
    if(errors.length)return {config:p,feasible:false,reasons:errors,samples:[],physicalSamples:[],metrics:null,bounds:null};
    const n=p.samples,physicalSamples=Array.from({length:n},(_,i)=>kinematics(p,p.te+(p.tc-p.te)*i/(n-1)));
    const reasons=[];
    if(physicalSamples.some(s=>s.dCg[1]<=0))reasons.push('Vertical path reverses or reaches a singularity inside the physical window.');
    const totalTravel=physicalSamples.at(-1).dz;
    if(totalTravel<p.targetMin-1e-8||totalTravel>p.targetMax+1e-8)reasons.push(`Total capacity ${totalTravel.toFixed(2)} mm is outside ${p.targetMin}–${p.targetMax} mm.`);
    if(totalTravel<=0)return {config:p,feasible:false,reasons,samples:[],physicalSamples,metrics:null,bounds:null};
    const usableTe=bufferAngle(p,'startBuffer'),usableTc=bufferAngle(p,'endBuffer');
    if(usableTc<=usableTe) return {config:p,feasible:false,reasons:[...reasons,'Buffers consume the physical travel.'],samples:[],physicalSamples,metrics:null,bounds:{te:p.te,tc:p.tc,usableTe,usableTc}};
    const startMM=kinematics(p,usableTe).dz,endMM=totalTravel-kinematics(p,usableTc).dz;
    const usableTravel=totalTravel-startMM-endMM;
    if(usableTravel<p.minUsableTravel-1e-8)reasons.push('Usable travel is below the hard minimum.');
    const samples=Array.from({length:n},(_,i)=>{
      const u=i/(n-1),phase=p.weighting==='time'?10*u**3-15*u**4+6*u**5:u;
      const t=p.weighting!=='angle'?inverseHeight(p,startMM+usableTravel*phase,usableTe,usableTc):usableTe+(usableTc-usableTe)*phase;
      return {...statics(p,t),fraction:u,timeSeconds:u*p.cycleSeconds/2,usableDz:kinematics(p,t).dz-startMM};
    });
    const avg=f=>samples.reduce((sum,s,i)=>sum+f(s)*(i===0||i===n-1?.5:1),0)/(n-1);
    let signedWorkJ=0,absoluteWorkJ=0;
    for(let i=1;i<n;i++){const a=samples[i-1],b=samples[i],dq=(b.t2-a.t2)*R;signedWorkJ+=(a.tau2+b.tau2)*dq/2;absoluteWorkJ+=(Math.abs(a.tau2)+Math.abs(b.tau2))*dq/2;}
    const ys=physicalSamples.map(s=>s.Cg[0]),zs=physicalSamples.map(s=>s.groundGap);
    const metrics={totalTravel,usableTravel,startMM,endMM,
      peak:Math.max(...samples.map(s=>s.combinedTorque)),rms:Math.sqrt(avg(s=>s.combinedTorque**2)),
      meanAbs:avg(s=>Math.abs(s.tau2)),signedMean:avg(s=>s.tau2),
      peakTau2:Math.max(...samples.map(s=>Math.abs(s.tau2))),peakTau4:Math.max(...samples.map(s=>Math.abs(s.tau4))),
      rmsTau2:Math.sqrt(avg(s=>s.tau2**2)),rmsTau4:Math.sqrt(avg(s=>s.tau4**2)),
      drift:Math.max(...ys)-Math.min(...ys),minClearance:Math.min(...zs),
      minHipRimGap:Math.min(...physicalSamples.map(s=>s.hipRimGap)),
      minJacobian:Math.min(...samples.map(s=>s.dCg[1])),
      peakBelt:Math.max(...samples.flatMap(s=>[s.ab.U,s.ab.L,s.cd.U,s.cd.L,s.ef.U,s.ef.L])),
      signedWorkJ,absoluteWorkJ,size:p.L2+p.L3,
      loadWorkJ:dot([p.Fy,p.Fz],sub(samples.at(-1).Cg,samples[0].Cg))/1000+samples[0].Mw*samples[0].K*(usableTc-usableTe)*R,
      K:samples[0].K,...ratios(p)};
    // Resolve the load for work even when the independent inputs are Fn/Ft.
    metrics.loadWorkJ=dot(samples[0].FcontactG,sub(samples.at(-1).Cg,samples[0].Cg))/1000+samples[0].Mw*samples[0].K*(usableTc-usableTe)*R;
    metrics.nominalPeak=metrics.peak;metrics.nominalRms=metrics.rms;
    const loadCases=[{label:'nominal',Fy:samples[0].Fy,Fz:samples[0].Fz,peak:metrics.peak,rms:metrics.rms,peakTau2:metrics.peakTau2,rmsTau2:metrics.rmsTau2,peakTau4:metrics.peakTau4}];
    if(p.loadCases==='lateral-envelope')for(const Fy of [...new Set([-Math.abs(p.Fy),0,Math.abs(p.Fy)])].filter(f=>f!==p.Fy)) {
      const pp={...p,Fy},rows=samples.map(s=>statics(pp,s.t2));
      const average=f=>rows.reduce((sum,s,i)=>sum+f(s)*(i===0||i===n-1?.5:1),0)/(n-1);
      loadCases.push({label:`Fy=${Fy} N`,Fy,Fz:p.Fz,peak:Math.max(...rows.map(s=>s.combinedTorque)),
        rms:Math.sqrt(average(s=>s.combinedTorque**2)),peakTau2:Math.max(...rows.map(s=>Math.abs(s.tau2))),
        rmsTau2:Math.sqrt(average(s=>s.tau2**2)),peakTau4:Math.max(...rows.map(s=>Math.abs(s.tau4)))});
    }
    metrics.peak=Math.max(...loadCases.map(c=>c.peak));metrics.rms=Math.max(...loadCases.map(c=>c.rms));
    metrics.robustPeakTau2=Math.max(...loadCases.map(c=>c.peakTau2));metrics.robustRmsTau2=Math.max(...loadCases.map(c=>c.rmsTau2));
    metrics.robustPeakTau4=Math.max(...loadCases.map(c=>c.peakTau4));
    if(metrics.drift>p.maxDrift+1e-8)reasons.push('Lateral drift exceeds the configured limit.');
    if(metrics.minClearance<p.minClearance-1e-8)reasons.push('Flat-ground chassis clearance is below the configured minimum.');
    if(p.enforceHipRim&&metrics.minHipRimGap<p.minClearance-1e-8)reasons.push('Projected wheel rim violates the assumed hip exclusion disk; 3D axial packaging is unresolved.');
    if(metrics.minJacobian<p.minJacobian-1e-8)reasons.push('Usable vertical Jacobian is below the singularity margin.');
    return {config:p,samples,physicalSamples,metrics,loadCases,bounds:{te:p.te,tc:p.tc,usableTe,usableTc,startMM,endMM},feasible:reasons.length===0,reasons};
  }
  const DEFAULT_DOMAINS=Object.freeze({L2:[180,340,40],L3:[180,340,40],qab:[1.4,2.4,.25],alpha:[0,20,10],te:[100,110,10],tc:[155,170,15]});
  function grid([lo,hi,step]) {
    if(!Number.isFinite(lo)||!Number.isFinite(hi)||!Number.isFinite(step)||step<=0||hi<lo)throw Error('Invalid search bounds.');
    const values=[];for(let i=0;i<=Math.floor((hi-lo)/step+1e-9);i++)values.push(lo+i*step);
    if(values.at(-1)<hi-1e-9)values.push(hi);return values;
  }
  function dominates(a,b,objective='peak') {const av=[a.metrics[objective],a.metrics.size,a.metrics.drift],bv=[b.metrics[objective],b.metrics.size,b.metrics.drift];return av.every((v,i)=>v<=bv[i]+1e-9)&&av.some((v,i)=>v<bv[i]-1e-9);}
  function paretoFront(candidates,objective='peak') {
    const front=[];for(const c of candidates){if(front.some(a=>dominates(a,c,objective)))continue;for(let i=front.length-1;i>=0;i--)if(dominates(c,front[i],objective))front.splice(i,1);front.push(c);}return front;
  }
  function optimize(config,options={}) {
    const method=options.method??'single',objective=options.objective??config.objective;
    if(!['single','pareto'].includes(method)||!['peak','rms'].includes(objective))throw Error('Unknown optimization method or objective.');
    const domain=clone(options.domains??DEFAULT_DOMAINS),exactTarget=options.exactTarget??true;
    const keys=Object.keys(domain).filter(k=>!exactTarget||k!=='tc'),allowed=['L2','L3','q23','qab','qcd','qef','alpha','phi0','te','tc'];
    if(keys.some(k=>!allowed.includes(k)))throw Error('Search may vary geometry only; load, radius and mass remain fixed.');
    if(keys.includes('q23')&&keys.includes('L2'))throw Error('Vary L2 or q23, not both.');
    const grids=keys.map(k=>grid(domain[k])),coarseCount=grids.reduce((a,g)=>a*g.length,1),maxEvaluations=options.maxEvaluations??30000;
    if(coarseCount>maxEvaluations)throw Error(`Coarse grid has ${coarseCount} candidates; limit is ${maxEvaluations}.`);
    const refineIterations=options.refineIterations??5;
    if(!Number.isInteger(refineIterations)||refineIterations<0||refineIterations>12)throw Error('refineIterations must be 0–12.');
    let evaluations=0,rejected=0,best=null;const candidates=[],seen=new Set(),convergence=[];
    const tie=(a,b)=>a.score-b.score||a.metrics.size-b.metrics.size||a.metrics.drift-b.metrics.drift;
    function evaluate(values) {
      if(evaluations>=maxEvaluations)return null;
      const id=values.map(v=>v.toFixed(9)).join(',');if(seen.has(id))return null;seen.add(id);
      const p=clone(config);p.objective=objective;keys.forEach((k,i)=>{if(!k.startsWith('q'))p[k]=values[i];});
      keys.forEach((k,i)=>{if(k==='q23')p.L2=values[i]*p.L3;if(k==='qab')p.ra=values[i]*p.rb;if(k==='qcd')p.rc=values[i]*p.rd;if(k==='qef')p.re=values[i]*p.rf;});
      if(exactTarget) {
        const lo=domain.tc?.[0]??p.te,hi=domain.tc?.[1]??180;
        let previous=p.te,found=false;
        for(let j=1;j<=90;j++){const t=p.te+(hi-p.te)*j/90;
          if(kinematics(p,t).dz>=p.targetTotal){p.tc=inverseHeight(p,p.targetTotal,previous,t);found=p.tc>=lo-1e-8;break;}previous=t;
        }
        if(!found){evaluations++;rejected++;return null;}
      }
      // Search screening uses fewer integration samples, with the same constraints.
      p.samples=Math.min(config.samples,81);const result=profile(p);evaluations++;
      if(!result.feasible){rejected++;return null;}
      const c={config:{...p,samples:config.samples},profile:result,metrics:result.metrics,score:result.metrics[objective],values:[...values]};
      candidates.push(c);if(!best||tie(c,best)<0)best=c;return c;
    }
    function enumerate(values,i){if(i===keys.length){evaluate(values);return;}for(const v of grids[i])enumerate([...values,v],i+1);}
    enumerate([],0);convergence.push({stage:'coarse',iteration:0,evaluations,feasible:candidates.length,best:best?.score??null});
    const initialFront=paretoFront(candidates,objective);
    let seeds=method==='pareto'?initialFront.sort(tie).filter((_,i)=>i%Math.max(1,Math.floor(initialFront.length/12))===0).slice(0,12):candidates.slice().sort(tie).slice(0,4);
    for(let iteration=1;iteration<=refineIterations&&seeds.length;iteration++) {
      const nextSeeds=[];
      for(const seed of seeds){let current=seed;for(let i=0;i<keys.length;i++)for(const sign of [-1,1]){
        const values=[...current.values],step=domain[keys[i]][2]/2**iteration;
        values[i]=Math.max(domain[keys[i]][0],Math.min(domain[keys[i]][1],values[i]+sign*step));
        const c=evaluate(values);if(c&&(method==='pareto'?!dominates(current,c,objective):tie(c,current)<0))current=c;
      }nextSeeds.push(current);}
      seeds=nextSeeds;convergence.push({stage:'local-refinement',iteration,evaluations,feasible:candidates.length,best:best?.score??null});
    }
    // Recheck every retained finalist with >=721 samples. Do not certify a coarse winner.
    const finalistPool=[...new Set([...candidates.slice().sort(tie).slice(0,40),...paretoFront(candidates,objective)])];
    const verified=[];for(const c of finalistPool){const p={...c.config,samples:Math.max(721,config.samples)},r=profile(p);if(r.feasible)verified.push({...c,config:{...c.config},profile:r,metrics:r.metrics,score:r.metrics[objective]});}
    verified.sort(tie);best=verified[0]??null;
    convergence.push({stage:'dense-verification',iteration:refineIterations,evaluations,feasible:verified.length,best:best?.score??null});
    const boundary=[];if(best)for(let i=0;i<keys.length;i++) {
      const [lo,hi]=domain[keys[i]],v=best.values[i];
      if(Math.abs(v-lo)<1e-7)boundary.push({key:keys[i],side:'minimum',value:v});
      if(Math.abs(v-hi)<1e-7)boundary.push({key:keys[i],side:'maximum',value:v});
    }
    return {best,candidates:verified.slice(0,40),pareto:paretoFront(verified,objective).sort((a,b)=>a.metrics.size-b.metrics.size),convergence,evaluations,rejected,method,objective,domain,exactTarget,
      boundary,limited:evaluations>=maxEvaluations,
      limitations:'Finite coarse geometry enumeration and local coordinate refinement; sampled pose constraints. Domain-limited alternatives, not a global hardware optimum. Loads/masses remain fixed; RMS weighting is explicit.'};
  }
  const api={DEFAULT_CONFIG,DEFAULT_DOMAINS,validateConfig,ratios,resolveLoads,global,local,kinematics,statics,profile,inverseHeight,convertBuffer,optimize,paretoFront};
  globalThis.DesignStudyModel=api;
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
})();
