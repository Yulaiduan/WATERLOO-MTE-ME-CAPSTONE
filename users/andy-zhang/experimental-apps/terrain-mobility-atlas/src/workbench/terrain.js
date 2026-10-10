/** Terrain inputs are SI. Presets are engineering assumptions, not biome measurements. */
const CHAT_SOURCE = 'https://chatgpt.com/c/6abb5d6d-029c-83ea-8d0d-cab0e6a3ef19';
const USFS_SOURCE = 'https://www.fs.usda.gov/eng/pubs/pdfpubs/pdf11232804/pdf11232804dpi100.pdf';
export const TERRAIN_PRESETS = [
  ['road', 'Improved road', .005, 3, .01, 50, 1],
  ['gravel', 'Gravel / service road', .02, .5, .05, 10, 3],
  ['maintained', 'Maintained natural trail', .04, 1, .1, 5, 8],
  ['primitive', 'Primitive trail', .08, .7, .2, 2, 15],
  ['boreal', 'Boreal forest / Canadian Shield', .1, .6, .25, 1.5, 10],
  ['alpine', 'Alpine / scree', .13, .5, .3, 1, 20],
  ['talus', 'Talus / boulder field', .2, .4, .4, .5, 20],
].map(([id, label, roughnessRmsM, wavelengthM, obstacleHeightM, obstacleSpacingM, gradePercent]) => ({
  id, label, defaults: { roughnessRmsM, wavelengthM, obstacleHeightM, obstacleSpacingM, gradePercent, obstacleWidthM: .3 },
  evidence: {
    roughnessRmsM: { type: 'illustrative design preset', source: CHAT_SOURCE, scale: 'sine component only' },
    wavelengthM: { type: 'illustrative design preset', source: CHAT_SOURCE },
    obstacleHeightM: { type: 'illustrative design preset', source: CHAT_SOURCE },
    obstacleSpacingM: { type: 'illustrative design preset', source: CHAT_SOURCE },
    gradePercent: { type: 'engineering assumption', source: 'chosen test grade within synthesized terrain envelope' },
    obstacleWidthM: { type: 'engineering assumption', source: 'chosen Gaussian full width at half maximum' },
  },
}));
export const DEFAULT_TERRAIN_CONFIG = { presetId: 'maintained', mode: 'periodic', lengthM: 100, stepM: .01,
  ...TERRAIN_PRESETS[2].defaults, seed: 42 };
const MAX_SAMPLES = 200001;
function number(value, name, min, max = Infinity) {
  if (!Number.isFinite(value) || value < min || value > max) throw new Error(`${name} must be finite and between ${min} and ${max}.`);
  return value;
}
function statistics(samples) {
  const n = samples.length;
  let mean = 0, squares = 0, minGrade = Infinity, maxGrade = -Infinity, events = 0, minStepM = Infinity;
  for (let i = 0; i < n; i++) {
    mean += samples[i].roughness; squares += samples[i].roughness ** 2;
    if (i) {
      minStepM = Math.min(minStepM, samples[i].x - samples[i - 1].x);
      const grade = 100 * (samples[i].z - samples[i - 1].z) / (samples[i].x - samples[i - 1].x);
      minGrade = Math.min(minGrade, grade); maxGrade = Math.max(maxGrade, grade);
    }
    if (i > 0 && i < n - 1 && samples[i].obstacle > 1e-8 && samples[i].obstacle > samples[i - 1].obstacle && samples[i].obstacle >= samples[i + 1].obstacle) events++;
  }
  const lengthM = samples[n - 1].x - samples[0].x;
  return { lengthM, sampleCount: n, minStepM,
    netElevationM: samples[n - 1].z - samples[0].z,
    meanGradePercent: 100 * (samples[n - 1].z - samples[0].z) / lengthM,
    realizedRoughnessRmsM: Math.sqrt(Math.max(0, squares / n - (mean / n) ** 2)),
    minGradePercent: minGrade, maxGradePercent: maxGrade, obstacleCount: events };
}
function checkedSamples(samples) {
  if (!Array.isArray(samples) || samples.length < 2 || samples.length > MAX_SAMPLES) throw new Error(`Terrain requires 2–${MAX_SAMPLES} samples.`);
  return samples.map((s, i) => {
    const x = number(s.x, `Distance at sample ${i + 1}`, 0);
    const z = number(s.z, `Elevation at sample ${i + 1}`, -1e6, 1e6);
    if (i && x <= samples[i - 1].x) throw new Error(`Distance must increase strictly; sample ${i + 1} is invalid.`);
    const baseline = s.baseline ?? z, roughness = s.roughness ?? 0, obstacle = s.obstacle ?? 0;
    [baseline, roughness, obstacle].forEach(v => number(v, 'Terrain component', -1e6, 1e6));
    if (Math.abs(z - baseline - roughness - obstacle) > 1e-4) throw new Error(`Terrain layers do not sum to elevation at sample ${i + 1}.`);
    return { x, z, baseline, roughness, obstacle };
  });
}
function randomGenerator(seed) {
  let t = seed >>> 0;
  return () => { t += 0x6D2B79F5; let r = Math.imul(t ^ t >>> 15, 1 | t); r ^= r + Math.imul(r ^ r >>> 7, 61 | r); return ((r ^ r >>> 14) >>> 0) / 4294967296; };
}
function class3Baseline(x) {
  const cycles = Math.floor(x / 100), s = x - cycles * 100;
  // 8% base; 5 m half-cosine up, 20 m plateau, 5 m down. 12.25 m / 100 m.
  function integral(t) {
    if (t <= 35) return 0;
    if (t < 40) { const u = t - 35; return .17 * (u / 2 - 5 / (2 * Math.PI) * Math.sin(Math.PI * u / 5)); }
    if (t <= 60) return .17 * (2.5 + t - 40);
    if (t < 65) { const u = t - 60; return .17 * (22.5 + u / 2 + 5 / (2 * Math.PI) * Math.sin(Math.PI * u / 5)); }
    return 4.25;
  }
  return cycles * 12.25 + .08 * s + integral(s);
}
export function buildTerrain(config = {}) {
  const preset = TERRAIN_PRESETS.find(p => p.id === (config.presetId ?? DEFAULT_TERRAIN_CONFIG.presetId));
  if (!preset) throw new Error('Unknown terrain preset.');
  const c = { ...DEFAULT_TERRAIN_CONFIG, ...preset.defaults, ...config };
  if (c.mode === 'measured') {
    const supplied = c.samples ?? c.terrain?.samples;
    const samples = checkedSamples(supplied);
    const end = samples[0].x + (config.lengthM ?? samples.at(-1).x - samples[0].x);
    if (end > samples.at(-1).x + 1e-8) throw new Error('Requested measured window exceeds available source distance.');
    const cropped = samples.filter(s => s.x <= end + 1e-9);
    if (end < samples.at(-1).x && cropped.length && Math.abs(cropped.at(-1).x - end) > 1e-9) {
      const left = cropped.at(-1), right = samples[cropped.length], f = (end - left.x) / (right.x - left.x);
      cropped.push({ x: end, ...Object.fromEntries(['z', 'baseline', 'roughness', 'obstacle'].map(k => [k, left[k] + f * (right[k] - left[k])])) });
    }
    if (cropped.length < 2) throw new Error('Requested measured window contains fewer than two samples.');
    const incomingMetadata = c.terrain?.metadata ?? c.metadata ?? {};
    return { samples: cropped, summary: { ...statistics(cropped), realizedRoughnessRmsM: incomingMetadata.layersProvided ? statistics(cropped).realizedRoughnessRmsM : null }, metadata: { ...incomingMetadata,
      mode: 'measured', evidenceType: incomingMetadata.evidenceType ?? 'imported profile; source supplied by user', sourceResolutionM: c.sourceResolutionM ?? c.terrain?.metadata?.sourceResolutionM ?? c.metadata?.sourceResolutionM ?? null,
      assumptions: ['Replays source-scale elevation. Interpolation cannot create unresolved roots or rocks.'], units: 'SI' } };
  }
  if (!['periodic', 'stochastic', 'class3'].includes(c.mode)) throw new Error('Unknown terrain generation mode.');
  number(c.lengthM, 'Route length (m)', .01, 1000); number(c.stepM, 'Sample spacing (m)', .001, 10);
  number(c.gradePercent, 'Grade (%)', -100, 100); number(c.roughnessRmsM, 'Roughness RMS (m)', 0, 1);
  number(c.wavelengthM, 'Wavelength (m)', .02, 1000); number(c.obstacleHeightM, 'Obstacle height (m)', 0, 2);
  number(c.obstacleSpacingM, 'Obstacle spacing (m)', .02, 1000); number(c.obstacleWidthM, 'Obstacle width (m)', .01, 100);
  number(c.seed, 'Random seed', 0, 4294967295);
  if (c.obstacleWidthM / c.obstacleSpacingM > 20) throw new Error('Obstacle width exceeds 20 times spacing; reduce overlap for a bounded profile generation.');
  const count = Math.ceil(c.lengthM / c.stepM) + 1;
  if (count > MAX_SAMPLES) throw new Error(`Too many terrain samples. Increase spacing to keep at most ${MAX_SAMPLES}.`);
  if (c.stepM > Math.min(c.wavelengthM / 12, c.obstacleWidthM / 8) && (c.roughnessRmsM > 0 || c.obstacleHeightM > 0)) throw new Error('Spacing is too coarse: use at least 12 samples per wavelength and 8 per obstacle width.');
  // A fixed seeded Fourier realization, normalized by coefficients, independent of crop length.
  const rng = randomGenerator(c.seed), waves = Array.from({ length: 24 }, () => ({
    phase: rng() * 2 * Math.PI, length: c.wavelengthM * (0.5 + rng() * 1.5), weight: .5 + rng(),
  }));
  const norm = Math.sqrt(waves.reduce((sum, w) => sum + w.weight ** 2 / 2, 0));
  const obstacles = [];
  if (c.mode === 'stochastic') {
    let x = c.obstacleSpacingM;
    while (x < 1000 + 3 * c.obstacleWidthM) { obstacles.push({ x, h: c.obstacleHeightM * (.5 + rng()) }); x += c.obstacleSpacingM * (.5 + rng()); }
  }
  const sigma = c.obstacleWidthM / (2 * Math.sqrt(2 * Math.log(2))), samples = [];
  let cursor = 0;
  for (let i = 0; i < count; i++) {
    const x = Math.min(c.lengthM, i * c.stepM), baseline = c.mode === 'class3' ? class3Baseline(x) : x * c.gradePercent / 100;
    const roughness = c.mode === 'stochastic' ? c.roughnessRmsM * waves.reduce((sum, w) => sum + w.weight * Math.sin(2 * Math.PI * x / w.length + w.phase), 0) / norm : Math.SQRT2 * c.roughnessRmsM * Math.sin(2 * Math.PI * x / c.wavelengthM);
    let obstacle = 0;
    if (c.mode === 'stochastic') {
      while (cursor < obstacles.length && obstacles[cursor].x < x - 6 * sigma) cursor++;
      for (let k = cursor; k < obstacles.length && obstacles[k].x <= x + 6 * sigma; k++) obstacle += obstacles[k].h * Math.exp(-.5 * ((x - obstacles[k].x) / sigma) ** 2);
    } else {
      const nearest = Math.round(x / c.obstacleSpacingM);
      for (let k = Math.max(1, nearest - Math.ceil(6 * sigma / c.obstacleSpacingM)); k <= nearest + Math.ceil(6 * sigma / c.obstacleSpacingM); k++) obstacle += c.obstacleHeightM * Math.exp(-.5 * ((x - k * c.obstacleSpacingM) / sigma) ** 2);
    }
    samples.push({ x, z: baseline + roughness + obstacle, baseline, roughness, obstacle });
  }
  const obstacleCount = c.obstacleHeightM === 0 ? 0 : c.mode === 'stochastic' ? obstacles.filter(o => o.x <= c.lengthM + 1e-9).length : Math.floor((c.lengthM + 1e-9) / c.obstacleSpacingM);
  const roughnessCycles = c.mode === 'stochastic' ? null : c.roughnessRmsM > 0 ? c.lengthM / c.wavelengthM : 0;
  const gradeCycles = c.mode === 'class3' ? c.lengthM / 100 : 0;
  const cycles = c.mode === 'class3' ? gradeCycles : roughnessCycles;
  const evidence = Object.fromEntries(Object.entries(preset.evidence).map(([key, sourceEvidence]) => [key, {
    ...sourceEvidence, sourcePresetValue: preset.defaults[key], selectedValue: c[key],
    ...(c[key] !== preset.defaults[key] ? { type: 'engineering assumption', selection: 'user override of illustrative preset', sourceEvidenceType: sourceEvidence.type } : { selection: 'illustrative preset value' }),
  }]));
  if (c.mode === 'class3') evidence.gradePercent = { type: 'engineering assumption', source: USFS_SOURCE,
    selectedValue: 8, benchmarkTargetGradePercent: [5, 15], benchmarkShortPitchMaxPercent: 25,
    selection: 'chosen 8% baseline, 100m cycle, 20m plateau and 5m transitions; historical guideline supplies limits, not cycle statistics' };
  return { samples, summary: { ...statistics(samples), obstacleCount, requestedRoughnessRmsM: c.roughnessRmsM, cycles, roughnessCycles, gradeCycles }, metadata: {
    mode: c.mode, presetId: preset.id, presetLabel: preset.label, config: c, evidenceType: 'synthetic engineering test', evidence,
    source: c.mode === 'class3' ? USFS_SOURCE : CHAT_SOURCE, units: 'SI', seed: c.mode === 'stochastic' ? c.seed : null,
    assumptions: [c.mode === 'class3' ? 'Historical USFS Class 3 limits; 100 m cycle, 8% base, 20 m at 25%, 5 m transitions are chosen assumptions.' : 'Preset values are illustrative test points, not measured biome averages.',
      'Gaussian obstacle width is an assumption. Layers add; total height and slope may exceed each layer.',
      c.mode === 'stochastic' ? 'Seeded 24-component band-limited realization, 0.5–2 times selected wavelength; no fitted natural distribution. One master realization cropped without RMS renormalization.' : 'Single sinusoidal roughness concentrates excitation at one spatial frequency.'],
    roughnessStatistic: 'Population RMS of separate roughness layer about its mean; excludes baseline and obstacles.',
    gradeStatistic: 'Adjacent-sample finite difference of total surface; not guideline macro grade.',
    obstacleStatistic: 'Count of declared obstacle centres within route including endpoint; adjacent overlapping Gaussians may not have distinct visible peaks.',
    cycleStatistic: c.mode === 'class3' ? 'cycles counts the 100m grade cycle; roughnessCycles separately counts any added sine layer.' : c.mode === 'stochastic' ? 'No single periodic cycle; cycles and roughnessCycles unknown (null).' : 'cycles counts the sine roughness layer only; zero when that layer is disabled.',
  } };
}
function csvRows(text) {
  if (typeof text !== 'string' || text.length > 35e6) throw new Error('CSV input must be text smaller than 35 MB.');
  const rows = []; let row = [], cell = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (ch === '"') { if (quoted && text[i + 1] === '"') { cell += '"'; i++; } else quoted = !quoted; }
    else if (!quoted && (ch === ',' || ch === '\n')) { row.push(cell.trim()); cell = ''; if (ch === '\n') { if (row.some(Boolean)) rows.push(row); row = []; } }
    else if (ch !== '\r') cell += ch;
    if (rows.length > MAX_SAMPLES + 1) throw new Error('CSV exceeds row limit.');
  }
  if (quoted) throw new Error('CSV contains an unterminated quoted value.');
  row.push(cell.trim()); if (row.some(Boolean)) rows.push(row); return rows;
}
export function parseTerrainCsv(text) {
  if (typeof text !== 'string') throw new Error('CSV input must be text.');
  const rows = csvRows(text.replace(/^\uFEFF/, '')); if (rows.length < 3) throw new Error('CSV requires a header and at least two data rows.');
  const header = rows.shift().map(v => v.toLowerCase());
  const index = (...names) => names.map(n => header.indexOf(n)).find(i => i >= 0) ?? -1;
  const xi = index('distance_m', 'x_m', 'x'), zi = index('relative_elevation_m', 'elevation_navd88_m', 'height_m', 'z_m', 'z');
  if (xi < 0 || zi < 0) throw new Error('CSV needs distance_m and relative_elevation_m (or height_m) columns in metres.');
  const bi = index('grade_component_m', 'baseline_m'), ri = index('roughness_component_m', 'roughness_m'), oi = index('obstacle_component_m', 'obstacle_m');
  const hasLayers = [bi, ri, oi].every(i => i >= 0);
  if (!hasLayers && [bi, ri, oi].some(i => i >= 0)) throw new Error('CSV layers must supply baseline, roughness and obstacle together.');
  const read = (row, col, line) => { if (row[col] === undefined || row[col] === '') throw new Error(`Missing numeric value at CSV row ${line}.`); const value = Number(row[col]); if (!Number.isFinite(value)) throw new Error(`Invalid numeric value at CSV row ${line}.`); return value; };
  const samples = checkedSamples(rows.map((row, i) => {
    if (row.length !== header.length) throw new Error(`CSV row ${i + 2} has an incorrect column count.`);
    const x = read(row, xi, i + 2), z = read(row, zi, i + 2);
    return { x, z, baseline: hasLayers ? read(row, bi, i + 2) : z, roughness: hasLayers ? read(row, ri, i + 2) : 0, obstacle: hasLayers ? read(row, oi, i + 2) : 0 };
  }));
  const pi = header.indexOf('provenance'), provenance = pi < 0 ? null : rows[0][pi];
  return { samples, summary: { ...statistics(samples), realizedRoughnessRmsM: hasLayers ? statistics(samples).realizedRoughnessRmsM : null }, metadata: { mode: 'measured', evidenceType: provenance?.startsWith('synthetic') ? 'imported synthetic profile' : 'imported profile; verify source', provenance,
    sourceResolutionM: provenance?.startsWith('USGS_3DEP_1m') ? 1 : null, units: 'SI', layersProvided: hasLayers,
    assumptions: ['Source numeric values preserved; interpolation adds no source detail.', ...(!hasLayers ? ['Entire source elevation assigned to baseline; fine roughness is unknown, not measured as zero.'] : [])] } };
}
export function serializeTerrainCsv(terrain) {
  const samples = checkedSamples(terrain.samples);
  // Absent fine layers remain unknown through CSV round trips. Zero-valued layer
  // columns would falsely turn source-scale elevation into a measured smooth surface.
  if (terrain.metadata?.layersProvided === false || terrain.summary?.realizedRoughnessRmsM === null) {
    return 'distance_m,relative_elevation_m\n' + samples.map(s => [s.x, s.z].join(',')).join('\n');
  }
  return 'distance_m,relative_elevation_m,grade_component_m,roughness_component_m,obstacle_component_m\n' + samples.map(s => [s.x, s.z, s.baseline, s.roughness, s.obstacle].join(',')).join('\n');
}
