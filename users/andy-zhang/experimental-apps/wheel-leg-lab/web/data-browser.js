/** Mount the motion lab's browser-local profiles and recorded-data inspector.
 * Invocation: mountDataBrowser(element, callbacks), then refresh()/setTheme('dark'|'light').
 * Inputs: library JSON/SI solver channels; outputs: Plotly inspection, CSV/JSON and load callbacks.
 * Limitations: numeric data only, original units retained; IndexedDB stays in this browser/origin.
 */
import { listRecords, getRecord, saveRecord, normalizeImport, downloadJSON, extractTables, numericRow, MAX_IMPORT_BYTES } from './library.js';

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function button(text, action) { const node = element('button', text); node.type = 'button'; node.addEventListener('click', action); return node; }
function field(label, control) { const node = element('label', label); node.append(control); return node; }
function csvCell(value) { const text = String(value ?? ''); return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text; }
function csvDownload(rows, name) {
  const columns = [...new Set(rows.flatMap(row => Object.keys(row)))];
  const csv = [columns.map(csvCell).join(','), ...rows.map(row => columns.map(key => csvCell(row[key])).join(','))].join('\r\n');
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  const link = element('a'); link.href = url; link.download = name.replace(/[<>:"/\\|?*\x00-\x1f]/g, '-') + '.csv'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function mountDataBrowser(root, { onLoadProfile = () => {}, onPymunk = () => {}, onLoadStudy=()=>{}, theme = 'light' } = {}) {
  let summaries = [], selected = null, tableIndex = 0, normalizedRows = [], channels = [], selectedChannels = [], xChannel = 't', currentTheme = theme, plotRevision = 0;
  let selectionGeneration = 0;
  root.replaceChildren();
  const heading = element('div', undefined, 'panel-head');
  heading.append(element('h2', 'Profiles & recorded data'), element('p', 'Save locally in this browser; download JSON for a portable backup.'));
  root.append(heading);
  const status = element('div', '', 'data-status'); status.setAttribute('role', 'status');
  const error = element('div', '', 'error'); error.setAttribute('role', 'alert'); error.hidden = true;
  root.append(status, error);
  const layout = element('div', undefined, 'data-layout'), sidebar = element('aside', undefined, 'data-sidebar'), detail = element('section', undefined, 'data-detail');
  layout.append(sidebar, detail); root.append(layout);
  const search = element('input'); search.type = 'search'; search.placeholder = 'Search profiles and runs'; search.setAttribute('aria-label', 'Search profiles and runs');
  const file = element('input'); file.type = 'file'; file.accept = '.json,application/json'; file.setAttribute('aria-label', 'Import profile or recorded run JSON');
  const importer = field('Import JSON', file), listing = element('div', undefined, 'data-record-list');
  sidebar.append(search, importer, button('Refresh library', () => refresh()), listing);
  const metadata = element('div', undefined, 'data-metadata'), actions = element('div', undefined, 'data-controls'), controls = element('div', undefined, 'data-controls'), channelBox = element('fieldset', undefined, 'data-channel-list');
  const chart = element('div', undefined, 'data-chart'); chart.setAttribute('aria-label', 'Recorded numeric channels'); chart.style.minHeight = '380px';
  const tableCaption = element('p', '', 'muted'), tableHolder = element('div', undefined, 'data-table');
  detail.append(metadata, actions, controls, channelBox, chart, tableCaption, tableHolder);
  const empty = element('p', 'Select a saved study. Run a simulation and save its profile or data, or import a JSON file.'); metadata.append(empty);
  [actions, controls, channelBox, chart, tableCaption, tableHolder].forEach(node => node.hidden = true);

  function report(message) { error.hidden = false; error.textContent = message instanceof Error ? message.message : String(message); }
  function clearError() { error.hidden = true; error.textContent = ''; }
  async function safe(action) { clearError(); try { await action(); } catch (cause) { report(cause); } }
  function list() {
    listing.replaceChildren();
    const query = search.value.toLowerCase().trim();
    const shown = summaries.filter(item => `${item.name} ${item.backend || ''} ${item.kind}`.toLowerCase().includes(query));
    if (!shown.length) listing.append(element('p', query ? 'No matching studies.' : 'Your library is empty.'));
    for (const item of shown) {
      const row = button('', () => safe(() => selectRecord(item.id))); row.className = 'data-record'; row.setAttribute('aria-pressed', String(item.id === selected?.id));
      row.append(element('strong', item.name), element('span', `${item.backend || 'Imported data'} · ${item.kind}${item.sample_count ? ' · ' + item.sample_count.toLocaleString() + ' samples' : ''}`), element('small', new Date(item.created_at).toLocaleString()));
      listing.append(row);
    }
  }
  async function refresh() {
    try { summaries = await listRecords(); list(); status.textContent = `${summaries.length} saved studies · browser-local storage`; }
    catch (cause) { report(cause); }
  }
  search.addEventListener('input', list);
  file.addEventListener('change', () => safe(async () => {
    const chosen = file.files?.[0]; if (!chosen) return;
    try {
      if (chosen.size > MAX_IMPORT_BYTES) throw new Error('JSON exceeds the 80 MiB import limit.');
      let json; try { json = JSON.parse(await chosen.text()); } catch { throw new Error('This file is not valid JSON.'); }
      const imported = normalizeImport(json, chosen.name);
      const saved = await saveRecord(imported); await refresh(); await selectRecord(saved.id);
      status.textContent = `Imported ${saved.name}${saved.kind === 'dataset' ? ' as read-only recorded data' : ''}.`;
    } finally { file.value = ''; }
  }));

  async function selectRecord(id) {
    const generation = ++selectionGeneration;
    const record = await getRecord(id);
    if (generation !== selectionGeneration) return;
    if (!record) throw new Error('Saved study could not be found. Refresh the library.');
    selected = record; tableIndex = 0; selectedChannels = []; plotRevision++; list();
    metadata.replaceChildren(element('h3', record.name));
    const text = `${record.backend || 'Imported dataset'} · ${record.kind} · saved ${new Date(record.created_at).toLocaleString()}`;
    metadata.append(element('p', text));
    const configPanel = element('details'), summary = element('summary', record.config ? 'Saved configuration & reference inputs' : 'Dataset provenance');
    const pre = element('pre', JSON.stringify({ config: record.config, reference_inputs: record.reference_inputs, engine:record.result?.engine, units:record.result?.units, solver:record.result?.solver, scope:record.result?.scope, source_created_at: record.source_created_at }, null, 2));
    configPanel.append(summary, pre); metadata.append(configPanel);
    actions.replaceChildren(); actions.hidden = false;
    if (record.config && record.backend) actions.append(button(`Load ${record.backend === 'math' ? 'mathematical' : record.backend === 'pymunk' ? '2D physics' : 'detailed linkage'} profile`, () => safe(() => onLoadProfile(record, record.backend))));
    if (record.config && ['pymunk','math'].includes(record.backend)) actions.append(button('Show Pymunk visual GUI', () => safe(() => onPymunk(record))));
    if(record.result?.study_settings)actions.append(button('Restore motion study settings',()=>safe(()=>onLoadStudy(record))));
    actions.append(button('Download JSON', () => downloadJSON(record, record.name + '.json')));
    const tables = record.result ? extractTables(record.result) : [];
    [controls, channelBox, chart, tableCaption, tableHolder].forEach(node => node.hidden = !tables.length);
    if (!tables.length) { if (window.Plotly) window.Plotly.purge(chart); return; }
    const cases = element('select'); cases.setAttribute('aria-label', 'Recorded table');
    tables.forEach((table, index) => { const option = element('option', `${table.name} · ${table.rows.length.toLocaleString()} samples`); option.value = index; cases.append(option); });
    cases.addEventListener('change', () => { tableIndex = Number(cases.value); selectedChannels = []; plotRevision++; updateTable(); });
    controls.replaceChildren(field('Recorded table', cases), button('Download complete table CSV', () => csvDownload(normalizedRows, `${record.name}-${tables[tableIndex].name}`)), button('Reset plot view', () => { plotRevision++; plot(); }));
    updateTable();
  }

  function updateTable() {
    const tables = extractTables(selected.result), rows = tables[tableIndex].rows;
    normalizedRows = rows.map(numericRow);
    channels = [...new Set(normalizedRows.flatMap(row => Object.keys(row)))];
    xChannel = channels.includes('t') ? 't' : channels.includes('time') ? 'time' : '$sample';
    const available = channels.filter(key => key !== xChannel);
    const preferred = ['input_mm', 'position_actual_mm', 'chassis_displacement_mm', 'theta_deg', 'q', 'driver_force'];
    selectedChannels = preferred.filter(key => available.includes(key)).slice(0, 3);
    if (!selectedChannels.length) selectedChannels = available.slice(0, 2);
    channelBox.replaceChildren(element('legend', 'Plot channels · units retained from source data'));
    const xSelect = element('select'); xSelect.setAttribute('aria-label', 'Plot horizontal channel');
    for (const key of ['$sample', ...channels]) { const option = element('option', key === '$sample' ? 'Sample index' : key); option.value = key; option.selected = key === xChannel; xSelect.append(option); }
    xSelect.addEventListener('change', () => { xChannel = xSelect.value; plotRevision++; plot(); });
    channelBox.append(field('Horizontal axis', xSelect));
    for (const key of channels) {
      const check = element('input'); check.type = 'checkbox'; check.value = key; check.checked = selectedChannels.includes(key);
      check.addEventListener('change', () => { if (check.checked) selectedChannels.push(key); else selectedChannels = selectedChannels.filter(channel => channel !== key); plot(); sampleTable(); });
      const label = element('label'); label.append(check, document.createTextNode(key)); channelBox.append(label);
    }
    plot(); sampleTable();
  }

  function plot() {
    if (!selected?.result || chart.hidden) return;
    if (!window.Plotly) { report('Plotly is unavailable. JSON/CSV downloads remain available.'); return; }
    const css = getComputedStyle(root), color = name => css.getPropertyValue(name).trim();
    const colors = ['--blue', '--orange', '--purple', '--red'].map(color);
    const traces = selectedChannels.map((key, index) => ({
      type: 'scatter', mode: 'lines', name: key,
      x: normalizedRows.map((row, i) => xChannel === '$sample' ? i : row[xChannel] ?? null), y: normalizedRows.map(row => row[key] ?? null),
      line: { color: colors[index % colors.length], width: 1.8 }, connectgaps: false,
      hovertemplate: `${key.replace(/[<>&]/g, '')}: %{y:.6g}<br>${xChannel === '$sample' ? 'Sample' : xChannel.replace(/[<>&]/g, '')}: %{x:.6g}<extra></extra>`,
    }));
    window.Plotly.react(chart, traces, {
      title: { text: 'Recorded data', font: { size: 16 } },
      paper_bgcolor: color('--panel') || (currentTheme === 'dark' ? '#18212d' : '#fff'), plot_bgcolor: color('--panel') || 'transparent',
      font: { color: color('--text') || (currentTheme === 'dark' ? '#e5edf6' : '#233047'), size: 12 },
      xaxis: { title: { text: xChannel === '$sample' ? 'Sample index' : xChannel }, gridcolor: color('--line'), automargin: true },
      yaxis: { title: { text: 'Source values · inspect channel units' }, gridcolor: color('--line'), automargin: true },
      margin: { l: 65, r: 25, t: 55, b: 65 }, height: 400, hovermode: 'x unified', dragmode: 'zoom',
      legend: { orientation: 'h', y: -0.25 }, uirevision: `${selected.id}-${tableIndex}-${plotRevision}`,
      annotations: traces.length ? [] : [{ text: 'Select one or more numeric channels', x: 0.5, y: 0.5, xref: 'paper', yref: 'paper', showarrow: false }],
    }, { responsive: true, scrollZoom: true, displaylogo: false, toImageButtonOptions: { filename: 'motion-study', format: 'png', scale: 2 } }).catch(report);
  }

  function sampleTable() {
    const columns = [...new Set([...(xChannel === '$sample' ? [] : [xChannel]), ...selectedChannels])];
    tableCaption.textContent = `Previewing the first ${Math.min(12, normalizedRows.length)} of ${normalizedRows.length.toLocaleString()} recorded samples. CSV retains the complete numeric table; JSON retains all source fields.`;
    tableHolder.replaceChildren();
    const table = element('table'), head = element('thead'), header = element('tr'), body = element('tbody');
    header.append(element('th', '#')); columns.forEach(key => header.append(element('th', key))); head.append(header);
    normalizedRows.slice(0, 12).forEach((row, index) => { const tr = element('tr'); tr.append(element('td', index)); columns.forEach(key => tr.append(element('td', row[key] === undefined ? '—' : Number(row[key]).toPrecision(6)))); body.append(tr); });
    table.append(head, body); tableHolder.append(table);
  }

  void refresh();
  return {
    refresh,
    setTheme(next) { currentTheme = next; plot(); },
    async select(id) { await safe(() => selectRecord(id)); },
  };
}
