/** Verify source ingestion, SI conversions, rating arithmetic and catalog DOM callbacks.
 * Run: node verify-motor-gearbox-catalog.cjs from this app (Node standard library only).
 * Inputs: offline motor/gearbox JSON; N m, kg m², rpm, mm and source kg cm².
 * Output: assertion count; no server, live library/source-sheet writes or simulation.
 * Limit: minimal DOM fixture checks handlers/content, not browser CSS or mounting/hardware.
 */
'use strict';
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const raw = JSON.parse(fs.readFileSync(__dirname + '/motor-gearbox-catalog.json', 'utf8'));
const C = require('./motor-gearbox-catalog.js');
let checks = 0;
const ok = (value, label) => { assert.ok(value, label); checks++; };
const equal = (a, b, label) => { assert.deepEqual(a, b, label); checks++; };
const near = (a, b, label) => ok(Math.abs(a - b) <= Math.max(1e-15, Math.abs(b) * 2e-9), label);
const throws = fn => { assert.throws(fn); checks++; };
const copy = x => JSON.parse(JSON.stringify(x));
const before = JSON.stringify(raw), data = C.init(raw);
equal(Object.keys(data.motors[0].inertiaModel.components[0]), ['Motor model', 'Rotating component', 'Material (assumed)', 'Density (kg/m³)', 'Outer radius (mm)', 'Inner radius (mm)', 'Axial length (mm)', 'Occupied fraction', 'Component mass (kg)', 'Component Jz (kg·m²)', 'Geometry check', 'Model note'], 'Verified component-model columns');
equal([data.motors.length, data.gearboxes.length], [14, 157], 'Complete named motor/SO listing snapshot');
equal(JSON.stringify(raw), before, 'No mutation of source snapshot');
ok(Object.isFrozen(data) && Object.isFrozen(data.motors[0].inertiaModel.components), 'Deep immutable records');
equal(data.gearboxes.filter(g => g.inputInertiaKgM2 !== null).length, 12, '12 sourced input inertias');
equal(data.gearboxes.filter(g => g.efficiency === null).length, 14, '14 unresolved efficiencies');
for (const m of data.motors) {
  equal(m.peakTorqueNm, m.sourceValues['Peak/stall τ (N·m)'], m.name + ' source peak');
  equal(m.continuousTorqueNm, m.sourceValues['Rated τ (N·m)'], m.name + ' source rated');
  equal(m.rotorInertiaKgM2, m.inertiaModel.values['Rotor Jz estimate (kg·m²)'], 'Name-based Rev2 join');
  equal(m.name, m.inertiaModel.values['Motor model'], 'No old positional inertia mapping');
  equal(m.rotorInertiaKgM2, m.sourceValues['Rotor J (kg·m²)'], 'Displayed/current model agreement');
  equal([m.ratedRpm, m.noLoadRpm, m.maxRpm], [null, null, null], 'No invented rpm limit');
  equal(m.inertiaModel.components.length, 6, 'Six rotating components only');
  let total = 0;
  for (const c of m.inertiaModel.components) {
    // Header names are verified below; use exact source keys instead of row positions.
    const header = Object.keys(c);
    const density = c[header[3]], outer = c[header[4]] * .001, inner = c[header[5]] * .001;
    const length = c[header[6]] * .001, fraction = c[header[7]];
    const mass = density * Math.PI * length * fraction * (outer * outer - inner * inner);
    const inertia = .5 * mass * (outer * outer + inner * inner);
    near(inertia, c[header[9]], 'Independent annulus component integral');
    total += c[header[9]];
  }
  near(total, m.rotorInertiaKgM2, 'Six component sum matches selected J');
  ok(m.rotorInertiaLowKgM2 <= m.rotorInertiaKgM2 && m.rotorInertiaHighKgM2 >= m.rotorInertiaKgM2, 'Scenario endpoints bound nominal');
  ok(m.provenance.url.includes('gid=1825746970') && m.fieldCells.peakTorqueNm === 'J' + m.provenance.row, 'Exact motor row/cells retained');
}
for (const g of data.gearboxes) {
  equal(g.ratio, g.sourceValues['Ratio (:1)'], 'Exact ratio per actual SKU');
  equal(g.continuousOutputNm, g.sourceValues['Nominal / max permissible (Nm)'], 'Nominal source retained separately');
  equal(g.peakOutputNm, g.sourceValues['Momentary permissible (Nm)'], 'Momentary source retained separately');
  equal(g.efficiency, g.sourceValues.Efficiency, 'No borrowed family efficiency');
  equal(g.inputInertiaKgM2, g.inputInertiaKgCm2 === null ? null : g.inputInertiaKgCm2 * 1e-4, 'kg cm² → SI');
  equal(g.outputInertiaKgM2, null, 'No invented second output inertia');
  ok(g.provenance.range === 'A' + g.provenance.row + ':AN' + g.provenance.row, 'Exact listing row');
}
const motor = data.motors.find(m => /6374 190KV/.test(m.name));
const gear = data.gearboxes.find(g => g.name === 'EG23-G50-D10');
const combo = C.combination({motorId: motor.id, gearboxId: gear.id});
equal(combo.gearRatio, 50); near(combo.metrics.idealGearedPeakNm, 400); near(combo.metrics.sourceEfficiencyGearedPeakNm, 376);
equal(combo.metrics.sourcePeakOutputBoundNm, 50, 'Gear momentary cap governs');
near(combo.metrics.rotorInertiaAtOutputKgM2, motor.rotorInertiaKgM2 * 2500);
near(combo.metrics.gearboxInputInertiaAtOutputKgM2, .03 * 1e-4 * 2500);
near(combo.metrics.knownInputEquivalentInertiaAtOutputKgM2, (motor.rotorInertiaKgM2 + .03 * 1e-4) * 2500, 'No double-count of referred gearbox inertia');
equal(combo.metrics.sourceContinuousOutputBoundNm, null, 'Peak does not invent continuous limit');
equal(combo.metrics.safeCombinedMaxOutputRpm, null, 'Gear-only rpm is not combined safe limit');
equal(combo.gearMaxOutputRpm, gear.maxInputRpm / gear.ratio);
const conflict = data.gearboxes.find(g => g.family === 'EGS11');
const unresolved = C.combination({motorId: motor.id, gearboxId: conflict.id});
equal(unresolved.efficiency, null); equal(unresolved.metrics.sourceEfficiencyGearedPeakNm, null); equal(unresolved.metrics.sourcePeakOutputBoundNm, null);
ok(unresolved.unresolved.some(s => /efficiency/.test(s)), 'Conflict visible');
const ua = data.motors.find(m => m.name.includes('UA80'));
equal(C.combination({motorId: ua.id, gearboxId: gear.id}).peakMotorTorqueNm, null, 'Bench motor has no verified torque');
throws(() => C.combination({motorId: motor.id, gearboxId: gear.id, ratio: 10}));
throws(() => C.combination({motorId: motor.id, gearboxId: gear.id, efficiency: .9}));
throws(() => C.combination({motorId: 'missing', gearboxId: gear.id}));
equal(C.availableRatios(gear.id), C.availableRatios(gear.family));
ok(C.searchMotors('FLIPSKY 6374').length >= 2, 'Case insensitive AND search');
ok(C.searchGearboxes('eg23', {ratio: 50}).every(g => g.family === 'EG23' && g.ratio === 50));
ok(C.searchGearboxes('', {hasInertia: true}).length === 12);
ok(C.searchGearboxes('', {condition: 'Used'}).every(g => g.condition === 'Used'));
for (const value of [null, NaN, Infinity, true, -1, '50']) { const d = copy(raw); d.gearboxes[0].ratio = value; throws(() => C.normalize(d)); }
for (const value of [NaN, true, -1]) { const d = copy(raw); d.motors[0].rotorInertiaKgM2 = value; throws(() => C.normalize(d)); }
for (const mutate of [d => { d.gearboxes[1].id = d.gearboxes[0].id; }, d => { delete d.motors[0].peakTorqueNm; }, d => { d.gearboxes[0].efficiency = 1.1; }, d => { d.gearboxes[0].inputInertiaKgCm2 = 1; d.gearboxes[0].inputInertiaKgM2 = 1; }]) { const d = copy(raw); mutate(d); throws(() => C.normalize(d)); }

class Element {
  constructor(tag, doc) { this.tagName = tag.toUpperCase(); this.ownerDocument = doc; this.children = []; this.attrs = {}; this.listeners = {}; this.parentNode = null; this._value = ''; this._text = ''; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  appendChild(n) { this.children.push(n); n.parentNode = this; return n; }
  removeChild(n) { this.children.splice(this.children.indexOf(n), 1); n.parentNode = null; return n; }
  get firstChild() { return this.children[0] || null; }
  set textContent(v) { this.children = []; this._text = String(v); }
  get textContent() { return this._text + this.children.map(c => c.textContent).join(' '); }
  set value(v) { this._value = String(v); }
  get value() { return this.tagName === 'OPTION' ? this.attrs.value : this._value; }
  addEventListener(e, f) { (this.listeners[e] ||= []).push(f); }
  removeEventListener(e, f) { this.listeners[e] = (this.listeners[e] || []).filter(x => x !== f); }
  fire(e) { if (!this.disabled) (this.listeners[e] || []).slice().forEach(f => f({target: this})); }
  find(attr, value) { for (const c of this.children) { if (c.attrs[attr] === value) return c; const found = c.find(attr, value); if (found) return found; } return null; }
}
const document = {createElement(tag) { return new Element(tag, this); }};
async function main() {
  const sandbox = {fetch: async () => ({ok: true, json: async () => copy(raw)}), console};
  vm.createContext(sandbox); vm.runInContext(fs.readFileSync(__dirname + '/motor-gearbox-catalog.js', 'utf8'), sandbox);
  const B = sandbox.KinefoldActuatorCatalog;
  const rootA = new Element('div', document), rootB = new Element('div', document), selections = [], comparisons = [], exports = [];
  const a = B.mount(rootA, {onSelect: c => selections.push(c), onCompare: c => comparisons.push(c), onExport: x => exports.push(x)});
  const b = B.mount(rootB, {});
  await Promise.all([a.ready, b.ready]);
  equal(selections.length, 1, 'Initial source combination delivered once');
  equal(a.getSelection().id, combo.id, 'Useful default known-J candidate');
  const find = (role, root = rootA) => { const n = root.find('data-ac', role); assert.ok(n, role); return n; };
  equal(find('motor-select').children.length, 14); equal(find('gear-select').children.length, 157);
  equal(find('gear-select', rootB).value, gear.id, 'Two asynchronous mounts both fill options');
  find('motor-search').value = 'ODrive'; find('motor-search').fire('input');
  equal(find('motor-select').children.length, 3); equal(selections.length, 1, 'Draft selection does not apply');
  find('use').fire('click'); equal(selections.length, 2); ok(a.getSelection().motor.name.startsWith('ODrive'));
  find('pin').fire('click'); find('pin').fire('click'); equal(a.getComparisons().length, 1, 'No duplicate pin');
  for (const g of data.gearboxes.slice(0, 5)) { find('gear-select').value = g.id; find('gear-select').fire('change'); find('pin').fire('click'); }
  equal(a.getComparisons().length, 4, 'Comparison bounded to four captured candidates');
  ok(Object.isFrozen(a.getComparisons()) && Object.isFrozen(a.getComparisons()[0].motor), 'Immutable captured comparisons');
  ok(comparisons.length === 4 && comparisons[0].length === 1, 'Captured callback arrays do not mutate');
  const table = find('comparison');
  function firstRemove(n) { if (n.tagName === 'BUTTON' && n.textContent === 'Remove') return n; for (const c of n.children) { const result = firstRemove(c); if (result) return result; } return null; }
  firstRemove(table).fire('click'); equal(a.getComparisons().length, 3); equal(comparisons.at(-1).length, 3);
  find('export').fire('click'); equal(exports.length, 1); equal(JSON.parse(exports[0].text).comparisons.length, 3); equal(exports[0].mimeType, 'application/json');
  find('family').value = 'EG23'; find('family').fire('change'); find('ratio').value = '50'; find('ratio').fire('change');
  ok(find('gear-select').children.every(n => /EG23-G50/.test(n.textContent)), 'Family/ratio DOM filters');
  find('gear-search').value = 'no-such-gear'; find('gear-search').fire('input');
  equal(find('gear-select').children.length, 0); ok(find('use').disabled && find('pin').disabled, 'Empty search blocks apply');
  ok(rootA.textContent.includes('mounting compatibility unverified') && rootA.textContent.includes('Motor rpm limits are missing'), 'Important missing/fit labels visible');
  a.destroy(); b.destroy(); equal(rootA.children.length, 0); equal(rootB.children.length, 0);
  console.log(`PASS ${checks} catalog/source/SI/rating/DOM assertions; 14 motors, 157 SO listings; no server, library writes or hardware claims.`);
}
main().catch(e => { console.error(e); process.exitCode = 1; });
