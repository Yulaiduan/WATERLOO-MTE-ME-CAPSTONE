/** Reduced vertical model, output-shaft actuator. All calculations use SI units. */
export const DEFAULT_MECHANISM = { linkLengthM: .18, minAngleDeg: 12, maxAngleDeg: 75, nominalAngleDeg: 45, wheelRadiusM: .08 };
export const DEFAULT_SCENARIO = { speedMps: 1, sprungMassKg: 5, unsprungMassKg: 1, springRateNpm: 1000,
  damperNsPm: 20, tireRateNpm: 12000, tireDamperNsPm: 35, controlMode: 'body-isolation', skyhookNsPm: 80,
  positionGainNpm: 1800, velocityGainNsPm: 100, timeStepS: .001, outputStepS: .01, maxDurationS: 1200 };
export const DEFAULT_ACTUATOR = { peakTorqueNm: 12, continuousTorqueNm: 4, noLoadSpeedRadPs: 20, responseTimeS: .02, slewRateNmPs: 300 };
const G = 9.80665, RAD = Math.PI / 180;
const LIMITATIONS = [
  'Prescribed forward speed; no traction, propulsion, pitch, roll or skid-steer dynamics.',
  'Rigid vertical ground base input with unilateral tire compliance; does not establish step-climbing or wheel-radius obstacle filtering.',
  'Equivalent linear wheel-coordinate spring preloaded for the selected supported mass; actual spring routing and link-mass distribution are unknown.',
  'Moving assembly represented by one unsprung mass; link rotational inertia, reflected motor inertia, belt/pin reactions and coaxial drive-fold interaction are excluded.',
  'Generic chosen output-shaft torque-speed envelope, response and slew assumptions; no manufacturer verified motor recommendation.',
  'Mechanical power/work only. Current, voltage, electrical loss, thermal capacity, battery and regeneration remain unknown.',
  'RMS and peaks refer to simulated portion only; failed runs are not complete-route sizing evidence.',
];
function finite(n, name, min, max = Infinity) { if (!Number.isFinite(n) || n < min || n > max) throw new Error(`${name} must be finite between ${min} and ${max}.`); }
function mechanismConfig(input) {
  const m = { ...DEFAULT_MECHANISM, ...input };
  finite(m.linkLengthM, 'Link length', .01, 2); finite(m.minAngleDeg, 'Minimum fold angle', 1, 85);
  finite(m.maxAngleDeg, 'Maximum fold angle', 2, 89); finite(m.nominalAngleDeg, 'Nominal fold angle', m.minAngleDeg, m.maxAngleDeg);
  finite(m.wheelRadiusM, 'Wheel radius', .001, 2);
  if (m.minAngleDeg >= m.maxAngleDeg) throw new Error('Minimum fold angle must be below maximum fold angle.');
  return m;
}
export function linkageAtAngle(angleRad, mechanism = {}) {
  const m = mechanismConfig(mechanism); finite(angleRad, 'Fold angle (rad)', 0, Math.PI / 2);
  const x = m.linkLengthM * Math.sin(angleRad), y = -m.linkLengthM * Math.cos(angleRad);
  return { angleRad, upperAngleRad: angleRad, lowerAngleRad: -angleRad, kneeAngleRad: -2 * angleRad,
    extensionM: -2 * y, jacobianMPerRad: -2 * m.linkLengthM * Math.sin(angleRad),
    knee: { x, y }, wheel: { x: 0, y: 2 * y }, usable: angleRad >= m.minAngleDeg * RAD && angleRad <= m.maxAngleDeg * RAD };
}
function validate(terrain, scenario, mechanism, actuator) {
  if (!terrain?.samples || terrain.samples.length < 2) throw new Error('Terrain needs at least two samples.');
  terrain.samples.forEach((s, i) => { finite(s.x, 'Terrain distance', 0); finite(s.z, 'Terrain elevation', -1e6, 1e6); finite(s.baseline ?? s.z, 'Baseline elevation', -1e6, 1e6); if (i && s.x <= terrain.samples[i - 1].x) throw new Error('Terrain distance must increase strictly.'); });
  const c = { ...DEFAULT_SCENARIO, ...scenario }, m = mechanismConfig(mechanism), a = { ...DEFAULT_ACTUATOR, ...actuator };
  for (const key of ['speedMps', 'sprungMassKg', 'unsprungMassKg', 'springRateNpm', 'tireRateNpm', 'timeStepS', 'outputStepS', 'maxDurationS']) finite(c[key], key, 1e-8);
  for (const key of ['damperNsPm', 'tireDamperNsPm', 'skyhookNsPm', 'positionGainNpm', 'velocityGainNsPm']) finite(c[key], key, 0);
  finite(c.timeStepS, 'Solver timestep', .00001, .02); finite(c.outputStepS, 'Output interval', .0001, 10); finite(c.speedMps, 'Speed', .001, 30);
  finite(c.maxDurationS, 'Maximum duration', .001, 2000);
  if (!['passive', 'active-damping', 'body-isolation'].includes(c.controlMode)) throw new Error('Unknown suspension control mode.');
  for (const key of ['peakTorqueNm', 'continuousTorqueNm', 'noLoadSpeedRadPs', 'responseTimeS', 'slewRateNmPs']) finite(a[key], key, key === 'responseTimeS' ? .0001 : 0);
  if (a.noLoadSpeedRadPs <= 0 || a.slewRateNmPs <= 0) throw new Error('No-load speed and slew rate must be positive.');
  if (a.continuousTorqueNm > a.peakTorqueNm) throw new Error('Continuous torque cannot exceed peak torque.');
  return { c, m, a };
}
function interpolate(samples, x) {
  let lo = 0, hi = samples.length - 1;
  if (x <= samples[0].x) hi = 1;
  else if (x >= samples.at(-1).x) lo = samples.length - 2;
  else { while (hi - lo > 1) { const mid = (lo + hi) >>> 1; if (samples[mid].x <= x) lo = mid; else hi = mid; } }
  const s0 = samples[lo], s1 = samples[hi], dx = s1.x - s0.x, f = Math.max(0, Math.min(1, (x - s0.x) / dx));
  return { z: s0.z + f * (s1.z - s0.z), baseline: (s0.baseline ?? s0.z) + f * ((s1.baseline ?? s1.z) - (s0.baseline ?? s0.z)), slope: (s1.z - s0.z) / dx };
}
function makeSummary() { return { peakTorqueNm: 0, rmsTorqueNm: 0, peakJointSpeedRadPs: 0, peakPowerW: 0,
  rmsBodyAccelerationMps2: 0, peakBodyAccelerationMps2: 0, minTravelMarginM: Infinity, contactLossTimeS: 0,
  saturationTimeS: 0, responseLimitedTimeS: 0, completedDistanceM: 0, simulatedTimeS: 0, positiveWorkJ: 0, negativeWorkJ: 0,
  continuousOverloadTimeS: 0, longestContinuousOverloadS: 0, above90PercentPeakTimeS: 0, longestAbove90PercentPeakS: 0,
  peakPassiveTorqueNm: 0, peakNormalForceN: 0, peakTotalJointTorqueNm: 0 };
}
function reduceHistory(history, budget = 6000) {
  if (history.length <= budget) return history;
  const selected = new Set([0, history.length - 1]), bucket = Math.ceil(history.length / (budget / 6));
  for (let start = 0; start < history.length; start += bucket) {
    const end = Math.min(history.length, start + bucket);
    for (const key of ['torqueNm', 'angleRad', 'bodyAccelerationMps2']) {
      let imin = start, imax = start;
      for (let i = start + 1; i < end; i++) { if (history[i][key] < history[imin][key]) imin = i; if (history[i][key] > history[imax][key]) imax = i; }
      selected.add(imin); selected.add(imax);
    }
  }
  return Array.from(selected).sort((a, b) => a - b).map(i => history[i]);
}
function runPass(terrain, c, m, a, limited) {
  const samples = terrain.samples, x0 = samples[0].x, xEnd = samples.at(-1).x;
  const fullDuration = (xEnd - x0) / c.speedMps, duration = Math.min(fullDuration, c.maxDurationS);
  const nominal = linkageAtAngle(m.nominalAngleDeg * RAD, m), ell0 = nominal.extensionM;
  const ellMin = 2 * m.linkLengthM * Math.cos(m.maxAngleDeg * RAD), ellMax = 2 * m.linkLengthM * Math.cos(m.minAngleDeg * RAD);
  const naturalPeriod = 2 * Math.PI / Math.sqrt((c.tireRateNpm + c.springRateNpm) / c.unsprungMassKg);
  let minSpacing = Infinity; for (let i = 1; i < samples.length; i++) minSpacing = Math.min(minSpacing, samples[i].x - samples[i - 1].x);
  const dt = Math.min(c.timeStepS, naturalPeriod / 80, minSpacing / c.speedMps / 4, limited ? a.responseTimeS / 6 : Infinity);
  if (duration / dt > 5e6) throw new Error('Case exceeds 5 million solver steps. Shorten the run, increase speed or reduce terrain resolution.');
  const outputDt = Math.max(c.outputStepS, duration / 100000);
  const initial = interpolate(samples, x0), baseZero = initial.z;
  // Wheel initial compression = (ms+mu)g/kt; body spring preload = msg.
  // wheelM stores axle height, terrainM stores the uncompressed axle base z+r.
  const reference = t => {
    const x = x0 + c.speedMps * t, h = Math.max(minSpacing, 1);
    const b = interpolate(samples, x).baseline;
    const leftX = Math.max(x0, x - h), rightX = Math.min(xEnd, x + h);
    const slope = (interpolate(samples, rightX).baseline - interpolate(samples, leftX).baseline) / Math.max(1e-9, rightX - leftX);
    return { height: b - initial.baseline + ell0, velocity: slope * c.speedMps };
  };
  const tireSag = (c.sprungMassKg + c.unsprungMassKg) * G / c.tireRateNpm;
  const initialVelocity = reference(0).velocity;
  let state = [ell0, initialVelocity, 0, initialVelocity, 0], t = 0, nextRecord = 0;
  const summary = makeSummary(), history = [], points = new Map();
  let torqueSquares = 0, accelSquares = 0, overloadStreak = 0, peakStreak = 0, firstFailure = null;
  function evaluate(time, y) {
    const x = Math.min(xEnd, x0 + c.speedMps * time), ground = interpolate(samples, x), ref = reference(time);
    const ell = y[0] - y[2], ratio = ell / (2 * m.linkLengthM);
    if (!Number.isFinite(ratio) || ratio <= 0 || ratio >= 1) return { invalid: 'Linkage mapping became singular or physically unreachable.' };
    const q = Math.acos(ratio), J = -2 * m.linkLengthM * Math.sin(q), qdot = (y[1] - y[3]) / J;
    const passive = c.sprungMassKg * G + c.springRateNpm * (ell0 - ell) - c.damperNsPm * (y[1] - y[3]);
    let demand = 0;
    if (c.controlMode === 'active-damping') demand = -c.skyhookNsPm * (y[1] - ref.velocity);
    if (c.controlMode === 'body-isolation') demand = c.positionGainNpm * (ref.height - y[0]) + c.velocityGainNsPm * (ref.velocity - y[1]);
    const demandTorque = demand * J, cap = a.peakTorqueNm * Math.max(0, 1 - Math.abs(qdot) / a.noLoadSpeedRadPs);
    const target = Math.max(-cap, Math.min(cap, demandTorque));
    const torque = limited ? Math.max(-cap, Math.min(cap, y[4])) : demandTorque;
    const active = torque / J, tireCompression = tireSag + ground.z - baseZero - y[2];
    // Damping acts only while geometric contact exists; it must not pull or create force across a gap.
    const normal = tireCompression > 0 ? Math.max(0, c.tireRateNpm * tireCompression + c.tireDamperNsPm * (ground.slope * c.speedMps - y[3])) : 0;
    const ab = (passive + active - c.sprungMassKg * G) / c.sprungMassKg;
    const aw = (normal - passive - active - c.unsprungMassKg * G) / c.unsprungMassKg;
    const torqueRate = limited ? Math.max(-a.slewRateNmPs, Math.min(a.slewRateNmPs, (target - y[4]) / a.responseTimeS)) : 0;
    return { derivative: [y[1], ab, y[3], aw, torqueRate], row: {
      timeS: time, xM: x, groundM: ground.z, wheelM: y[2] + baseZero + m.wheelRadiusM - tireSag,
      bodyM: y[0] + baseZero + m.wheelRadiusM - tireSag, extensionM: ell, angleRad: q, jointSpeedRadPs: qdot,
      torqueNm: torque, demandTorqueNm: demandTorque, passiveTorqueNm: passive * J, totalJointTorqueNm: (passive + active) * J,
      springForceN: c.sprungMassKg * G + c.springRateNpm * (ell0 - ell), passiveForceN: passive, activeForceN: active,
      normalForceN: normal, bodyAccelerationMps2: ab, travelMarginM: Math.min(ell - ellMin, ellMax - ell),
      mechanicalPowerW: torque * qdot, torqueCapacityNm: cap,
      saturated: limited && (Math.abs(demandTorque) > cap + 1e-8 || Math.abs(y[4]) > cap + 1e-8),
      responseLimited: limited && Math.abs(target - torque) > Math.max(.01, .02 * Math.abs(target)),
    } };
  }
  function failure(reason, row) { return { reason, timeS: row?.timeS ?? t, xM: row?.xM ?? x0 + t * c.speedMps }; }
  function collect(row, h) {
    const absT = Math.abs(row.torqueNm), power = row.mechanicalPowerW;
    torqueSquares += row.torqueNm ** 2 * h; accelSquares += row.bodyAccelerationMps2 ** 2 * h;
    summary.minTravelMarginM = Math.min(summary.minTravelMarginM, row.travelMarginM);
    summary.peakBodyAccelerationMps2 = Math.max(summary.peakBodyAccelerationMps2, Math.abs(row.bodyAccelerationMps2));
    if (Math.abs(row.jointSpeedRadPs) >= summary.peakJointSpeedRadPs) {
      summary.peakJointSpeedRadPs = Math.abs(row.jointSpeedRadPs);
      summary.peakSpeedLocation = { timeS: row.timeS, xM: row.xM, torqueNm: row.torqueNm, speedRadPs: row.jointSpeedRadPs };
    }
    summary.peakPassiveTorqueNm = Math.max(summary.peakPassiveTorqueNm, Math.abs(row.passiveTorqueNm));
    summary.peakTotalJointTorqueNm = Math.max(summary.peakTotalJointTorqueNm, Math.abs(row.totalJointTorqueNm));
    summary.peakNormalForceN = Math.max(summary.peakNormalForceN, row.normalForceN);
    if (absT >= summary.peakTorqueNm) { summary.peakTorqueNm = absT; summary.peakTorqueLocation = { timeS: row.timeS, xM: row.xM, torqueNm: row.torqueNm, speedRadPs: row.jointSpeedRadPs }; }
    if (Math.abs(power) >= summary.peakPowerW) {
      summary.peakPowerW = Math.abs(power);
      summary.peakPowerLocation = { timeS: row.timeS, xM: row.xM, powerW: power, torqueNm: row.torqueNm, speedRadPs: row.jointSpeedRadPs };
    }
    summary.positiveWorkJ += Math.max(0, power) * h; summary.negativeWorkJ += Math.min(0, power) * h;
    if (row.normalForceN < 1e-5) summary.contactLossTimeS += h;
    if (row.saturated) summary.saturationTimeS += h;
    if (row.responseLimited) summary.responseLimitedTimeS += h;
    const overloaded = absT > a.continuousTorqueNm + 1e-8;
    overloadStreak = overloaded ? overloadStreak + h : 0; summary.continuousOverloadTimeS += overloaded ? h : 0;
    summary.longestContinuousOverloadS = Math.max(summary.longestContinuousOverloadS, overloadStreak);
    const nearPeak = a.peakTorqueNm > 0 && absT > .9 * a.peakTorqueNm;
    peakStreak = nearPeak ? peakStreak + h : 0; summary.above90PercentPeakTimeS += nearPeak ? h : 0;
    summary.longestAbove90PercentPeakS = Math.max(summary.longestAbove90PercentPeakS, peakStreak);
    // Signed speed bins retain torque extrema and true simultaneous pairs, at solver cadence.
    const bin = Math.round(row.jointSpeedRadPs / Math.max(.05, a.noLoadSpeedRadPs / 100));
    const entry = points.get(bin) ?? { min: row, max: row };
    if (row.torqueNm < entry.min.torqueNm) entry.min = row; if (row.torqueNm > entry.max.torqueNm) entry.max = row;
    points.set(bin, entry);
    if (row.timeS >= nextRecord - 1e-10) { history.push(row); nextRecord = row.timeS + outputDt; }
  }
  const initialEvaluation = evaluate(0, state); collect(initialEvaluation.row, 0);
  while (t < duration - 1e-10) {
    const h = Math.min(dt, duration - t), e1 = evaluate(t, state);
    if (e1.invalid) { firstFailure = failure(e1.invalid); break; }
    if (e1.row.travelMarginM < -1e-9) { firstFailure = failure('Suspension travel exceeded the declared usable fold-angle range.', e1.row); break; }
    const k1 = e1.derivative;
    const stage = (k, scale) => state.map((v, i) => v + h * scale * k[i]);
    const e2 = evaluate(t + h / 2, stage(k1, .5)); if (e2.invalid) { firstFailure = failure(e2.invalid); break; }
    const e3 = evaluate(t + h / 2, stage(e2.derivative, .5)); if (e3.invalid) { firstFailure = failure(e3.invalid); break; }
    const e4 = evaluate(t + h, stage(e3.derivative, 1)); if (e4.invalid) { firstFailure = failure(e4.invalid); break; }
    state = state.map((v, i) => v + h * (k1[i] + 2 * e2.derivative[i] + 2 * e3.derivative[i] + e4.derivative[i]) / 6);
    t += h;
    if (state.some(v => !Number.isFinite(v))) { firstFailure = failure('Numerically invalid state.'); break; }
    const evaluated = evaluate(t, state); if (evaluated.invalid) { firstFailure = failure(evaluated.invalid); break; }
    collect(evaluated.row, h);
    if (evaluated.row.travelMarginM < -1e-9) { firstFailure = failure('Suspension travel exceeded the declared usable fold-angle range.', evaluated.row); break; }
  }
  const last = evaluate(t, state); if (last.row && history.at(-1)?.timeS !== last.row.timeS) history.push(last.row);
  summary.simulatedTimeS = t; summary.completedDistanceM = t * c.speedMps;
  summary.rmsTorqueNm = t ? Math.sqrt(torqueSquares / t) : 0;
  summary.rmsBodyAccelerationMps2 = t ? Math.sqrt(accelSquares / t) : 0;
  summary.holdingTorqueNm = 0; summary.nominalPassiveSupportTorqueNm = c.sprungMassKg * G * nominal.jacobianMPerRad;
  summary.maxTorqueNm = -Infinity; summary.minTorqueNm = Infinity;
  for (const entry of points.values()) { summary.maxTorqueNm = Math.max(summary.maxTorqueNm, entry.max.torqueNm); summary.minTorqueNm = Math.min(summary.minTorqueNm, entry.min.torqueNm); }
  const operatingPoints = Array.from(points.values()).flatMap(p => [p.min, p.max]).map(r => ({ torqueNm: r.torqueNm, speedRadPs: r.jointSpeedRadPs, timeS: r.timeS, xM: r.xM, capacityNm: r.torqueCapacityNm }));
  if (!firstFailure && fullDuration > c.maxDurationS) firstFailure = failure('Requested route exceeds maximum run duration.');
  return { status: firstFailure ? 'failed' : 'completed', history: reduceHistory(history), fullHistory: history, summary, operatingPoints, firstFailure,
    metadata: { pass: limited ? 'hardware-limited' : 'ideal-demand', actualTimeStepS: dt, outputStepS: outputDt, summaryCadenceS: dt,
      fullRouteDurationS: fullDuration, historyReduction: 'Plot history uses bucket extrema. fullHistory is recorded output cadence, not every solver step. Summary and operating points use solver cadence.',
      tireSagM: tireSag, springPreloadN: c.sprungMassKg * G,
      saturationStatistic: 'Demand or lag state exceeds instantaneous torque-speed envelope. responseLimitedTimeS separately records lag/slew tracking mismatch above 2% or 0.01Nm.',
      contactModel: 'Unilateral compliant tire: normal=max(0,kt compression+ct compression velocity) only when compression>0; zero across geometric gap. Wheel-radius ground filtering excluded.' } };
}
export function simulateScenario(terrain, scenario = {}, mechanism = {}, actuator = {}) {
  const { c, m, a } = validate(terrain, scenario, mechanism, actuator);
  const ideal = runPass(terrain, c, m, a, false), limited = runPass(terrain, c, m, a, true);
  return { ideal, limited, metadata: { model: 'V1 reduced vertical quarter-car / equal-link kinematics', scenario: c, mechanism: m, actuator: a,
    actuatorEvidence: 'Illustrative generic output-shaft ratings and response assumptions; not verified manufacturer specifications.',
    limitations: LIMITATIONS, terrain: terrain.metadata, unknown: ['current', 'voltage', 'electrical loss', 'temperature', 'battery energy', 'reflected inertia', 'belt tension', 'pin loads', 'drive-fold coupling'],
    conventions: 'Fold q from downward vertical; upper +q, lower -q, relative knee -2q. Extension ell=2Lcos(q); torque=u*dell/dq. Active torque excludes spring/damper support; total joint torque includes it.',
    reference: 'Body follows macro baseline height; velocity uses centred baseline differences over ±1m. Full imported elevation is macro baseline when fine layers are absent.',
    acceptance: 'No approved vehicle acceleration/contact limits. Completed means numerical route completion inside travel bounds, not hardware approval.',
    solver: 'RK4; timestep bounded by tire natural period, terrain sample traversal and actuator response. Refine timestep and source resolution to assess convergence.' } };
}
export function serializeResultsCsv(result) {
  const keys = ['timeS','xM','groundM','wheelM','bodyM','extensionM','angleRad','jointSpeedRadPs','torqueNm','demandTorqueNm','passiveTorqueNm','totalJointTorqueNm','springForceN','activeForceN','normalForceN','bodyAccelerationMps2','travelMarginM','mechanicalPowerW','saturated'];
  const header = ['pass', ...keys].join(',');
  return header + '\n' + ['ideal','limited'].flatMap(pass => (result[pass]?.fullHistory ?? result[pass]?.history ?? []).map(row => [pass, ...keys.map(k => typeof row[k] === 'boolean' ? Number(row[k]) : row[k])].join(','))).join('\n');
}
