/** Native categorized dynamic results and exact-sample comparison presentation.
 * Load after dynamic-analysis.js; solvers.js supplies captured result state and
 * playback callbacks. Inputs: seconds/mm/deg/N/J rows; output: accessible native
 * Plotly plots/disclosures. All curves are sampled, with one-sided jump rates.
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
  const chartState = new WeakMap(), playback = new WeakMap();
  const plot = () => globalThis.KinefoldPlotly;
  // Preserve exact event-side samples; null separators break undefined rates.
  function traces(config, selected = new Set(config.series.map(s => s[0]))) {
    return config.series.map(([key, label, color]) => {
      const x = [], y = [], customdata = [];
      config.rows.forEach((row, index) => {
        if (config.breakJumps && row.eventSide === 'after' && config.rows[index - 1]?.eventSide === 'before') {
          x.push(row.t); y.push(null); customdata.push(null);
        }
        x.push(config.xKey ? (Number.isFinite(row[config.xKey]) ? row[config.xKey] : null) : row.t); y.push(Number.isFinite(row[key]) ? row[key] : null);
        customdata.push([index, row.eventSide || 'sample', row.t]);
      });
      return {type:'scatter', mode:'lines', name:label, x, y, customdata,
        visible:selected.has(key) ? true : 'legendonly', connectgaps:false,
        ...(config.fill?{fill:'tozeroy',opacity:.7}:{}),
        line:{color, width:2, dash:key.endsWith('P') ? 'dash' : 'solid'},
        hovertemplate:'%{x:.7g} '+(config.xKey?config.xLabel:'s')+' · %{customdata[1]}<br>' + label + ': %{y:.7g} ' + config.unit + '<br>t = %{customdata[2]:.7g} s<extra></extra>'};
    });
  }
  function chart(host, config, currentTime, context = {}) {
    plot().purge(host);
    const {series, unit, title} = config;
    if (!seriesChoices.has(config.key)) seriesChoices.set(config.key, new Set(series.map(s => s[0])));
    const selected = seriesChoices.get(config.key);
    host.innerHTML = `<h3>${esc(title)}</h3>${config.note?`<p class="dyn-integral-note">${esc(config.note)}</p>`:''}<div class="dyn-series">${series.map(([key, label, color]) => `<label style="color:${color}"><input type="checkbox" data-series="${key}" ${selected.has(key) ? 'checked' : ''}>${esc(label)}</label>`).join('')}</div><div class="dyn-chart-stage"><div style="width:100%;height:340px" role="img" aria-label="${esc(title)} versus ${esc(config.xLabel||'time')}" data-dynamic-chart="${config.key}" ${config.xKey?'data-parametric="true"':''}></div></div>`;
    const node = host.querySelector('[data-dynamic-chart]');
    node.dataset.cursorTime = String(currentTime);
    function seek(point) {
      const rows = context.rows || config.rows;
      const time = point?.customdata?.[2] ?? point?.x;
      if (!Number.isFinite(time) || !context.onScrub) return;
      const side = point?.customdata?.[1]; let best = 0;
      rows.forEach((row, i) => {
        const distance = Math.abs(row.t - time), previous = Math.abs(rows[best].t - time);
        if (distance < previous || (distance === previous && (row.eventSide || 'sample') === side)) best = i;
      });
      context.onScrub(best);
    }
    function draw() {
      const data = traces(config, selected).map(trace => ({...trace, line:{...trace.line, color:plot().color(trace.line.color)}}));
      const events = (config.events || []).filter(e => Number.isFinite(e.t)&&(!config.rows.length||e.t>=config.rows[0].t-1e-12&&e.t<=config.rows.at(-1).t+1e-12));
      const layout = {height:340, margin:{l:75,r:20,t:35,b:75},
        xaxis:{title:{text:config.xLabel||'Time · s'}, zeroline:false}, yaxis:{title:{text:unit}, rangemode:'tozero'},
        uirevision:config.key, legend:{orientation:'h',y:-.24},
        shapes:config.xKey?[]:events.map(e => ({type:'line',xref:'x',yref:'paper',x0:e.t,x1:e.t,y0:0,y1:1,line:{color:plot().color('var(--amber)'),width:1,dash:'dot'}})),
        annotations:config.xKey?[]:events.slice(0,8).map((e,i) => ({xref:'x',yref:'paper',x:e.t,y:1-(i%3)*.065,text:e.type,showarrow:false,font:{size:10},xanchor:'left'}))};
      if (!data.some(t => t.visible === true && t.y.some(Number.isFinite))) layout.annotations.push({xref:'paper',yref:'paper',x:.5,y:.5,text:selected.size?'No samples available':'Select a series to inspect',showarrow:false});
      return plot().react(node, data, layout, {key:config.key,filename:config.key,onScrub:seek}).then(rendered => {
        if(rendered===false||!node.isConnected)return;
        if(!config.xKey)plot().cursor(node, Number(node.dataset.cursorTime));
        if (node.removeAllListeners) {
          node.removeAllListeners('plotly_legendclick'); node.removeAllListeners('plotly_legenddoubleclick');
          node.on('plotly_legendclick', event => {
            const key = series[event.curveNumber]?.[0]; if (!key) return false;
            selected.has(key) ? selected.delete(key) : selected.add(key);
            host.querySelectorAll('[data-series]').forEach(input => input.checked = selected.has(input.dataset.series));
            draw(); return false;
          });
          node.on('plotly_legenddoubleclick', () => false);
        }
      }).catch(error=>{if(node.isConnected){host.dataset.plotError=error.message;let note=host.querySelector('.plotly-failure');if(!note){note=document.createElement('p');note.className='plotly-failure';note.setAttribute('role','status');host.append(note);}note.textContent='Chart rendering failed: '+error.message;}});
    }
    chartState.set(node, draw);
    for (const input of host.querySelectorAll('[data-series]')) input.onchange = () => {
      input.checked ? selected.add(input.dataset.series) : selected.delete(input.dataset.series); draw();
    };
    draw();
  }
  function comparison(host, value, currentTime, onExport) {
    const fields=value.fields||A.comparisonFields;
    const priorField = host.querySelector('select')?.value || fields[0][0];
    plot().purge(host);
    if (!value.valid) {
      host.innerHTML = `<p class="notice">${esc(value.reason)}</p><p>Use Run both & compare to capture identical mechanism geometry, masses, spring and complete input/numerical profile once.</p>`;
      return;
    }
    host.innerHTML = `${value.outcomeA&&value.outcomeP&&value.outcomeA!==value.outcomeP?`<p class="notice error"><strong>Case outcomes differ.</strong> Analytical: ${esc(value.outcomeA)} · Pymunk: ${esc(value.outcomeP)}. Refine dt and inspect contact/stop events; equal run duration is not agreement.</p>`:''}<div class="dyn-comparison-summary"><strong>${value.matched} exact time / event-side pairs</strong><span>Overlap ${fmt(value.start)}–${fmt(value.end)} s · analytical ${value.analyticalSamples} / Pymunk ${value.pymunkSamples} samples</span><span>${value.complete ? 'All samples matched' : 'Partial common coverage only'} · stops: ${esc(value.terminationA)} / ${esc(value.terminationP)}</span></div><p>No interpolation across input jumps and no extrapolation beyond either run. Errors are Pymunk minus analytical; maxima are sampled.</p><div class="dyn-compare-actions"><label>Compare variable<select aria-label="Comparison variable">${fields.map(([key, label, unit]) => `<option value="${key}" ${key === priorField ? 'selected' : ''}>${label} · ${unit}</option>`).join('')}</select></label><button data-export-comparison>Export comparison JSON</button></div><div class="dyn-comparison-plots"><article class="dyn-chart-card" data-overlay></article><article class="dyn-chart-card" data-error></article></div><div class="eqd-table-wrap"><table><thead><tr><th>Quantity</th><th>Sampled max |error|</th><th>RMS error</th><th>Units</th></tr></thead><tbody>${value.stats.map(s => `<tr><td>${esc(s.label)}</td><td>${fmt(s.maxAbs, 6)}</td><td>${fmt(s.rms, 6)}</td><td>${s.unit}</td></tr>`).join('')}</tbody></table></div>`;
    const draw = () => {
      const latestTime = Number(host.querySelector('[data-dynamic-chart]')?.dataset.cursorTime ?? currentTime);
      const [field, label, unit] = fields.find(([key]) => key === host.querySelector('select').value);
      chart(host.querySelector('[data-overlay]'), {key: 'comparison-' + field, rows: value.rows, title: label + ' · engine overlay', unit,
        events:playback.get(host)?.events, breakJumps: field === 'inputReactionN', series: [[field + 'A', 'Analytical · solid', 'var(--sage)'], [field + 'P', 'Pymunk · dashed', 'var(--blue)']]}, latestTime, playback.get(host) || {});
      chart(host.querySelector('[data-error]'), {key: 'error-' + field, rows: value.rows, title: label + ' · Pymunk − analytical', unit,
        events:playback.get(host)?.events, breakJumps: field === 'inputReactionN', series: [[field + 'Error', 'Signed error', 'var(--red)']]}, latestTime, playback.get(host) || {});
    };
    host.querySelector('select').onchange = draw;
    host.querySelector('[data-export-comparison]').onclick = onExport;
    draw();
  }
  function terrainSummary(result){
    const c=result.terrainConfig;if(!c||(result.caseConfig?.kind||'terrain-stability')!=='terrain-stability')return '';
    const stats=result.terrain?.statistics||{},v2=c.schema==='kinefold/terrain-v2';
    return `<section class="case-summary"><h3>Captured terrain · ${esc(c.profileId)}</h3><p>${esc(c.severity)} / ${esc(c.representation)} · nominal repeat ${fmt(c.periodMm)} mm · ${v2?'seed '+c.seed+' / '+fmt(c.variationPercent)+'% variation / grade '+fmt(c.gradePercent)+'% ('+fmt(Math.atan(c.gradePercent/100)*180/Math.PI)+'°)':'legacy regular v1 / flat grade'}</p><p>Nominal source RMS ${fmt(c.rmsMm)} mm · generated-mesh detrended roughness RMS ${fmt(stats.detrendedRmsMm??stats.rmsMm)} mm (${stats.cellCount||1} complete cells; supporting tails excluded) · realized roughness peak ${fmt(stats.peakMm)} mm. The grade baseline is removed before RMS. Both engines capture the same seed, cells and incline.</p><p>Chassis horizontal position stays fixed. Horizontal rail reactions change the ordinary free-vehicle incline load balance; terrain work is the actual ground-velocity dot contact impulse. No additional gravity-sized slope force is inserted.</p><details><summary>Captured terrain, realized cell statistics & initial conditions</summary><pre>${esc(JSON.stringify({terrainConfig:c,realized:stats,initialConditions:result.terrain?.initialConditions},null,2))}</pre></details></section>`;
  }
  function caseSummary(result) {
    const metrics=result.caseMetrics||{}, estimate=result.energyEstimate||metrics.energyEstimate||{}, observation=result.targetObservations||{};
    const kind=result.caseConfig?.kind||'terrain-stability', energy=result.caseConfig?.energyMethod!==false, last=result.rows.at(-1);
    let items=kind==='jump'?[['Takeoff',observation.takeoff?.t??metrics.takeoffTimeS,'s'],['First flight rise above takeoff',observation.flightRiseMm,'mm'],['Final motor work',last.motorWorkJ,'J'],['Travel-stop loss',last.stopDissipationJ,'J']]:kind==='landing'?[['Landing impact',metrics.impactTimeS,'s'],['Impact chassis speed',metrics.impactChassisVelocityMmS,'mm/s'],['First chassis arrest',metrics.firstArrestTimeS,'s'],['Minimum clearance through first arrest',observation.minimumClearanceThroughArrestMm,'mm'],['Maximum compression angle',metrics.maxCompressionDeg,'°']]:[];
    items.push(['Minimum underside clearance',metrics.minimumUndersideClearanceMm,'mm']);
    if(energy&&kind==='landing')items.push(['Energy-average brake torque',estimate.averageTorqueNm,'N·m']);
    const residual=Math.max(...result.rows.map(r=>Math.abs(r.energyBalanceResidualJ||0)));
    return `<section class="case-summary"><h3>Case outcome · ${esc(metrics.outcome||result.diagnostics?.termination||'completed')}</h3><p>${esc(kind)} · ${metrics.landingSuccess===true?'Landing arrested before bottom-out':metrics.landingSuccess===false?'Landing did not meet the arrest criterion':'Actual trajectory observation'} · chassis strike ${result.caseConfig?.undersideOffsetMm==null?'unassessed (no underside offset)':'assessed at the entered underside offset'}</p><div class="solver-readouts">${items.map(([label,value,unit])=>`<div class="readout"><span>${label}</span><strong>${fmt(value)}<small>${unit}</small></strong></div>`).join('')}</div>${energy?`<p>Sampled max energy-ledger residual: <strong>${fmt(residual)} J</strong>. Refine dt; this unresolved numerical quantity is not physical loss or a claim of tight conservation. Motor ∫τdθ, chassis ½m₁v², wheel energy, spring/gravity and stop/contact losses remain separate.</p>`:''}<details><summary>Case events (${result.events.length})</summary><div class="eqd-table-wrap"><table><thead><tr><th>Event</th><th>Time · s</th></tr></thead><tbody>${result.events.slice(0,30).map(event=>'<tr><td>'+esc(event.type)+'</td><td>'+fmt(event.t)+'</td></tr>').join('')}</tbody></table></div></details><details><summary>Captured case and ${energy?'energy estimate / ':''}diagnostics</summary><pre>${esc(JSON.stringify({case:result.caseConfig,metrics,...(energy?{energyEstimate:estimate}:{})},null,2))}</pre></details></section>`;
  }
  function integralSummary(result) {
    const impact=result.events.find(e=>e.type==='first-contact'), arrest=result.events.find(e=>e.type==='chassis-arrest');
    const stop=result.events.find(e=>e.type==='compression-stop'), failed=stop&&(!arrest||stop.t<=arrest.t);
    const end=arrest?.sinceContact, start=impact?.state;
    const terms=[['Spring stored · recoverable','springStoredJ'],['Motor net work removed','motorRemovedJ'],['Gravity released','gravityReleasedJ'],['Cogging stored · recoverable','coggingStoredJ'],['Kinetic change · all moving bodies','kineticChangeJ'],['Chassis ∫m₁v dv','chassisKineticChangeJ'],['Joint damping removed','dampingRemovedJ'],['Motor friction loss','motorLossJ'],['Terrain work supplied','terrainSuppliedJ'],['Additional load work supplied','externalSuppliedJ'],['Contact impulse accounting','contactLossJ'],['Stop impulse accounting','stopLossJ'],['Coupled native constraint · signed numerical','coupledNumericalLossJ'],['Position projection · signed numerical','projectionEnergyJ'],['Unresolved numerical residual','ledgerResidualJ']];
    return `<section class="dyn-work-summary"><h3>Work, storage & contact events</h3><p><strong>${esc(result.workIntegrals?.springLaw||'Rerun this captured case for work-integral data')}.</strong> Spring storage is recoverable: ΔUₛ = ∫F dℓ = −∫τₛ dθ₂. Motor removal is −∫τ_motor dθ. Reversal can release stored energy; no absolute-angle accumulation is used.</p><p><strong>The first wheel impulse does not instantly stop the chassis.</strong> The wheel normal speed changes while the leg can compress. Analytical first-contact is its first unilateral impulse: a small positive gap can trigger speculative gap/step contact before geometric touching. Chassis arrest occurs when its vertical speed crosses zero. ${failed?'<strong class="notice error">Compression stop occurs before or at arrest: this is bottom-out, even if a later velocity becomes zero.</strong>':''}</p><div class="eqd-table-wrap"><table><thead><tr><th>Actual integration-step event</th><th>Time · s</th><th>Chassis before · mm/s</th><th>Chassis after · mm/s</th><th>Wheel after · mm/s</th><th>Chassis K after · J</th><th>Contact gap · mm</th></tr></thead><tbody>${[impact,arrest].filter(Boolean).map(e=>`<tr><td>${esc(e.type)}</td><td>${fmt(e.t,7)}</td><td>${fmt(e.preImpulseChassisVelocityMmS??e.beforeStepChassisVelocityMmS)}</td><td>${fmt(e.postImpulseChassisVelocityMmS??e.state?.chassisVelocityMmS)}</td><td>${fmt(e.postImpulseWheelVelocityZMmS??e.state?.wheelVelocityZMmS)}</td><td>${fmt(e.state?.chassisKineticJ)}</td><td>${fmt(e.contactGapMm)}</td></tr>`).join('')}</tbody></table></div><p>At first contact: total moving kinetic energy <strong>${fmt(start?.kineticJ)} J</strong>, including chassis <strong>${fmt(start?.chassisKineticJ)} J</strong>. Table below spans the exact post-contact state to first chassis arrest${failed?' (after bottom-out; not a successful landing)':''}. Unobserved arrest remains unavailable.</p><div class="eqd-table-wrap"><table><thead><tr><th>Signed first-contact → first-arrest account</th><th>J</th></tr></thead><tbody>${terms.map(([label,key])=>`<tr><td>${label}</td><td>${fmt(end?.[key],7)}</td></tr>`).join('')}</tbody></table></div><p>ΔK = gravity released − spring stored − cogging stored − motor removed − damping removed − motor friction + terrain / additional-load work − impulse accounting + projection + residual. Contact/stop accounts include numerical bias; the native rotor reports a combined signed constraint account instead of inventing separate losses. These are experimental engine results, not impact or regeneration ratings.</p></section>`;
  }
  function mount(host, state, options) {
    const {id, result, snapshot} = state, rows = A.enrich(result), first = rows[0];
    const now = rows[state.index].t, contact=result.scope?.mode==='terrain-contact', catalog=[...(contact?[...A.contactManifest,...A.integralManifest]:A.manifest),...A.motorManifest];
    const displayGroups=contact?[['motion','Motion & events','Actual heave, height, clearance and case events'],['integrals','Work integrals & energy portions','Signed spring storage, motor removal, first contact and chassis arrest'],['forces','Contact & wheel','Wheel spin, interval forces, slip and separation'],['kinematics','Motor & travel','Backdriven indices, actuation and working travel'],['energy','Energy & checks','Chassis kinetic energy, motor work and stop losses']]:[...groups];displayGroups.push(['motor','Motor, gearing & losses','Motor-side and joint-side torque, reflected inertia, conservative cogging and dissipated energy']);
    const max = key => Math.max(...rows.map(row => Math.abs(row[key])));
    const range = key => Math.max(...rows.map(row => row[key])) - Math.min(...rows.map(row => row[key]));
    plot().purge(host);
    host.innerHTML = `<div class="solver-result-identity"><strong>Results: ${esc(snapshot.name)} · model revision ${snapshot.modelRevision}</strong><span data-snapshot-state>Current captured snapshot</span></div><div class="solver-readouts">${[['Chassis range', range('chassisZMm'), 'mm'], ['Peak chassis speed', max('chassisVelocityMmS'), 'mm/s'], ['Peak spring tension', max('Fs'), 'N'], [contact?'Sampled max interval normal':'Input events', contact?max('contactNormalForceN'):result.events.length, contact?'N':'events']].map(([label, value, unit]) => `<div class="readout"><span>${label}</span><strong>${fmt(value)}<small>${unit}</small></strong></div>`).join('')}</div><nav class="eq-jumps" aria-label="Dynamic result categories">${[...displayGroups.map(([key, label]) => [key, label]), ['comparison', 'Compare engines']].map(([key, label]) => `<button data-result-jump="${key}">${label}</button>`).join('')}</nav><div class="solver-player"><svg id="${id}-preview" role="img" aria-label="${contact?'Actual wheel and terrain contact':'World-frame quarter mechanism and moving prescribed spatial floor'}"></svg><div class="solver-playerbar"><button id="${id}-play" aria-label="Play simulation result" aria-pressed="false">▶</button><input id="${id}-scrub" aria-label="Simulation time" type="range" min="0" max="${rows.length - 1}" value="${state.index}" step="1"><output id="${id}-time"></output></div><p class="dyn-floor-note">${contact?(result.caseConfig?.kind&&result.caseConfig.kind!=='terrain-stability'?'Stationary flat collision floor.':'Actual collision mesh moves in the world toward −x.')+(result.diagnostics?.finiteLinkDynamics?' Chassis, rod and wheel transforms are finite-link engine outputs; belts are ideal constraints.':' Chassis/wheel transforms, wheel spin and contacts are engine outputs; links and belts are the exact ideal massless transmission.')+' The wheel can slip, separate or bridge gaps.':'Prescribed spatial floor moves toward −x (screen right), anchored under the instantaneous wheel C_x. Solid = applied input; dashed = requested square. This is a wheel-height driver, not horizontal rolling or collision terrain.'}</p></div>${contact?terrainSummary(result)+caseSummary(result):''}${displayGroups.map(([key, label, sub], i) => `<details class="eq-category dyn-category" data-result-group="${key}" ${(openGroups.get(id + key) ?? (i === 0 || key === 'integrals')) ? 'open' : ''}><summary><span>0${i + 1}</span><div><strong>${label}</strong><small>${sub}</small></div><b>+</b></summary><div class="eq-category-body dyn-result-body"></div></details>`).join('')}<details class="eq-category dyn-category" data-result-group="comparison" ${openGroups.get(id + 'comparison') ? 'open' : ''}><summary><span>${String(displayGroups.length+1).padStart(2,'0')}</span><div><strong>Analytical ↔ Pymunk comparison</strong><small>One captured design/profile · exact time and event-side pairs</small></div><b>+</b></summary><div class="eq-category-body" data-comparison-host></div></details><details class="solver-details"><summary>Events, captured inputs & numerical diagnostics</summary><p>${contact?(result.diagnostics?.finiteLinkDynamics?'Actual finite-link contact: chassis + two uniform rods + free wheel; chassis x/pitch constrained, ideal belt coupling. ':'Actual unilateral contact mode: two dynamic bodies, chassis fixed in x/pitch, free wheel spin and an exact straight-path massless linkage. ')+'Contact forces are interval impulse means, not continuous peak bounds. Motor, terrain, contact and stop impulse work/losses are reported with an unresolved numerical ledger residual. Pymunk impulse-loss accounting includes constraint bias effects; analytical position-projection energy is separate. Refine dt before interpreting energy/impact values. The analytical contact integrator is independent of Pymunk; compare the exact same captured mechanism, material and case.':'Quarter model: actual chassis heave; ideal condensed linkage; no collision/tire/guide support model. Angular rates and input reaction at exact square edges are undefined; plotted edge values are finite one-sided states. Force extrema are sampled. The balance torque is a zero-rate, zero-input-acceleration reference, not full inverse dynamics. Dynamic pin and belt reactions are not solved by this reduced model. Analytical chassis constraint errors are identically zero by construction; Pymunk errors are sampled actual transforms.'}</p><pre>${esc(JSON.stringify({designHash: result.designHash, diagnostics: result.diagnostics, events: result.events}, null, 2))}</pre></details>`;
    playback.set(host.querySelector('[data-comparison-host]'), {rows,events:result.events,onScrub:options.onScrub});
    for (const details of host.querySelectorAll('[data-result-group]')) {
      function render() {
        const key = details.dataset.resultGroup; openGroups.set(id + key, details.open);
        if (!details.open) return;
        if (details.dataset.rendered) { plot().resizeAll(details); return; }
        details.dataset.rendered = 'true';
        if (key === 'comparison') comparison(details.querySelector('[data-comparison-host]'), options.comparison(), options.currentTime(), options.onExportComparison);
        else {
          const body = details.querySelector('.dyn-result-body');
          body.innerHTML = (key==='integrals'?integralSummary(result)+`<label class="dyn-integral-range">Plot interval<select data-integral-range><option value="arrest" ${result.caseConfig?.kind==='landing'?'selected':''}>First contact → first arrest / compression stop</option><option value="all" ${result.caseConfig?.kind!=='landing'?'selected':''}>Full trajectory · signed reversals retained</option></select></label>`:'')+'<div class="dyn-chart-grid">' + catalog.filter(item => item.group === key).map(item => `<article class="dyn-chart-card" data-chart="${item.id}"></article>`).join('') + '</div>';
          const drawGroup=()=>{
            const plotRows=key==='integrals'?A.integralRows(result,rows,body.querySelector('[data-integral-range]').value==='arrest'):rows;
            for (const item of catalog.filter(item => item.group === key)) chart(body.querySelector(`[data-chart="${item.id}"]`), {...item, key: item.id, rows:item.id==='integral-event-speed'?A.velocityRows(result,plotRows):plotRows, events:result.events,
              breakJumps: ['rates', 'angular-acceleration', 'reaction'].includes(item.id)}, options.currentTime(), {rows,onScrub:options.onScrub});
          };
          drawGroup();if(key==='integrals')body.querySelector('[data-integral-range]').onchange=drawGroup;
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
    for (const node of host.querySelectorAll('[data-dynamic-chart]')) {
      node.dataset.cursorTime = String(time);
      if(!node.dataset.parametric)plot().cursor(node, time);
    }
  }
  if (typeof window !== 'undefined') window.addEventListener('kinefold-theme-change', () => {
    document.querySelectorAll('[data-dynamic-chart]').forEach(node => chartState.get(node)?.());
  });
  return {mount, updateComparison, cursor, traces, integralSummary};
})();
