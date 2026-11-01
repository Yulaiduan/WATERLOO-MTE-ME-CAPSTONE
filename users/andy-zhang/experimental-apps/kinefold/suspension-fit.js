/** Expose the retained V4 minimax spring fitter in Kinefold's builder.
 * Load after reference-v4.js/model.js; mount(host,{studio,beforeSolve}) in app.js.
 * Inputs explicit mm/deg/kg/N design and seven boolean locks; outputs proposed
 * spring values, sampled peak hip torque (Nm), bounds and an exportable report.
 * Uses unchanged VSLFit, not a new optimizer. Bounded quasi-static fit only;
 * dense sampling is not a global optimum or hardware/contact certification.
 */
globalThis.KinefoldSuspensionFit=(()=>{
 'use strict';
 const M=globalThis.Kinefold,source=VSLFit;
 const keys=Object.freeze([...source.keys]),defaults=Object.freeze({...source.defaults});
 const names={springK:['Spring rate','k','N/mm'],hornR:['Horn radius','rₕ','mm'],Sv:['Idler local v','Sᵥ','mm'],rs:['Idler radius','rₛ','mm'],p0:['Reference force','p₀','N'],nu:['Horn offset','ν','°'],Su:['Idler local u','Sᵤ','mm']};
 const settings=Object.freeze({samples:181,iterations:240,verification:6501,starts:6});
 const signature=p=>JSON.stringify(Object.keys(p).sort().filter(k=>k!=='theta2').map(k=>[k,p[k]]));
 function peak(p,count){
  if(M.validate(p).length)return null;
  const r=M.reference(p);let maximum=0,at=p.te;
  for(let i=0;i<count;i++){const theta=p.te+(p.tc-p.te)*i/(count-1),z=KinefoldV4.VSLStatic.solve(r,theta,false);if(!z.valid||!Number.isFinite(z.tau2))return null;if(Math.abs(z.tau2)>maximum){maximum=Math.abs(z.tau2);at=theta;}}
  return {maxTorqueNm:maximum,thetaDeg:at};
 }
 function solve(params,locks=defaults,{progress=()=>{},...options}={}){
  const captured={...params},driving=source.normalize(locks),run={...settings,...options};
  const fit=source.fit(M.reference(captured),{...run,driving,progress});
  if(!fit.valid)return {valid:false,reason:fit.reason};
  const proposed={...captured};for(const key of keys)proposed[key]=driving[key]?captured[key]:fit.parameters[key];
  const errors=M.validate(proposed);if(errors.length)return {valid:false,reason:'Fitted design is invalid in Kinefold: '+errors.join(' ')};
  return {schema:'kinefold/suspension-fit-v1',valid:true,inputParams:captured,params:proposed,locks:driving,free:fit.free,
   before:peak(captured,fit.verification),after:{maxTorqueNm:fit.maxTorque,thetaDeg:fit.peakTheta},bounds:fit.bounds,
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
  host.innerHTML=`<h3>Find suspension fit</h3><p class="hint">Lock keeps the current value. Solve lets the fitter change it to minimize peak residual hip torque over the working travel.</p><div class="fit-choices">${keys.map(key=>`<label><span>${names[key][0]}<small>${names[key][1]} · ${names[key][2]}</small></span><select data-fit-lock="${key}" aria-label="${names[key][0]} fit mode"><option value="lock" ${locks[key]?'selected':''}>Lock</option><option value="solve" ${locks[key]?'':'selected'}>Solve</option></select></label>`).join('')}</div><div class="fit-actions"><button class="primary" data-fit-solve>Solve suspension</button><button data-fit-cancel hidden>Cancel</button></div><p data-fit-status role="status" aria-live="polite">Current α, loads, masses and leg geometry stay fixed.</p><div data-fit-result></div><details class="fit-bounds"><summary>Search bounds &amp; method</summary><div data-fit-bounds></div><p>Jon’s retained V4 bounded minimax fitter: 181 search poses, 6 starts, then 6,501 checked poses. A numerical fit, not a guaranteed global optimum. Freeing the idler radius can reach the ideal zero-radius limit.</p></details>`;
  const $=selector=>host.querySelector(selector),status=$('[data-fit-status]'),solveButton=$('[data-fit-solve]'),cancelButton=$('[data-fit-cancel]'),result=$('[data-fit-result]');
  function refreshBounds(params){try{const bounds=source.boundsFor(M.reference(params));$('[data-fit-bounds]').innerHTML=`<table><thead><tr><th>Variable</th><th>Min</th><th>Max</th></tr></thead><tbody>${keys.map(k=>`<tr><th>${names[k][1]} · ${names[k][2]}</th><td>${fmt(bounds[k].min)}</td><td>${fmt(bounds[k].max)}</td></tr>`).join('')}</tbody></table>`;}catch{$('[data-fit-bounds]').textContent='Enter finite mechanism and spring values to inspect bounds.';}}
  function busy(on){solveButton.disabled=on||!S.getSnapshot().params.springEnabled;cancelButton.hidden=!on;for(const el of host.querySelectorAll('[data-fit-lock]'))el.disabled=on;host.setAttribute('aria-busy',String(on));}
  function stop(message){generation++;worker?.terminate();worker=null;busy(false);if(message)status.textContent=message;}
  function invalidate(message){stop();candidate=null;capturedKey='';applied=false;result.innerHTML='';status.textContent=message;}
  function render(){
   const c=candidate;
   result.innerHTML=`<div class="fit-peaks"><span>Current peak <b>${fmt(c.before?.maxTorqueNm)} N·m</b></span><span>Proposed peak <b>${fmt(c.after.maxTorqueNm)} N·m</b></span></div><p class="hint">Checked ${c.settings.verification.toLocaleString('en-CA')} poses, ${fmt(c.inputParams.te)}–${fmt(c.inputParams.tc)}°. Peak at ${fmt(c.after.thetaDeg)}°.</p><details class="fit-values"><summary>Proposed parameter values</summary><table><thead><tr><th>Variable</th><th>Current</th><th>Proposed</th></tr></thead><tbody>${keys.map(k=>`<tr><th>${names[k][1]} · ${names[k][2]}</th><td>${fmt(c.inputParams[k])}</td><td>${fmt(c.params[k])}${c.locks[k]?' · locked':''}</td></tr>`).join('')}</tbody></table></details>${c.warnings.map(w=>`<p class="notice">${esc(w)}</p>`).join('')}<div class="fit-actions"><button data-fit-apply class="primary" ${c.free.length?'':'disabled'}>Apply fit</button><button data-fit-export>Export fit JSON</button></div><p class="hint">Apply updates the working design and all its plots. Save the named profile separately. ${esc(c.limitations)}</p>`;
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
 return {keys,defaults,names,settings,signature,solve,mount};
})();
