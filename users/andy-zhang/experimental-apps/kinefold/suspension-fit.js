/** Expose the retained V4 minimax spring fitter in Kinefold's builder.
 * Load after reference-v4.js/model.js; mount(host,{studio,beforeSolve}) in app.js.
 * Inputs explicit mm/deg/kg/N design and seven boolean locks; outputs proposed
 * spring values, sampled peak hip torque (Nm), bounds and an exportable report.
 * Uses retained VSLFit when locks map directly, and a chassis-variable bounded
 * search when tilted idler locks require it. Quasi-static fit only;
 * dense sampling is not a global optimum or hardware/contact certification.
 */
globalThis.KinefoldSuspensionFit=(()=>{
 'use strict';
 const M=globalThis.Kinefold,source=VSLFit;
 const keys=Object.freeze([...source.keys]),defaults=Object.freeze({...source.defaults});
 const names={springK:['Spring rate','k','N/mm'],hornR:['Horn radius','rₕ','mm'],Sv:['Idler chassis v','Sᵥ','mm'],rs:['Idler radius','rₛ','mm'],p0:['Reference force','p₀','N'],nu:['Horn offset','ν','°'],Su:['Idler chassis u','Sᵤ','mm']};
 const settings=Object.freeze({samples:181,iterations:240,verification:6501,starts:6});
 const signature=p=>JSON.stringify(Object.keys(p).sort().filter(k=>k!=='theta2').map(k=>[k,p[k]]));
 function massBasis(p){
  const r=M.reference(p),massesKg=Object.fromEntries(['m1','m2','m3','m5','m6'].map(k=>[k,p[k]])),totalMassKg=Object.values(massesKg).reduce((a,b)=>a+b,0);
  return {massesKg,totalMassKg,gravityMS2:p.g,totalWeightN:totalMassKg*p.g,loadMode:p.loadMode,automaticWeightReference:p.loadMode==='weight',resolvedWheelForceN:{x:-r.Fy,z:r.Fz},
   explanation:'All body masses are included at their actual static centres of mass. For a grounded wheel at fixed world height and zero contact moment, wheel gravity has zero stance work; its weight remains in the ground reaction and its mass/inertia remain in dynamics. Tilted finite-link gravity can make the required equivalent support pose-dependent. The fit minimizes residual hip torque, not variation of cable force or gross-weight lift ratio. Minimizing holding torque can remove restoring stiffness; test terrain response separately.'};
 }
 function peak(p,count){
  if(M.validate(p).length)return null;
  const r=M.reference(p);let maximum=0,at=p.te,sum=0,maxForce=0,sumForce=0,forceCount=0;
  for(let i=0;i<count;i++){const theta=p.te+(p.tc-p.te)*i/(count-1),z=KinefoldV4.VSLStatic.solve(r,theta,false);if(!z.valid||!Number.isFinite(z.tau2))return null;if(Math.abs(z.tau2)>maximum){maximum=Math.abs(z.tau2);at=theta;}sum+=z.tau2*z.tau2;
   if(Number.isFinite(z.spring?.Jz)&&Math.abs(z.spring.Jz)>1e-7){const f=z.tau2/(z.spring.Jz/1000);maxForce=Math.max(maxForce,Math.abs(f));sumForce+=f*f;forceCount++;}}
  return {maxTorqueNm:maximum,thetaDeg:at,rmsTorqueNm:Math.sqrt(sum/count),maxEquivalentResidualForceN:forceCount===count?maxForce:null,rmsEquivalentResidualForceN:forceCount===count?Math.sqrt(sumForce/count):null,samples:count};
 }
 // At nonzero alpha an independent source-S lock is not a chassis-S lock.
 // This bounded multistart Nelder–Mead adapter searches the stored chassis
 // variables directly. Bounds are captured once; the source equations stay intact.
 function fitChassis(p,driving,run,progress){
  if(!p.springEnabled)return {valid:false,reason:'Enable spring assistance before fitting.'};
  const free=keys.filter(k=>!driving[k]),bounds=source.boundsFor(p),n=free.length;
  const ts=Array.from({length:run.samples},(_,i)=>p.te+(p.tc-p.te)*i/(run.samples-1)),ref=M.reference(p);
  const bad=KinefoldV4.VSLUnassisted.validate(ref);if(bad.length)return {valid:false,reason:bad.join(' ')};
  const base=ts.map(t=>KinefoldV4.VSLUnassisted.solve(ref,t,false).tau2),clamp=x=>Math.max(0,Math.min(1,x));let evaluations=0;
  const encode=a=>free.map(k=>clamp((a[k]-bounds[k].min)/(bounds[k].max-bounds[k].min)));
  function evaluate(v){evaluations++;v=v.map(clamp);const candidate={...p};free.forEach((k,i)=>candidate[k]=bounds[k].min+v[i]*(bounds[k].max-bounds[k].min));
   const r=M.reference(candidate),world=M.springReference(candidate),route=KinefoldV4.VSLSpring.exit(world),window=KinefoldV4.VSLSpring.interval(r,p.te,p.tc),reference=KinefoldV4.VSLSpring.geometry(r,90);
   if(!route.valid||Math.abs(route.applied)>1e-8||!window.valid||!reference.valid||candidate.p0+candidate.springK*(window.min-reference.payout)<-1e-8)return {v,score:1e100,parameters:candidate};
   let score=0;for(let i=0;i<ts.length;i++){const z=KinefoldV4.VSLSpring.geometry(r,ts[i]);if(!z.valid)return {v,score:1e100,parameters:candidate};const force=Math.max(0,candidate.p0+candidate.springK*(z.payout-reference.payout));score=Math.max(score,Math.abs(base[i]+force*z.derivative/1000));}
   return {v,score,parameters:candidate};
  }
  function search(seed){let simplex=[evaluate(seed),...free.map((_,i)=>evaluate(seed.map((x,j)=>j===i?x+(x>.94?-.035:.035):x)))];
   for(let step=0;step<run.iterations;step++){simplex.sort((a,b)=>a.score-b.score);const best=simplex[0],worst=simplex.at(-1),center=free.map((_,j)=>simplex.slice(0,-1).reduce((sum,z)=>sum+z.v[j],0)/n),reflect=evaluate(center.map((x,j)=>2*x-worst.v[j]));
    if(reflect.score<best.score){const expand=evaluate(center.map((x,j)=>3*x-2*worst.v[j]));simplex[n]=expand.score<reflect.score?expand:reflect;}
    else if(reflect.score<simplex[n-1].score)simplex[n]=reflect;
    else{const target=reflect.score<worst.score?reflect:worst,contract=evaluate(center.map((x,j)=>(x+target.v[j])/2));if(contract.score<target.score)simplex[n]=contract;else simplex=[best,...simplex.slice(1).map(z=>evaluate(z.v.map((x,j)=>(x+best.v[j])/2)))];}
    if(step>35&&simplex[0].score<1e99&&Math.max(...simplex.flatMap(z=>z.v.map((x,j)=>Math.abs(x-simplex[0].v[j]))))<1e-9)break;
   }return simplex.sort((a,b)=>a.score-b.score)[0];
  }
  const seeds=[p,{...p,Su:0,hornR:p.hornR*.9,p0:p.p0*1.1},{...p,Su:p.rs,hornR:p.hornR*1.1},{...p,Su:-p.rs,p0:p.p0*.8},{...p,Su:p.Su+p.rs,hornR:p.hornR*.8},{...p,Su:p.Su-p.rs,hornR:p.hornR*1.2}];
  const unique=[...new Map(seeds.map(a=>{const v=encode(a);return [JSON.stringify(v),v];})).values()].slice(0,run.starts);let best=evaluate(encode(p));
  for(let i=0;i<unique.length;i++){const z=search(unique[i]);if(z.score<best.score)best=z;progress({completed:i+1,total:unique.length});}
  if(best.score>1e99)return {valid:false,reason:'No valid horizontal-exit spring fit within the captured chassis bounds.'};
  const checked=peak(best.parameters,run.verification);if(!checked)return {valid:false,reason:'Dense fitted-route verification failed.'};
  const warnings=['Chassis-frame bounded multistart search; no global optimum certificate.'];
  if(free.some(k=>Math.abs(best.parameters[k]-bounds[k].min)<1e-5*(bounds[k].max-bounds[k].min)||Math.abs(best.parameters[k]-bounds[k].max)<1e-5*(bounds[k].max-bounds[k].min)))warnings.push('A solved variable reached a numerical search bound.');
  if(checked.maxTorqueNm>best.score+1e-4)warnings.push('Dense check found a larger between-sample peak.');
  return {valid:true,parameters:best.parameters,free,maxTorque:checked.maxTorqueNm,peakTheta:checked.thetaDeg,bounds,evaluations,samples:run.samples,verification:run.verification,warnings,sampledObjective:best.score,method:'bounded sampled chassis-variable Nelder–Mead minimax |tau2|; no global optimum certificate'};
 }
 function solve(params,locks=defaults,{progress=()=>{},...options}={}){
  const captured={...params},driving=source.normalize(locks),run={...settings,...options};
  const chassisSearch=captured.alpha!==0&&keys.some(k=>!['springK','p0'].includes(k)&&!driving[k]);
  const fit=chassisSearch?fitChassis(captured,driving,run,progress):source.fit(M.reference(captured),{...run,driving,progress});
  if(!fit.valid)return {valid:false,reason:fit.reason};
  const proposed={...captured};for(const key of keys)proposed[key]=driving[key]?captured[key]:fit.parameters[key];
  const errors=M.validate(proposed);if(errors.length)return {valid:false,reason:'Fitted design is invalid in Kinefold: '+errors.join(' ')};
  return {schema:'kinefold/suspension-fit-v1',springConvention:M.springConvention,valid:true,inputParams:captured,params:proposed,locks:driving,free:fit.free,
   before:peak(captured,fit.verification),after:{...peak(proposed,fit.verification),maxTorqueNm:fit.maxTorque,thetaDeg:fit.peakTheta},massBasis:massBasis(captured),bounds:fit.bounds,
   settings:{samples:fit.samples,verification:fit.verification,iterations:run.iterations,starts:run.starts},evaluations:fit.evaluations,
   sampledObjectiveNm:fit.sampledObjective,warnings:fit.warnings,method:fit.method,
   objective:'Minimize peak |static residual hip torque| over working θ₂ at current α, loads and masses.',
   limitations:'Sampled bounded fit, not a global optimum certificate. No friction, dynamics, spring strength/stroke, cable stretch or physical packaging validation.'};
 }
 function mount(host,{studio:S,beforeSolve=()=>{},workerFactory=()=>new Worker('suspension-fit-worker.js')}={}){
  if(!host||!S)return;
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt=n=>Number.isFinite(n)?n.toLocaleString('en-CA',{maximumFractionDigits:6}):'Unavailable';
  let locks={...defaults},worker=null,candidate=null,capturedKey='',generation=0,applied=false;
  host.className='suspension-fit';
  host.innerHTML=`<h3>Find suspension fit</h3><p class="hint">Lock keeps the current value. Solve lets the fitter change it to minimize peak residual hip torque over the working travel.</p><div class="fit-choices">${keys.map(key=>`<label><span>${names[key][0]}<small>${names[key][1]} · ${names[key][2]}</small></span><select data-fit-lock="${key}" aria-label="${names[key][0]} fit mode"><option value="lock" ${locks[key]?'selected':''}>Lock</option><option value="solve" ${locks[key]?'':'selected'}>Solve</option></select></label>`).join('')}</div><div class="fit-actions"><button class="primary" data-fit-solve>Solve suspension</button><button data-fit-cancel hidden>Cancel</button></div><p data-fit-status role="status" aria-live="polite">Current α, loads, masses and leg geometry stay fixed.</p><div data-fit-result></div><details class="fit-bounds"><summary>Search bounds &amp; method</summary><div data-fit-bounds></div><p>181 search poses, up to 6 starts, then 6,501 checked poses. Tilted free idler coordinates use a bounded chassis-variable search; other cases use retained V4 fitting. A numerical fit, not a guaranteed global optimum. Freeing the idler radius can reach the ideal zero-radius limit.</p></details>`;
  const $=selector=>host.querySelector(selector),status=$('[data-fit-status]'),solveButton=$('[data-fit-solve]'),cancelButton=$('[data-fit-cancel]'),result=$('[data-fit-result]');
  function refreshBounds(params){try{const bounds=source.boundsFor(params.alpha!==0&&keys.some(k=>!['springK','p0'].includes(k)&&!locks[k])?params:M.reference(params));$('[data-fit-bounds]').innerHTML=`<table><thead><tr><th>Variable</th><th>Min</th><th>Max</th></tr></thead><tbody>${keys.map(k=>`<tr><th>${names[k][1]} · ${names[k][2]}</th><td>${fmt(locks[k]?params[k]:bounds[k].min)}</td><td>${fmt(locks[k]?params[k]:bounds[k].max)}</td></tr>`).join('')}</tbody></table>`;}catch{$('[data-fit-bounds]').textContent='Enter finite mechanism and spring values to inspect bounds.';}}
  function busy(on){solveButton.disabled=on||!S.getSnapshot().params.springEnabled;cancelButton.hidden=!on;for(const el of host.querySelectorAll('[data-fit-lock]'))el.disabled=on;host.setAttribute('aria-busy',String(on));}
  function stop(message){generation++;worker?.terminate();worker=null;busy(false);if(message)status.textContent=message;}
  function invalidate(message){stop();candidate=null;capturedKey='';applied=false;result.innerHTML='';status.textContent=message;}
  function render(){
   const c=candidate;
   result.innerHTML=`<div class="fit-peaks"><span>Current peak <b>${fmt(c.before?.maxTorqueNm)} N·m</b></span><span>Proposed peak <b>${fmt(c.after.maxTorqueNm)} N·m</b></span></div><p class="hint">Checked ${c.settings.verification.toLocaleString('en-CA')} poses, ${fmt(c.inputParams.te)}–${fmt(c.inputParams.tc)}°. Peak at ${fmt(c.after.thetaDeg)}°.</p><details class="fit-mass"><summary>Mass &amp; load basis</summary><table><tbody>${Object.entries(c.massBasis.massesKg).map(([k,v])=>`<tr><th>${k}</th><td>${fmt(v)} kg</td></tr>`).join('')}<tr><th>Total weight</th><td>${fmt(c.massBasis.totalWeightN)} N</td></tr><tr><th>Static wheel force · x / z</th><td>${fmt(c.massBasis.resolvedWheelForceN.x)} / ${fmt(c.massBasis.resolvedWheelForceN.z)} N · ${esc(c.massBasis.loadMode)}</td></tr><tr><th>Proposed torque · RMS</th><td>${fmt(c.after.rmsTorqueNm)} N·m</td></tr><tr><th>Equivalent residual force · max / RMS</th><td>${fmt(c.after.maxEquivalentResidualForceN)} / ${fmt(c.after.rmsEquivalentResidualForceN)} N</td></tr></tbody></table><p>${esc(c.massBasis.explanation)}</p></details><details class="fit-values"><summary>Proposed parameter values</summary><table><thead><tr><th>Variable</th><th>Current</th><th>Proposed</th></tr></thead><tbody>${keys.map(k=>`<tr><th>${names[k][1]} · ${names[k][2]}</th><td>${fmt(c.inputParams[k])}</td><td>${fmt(c.params[k])}${c.locks[k]?' · locked':''}</td></tr>`).join('')}</tbody></table></details>${c.warnings.map(w=>`<p class="notice">${esc(w)}</p>`).join('')}<div class="fit-actions"><button data-fit-apply class="primary" ${c.free.length?'':'disabled'}>Apply fit</button><button data-fit-export>Export fit JSON</button></div><p class="hint">Apply updates the working design and all its plots. Save the named profile separately. ${esc(c.limitations)}</p>`;
   $('[data-fit-apply]').onclick=async()=>{
    const current=S.getSnapshot();if(signature(current.params)!==capturedKey){invalidate('Design changed. Solve again before applying.');return;}
    const next={...current,params:{...current.params}};for(const k of keys)next.params[k]=c.params[k];
    applied=true;$('[data-fit-apply]').disabled=true;
    try{const saved=await S.applySnapshot(next);if(saved===null)throw Error('The working-copy save failed.');status.textContent='Fit applied to the working design. Save the named profile to retain a named revision.';candidate=null;capturedKey='';}
    catch(error){invalidate('Apply failed: '+error.message);}
    finally{applied=false;}
   };
   $('[data-fit-export]').onclick=()=>S.saveArtifact('kinefold-suspension-fit.json',c);
  }
  for(const el of host.querySelectorAll('[data-fit-lock]'))el.onchange=()=>{locks[el.dataset.fitLock]=el.value==='lock';invalidate('Lock / solve selection changed. Ready to solve.');};
  solveButton.onclick=()=>{
   beforeSolve();const params={...S.getSnapshot().params};invalidate('Solving captured inputs…');capturedKey=signature(params);const ticket=++generation;busy(true);
   try{worker=workerFactory();worker.onmessage=event=>{
    if(ticket!==generation)return;
    if(event.data.type==='progress'){status.textContent=`Solving · start ${event.data.completed} of ${event.data.total}…`;return;}
    const data=event.data;stop();if(signature(S.getSnapshot().params)!==capturedKey){invalidate('Design changed during solve. Solve again.');return;}
    if(data.type==='error'||!data.result?.valid){candidate=null;status.textContent='No fit: '+(data.message||data.result?.reason||'Unknown error.');return;}
    candidate=data.result;render();status.textContent='Fit ready for review. Apply it to update the mechanism.';
   };worker.onerror=event=>{stop();candidate=null;status.textContent='Solve failed: '+event.message;};worker.postMessage({params,locks:{...locks}});}
   catch(error){stop();status.textContent='Solve unavailable: '+error.message;}
  };
  cancelButton.onclick=()=>invalidate('Solve cancelled. The mechanism was not changed.');
  let lastSignature=signature(S.getSnapshot().params);
  const unsubscribe=S.subscribe(project=>{const next=signature(project.params);if(next!==lastSignature){if(!applied&&(candidate||worker||result.hasChildNodes()))invalidate('Design changed. Solve again.');lastSignature=next;refreshBounds(project.params);}busy(!!worker);});
  refreshBounds(S.getSnapshot().params);busy(false);
  return {destroy(){stop();unsubscribe();host.innerHTML='';},getState:()=>({locks:{...locks},candidate,running:!!worker})};
 }
 return {keys,defaults,names,settings,signature,massBasis,solve,mount};
})();
