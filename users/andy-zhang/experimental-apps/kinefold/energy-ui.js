/** Shared energy-only landing calculator UI; no dynamics API request is made.
 * Inputs: saved energyConfig mm/Nm, shared landing geometry and mechanism.
 * Outputs: constant-torque work screen, Plotly curve and app-folder JSON export.
 * It does not change controller torques or simulate contact. Catalog maximum torque
 * screens are ideal comparisons, not verified hardware or braking ratings.
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
    const manualTorque=panel.querySelector('[data-energy-key="torqueLimitNm"]');
    manualTorque.setAttribute('aria-label','Manual available hip-joint braking torque');
    manualTorque.insertAdjacentHTML('beforebegin','<small>Manual torque · retained when a component screen is selected</small>');
    const example=document.createElement('button');example.type='button';example.dataset.energyTwoMetre='';example.textContent='2 m drop example';
    panel.querySelector('.contact-controls').after(example);
    example.onclick=()=>{const project=S.getSnapshot();S.setEnergyConfig({...P.energyDefaults,...project.energyConfig,dropHeightMm:2000});};
    const catalog=document.createElement('section');catalog.className='energy-catalog';catalog.setAttribute('aria-label','Analysis-only motor and gearbox selection');
    catalog.innerHTML=`<h4>Motor & reduction · saved energy screen only</h4><div class="contact-controls"><label>Motor peak rating<select data-energy-motor><option value="manual">Manual joint torque · saved physical gearing</option><option value="custom">Custom motor peak</option>${A.motors.map(m=>`<option value="${m.id}">${esc(m.name)} · ${m.peakShaftNm} N·m peak</option>`).join('')}</select></label><label>Candidate reduction<select data-energy-gear><option value="direct">Direct drive · 1:1</option>${A.gearboxes.map(g=>`<option value="${g.id}">${g.name} · ${g.ratio}:1</option>`).join('')}<option value="custom">Custom reduction</option></select></label><label>Peak MOTOR-SHAFT torque · N·m<input data-energy-screen="peakShaftNm" type="number" min="0" max="10000" step="any"></label><label>Custom reduction N · :1<input data-energy-screen="customRatio" type="number" min="0.000001" max="10000" step="any"></label><label>Custom gearbox momentary OUTPUT limit · N·m<input data-energy-screen="customMomentaryNm" type="number" min="0" max="10000" step="any" placeholder="Blank = unassessed"></label></div><p>Selections and rating overrides save with this design as calculator settings. They do not apply a motor, reduction or torque command to either dynamic solver. Candidate gearing recalculates conservative cogging energy using the saved enabled motor’s passive parameters; disabled passives remain zero. No catalog inertia, friction or cogging is assumed.</p>`;
    catalog.insertAdjacentHTML('beforeend',`<details><summary>Catalog ratings · 9 motor variants / 4 gearbox models</summary><p>Snapshot transcribed 23 Oct 2026. Motor figures are maximum shaft torque, not continuous ratings. Sale/used listings of the same gearbox are deduplicated.</p><div class="eqd-table-wrap"><table class="energy-catalog-table" aria-label="Flipsky peak torque catalog"><thead><tr><th>Motor</th><th>Peak shaft torque · N·m</th><th>Duration</th></tr></thead><tbody>${A.motors.map(m=>`<tr><td>${esc(m.name)}</td><td>${fmt(m.peakShaftNm)}</td><td>${esc(m.duration)}</td></tr>`).join('')}</tbody></table></div><div class="eqd-table-wrap"><table class="energy-catalog-table" aria-label="EG gearbox output ratings"><thead><tr><th>Gearbox</th><th>Reduction</th><th>Nominal output · N·m</th><th>Momentary output · N·m</th><th>Forward efficiency · reference only</th></tr></thead><tbody>${A.gearboxes.map(g=>`<tr><td>${esc(g.name)}</td><td>${g.ratio}:1</td><td>${g.nominalNm}</td><td>${g.momentaryNm}</td><td>${fmt(g.forwardEfficiency*100)}%</td></tr>`).join('')}</tbody></table></div><p>Gearbox momentary duration and motor/adapter shaft fit are unverified. Forward efficiency does not establish regenerative/backdrive efficiency.</p></details>`);
    example.after(catalog);
    const changeScreen=event=>{try{
      const project=S.getSnapshot(),value={...P.energyDefaults,dropHeightMm:project.caseConfig?.landingDropMm??P.caseDefaults.landingDropMm,...project.energyConfig},motorId=panel.querySelector('[data-energy-motor]').value;
      if(motorId==='manual'){delete value.screening;}else{
        const old=value.screening,fields=Object.fromEntries([...panel.querySelectorAll('[data-energy-screen]')].map(el=>[el.dataset.energyScreen,el.value===''?null:Number(el.value)]));
        const selected=A.motors.find(m=>m.id===motorId);
        value.screening={motorId,gearboxId:panel.querySelector('[data-energy-gear]').value,peakShaftNm:event.target.hasAttribute('data-energy-motor')?(selected?.peakShaftNm??old?.peakShaftNm??20):(fields.peakShaftNm??selected?.peakShaftNm??20),customRatio:fields.customRatio??old?.customRatio??1,customMomentaryNm:fields.customMomentaryNm};
      }S.setEnergyConfig(value);
    }catch(error){S.toast(error.message);update(S.getSnapshot());}};
    for(const field of catalog.querySelectorAll('select,input'))field.onchange=changeScreen;
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
      {type:'scatter',mode:'lines',name:z.screening&&!z.screening.gearboxAssessed?'Motor upper bound · gearbox unassessed':'Available screening joint torque',x:[0,z.curve.at(-1).dropHeightMm],y:[z.availableJointNm,z.availableJointNm],line:{color:'var(--blue)',dash:'dash'},hovertemplate:'Available %{y:.4f} N·m<extra></extra>'},
      {type:'scatter',mode:'markers',name:'Current drop',x:[z.config.dropHeightMm],y:[z.requiredJointNm],marker:{color:'var(--red)',size:9},hovertemplate:'Current %{x:.2f} mm<br>%{y:.4f} N·m<extra></extra>'}
    ],{height:380,margin:{l:80,r:25,t:30,b:100},xaxis:{title:{text:'Drop height H · mm'}},yaxis:{title:{text:'Constant joint braking torque · N·m'},rangemode:'tozero'},legend:{orientation:'h',y:-.25}},{key:'energy-drop-'+panel.dataset.energyPanel}).catch(error=>{if(node.isConnected)panel.querySelector('[data-energy-summary]').textContent='Chart error: '+error.message;});
  }
  function render(panel,z){
    const output=panel.querySelector('[data-energy-output]');KinefoldPlotly.purge(output);
    const card=(label,value,unit)=>`<div class="readout"><span>${label}</span><strong>${fmt(value)}<small>${unit}</small></strong></div>`;
    const rows=[
      ['Supported chassis mass m₁','Saved mechanism · Loadings & preloads',z.massKg,'kg'],
      ['Gravity g','Saved mechanism · Loadings & preloads',z.gravityMS2,'m/s²'],
      ['Drop height H','Editable above · mm ÷ 1000',z.config.dropHeightMm/1000,'m'],
      ['Usable hip rotation Δq','(θ_end − θ₀) × π / 180',z.angularTravelRad,'rad'],
      ['Chassis compression s','(h₀ − h_end) ÷ 1000',z.chassisCompressionMm/1000,'m'],
      ['Impact speed v','√(2gH)',z.impactSpeedMS,'m/s'],
      ['Chassis drop energy','½m₁v² = m₁gH',z.dropJ,'J'],
      ['Gravity during compression','m₁gs',z.gravityCompressionJ,'J'],
      ['Spring energy stored ΔU_spring','U_spring,end − U_spring,start',-z.springReleasedJ,'J'],
      ['Cogging energy stored ΔU_cog','U_cog,end − U_cog,start',-z.coggingReleasedJ,'J'],
      ['Signed net work W','m₁g(H + s) − ΔU_spring − ΔU_cog',z.workJ,'J'],
      ['Required HIP-JOINT braking magnitude','max(0, W / Δq)',z.requiredJointNm,'N·m'],
      ['Active ideal reduction N',z.screening?'Analysis candidate only · physical motor unchanged':'Saved hip motor · disabled motor uses N = 1',z.gearRatio,':1'],
      ['Required MOTOR-SHAFT braking magnitude','τ_joint / N',z.requiredShaftNm,'N·m'],
      [z.screening?'Available screening work':'Available motor work','τ_available,joint × Δq',z.availableWorkJ,'J']
    ];
    const candidate=z.screening;
    const screening=candidate?`<h4>Selected catalog energy screen</h4><p><b>${esc(candidate.motorName)}</b> + <b>${esc(candidate.gearboxName)}</b>. Motor: <b>${candidate.motorPass?'meets':'below'} required ideal shaft torque</b>; gearbox: <b>${candidate.gearboxPass===null?'unassessed — enter a momentary output limit':candidate.gearboxPass?'within momentary output limit':'exceeds momentary output limit'}</b>. ${candidate.peakOverridden?'Saved peak override replaces the catalog value.':''}</p><div class="eqd-table-wrap"><table class="energy-screen-table" aria-label="Motor and gearbox energy screen"><thead><tr><th>Quantity</th><th>Value</th><th>Meaning</th></tr></thead><tbody>
      <tr><td>Required shaft braking magnitude</td><td>${fmt(z.requiredShaftNm,6)} N·m</td><td>Required joint torque ÷ candidate ${fmt(z.gearRatio)}:1</td></tr>
      <tr><td>Motor peak / maximum shaft rating</td><td>${fmt(candidate.peakShaftNm)} N·m</td><td>${esc(candidate.duration)}${candidate.peakOverridden?' · overridden':''}</td></tr>
      <tr><td>Ideal motor joint peak</td><td>${fmt(candidate.idealJointPeakNm)} N·m</td><td>Peak shaft rating × N; ideal transmission</td></tr>
      <tr><td>Gearbox nominal output limit</td><td>${candidate.nominalNm===null?'Not specified':fmt(candidate.nominalNm)+' N·m'}</td><td>Reference nominal rating; not the momentary screen</td></tr>
      <tr><td>Gearbox momentary output limit</td><td>${candidate.momentaryNm===null?(candidate.gearboxId==='direct'?'No gearbox':'Unassessed'):fmt(candidate.momentaryNm)+' N·m'}</td><td>Separate output limit; momentary duration unspecified</td></tr>
      <tr><td>Effective screening joint capacity</td><td>${fmt(candidate.effectiveJointNm)} N·m</td><td>min(ideal motor joint peak, gearbox momentary limit), when assessed</td></tr>
    </tbody></table></div><p>Catalog snapshot: 23 Oct 2026. Flipsky maximum/marketing peak is used as an ideal controllable resisting-torque assumption, not a verified braking rating. Regeneration, controller/DC bus, thermal duration, shaft/adapter fit and subsequent holding are unverified. ${candidate.forwardEfficiency===null?'':`Listed forward efficiency ${fmt(candidate.forwardEfficiency*100)}% is reference only; no unvalidated backdrive-efficiency credit is used.`} <a href="https://flipsky.net/collections/motor" target="_blank" rel="noreferrer">Flipsky motor family</a> · <a href="https://www.omc-stepperonline.com/nema-23-eg-series-planetary-gearbox" target="_blank" rel="noreferrer">EG gearbox family</a>.</p>`:'';
    output.innerHTML=`
      <p class="notice ${z.passes&&!z.boundaryOnly?'':'error'}"><strong>${z.boundaryOnly?'Stop-boundary calculation only — zero reserve does not avoid the stop':z.screening&&!z.screening.gearboxAssessed?'Custom gearbox capacity is unassessed':z.passes?(z.screening?'Selected components pass the catalog endpoint energy screen':'Available torque passes this endpoint energy screen'):'Available motor/gearbox torque is below the endpoint energy requirement'}.</strong> Limiter: ${esc(z.limiter)}. Initial-arrest work screen, not a peak-torque or post-arrest holding guarantee.</p>
      <div class="solver-readouts">${card('Constant joint resisting torque magnitude',z.requiredJointNm,'N·m')}${card('Motor-shaft resisting magnitude · N='+fmt(z.gearRatio),z.requiredShaftNm,'N·m')}${card(z.screening&&!z.screening.gearboxAssessed?'Motor-only drop screen · gearbox unassessed':'Drop capacity at selected endpoint',z.capacityMm,'mm')}${card('Clearance at arrest endpoint',z.endClearanceMm,'mm')}</div>
      ${screening}
      <h4>Landing energy equation · live calculator</h4>
      <p><b>τ_joint = max[0, (m₁g(H + s) − ΔU_spring − ΔU_cog) / Δq]</b><br>τ_shaft = τ_joint / N. Positive stored spring/cogging energy reduces the motor work; a negative value releases energy.</p>
      <div class="eqd-table-wrap"><table class="energy-equation-table" aria-label="Landing energy equation calculator"><thead><tr><th>Quantity</th><th>Equation / source</th><th>Value</th><th>Unit</th></tr></thead><tbody>${rows.map(([label,equation,value,unit])=>`<tr><td>${label}</td><td>${equation}</td><td>${fmt(value,6)}</td><td>${unit}</td></tr>`).join('')}</tbody></table></div>
      <p>For these inputs: max[0, ${fmt(z.workJ,6)} J / ${fmt(z.angularTravelRad,6)} rad] = <b>${fmt(z.requiredJointNm,6)} joint N·m</b>; ÷ ${fmt(z.gearRatio)} = <b>${fmt(z.requiredShaftNm,6)} shaft N·m</b>. Edit drop height, residual clearance, reserve and available torque above; mass, gravity and spring come from the shared saved design. ${z.screening?'Reduction is the analysis candidate selected above; saved physical motor settings remain unchanged.':'Gearing comes from the saved physical motor.'}</p>
      <p>Braking commands are −${fmt(z.requiredJointNm)} joint N·m / −${fmt(z.requiredShaftNm)} shaft N·m during positive compression. Available torque is <b>${fmt(z.availableJointNm)} joint N·m</b> (${fmt(z.availableShaftNm)} shaft N·m), regardless of the dynamic command-basis setting. Capacity is a sufficient endpoint screen, not a global maximum over spring/cogging barriers.</p>
      <div data-energy-plot style="height:380px;width:100%" aria-label="Energy-only drop height versus constant braking torque"></div>
      <details><summary>Geometry details</summary><ol><li>Saved opening ${fmt(z.openingFraction,5)} gives θ₀=${fmt(z.qStartDeg)}°. Wheel centre is fixed at wheel radius above flat floor.</li><li>Hip height h=r_w−C_z(q); underbody clearance=h−${fmt(z.undersideOffsetMm)} mm. Initial clearance ${fmt(z.initialClearanceMm)} mm.</li><li>Stop reserve ${fmt(z.config.compressionReserveDeg)}° and ground-clearance target ${fmt(z.config.targetClearanceMm)} mm give θ_end=${fmt(z.qEndDeg)}°, Δq=${fmt(z.angularTravelRad,6)} rad and chassis compression ${fmt(z.chassisCompressionMm)} mm.</li></ol></details>
      <p>Scope: supported quarter chassis m₁=${fmt(z.massKg)} kg; massless moving links, vertical path and stationary wheel during braking. Full chassis drop energy is retained without impact-loss credit; wheel impact energy is excluded. Rotor starts/ends at rest, so inertia adds no endpoint energy; it affects transient dynamics and peaks. No motor/joint friction credit, electrical efficiency, tire compliance or post-arrest controller behavior is inferred. ${z.screening?'Catalog peak torque remains a screening assumption; sustained braking capability is unverified.':''}</p>`;
  }
  function update(project){
    const config={...P.energyDefaults,dropHeightMm:project.caseConfig?.landingDropMm??P.caseDefaults.landingDropMm,...project.energyConfig},c={...P.caseDefaults,...project.caseConfig};
    for(const panel of document.querySelectorAll('[data-energy-panel]')){
      for(const input of panel.querySelectorAll('[data-energy-key]'))input.value=config[input.dataset.energyKey];
      const screen=config.screening;panel.querySelector('[data-energy-motor]').value=screen?.motorId??'manual';panel.querySelector('[data-energy-gear]').value=screen?.gearboxId??'direct';panel.querySelector('[data-energy-gear]').disabled=!screen;
      for(const field of panel.querySelectorAll('[data-energy-screen]')){const key=field.dataset.energyScreen;field.value=screen?.[key]??(key==='customRatio'?1:'');field.disabled=!screen||(key!=='peakShaftNm'&&screen.gearboxId!=='custom');}
      panel.querySelector('[data-energy-key="torqueLimitNm"]').disabled=!!screen;
      panel.querySelector('[data-energy-key="torqueLimitNm"]').title=screen?'Manual torque retained; candidate peak and gearbox limit set screening capacity.':'';
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
