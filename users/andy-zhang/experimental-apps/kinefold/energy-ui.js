/** Shared energy-only landing calculator UI; no dynamics API request is made.
 * Inputs: saved energyConfig mm/Nm, shared landing geometry and mechanism.
 * Outputs: constant-torque work screen, Plotly curve and app-folder JSON export.
 * It does not change controller torques, simulate contact, or rate a peak motor.
 */
globalThis.KinefoldEnergyUI=(()=>{
  'use strict';
  const S=KinefoldStudio,P=KinefoldProjects,A=KinefoldEnergyAnalysis,states=new WeakMap();
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt=(v,n=3)=>Number.isFinite(v)?v.toLocaleString('en-CA',{maximumFractionDigits:n}):'Unavailable';
  const input=(key,label,unit,min,max,step='any')=>`<label>${label} · ${unit}<input data-energy-key="${key}" type="number" min="${min}" max="${max}" step="${step}"></label>`;
  function mount(id,root){
    const panel=document.createElement('details');panel.className='contact-mode-panel energy-panel';panel.dataset.energyPanel=id;
    panel.innerHTML=`<summary><strong>Energy only · drop height → braking torque</strong> <small data-energy-summary>No simulation required</small></summary><p>Instant work–energy calculation for the same saved mechanism. The target below is <b>underbody-to-ground clearance</b>, distinct from the chassis underside offset below hip A.</p><div class="contact-controls">${input('dropHeightMm','Drop height H','mm',0,5000)}${input('targetClearanceMm','Residual ground clearance target','mm',0,5000)}${input('compressionReserveDeg','Reserve before compression stop','°',0,180)}${input('torqueLimitNm','Available constant HIP-JOINT braking torque','N·m',0,10000)}</div><details><summary>Shared landing geometry</summary><div class="contact-controls"><label>Saved landing opening fraction · 0–1<input data-energy-case="landingOpenFraction" type="number" min=".01" max=".99" step=".01"></label><label>Saved underside offset BELOW HIP A · mm<input data-energy-case="undersideOffsetMm" type="number" min="0" max="5000" placeholder="Blank = unassessed"></label></div><p>These two inputs edit the saved landing case geometry. Calculator inputs do not change dynamic torque commands or controllers.</p></details><div data-energy-output role="status"></div><div class="design-actions"><button data-energy-export>Export energy calculation JSON</button><button data-energy-remove>Remove calculator block</button></div>`;
    root.querySelector('.quarter-scope').before(panel);states.set(panel,{key:'',result:null});
    for(const field of panel.querySelectorAll('[data-energy-key]'))field.onchange=()=>{
      try{const project=S.getSnapshot(),value={...P.energyDefaults,dropHeightMm:project.caseConfig?.landingDropMm??P.caseDefaults.landingDropMm,...project.energyConfig};for(const el of panel.querySelectorAll('[data-energy-key]'))value[el.dataset.energyKey]=el.value===''?NaN:Number(el.value);S.setEnergyConfig(value);}
      catch(error){S.toast(error.message);update(S.getSnapshot());}
    };
    for(const field of panel.querySelectorAll('[data-energy-case]'))field.onchange=()=>{
      try{const value={...P.caseDefaults,...S.getSnapshot().caseConfig};for(const el of panel.querySelectorAll('[data-energy-case]'))value[el.dataset.energyCase]=el.value===''?(el.dataset.energyCase==='undersideOffsetMm'?null:NaN):Number(el.value);S.setCaseConfig(value);}
      catch(error){S.toast(error.message);update(S.getSnapshot());}
    };
    panel.querySelector('[data-energy-remove]').onclick=()=>S.setEnergyConfig(null);
    panel.querySelector('[data-energy-export]').onclick=async()=>{try{const project=S.exportProject(),result=A.calculate(project);await S.saveArtifact('kinefold-energy-drop-torque.json',{schema:'kinefold/energy-drop-torque-v1',projectSnapshot:project,calculation:result,assumptions:'Chassis-only full m1*g*H; stationary flat floor/fixed wheel; rest endpoints; no impact/friction credit; initial arrest only, not peak or post-arrest hold.'});}catch(error){S.toast('Energy export unavailable: '+error.message);}};
    panel.ontoggle=()=>{if(panel.open)draw(panel);};
  }
  function draw(panel){
    const state=states.get(panel),node=panel.querySelector('[data-energy-plot]');
    if(!state.result||!node||!panel.open||panel.closest('[role=tabpanel]').hidden)return;
    if(node.dataset.rendered===state.key){KinefoldPlotly.resize(node);return;}
    node.dataset.rendered=state.key;const z=state.result;
    KinefoldPlotly.react(node,[
      {type:'scatter',mode:'lines',name:'Required constant joint braking torque',x:z.curve.map(r=>r.dropHeightMm),y:z.curve.map(r=>r.jointTorqueNm),line:{color:'var(--sage)',width:2},hovertemplate:'Drop %{x:.2f} mm<br>Joint braking %{y:.4f} N·m<extra></extra>'},
      {type:'scatter',mode:'lines',name:'Available joint torque',x:[0,z.curve.at(-1).dropHeightMm],y:[z.availableJointNm,z.availableJointNm],line:{color:'var(--blue)',dash:'dash'},hovertemplate:'Available %{y:.4f} N·m<extra></extra>'},
      {type:'scatter',mode:'markers',name:'Current drop',x:[z.config.dropHeightMm],y:[z.requiredJointNm],marker:{color:'var(--red)',size:9},hovertemplate:'Current %{x:.2f} mm<br>%{y:.4f} N·m<extra></extra>'}
    ],{height:380,margin:{l:80,r:25,t:30,b:100},xaxis:{title:{text:'Drop height H · mm'}},yaxis:{title:{text:'Constant joint braking torque · N·m'},rangemode:'tozero'},legend:{orientation:'h',y:-.25}},{key:'energy-drop-'+panel.dataset.energyPanel}).catch(error=>{if(node.isConnected)panel.querySelector('[data-energy-summary]').textContent='Chart error: '+error.message;});
  }
  function render(panel,z){
    const output=panel.querySelector('[data-energy-output]');KinefoldPlotly.purge(output);
    const card=(label,value,unit)=>`<div class="readout"><span>${label}</span><strong>${fmt(value)}<small>${unit}</small></strong></div>`;
    output.innerHTML=`<p class="notice ${z.passes&&!z.boundaryOnly?'':'error'}"><strong>${z.boundaryOnly?'Stop-boundary calculation only — zero reserve does not avoid the stop':z.passes?'Available torque passes this endpoint energy screen':'Available torque is below the endpoint energy requirement'}.</strong> Limiter: ${esc(z.limiter)}. Initial-arrest work screen, not a peak-torque or post-arrest holding guarantee.</p><div class="solver-readouts">${card('Constant joint resisting torque magnitude',z.requiredJointNm,'N·m')}${card('Motor-shaft resisting magnitude · N='+fmt(z.gearRatio),z.requiredShaftNm,'N·m')}${card('Drop capacity at selected endpoint',z.capacityMm,'mm')}${card('Clearance at arrest endpoint',z.endClearanceMm,'mm')}</div><p>Braking commands are −${fmt(z.requiredJointNm)} joint N·m / −${fmt(z.requiredShaftNm)} shaft N·m during positive compression. Available torque is <b>${fmt(z.availableJointNm)} joint N·m</b> (${fmt(z.availableShaftNm)} shaft N·m), regardless of the dynamic command-basis setting. Capacity is a sufficient endpoint screen, not a global maximum over spring/cogging barriers.</p><div data-energy-plot style="height:380px;width:100%" aria-label="Energy-only drop height versus constant braking torque"></div><details><summary>Geometry and work–energy calculation</summary><ol><li>Saved opening ${fmt(z.openingFraction,5)} gives θ₀=${fmt(z.qStartDeg)}°. Wheel centre is fixed at wheel radius above flat floor.</li><li>Hip height h=r_w−C_z(q); underbody clearance=h−${fmt(z.undersideOffsetMm)} mm. Initial clearance ${fmt(z.initialClearanceMm)} mm.</li><li>Stop reserve ${fmt(z.config.compressionReserveDeg)}° and ground-clearance target ${fmt(z.config.targetClearanceMm)} mm give θ_end=${fmt(z.qEndDeg)}°, Δq=${fmt(z.angularTravelRad,6)} rad and chassis compression ${fmt(z.chassisCompressionMm)} mm.</li><li>v=√(2gH)=${fmt(z.impactSpeedMS,5)} m/s; ½m₁v²=m₁gH=${fmt(z.dropJ,6)} J. Full chassis drop energy is retained without impact-loss credit.</li><li>τ_joint=max[0, (m₁gH + gravity released + spring released + cogging released)/Δq]; τ_shaft=τ_joint/N.</li></ol><div class="eqd-table-wrap"><table><thead><tr><th>Energy term</th><th>J</th></tr></thead><tbody>${[['Chassis drop · ½m₁v²',z.dropJ],['Gravity released during compression',z.gravityCompressionJ],['Spring released · negative means absorbed',z.springReleasedJ],['Cogging released · signed',z.coggingReleasedJ],['Net work to absorb',z.workJ],['Available joint motor work · τΔq',z.availableWorkJ]].map(([l,v])=>`<tr><td>${l}</td><td>${fmt(v,6)}</td></tr>`).join('')}</tbody></table></div></details><p>Scope: supported quarter chassis m₁=${fmt(z.massKg)} kg; massless moving links, vertical path and stationary wheel during braking. Wheel impact energy is excluded. Rotor starts/ends at rest, so inertia adds no endpoint energy; it affects transient dynamics and peaks. No motor/joint friction credit, electrical efficiency, tire compliance or post-arrest controller behavior is inferred.</p>`;
  }
  function update(project){
    const config={...P.energyDefaults,dropHeightMm:project.caseConfig?.landingDropMm??P.caseDefaults.landingDropMm,...project.energyConfig},c={...P.caseDefaults,...project.caseConfig};
    for(const panel of document.querySelectorAll('[data-energy-panel]')){
      for(const input of panel.querySelectorAll('[data-energy-key]'))input.value=config[input.dataset.energyKey];
      for(const input of panel.querySelectorAll('[data-energy-case]'))input.value=c[input.dataset.energyCase]??'';
      panel.querySelector('[data-energy-remove]').disabled=!project.energyConfig;
      const state=states.get(panel),key=JSON.stringify([project.id,{...project.params,theta2:null},c.landingOpenFraction,c.undersideOffsetMm,project.motorConfig,config]);
      if(key===state.key){if(panel.open)draw(panel);continue;}state.key=key;
      try{const z=A.calculate(project);state.result=z;render(panel,z);panel.querySelector('[data-energy-summary]').textContent=`${fmt(z.requiredJointNm)} joint N·m · no simulation`;panel.querySelector('[data-energy-export]').disabled=false;draw(panel);}
      catch(error){state.result=null;KinefoldPlotly.purge(panel.querySelector('[data-energy-output]'));panel.querySelector('[data-energy-output]').innerHTML=`<p class="notice error">${esc(error.message)}</p>`;panel.querySelector('[data-energy-summary]').textContent='Geometry/input unavailable';panel.querySelector('[data-energy-export]').disabled=true;}
    }
  }
  window.addEventListener('kinefold-solver-tab',()=>{for(const panel of document.querySelectorAll('[data-energy-panel]'))if(panel.open)draw(panel);});
  return {mount,update};
})();
