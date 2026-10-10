export const DEFAULT_VEHICLE = { name: 'Scout 01', grade: 25, cross: 15, roughness: 100, obstacle: 200, spacing: 1, corridor: 1.2, surfaces: ['hard', 'mixed'] };
export const VEHICLES = {
  scout: DEFAULT_VEHICLE,
  rover: { name: 'Trail rover', grade: 35, cross: 22, roughness: 150, obstacle: 300, spacing: 0.5, corridor: 1.5, surfaces: ['hard', 'mixed', 'loose'] },
  compact: { name: 'Compact crawler', grade: 40, cross: 25, roughness: 180, obstacle: 350, spacing: 0.3, corridor: 0.9, surfaces: ['hard', 'mixed', 'loose', 'soft'] },
};
export const CONTROLS = [
  { key: 'grade', label: 'Maximum grade', unit: '%', min: 5, max: 60, step: 1, icon: 'slope', hint: 'Symmetric uphill / downhill screening limit.' },
  { key: 'cross', label: 'Maximum cross-slope', unit: '%', min: 3, max: 40, step: 1, icon: 'cross', hint: 'Lateral slope at the assumed driving heading.' },
  { key: 'roughness', label: 'Roughness tolerance', unit: 'mm', min: 10, max: 250, step: 5, icon: 'wave', hint: 'Synthetic RMS residual over a 5 m detrended profile.' },
  { key: 'obstacle', label: 'Obstacle height', unit: 'mm', min: 25, max: 500, step: 5, icon: 'obstacle', hint: 'Assumed perpendicular step capability at low speed.' },
  { key: 'spacing', label: 'Minimum obstacle spacing', unit: 'm', min: 0.2, max: 4, step: 0.1, icon: 'spacing', hint: 'Minimum separation the vehicle requires between obstacles.' },
  { key: 'corridor', label: 'Required corridor', unit: 'm', min: 0.5, max: 2.5, step: 0.05, icon: 'width', hint: 'Vehicle width plus the total lateral clearance allowance.' },
];
export const clone = value => structuredClone(value);
export const format = (value, key) => value == null ? 'Unknown' : ['spacing', 'corridor'].includes(key) ? Number(value).toFixed(2).replace(/0$/, '') : Math.round(value).toString();

export function normalizeVehicle(value) {
  const result = clone(DEFAULT_VEHICLE);
  if (!value || typeof value !== 'object') return result;
  result.name = typeof value.name === 'string' ? value.name.slice(0, 60) : result.name;
  for (const control of CONTROLS) {
    if (Number.isFinite(value[control.key])) result[control.key] = Math.max(control.min, Math.min(control.max, value[control.key]));
  }
  if (Array.isArray(value.surfaces)) result.surfaces = [...new Set(value.surfaces.filter(s => ['hard', 'mixed', 'loose', 'soft'].includes(s)))];
  return result;
}

// Hard constraint evaluation, not a probability or a weighted average.
export function evaluate(terrain, vehicle) {
  const constraints = CONTROLS.map(({ key, label, unit }) => {
    const demand = terrain[key];
    const capacity = vehicle[key];
    if (demand == null) return { key, label, unit, demand, capacity, status: 'unknown', margin: null };
    const inverse = ['spacing', 'corridor'].includes(key);
    const margin = inverse ? (demand - capacity) / demand : (capacity - demand) / capacity;
    return { key, label, unit, demand, capacity, margin, status: margin < -1e-9 ? 'fail' : margin < 0.15 ? 'near' : 'pass' };
  });
  const surface = terrain.surface;
  constraints.push({ key: 'surface', label: 'Surface', demand: surface, capacity: vehicle.surfaces, margin: surface == null ? null : vehicle.surfaces.includes(surface) ? 1 : -1, status: surface == null ? 'unknown' : vehicle.surfaces.includes(surface) ? 'pass' : 'fail' });
  const failures = constraints.filter(c => c.status === 'fail');
  const unknowns = constraints.filter(c => c.status === 'unknown');
  const limiting = constraints.filter(c => c.margin !== null).sort((a, b) => a.margin - b.margin)[0];
  const status = failures.length ? 'fail' : unknowns.length ? 'unknown' : constraints.some(c => c.status === 'near') ? 'near' : 'pass';
  return { status, constraints, failures, unknowns, limiting, margin: status === 'unknown' ? null : status === 'fail' ? 0 : Math.round(Math.max(0, limiting.margin) * 100) };
}

export const isFeasible = result => ['pass', 'near'].includes(result.status);
export function coverage(cells, vehicle) {
  const totals = { pass: 0, near: 0, fail: 0, unknown: 0, total: 0 };
  for (const cell of cells) {
    const area = cell.area;
    totals[evaluate(cell.terrain, vehicle).status] += area;
    totals.total += area;
  }
  totals.feasible = totals.pass + totals.near;
  totals.percent = totals.total ? 100 * totals.feasible / totals.total : 0;
  return totals;
}
export function comparison(cells, before, after) {
  let gained = 0, lost = 0;
  for (const cell of cells) {
    const previous = isFeasible(evaluate(cell.terrain, before));
    const current = isFeasible(evaluate(cell.terrain, after));
    if (!previous && current) gained += cell.area;
    if (previous && !current) lost += cell.area;
  }
  return { before: coverage(cells, before), after: coverage(cells, after), gained, lost };
}
