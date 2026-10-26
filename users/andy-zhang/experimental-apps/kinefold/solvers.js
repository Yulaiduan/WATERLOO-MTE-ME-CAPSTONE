/** Native Kinefold floating single-leg dynamics UI and comparison orchestration.
 * Invocation: load in index.html after model, drawing and KinefoldStudio.
 * Inputs: versioned shared project; geometry mm/deg/kg/N and SI run settings.
 * Outputs: actual backend trajectories, matched comparisons, playback and downloads.
 * Limitations: experimental guided vertical chassis; no terrain or hardware claim.
 */
(() => {
'use strict';
const $=id=>document.getElementById(id), esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=(n,d=3)=>Number.isFinite(n)?(Math.abs(n)<10**(-d)/2?0:n).toLocaleString('en-CA',{maximumFractionDigits:d}):'—';
const engines=['analytical','pymunk'], runs=Object.fromEntries(engines.map(id=>[id,{result:null,snapshot:null,index:0,playing:false,busy:false,request:0}]));
let snapshot=null,previousModel=null,clock=0,sharedTime=0,sharedSide='',pairBusy=false,viewerTimer=null,viewerSnapshotKey=null;
const Analysis=KinefoldDynamicAnalysis,Results=KinefoldDynamicResults,Contact=KinefoldContactUI;
const field=(id,key,label,unit,min,max,step='any')=>`<label for="${id}-${key}"><span>${label}${unit?` · ${unit}`:''}</span><input id="${id}-${key}" data-run-key="${key}" type="number" min="${min}" max="${max}" step="${step}"></label>`;
function dynamicShell(id){const title=id==='analytical'?'Dynamic · analytical':'Dynamic · Pymunk guided chassis';$(id).innerHTML=`<div class="solver-heading"><div><span class="eyebrow">KINEFOLD / VERTICAL CHASSIS</span><h2>${title}</h2><p>${id==='analytical'?'Reduced equations · SciPy DOP853':'Pymunk chassis body · ideal belt-coupled transmission'}</p></div><strong class="quarter-badge">¼ MODEL · SINGLE LEG</strong></div><div id="${id}-identity"></div><div class="dyn-toolbar"><button class="primary" data-run-primary="${id}">Run ${id==='analytical'?'analytical':'Pymunk'}</button><button data-run-both>Run both & compare</button><button id="${id}-export" disabled>Export run JSON</button><button id="${id}-csv" disabled>CSV</button>${id==='pymunk'?'<button data-viewer-open>Open desktop Pymunk</button><button data-viewer-close disabled>Close desktop window</button><span data-viewer-status role="status">Desktop viewer closed</span>':''}</div><div class="quarter-scope"><b>Chassis heave · fixed horizontal position and pitch · prescribed wheel height</b><details><summary>Model assumptions</summary><p>Mass m₁ moves vertically with hip A; no guide rods are drawn. The same saved mechanism geometry, finite-idler spring, masses and belt ratios feed both engines. θ₄ is locked. Pymunk integrates a real guided chassis body with the ideal linkage/inertia condensed into its force law; it is not an all-body rigid linkage simulation.</p><p>The exact V4 baseline uses m₁ = 8.75 kg, other masses = 0, no added rotor inertia and no damping. Its ideal square input has instantaneous massless-linkage pose jumps while chassis position and velocity stay continuous. Moving linkage inertia or damping requires a declared finite transition. This prescribed wheel-height test does not solve collision, tire contact, pitch, roll or four-leg redistribution.</p></details></div><div class="dyn-workspace"><details class="dyn-settings-panel"><summary>Input, actuation & numerical settings <small>Shared saved profile · expand to edit</small></summary><aside class="solver-settings" aria-label="${title} settings"><button class="primary solver-run-top" data-run-top="${id}">Run ${id==='analytical'?'analytical':'Pymunk'}</button><button class="solver-small-action" data-baseline="${id}">Apply V4 baseline + 150 mm square</button><details open><summary>Wheel input</summary>${field(id,'inputHeightMm','Square height','mm',0,1000)}${field(id,'inputPlateauMm','Plateau width','mm',.1,10000)}${field(id,'inputGapMm','Gap width','mm',.1,10000)}${field(id,'inputSpeedMmS','Input speed','mm/s',.1,10000)}${field(id,'inputRiseMm','Transition distance · 0 = exact square','mm',0,1000)}${field(id,'inputDelayS','Initial delay','s',0,30)}<p>Width and gap map to time through the entered speed. Positive transition distance applies smooth ramps inside the square plateau; requested and applied inputs are plotted separately.</p></details><details open><summary>Run & actuation</summary>${field(id,'duration','Duration','s',.05,30)}${field(id,'initialVelocityDegS','Initial relative hip rate','°/s',-720,720)}${field(id,'hipTorqueNm','Constant hip torque','N·m',-10000,10000)}${field(id,'dampingNms','Hip viscous damping','N·m·s/rad',0,10000)}<button class="solver-small-action" data-hold="${id}">Copy static balance torque</button> <button class="solver-small-action" data-release="${id}">Release · torque 0</button><p>These actions set one constant torque; they do not add a feedback controller.</p></details><details><summary>Inertia assumptions</summary><label for="${id}-inertiaModel">Body inertia model<select id="${id}-inertiaModel" data-run-key="inertiaModel"><option value="uniform-rods-discs">Uniform rods & discs</option><option value="custom">Custom inertias</option></select></label>${field(id,'hipRotorInertiaKgM2','Additional joint inertia · legacy','kg·m²',0,1000)}${field(id,'I2','Femur I₂','kg·m²',0,1000)}${field(id,'I3','Tibia I₃','kg·m²',0,1000)}${field(id,'I5','Compound pulley I₅','kg·m²',0,1000)}${field(id,'I6','Wheel assembly I₆','kg·m²',0,1000)}<p>Baseline values are exactly zero for massless moving parts. Custom values are explicit assumptions. Geometry and all masses remain controlled by the builder.</p></details><details><summary>Numerical settings</summary>${field(id,'dt','Integration / maximum step','s',.0001,.01)}${field(id,'outputHz','Output sample rate','Hz',1,1000,1)}${field(id,'iterations','Pymunk constraint iterations','',10,500,1)}<p>Refine the step and compare chassis trajectories. Exact-square jump events are retained separately and do not represent a finite peak hip speed.</p></details><div class="solver-actions"><button class="primary" id="${id}-run">Run ${id==='analytical'?'analytical':'Pymunk'}</button></div></aside></details><div class="solver-output"><div class="solver-state" id="${id}-status" role="status">Ready to run the saved mechanism and input profile.</div><div class="solver-warnings" id="${id}-warnings"></div><div id="${id}-results"><div class="solver-empty"><b>Vertical chassis response</b><span>Apply the exact V4 square baseline or run your saved design.<br>No link mass is added automatically.</span></div></div></div></div>`;
Contact.mount(id,$(id));
KinefoldCaseUI.mount(id,$(id));KinefoldMotorUI.mount(id,$(id));KinefoldEnergyUI.mount(id,$(id));
for(const input of $(id).querySelectorAll('[data-run-key]'))input.addEventListener('change',()=>saveSettings(id));
for(const button of [$(id+'-run'),$(id).querySelector('[data-run-top]'),$(id).querySelector('[data-run-primary]')])button.addEventListener('click',()=>run(id));
$(id).querySelector('[data-run-both]').onclick=runBoth;
if(id==='pymunk'){ $(id).querySelector('[data-viewer-open]').onclick=()=>viewer('open'); $(id).querySelector('[data-viewer-close]').onclick=()=>viewer('close'); }
$(id+'-export').addEventListener('click',()=>download(id,false));$(id+'-csv').addEventListener('click',()=>download(id,true));
$(id).querySelector('[data-baseline]').addEventListener('click',async()=>{if(await KinefoldStudio.ask('Open the exact V4 geometry and masses with the 150 mm square input? Save or export the current working copy first to keep its changes.'))await KinefoldStudio.applySnapshot(KinefoldProjects.baseline());});
$(id).querySelector('[data-hold]').addEventListener('click',()=>{try{const z=Kinefold.evaluate(snapshot.params);if(!z.valid)throw Error(z.errors.join(' '));KinefoldStudio.setSolverConfig({...snapshot.solverConfig,hipTorqueNm:KinefoldMotorUI.balanceCommand(snapshot,z.raw.tau2)});}catch(e){status(id,e.message,'error');}});
$(id).querySelector('[data-release]').addEventListener('click',()=>KinefoldStudio.setSolverConfig({...snapshot.solverConfig,hipTorqueNm:0}));}
function identity(s){return `<div class="solver-design"><div><strong>${esc(s.name)}</strong><small>Shared design · revision ${s.modelRevision} · ${esc(s.id)}</small></div><button data-open-designs>Mechanism studio / profiles</button></div>`;}
function status(id,message,state='idle'){$(id+'-status').textContent=message;$(id+'-status').dataset.state=state;}
function syncSettings(s){for(const id of engines){for(const input of $(id).querySelectorAll('[data-run-key]')){const k=input.dataset.runKey;input.value=s.solverConfig[k];input.removeAttribute('aria-invalid');if(/^I[2356]$/.test(k))input.disabled=s.solverConfig.inertiaModel!=='custom';}runs[id].invalidConfig=false;$(id+'-run').disabled=runs[id].busy;$(id).querySelector('[data-run-top]').disabled=runs[id].busy;$(id+'-identity').innerHTML=identity(s);$(id+'-identity').querySelector('button').addEventListener('click',openDesigns);}}
function openDesigns(){KinefoldStudio.showTab('designs');}
function saveSettings(id){try{const config={...snapshot.solverConfig};for(const input of $(id).querySelectorAll('[data-run-key]')){const key=input.dataset.runKey;config[key]=key==='inertiaModel'?input.value:input.value===''?NaN:Number(input.value);}KinefoldStudio.setSolverConfig(config);syncSettings(KinefoldStudio.getSnapshot());}catch(error){runs[id].invalidConfig=true;$(id+'-run').disabled=true;$(id).querySelector('[data-run-top]').disabled=true;for(const input of $(id).querySelectorAll('[data-run-key]'))input.setAttribute('aria-invalid','true');status(id,error.message,'error');syncRunControls();}}
function changed(s){snapshot=s;syncSettings(s);if(previousModel!==null&&previousModel!==s.modelRevision){for(const id of engines){const state=runs[id];stop(id);if(state.result||state.busy){const label=$(id).querySelector('[data-snapshot-state]');if(label)label.textContent='Earlier snapshot · rerun the current design';status(id,'Design or run settings changed. These results belong to an earlier snapshot; run again to update.','stale');$(id+'-results').classList.add('solver-stale-content');}}}previousModel=s.modelRevision;Contact.update(s);KinefoldCaseUI.update(s);KinefoldMotorUI.update(s);KinefoldEnergyUI.update(s);syncRunControls();refreshComparisons();}
function syncRunControls() {
  const busy=pairBusy||engines.some(id=>runs[id].busy),contact=Contact.isContact(snapshot||{});
  for(const id of engines) {
    for(const selector of ['[data-run-primary]','[data-run-top]','#'+id+'-run'])
      $(id).querySelector(selector).disabled=busy||runs[id].invalidConfig;
    $(id).querySelector('[data-run-both]').disabled=busy||engines.some(key=>runs[key].invalidConfig);
  }
}
function currentComparison() {
  const a=runs.analytical,b=runs.pymunk,current=Analysis.snapshotKey(KinefoldStudio.getSnapshot());
  if((a.snapshot&&Analysis.snapshotKey(a.snapshot)!==current)||(b.snapshot&&Analysis.snapshotKey(b.snapshot)!==current))
    return {valid:false,reason:'Results belong to an earlier mechanism or input profile. Run both again to compare the current snapshot.'};
  return Analysis.comparison(a.result,b.result);
}
function refreshComparisons() {
  const value=currentComparison();
  for(const id of engines) if(runs[id].result)
    Results.updateComparison($(id+'-results'),value,sharedTime,downloadComparison);
}
async function run(id,capture=null) {
  const state=runs[id]; if(state.busy||state.invalidConfig)return false;
  stop(id);
  const captured=capture||structuredClone(KinefoldStudio.getSnapshot()),request=++state.request;
  state.busy=true;syncRunControls();status(id,'Integrating the captured design…','running');
  $(id+'-warnings').innerHTML='';
  try {
    const errors=Kinefold.validate(captured.params);if(errors.length)throw Error(errors.join(' '));
    const response=await fetch('/api/dynamics',{method:'POST',headers:{'Content-Type':'application/json','X-Kinefold-Request':'coupled-dynamics'},body:JSON.stringify(Contact.payload(captured,id))});
    const result=await response.json();
    if(!response.ok||result.error)throw Error(result.error||`Solver request failed (${response.status}).`);
    if(!Array.isArray(result.rows)||!result.rows.length)throw Error('Solver returned no trajectory samples.');
    if(request!==state.request)return false;
    if(captured.modelRevision!==KinefoldStudio.getSnapshot().modelRevision){status(id,'Run finished for an earlier snapshot and was discarded. Run the current design.','stale');return false;}
    state.result=result;state.snapshot=captured;state.camera=null;state.contactBounds=null;
    state.index=nearestIndex(result.rows,sharedTime);
    renderResult(id);$(id+'-results').classList.remove('solver-stale-content');
    const last=result.rows.at(-1),termination=result.diagnostics?.termination||'completed';
    const failedCase=result.caseMetrics?.landingSuccess===false;
    status(id,`${termination==='duration'?'Run complete':'Partial result · '+termination}${failedCase?' · case failed':''} · ${result.rows.length} samples · t = ${fmt(last.t,3)} s · ${result.caseMetrics?.outcome||termination}`,failedCase?'error':termination==='duration'?'ready':'stale');
    $(id+'-warnings').innerHTML=(result.warnings||[]).length?`<details class="solver-run-notes"><summary>Run notes (${result.warnings.length})</summary>${result.warnings.map(w=>`<div class="notice">${esc(typeof w==='string'?w:JSON.stringify(w))}</div>`).join('')}</details>`:'';
    $(id+'-export').disabled=false;$(id+'-csv').disabled=false;refreshComparisons();return true;
  }catch(error){status(id,captured.modelRevision===KinefoldStudio.getSnapshot().modelRevision?error.message:'Design changed during the run. Run the current snapshot again.','error');return false;}
  finally{state.busy=false;syncRunControls();}
}
async function runBoth() {
  if(pairBusy||engines.some(id=>runs[id].busy||runs[id].invalidConfig))return;
  const captured=structuredClone(KinefoldStudio.getSnapshot());pairBusy=true;syncRunControls();
  try {
    status('pymunk','Waiting for analytical run of the same captured mechanism/profile…','running');
    if(await run('analytical',captured))await run('pymunk',captured);
    else status('pymunk','Paired run stopped because the analytical run did not complete for this snapshot.','error');
    refreshComparisons();
    for(const id of engines)if(runs[id].result)$(id+'-results').querySelector('[data-result-group="comparison"]').open=true;
  }finally{pairBusy=false;syncRunControls();}
}
function nearestIndex(rows,time) {
  const exact=rows.findIndex(row=>Math.abs(row.t-time)<1e-9&&(row.eventSide||'')===sharedSide);
  if(exact>=0)return exact;
  let index=0;
  for(let i=0;i<rows.length;i++)if(rows[i].t<=time+1e-9)index=i;else break;
  return index;
}
function renderResult(id) {
  const state=runs[id];
  Results.mount($(id+'-results'),{id,result:state.result,snapshot:state.snapshot,index:state.index},{
    comparison:currentComparison,currentTime:()=>sharedTime,onExportComparison:downloadComparison,
    onScrub:index=>{stop(id);state.index=index;sharedTime=state.result.rows[index].t;sharedSide=state.result.rows[index].eventSide||'';drawFrame(id);},
    onPlay:()=>state.playing?stop(id):play(id)});
  drawFrame(id);
}
async function downloadComparison() {
  const comparison=currentComparison();if(!comparison.valid)return;
  const value={schema:'kinefold/dynamic-comparison-v1',alignment:'Exact sampled time and eventSide; no interpolation or extrapolation',
    analytical:{projectSnapshot:runs.analytical.snapshot,result:runs.analytical.result},
    pymunk:{projectSnapshot:runs.pymunk.snapshot,result:runs.pymunk.result},comparison};
  try { await KinefoldStudio.saveArtifact('kinefold-dynamic-comparison.json',JSON.stringify(value,null,2),'application/json'); }
  catch(error) { for(const id of engines)status(id,'Comparison export failed: '+error.message,'error'); }
}
async function viewer(action) {
  const host=$('pymunk'),label=host.querySelector('[data-viewer-status]'),captured=structuredClone(KinefoldStudio.getSnapshot());
  try {
    if(action==='open')label.textContent='Integrating captured Pymunk result / opening desktop window…';
    const request=action==='open'?{action,params:captured.params,runConfig:captured.solverConfig,name:captured.name,...(captured.contactConfig?{contactConfig:captured.contactConfig}:{}),...(captured.caseConfig?{caseConfig:captured.caseConfig}:{}),...(captured.motorConfig?{motorConfig:captured.motorConfig}:{})}:{action};
    const response=await fetch('/api/viewer',{method:'POST',headers:{'Content-Type':'application/json','X-Kinefold-Request':'coupled-dynamics'},body:JSON.stringify(request)});
    const value=await response.json();if(!response.ok||value.error)throw Error(value.error||'Desktop viewer request failed.');
    if(action==='open')viewerSnapshotKey=Analysis.snapshotKey(captured);
    const active=['starting','ready'].includes(value.state);
    host.querySelector('[data-viewer-open]').disabled=active;host.querySelector('[data-viewer-close]').disabled=!active;
    label.textContent=value.state==='ready'?`Desktop playback open · t ${fmt(value.t||0,2)} s · ${value.name||captured.name}`:value.state==='starting'?'Integrating captured Pymunk result / opening desktop window…':value.state==='error'?'Desktop viewer failed: '+(value.message||'Read .preview viewer log'):'Desktop viewer closed';
    if(active&&viewerSnapshotKey&&viewerSnapshotKey!==Analysis.snapshotKey(captured))label.textContent+=' · earlier captured mechanism/profile';
    if(!active)viewerSnapshotKey=null;
    clearTimeout(viewerTimer);if(active)viewerTimer=setTimeout(()=>viewer('status'),1000);
  }catch(error){label.textContent=error.message;clearTimeout(viewerTimer);host.querySelector('[data-viewer-open]').disabled=false;}
}
function camera(state,p) {
  if(state.camera)return state.camera;
  const bounds={loX:Infinity,hiX:-Infinity,loY:Infinity,hiY:-Infinity};
  for(const frame of state.result.frames) {
    const spring=KinefoldDrawing.spring(p,frame);
    const points=[frame.A,[frame.A[0],0,frame.A[2]+100],frame.B,...(spring.valid?[spring.D,spring.S,...spring.assemblyPoints]:[]),
      [frame.C[0]-p.rw,0,frame.C[2]-p.rw],[frame.C[0]+p.rw,0,frame.C[2]+p.rw]];
    for(const point of points){bounds.loX=Math.min(bounds.loX,-point[0]);bounds.hiX=Math.max(bounds.hiX,-point[0]);bounds.loY=Math.min(bounds.loY,-point[2]);bounds.hiY=Math.max(bounds.hiY,-point[2]);}
  }
  state.camera=bounds;return bounds;
}
function drawFrame(id){const state=runs[id];if(state.result.scope?.mode==='terrain-contact'){const view=KinefoldContactDrawing.render(state),svg=$(id+'-preview');svg.setAttribute('viewBox','0 0 740 450');svg.innerHTML=view.html;svg.dataset.theta2=String(view.row.theta2);svg.dataset.wheelAngle=String(view.frame.wheelAngle);svg.dataset.time=String(view.row.t);svg.dataset.terrainOffset=JSON.stringify(view.frame.terrainOffsetMm);$(id+'-scrub').value=state.index;$(id+'-time').textContent=`${fmt(view.row.t,3)} s · θ₂ ${fmt(view.row.theta2,2)}° · wheel ${fmt(view.row.wheelAngularVelocityDegS,2)} °/s · ${view.row.controllerPhase||'terrain'} / ${view.row.motionPhase||'contact'}`;Results.cursor($(id+'-results'),view.row.t);return;}const row=state.result.rows[state.index],frame=state.result.frames[state.index],p={...state.snapshot.params,theta2:row.theta2},z=Kinefold.evaluate(p),svg=$(id+'-preview');if(!z.valid){svg.innerHTML=`<text x="20" y="30" fill="var(--red)">${esc(z.errors.join(' '))}</text>`;return;}
const A=frame.A,translate=v=>[v[0]+A[0],v[1]+A[1],v[2]+A[2]],W=740,H=450,{loX,hiX,loY,hiY}=camera(state,p),scale=Math.min((W-120)/Math.max(200,hiX-loX),(H-120)/Math.max(200,hiY-loY)),P=v=>[W/2+(-v[0]-(loX+hiX)/2)*scale,H/2+(-v[2]-(loY+hiY)/2)*scale],path=vs=>vs.map((v,i)=>(i?'L':'M')+P(v).join(',')).join(' '),line=(vs,c,width=1,attrs='')=>`<path d="${path(vs)}" stroke="${c}" stroke-width="${width}" fill="none" ${attrs}/>`,circle=(v,r,c,width=1)=>`<circle cx="${P(v)[0]}" cy="${P(v)[1]}" r="${r*scale}" stroke="${c}" stroke-width="${width}" fill="none"/>`;
let out='<rect width="740" height="450" fill="var(--paper)"/>';const target=45/scale,b=10**Math.floor(Math.log10(target)),step=[1,2,5,10].map(n=>n*b).reduce((a,n)=>Math.abs(n-target)<Math.abs(a-target)?n:a),origin=P([0,0,0]);for(let x=origin[0]%(step*scale);x<W;x+=step*scale)out+=`<path d="M${x} 0V450" stroke="var(--line)" opacity=".7"/>`;for(let y=origin[1]%(step*scale);y<H;y+=step*scale)out+=`<path d="M0 ${y}H740" stroke="var(--line)" opacity=".7"/>`;
out+=line([frame.A,frame.B],'var(--sage)',12)+line([frame.B,frame.C],'var(--blue)',10)+circle(frame.C,p.rw,'var(--ink)',2);
for(const belt of KinefoldDrawing.belts(z.reference,p.theta2))if(belt.valid){out+=line(belt.outline.map(translate),'var(--muted)',1);for(const point of belt.markers){const [x,y]=P(translate(point));out+=`<circle cx="${x}" cy="${y}" r="1.7" fill="var(--sage)"/>`;}}
for(const axis of KinefoldDrawing.indices(z.reference,p.theta2))out+=circle(translate(axis.center),axis.radius,'var(--amber)',1.2)+line([translate(axis.center),translate(axis.primary)],'var(--red)',1.3)+line([translate(axis.center),translate(axis.secondary)],'var(--red)',.8,'stroke-dasharray="3 3"');
out+=KinefoldDrawing.springSvg(KinefoldDrawing.spring(p,frame),P,scale);
const [ax,az]=P(A),baseZ=row.wheelZMm-p.rw-row.appliedInputMm;
const terrain=Analysis.floor(state.snapshot.solverConfig,row,frame.C[0],-(W/2/scale)+(loX+hiX)/-2,(W/2/scale)+(loX+hiX)/-2);
const floorPoints=points=>points.map(([x,height])=>[x,0,baseZ+height]);
out+=line(floorPoints(terrain.requested),'var(--muted)',1.5,'stroke-dasharray="5 4"')+line(floorPoints(terrain.applied),'var(--amber)',3);
out+=`<rect x="${ax-48}" y="${az-32}" width="96" height="32" rx="4" fill="var(--soft)" stroke="var(--sage)" stroke-width="2"/><text x="${ax}" y="${az-12}" text-anchor="middle" fill="var(--ink)" font-size="11">m₁ ${fmt(p.m1,2)} kg</text>`;
if(terrain.dense)out+=`<text x="22" y="350" fill="var(--amber)" font-size="11">Dense floor display sampled · wheel input remains exact</text>`;
out+=`<path d="M530 425H610m-8-5 8 5-8 5" stroke="var(--amber)" fill="none"/><text x="528" y="411" fill="var(--amber)" font-size="11">Prescribed spatial floor · −x →</text>`;
for(const [point,label]of [[frame.A,'A'],[frame.B,'B'],[frame.C,'C']]){const[x,y]=P(point);out+=`<circle cx="${x}" cy="${y}" r="3" fill="var(--paper)" stroke="var(--ink)"/><text x="${x+(label==='A'?-18:10)}" y="${y+(label==='A'?14:-7)}" fill="var(--ink)" font-size="11">${label}</text>`;}
out+=`<rect x="12" y="12" width="300" height="26" fill="var(--paper)" opacity=".9"/><text x="22" y="29" fill="var(--muted)" font-size="10">WORLD FRAME · GRID ${fmt(step,0)} mm · IDEAL TRANSMISSION</text><rect x="12" y="368" width="184" height="69" fill="var(--paper)" opacity=".94"/><path d="M95 415H35m8-4-8 4 8 4M95 415V382m-4 8 4-8 4 8" fill="none" stroke="var(--ink)" stroke-width="1.4"/><text x="14" y="418" fill="var(--red)" font-size="11">+x</text><text x="105" y="387" fill="var(--blue)" font-size="11">+z</text><text x="108" y="418" fill="var(--sage)" font-size="9">⊙ +y toward you</text>`;
svg.setAttribute('viewBox','0 0 740 450');svg.dataset.theta2=String(row.theta2);svg.dataset.chassisZMm=String(row.chassisZMm);svg.dataset.time=String(row.t);svg.dataset.floorAppliedAtWheel=String(terrain.atWheel.applied);svg.dataset.floorRequestedAtWheel=String(terrain.atWheel.requested);svg.dataset.inputDistanceMm=String(terrain.distance);svg.innerHTML=out;Results.cursor($(id+'-results'),row.t);$(id+'-scrub').value=state.index;$(id+'-time').textContent=`${fmt(row.t,3)} s · chassis ${fmt(row.chassisZMm,2)} mm · θ₂ ${fmt(row.theta2,2)}°`;}
function stop(id){const state=runs[id];state.playing=false;const button=$(id+'-play');if(button){button.textContent='▶';button.setAttribute('aria-pressed','false');}}
function play(id){for(const other of engines)stop(other);const s=runs[id];if(s.index>=s.result.rows.length-1)s.index=0;s.playing=true;s.playStarted=performance.now();s.playTime=s.result.rows[s.index].t;$(id+'-play').textContent='Ⅱ';$(id+'-play').setAttribute('aria-pressed','true');if(!clock)clock=requestAnimationFrame(tick);}
function tick(now){clock=0;for(const id of engines){const s=runs[id];if(!s.playing)continue;const target=s.playTime+(now-s.playStarted)/1000;while(s.index<s.result.rows.length-1&&s.result.rows[s.index+1].t<=target)s.index++;sharedTime=s.result.rows[s.index].t;sharedSide=s.result.rows[s.index].eventSide||'';drawFrame(id);if(s.index>=s.result.rows.length-1)stop(id);}if(engines.some(id=>runs[id].playing))clock=requestAnimationFrame(tick);}
async function download(id,csv) {
  const state=runs[id];if(!state.result)return;
  const name=state.snapshot.name.replace(/[^a-z0-9_-]+/gi,'-').slice(0,60)||'mechanism';
  const content=csv?(()=>{
    const keys=Object.keys(state.result.rows[0]);
    return keys.join(',')+'\n'+state.result.rows.map(row=>keys.map(key=>typeof row[key]==='string'?'"'+row[key].replaceAll('"','""')+'"':row[key]??'').join(',')).join('\n');
  })():JSON.stringify({schema:'kinefold/run-v1',engine:id,projectSnapshot:state.snapshot,runConfig:state.snapshot.solverConfig,result:state.result},null,2);
  try { await KinefoldStudio.saveArtifact(`${name}-${id}.${csv?'csv':'json'}`,content,csv?'text/csv':'application/json'); }
  catch(error) { status(id,'Run export failed: '+error.message,'error'); }
}
for(const id of engines)dynamicShell(id);
window.addEventListener('kinefold-design-change',event=>changed(event.detail));
window.addEventListener('kinefold-solver-tab',event=>{for(const id of engines){if(id!==event.detail.id)stop(id);else if(runs[id].result){runs[id].index=nearestIndex(runs[id].result.rows,sharedTime);drawFrame(id);}}});
if(globalThis.KinefoldStudio)changed(KinefoldStudio.getSnapshot());
viewer('status');
window.dispatchEvent(new Event('kinefold-request-solver-state'));
})();
