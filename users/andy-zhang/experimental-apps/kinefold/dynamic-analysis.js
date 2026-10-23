/** Pure native dynamic chart/comparison and prescribed spatial-floor data.
 * Load after model.js; Node VM tests may call the exported helpers. Inputs use
 * captured builder mm/deg/kg/N and backend seconds/SI energy rows. Outputs are
 * derived chart rows, exact-time/event-side comparisons and world-mm profiles.
 * No interpolated jump peaks, dynamic pin-force solve or collision model.
 */
globalThis.KinefoldDynamicAnalysis = (() => {
  'use strict';
  const palette = ['var(--sage)', 'var(--blue)', 'var(--amber)', 'var(--purple)'];
  const series = (...items) => items.map(([key, label], i) => [key, label, palette[i % palette.length]]);
  const manifest = [
    ['motion', 'input', 'Requested & applied wheel input', 'mm', series(['requestedInputMm', 'Requested square'], ['appliedInputMm', 'Applied input'])],
    ['motion', 'heave', 'Chassis displacement from initial', 'mm', series(['chassisDisplacementMm', 'Chassis heave'])],
    ['motion', 'height', 'World-frame heights', 'mm', series(['chassisZMm', 'Hip A'], ['wheelZMm', 'Wheel centre C'])],
    ['motion', 'speed', 'Chassis vertical speed', 'mm/s', series(['chassisVelocityMmS', 'Chassis speed'])],
    ['motion', 'acceleration', 'Chassis vertical acceleration', 'mm/s²', series(['chassisAccelerationMmS2', 'Chassis acceleration'])],
    ['kinematics', 'angles', 'Physical angles · jumps retained', '°', series(['theta2', 'Hip θ₂'], ['theta3', 'Tibia θ₃'], ['theta5', 'Compound θ₅'], ['theta6', 'Wheel θ₆'])],
    ['kinematics', 'rates', 'Angular rates · between input edges', '°/s', series(['velocityDegS', 'Hip'], ['rate3', 'Tibia'], ['rate5', 'Compound'], ['rate6', 'Wheel'])],
    ['kinematics', 'angular-acceleration', 'Angular acceleration · between input edges', '°/s²', series(['accelerationDegS2', 'Hip'], ['accel3', 'Tibia'], ['accel5', 'Compound'], ['accel6', 'Wheel'])],
    ['kinematics', 'wheel-x', 'Wheel-centre horizontal displacement', 'mm', series(['wheelDisplacementXMm', 'C_x − initial C_x'])],
    ['forces', 'spring', 'Spring cable tension', 'N', series(['Fs', 'Cable tension'])],
    ['forces', 'reaction', 'Signed vertical wheel-input reaction', 'N', series(['inputReactionN', 'Input actuator reaction'])],
    ['forces', 'torques', 'Applied & balance-reference torques', 'N·m', series(['motorTorqueNm', 'Motor command'], ['dampingTorqueNm', 'Damping'], ['tauApplied', 'Net actuation'], ['tauStatic', 'Instantaneous balance reference'])],
    ['energy', 'energy', 'Energy accounting', 'J', series(['kineticJ', 'Kinetic'], ['potentialJ', 'Effective potential'], ['energyJ', 'Total'])],
    ['energy', 'work', 'Cumulative supplied work', 'J', series(['actuatorDampingWorkJ', 'Actuation + damping'], ['inputWorkJ', 'Wheel input'])],
    ['energy', 'residual', 'Work–energy residual', 'J', series(['workEnergyResidualJ', 'E − E₀ − W_act − W_input'])],
    ['energy', 'constraint-position', 'Sampled horizontal chassis constraint error', 'mm', series(['constraintPositionErrorMm', '|x_A|'])],
    ['energy', 'constraint-angle', 'Sampled chassis pitch constraint error', '°', series(['constraintAngleErrorDeg', '|pitch|'])],
  ].map(([group, id, title, unit, keys]) => ({group, id, title, unit, series: keys}));
  const contactManifest = [
    ['motion','contact-heave','Chassis displacement from initial','mm',series(['chassisDisplacementMm','Chassis heave'])],
    ['motion','contact-heights','Actual chassis & wheel heights','mm',series(['chassisZMm','Actual A'],['wheelZMm','Actual C'])],
    ['motion','contact-speed','Actual vertical chassis speed','mm/s',series(['chassisVelocityMmS','Chassis speed'])],
    ['motion','contact-wheel-velocity','Actual wheel-centre velocity','mm/s',series(['wheelVelocityXMmS','+x velocity'],['wheelVelocityZMmS','+z velocity'])],
    ['kinematics','contact-angles','Backdriven physical indices','°',series(['theta2','Hip θ₂'],['theta4','Free drive θ₄'],['theta5','Compound θ₅'],['theta6','Wheel θ₆'])],
    ['kinematics','contact-spin','Actual wheel & backdrive angular rates','°/s',series(['wheelAngularVelocityDegS','Actual wheel spin'],['rate4','Backdriven shaft'],['rate5','Compound'])],
    ['kinematics','contact-guide','Actual guide residual','mm',series(['guideResidualMm','Constraint residual'])],
    ['forces','contact-spring','Spring cable tension','N',series(['Fs','Cable tension'])],
    ['forces','contact-forces','Contact force magnitudes · interval means','N',series(['contactNormalForceN','Normal magnitude'],['contactTangentialForceN','Tangential magnitude'])],
    ['forces','contact-world-forces','Signed contact force on wheel','N',series(['contactForceXN','+x component'],['contactForceZN','+z component'])],
    ['forces','contact-slip','Actual tangential slip · gaps when airborne','mm/s',series(['slipMmS','Contact slip'])],
    ['forces','contact-separation','Terrain separation & penetration','mm',series(['gapMm','Signed gap'],['penetrationMm','Penetration'])],
    ['forces','contact-guide-force','Massless guide actuation force','N',series(['guideForceN','Guide force'])],
    ['energy','contact-energy','Mechanical energy','J',series(['kineticJ','Kinetic'],['potentialJ','Potential'],['energyJ','Total'])],
    ['energy','contact-actuator-work','Cumulative hip actuation & damping work','J',series(['actuatorDampingWorkJ','Hip/damping work'])],
  ].map(([group,id,title,unit,keys])=>({group,id,title,unit,series:keys}));
  const comparisonFields = [
    ['chassisDisplacementMm', 'Chassis displacement', 'mm'],
    ['chassisVelocityMmS', 'Chassis speed', 'mm/s'],
    ['theta2', 'Hip angle', '°'],
    ['Fs', 'Spring tension', 'N'],
    ['inputReactionN', 'Wheel-input reaction', 'N'],
    ['workEnergyResidualJ', 'Work–energy residual', 'J'],
  ];
  function stable(value) {
    if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
    if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + stable(value[k])).join(',') + '}';
    return JSON.stringify(value);
  }
  function snapshotKey(snapshot) { return stable({params: snapshot.params, config: snapshot.solverConfig,contact:snapshot.contactConfig||null}); }
  function enrich(result) {
    const p = result.params, config = result.runConfig, ref = Kinefold.reference(p);
    const ratios = KinefoldV4.VSL.ratios(ref), k3 = 1 - ratios.qab, k5 = 1 - 1 / ratios.qdc;
    const k6 = KinefoldV4.VSL.coefficient(ref), first = result.rows[0];
    return result.rows.map((row, i) => {
      const pose = KinefoldV4.VSL.state(ref, row.theta2), frame = result.frames[i], contact=result.scope?.mode==='terrain-contact';
      const driveRate=contact?ratios.qdc*ratios.qfe*(row.wheelAngularVelocityDegS-k6*row.velocityDegS):0;
      return {...row, chassisDisplacementMm: row.chassisZMm - first.chassisZMm,
        wheelDisplacementXMm: row.CxMm - first.CxMm,
        theta3: pose.t3, theta4:contact?row.theta4:0,theta5: contact?row.theta5:pose.t5, theta6: contact?row.theta6:pose.t6,
        rate3: k3 * row.velocityDegS,rate4:driveRate, rate5: k5 * row.velocityDegS+driveRate/ratios.qdc, rate6: contact?row.wheelAngularVelocityDegS:k6 * row.velocityDegS,
        accel3:Number.isFinite(row.accelerationDegS2)?k3*row.accelerationDegS2:null, accel5:Number.isFinite(row.accelerationDegS2)?k5*row.accelerationDegS2:null, accel6:Number.isFinite(row.accelerationDegS2)?k6*row.accelerationDegS2:null,
        motorTorqueNm: config.hipTorqueNm, dampingTorqueNm: -config.dampingNms * row.velocityDegS * Math.PI / 180,
        workEnergyResidualJ: [row.energyJ,first.energyJ,row.actuatorDampingWorkJ,row.inputWorkJ].every(Number.isFinite)?row.energyJ-first.energyJ-row.actuatorDampingWorkJ-row.inputWorkJ:null,
        constraintPositionErrorMm: frame.constraintPositionErrorMm ?? (result.engine === 'analytical' ? 0 : null),
        constraintAngleErrorDeg: frame.constraintAngleErrorDeg ?? (result.engine === 'analytical' ? 0 : null)};
    });
  }
  function comparison(a, b) {
    if(a?.scope?.mode==='terrain-contact'||b?.scope?.mode==='terrain-contact')return {valid:false,reason:'Actual Pymunk terrain contact and the analytical prescribed-height bench are different models. Comparison is unavailable.'};
    if (a && b && (a.engine !== 'analytical' || b.engine !== 'pymunk')) return {valid:false,reason:'Choose one analytical run and one Pymunk run.'};
    if (!a || !b) return {valid: false, reason: 'Run both engines on the same captured mechanism and input profile.'};
    if (!a.designHash || a.designHash !== b.designHash || stable(a.params) !== stable(b.params))
      return {valid: false, reason: 'Mechanism snapshots differ. Run both again from one captured design.'};
    if (stable(a.runConfig) !== stable(b.runConfig)) return {valid: false, reason: 'Input or numerical profiles differ. Run both again with the same profile.'};
    const aa = enrich(a), bb = enrich(b), key = r => r.t.toFixed(8) + '|' + (r.eventSide || 'sample');
    const byTime = new Map(bb.map(row => [key(row), row])), rows = [];
    for (const ar of aa) {
      const br = byTime.get(key(ar));
      if (!br || Math.abs(ar.t - br.t) > 1e-8) continue;
      const row = {t: ar.t, eventSide: ar.eventSide || ''};
      for (const [field] of comparisonFields) {
        row[field + 'A'] = ar[field]; row[field + 'P'] = br[field];
        row[field + 'Error'] = Number.isFinite(br[field]) && Number.isFinite(ar[field]) ? br[field] - ar[field] : null;
      }
      rows.push(row);
    }
    if (!rows.length) return {valid: false, reason: 'No matching time/event-side samples; no interpolation or extrapolation is performed.'};
    const stats = comparisonFields.map(([field, label, unit]) => {
      const values = rows.map(row => row[field + 'Error']).filter(Number.isFinite);
      return {field, label, unit, count: values.length, maxAbs: values.length ? Math.max(...values.map(Math.abs)) : null,
        rms: values.length ? Math.sqrt(values.reduce((v, x) => v + x * x, 0) / values.length) : null};
    });
    return {valid: true, rows, stats, matched: rows.length, analyticalSamples: aa.length, pymunkSamples: bb.length,
      start: rows[0].t, end: rows.at(-1).t, complete: rows.length === aa.length && rows.length === bb.length,
      terminationA: a.diagnostics.termination, terminationP: b.diagnostics.termination};
  }
  function inputAtDistance(config, distance, side = 'right') {
    const height = config.inputHeightMm, high = config.inputPlateauMm, period = high + config.inputGapMm;
    const tolerance = config.inputSpeedMmS * 1e-10, startTolerance = config.inputSpeedMmS * 1e-12;
    if (distance < -startTolerance || (Math.abs(distance) < startTolerance && side === 'left')) return {requested: 0, applied: 0};
    let phase = Math.max(0, distance) % period;
    if (phase < tolerance || period - phase < tolerance) phase = side === 'left' && distance > 0 ? period : 0;
    if (Math.abs(phase - high) < tolerance) phase = side === 'left' ? high - config.inputSpeedMmS * 1e-11 : high;
    const requested = phase < high ? height : 0, rise = config.inputRiseMm;
    if (!requested || !rise) return {requested, applied: requested};
    const u = phase < rise ? phase / rise : phase > high - rise ? (high - phase) / rise : 1;
    return {requested, applied: height * u ** 3 * (10 + u * (-15 + 6 * u))};
  }
  function floor(config, row, wheelX, minX, maxX) {
    const distance = config.inputSpeedMmS * (row.t - config.inputDelayS);
    const period = config.inputPlateauMm + config.inputGapMm, positions = [minX, maxX, wheelX];
    const start = Math.max(0, Math.floor((distance + minX - wheelX) / period) - 1);
    const end = Math.max(start, Math.ceil((distance + maxX - wheelX) / period) + 1);
    for (let n = start; n <= end && n - start < 2000; n++) {
      const origin = wheelX - distance + n * period;
      for (const offset of [0, config.inputRiseMm, config.inputPlateauMm - config.inputRiseMm, config.inputPlateauMm]) {
        const x = origin + offset;
        if (x >= minX && x <= maxX) positions.push(x);
      }
    }
    for (let i = 0; i <= 300; i++) positions.push(minX + (maxX - minX) * i / 300);
    const xs = [...new Set(positions)].filter(x => x >= minX && x <= maxX).sort((a, b) => a - b), requested = [], applied = [];
    for (const x of xs) {
      const d = distance + x - wheelX;
      for (const side of ['left', 'right']) {
        const value = inputAtDistance(config, d, side);
        requested.push([x, value.requested]); applied.push([x, value.applied]);
      }
    }
    return {requested, applied, atWheel: inputAtDistance(config, distance, row.eventSide === 'before' ? 'left' : 'right'), distance, dense: end - start >= 2000};
  }
  return {manifest,contactManifest, comparisonFields, stable, snapshotKey, enrich, comparison, inputAtDistance, floor};
})();
