/* Motor/SO gearbox source catalog and independent selector.
 * Browser: load this script, then KinefoldActuatorCatalog.mount(root,{onSelect,onCompare}).
 * Node: require('./motor-gearbox-catalog.js').init(JSON.parse(...)).
 * Inputs: offline catalog snapshot; torque N m, inertia kg m², speed rpm, ratio wm/wout.
 * Outputs: immutable numerical candidate combinations and optional selection callbacks.
 * Limits: ratings/assumed rotor geometry, not mounting verification, thermal or safe-speed certification.
 * No saved-profile writes, simulation runs, source-sheet writes or Downloads exports.
 */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.KinefoldActuatorCatalog = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const SCHEMA = 'kinefold/actuator-catalog-v1';
  const COMBINATION_SCHEMA = 'kinefold/actuator-combination-v1';
  let catalog = null, pending = null;
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const clone = o => JSON.parse(JSON.stringify(o));
  function freeze(o) { if (o && typeof o === 'object') { Object.values(o).forEach(freeze); Object.freeze(o); } return o; }
  function number(x, label, positive = false) {
    if (x === null) return null;
    if (typeof x !== 'number' || !Number.isFinite(x) || (positive ? x <= 0 : x < 0)) throw new Error('Invalid ' + label);
    return x;
  }
  const motorNumbers = ['kvRpmPerV', 'convertedKtNmPerA', 'torqueConstantNmPerA', 'continuousTorqueNm', 'peakTorqueNm', 'powerW', 'ratedRpm', 'noLoadRpm', 'maxRpm', 'ratedCurrentA', 'peakCurrentA', 'massKg', 'rotorInertiaKgM2', 'rotorInertiaLowKgM2', 'rotorInertiaHighKgM2'];
  const gearNumbers = ['frameMm', 'ratio', 'bodyLengthMm', 'continuousOutputNm', 'peakOutputNm', 'inputBoreMm', 'outputShaftDiameterMm', 'outputShaftLengthMm', 'stages', 'efficiency', 'ratedInputRpm', 'maxInputRpm', 'backlashArcmin', 'massKg', 'inputInertiaKgCm2', 'inputInertiaKgM2', 'outputInertiaKgM2'];
  function normalize(data) {
    if (!data || data.schema !== SCHEMA || typeof data.revision !== 'string' || !Array.isArray(data.motors) || !Array.isArray(data.gearboxes)) throw new Error('Invalid actuator catalog');
    const ids = new Set();
    for (const [kind, records, fields] of [['motor', data.motors, motorNumbers], ['gearbox', data.gearboxes, gearNumbers]]) {
      for (const r of records) {
        if (!r || typeof r.id !== 'string' || !r.id || typeof r.name !== 'string' || !r.name || ids.has(r.id)) throw new Error('Invalid or duplicate ' + kind + ' identity');
        ids.add(r.id);
        if (!r.provenance || typeof r.provenance.sheet !== 'string' || !Number.isInteger(r.provenance.row)) throw new Error('Missing ' + kind + ' source provenance');
        for (const f of fields) { if (!own(r, f)) throw new Error('Missing nullable ' + kind + '.' + f); number(r[f], kind + '.' + f, f === 'ratio'); }
        if (kind === 'motor') {
          if (r.rotorInertiaLowKgM2 !== null && r.rotorInertiaKgM2 !== null && r.rotorInertiaLowKgM2 > r.rotorInertiaKgM2) throw new Error('Inertia lower scenario exceeds nominal');
          if (r.rotorInertiaHighKgM2 !== null && r.rotorInertiaKgM2 !== null && r.rotorInertiaHighKgM2 < r.rotorInertiaKgM2) throw new Error('Inertia upper scenario below nominal');
        } else {
          if (r.ratio === null) throw new Error('A gearbox SKU needs its sourced ratio');
          if (r.efficiency !== null && (r.efficiency <= 0 || r.efficiency > 1)) throw new Error('Invalid efficiency');
          if (r.inputInertiaKgCm2 !== null && r.inputInertiaKgM2 !== r.inputInertiaKgCm2 * 1e-4) throw new Error('Invalid kg cm² conversion');
          if (r.inertiaReference !== 'input-equivalent') throw new Error('Unsupported gearbox inertia reference');
        }
      }
    }
    return freeze(clone(data));
  }
  function init(data) { catalog = normalize(data); return catalog; }
  function current() { if (!catalog) throw new Error('Load or init the actuator catalog first'); return catalog; }
  function load(url = 'motor-gearbox-catalog.json') {
    if (catalog) return Promise.resolve(catalog);
    if (!pending) pending = Promise.resolve().then(() => fetch(url, {cache: 'no-cache'})).then(r => { if (!r.ok) throw new Error('Catalog request failed: HTTP ' + r.status); return r.json(); }).then(init).catch(e => { pending = null; throw e; });
    return pending;
  }
  const canonical = s => String(s ?? '').normalize('NFKD').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  function matches(r, query) { const hay = canonical([r.name, r.brand, r.family, r.series, r.motorInterface, r.configuration, r.condition, r.notes, r.dataNotes].filter(Boolean).join(' ')); return canonical(query).split(' ').filter(Boolean).every(t => hay.includes(t)); }
  function searchMotors(query = '', filters = {}) {
    return current().motors.filter(r => matches(r, query) && (!filters.brand || r.brand === filters.brand) && (!filters.hasPeak || r.peakTorqueNm !== null) && (!filters.hasContinuous || r.continuousTorqueNm !== null));
  }
  function searchGearboxes(query = '', filters = {}) {
    return current().gearboxes.filter(r => matches(r, query) && (!filters.family || r.family === filters.family) && (!filters.condition || r.condition === filters.condition) && (filters.ratio === undefined || filters.ratio === null || r.ratio === filters.ratio) && (!filters.hasInertia || r.inputInertiaKgM2 !== null) && (filters.minPeakNm === undefined || (r.peakOutputNm !== null && r.peakOutputNm >= filters.minPeakNm)));
  }
  function availableRatios(familyOrId) {
    const data = current(), found = data.gearboxes.find(r => r.id === familyOrId);
    return [...new Set(data.gearboxes.filter(r => !familyOrId || r.family === (found ? found.family : familyOrId)).map(r => r.ratio))].sort((a, b) => a - b);
  }
  function combination(options) {
    if (!options || typeof options !== 'object') throw new Error('Combination identifiers required');
    for (const key of Object.keys(options)) if (!['motorId', 'gearboxId', 'ratio'].includes(key)) throw new Error('Unknown combination field: ' + key);
    const data = current(), motor = data.motors.find(r => r.id === options.motorId), gearbox = data.gearboxes.find(r => r.id === options.gearboxId);
    if (!motor || !gearbox) throw new Error('Select a known motor and gearbox SKU');
    if (own(options, 'ratio') && options.ratio !== gearbox.ratio) throw new Error('Ratio must match the selected gearbox SKU; choose another listing');
    const N = gearbox.ratio, eta = gearbox.efficiency;
    const product = (...a) => a.some(x => x === null) ? null : a.reduce((s, x) => s * x, 1);
    const limited = (a, b) => a === null || b === null ? null : Math.min(a, b);
    const gearedPeak = product(motor.peakTorqueNm, N, eta);
    const reflectedRotor = product(motor.rotorInertiaKgM2, N * N);
    const reflectedGear = product(gearbox.inputInertiaKgM2, N * N);
    const unresolved = [];
    if (motor.peakTorqueNm === null) unresolved.push('Motor peak torque is not sourced.');
    if (motor.continuousTorqueNm === null) unresolved.push('Motor continuous torque is not sourced.');
    if (motor.maxRpm === null) unresolved.push('Motor maximum rpm is not sourced; no safe combined speed limit.');
    if (eta === null) unresolved.push('Gearbox efficiency is missing or conflicting; enter an explicit assumption in the calculator.');
    if (gearbox.inputInertiaKgM2 === null) unresolved.push('Gearbox input-equivalent inertia is missing; an explicit approximation is needed.');
    if (gearbox.maxInputRpm === null) unresolved.push('Gearbox maximum input rpm is missing.');
    unresolved.push('Motor-to-gearbox mechanical mounting and adapters are unverified.');
    const result = {
      schema: COMBINATION_SCHEMA, id: motor.id + '__' + gearbox.id, name: motor.name + ' + ' + gearbox.name,
      motorId: motor.id, gearboxId: gearbox.id, catalogRevision: data.revision,
      gearRatio: N, efficiency: eta,
      peakMotorTorqueNm: motor.peakTorqueNm, continuousMotorTorqueNm: motor.continuousTorqueNm,
      rotorInertiaKgM2: motor.rotorInertiaKgM2, rotorInertiaLowKgM2: motor.rotorInertiaLowKgM2, rotorInertiaHighKgM2: motor.rotorInertiaHighKgM2,
      motorMaxRpm: motor.maxRpm, motorRatedRpm: motor.ratedRpm, motorNoLoadRpm: motor.noLoadRpm,
      gearboxInputInertiaKgM2: gearbox.inputInertiaKgM2, gearboxOutputInertiaKgM2: gearbox.outputInertiaKgM2, gearboxInertiaReference: gearbox.inertiaReference,
      gearRatedInputRpm: gearbox.ratedInputRpm, gearMaxInputRpm: gearbox.maxInputRpm,
      gearMaxOutputRpm: gearbox.maxInputRpm === null ? null : gearbox.maxInputRpm / N,
      gearContinuousOutputNm: gearbox.continuousOutputNm, gearPeakOutputNm: gearbox.peakOutputNm,
      metrics: {
        idealGearedPeakNm: product(motor.peakTorqueNm, N), sourceEfficiencyGearedPeakNm: gearedPeak,
        sourcePeakOutputBoundNm: limited(gearedPeak, gearbox.peakOutputNm),
        sourceContinuousOutputBoundNm: limited(product(motor.continuousTorqueNm, N, eta), gearbox.continuousOutputNm),
        rotorInertiaAtOutputKgM2: reflectedRotor,
        rotorInertiaLowAtOutputKgM2: product(motor.rotorInertiaLowKgM2, N * N),
        rotorInertiaHighAtOutputKgM2: product(motor.rotorInertiaHighKgM2, N * N),
        gearboxInputInertiaAtOutputKgM2: reflectedGear,
        knownInputEquivalentInertiaAtOutputKgM2: reflectedRotor === null || reflectedGear === null ? null : reflectedRotor + reflectedGear,
        safeCombinedMaxOutputRpm: null,
        scope: 'Static rating arithmetic only, no torque-speed curve; gear-only rpm is not a motor-safe envelope.'
      },
      motor, gearbox, unresolved, provenance: {motor: motor.provenance, gearbox: gearbox.provenance, sourceUrl: data.source.url, retrieved: data.retrieved}
    };
    return freeze(clone(result));
  }
  function mount(root, options = {}) {
    if (!root || !root.ownerDocument) throw new Error('Catalog mount needs a DOM root');
    const doc = root.ownerDocument; let alive = true, selected = null, draft = null, compared = [];
    const listeners = [];
    function el(tag, attrs = {}, text) {
      const n = doc.createElement(tag);
      for (const [k, v] of Object.entries(attrs)) { if (k === 'className') n.className = v; else n.setAttribute(k, v); }
      if (text !== undefined) n.textContent = text;
      return n;
    }
    function add(parent, tag, attrs, text) { const n = el(tag, attrs, text); parent.appendChild(n); return n; }
    function listen(node, event, fn) { node.addEventListener(event, fn); listeners.push([node, event, fn]); }
    const shell = add(root, 'section', {className: 'actuator-catalog', 'aria-label': 'Motor and SO gearbox catalog'});
    const status = add(shell, 'p', {className: 'ac-status', role: 'status'}, 'Loading motor and gearbox snapshot…');
    const controller = {
      ready: null,
      getSelection: () => selected,
      getComparisons: () => freeze(compared.slice()),
      exportJSON: () => JSON.stringify({schema: 'kinefold/actuator-candidates-v1', catalogRevision: current().revision, selected, comparisons: compared}, null, 2),
      destroy() { alive = false; listeners.forEach(([n, e, f]) => n.removeEventListener(e, f)); if (shell.parentNode) shell.parentNode.removeChild(shell); }
    };
    controller.ready = (options.catalog ? Promise.resolve(init(options.catalog)) : load(options.url)).then(data => {
      if (!alive) return controller;
      status.textContent = data.motors.length + ' motors · ' + data.gearboxes.length + ' SO listings · sheet snapshot ' + data.retrieved;
      add(shell, 'p', {className: 'ac-notice'}, 'Numerical candidates · mounting compatibility unverified. Source peaks, nominal gear ratings and estimated rotor inertia remain separate. Motor rpm limits are missing.');
      const columns = add(shell, 'div', {className: 'ac-columns'});
      const motorBox = add(columns, 'div', {className: 'ac-picker'}), gearBox = add(columns, 'div', {className: 'ac-picker'});
      function field(parent, text, tag, attrs) { const label = add(parent, 'label', {className: 'ac-field'}); add(label, 'span', {}, text); return add(label, tag, attrs); }
      const mq = field(motorBox, 'Find motor', 'input', {type: 'search', placeholder: 'Flipsky, ODrive, 6374…', 'data-ac': 'motor-search'});
      const ms = field(motorBox, 'Motor', 'select', {'data-ac': 'motor-select', size: '6'});
      const gq = field(gearBox, 'Find gearbox', 'input', {type: 'search', placeholder: 'EG23, planetary, used…', 'data-ac': 'gear-search'});
      const filters = add(gearBox, 'div', {className: 'ac-filters'});
      const family = field(filters, 'Family', 'select', {'data-ac': 'family'});
      const ratio = field(filters, 'Reduction', 'select', {'data-ac': 'ratio'});
      const condition = field(filters, 'Condition', 'select', {'data-ac': 'condition'});
      const gs = field(gearBox, 'Gearbox SKU / listing', 'select', {'data-ac': 'gear-select', size: '6'});
      const counts = add(gearBox, 'small', {className: 'ac-muted', 'data-ac': 'counts'});
      const info = add(shell, 'div', {className: 'ac-selection', 'data-ac': 'selection'});
      const actions = add(shell, 'div', {className: 'ac-actions'});
      const use = add(actions, 'button', {type: 'button', 'data-ac': 'use'}, 'Use combination');
      const pin = add(actions, 'button', {type: 'button', 'data-ac': 'pin'}, 'Pin for comparison (0/4)');
      const notice = add(actions, 'span', {role: 'status', 'data-ac': 'notice', className: 'ac-muted'});
      const comparison = add(shell, 'div', {className: 'ac-comparison', 'data-ac': 'comparison'});
      function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
      function fill(select, rows, old, label) {
        clear(select); rows.forEach(r => add(select, 'option', {value: r.id}, label(r)));
        select.value = rows.some(r => r.id === old) ? old : rows[0]?.id || '';
      }
      function simple(select, values, allLabel) { clear(select); add(select, 'option', {value: ''}, allLabel); values.forEach(v => add(select, 'option', {value: String(v)}, String(v))); select.value = ''; }
      const format = (v, digits = 3) => v === null ? 'Missing' : Number(v).toLocaleString('en', {maximumSignificantDigits: digits});
      const si = v => v === null ? 'Missing' : v.toExponential(4);
      function sourceLink(parent, label, href) { if (href && /^https?:\/\//.test(href)) add(parent, 'a', {href, target: '_blank', rel: 'noopener noreferrer'}, label); }
      function renderDraft() {
        clear(info); notice.textContent = '';
        draft = ms.value && gs.value ? combination({motorId: ms.value, gearboxId: gs.value}) : null;
        use.disabled = !draft; pin.disabled = !draft;
        if (!draft) { add(info, 'p', {}, 'No matching candidates. Clear a search or filter.'); return; }
        add(info, 'h4', {}, draft.name);
        const grid = add(info, 'dl', {className: 'ac-metrics'});
        for (const [k, v] of [
          ['Motor peak / continuous', format(draft.peakMotorTorqueNm) + ' / ' + format(draft.continuousMotorTorqueNm) + ' N m'],
          ['Reduction N = ωmotor / ωoutput', format(draft.gearRatio) + ':1'],
          ['Gear nominal / momentary', format(draft.gearContinuousOutputNm) + ' / ' + format(draft.gearPeakOutputNm) + ' N m'],
          ['Efficiency · source', draft.efficiency === null ? 'Missing / unresolved' : format(100 * draft.efficiency) + '% · ' + draft.gearbox.efficiencyStatus],
          ['Peak output bound · source η + gear cap', format(draft.metrics.sourcePeakOutputBoundNm) + ' N m'],
          ['Rotor inertia · ESTIMATED', si(draft.rotorInertiaKgM2) + ' kg m²'],
          ['Rotor scenarios · not confidence limits', si(draft.rotorInertiaLowKgM2) + ' to ' + si(draft.rotorInertiaHighKgM2) + ' kg m²'],
          ['Gear inertia · input-equivalent', si(draft.gearboxInputInertiaKgM2) + ' kg m²'],
          ['Motor maximum speed', format(draft.motorMaxRpm) + ' rpm'],
          ['Gear-only max input / output', format(draft.gearMaxInputRpm) + ' / ' + format(draft.gearMaxOutputRpm) + ' rpm']
        ]) { add(grid, 'dt', {}, k); add(grid, 'dd', {}, v); }
        const details = add(info, 'details'); add(details, 'summary', {}, 'Source, assumptions & unresolved fields');
        add(details, 'p', {}, draft.motor.torqueStatus + ' ' + draft.motor.notes);
        add(details, 'p', {}, draft.motor.rotorInertiaBoundsMeaning + ' ' + data.inertiaModel.exclusions);
        add(details, 'p', {}, (draft.gearbox.notes || '') + ' ' + (draft.gearbox.dataNotes || ''));
        add(details, 'p', {}, 'Mount: ' + draft.gearbox.motorInterface + '; input bore ' + format(draft.gearbox.inputBoreMm) + ' mm; ' + draft.gearbox.mountingReference + '. This does not verify a fit to the selected motor.');
        const ul = add(details, 'ul'); draft.unresolved.forEach(s => add(ul, 'li', {}, s));
        const links = add(details, 'p', {className: 'ac-links'});
        sourceLink(links, 'Motor sheet row ' + draft.motor.provenance.row, draft.motor.provenance.url);
        sourceLink(links, 'Gearbox sheet row ' + draft.gearbox.provenance.row, draft.gearbox.provenance.url);
        sourceLink(links, 'Rotor model', draft.motor.inertiaModel.provenance.url);
        sourceLink(links, 'Motor source', draft.motor.sourceUrl); sourceLink(links, 'Gearbox source', draft.gearbox.detailSourceUrl || draft.gearbox.sourceUrl);
      }
      function updateMotors() { fill(ms, searchMotors(mq.value), ms.value, r => r.name + ' · peak ' + format(r.peakTorqueNm) + ' N m'); renderDraft(); }
      function updateGears() {
        const rows = searchGearboxes(gq.value, {family: family.value || undefined, ratio: ratio.value ? Number(ratio.value) : undefined, condition: condition.value || undefined});
        fill(gs, rows, gs.value, r => r.name + ' · ' + r.ratio + ':1 · ' + format(r.peakOutputNm) + ' N m momentary');
        counts.textContent = rows.length + ' / ' + data.gearboxes.length + ' listings'; renderDraft();
      }
      function renderComparisons() {
        clear(comparison); pin.textContent = 'Pin for comparison (' + compared.length + '/4)';
        if (!compared.length) { add(comparison, 'p', {className: 'ac-muted'}, 'Pin up to four combinations to compare their ratings and inertia.'); return; }
        const wrap = add(comparison, 'div', {className: 'ac-table-scroll'}), table = add(wrap, 'table');
        const header = add(add(table, 'thead'), 'tr'); ['Candidate', 'N', 'Motor peak N m', 'Gear momentary N m', 'Source output bound N m', 'Rotor J × N² kg m²', 'Gear J × N² kg m²', ''].forEach(s => add(header, 'th', {scope: 'col'}, s));
        const body = add(table, 'tbody');
        compared.forEach(c => {
          const tr = add(body, 'tr'); [c.name, format(c.gearRatio), format(c.peakMotorTorqueNm), format(c.gearPeakOutputNm), format(c.metrics.sourcePeakOutputBoundNm), si(c.metrics.rotorInertiaAtOutputKgM2), si(c.metrics.gearboxInputInertiaAtOutputKgM2)].forEach(s => add(tr, 'td', {}, s));
          const remove = add(add(tr, 'td'), 'button', {type: 'button', 'aria-label': 'Remove ' + c.name}, 'Remove');
          listen(remove, 'click', () => { compared = compared.filter(x => x.id !== c.id); renderComparisons(); options.onCompare?.(controller.getComparisons()); });
        });
      }
      simple(family, [...new Set(data.gearboxes.map(r => r.family))].sort(), 'All families');
      simple(ratio, availableRatios(), 'All ratios'); simple(condition, [...new Set(data.gearboxes.map(r => r.condition))].sort(), 'All conditions');
      fill(ms, data.motors, options.motorId || data.motors.find(m => /6374 190KV/.test(m.name))?.id, r => r.name + ' · peak ' + format(r.peakTorqueNm) + ' N m');
      fill(gs, data.gearboxes, options.gearboxId || data.gearboxes.find(g => g.name === 'EG23-G50-D10')?.id, r => r.name + ' · ' + r.ratio + ':1 · ' + format(r.peakOutputNm) + ' N m momentary');
      counts.textContent = data.gearboxes.length + ' / ' + data.gearboxes.length + ' listings';
      listen(mq, 'input', updateMotors); listen(gq, 'input', updateGears);
      listen(family, 'change', () => { const old = ratio.value; simple(ratio, availableRatios(family.value), 'All ratios'); if (availableRatios(family.value).includes(Number(old))) ratio.value = old; updateGears(); });
      listen(ratio, 'change', updateGears); listen(condition, 'change', updateGears); listen(ms, 'change', renderDraft); listen(gs, 'change', renderDraft);
      listen(use, 'click', () => { if (!draft) return; selected = draft; notice.textContent = 'Combination passed to the calculator. No simulation or saved design changed.'; options.onSelect?.(selected); });
      listen(pin, 'click', () => {
        if (!draft) return;
        if (compared.some(c => c.id === draft.id)) { notice.textContent = 'Already pinned.'; return; }
        if (compared.length === 4) { notice.textContent = 'Four candidates pinned. Remove one to add another.'; return; }
        compared = compared.concat(draft); renderComparisons(); notice.textContent = 'Pinned locally for comparison.'; options.onCompare?.(controller.getComparisons());
      });
      if (options.onExport) { const exportButton = add(actions, 'button', {type: 'button', 'data-ac': 'export'}, 'Save candidate JSON'); listen(exportButton, 'click', () => options.onExport({filename: 'actuator-candidates.json', mimeType: 'application/json', text: controller.exportJSON()})); }
      renderDraft(); renderComparisons(); selected = draft; options.onSelect?.(selected);
      return controller;
    }).catch(e => { if (alive) status.textContent = 'Catalog unavailable: ' + e.message; throw e; });
    return controller;
  }
  return {SCHEMA, COMBINATION_SCHEMA, init, normalize, load, getCatalog: current, searchMotors, searchGearboxes, availableRatios, combination, mount};
});
