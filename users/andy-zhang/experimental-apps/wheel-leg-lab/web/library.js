/** Browser-local motion study library. Import this ES module from the lab shell.
 * Inputs: JSON configs/results in each backend's documented units (Jonathan uses mm/deg).
 * Outputs: append-only IndexedDB records, lightweight summaries and explicit JSON downloads.
 * Limits: this browser/origin only; no server synchronization, deletion or physics validation.
 */
export const RECORD_SCHEMA = 'wheel-leg-lab-record/v1';
export const MAX_IMPORT_BYTES = 80 * 1024 * 1024;
const BACKENDS = ['math', 'pymunk', 'linkage', 'counterbalance_math', 'counterbalance_pymunk','inversion_math','inversion_pymunk','jon_v2'];
const FORBIDDEN = new Set(['__proto__', 'prototype', 'constructor']);
let databasePromise;

const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
/** Resolve an explicit saved inversion profile without modifying its original JSON.
 * Pre-correction exports have no routing marker and reproduce the prior rim route.
 * Fresh server defaults/session edits use central_wrap. Old recorded frames stay intact.
 */
export function resolveInversionProfile(config) {
  return {...config,rope_routing:config.rope_routing ?? 'outer_rim',angle_limit_enabled:config.angle_limit_enabled ?? false};
}
function checkedJSON(value) {
  let nodes = 0;
  function visit(item, depth) {
    if (++nodes > 5000000 || depth > 28) throw new Error('JSON is too large or deeply nested.');
    if (typeof item === 'number' && !Number.isFinite(item)) throw new Error('All numeric values must be finite.');
    if (item === null || ['number', 'boolean', 'string'].includes(typeof item)) return;
    if (typeof item !== 'object') throw new Error('Only JSON values are supported.');
    for (const [key, child] of Object.entries(item)) {
      if (FORBIDDEN.has(key)) throw new Error(`Unsafe JSON key: ${key}.`);
      visit(child, depth + 1);
    }
  }
  visit(value, 0);
  const text = JSON.stringify(value);
  if (new TextEncoder().encode(text).length > MAX_IMPORT_BYTES) throw new Error('JSON exceeds the 80 MiB import limit.');
  return JSON.parse(text);
}

/** Flatten numeric scalars/arrays for plotting; retain original JSON separately. */
export function numericRow(row) {
  const out = {};
  function visit(value, path, depth) {
    if (typeof value === 'number' && Number.isFinite(value)) out[path] = value;
    else if (value !== null && typeof value === 'object' && depth < 8) {
      for (const [key, child] of Object.entries(value)) visit(child, path ? `${path}.${key}` : key, depth + 1);
    }
  }
  visit(row, '', 0);
  return out;
}

/** Discover ordinary rows, linkage samples and mode comparisons without inventing units. */
export function extractTables(result) {
  const tables = [];
  function inspect(value, label, depth) {
    if (depth > 5 || value === null || typeof value !== 'object') return;
    if (Array.isArray(value)) {
      if (value.length && value.every(object)) {
        const modes=[...new Set(value.map(row=>row.mode).filter(mode=>typeof mode==='string'))];
        if(modes.length>1&&value.every(row=>typeof row.mode==='string'))
          for(const mode of modes)tables.push({name:mode,rows:value.filter(row=>row.mode===mode)});
        else tables.push({name:label||'Recorded samples',rows:value});
      }
      return;
    }
    for (const key of ['rows', 'samples', 'history', 'trace']) {
      if (Array.isArray(value[key])) { inspect(value[key], label || 'Recorded samples', depth + 1); return; }
    }
    for (const key of ['passive', 'ideal', 'finite', 'cases', 'results', 'result']) {
      if (value[key]) {
        if (key === 'cases' || key === 'results') for (const [name, child] of Object.entries(value[key])) inspect(child, name, depth + 1);
        else inspect(value[key], ['passive', 'ideal', 'finite'].includes(key) ? key : label, depth + 1);
      }
    }
  }
  inspect(result, '', 0);
  return tables;
}

function validateTables(result) {
  const tables = extractTables(result);
  if (!tables.length) throw new Error('Run JSON needs a nonempty rows or samples table.');
  let count = 0;
  for (const table of tables) {
    count += table.rows.length;
    if (count > 250001) throw new Error('At most 250,001 total samples can be imported.');
    if (table.rows.some(row => !object(row))) throw new Error('Every sample must be a JSON object.');
    if (!table.rows.some(row => Object.keys(numericRow(row)).length)) throw new Error('Samples need at least one numeric channel.');
    for (const row of table.rows) {
      for (const key of ['t', 'time']) if (key in row && typeof row[key] !== 'number') throw new Error(`Sample ${key} must be a finite number.`);
    }
  }
  return tables;
}

function inferredBackend(value, config) {
  if (value.backend !== undefined && value.backend !== null) {
    if (!BACKENDS.includes(value.backend)) throw new Error('Unknown model backend.');
    return value.backend;
  }
  if (object(config?.geometry) && object(config?.simulation)) return 'linkage';
  if(['dual_rope','knee_bellcrank'].includes(config?.preset)&&typeof config?.femur_torque==='number')return 'inversion_pymunk';
  if (typeof config?.spring_radius==='number' && typeof config?.anchor_height==='number' && typeof config?.law==='string') return 'counterbalance_math';
  if (typeof config?.length === 'number' && typeof config?.target === 'string') return 'pymunk';
  return null;
}

/** Validate imported envelopes, historical config exports, raw results or row-only datasets.
 * Dataset-only JSON cannot be loaded into a solver. Solver-specific config checks run on load.
 */
export function normalizeImport(input, fileName = 'Imported study') {
  let value = checkedJSON(input);
  if (!Array.isArray(value) && !object(value)) throw new Error('Import a JSON object or an array of recorded samples.');
  if(['general-vsl/v1-kinematics','general-vsl/v2-quasi-static'].includes(value.schema))value={backend:'jon_v2',config:value,name:fileName.replace(/\.json$/i,'')};
  if (value.schema !== undefined && ![RECORD_SCHEMA,'wheel-leg-lab-profile/v1','motion-lab-linkage-run','motion-lab-study/v1'].includes(value.schema)) throw new Error('Unsupported record schema.');
  if (value.schema==='motion-lab-linkage-run' && value.version!==1) throw new Error('Unsupported linkage run version.');
  if(value.schema==='motion-lab-study/v1'){
    if(!object(value.study_settings)||!Array.isArray(value.study_settings.controls))throw new Error('Study JSON needs its control settings.');
    const values=Object.fromEntries(value.study_settings.controls.filter(control=>control.id&&typeof control.value!=='object'&&Number.isFinite(Number(control.value))).map(control=>[control.id,Number(control.value)]));
    value={name:value.name,result:{...value,rows:value.rows?.length?value.rows:[values]}};
  }
  // MATLAB jsonencode emits numeric columns rather than row objects. Preserve
  // the original columns and expose a row view for the common data browser.
  if (value.backend==='matlab-ode45') {
    const times=value.t;
    if (!Array.isArray(times)||!times.length||!times.every(Number.isFinite)) throw new Error('MATLAB output needs a finite t column.');
    const columns=Object.entries(value).filter(([,column])=>Array.isArray(column)&&column.length===times.length&&column.every(Number.isFinite));
    const rows=times.map((_,i)=>Object.fromEntries(columns.map(([key,column])=>[key,column[i]])));
    value={backend:'math',config:value.config,name:value.name||fileName.replace(/\.json$/i,''),result:{...value,backend:'math',source_backend:'matlab-ode45',engine:'MATLAB ode45',rows}};
  }
  let config = Array.isArray(value) ? null : (value.config ?? value.result?.config ?? null);
  if (config !== null && (!object(config) || !Object.keys(config).length)) throw new Error('Config must be a nonempty JSON object.');
  const backend = inferredBackend(value, config);
  let result = Array.isArray(value) ? { rows: value } : value.result;
  if (result === undefined && extractTables(value).length) result = value;
  const hasData = result !== undefined && result !== null;
  if (hasData) validateTables(result);
  if (!config && !hasData) {
    // Older detailed-linkage exports may contain the config directly.
    if (object(value.geometry) && object(value.simulation)) config = value;
    else throw new Error('JSON contains neither a configuration nor recorded samples.');
  }
  const selectedBackend = backend || inferredBackend(value, config);
  if (config && !selectedBackend) throw new Error('Configuration backend is missing; set backend to math, pymunk or linkage.');
  if (config && selectedBackend === 'linkage' && (!object(config.geometry) || !object(config.simulation))) throw new Error('Linkage profiles need geometry and simulation objects.');
  if (config && ['pymunk', 'math'].includes(selectedBackend)) {
    for (const key of ['length', 'radius']) if (typeof config[key] !== 'number' || config[key] <= 0) throw new Error(`${key} must be a positive number in metres.`);
    if (typeof config.target !== 'string' || !['position', 'force', 'knee'].includes(config.target)) throw new Error('Config target must be position, force or knee.');
    if (config.dt !== undefined && (typeof config.dt !== 'number' || config.dt <= 0)) throw new Error('Solver dt must be positive seconds.');
    if (config.duration !== undefined && (typeof config.duration !== 'number' || config.duration <= 0)) throw new Error('Duration must be positive seconds.');
  }
  if(config&&['counterbalance_math','counterbalance_pymunk'].includes(selectedBackend)){
    for(const key of ['length','spring_radius','anchor_height'])if(typeof config[key]!=='number'||config[key]<=0)throw new Error(`Counterbalance ${key} must be positive metres.`);
    if(config.spring_radius>config.length)throw new Error('Spring radius must fit on the counterbalance lever.');
    if(!['zero_effective','ordinary'].includes(config.law))throw new Error('Counterbalance law must be zero_effective or ordinary.');
    if(!['prescribed','free','force'].includes(config.mode))throw new Error('Counterbalance mode must be prescribed, free or force.');
    for(const key of ['dt','duration'])if(config[key]!==undefined&&(typeof config[key]!=='number'||config[key]<=0))throw new Error(`Counterbalance ${key} must be positive seconds.`);
    if(config.stiffness_auto!==undefined&&typeof config.stiffness_auto!=='boolean')throw new Error('Automatic counterbalance stiffness must be boolean.');
  }
  if(config&&selectedBackend?.startsWith('inversion_')){
    if(!['dual_rope','knee_bellcrank'].includes(config.preset))throw Error('Unknown invertible suspension preset.');
    if(!['ground','hip_fixed'].includes(config.fixture))throw Error('Unknown inversion fixture.');
    if(config.rope_routing!==undefined&&!['central_wrap','central_face','outer_rim'].includes(config.rope_routing))throw Error('Unknown inversion rope routing.');
    for(const key of ['length','radius','dt','duration'])if(typeof config[key]!=='number'||config[key]<=0)throw Error('Inversion '+key+' must be positive SI.');
  }
  if(config&&selectedBackend==='jon_v2'){
    if(!['general-vsl/v1-kinematics','general-vsl/v2-quasi-static'].includes(config.schema)||!object(config.parameters))throw Error('Jonathan profiles need original v1/v2 parameter JSON.');
    const p=config.parameters;
    for(const key of ['L2','L3','ra','rb','rc','rd','re','rf','rw'])if(typeof p[key]!=='number'||p[key]<=0)throw Error('Jonathan '+key+' must be positive millimetres.');
    for(const [key,min,max] of [['alpha',0,45],['phi0',0,30],['te',90,180],['tc',90,180]])if(typeof p[key]!=='number'||p[key]<min||p[key]>max)throw Error('Invalid Jonathan '+key+' angle in degrees.');
    if(p.te>p.tc)throw Error('Jonathan extension must be no greater than compression.');
    for(const key of ['m1','m2','m3','m5','m6','g','Tab0','Tcd0','Tef0'])if(p[key]!==undefined&&(typeof p[key]!=='number'||p[key]<0))throw Error('Jonathan '+key+' must be nonnegative.');
    if(p.r5I!==undefined&&(typeof p.r5I!=='number'||p.r5I<=0))throw Error('Jonathan effective inertia radius must be positive millimetres.');
    if(p.loadMode!==undefined&&!['nt','yz'].includes(p.loadMode))throw Error('Unknown Jonathan force convention.');
    for(const key of ['Fn','Ft','Fy','Fz'])if(p[key]!==undefined&&typeof p[key]!=='number')throw Error('Jonathan forces must be numbers in newtons.');
    if(p.beta!==undefined&&(typeof p.beta!=='number'||p.beta<0||p.beta>90))throw Error('Jonathan beta must be 0–90 degrees.');
    if(config.theta2!==undefined&&typeof config.theta2!=='number')throw Error('Jonathan current angle must be a number.');
    // The original model performs complete window/driven/belt checks when loading.
  }
  const kind = config ? (hasData ? 'run' : 'profile') : 'dataset';
  if (value.kind && !['profile', 'run', 'dataset'].includes(value.kind)) throw new Error('Unknown record kind.');
  if (value.kind === 'run' && !hasData) throw new Error('A run record must include recorded samples.');
  if (value.kind === 'profile' && hasData) throw new Error('A profile must contain config only; use kind run for samples.');
  if (value.kind === 'dataset' && config) throw new Error('Dataset-only records cannot contain a runnable configuration.');
  const name = String(value.name || fileName.replace(/\.json$/i, '') || 'Imported study').trim().slice(0, 160);
  const record = { schema: RECORD_SCHEMA, kind, name: name || 'Imported study', backend: config ? selectedBackend : null, config };
  if (hasData) record.result = result;
  if (value.reference_inputs !== undefined) record.reference_inputs = value.reference_inputs;
  if (typeof value.created_at === 'string' && Number.isFinite(Date.parse(value.created_at))) record.source_created_at = value.created_at;
  return record;
}

function openDatabase() {
  if (!databasePromise) databasePromise = new Promise((resolve, reject) => {
    if (!globalThis.indexedDB) { reject(new Error('IndexedDB is unavailable in this browser. JSON downloads still work.')); return; }
    const request = indexedDB.open('wheel-leg-lab-library', 1);
    request.onupgradeneeded = () => {
      request.result.createObjectStore('records', { keyPath: 'id' });
      request.result.createObjectStore('summaries', { keyPath: 'id' });
    };
    request.onsuccess = () => { request.result.onversionchange = () => { request.result.close(); databasePromise = null; }; resolve(request.result); };
    request.onerror = () => { databasePromise = null; reject(new Error(`Could not open browser library: ${request.error?.message || 'storage denied'}`)); };
    request.onblocked = () => reject(new Error('Library upgrade is blocked by another tab. Close the older tab and retry.'));
  });
  return databasePromise;
}

function requestValue(request) {
  return new Promise((resolve, reject) => { request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error); });
}

/** Append a new record; imported IDs never overwrite existing profiles or runs. */
export async function saveRecord(input) {
  const record = normalizeImport(input, input.name || 'Saved study');
  record.id = globalThis.crypto?.randomUUID?.() || `study-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  record.created_at = new Date().toISOString();
  const tables = record.result ? extractTables(record.result) : [];
  const summary = { id: record.id, name: record.name, kind: record.kind, backend: record.backend, created_at: record.created_at, sample_count: tables.reduce((sum, table) => sum + table.rows.length, 0), tables: tables.map(table => table.name) };
  const db = await openDatabase();
  await new Promise((resolve, reject) => {
    const transaction = db.transaction(['records', 'summaries'], 'readwrite');
    transaction.objectStore('records').add(record);
    transaction.objectStore('summaries').add(summary);
    transaction.oncomplete = resolve;
    transaction.onabort = transaction.onerror = () => reject(new Error(`Browser library could not save this study: ${transaction.error?.message || 'storage quota or permission error'}. Download JSON to retain it.`));
  });
  return record;
}

export async function listRecords() {
  const db = await openDatabase();
  const records = await requestValue(db.transaction('summaries').objectStore('summaries').getAll());
  return records.sort((a, b) => b.created_at.localeCompare(a.created_at));
}

export async function getRecord(id) {
  const db = await openDatabase();
  return requestValue(db.transaction('records').objectStore('records').get(id));
}

export function downloadJSON(value, name = 'motion-study.json', {compact=false} = {}) {
  const data = JSON.stringify(value, null, compact?0:2);
  const url = URL.createObjectURL(new Blob([data], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url; link.download = name.replace(/[<>:"/\\|?*\x00-\x1f]/g, '-'); link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
