/** Native categorized dynamic results and exact-sample comparison presentation.
 * Load after dynamic-analysis.js; solvers.js supplies captured result state and
 * playback callbacks. Inputs: seconds/mm/deg/N/J rows; output: accessible native
 * SVG plots/disclosures. All curves are sampled, with one-sided jump rates.
 */
globalThis.KinefoldDynamicResults = (() => {
  'use strict';
  const A = KinefoldDynamicAnalysis;
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = (value, digits = 4) => !Number.isFinite(value) ? '—' : value !== 0 && (Math.abs(value) < .001 || Math.abs(value) >= 1e6) ? value.toExponential(Math.min(4, digits - 1)) : value.toLocaleString('en-CA', {maximumSignificantDigits: digits});
  const groups = [
    ['motion', 'Motion & wheel input', 'Prescribed input, world heights and chassis response'],
    ['kinematics', 'Angles & kinematics', 'Joint angles, horizontal travel and one-sided rates'],
    ['forces', 'Forces & actuation', 'Cable tension, input reaction and torque accounting'],
    ['energy', 'Energy & numerical checks', 'Energy, source work, balance residuals and sampled constraints'],
  ];
  const openGroups = new Map(), seriesChoices = new Map();
  function chart(host, config, currentTime) {
    const {rows, series, unit, title} = config;
    if (!seriesChoices.has(config.key)) seriesChoices.set(config.key, new Set(series.map(s => s[0])));
    const selected = seriesChoices.get(config.key);
    host.innerHTML = `<h3>${esc(title)}</h3><div class="dyn-series">${series.map(([key, label, color]) => `<label style="color:${color}"><input type="checkbox" data-series="${key}" ${selected.has(key) ? 'checked' : ''}>${esc(label)}</label>`).join('')}</div><div class="dyn-chart-stage"><svg viewBox="0 0 720 340" role="img" aria-label="${esc(title)} versus time" data-dynamic-chart="${config.key}"></svg><output hidden class="eq-tooltip"></output></div>`;
    function draw() {
      const svg = host.querySelector('svg'), active = series.filter(([key]) => selected.has(key));
      const values = rows.flatMap(r => active.map(([key]) => r[key])).filter(Number.isFinite);
      const x0 = rows[0].t, x1 = rows.at(-1).t, lo = values.reduce((a,v)=>Math.min(a,v),0), hi = values.reduce((a,v)=>Math.max(a,v),0);
      const pad = Math.max((hi - lo) * .08, Math.max(Math.abs(lo), Math.abs(hi)) * 1e-7, 1e-8);
      const X = t => 90 + (t - x0) / Math.max(1e-12, x1 - x0) * 600;
      const cursorTime = Number(svg.dataset.cursorTime ?? currentTime);
      const Y = v => 280 - (v - lo + pad) / (hi - lo + 2 * pad) * 240;
      let html = '<rect width="720" height="340" fill="var(--paper)"/>';
      for (let i = 0; i <= 4; i++) {
        const v = lo - pad + (hi - lo + 2 * pad) * i / 4;
        html += `<path d="M90 ${Y(v)}H690" stroke="var(--line)"/><text x="80" y="${Y(v) + 5}" text-anchor="end" font-size="14" fill="var(--muted)">${fmt(v)}</text>`;
      }
      for (let i = 0; i <= 6; i++) {
        const t = x0 + (x1 - x0) * i / 6;
        html += `<path d="M${X(t)} 40V280" stroke="var(--line)" opacity=".5"/><text x="${X(t)}" y="305" text-anchor="middle" font-size="14" fill="var(--muted)">${fmt(t)}</text>`;
      }
      for (const [key, , color] of active) {
        let path = '', previous = null;
        for (const row of rows) {
          const gap = !Number.isFinite(row[key]) || (config.breakJumps && row.eventSide === 'after' && previous?.eventSide === 'before');
          if (gap) path += ' ';
          if (Number.isFinite(row[key])) path += (!previous || gap || !Number.isFinite(previous[key]) ? 'M' : 'L') + X(row.t) + ',' + Y(row[key]);
          previous = row;
        }
        html += `<path data-series="${key}" d="${path}" fill="none" stroke="${color}" stroke-width="2" ${key.endsWith('P') ? 'stroke-dasharray="6 3"' : ''}/>`;
      }
      for(const [i,event] of (config.events||[]).filter(e=>['first-contact','takeoff','apex','chassis-arrest','extension-stop','compression-stop','underside-contact'].includes(e.type)).slice(0,8).entries()) html += `<path d="M${X(event.t)} 40V280" stroke="var(--amber)" opacity=".5" stroke-dasharray="3 4"/><text x="${X(event.t)+3}" y="${48+(i%3)*14}" font-size="11" fill="var(--muted)">${esc(event.type)}</text>`;
      html += `<path data-time-cursor d="M${X(cursorTime)} 40V280" stroke="var(--ink)" stroke-width="1.4"/><text x="90" y="23" font-size="14" fill="var(--muted)">${unit}</text><text x="390" y="333" text-anchor="middle" font-size="14" fill="var(--muted)">Time · s</text>`;
      if (!values.length) html += '<text x="390" y="160" text-anchor="middle" fill="var(--muted)">' + (active.length ? 'No samples available' : 'Select a series to inspect') + '</text>';
      svg.innerHTML = html;
      svg.dataset.timeMin = x0; svg.dataset.timeMax = x1;
      svg.onpointermove = event => {
        const matrix = svg.getScreenCTM(); if (!matrix) return;
        const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
        const time = x0 + Math.max(0, Math.min(1, (point.x - 90) / 600)) * (x1 - x0);
        const nearest = rows.reduce((a, b) => Math.abs(b.t - time) < Math.abs(a.t - time) ? b : a);
        const sameTime = rows.filter(r => Math.abs(r.t - nearest.t) < 1e-9);
        const output = host.querySelector('output');
        output.textContent = sameTime.map(row => `t ${fmt(row.t, 6)} s ${row.eventSide || ''}\n` + active.map(([key, label]) => `${label}: ${fmt(row[key], 7)} ${unit}`).join('\n')).join('\n\n');
        output.hidden = false;
      };
      svg.onpointerleave = () => { host.querySelector('output').hidden = true; };
    }
    for (const input of host.querySelectorAll('[data-series]')) input.onchange = () => {
      input.checked ? selected.add(input.dataset.series) : selected.delete(input.dataset.series); draw();
    };
    draw();
  }
  function comparison(host, value, currentTime, onExport) {
    const fields=value.fields||A.comparisonFields;
    const priorField = host.querySelector('select')?.value || fields[0][0];
    if (!value.valid) {
      host.innerHTML = `<p class="notice">${esc(value.reason)}</p><p>Use Run both & compare to capture identical mechanism geometry, masses, spring and complete input/numerical profile once.</p>`;
      return;
    }
    host.innerHTML = `${value.outcomeA&&value.outcomeP&&value.outcomeA!==value.outcomeP?`<p class="notice error"><strong>Case outcomes differ.</strong> Analytical: ${esc(value.outcomeA)} · Pymunk: ${esc(value.outcomeP)}. Refine dt and inspect contact/stop events; equal run duration is not agreement.</p>`:''}<div class="dyn-comparison-summary"><strong>${value.matched} exact time / event-side pairs</strong><span>Overlap ${fmt(value.start)}–${fmt(value.end)} s · analytical ${value.analyticalSamples} / Pymunk ${value.pymunkSamples} samples</span><span>${value.complete ? 'All samples matched' : 'Partial common coverage only'} · stops: ${esc(value.terminationA)} / ${esc(value.terminationP)}</span></div><p>No interpolation across input jumps and no extrapolation beyond either run. Errors are Pymunk minus analytical; maxima are sampled.</p><div class="dyn-compare-actions"><label>Compare variable<select aria-label="Comparison variable">${fields.map(([key, label, unit]) => `<option value="${key}" ${key === priorField ? 'selected' : ''}>${label} · ${unit}</option>`).join('')}</select></label><button data-export-comparison>Export comparison JSON</button></div><div class="dyn-comparison-plots"><article class="dyn-chart-card" data-overlay></article><article class="dyn-chart-card" data-error></article></div><div class="eqd-table-wrap"><table><thead><tr><th>Quantity</th><th>Sampled max |error|</th><th>RMS error</th><th>Units</th></tr></thead><tbody>${value.stats.map(s => `<tr><td>${esc(s.label)}</td><td>${fmt(s.maxAbs, 6)}</td><td>${fmt(s.rms, 6)}</td><td>${s.unit}</td></tr>`).join('')}</tbody></table></div>`;
    const draw = () => {
      const latestTime = Number(host.querySelector('svg[data-dynamic-chart]')?.dataset.cursorTime ?? currentTime);
      const [field, label, unit] = fields.find(([key]) => key === host.querySelector('select').value);
      chart(host.querySelector('[data-overlay]'), {key: 'comparison-' + field, rows: value.rows, title: label + ' · engine overlay', unit,
        breakJumps: field === 'inputReactionN', series: [[field + 'A', 'Analytical · solid', 'var(--sage)'], [field + 'P', 'Pymunk · dashed', 'var(--blue)']]}, latestTime);
      chart(host.querySelector('[data-error]'), {key: 'error-' + field, rows: value.rows, title: label + ' · Pymunk − analytical', unit,
        breakJumps: field === 'inputReactionN', series: [[field + 'Error', 'Signed error', 'var(--red)']]}, latestTime);
    };
    host.querySelector('select').onchange = draw;
    host.querySelector('[data-export-comparison]').onclick = onExport;
    draw();
  }
  function caseSummary(result) {
    const metrics=result.caseMetrics||{}, estimate=result.energyEstimate||metrics.energyEstimate||{};
    const kind=result.caseConfig?.kind||'terrain-stability', energy=result.caseConfig?.energyMethod!==false, last=result.rows.at(-1);
    let items=kind==='jump'?[['Takeoff',metrics.takeoffTimeS,'s'],['Apex rise from initial',metrics.apexChassisZMm-result.rows[0].chassisZMm,'mm'],['Final motor work',last.motorWorkJ,'J'],['Travel-stop loss',last.stopDissipationJ,'J']]:kind==='landing'?[['Landing impact',metrics.impactTimeS,'s'],['Impact chassis speed',metrics.impactChassisVelocityMmS,'mm/s'],['First chassis arrest',metrics.firstArrestTimeS,'s'],['Maximum compression angle',metrics.maxCompressionDeg,'°']]:[];
    items.push(['Minimum underside clearance',metrics.minimumUndersideClearanceMm,'mm']);
    if(energy&&kind==='landing')items.push(['Energy-average brake torque',estimate.averageTorqueNm,'N·m']);
    const residual=Math.max(...result.rows.map(r=>Math.abs(r.energyBalanceResidualJ||0)));
    return `<section class="case-summary"><h3>Case outcome · ${esc(metrics.outcome||result.diagnostics?.termination||'completed')}</h3><p>${esc(kind)} · ${metrics.landingSuccess===true?'Landing arrested before bottom-out':metrics.landingSuccess===false?'Landing did not meet the arrest criterion':'Actual trajectory observation'} · chassis strike ${result.caseConfig?.undersideOffsetMm==null?'unassessed (no underside offset)':'assessed at the entered underside offset'}</p><div class="solver-readouts">${items.map(([label,value,unit])=>`<div class="readout"><span>${label}</span><strong>${fmt(value)}<small>${unit}</small></strong></div>`).join('')}</div>${energy?`<p>Sampled max energy-ledger residual: <strong>${fmt(residual)} J</strong>. Refine dt; this unresolved numerical quantity is not physical loss or a claim of tight conservation. Motor ∫τdθ, chassis ½m₁v², wheel energy, spring/gravity and stop/contact losses remain separate.</p>`:''}<details><summary>Case events (${result.events.length})</summary><div class="eqd-table-wrap"><table><thead><tr><th>Event</th><th>Time · s</th></tr></thead><tbody>${result.events.slice(0,30).map(event=>'<tr><td>'+esc(event.type)+'</td><td>'+fmt(event.t)+'</td></tr>').join('')}</tbody></table></div></details><details><summary>Captured case and ${energy?'energy estimate / ':''}diagnostics</summary><pre>${esc(JSON.stringify({case:result.caseConfig,metrics,...(energy?{energyEstimate:estimate}:{})},null,2))}</pre></details></section>`;
  }
  function mount(host, state, options) {
    const {id, result, snapshot} = state, rows = A.enrich(result), first = rows[0];
    const now = rows[state.index].t, contact=result.scope?.mode==='terrain-contact', catalog=contact?A.contactManifest:A.manifest;
    const displayGroups=contact?[['motion','Motion & events','Actual heave, height, clearance and case events'],['forces','Contact & wheel','Wheel spin, interval forces, slip and separation'],['kinematics','Motor & travel','Backdriven indices, actuation and working travel'],['energy','Energy & checks','Chassis kinetic energy, motor work and stop losses']]:groups;
    const max = key => Math.max(...rows.map(row => Math.abs(row[key])));
    const range = key => Math.max(...rows.map(row => row[key])) - Math.min(...rows.map(row => row[key]));
    host.innerHTML = `<div class="solver-result-identity"><strong>Results: ${esc(snapshot.name)} · model revision ${snapshot.modelRevision}</strong><span data-snapshot-state>Current captured snapshot</span></div><div class="solver-readouts">${[['Chassis range', range('chassisZMm'), 'mm'], ['Peak chassis speed', max('chassisVelocityMmS'), 'mm/s'], ['Peak spring tension', max('Fs'), 'N'], [contact?'Sampled max interval normal':'Input events', contact?max('contactNormalForceN'):result.events.length, contact?'N':'events']].map(([label, value, unit]) => `<div class="readout"><span>${label}</span><strong>${fmt(value)}<small>${unit}</small></strong></div>`).join('')}</div><nav class="eq-jumps" aria-label="Dynamic result categories">${[...displayGroups.map(([key, label]) => [key, label]), ['comparison', 'Compare engines']].map(([key, label]) => `<button data-result-jump="${key}">${label}</button>`).join('')}</nav><div class="solver-player"><svg id="${id}-preview" role="img" aria-label="${contact?'Actual wheel and terrain contact':'World-frame quarter mechanism and moving prescribed spatial floor'}"></svg><div class="solver-playerbar"><button id="${id}-play" aria-label="Play simulation result" aria-pressed="false">▶</button><input id="${id}-scrub" aria-label="Simulation time" type="range" min="0" max="${rows.length - 1}" value="${state.index}" step="1"><output id="${id}-time"></output></div><p class="dyn-floor-note">${contact?(result.caseConfig?.kind&&result.caseConfig.kind!=='terrain-stability'?'Stationary flat collision floor.':'Actual collision mesh moves in the world toward −x.')+' Chassis/wheel transforms, wheel spin and contacts are engine outputs; links and belts are the exact ideal massless transmission. The wheel can slip, separate or bridge gaps.':'Prescribed spatial floor moves toward −x (screen right), anchored under the instantaneous wheel C_x. Solid = applied input; dashed = requested square. This is a wheel-height driver, not horizontal rolling or collision terrain.'}</p></div>${contact?caseSummary(result):''}${displayGroups.map(([key, label, sub], i) => `<details class="eq-category dyn-category" data-result-group="${key}" ${openGroups.get(id + key) ?? i === 0 ? 'open' : ''}><summary><span>0${i + 1}</span><div><strong>${label}</strong><small>${sub}</small></div><b>+</b></summary><div class="eq-category-body dyn-result-body"></div></details>`).join('')}<details class="eq-category dyn-category" data-result-group="comparison" ${openGroups.get(id + 'comparison') ? 'open' : ''}><summary><span>05</span><div><strong>Analytical ↔ Pymunk comparison</strong><small>One captured design/profile · exact time and event-side pairs</small></div><b>+</b></summary><div class="eq-category-body" data-comparison-host></div></details><details class="solver-details"><summary>Events, captured inputs & numerical diagnostics</summary><p>${contact?'Actual unilateral contact mode: two dynamic bodies, chassis fixed in x/pitch, free wheel spin and an exact straight-path massless linkage. Contact forces are interval impulse means, not continuous peak bounds. Motor, terrain, contact and stop impulse work/losses are reported with an unresolved numerical ledger residual. Pymunk impulse-loss accounting includes constraint bias effects; analytical position-projection energy is separate. Refine dt before interpreting energy/impact values. The analytical contact integrator is independent of Pymunk; compare the exact same captured mechanism, material and case.':'Quarter model: actual chassis heave; ideal condensed linkage; no collision/tire/guide support model. Angular rates and input reaction at exact square edges are undefined; plotted edge values are finite one-sided states. Force extrema are sampled. The balance torque is a zero-rate, zero-input-acceleration reference, not full inverse dynamics. Dynamic pin and belt reactions are not solved by this reduced model. Analytical chassis constraint errors are identically zero by construction; Pymunk errors are sampled actual transforms.'}</p><pre>${esc(JSON.stringify({designHash: result.designHash, diagnostics: result.diagnostics, events: result.events}, null, 2))}</pre></details>`;
    for (const details of host.querySelectorAll('[data-result-group]')) {
      function render() {
        const key = details.dataset.resultGroup; openGroups.set(id + key, details.open);
        if (!details.open || details.dataset.rendered) return;
        details.dataset.rendered = 'true';
        if (key === 'comparison') comparison(details.querySelector('[data-comparison-host]'), options.comparison(), options.currentTime(), options.onExportComparison);
        else {
          const body = details.querySelector('.dyn-result-body');
          body.innerHTML = '<div class="dyn-chart-grid">' + catalog.filter(item => item.group === key).map(item => `<article class="dyn-chart-card" data-chart="${item.id}"></article>`).join('') + '</div>';
          for (const item of catalog.filter(item => item.group === key)) chart(body.querySelector(`[data-chart="${item.id}"]`), {...item, key: item.id, rows, events:result.events,
            breakJumps: ['rates', 'angular-acceleration', 'reaction'].includes(item.id)}, options.currentTime());
        }
      }
      details.ontoggle = render; render();
    }
    for (const button of host.querySelectorAll('[data-result-jump]')) button.onclick = () => {
      const details = host.querySelector(`[data-result-group="${button.dataset.resultJump}"]`);
      details.open = true; details.scrollIntoView({block: 'start', behavior: 'smooth'});
    };
    host.querySelector('#' + id + '-scrub').oninput = event => options.onScrub(Number(event.target.value));
    host.querySelector('#' + id + '-play').onclick = options.onPlay;
  }
  function updateComparison(host, value, now, onExport) {
    const details = host.querySelector('[data-result-group="comparison"]');
    if (!details) return;
    if (details.open) comparison(details.querySelector('[data-comparison-host]'), value, now, onExport);
    else delete details.dataset.rendered;
  }
  function cursor(host, time) {
    for (const svg of host.querySelectorAll('svg[data-dynamic-chart]')) {
      const min = Number(svg.dataset.timeMin), max = Number(svg.dataset.timeMax);
      const x = 90 + (time - min) / Math.max(1e-12, max - min) * 600;
      svg.dataset.cursorTime = String(time);
      const line = svg.querySelector('[data-time-cursor]');
      if (line) { line.setAttribute('d', `M${x} 40V280`); line.setAttribute('visibility', time < min || time > max ? 'hidden' : 'visible'); }
    }
  }
  return {mount, updateComparison, cursor};
})();
