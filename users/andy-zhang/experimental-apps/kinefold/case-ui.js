/** Shared saved terrain/jump/landing controls and bounded landing assessment.
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
    panel.innerHTML = `<div class="contact-mode-heading"><div><span class="eyebrow">SHARED SAVED CASE · ¼ MODEL</span><h3>Terrain, jump or landing</h3></div><label>Case<select data-case-key="kind"><option value="terrain-stability">Terrain stability</option><option value="jump">Jump · compressed start</option><option value="landing">Landing · held drop</option></select></label></div><div data-case-description></div><details class="case-settings"><summary>Case controls & energy method <small>Editable study examples</small></summary><div class="contact-controls"><div data-case-for="jump">${number('jumpTorqueNm','Extension motor torque','N·m',0,10000)}</div><div data-case-for="landing">${number('landingDropMm','Initial wheel-bottom gap','mm',0,5000)}${number('landingOpenFraction','Initial opening fraction','0–1',.01,.99,.01)}<label>Braking strategy<select data-case-key="brakeStrategy"><option value="entered">Entered constant resisting torque</option><option value="energy-sized">Energy-sized average torque</option></select></label>${number('landingBrakeTorqueNm','Entered resisting torque','N·m',0,10000)}${number('landingBrakeLimitNm','Brake/search torque limit','N·m',0,10000)}<button data-case-search>Estimate minimum landing torque</button></div><div><label>Chassis underside below hip A · mm<input data-case-key="undersideOffsetMm" type="number" min="0" max="5000" placeholder="Blank = chassis strike unassessed"></label><label><input data-case-key="energyMethod" type="checkbox"> Show energy-method sizing and work accounting</label></div></div><p>The example torque/drop values are study inputs. A null underside offset leaves chassis collision unassessed. The mechanism, masses and spring remain the builder design.</p></details><div data-case-assessment role="status"></div>`;
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
    panel.querySelector('[data-case-search]').onclick = () => assess(id);
  }
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
      panel.querySelector('[data-case-search]').disabled = !contact || config.kind !== 'landing';
      panel.querySelector('[data-case-description]').innerHTML = !contact ? '<p>These cases use actual terrain contact. Select the contact interaction model above to run them; the prescribed-height benchmark remains unchanged.</p>' : config.kind === 'jump' ? '<p><strong>Jump:</strong> stationary flat floor; start fully compressed at θ₂ = θ_c with zero velocity. Entered extension torque acts until the extension stop, then cuts off. Takeoff, apex, stop losses and motor work are measured from the trajectory.</p>' : config.kind === 'landing' ? `<p><strong>Landing:</strong> stationary flat floor; start at θ_c + ${config.landingOpenFraction.toFixed(4)}(θ_e − θ_c), at rest with the entered wheel-bottom gap. The motor compensates the spring during free fall, then releases the hold and resists compression after first contact. Bottom-out before arrest is a failed landing. Energy sizing is an average-work estimate; the bounded simulation search tests dynamic arrest.</p>` : '<p><strong>Terrain stability:</strong> actual moving square mesh, free wheel spin and unilateral friction contact. Terrain dimensions/speed come from the shared input settings. Both independent engines use the same captured case and compare at common sample times.</p>';
      const assessment = panel.querySelector('[data-case-assessment]');
      if (assessment.dataset.snapshot && assessment.dataset.snapshot !== KinefoldDynamicAnalysis.snapshotKey(project)) assessment.innerHTML = '<p class="notice">Earlier snapshot assessment · rerun the search for this profile.</p>';
    }
  }
  async function assess(id) {
    const project = structuredClone(S.getSnapshot()), panel = document.querySelector(`[data-case-panel="${id}"]`), output = panel.querySelector('[data-case-assessment]'), button = panel.querySelector('[data-case-search]');
    button.disabled = true; output.textContent = 'Searching the captured landing case within the entered torque limit…';
    try {
      const request = {...KinefoldContactUI.payload(project, id), study: 'minimum-landing-torque'};
      const response = await fetch('/api/contact-study', {method:'POST', headers:{'Content-Type':'application/json','X-Kinefold-Request':'coupled-dynamics'}, body:JSON.stringify(request)});
      const value = await response.json(); if (!response.ok || value.error) throw Error(value.error || 'Landing assessment failed.');
      output.dataset.snapshot = KinefoldDynamicAnalysis.snapshotKey(project);
      const fmt = v => Number.isFinite(v) ? v.toLocaleString('en-CA',{maximumFractionDigits:3}) : '—';
      const trials = Array.isArray(value.evaluations) ? value.evaluations : value.trials || [];
      output.innerHTML = `<button data-export-case-assessment>Export assessment JSON</button><h4>${id==='analytical'?'Analytical':'Pymunk'} first-arrest assessment · ${value.feasible?'A passing torque was found':'No passing torque found within the limit'}</h4><div class="solver-readouts"><div class="readout"><span>Lowest passing tested torque</span><strong>${fmt(value.torqueNm)}<small>N·m</small></strong></div><div class="readout"><span>Lower failing bracket</span><strong>${fmt(value.lowerBoundNm)}<small>N·m</small></strong></div><div class="readout"><span>Entered search limit</span><strong>${fmt(value.limitNm)}<small>N·m</small></strong></div></div><p><strong>Initial landing arrest only.</strong> Later rebound, settling and chassis safety require a full-duration run.</p><p>${esc(value.reason||value.limitation||'This is a sampled first-arrest torque bracket, not full-duration safety. Rebound and later chassis strike still require a complete run; it is not a certified global minimum or peak rating.')}</p>${trials.length?'<div class="eqd-table-wrap"><table><thead><tr><th>Tested torque · N·m</th><th>Outcome</th><th>First arrest · s</th></tr></thead><tbody>'+trials.map(trial=>`<tr><td>${fmt(trial.torqueNm)}</td><td>${esc(trial.outcome||(trial.success?'Arrested before bottom-out':'Did not meet arrest criterion'))}</td><td>${fmt(trial.firstArrestTimeS)}</td></tr>`).join('')+'</tbody></table></div>':''}<details><summary>Captured search diagnostics</summary><pre>${esc(JSON.stringify(value,null,2))}</pre></details>`;
      output.querySelector('[data-export-case-assessment]').onclick=()=>S.saveArtifact('kinefold-landing-torque-assessment.json',{schema:'kinefold/landing-assessment-v1',engine:id,projectSnapshot:project,assessment:value});
      if(output.dataset.snapshot!==KinefoldDynamicAnalysis.snapshotKey(S.getSnapshot()))output.insertAdjacentHTML('afterbegin','<p class="notice">Earlier captured snapshot · settings changed during this search. Run again to assess the current case.</p>');
    } catch (error) { output.textContent = 'Assessment failed: ' + error.message; }
    finally { button.disabled = false; }
  }
  return {mount, update};
})();
