import { Matrix, EigenvalueDecomposition } from 'ml-matrix';

/** Planar fixed-base belt leg. SI units; q and beta are CCW from down vertical.
 * Independent coordinates are folding q and coaxial drive phi, not two knees.
 * Guide beta=(1-rs)q+phase. Open drive belts use relative carrier velocities.
 */
export function defaultConfig() {
  const axis = { kp: 25, kd: 1.5, feedforward: true, torqueFeedforward: 0, torqueLimit: 18, continuousTorque: 6,
    noLoadSpeed: 35, lag: 0.012, slewRate: 500, rotorInertia: 0.00008,
    reduction: 6, viscousFriction: 0.015 };
  return {
    geometry: { upperLength: 0.18, lowerLength: 0.18, guideRatio: 2,
      guidePhase: 0, driveRatio1: 1, driveRatio2: 1, wheelRadius: 0.075,
      foldMin: 0.12, foldMax: 1.38, pose: 0.6, driveAngle: 0 },
    mass: { upperMass: 0.35, lowerMass: 0.35, wheelMass: 0.6,
      upperComFraction: 0.5, lowerComFraction: 0.5,
      upperInertia: 0.000945, lowerInertia: 0.000945,
      wheelInertia: 0.0016875, compoundPulleyInertia: 0.00004, gravity: 9.80665 },
    spring: { type: 'torsion', stiffness: 20, damping: 0.15,
      restAngle: 0.2, preloadTorque: 0,
      anchorX: -0.08, anchorY: 0.02, attachLink: 'upper', attachFraction: 0.75,
      freeLength: 0.15, linearStiffness: 1600, linearDamping: 10, tensionOnly: false },
    load: { forceX: 0, forceY: 50, wheelMoment: 0, disturbanceTorque: 0,
      disturbanceStart: 0.5, disturbanceDuration: 0.2 },
    actuators: { fold: axis, drive: { ...axis, kp: 2, kd: 0.25,
      torqueLimit: 4, continuousTorque: 1.5, noLoadSpeed: 90, reduction: 1, viscousFriction: 0.003 } },
    motion: { type: 'step', target: 0.6, initialAngle: 0.55, initialVelocity: 0,
      amplitude: 0.08, frequency: 1, stepTime: 0.4, stepSize: 0.12,
      driveSpeed: 0, initialDriveAngle: 0, initialDriveVelocity: 0 },
    simulation: { mode: 'finite', duration: 3, dt: 0.001, outputDt: 0.01 }
  };
}

const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const mul = (a, k) => a.map(x => x * k);
const v = q => [Math.sin(q), -Math.cos(q)];
const dv = q => [Math.cos(q), Math.sin(q)];
const ddv = q => [-Math.sin(q), Math.cos(q)];
const finite = (x, name) => { if (!Number.isFinite(x)) throw new Error(`${name} must be finite.`); };
const positive = (x, name, allowZero = false) => {
  finite(x, name); if (allowZero ? x < 0 : x <= 0) throw new Error(`${name} must be ${allowZero ? 'nonnegative' : 'positive'}.`);
};

export function normalizeConfig(input = {}) {
  const d = defaultConfig();
  const c = { ...d };
  for (const key of ['geometry', 'mass', 'spring', 'load', 'motion', 'simulation']) c[key] = { ...d[key], ...(input[key] || {}) };
  c.actuators = { fold: { ...d.actuators.fold, ...input.actuators?.fold }, drive: { ...d.actuators.drive, ...input.actuators?.drive } };
  for (const group of ['geometry', 'mass', 'spring', 'load', 'motion', 'simulation']) {
    for (const [key, val] of Object.entries(d[group])) {
      if (typeof val === 'number') finite(c[group][key], `${group}.${key}`);
      if (typeof val === 'boolean' && typeof c[group][key] !== 'boolean') throw new Error(`${group}.${key} must be boolean.`);
    }
  }
  for (const name of ['fold', 'drive']) for (const [key, val] of Object.entries(d.actuators[name])) {
    if (typeof val === 'number') finite(c.actuators[name][key], `${name}.${key}`);
    if (typeof val === 'boolean' && typeof c.actuators[name][key] !== 'boolean') throw new Error(`${name}.${key} must be boolean.`);
  }
  const g = c.geometry, m = c.mass, s = c.spring;
  for (const key of ['upperLength', 'lowerLength', 'guideRatio', 'driveRatio1', 'driveRatio2', 'wheelRadius']) positive(g[key], `geometry.${key}`);
  if (g.foldMin >= g.foldMax || g.foldMax - g.foldMin > 2 * Math.PI) throw new Error('Fold working limits must be ordered and span at most 2π.');
  if (g.pose < g.foldMin || g.pose > g.foldMax) throw new Error('Selected pose is outside the fold working limits.');
  for (const key of ['upperMass', 'lowerMass', 'wheelMass', 'upperInertia', 'lowerInertia', 'wheelInertia', 'compoundPulleyInertia', 'gravity']) positive(m[key], `mass.${key}`, true);
  for (const key of ['upperComFraction', 'lowerComFraction']) if (m[key] < 0 || m[key] > 1) throw new Error(`${key} must be between 0 and 1.`);
  for (const key of ['stiffness', 'damping', 'linearStiffness', 'linearDamping']) positive(s[key], `spring.${key}`, true);
  positive(s.freeLength, 'spring.freeLength');
  if (!['torsion', 'linear', 'none'].includes(s.type)) throw new Error('Spring type must be torsion, linear, or none.');
  if (!['upper', 'lower'].includes(s.attachLink) || s.attachFraction < 0 || s.attachFraction > 1) throw new Error('Spring attachment must be on the upper/lower link with fraction 0–1.');
  for (const [name, a] of Object.entries(c.actuators)) {
    for (const key of ['kp', 'kd', 'rotorInertia', 'viscousFriction']) positive(a[key], `${name}.${key}`, true);
    for (const key of ['torqueLimit', 'continuousTorque', 'noLoadSpeed', 'lag', 'slewRate', 'reduction']) positive(a[key], `${name}.${key}`);
  }
  if (!['passive', 'ideal', 'finite'].includes(c.simulation.mode)) throw new Error('Simulation mode must be passive, ideal, or finite.');
  if (!['hold', 'step', 'sine', 'release'].includes(c.motion.type)) throw new Error('Motion type must be hold, step, sine, or release.');
  positive(c.motion.frequency, 'motion.frequency', true);
  positive(c.simulation.duration, 'simulation.duration'); positive(c.simulation.dt, 'simulation.dt'); positive(c.simulation.outputDt, 'simulation.outputDt');
  if (c.simulation.dt > 0.01 || c.simulation.duration > 30 || c.simulation.duration / c.simulation.dt > 200000) throw new Error('Use dt ≤ 0.01 s, duration ≤ 30 s, and at most 200,000 integration steps.');
  if (c.motion.initialAngle < g.foldMin || c.motion.initialAngle > g.foldMax) throw new Error('Initial fold angle is outside the working limits.');
  if (c.load.disturbanceDuration < 0) throw new Error('Disturbance duration must be nonnegative.');
  return c;
}

function coefficients(c) {
  const g = c.geometry, s = 1 - g.guideRatio;
  return { s, a: g.driveRatio1 * g.driveRatio2,
    b: g.driveRatio2 * (1 - g.driveRatio1) + (1 - g.driveRatio2) * s };
}

function kinematics(c, q, phi = 0) {
  const g = c.geometry, m = c.mass, { s, a, b } = coefficients(c);
  const beta = s * q + g.guidePhase;
  const B = mul(v(q), g.upperLength), C = add(B, mul(v(beta), g.lowerLength));
  const Bq = mul(dv(q), g.upperLength), Bqq = mul(ddv(q), g.upperLength);
  const Cq = add(Bq, mul(dv(beta), g.lowerLength * s));
  const Cqq = add(Bqq, mul(ddv(beta), g.lowerLength * s * s));
  const upperCom = mul(B, m.upperComFraction), upperD = mul(Bq, m.upperComFraction), upperDD = mul(Bqq, m.upperComFraction);
  const lowerCom = add(B, mul(v(beta), g.lowerLength * m.lowerComFraction));
  const lowerD = add(Bq, mul(dv(beta), g.lowerLength * m.lowerComFraction * s));
  const lowerDD = add(Bqq, mul(ddv(beta), g.lowerLength * m.lowerComFraction * s * s));
  return { A: [0, 0], B, C, q, phi, beta, wheelAngle: a * phi + b * q + (1 - g.driveRatio2) * g.guidePhase,
    compoundAngle: g.driveRatio1 * phi + (1 - g.driveRatio1) * q,
    jacobian: [[Cq[0], 0], [Cq[1], 0], [b, a]], Cq, Cqq,
    coms: { upper: upperCom, lower: lowerCom, wheel: C },
    derivatives: { upper: upperD, lower: lowerD, wheel: Cq },
    secondDerivatives: { upper: upperDD, lower: lowerDD, wheel: Cqq }, s, a, b };
}

function inertial(c, k) {
  const m = c.mass, g = c.geometry;
  // Configured COM inertias. Defaults estimate uniform rods; custom COMs require measured I.
  const I1 = m.upperInertia, I2 = m.lowerInertia;
  let Mqq = I1 + I2 * k.s ** 2, MqqDerivative = 0;
  for (const [name, mass] of [['upper', m.upperMass], ['lower', m.lowerMass], ['wheel', m.wheelMass]]) {
    Mqq += mass * dot(k.derivatives[name], k.derivatives[name]);
    MqqDerivative += 2 * mass * dot(k.derivatives[name], k.secondDerivatives[name]);
  }
  const pb = 1 - g.driveRatio1, pa = g.driveRatio1;
  // Rotor inertias are referred to output coordinates once, using reduction².
  Mqq += m.wheelInertia * k.b ** 2 + m.compoundPulleyInertia * pb ** 2 + c.actuators.fold.rotorInertia * c.actuators.fold.reduction ** 2;
  const Mqp = m.wheelInertia * k.a * k.b + m.compoundPulleyInertia * pa * pb;
  const Mpp = m.wheelInertia * k.a ** 2 + m.compoundPulleyInertia * pa ** 2 + c.actuators.drive.rotorInertia * c.actuators.drive.reduction ** 2;
  const determinant = Mqq * Mpp - Mqp ** 2;
  if (!(Mqq > 0 && Mpp > 0 && determinant > 1e-14)) throw new Error('Mass matrix is singular; provide positive physical inertia/mass.');
  const gravity = m.gravity * (m.upperMass * k.derivatives.upper[1] + m.lowerMass * k.derivatives.lower[1] + m.wheelMass * k.Cq[1]);
  const gravityDerivative = m.gravity * (m.upperMass * k.secondDerivatives.upper[1] + m.lowerMass * k.secondDerivatives.lower[1] + m.wheelMass * k.Cqq[1]);
  const gravitationalEnergy = m.gravity * (m.upperMass * k.coms.upper[1] + m.lowerMass * k.coms.lower[1] + m.wheelMass * k.C[1]);
  return { massMatrix: [[Mqq, Mqp], [Mqp, Mpp]], determinant, MqqDerivative, gravity, gravityDerivative, gravitationalEnergy, rodInertia: [I1, I2] };
}

function springAt(c, k, dq = 0) {
  const s = c.spring;
  if (s.type === 'none') return { torque: 0, elasticTorque: 0, dampingTorque: 0, energy: 0, force: 0, length: null, lengthJacobian: 0, tangentStiffness: 0, generalizedDamping: 0, anchor: null, attachment: null };
  if (s.type === 'torsion') {
    const delta = k.q - s.restAngle, elasticTorque = s.preloadTorque - s.stiffness * delta;
    return { torque: elasticTorque - s.damping * dq, elasticTorque, dampingTorque: -s.damping * dq,
      energy: 0.5 * s.stiffness * delta ** 2 - s.preloadTorque * delta,
      force: null, length: null, lengthJacobian: null, tangentStiffness: s.stiffness,
      generalizedDamping: s.damping, anchor: null, attachment: null };
  }
  const g = c.geometry, f = s.attachFraction;
  const attachment = s.attachLink === 'upper' ? mul(k.B, f) : add(k.B, mul(v(k.beta), g.lowerLength * f));
  const D = s.attachLink === 'upper' ? mul(dv(k.q), g.upperLength * f) : add(mul(dv(k.q), g.upperLength), mul(dv(k.beta), g.lowerLength * f * k.s));
  const DD = s.attachLink === 'upper' ? mul(ddv(k.q), g.upperLength * f) : add(mul(ddv(k.q), g.upperLength), mul(ddv(k.beta), g.lowerLength * f * k.s ** 2));
  const anchor = [s.anchorX, s.anchorY], d = add(attachment, mul(anchor, -1)), length = Math.hypot(...d);
  if (length < 1e-8) throw new Error('Linear spring attachment coincides with its base anchor.');
  const lengthJacobian = dot(d, D) / length, lengthSecondDerivative = (dot(D, D) + dot(d, DD)) / length - lengthJacobian ** 2 / length;
  const extension = length - s.freeLength, active = !s.tensionOnly || extension > 0;
  const elasticForce = active ? s.linearStiffness * extension : 0;
  const dampingForce = active ? s.linearDamping * lengthJacobian * dq : 0;
  const force = s.tensionOnly ? Math.max(0, elasticForce + dampingForce) : elasticForce + dampingForce;
  const actualDampingForce = force - elasticForce, elasticTorque = -elasticForce * lengthJacobian;
  return { anchor, attachment, length, extension, lengthJacobian, lengthSecondDerivative, force, elasticForce,
    torque: -force * lengthJacobian, elasticTorque, dampingTorque: -actualDampingForce * lengthJacobian,
    energy: active ? 0.5 * s.linearStiffness * extension ** 2 : 0,
    tangentStiffness: active ? s.linearStiffness * lengthJacobian ** 2 + elasticForce * lengthSecondDerivative : 0,
    generalizedDamping: active ? s.linearDamping * lengthJacobian ** 2 : 0 };
}

function external(c, k) {
  const l = c.load;
  return [k.Cq[0] * l.forceX + k.Cq[1] * l.forceY + k.b * l.wheelMoment, k.a * l.wheelMoment];
}

export function pose(input, q, phi = 0, velocities = [0, 0]) {
  const c = normalizeConfig(input); finite(q, 'q'); finite(phi, 'phi');
  const k = kinematics(c, q, phi), i = inertial(c, k), spring = springAt(c, k, velocities[0]);
  const loadTorque = external(c, k), staticFold = i.gravity - loadTorque[0] - spring.elasticTorque;
  const staticDrive = -loadTorque[1];
  const verticalJacobian = k.Cq[1], singular = Math.abs(verticalJacobian) < 1e-5;
  const loadDerivative = k.Cqq[0] * c.load.forceX + k.Cqq[1] * c.load.forceY;
  const loadedTangent = i.gravityDerivative - loadDerivative + spring.tangentStiffness;
  const warnings = [];
  if (singular) warnings.push('Vertical motion is singular here; force/stiffness conversion is undefined.');
  if (q < c.geometry.foldMin || q > c.geometry.foldMax) warnings.push('Pose is outside the selected working range.');
  return { ...k, ...i, x: k.C[0], y: k.C[1], extension: -k.C[1], verticalJacobian,
    spring, loadTorque, velocity: k.jacobian.map(row => row[0] * velocities[0] + row[1] * velocities[1]),
    static: { foldTorque: staticFold, driveTorque: staticDrive, springTorque: spring.elasticTorque,
      gravityTorque: i.gravity, axleLoadTorque: loadTorque[0], totalFoldTorque: staticFold,
      springVerticalForce: singular ? null : spring.elasticTorque / verticalJacobian,
      springVerticalStiffness: singular ? null : spring.tangentStiffness / verticalJacobian ** 2 + spring.elasticTorque * k.Cqq[1] / verticalJacobian ** 3,
      loadedVerticalStiffness: singular ? null : loadedTangent / verticalJacobian ** 2,
      controlledVerticalStiffness: singular ? null : (loadedTangent + c.actuators.fold.kp) / verticalJacobian ** 2,
      verticalDamping: singular ? null : spring.generalizedDamping / verticalJacobian ** 2 },
    singular, valid: warnings.length === 0, warnings };
}

export function virtualWork(input, q, force = [0, 0], moment = 0, velocity = [0, 0]) {
  const k = kinematics(normalizeConfig(input), q);
  const generalized = [k.Cq[0] * force[0] + k.Cq[1] * force[1] + k.b * moment, k.a * moment];
  const axleVelocity = mul(k.Cq, velocity[0]), wheelSpeed = k.b * velocity[0] + k.a * velocity[1];
  return { generalized, axleVelocity, wheelSpeed, inputPower: generalized[0] * velocity[0] + generalized[1] * velocity[1], outputPower: dot(force, axleVelocity) + moment * wheelSpeed };
}

export function workspace(input, count = 161) {
  const c = normalizeConfig(input);
  if (!Number.isInteger(count) || count < 2 || count > 2001) throw new Error('Workspace samples must be an integer between 2 and 2001.');
  return Array.from({ length: count }, (_, n) => pose(c, c.geometry.foldMin + n * (c.geometry.foldMax - c.geometry.foldMin) / (count - 1), c.geometry.driveAngle));
}

/** One guide-constrained shape DOF: solve extension on working branches, then report x residual. */
export function inverseKinematics(input, extension, targetX = 0, preferredQ) {
  const c = normalizeConfig(input); finite(extension, 'extension'); finite(targetX, 'targetX');
  const f = q => -kinematics(c, q).C[1] - extension, roots = [], n = 400;
  let qa = c.geometry.foldMin, fa = f(qa);
  const addRoot = q => { if (!roots.some(r => Math.abs(r - q) < 1e-7)) roots.push(q); };
  for (let j = 1; j <= n; j++) {
    let qb = c.geometry.foldMin + (c.geometry.foldMax - c.geometry.foldMin) * j / n, fb = f(qb);
    if (Math.abs(fa) < 1e-9) addRoot(qa);
    if (fa * fb < 0) {
      let lo = qa, hi = qb, flo = fa;
      for (let it = 0; it < 50; it++) { const mid = (lo + hi) / 2, fm = f(mid); if (flo * fm <= 0) hi = mid; else { lo = mid; flo = fm; } }
      addRoot((lo + hi) / 2);
    }
    if (j === n && Math.abs(fb) < 1e-9) addRoot(qb);
    qa = qb; fa = fb;
  }
  roots.sort((a, b) => Math.abs(a - (preferredQ ?? c.geometry.pose)) - Math.abs(b - (preferredQ ?? c.geometry.pose)));
  const candidates = roots.map(q => { const k = kinematics(c, q); return { q, x: k.C[0], y: k.C[1], extension: -k.C[1], residualX: k.C[0] - targetX, residualExtension: -k.C[1] - extension }; });
  return { reachable: candidates.length > 0, solution: candidates[0] ?? null, candidates,
    note: 'The grounded guide permits one shape coordinate; independent x and y targets cannot generally both be met.' };
}

function solve2(M, r) {
  const d = M[0][0] * M[1][1] - M[0][1] ** 2;
  return [(M[1][1] * r[0] - M[0][1] * r[1]) / d, (M[0][0] * r[1] - M[0][1] * r[0]) / d];
}

/** Output-coordinate four-quadrant constant-power-style sizing envelope.
 * Driving torque falls linearly to zero at no-load speed; braking retains the
 * supplied torque limit. This is an illustrative envelope, not a verified motor map.
 */
export function torqueEnvelope(axis, speed, torque = 1) {
  return speed * torque > 0 ? axis.torqueLimit * Math.max(0, 1 - Math.abs(speed) / axis.noLoadSpeed) : axis.torqueLimit;
}

function limitTorque(axis, speed, command) {
  const limit = torqueEnvelope(axis, speed, command);
  return clamp(command, -limit, limit);
}

function reference(c, t) {
  const m = c.motion;
  let q = m.target, dq = 0, ddq = 0;
  if (m.type === 'step' && t >= m.stepTime) q += m.stepSize;
  if (m.type === 'sine') {
    const w = 2 * Math.PI * m.frequency;
    q += m.amplitude * Math.sin(w * t); dq = m.amplitude * w * Math.cos(w * t); ddq = -m.amplitude * w ** 2 * Math.sin(w * t);
  }
  return { q, dq, ddq, phi: m.initialDriveAngle + m.driveSpeed * t, dphi: m.driveSpeed, ddphi: 0 };
}

function holdingFeedforward(c, q = c.motion.target, velocities = [0, c.motion.driveSpeed]) {
  const k = kinematics(c, q), i = inertial(c, k), s = springAt(c, k, 0), Q = external(c, k);
  return [i.gravity - Q[0] - s.elasticTorque + c.actuators.fold.viscousFriction * velocities[0],
    -Q[1] + c.actuators.drive.viscousFriction * velocities[1]];
}

export function equilibriumFeedforward(input, q, velocities = [0, 0]) {
  const c = normalizeConfig(input);
  return holdingFeedforward(c, q ?? c.geometry.pose, velocities);
}

function activeAxis(c, mode, j) {
  return mode !== 'passive' && !(j === 0 && c.motion.type === 'release');
}

function commands(c, t, state, ff, mode) {
  const r = reference(c, t), refs = [r.q, r.phi], speeds = [r.dq, r.dphi];
  return [c.actuators.fold, c.actuators.drive].map((a, j) => activeAxis(c, mode, j)
    ? a.kp * (refs[j] - state[j]) + a.kd * (speeds[j] - state[j + 2]) + (a.feedforward ? ff[j] : 0) + a.torqueFeedforward : 0);
}

function derivative(c, t, state, ff, mode, ignoreLimits = false) {
  const k = kinematics(c, state[0], state[1]), i = inertial(c, k), s = springAt(c, k, state[2]), Q = external(c, k);
  const cmd = commands(c, t, state, ff, mode), axes = [c.actuators.fold, c.actuators.drive];
  const tau = mode === 'finite' ? state.slice(4, 6) : cmd;
  // The ideal MIT comparison is intentionally unsaturated and has no lag.
  const torque = tau.map((val, j) => !activeAxis(c, mode, j) ? 0 : mode === 'finite' && !ignoreLimits ? limitTorque(axes[j], state[j + 2], val) : val);
  let disturbance = 0;
  if (t >= c.load.disturbanceStart && t < c.load.disturbanceStart + c.load.disturbanceDuration) disturbance = c.load.disturbanceTorque;
  const rhs = [torque[0] + s.torque + Q[0] + disturbance - i.gravity - 0.5 * i.MqqDerivative * state[2] ** 2 - axes[0].viscousFriction * state[2],
    torque[1] + Q[1] - axes[1].viscousFriction * state[3]];
  const acceleration = solve2(i.massMatrix, rhs);
  const result = [state[2], state[3], ...acceleration];
  if (mode === 'finite') for (let j = 0; j < 2; j++) {
    const desired = activeAxis(c, mode, j) ? (ignoreLimits ? cmd[j] : limitTorque(axes[j], state[j + 2], cmd[j])) : 0;
    const rate = (desired - state[j + 4]) / axes[j].lag;
    result.push(ignoreLimits ? rate : clamp(rate, -axes[j].slewRate, axes[j].slewRate));
  }
  return result;
}

function rk4(c, t, x, dt, ff, mode) {
  const evaluate = (time, state) => derivative(c, time, state, ff, mode);
  const shift = (v, k, h) => v.map((val, j) => val + h * k[j]);
  const a = evaluate(t, x), b = evaluate(t + dt / 2, shift(x, a, dt / 2));
  const d = evaluate(t + dt / 2, shift(x, b, dt / 2)), e = evaluate(t + dt, shift(x, d, dt));
  const next = x.map((val, j) => val + dt * (a[j] + 2 * b[j] + 2 * d[j] + e[j]) / 6);
  if (mode === 'finite') for (let j = 0; j < 2; j++) next[j + 4] = activeAxis(c, mode, j) ? limitTorque([c.actuators.fold, c.actuators.drive][j], next[j + 2], next[j + 4]) : 0;
  return next;
}

function sample(c, t, state, ff, mode) {
  const k = kinematics(c, state[0], state[1]), i = inertial(c, k), s = springAt(c, k, state[2]);
  const tauCommand = commands(c, t, state, ff, mode), r = reference(c, t), axes = [c.actuators.fold, c.actuators.drive];
  const tauActual = mode === 'finite' ? state.slice(4, 6).map((val, j) => activeAxis(c, mode, j) ? limitTorque(axes[j], state[j + 2], val) : 0) : tauCommand;
  const M = i.massMatrix, kineticEnergy = 0.5 * (M[0][0] * state[2] ** 2 + 2 * M[0][1] * state[2] * state[3] + M[1][1] * state[3] ** 2);
  const loadPotential = -c.load.forceX * k.C[0] - c.load.forceY * k.C[1] - c.load.wheelMoment * k.wheelAngle;
  const stateDerivative = derivative(c, t, state, ff, mode);
  const envelopes = axes.map((a, j) => torqueEnvelope(a, state[j + 2], tauCommand[j]));
  return { t, q: state[0], phi: state[1], dq: state[2], dphi: state[3], ddq: stateDerivative[2], ddphi: stateDerivative[3],
    x: k.C[0], y: k.C[1], extension: -k.C[1], dx: k.Cq[0] * state[2], dy: k.Cq[1] * state[2], beta: k.beta,
    wheelAngle: k.wheelAngle, wheelSpeed: k.b * state[2] + k.a * state[3],
    qRef: r.q, phiRef: r.phi, qRefSpeed: r.dq, phiRefSpeed: r.dphi,
    tauCommand, tauActual, torqueEnvelope: envelopes,
    torqueLimited: tauCommand.map((val, j) => mode === 'finite' && activeAxis(c, mode, j) && Math.abs(val) > envelopes[j] + 1e-7),
    speedExceeded: axes.map((a, j) => Math.abs(state[j + 2]) > a.noLoadSpeed),
    slewLimited: axes.map((a, j) => mode === 'finite' && Math.abs((limitTorque(a, state[j + 2], tauCommand[j]) - state[j + 4]) / a.lag) > a.slewRate),
    springTorque: s.torque, springForce: s.force, springLength: s.length,
    gravityTorque: i.gravity, loadTorque: external(c, k), kineticEnergy,
    springEnergy: s.energy, gravitationalEnergy: i.gravitationalEnergy, loadPotential,
    energy: kineticEnergy + s.energy + i.gravitationalEnergy + loadPotential,
    motorPower: tauActual[0] * state[2] + tauActual[1] * state[3],
    foldPower: tauActual[0] * state[2], drivePower: tauActual[1] * state[3],
    foldError: r.q - state[0], wheelError: r.phi - state[1],
    springDissipation: -s.dampingTorque * state[2],
    frictionDissipation: axes[0].viscousFriction * state[2] ** 2 + axes[1].viscousFriction * state[3] ** 2 };
}

function aggregate(samples, integrals, elapsed, mode, c) {
  const e = integrals.extrema;
  const rms = integrals.torque2.map(v => Math.sqrt(v / Math.max(elapsed, 1e-9)));
  return { duration: elapsed, sampleCount: samples.length,
    peakFoldTorque: e.torque[0].magnitude, peakDriveTorque: e.torque[1].magnitude, peakTorqueEvents: e.torque,
    rmsFoldTorque: rms[0], rmsDriveTorque: rms[1],
    continuousTorqueExceeded: [rms[0] > c.actuators.fold.continuousTorque, rms[1] > c.actuators.drive.continuousTorque],
    peakFoldSpeed: e.foldSpeed, peakDriveSpeed: e.driveSpeed, peakWheelSpeed: e.wheelSpeed,
    peakFoldError: e.foldError, rmsFoldError: Math.sqrt(integrals.error2 / Math.max(elapsed, 1e-9)),
    peakMotorPower: e.power, motorWork: integrals.work, positiveMotorWork: integrals.positiveWork,
    dampingEnergy: integrals.dissipation, torqueLimitTime: integrals.torqueLimitTime,
    speedLimitTime: integrals.speedLimitTime, slewLimitTime: integrals.slewLimitTime,
    minAngle: e.minAngle, maxAngle: e.maxAngle,
    minExtension: e.minExtension, maxExtension: e.maxExtension,
    energyChange: samples.at(-1).energy - samples[0].energy, mode,
    finalFoldError: samples.at(-1).foldError, finalWheelError: samples.at(-1).wheelError };
}

/** Forward dynamics with the chassis pivot fixed. No wheel-ground contact is inferred. */
export function runSimulation(input) {
  const c = normalizeConfig(input), mode = c.simulation.mode, ff = holdingFeedforward(c);
  const warnings = ['Fixed chassis pivot and prescribed axle force; this is not a terrain-contact or whole-vehicle simulation.',
    'Motor torque–speed envelopes are illustrative output-coordinate limits. Thermal/current predictions require measured actuator data.'];
  if (mode === 'ideal') warnings.push('Ideal MIT is unsaturated with instantaneous torque.');
  if (mode === 'passive' || c.motion.type === 'release') warnings.push('Passive/release folding axis has no motor holding feedforward.');
  if (c.motion.type === 'step' || c.motion.type === 'sine') warnings.push('Holding feedforward is constant at the base target; it does not track the moving reference.');
  const refs = [c.motion.target, c.motion.target + (c.motion.type === 'step' ? c.motion.stepSize : 0), c.motion.target - (c.motion.type === 'sine' ? c.motion.amplitude : 0), c.motion.target + (c.motion.type === 'sine' ? c.motion.amplitude : 0)];
  if (refs.some(q => q < c.geometry.foldMin || q > c.geometry.foldMax)) warnings.push('A requested reference lies outside the working range.');
  const stability = localStability(c, mode);
  const poleRate = stability.poles.reduce((rate, p) => Math.max(rate, Math.hypot(p.real, p.imag)), 0);
  // Conservative local time-scale guard; convergence should still be checked for
  // nonlinear extreme poses. This prevents coarse user dt from creating instability.
  const integrationDt = Math.min(c.simulation.dt, poleRate > 0 ? 0.25 / poleRate : c.simulation.dt,
    mode === 'finite' ? Math.min(c.actuators.fold.lag, c.actuators.drive.lag) / 3 : c.simulation.dt);
  if (c.simulation.duration / integrationDt > 200000) throw new Error('Requested gains/inertias require more than 200,000 stable integration steps. Reduce duration or revise stiffness/inertia.');
  if (integrationDt < c.simulation.dt * 0.999) warnings.push(`Integration step reduced from ${c.simulation.dt} to ${integrationDt.toPrecision(4)} s to resolve the local pole/lag time scale.`);
  let state = [c.motion.initialAngle, c.motion.initialDriveAngle, c.motion.initialVelocity, c.motion.initialDriveVelocity];
  if (mode === 'finite') state.push(...[c.actuators.fold, c.actuators.drive].map((a, j) => activeAxis(c, mode, j) ? limitTorque(a, state[j + 2], (a.feedforward ? ff[j] : 0) + a.torqueFeedforward) : 0));
  const samples = [], integrals = { torque2: [0, 0], error2: 0, work: 0, positiveWork: 0, dissipation: 0, torqueLimitTime: [0, 0], speedLimitTime: [0, 0], slewLimitTime: [0, 0],
    extrema: { torque: [{ magnitude: -1 }, { magnitude: -1 }], foldSpeed: 0, driveSpeed: 0, wheelSpeed: 0, foldError: 0, power: 0, minAngle: Infinity, maxAngle: -Infinity, minExtension: Infinity, maxExtension: -Infinity } };
  const recordExtrema = s => {
    const e = integrals.extrema;
    for (let j = 0; j < 2; j++) if (Math.abs(s.tauActual[j]) > e.torque[j].magnitude) e.torque[j] = { magnitude: Math.abs(s.tauActual[j]), value: s.tauActual[j], time: s.t, q: s.q, phi: s.phi, outputSpeed: j === 0 ? s.dq : s.dphi, shaftSpeed: (j === 0 ? s.dq : s.dphi) * [c.actuators.fold, c.actuators.drive][j].reduction };
    e.foldSpeed = Math.max(e.foldSpeed, Math.abs(s.dq)); e.driveSpeed = Math.max(e.driveSpeed, Math.abs(s.dphi)); e.wheelSpeed = Math.max(e.wheelSpeed, Math.abs(s.wheelSpeed));
    e.foldError = Math.max(e.foldError, Math.abs(s.foldError)); e.power = Math.max(e.power, Math.abs(s.motorPower));
    e.minAngle = Math.min(e.minAngle, s.q); e.maxAngle = Math.max(e.maxAngle, s.q); e.minExtension = Math.min(e.minExtension, s.extension); e.maxExtension = Math.max(e.maxExtension, s.extension);
  };
  let t = 0, nextOutput = 0, status = { code: 'complete', message: 'Run completed.' }, previous = sample(c, 0, state, ff, mode);
  samples.push(previous); recordExtrema(previous); nextOutput = c.simulation.outputDt;
  if (Math.abs(kinematics(c, state[0]).Cq[1]) < 1e-5) status = { code: 'vertical-singularity', message: 'Initial pose is a vertical-motion singularity.' };
  for (let n = 0; t < c.simulation.duration - 1e-12; n++) {
    if (status.code !== 'complete') break;
    const dt = Math.min(integrationDt, c.simulation.duration - t);
    const candidate = rk4(c, t, state, dt, ff, mode);
    if (candidate.some(v => !Number.isFinite(v))) { status = { code: 'nonfinite', message: 'Integrator produced a nonfinite state; lower dt or revise gains.' }; break; }
    const outOfRange = candidate[0] < c.geometry.foldMin || candidate[0] > c.geometry.foldMax;
    if (outOfRange) {
      // Retain the last valid state, without inventing a hard-stop collision impulse.
      status = { code: 'working-limit', message: `Fold motion reached the ${candidate[0] < c.geometry.foldMin ? 'minimum' : 'maximum'} working bound.` }; break;
    }
    const k = kinematics(c, candidate[0]);
    if (Math.abs(k.Cq[1]) < 1e-5) { status = { code: 'vertical-singularity', message: 'Run reached a vertical-motion singularity.' }; break; }
    state = candidate; t += dt;
    const current = sample(c, t, state, ff, mode); recordExtrema(current);
    for (let j = 0; j < 2; j++) {
      integrals.torque2[j] += dt * (previous.tauActual[j] ** 2 + current.tauActual[j] ** 2) / 2;
      integrals.torqueLimitTime[j] += dt * (+previous.torqueLimited[j] + +current.torqueLimited[j]) / 2;
      integrals.speedLimitTime[j] += dt * (+previous.speedExceeded[j] + +current.speedExceeded[j]) / 2;
      integrals.slewLimitTime[j] += dt * (+previous.slewLimited[j] + +current.slewLimited[j]) / 2;
    }
    integrals.error2 += dt * (previous.foldError ** 2 + current.foldError ** 2) / 2;
    integrals.work += dt * (previous.motorPower + current.motorPower) / 2;
    integrals.positiveWork += dt * (Math.max(0, previous.motorPower) + Math.max(0, current.motorPower)) / 2;
    integrals.dissipation += dt * (previous.springDissipation + previous.frictionDissipation + current.springDissipation + current.frictionDissipation) / 2;
    if (t >= nextOutput - 1e-10 || t >= c.simulation.duration - 1e-10) { samples.push(current); nextOutput += c.simulation.outputDt; }
    previous = current;
  }
  if (samples.at(-1).t !== t) samples.push(previous);
  if (status.code !== 'complete') warnings.push(status.message);
  return { config: c, samples, summary: aggregate(samples, integrals, t, mode, c), status, warnings,
    feedforward: ff, stability,
    metadata: { schema: 'belt-linkage-v1', units: 'SI: m, kg, s, rad, N, N·m',
      coordinates: ['q: folding CCW from down vertical', 'phi: independent coaxial drive input angle'],
      topology: 'Grounded guide belt + two open wheel-drive belts; compound knee on free bearing.',
      scope: 'Fixed-base planar linkage; prescribed axle load; illustrative motor limits.',
      feedforwardPolicy: 'Constant equilibrium bias at motion.target; no state-dependent gravity compensation.',
      requestedDt: c.simulation.dt, integrationDt, outputDt: c.simulation.outputDt,
      solver: 'RK4, output inertias and moving-carrier no-slip belt constraints', timestamp: new Date().toISOString() } };
}

/** Required torques for specified motion, with physical spring/damper included. */
export function inverseDynamics(input, q, phi, dq, dphi, ddq, ddphi) {
  const c = normalizeConfig(input), k = kinematics(c, q, phi), i = inertial(c, k), s = springAt(c, k, dq), Q = external(c, k), M = i.massMatrix;
  const tau = [M[0][0] * ddq + M[0][1] * ddphi + 0.5 * i.MqqDerivative * dq ** 2 + i.gravity - s.torque - Q[0] + c.actuators.fold.viscousFriction * dq,
    M[1][0] * ddq + M[1][1] * ddphi - Q[1] + c.actuators.drive.viscousFriction * dphi];
  return { tau, pose: k, spring: s, power: tau[0] * dq + tau[1] * dphi, rotorSpeeds: [c.actuators.fold.reduction * dq, c.actuators.drive.reduction * dphi],
    motorTorques: [tau[0] / c.actuators.fold.reduction, tau[1] / c.actuators.drive.reduction] };
}

export function prescribedMotion(input) {
  const c = normalizeConfig(input), samples = [];
  if (c.motion.type === 'step') throw new Error('An instantaneous position step has unbounded inverse-dynamics demand; choose a sine or hold reference.');
  for (let t = 0; t <= c.simulation.duration + 1e-10; t += c.simulation.outputDt) {
    const r = reference(c, t), d = inverseDynamics(c, r.q, r.phi, r.dq, r.dphi, r.ddq, r.ddphi);
    samples.push({ t, q: r.q, phi: r.phi, dq: r.dq, dphi: r.dphi, ddq: r.ddq, ddphi: r.ddphi,
      x: d.pose.C[0], y: d.pose.C[1], wheelAngle: d.pose.wheelAngle, wheelSpeed: d.pose.b * r.dq + d.pose.a * r.dphi,
      tau: d.tau, springTorque: d.spring.torque, motorPower: d.power });
  }
  return { config: c, samples, note: 'Prescribed ideal motion; demand only, not an achieved actuator trajectory.' };
}

export function passiveEquilibria(input) {
  const c = normalizeConfig(input), residual = q => {
    const k = kinematics(c, q), i = inertial(c, k), s = springAt(c, k);
    return i.gravity - external(c, k)[0] - s.elasticTorque;
  };
  const roots = [], count = 400;
  let qa = c.geometry.foldMin, fa = residual(qa);
  for (let j = 1; j <= count; j++) {
    const qb = c.geometry.foldMin + (c.geometry.foldMax - c.geometry.foldMin) * j / count, fb = residual(qb);
    if (Math.abs(fa) < 1e-8 && !roots.some(r => Math.abs(r.q - qa) < 1e-6)) roots.push({ q: qa });
    if (fa * fb < 0) {
      let lo = qa, hi = qb, flo = fa;
      for (let n = 0; n < 50; n++) { const mid = (lo + hi) / 2, fm = residual(mid); if (flo * fm <= 0) hi = mid; else { lo = mid; flo = fm; } }
      roots.push({ q: (lo + hi) / 2 });
    }
    if (j === count && Math.abs(fb) < 1e-8) roots.push({ q: qb });
    qa = qb; fa = fb;
  }
  return roots.map(({ q }) => {
    const p = pose(c, q), tangent = p.gravityDerivative - p.Cqq[0] * c.load.forceX - p.Cqq[1] * c.load.forceY + p.spring.tangentStiffness;
    return { q, residual: residual(q), extension: p.extension, tangentStiffness: tangent, stableFold: tangent > 0, singular: p.singular };
  });
}

const complexAdd = (a, b) => [a[0] + b[0], a[1] + b[1]];
const complexSub = (a, b) => [a[0] - b[0], a[1] - b[1]];
const complexMul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
const complexDiv = (a, b) => { const d = b[0] ** 2 + b[1] ** 2; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; };

function complexSolve(A, b) {
  const n = A.length, rows = A.map((row, j) => [...row.map(v => [...v]), [...b[j]]]);
  for (let col = 0; col < n; col++) {
    let pivot = col;
    for (let row = col + 1; row < n; row++) if (Math.hypot(...rows[row][col]) > Math.hypot(...rows[pivot][col])) pivot = row;
    if (Math.hypot(...rows[pivot][col]) < 1e-16) return Array.from({ length: n }, () => [NaN, NaN]);
    [rows[col], rows[pivot]] = [rows[pivot], rows[col]];
    const divisor = rows[col][col];
    for (let j = col; j <= n; j++) rows[col][j] = complexDiv(rows[col][j], divisor);
    for (let row = 0; row < n; row++) if (row !== col) {
      const factor = rows[row][col];
      for (let j = col; j <= n; j++) rows[row][j] = complexSub(rows[row][j], complexMul(factor, rows[col][j]));
    }
  }
  return rows.map(row => row[n]);
}

function bode(A, B, k) {
  const n = A.length;
  return Array.from({ length: 121 }, (_, j) => {
    const frequencyHz = 0.05 * (200 / 0.05) ** (j / 120), w = 2 * Math.PI * frequencyHz;
    const R = A.map((row, r) => row.map((val, col) => [-val, r === col ? w : 0]));
    const H = complexSolve(R, B.map(row => [row[0], 0]));
    const q = H[0], y = mul(q, k.Cq[1]);
    const wheel = complexAdd(mul(H[0], k.b), mul(H[1], k.a));
    const magnitude = z => Math.hypot(...z), phase = z => Math.atan2(z[1], z[0]) * 180 / Math.PI;
    const qMagnitude = magnitude(q), yMagnitude = magnitude(y);
    const qMagnitudeDb = 20 * Math.log10(Math.max(qMagnitude, 1e-30)), yMagnitudeDb = 20 * Math.log10(Math.max(yMagnitude, 1e-30));
    return { frequencyHz, qMagnitude, qMagnitudeDb, qPhaseDeg: phase(q), yMagnitude, yMagnitudeDb, yPhaseDeg: phase(y),
      wheelMagnitude: magnitude(wheel), wheelPhaseDeg: phase(wheel), magnitudeDb: qMagnitudeDb, phaseDeg: phase(q) };
  });
}

/** Frozen operating-point Jacobian. True local stability requires equilibrium and
 * unsaturated actuators; those validity conditions are explicit in the result.
 * Feedforward is a constant bias, so load/spring geometric stiffness remains.
 */
export function localStability(input, mode) {
  const c = normalizeConfig(input); mode ??= c.simulation.mode;
  if (!['passive', 'ideal', 'finite'].includes(mode)) throw new Error('Invalid stability mode.');
  const local = { ...c, motion: { ...c.motion, type: c.motion.type === 'release' ? 'release' : 'hold', target: c.geometry.pose }, load: { ...c.load, disturbanceTorque: 0 } };
  const q = c.geometry.pose, phi = c.motion.initialDriveAngle, speed = c.motion.driveSpeed;
  const k = kinematics(c, q, phi), i = inertial(c, k), s = springAt(c, k, 0), ff = holdingFeedforward(local, q, [0, speed]);
  let x = [q, phi, 0, speed];
  const cmd = commands(local, 0, x, ff, mode), axes = [c.actuators.fold, c.actuators.drive];
  const actual = cmd.map((v, j) => mode === 'finite' ? limitTorque(axes[j], x[j + 2], v) : v);
  if (mode === 'finite') x.push(...actual);
  const nominal = derivative(local, 0, x, ff, mode, true), n = x.length;
  const A = Array.from({ length: n }, () => Array(n).fill(0));
  for (let col = 0; col < n; col++) {
    const h = 1e-5 * Math.max(1, Math.abs(x[col])), plus = [...x], minus = [...x]; plus[col] += h; minus[col] -= h;
    const fp = derivative(local, 0, plus, ff, mode, true), fm = derivative(local, 0, minus, ff, mode, true);
    for (let row = 0; row < n; row++) A[row][col] = (fp[row] - fm[row]) / (2 * h);
  }
  // B maps additive generalized disturbance torque at fold and drive outputs.
  const inv0 = solve2(i.massMatrix, [1, 0]), inv1 = solve2(i.massMatrix, [0, 1]);
  const B = Array.from({ length: n }, () => [0, 0]); B[2] = [inv0[0], inv1[0]]; B[3] = [inv0[1], inv1[1]];
  const eig = new EigenvalueDecomposition(new Matrix(A), { assumeSymmetric: false });
  const poles = eig.realEigenvalues.map((real, j) => {
    const imag = eig.imaginaryEigenvalues[j], wn = Math.hypot(real, imag), marginal = wn < 1e-6;
    return { real, imag, frequencyHz: Math.abs(imag) / (2 * Math.PI), naturalFrequencyHz: wn / (2 * Math.PI),
      dampingRatio: marginal ? null : -real / wn, classification: marginal ? 'neutral' : real > 1e-6 ? 'unstable' : real < -1e-6 ? 'decaying' : 'undamped' };
  });
  const Q = external(c, k), equilibriumResidual = [actual[0] + s.elasticTorque + Q[0] - i.gravity,
    actual[1] + Q[1] - c.actuators.drive.viscousFriction * speed];
  const isEquilibrium = equilibriumResidual.every(v => Math.abs(v) < 1e-6);
  const saturated = mode === 'finite' && cmd.some((v, j) => Math.abs(v) >= torqueEnvelope(axes[j], x[j + 2], v) - 1e-7);
  const warnings = [];
  if (!isEquilibrium) warnings.push('Selected pose is not an equilibrium for this mode; poles describe a frozen pose, not stability about a resting solution.');
  if (saturated) warnings.push('Nominal actuator demand reaches its envelope; unsaturated linear poles/frequency response are invalid at this operating point.');
  if (c.spring.type === 'linear' && c.spring.tensionOnly && Math.abs(s.extension) < 1e-6) warnings.push('Spring lies at a tension-only engagement boundary; a single smooth linearization is insufficient.');
  if (poles.some(p => p.classification === 'neutral')) warnings.push('A neutral pole may be the free wheel phase; it is marginal and does not imply an unstable folding axis.');
  if (poles.some(p => Math.abs(p.real) <= 1e-6)) warnings.push('Nondecaying modes require separate review: poles with zero real part do not prove bounded full-state motion; an undamped free wheel can drift in angle.');
  const stable = poles.every(p => p.real <= 1e-6), asymptoticallyStable = poles.every(p => p.real < -1e-6);
  return { mode, q, phi, driveSpeed: speed, state: x, stateNames: ['q', 'phi', 'dq', 'dphi', ...(mode === 'finite' ? ['foldTorque', 'driveTorque'] : [])],
    A, stateMatrix: A, B, poles, eigenvalues: poles, stable, noExponentialGrowth: stable, asymptoticallyStable,
    stableMeaning: 'No positive-real poles; nondecaying/Jordan modes can still be unbounded and need separate review.',
    valid: isEquilibrium && !saturated, isEquilibrium, saturated, equilibriumResidual,
    feedforward: ff, nominalTorque: actual, nominalDerivative: nominal, passiveEquilibria: passiveEquilibria(c),
    physicalFoldStiffness: i.gravityDerivative - k.Cqq[0] * c.load.forceX - k.Cqq[1] * c.load.forceY + s.tangentStiffness,
    frequencyResponse: bode(A, B, k),
    frequencyResponseUnits: { q: 'rad/(N·m)', y: 'm/(N·m)', input: 'additive folding-axis disturbance torque', dbReference: '1 rad/(N·m) or 1 m/(N·m)' },
    warnings, scope: 'Small-signal, fixed-base, unsaturated local model; constant holding feedforward. Nonzero drive speed uses a translating phase-reference frame.' };
}

export function exportCSV(result) {
  if (!Array.isArray(result?.samples)) throw new Error('Result must contain samples.');
  const scalar = [
    ['t', 't_s'], ['q', 'q_rad'], ['phi', 'phi_rad'], ['dq', 'dq_rad_s'], ['dphi', 'dphi_rad_s'],
    ['ddq', 'ddq_rad_s2'], ['ddphi', 'ddphi_rad_s2'], ['x', 'x_m'], ['y', 'y_m'], ['extension', 'extension_m'], ['dx', 'dx_m_s'], ['dy', 'dy_m_s'],
    ['beta', 'beta_rad'], ['wheelAngle', 'wheel_angle_rad'], ['wheelSpeed', 'wheel_speed_rad_s'],
    ['qRef', 'q_reference_rad'], ['phiRef', 'phi_reference_rad'], ['qRefSpeed', 'fold_reference_speed_rad_s'], ['phiRefSpeed', 'drive_reference_speed_rad_s'],
    ['springTorque', 'spring_torque_Nm'], ['springForce', 'spring_force_N'], ['springLength', 'spring_length_m'], ['gravityTorque', 'gravity_torque_Nm'],
    ['kineticEnergy', 'kinetic_energy_J'], ['springEnergy', 'spring_energy_J'], ['gravitationalEnergy', 'gravitational_energy_J'], ['loadPotential', 'prescribed_load_potential_J'], ['energy', 'mechanical_energy_J'],
    ['motorPower', 'motor_power_W'], ['foldPower', 'fold_motor_power_W'], ['drivePower', 'drive_motor_power_W'],
    ['foldError', 'fold_error_rad'], ['wheelError', 'drive_error_rad'], ['springDissipation', 'spring_dissipation_W'], ['frictionDissipation', 'friction_dissipation_W']
  ];
  const columns = scalar.map(([key, header]) => [header, s => s[key]]);
  for (const [key, suffix] of [['tauCommand', 'command_Nm'], ['tauActual', 'actual_Nm'], ['torqueEnvelope', 'torque_envelope_Nm'], ['loadTorque', 'prescribed_load_torque_Nm'], ['torqueLimited', 'torque_limited'], ['speedExceeded', 'speed_exceeded'], ['slewLimited', 'slew_limited']]) {
    for (let j = 0; j < 2; j++) columns.push([`${j === 0 ? 'fold' : 'drive'}_${suffix}`, s => s[key]?.[j]]);
  }
  const cell = v => v == null ? '' : typeof v === 'boolean' ? String(+v) : Number.isFinite(v) ? String(v) : '';
  return [columns.map(([header]) => header).join(','), ...result.samples.map(s => columns.map(([, getter]) => cell(getter(s))).join(','))].join('\r\n');
}

export const simulate = runSimulation;
export const analyzeStability = localStability;
