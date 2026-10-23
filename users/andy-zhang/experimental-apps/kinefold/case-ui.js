/** Visible saved terrain/jump/landing controls and bounded target torque sizing.
 * Load after contact-ui.js. Inputs: builder mm/deg/kg/N, SI run settings and
 * optional project-v3 caseConfig. Outputs: synchronized saved controls and a
 * captured-engine torque-search report; no design is modified by assessment.
 * Values for jump torque/drop/braking are editable study examples, not ratings.
 */
globalThis.KinefoldCaseUI = (() => {
  'use strict';
  const S = KinefoldStudio, P = KinefoldProjects;
  const esc = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number = (key, label, unit, min, max, step = 'any') => `<label>${label} · ${unit}<input data-case-key="${key}" type="number" min="${min}" max="${max}" step="${step}"></label>`;
  function mount(id, root) {
    const panel = document.createElement('section');
    panel.className = 'case-panel contact-mode-panel'; panel.dataset.casePanel = id;
    panel.innerHTML = `<div class="contact-mode-heading"><div><span class="eyebrow">SHARED SAVED CASE · ¼ MODEL</span><h3>Terrain, jump or landing</h3></div><label>Case<select data-case-key="kind"><option value="terrain-stability">Terrain stability</option><option value="jump">Jump · compressed start</option><option value="landing">Landing · held drop</option></select></label></div><section class="case-settings"><h4>Case inputs & target torque</h4><div class="contact-controls"><div data-case-for="jump">${number('jumpTorqueNm','Extension motor torque','N·m',0,10000)}<label>Target chassis rise ABOVE TAKEOFF · mm<input data-target-key="jumpHeightMm" type="number" min="0" max="5000"></label><label>Search torque ceiling · N·m<input data-target-key="jumpTorqueLimitNm" type="number" min="0" max="10000"></label></div><div data-case-for="landing">${number('landingDropMm','Drop height · initial wheel-bottom gap','mm',0,5000)}<label>Minimum UNDERBODY ground clearance · mm<input data-target-key="landingClearanceMm" type="number" min="0" max="5000"></label>${number('landingOpenFraction','Initial opening fraction','0–1',.01,.99,.01)}<label>Braking strategy<select data-case-key="brakeStrategy"><option value="entered">Entered constant resisting torque</option><option value="energy-sized">Legacy energy-sized command · not clearance-targeted</option></select></label>${number('landingBrakeTorqueNm','Entered resisting torque','N·m',0,10000)}${number('landingBrakeLimitNm','Brake/search torque limit','N·m',0,10000)}</div><div><label>Chassis underside below hip A · mm<input data-case-key="undersideOffsetMm" type="number" min="0" max="5000" placeholder="Blank = chassis strike unassessed"></label><label><input data-case-key="energyMethod" type="checkbox"> Show energy-method sizing and work accounting</label></div></div><div data-target-actions><button class="primary" data-case-search>Solve torque for target</button> <button data-copy-energy>Copy landing targets to energy calculator</button><p data-case-basis></p><p data-target-energy></p><p>Jump height excludes stance rise: it is the first airborne chassis apex above actual takeoff. Landing clearance is measured through first arrest, separate from the underside offset. Solving does not change a command.</p></div><details><summary>Case assumptions</summary><div data-case-description></div></details><p>The example torque/drop values are study inputs. A null underside offset leaves chassis collision unassessed. The mechanism, masses and spring remain the builder design.</p></section><div data-case-assessment role="status"></div>`;
    root.querySelector('.quarter-scope').before(panel);
    for (const input of panel.querySelectorAll('[data-case-key]')) input.onchange = () => {
      try {
        const current = S.getSnapshot(), config = {...P.caseDefaults, ...current.caseConfig};
        for (const field of panel.querySelectorAll('[data-case-key]')) {
          const key = field.dataset.caseKey;
          config[key] = field.type === 'checkbox' ? field.checked : field.tagName === 'SELECT' ? field.value : field.value === '' ? (key === 'undersideOffsetMm' ? null : NaN) : Number(field.value);
        }
        S.setCaseConfig(config);
      } catch (error) { S.toast(error.message); update(S.getSnapshot()); }
    };
    for(const field of panel.querySelectorAll('[data-target-key]'))field.onchange=()=>{try{S.setTorqueTargetConfig({...targets(S.getSnapshot()),[field.dataset.targetKey]:field.value===''?NaN:Number(field.value)});}catch(error){S.toast(error.message);update(S.getSnapshot());}};
    panel.querySelector('[data-copy-energy]').onclick=()=>{const p=S.getSnapshot(),c={...P.caseDefaults,...p.caseConfig};S.setEnergyConfig({...P.energyDefaults,...p.energyConfig,dropHeightMm:c.landingDropMm,targetClearanceMm:targets(p).landingClearanceMm});S.toast('Landing drop and clearance copied to the separate energy calculator.');};
    panel.querySelector('[data-case-search]').onclick = () => assess(id);
  }
  const targets=p=>({...P.torqueTargetDefaults,...p.torqueTargetConfig});
  const searchKey=p=>JSON.stringify([KinefoldDynamicAnalysis.snapshotKey(p),targets(p)]);
  const captured=new Map();let searching=false;
  function update(project) {
    const config = {...P.caseDefaults, ...project.caseConfig}, contact = KinefoldContactUI.isContact(project);
    for (const panel of document.querySelectorAll('[data-case-panel]')) {
      for (const field of panel.querySelectorAll('[data-case-key]')) {
        const key = field.dataset.caseKey;
        if (field.type === 'checkbox') field.checked = config[key]; else field.value = config[key] ?? '';
        field.disabled = !contact || (key==='landingBrakeTorqueNm'&&config.brakeStrategy==='energy-sized');
      }
      for (const group of panel.querySelectorAll('[data-case-for]')) group.hidden = group.dataset.caseFor !== config.kind;
      for(const input of panel.closest('[role=tabpanel]').querySelectorAll('[data-run-key^=input]'))input.disabled=contact&&config.kind!=='terrain-stability';
      const workspace=panel.closest('[role=tabpanel]'),scenario=contact&&config.kind!=='terrain-stability';
      for(const key of ['hipTorqueNm','initialVelocityDegS'])workspace.querySelector(`[data-run-key="${key}"]`).disabled=scenario;
      workspace.querySelector('[data-release]').disabled=scenario;
      workspace.querySelector('[data-run-key="hipTorqueNm"]').closest('details').querySelector('p').textContent=scenario?'This case starts at zero speed and uses the explicit motor/hold/braking commands in Case controls. Constant hip torque and Release are overridden; damping remains active.':'These actions set one constant torque; they do not add a feedback controller.';
      workspace.querySelector('[data-run-key="inputHeightMm"]').closest('details').querySelector('p').textContent=!contact?'Width and gap map to time through the entered speed. Positive transition distance applies smooth ramps inside the square plateau; requested and applied inputs are plotted separately.':scenario?'Jump and landing use a stationary flat collision floor. Terrain dimensions, translation speed, transition and initial rim delay are unused by these cases.':'Actual square polygons translate at the entered speed. Width, gap and rim-clearance delay define world collision geometry; zero transition is required. Wheel height is solved by contact.';
      panel.querySelector('[data-case-search]').disabled = searching||!contact||config.kind==='terrain-stability';
      panel.querySelector('[data-target-actions]').hidden=config.kind==='terrain-stability';
      panel.querySelector('[data-copy-energy]').hidden=config.kind!=='landing';
      panel.querySelector('[data-target-key="jumpTorqueLimitNm"]').closest('label').firstChild.textContent='Search torque ceiling · '+KinefoldMotorUI.basis(project)+' N·m';
      panel.querySelector('[data-case-basis]').textContent='Commands and search ceilings use '+KinefoldMotorUI.basis(project)+'-side N·m. Use tested torque retains this basis.';
      for(const field of panel.querySelectorAll('[data-target-key]')){field.value=targets(project)[field.dataset.targetKey];field.disabled=!contact;}
      let message='';try{if(config.kind==='jump'){const e=KinefoldEnergyAnalysis.jumpEstimate(project,targets(project).jumpHeightMm);message='Ideal jump work estimate: '+e.jointNm.toFixed(3)+' N·m joint / '+e.shaftNm.toFixed(3)+' N·m shaft. Full extension at takeoff; ignores stop/friction losses, not a guarantee.';}else if(config.kind==='landing'){const e=KinefoldEnergyAnalysis.calculate({...project,energyConfig:{...P.energyDefaults,...project.energyConfig,dropHeightMm:config.landingDropMm,targetClearanceMm:targets(project).landingClearanceMm}});message='Conservative chassis-only energy screen for these targets: '+e.requiredJointNm.toFixed(3)+' N·m joint / '+e.requiredShaftNm.toFixed(3)+' N·m shaft; '+e.config.compressionReserveDeg+'° pre-stop reserve. Initial arrest work only; simulation tests impact and clearance.';}}catch(error){message='Energy estimate unavailable: '+error.message;}
      panel.querySelector('[data-target-energy]').textContent=message;
      panel.querySelector('[data-case-description]').innerHTML = !contact ? '<p>These cases use actual terrain contact. Select the contact interaction model above to run them; the prescribed-height benchmark remains unchanged.</p>' : config.kind === 'jump' ? '<p><strong>Jump:</strong> stationary flat floor; start fully compressed at θ₂ = θ_c with zero velocity. Entered extension torque acts until the extension stop, then cuts off. Takeoff, apex, stop losses and motor work are measured from the trajectory.</p>' : config.kind === 'landing' ? `<p><strong>Landing:</strong> stationary flat floor; start at θ_c + ${config.landingOpenFraction.toFixed(4)}(θ_e − θ_c), at rest with the entered wheel-bottom gap. The motor compensates the spring during free fall, then releases the hold and resists compression after first contact. Bottom-out before arrest is a failed landing. Energy sizing is an average-work estimate; the bounded simulation search tests dynamic arrest.</p>` : '<p><strong>Terrain stability:</strong> actual moving square mesh, free wheel spin and unilateral friction contact. Terrain dimensions/speed come from the shared input settings. Both independent engines use the same captured case and compare at common sample times.</p>';
      const saved=captured.get(panel.dataset.casePanel),output=panel.querySelector('[data-case-assessment]');
      if(saved){const stale=searchKey(project)!==saved.key;output.querySelector('[data-study-stale]')?.toggleAttribute('hidden',!stale);const apply=output.querySelector('[data-apply-torque]');if(apply)apply.disabled=stale||!saved.value.feasible;}
    }
  }
  async function assess(id) {
    const project=structuredClone(S.getSnapshot()),key=searchKey(project),config={...P.caseDefaults,...project.caseConfig};
    const panel=document.querySelector(`[data-case-panel="${id}"]`),output=panel.querySelector('[data-case-assessment]');
    searching=true;update(project);output.textContent='Testing at most 10 captured commands with '+id+'; waiting for '+(config.kind==='jump'?'the first flight apex':'first chassis arrest')+'. Duration is never extended…';
    try {
      const request={...KinefoldContactUI.payload(project,id),study:'target-case-torque',torqueTargetConfig:targets(project)};
      const response=await fetch('/api/contact-study',{method:'POST',headers:{'Content-Type':'application/json','X-Kinefold-Request':'coupled-dynamics'},body:JSON.stringify(request)});
      const value=await response.json();if(!response.ok||value.error)throw Error(value.error||'Target study failed.');
      captured.set(id,{key,value});
      const fmt=v=>Number.isFinite(v)?v.toLocaleString('en-CA',{maximumFractionDigits:3}):'—',basis=KinefoldMotorUI.basis(project);
      output.innerHTML=`<p class="notice" data-study-stale hidden>Earlier profile/targets · solve again before applying a command.</p><h4>${id==='analytical'?'Analytical':'Pymunk'} target sizing · ${esc(value.status)}</h4><div class="solver-readouts"><div class="readout"><span>Lowest passing tested · ${basis}</span><strong>${fmt(value.torqueNm)}<small>N·m</small></strong></div><div class="readout"><span>Lower known-failing bracket</span><strong>${fmt(value.lowerBoundNm)}<small>N·m</small></strong></div><div class="readout"><span>${config.kind==='jump'?'Achieved flight rise':'Minimum clearance through arrest'}</span><strong>${fmt(value.bestTrial?.achievedMm)}<small>mm</small></strong></div></div><button data-apply-torque>Use tested torque</button> <button data-export-case-assessment>Export assessment JSON</button><p>${esc(value.limitation)}</p><p>${esc(value.assessmentStopPolicy)}</p><details><summary>${value.trials.length} tested commands & diagnostics</summary><div class="eqd-table-wrap"><table><thead><tr><th>${basis} torque · N·m</th><th>Status / outcome</th><th>Achieved · mm</th></tr></thead><tbody>${value.trials.map(r=>`<tr><td>${fmt(r.torqueNm)}</td><td>${esc(r.status)} · ${esc(r.outcome)}</td><td>${fmt(r.achievedMm)}</td></tr>`).join('')}</tbody></table></div><pre>${esc(JSON.stringify(value,null,2))}</pre></details>`;
      output.querySelector('[data-apply-torque]').onclick=()=>{
        if(searchKey(S.getSnapshot())!==key){S.toast('Profile or targets changed. Solve again before using this command.');update(S.getSnapshot());return;}
        const c={...P.caseDefaults,...S.getSnapshot().caseConfig};if(c.kind==='jump')c.jumpTorqueNm=value.torqueNm;else{c.brakeStrategy='entered';c.landingBrakeTorqueNm=value.torqueNm;}S.setCaseConfig(c);S.toast('Tested command applied. Run normally to inspect the full trajectory and compare engines.');
      };
      output.querySelector('[data-export-case-assessment]').onclick=()=>S.saveArtifact('kinefold-target-torque-assessment.json',{schema:'kinefold/target-torque-assessment-v1',engine:id,projectSnapshot:project,assessment:value});
    }catch(error){output.textContent='Target assessment unavailable: '+error.message+' No command was applied.';}
    finally{searching=false;update(S.getSnapshot());}
  }
  return {mount,update,searchKey};
})();
