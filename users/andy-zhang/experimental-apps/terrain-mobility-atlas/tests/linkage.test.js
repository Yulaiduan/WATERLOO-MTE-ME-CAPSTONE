import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import {
  defaultConfig, normalizeConfig, pose, virtualWork, inverseKinematics, workspace,
  equilibriumFeedforward, passiveEquilibria, runSimulation, localStability,
  inverseDynamics, prescribedMotion, torqueEnvelope, exportCSV
} from '../src/linkage/model.js';

const close = (a, b, tol = 1e-8) => assert.ok(Math.abs(a - b) <= tol * Math.max(1, Math.abs(a), Math.abs(b)), `${a} != ${b}`);
const clone = c => structuredClone(c);
function unloaded() {
  const c = defaultConfig(); c.load.forceY = 0; c.mass.gravity = 0;
  c.spring.restAngle = 0.7; c.motion.target = c.geometry.pose = 0.7;
  c.motion.initialAngle = 0.8; c.motion.type = 'hold';
  c.actuators.fold.viscousFriction = c.actuators.drive.viscousFriction = 0;
  c.simulation.duration = 1; return c;
}
const recursiveClose = (actual, expected, tol = 1e-8) => {
  if (Array.isArray(expected)) expected.forEach((value, j) => recursiveClose(actual[j], value, tol));
  else close(actual, expected, tol);
};

test('grounded 2:1 guide produces a straight-line equal-link axle and independent wheel spin', () => {
  const c = defaultConfig();
  for (const q of [0.12, 0.4, 0.9, 1.38]) {
    const p = pose(c, q, 3.2);
    close(p.x, 0); close(p.y, -0.36 * Math.cos(q)); close(p.beta, -q);
    close(p.wheelAngle, 3.2); close(p.jacobian[2][0], 0); close(p.jacobian[2][1], 1);
    close(p.massMatrix[0][1], 0); assert.equal(p.jacobian[0][1], 0); assert.equal(p.jacobian[1][1], 0);
  }
});

test('nonunit open drive belts include moving-carrier velocities', () => {
  const c = defaultConfig(); Object.assign(c.geometry, { guideRatio: 1.7, guidePhase: 0.2, driveRatio1: 1.3, driveRatio2: 0.8 });
  const q = 0.63, phi = 1.2, dq = 0.8, dphi = -2.1, p = pose(c, q, phi, [dq, dphi]);
  const betaSpeed = (1 - 1.7) * dq, compoundSpeed = 1.3 * dphi + (1 - 1.3) * dq;
  close(p.velocity[2], 0.8 * compoundSpeed + (1 - 0.8) * betaSpeed);
  close(p.wheelAngle, 0.8 * (1.3 * phi + (1 - 1.3) * q) + (1 - 0.8) * p.beta);
});

test('Jacobian and axle curvature match central finite differences for unequal geometry', () => {
  const c = defaultConfig(); Object.assign(c.geometry, { upperLength: 0.23, lowerLength: 0.16, guideRatio: 1.6, guidePhase: 0.25, driveRatio1: 1.4, driveRatio2: 0.7 });
  const q = 0.65, phi = 0.3, h = 1e-5, p = pose(c, q, phi), a = pose(c, q - h, phi), b = pose(c, q + h, phi);
  for (let j = 0; j < 2; j++) { close(p.Cq[j], (b.C[j] - a.C[j]) / (2 * h)); close(p.Cqq[j], (b.Cq[j] - a.Cq[j]) / (2 * h)); }
  close(p.jacobian[2][0], (b.wheelAngle - a.wheelAngle) / (2 * h));
  close(p.jacobian[2][1], (pose(c, q, phi + h).wheelAngle - pose(c, q, phi - h).wheelAngle) / (2 * h));
});

test('virtual-work mapping conserves instantaneous force and torque power', () => {
  const c = defaultConfig(); Object.assign(c.geometry, { guideRatio: 1.8, driveRatio1: 1.5, driveRatio2: 0.7 });
  const result = virtualWork(c, 0.73, [7, 61], -1.2, [0.8, -2.3]);
  close(result.inputPower, result.outputPower);
});

test('mass matrix is positive symmetric with rotor inertia reflected exactly once', () => {
  const c = defaultConfig(); Object.assign(c.geometry, { upperLength: 0.23, lowerLength: 0.16, driveRatio1: 1.4, driveRatio2: 0.7 });
  for (const p of workspace(c, 31)) {
    const M = p.massMatrix; close(M[0][1], M[1][0]); assert.ok(M[0][0] > 0 && M[1][1] > 0 && p.determinant > 0);
  }
  const base = pose(c, 0.6).massMatrix; c.actuators.fold.rotorInertia += 0.0001;
  close(pose(c, 0.6).massMatrix[0][0] - base[0][0], 0.0001 * c.actuators.fold.reduction ** 2);
});

test('gravity and inertial derivatives match energy and matrix differences', () => {
  const c = defaultConfig(); Object.assign(c.geometry, { upperLength: 0.23, lowerLength: 0.16, guideRatio: 1.6, guidePhase: 0.25 });
  const h = 1e-5, q = 0.65, p = pose(c, q), a = pose(c, q - h), b = pose(c, q + h);
  close(p.gravity, (b.gravitationalEnergy - a.gravitationalEnergy) / (2 * h));
  close(p.gravityDerivative, (b.gravity - a.gravity) / (2 * h));
  close(p.MqqDerivative, (b.massMatrix[0][0] - a.massMatrix[0][0]) / (2 * h));
});

test('torsion and anchored linear spring torques and tangents derive from stored energy', () => {
  for (const type of ['torsion', 'linear']) {
    const c = defaultConfig(); c.spring.type = type; c.spring.attachLink = 'lower'; c.spring.preloadTorque = 1.2;
    const q = 0.65, h = 1e-5, p = pose(c, q), a = pose(c, q - h), b = pose(c, q + h);
    close(p.spring.elasticTorque, -(b.spring.energy - a.spring.energy) / (2 * h));
    close(p.spring.tangentStiffness, -(b.spring.elasticTorque - a.spring.elasticTorque) / (2 * h), 1e-7);
  }
});

test('linear spring is force-free at its selected rest length and tension-only cannot push', () => {
  const c = defaultConfig(); c.spring.type = 'linear'; c.spring.freeLength = pose(c, 0.6).spring.length;
  close(pose(c, 0.6).spring.force, 0); close(pose(c, 0.6).spring.torque, 0);
  c.spring.freeLength = 0.01; c.spring.tensionOnly = true; c.spring.linearDamping = 500;
  const p = pose(c, 0.6), contracting = -100 * Math.sign(p.spring.lengthJacobian);
  const moving = pose(c, 0.6, 0, [contracting, 0]);
  close(moving.spring.force, 0); close(moving.spring.torque, 0);
  assert.ok(-moving.spring.dampingTorque * contracting >= 0);
});

test('preload-aware spring equivalent vertical stiffness matches force derivative', () => {
  const c = defaultConfig(); c.spring.preloadTorque = 1.3;
  const q = 0.65, h = 1e-5, p = pose(c, q), a = pose(c, q - h), b = pose(c, q + h);
  const numeric = -(b.static.springVerticalForce - a.static.springVerticalForce) / (b.y - a.y);
  close(p.static.springVerticalStiffness, numeric, 1e-7);
  assert.ok(Math.abs(p.static.springVerticalStiffness - c.spring.stiffness / p.verticalJacobian ** 2) > 1);
});

test('guide-constrained IK finds extension branch and reports incompatible x target', () => {
  const c = defaultConfig(), p = pose(c, 0.72), solution = inverseKinematics(c, p.extension, 0.1);
  assert.equal(solution.reachable, true); close(solution.solution.q, 0.72); close(solution.solution.residualX, -0.1);
  assert.equal(inverseKinematics(c, 10).reachable, false);
});

test('equilibrium holding feedforward balances spring, gravity and prescribed axle load', () => {
  const c = defaultConfig(); c.motion.type = 'hold'; c.motion.initialAngle = c.motion.target;
  const p = pose(c, c.motion.target), ff = equilibriumFeedforward(c, c.motion.target);
  close(ff[0], p.static.foldTorque); close(ff[1], p.static.driveTorque);
  for (const mode of ['ideal', 'finite']) {
    c.simulation.mode = mode; const r = runSimulation(c);
    close(r.samples.at(-1).q, c.motion.target); close(r.samples.at(-1).dq, 0);
    assert.equal(r.stability.valid, true); recursiveClose(r.stability.equilibriumResidual, [0, 0]);
  }
});

test('passive mode has no hidden holding feedforward and identifies its true equilibrium', () => {
  const c = defaultConfig(); c.simulation.mode = 'passive'; c.motion.type = 'hold';
  const equilibria = passiveEquilibria(c); assert.equal(equilibria.length, 1); assert.ok(equilibria[0].stableFold);
  assert.equal(localStability(c, 'passive').valid, false);
  c.geometry.pose = c.motion.target = c.motion.initialAngle = equilibria[0].q;
  const r = runSimulation(c); close(r.samples.at(-1).q, equilibria[0].q);
  assert.ok(r.samples.every(s => s.tauActual.every(v => v === 0))); assert.equal(r.stability.valid, true);
  assert.ok(r.stability.poles.some(p => p.classification === 'neutral')); assert.equal(r.stability.stable, true);
});

test('unloaded ideal poles and frequency response match analytical spring/MIT oscillator', () => {
  const c = unloaded(); const p = pose(c, c.geometry.pose), st = localStability(c, 'ideal');
  const M = p.massMatrix[0][0], K = c.spring.stiffness + c.actuators.fold.kp, D = c.spring.damping + c.actuators.fold.kd;
  const re = -D / (2 * M), im = Math.sqrt(K / M - re ** 2);
  assert.ok(st.poles.some(p => Math.abs(p.real - re) < 1e-6 && Math.abs(p.imag - im) < 1e-6));
  for (const row of [st.frequencyResponse[0], st.frequencyResponse[40], st.frequencyResponse[120]]) {
    const w = 2 * Math.PI * row.frequencyHz, expected = 1 / Math.hypot(K - M * w ** 2, D * w);
    close(row.qMagnitude, expected); close(row.yMagnitude, Math.abs(p.verticalJacobian) * expected);
  }
});

test('finite MIT poles satisfy independently derived lagged-controller cubic', () => {
  const c = unloaded(), p = pose(c, c.geometry.pose), st = localStability(c, 'finite');
  const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const polynomial = (pole, j) => {
    const a = [c.actuators.fold, c.actuators.drive][j], M = p.massMatrix[j][j];
    const K = j === 0 ? c.spring.stiffness : 0, D = j === 0 ? c.spring.damping : 0;
    const coefficients = [M * a.lag, M + D * a.lag, D + K * a.lag + a.kd, K + a.kp];
    const z = [pole.real, pole.imag]; let out = [coefficients[0], 0];
    for (const value of coefficients.slice(1)) { out = cmul(out, z); out[0] += value; }
    return Math.hypot(...out);
  };
  for (const pole of st.poles) assert.ok(Math.min(polynomial(pole, 0), polynomial(pole, 1)) < 1e-5);
});

test('nonunit belt inertial coupling is included in full 2DOF local state matrix', () => {
  const c = unloaded(); Object.assign(c.geometry, { driveRatio1: 1.4, driveRatio2: 0.7 });
  const p = pose(c, c.geometry.pose), st = localStability(c, 'ideal'), M = p.massMatrix;
  assert.ok(Math.abs(M[0][1]) > 1e-6);
  close(st.A[2][1], M[0][1] * c.actuators.drive.kp / p.determinant);
  close(st.A[3][0], M[0][1] * (c.spring.stiffness + c.actuators.fold.kp) / p.determinant);
});

test('unforced undamped RK4 conserves physical energy and damping causes decay', () => {
  const c = unloaded(); c.simulation.mode = 'passive'; c.spring.damping = 0; c.simulation.dt = 0.002;
  const free = runSimulation(c); assert.equal(free.status.code, 'complete');
  assert.ok(Math.abs(free.summary.energyChange) < 1e-7);
  c.spring.damping = 0.2; const damped = runSimulation(c);
  assert.ok(damped.summary.energyChange < -0.02); close(damped.summary.energyChange, -damped.summary.dampingEnergy, 2e-5);
  assert.ok(damped.samples.slice(1).every((s, j) => s.energy <= damped.samples[j].energy + 1e-10));
});

test('timestep refinement agrees and solver cadence peak values ignore output downsampling', () => {
  const c = defaultConfig(); c.simulation.duration = 0.8; c.simulation.dt = 0.001;
  const coarse = runSimulation(c); const finer = clone(c); finer.simulation.dt = 0.0005; const fine = runSimulation(finer);
  close(coarse.samples.at(-1).q, fine.samples.at(-1).q, 8e-5);
  const sparse = clone(c); sparse.simulation.outputDt = 0.19; const sparseResult = runSimulation(sparse);
  close(sparseResult.summary.peakFoldTorque, coarse.summary.peakFoldTorque, 1e-13);
  close(sparseResult.summary.peakFoldSpeed, coarse.summary.peakFoldSpeed, 1e-13);
  close(sparseResult.summary.rmsFoldTorque, coarse.summary.rmsFoldTorque, 1e-13);
  assert.ok(sparseResult.samples.length < coarse.samples.length);
});

test('finite torque, slew and speed limits alter achieved response and are reported', () => {
  const c = defaultConfig(); c.motion.stepSize = 0.25; c.simulation.duration = 1;
  const ideal = runSimulation({ ...c, simulation: { ...c.simulation, mode: 'ideal' } });
  c.actuators.fold.torqueLimit = 0.15; c.actuators.fold.slewRate = 1;
  const finite = runSimulation(c);
  assert.ok(Math.abs(finite.summary.finalFoldError) > Math.abs(ideal.summary.finalFoldError) + 0.1);
  assert.ok(finite.summary.peakFoldTorque <= 0.150000001); assert.ok(finite.summary.torqueLimitTime[0] > 0);
  assert.equal(finite.stability.saturated, true); assert.equal(finite.stability.valid, false);
  close(torqueEnvelope(c.actuators.fold, c.actuators.fold.noLoadSpeed, 1), 0);
  close(torqueEnvelope(c.actuators.fold, c.actuators.fold.noLoadSpeed, -1), 0.15);
});

test('release preserves passive torque and stops at bounds without inventing contact', () => {
  const c = defaultConfig(); c.spring.type = 'none'; c.motion.type = 'release'; c.motion.initialAngle = 0.6;
  const r = runSimulation(c); assert.equal(r.status.code, 'working-limit');
  assert.ok(r.samples.every(s => s.q >= c.geometry.foldMin && s.q <= c.geometry.foldMax && s.tauActual[0] === 0));
  assert.ok(r.summary.duration < c.simulation.duration);
});

test('singular and invalid physical inputs fail clearly', () => {
  assert.throws(() => normalizeConfig({ geometry: { upperLength: 0 } }), /positive/);
  assert.throws(() => normalizeConfig({ load: { forceX: '12' } }), /finite/);
  assert.throws(() => normalizeConfig({ spring: { preloadTorque: 'abc' } }), /finite/);
  assert.throws(() => normalizeConfig({ actuators: { fold: { feedforward: 'yes' } } }), /boolean/);
  assert.throws(() => normalizeConfig({ motion: { initialAngle: 4 } }), /working limits/);
  assert.throws(() => workspace({}, 3000), /samples/);
  const c = defaultConfig(); Object.assign(c.geometry, { foldMin: 0, pose: 0 }); c.motion.initialAngle = c.motion.target = 0;
  const p = pose(c, 0); assert.equal(p.singular, true); assert.equal(p.static.springVerticalStiffness, null);
  assert.equal(runSimulation(c).status.code, 'vertical-singularity');
});

test('inverse dynamics hold demand equals static holding torque and discontinuous steps are rejected', () => {
  const c = defaultConfig(); const p = pose(c, 0.6), d = inverseDynamics(c, 0.6, 0, 0, 0, 0, 0);
  close(d.tau[0], p.static.foldTorque); close(d.tau[1], p.static.driveTorque);
  assert.throws(() => prescribedMotion(c), /unbounded/);
  c.motion.type = 'sine'; assert.ok(prescribedMotion(c).samples.length > 100);
});

test('CSV and snapshot metadata preserve SI columns, both actual/command axes and unwrapped phase', () => {
  const c = defaultConfig(); c.motion.type = 'hold'; c.motion.driveSpeed = c.motion.initialDriveVelocity = 20; c.simulation.duration = 0.7;
  const result = runSimulation(c); assert.ok(result.samples.at(-1).phi > 2 * Math.PI);
  const csv = exportCSV(result), lines = csv.split('\r\n'), fields = lines[0].split(',');
  assert.equal(lines.length, result.samples.length + 1); assert.ok(fields.includes('fold_actual_Nm') && fields.includes('drive_command_Nm'));
  assert.ok(lines.every(line => line.split(',').length === fields.length));
  assert.match(result.metadata.units, /rad/); assert.equal(result.metadata.integrationDt, 0.001);
  assert.doesNotThrow(() => JSON.parse(JSON.stringify(result)));
});

test('independent SymPy energy-Hessian fixtures agree for equal/unequal/link-spring geometries', async () => {
  const fixture = JSON.parse(await readFile(new URL('./fixtures/linkage/sympy-reference.json', import.meta.url), 'utf8'));
  for (const item of fixture.cases) {
    const p = pose(item.config, item.q, item.phi), e = item.expected;
    for (const key of ['C', 'wheelAngle', 'jacobian', 'massMatrix', 'gravity', 'gravityDerivative', 'gravitationalEnergy']) if (e[key] !== undefined) recursiveClose(p[key], e[key], 2e-10);
  }
});

test('independent SciPy ideal/finite state matrices, poles and complex responses agree', async () => {
  const fixture = JSON.parse(await readFile(new URL('./fixtures/linkage/sympy-reference.json', import.meta.url), 'utf8'));
  for (const item of fixture.cases) {
    const c = clone(item.config); c.geometry.pose = item.q;
    c.actuators.fold.torqueLimit = c.actuators.drive.torqueLimit = 1e6;
    for (const [mode, prefix] of [['ideal', 'ideal'], ['finite', 'finiteUnsaturated']]) {
      const st = localStability(c, mode), e = item.expected;
      recursiveClose(st.A, e[`${prefix}StateMatrix`], 2e-7);
      for (const pole of e[`${prefix}Poles`]) assert.ok(st.poles.some(p => Math.hypot(p.real - pole[0], p.imag - pole[1]) < 2e-6));
      for (const row of e[`${prefix}FrequencyResponse`]) {
        const actual = st.frequencyResponse.reduce((best, p) => Math.abs(p.frequencyHz - row.frequencyHz) < Math.abs(best.frequencyHz - row.frequencyHz) ? p : best);
        for (const key of ['qMagnitude', 'qPhaseDeg', 'yMagnitude', 'wheelMagnitude']) close(actual[key], row[key], 2e-7);
      }
    }
  }
});
