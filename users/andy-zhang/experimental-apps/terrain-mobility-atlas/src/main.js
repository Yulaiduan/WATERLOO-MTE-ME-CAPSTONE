import 'maplibre-gl/dist/maplibre-gl.css';
import mapWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import './style.css';
import { DEFAULT_VEHICLE, VEHICLES, CONTROLS, clone, format, normalizeVehicle, evaluate } from './model.js';
import { REGIONS, CELLS, defaultCell } from './data.js';

const $ = selector => document.querySelector(selector);
const escape = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const statusLabels = { pass: 'Within limits', near: 'Near limit', fail: 'Outside limits', unknown: 'Missing evidence' };
const colors = { pass: '#2c8c66', near: '#bd8519', fail: '#cd4239', unknown: '#74828e' };
const terrainLabels = { grade: 'Grade', cross: 'Cross-slope', roughness: 'Roughness RMS', obstacle: 'Obstacle height', spacing: 'Obstacle spacing', corridor: 'Corridor width', surface: 'Surface' };
let saved;
try { saved = JSON.parse(localStorage.getItem('terrain-vehicle-v1')); } catch { /* Defaults remain usable without storage. */ }
const state = { vehicle: normalizeVehicle(saved), selected: defaultCell('shield').id, region: 'shield', mapReady: false };
let map;
let exportUrl;
const selectedCell = () => CELLS.find(c => c.id === state.selected);
const selectedRegion = () => REGIONS.find(r => r.id === selectedCell().region);
const motionDuration = duration => window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : duration;

$('#app').innerHTML = `
  <header class="app-header"><h1>Terrain atlas</h1><div class="header-actions"><a href="/linkage/">Linkage simulator →</a><a href="/workbench/">Simulation workbench →</a><button id="export" class="primary">Export scenario</button></div></header>
  <main class="workspace">
    <aside class="vehicle-panel" aria-labelledby="vehicle-heading">
      <div class="panel-heading"><h2 id="vehicle-heading">Vehicle capabilities</h2><button id="reset" class="text-button">Reset</button></div>
      <label class="field">Profile name<input id="vehicle-name" maxlength="60" value="${escape(state.vehicle.name)}" /></label>
      <label class="field">Vehicle preset<select id="vehicle-preset"><option value="custom">Custom</option>${Object.entries(VEHICLES).map(([id, v]) => `<option value="${id}">${escape(v.name)}</option>`).join('')}</select></label>
      <div class="controls">${CONTROLS.map(c => `<div class="control"><label for="${c.key}">${c.label} <span class="unit">${c.unit}</span></label><input type="number" id="${c.key}" min="${c.min}" max="${c.max}" step="${c.step}" value="${state.vehicle[c.key]}" aria-describedby="hint-${c.key}" /><small id="hint-${c.key}">${escape(c.hint)}</small></div>`).join('')}</div>
      <fieldset><legend>Supported surfaces</legend><div class="surface-options">${['hard', 'mixed', 'loose', 'soft'].map(s => `<label><input type="checkbox" name="surface" value="${s}" ${state.vehicle.surfaces.includes(s) ? 'checked' : ''} />${s[0].toUpperCase() + s.slice(1)}</label>`).join('')}</div></fieldset>
      <div class="profile-actions"><button id="save">Save profile</button><span id="save-status" role="status" aria-live="polite">${saved ? 'Profile restored' : 'Local profile'}</span></div>
      <details class="method-notes"><summary>Assumptions & method</summary><p>Capabilities assume <strong>1 m/s and a fixed payload</strong>. Payload mass is not specified in this screening model. No seasonality or traction model is included.</p><p>Each limit is evaluated separately. One failed constraint makes the result outside limits. Missing critical inputs remain unknown unless another constraint establishes failure. A normalized margin below 15% is near limit; it is not a success probability.</p><p>Spacing is the minimum separation the vehicle needs. Corridor is vehicle width plus total clearance. Grade and cross-slope use percent rise/run, with an assumed heading.</p></details>
    </aside>
    <section class="terrain-panel" aria-labelledby="terrain-heading">
      <div class="panel-heading"><h2 id="terrain-heading">Scenario map</h2><button id="world-view" class="text-button">World view</button></div>
      <div class="scenario-selectors"><label class="field">Region<select id="region-select">${REGIONS.map(r => `<option value="${r.id}" ${r.id === state.region ? 'selected' : ''}>${escape(r.name)}</option>`).join('')}</select></label><label class="field">Scenario cell<select id="cell-select"></select></label></div>
      <div class="map-frame"><div id="map" aria-label="Geographic context and illustrative scenario cells"></div><p id="map-error" role="status" hidden></p></div>
      <div class="map-legend" aria-label="Cell status legend">${Object.entries(statusLabels).map(([key, label]) => `<span><i style="background:${colors[key]}" aria-hidden="true"></i>${label}</span>`).join('')}</div>
      <p class="map-caption">Terrain values and cell boundaries are illustrative. Geography provides location context, not measured roots, rocks, or route feasibility.</p>
      <section id="inspector" class="inspector" aria-label="Selected scenario evaluation"></section>
      <details class="source-notes"><summary>Data sources</summary><p>Geographic outlines: <a href="https://www.naturalearthdata.com/about/terms-of-use/" target="_blank" rel="noopener noreferrer">Natural Earth</a>. Regional labels, scenario footprints, and every terrain value are synthetic assumptions. The atlas does not extract microterrain from these outlines.</p><p>Use the <a href="/workbench/">simulation workbench</a> for measured profile replay, sourced parameters, terrain plots, and mechanism calculations.</p></details>
    </section>
  </main>
  <dialog id="export-dialog" aria-labelledby="export-title"><div class="dialog-heading"><h2 id="export-title">Export selected scenario</h2><button id="close-export" aria-label="Close export">Close</button></div><p>Includes the selected cell, current vehicle, units, assumptions, and evaluated constraints.</p><label for="export-preview">JSON snapshot</label><textarea id="export-preview" rows="12" readonly spellcheck="false"></textarea><div class="export-actions"><a id="download-export" class="button primary" download="terrain-scenario.json">Download JSON</a><button id="copy-export">Copy JSON</button></div><span id="export-status" role="status" aria-live="polite"></span></dialog>
`;

function markDirty() { $('#save-status').textContent = 'Unsaved'; $('#vehicle-preset').value = 'custom'; }
function syncControls() {
  $('#vehicle-name').value = state.vehicle.name;
  for (const c of CONTROLS) $(`#${c.key}`).value = state.vehicle[c.key];
  document.querySelectorAll('[name="surface"]').forEach(el => { el.checked = state.vehicle.surfaces.includes(el.value); });
}
function syncSelection() {
  const cell = selectedCell();
  $('#region-select').value = cell.region;
  const select = $('#cell-select');
  if (select.dataset.region !== cell.region) {
    select.innerHTML = CELLS.filter(c => c.region === cell.region).map(c => `<option value="${c.id}">Cell ${String(c.id + 1).padStart(3, '0')} · ${Math.abs(c.center[1]).toFixed(1)}° ${c.center[1] < 0 ? 'S' : 'N'}, ${Math.abs(c.center[0]).toFixed(1)}° ${c.center[0] < 0 ? 'W' : 'E'}</option>`).join('');
    select.dataset.region = cell.region;
  }
  select.value = cell.id;
}
function renderInspector() {
  const cell = selectedCell(), region = selectedRegion();
  const result = evaluate(cell.terrain, state.vehicle);
  const limitation = result.failures.length ? result.failures.map(c => terrainLabels[c.key]).join(', ') : result.unknowns.length ? result.unknowns.map(c => terrainLabels[c.key]).join(', ') : terrainLabels[result.limiting.key];
  const status = c => `<span class="status ${c.status}">${statusLabels[c.status]}</span>`;
  $('#inspector').innerHTML = `<div class="inspector-heading"><div><h3>${escape(region.name)} <span>· Cell ${String(cell.id + 1).padStart(3, '0')}</span></h3><p>${escape(region.biome)} · ${escape(region.location)}</p></div>${status(result)}</div><p class="limitation"><strong>${result.failures.length ? 'Exceeded limits' : result.unknowns.length ? 'Missing inputs' : 'Tightest constraint'}:</strong> ${escape(limitation)}${result.margin != null && !result.failures.length ? ` · ${result.margin}% minimum margin` : ''}</p><div class="table-wrap"><table><caption class="sr-only">Selected terrain demand compared with current vehicle capability</caption><thead><tr><th scope="col">Constraint</th><th scope="col">Terrain</th><th scope="col">Vehicle limit</th><th scope="col">Result</th></tr></thead><tbody>${result.constraints.map(c => `<tr><th scope="row">${terrainLabels[c.key]}</th><td>${c.demand == null ? '<span class="missing">Unknown</span>' : c.key === 'surface' ? escape(c.demand) : `${format(c.demand, c.key)} ${c.unit}`}</td><td>${c.key === 'surface' ? escape(c.capacity.join(', ') || 'None') : `${['spacing', 'corridor'].includes(c.key) ? '≥' : '≤'} ${format(c.capacity, c.key)} ${c.unit}`}</td><td>${status(c)}</td></tr>`).join('')}</tbody></table></div><p class="evidence">Evidence: illustrative terrain assumptions; no local observations. ${result.unknowns.length ? `${result.unknowns.length} critical inputs are missing.` : 'All screening inputs are populated.'}</p>`;
}
function cellFeatures() {
  return { type: 'FeatureCollection', features: CELLS.map(c => {
    const status = evaluate(c.terrain, state.vehicle).status;
    return { type: 'Feature', geometry: c.geometry, properties: { id: c.id, status, color: colors[status] } };
  }) };
}
function render() {
  syncSelection(); renderInspector();
  if (state.mapReady) {
    map.getSource('cells').setData(cellFeatures());
    map.setFilter('selected-cell', ['==', ['get', 'id'], state.selected]);
  }
}
function worldView(duration = 600) {
  map?.fitBounds([[-171, -55], [174, 74]], { padding: 24, duration: motionDuration(duration) });
}
function selectCell(id, fly = false) {
  state.selected = Number(id); state.region = selectedCell().region; render();
  if (fly) map?.flyTo({ center: selectedCell().center, zoom: 3.2, duration: motionDuration(700) });
}
function showMapError(message) { $('#map-error').hidden = false; $('#map-error').textContent = message; }
async function initializeMap() {
  try {
    const maplibregl = await import('maplibre-gl');
    maplibregl.setWorkerUrl(mapWorkerUrl);
    map = new maplibregl.Map({ container: 'map', style: { version: 8, sources: {}, layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#e5e7e0' } }] }, center: [-5, 23], zoom: 0.75, minZoom: -1.5, maxZoom: 9, attributionControl: false, renderWorldCopies: false, dragRotate: false, pitchWithRotate: false });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    map.addControl(new maplibregl.AttributionControl({ compact: true, customAttribution: '© Natural Earth · Illustrative scenarios' }), 'bottom-right');
    map.on('load', async () => {
      try {
        const response = await fetch('/countries.geojson');
        if (!response.ok) throw new Error('Geographic outlines could not load.');
        map.addSource('countries', { type: 'geojson', data: await response.json() });
        map.addLayer({ id: 'land', type: 'fill', source: 'countries', paint: { 'fill-color': '#fcfcfa' } });
        map.addLayer({ id: 'borders', type: 'line', source: 'countries', paint: { 'line-color': '#bfc1b7', 'line-width': 0.65 } });
        map.addSource('cells', { type: 'geojson', data: cellFeatures() });
        map.addLayer({ id: 'terrain-cells', type: 'fill', source: 'cells', paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.55 } });
        map.addLayer({ id: 'cell-grid', type: 'line', source: 'cells', paint: { 'line-color': '#fcfcfa', 'line-width': 0.5, 'line-opacity': 0.7 } });
        map.addLayer({ id: 'selected-cell', type: 'line', source: 'cells', filter: ['==', ['get', 'id'], state.selected], paint: { 'line-color': '#23251d', 'line-width': 2.5 } });
        map.on('click', 'terrain-cells', e => selectCell(e.features[0].properties.id));
        map.on('mouseenter', 'terrain-cells', () => { map.getCanvas().style.cursor = 'pointer'; });
        map.on('mouseleave', 'terrain-cells', () => { map.getCanvas().style.cursor = ''; });
        state.mapReady = true; worldView(0);
      } catch (error) { showMapError(`${error.message} Use the region and cell selectors to inspect scenarios.`); }
    });
    map.on('error', () => showMapError('Map rendering is unavailable. Use the region and cell selectors to inspect scenarios.'));
  } catch { showMapError('The map could not start. Use the region and cell selectors to inspect scenarios.'); }
}

for (const c of CONTROLS) {
  $(`#${c.key}`).addEventListener('input', e => {
    if (e.target.value === '' || !e.target.validity.valid) return;
    state.vehicle[c.key] = Number(e.target.value); markDirty(); render();
  });
  $(`#${c.key}`).addEventListener('change', e => {
    if (e.target.value === '' || !e.target.validity.valid) { e.target.value = state.vehicle[c.key]; }
  });
}
$('#vehicle-name').addEventListener('input', e => { state.vehicle.name = e.target.value; markDirty(); });
document.querySelectorAll('[name="surface"]').forEach(el => el.addEventListener('change', () => {
  state.vehicle.surfaces = [...document.querySelectorAll('[name="surface"]:checked')].map(input => input.value); markDirty(); render();
}));
$('#vehicle-preset').addEventListener('change', e => {
  if (!VEHICLES[e.target.value]) return;
  state.vehicle = clone(VEHICLES[e.target.value]); syncControls(); $('#save-status').textContent = 'Unsaved'; render();
});
$('#reset').addEventListener('click', () => { state.vehicle = clone(DEFAULT_VEHICLE); syncControls(); markDirty(); render(); });
$('#save').addEventListener('click', () => {
  try { localStorage.setItem('terrain-vehicle-v1', JSON.stringify(state.vehicle)); $('#save-status').textContent = 'Saved on this device'; }
  catch { $('#save-status').textContent = 'Storage unavailable; export to save.'; }
});
$('#region-select').addEventListener('change', e => selectCell(defaultCell(e.target.value).id, true));
$('#cell-select').addEventListener('change', e => selectCell(e.target.value, true));
$('#world-view').addEventListener('click', () => worldView());
$('#export').addEventListener('click', () => {
  if (exportUrl) URL.revokeObjectURL(exportUrl);
  const cell = selectedCell();
  const snapshot = JSON.stringify({ schemaVersion: 2, exportedAt: new Date().toISOString(), provenance: 'Illustrative scenario assumptions. Natural Earth outlines provide geographic context only. No measured microterrain or route feasibility.', vehicle: clone(state.vehicle), region: { id: selectedRegion().id, name: selectedRegion().name, biome: selectedRegion().biome }, selectedCell: cell, evaluation: evaluate(cell.terrain, state.vehicle), units: { grade: 'percent', cross: 'percent', roughness: 'mm RMS over 5 m detrended profile', obstacle: 'mm', spacing: 'm', corridor: 'm', area: 'km2' }, assumptions: { speed_m_s: 1, payload: 'Fixed, mass unspecified', seasonality: false, heading: 'Assumed', gradeLimit: 'Symmetric climb and descent', nearLimitThreshold: 0.15 } }, null, 2);
  $('#export-preview').value = snapshot;
  exportUrl = URL.createObjectURL(new Blob([snapshot], { type: 'application/json' }));
  $('#download-export').href = exportUrl;
  $('#export-status').textContent = '';
  $('#export-dialog').showModal();
});
$('#copy-export').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText($('#export-preview').value); $('#export-status').textContent = 'Copied.'; }
  catch { $('#export-preview').focus(); $('#export-preview').select(); $('#export-status').textContent = 'Press Ctrl+C to copy the selected JSON.'; }
});
$('#download-export').addEventListener('click', () => { $('#export-status').textContent = 'Download requested.'; });
$('#close-export').addEventListener('click', () => $('#export-dialog').close());
$('#export-dialog').addEventListener('close', () => { if (exportUrl) URL.revokeObjectURL(exportUrl); exportUrl = undefined; });
render();
initializeMap();
