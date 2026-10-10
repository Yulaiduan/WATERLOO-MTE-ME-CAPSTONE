import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { buildTerrain, parseTerrainCsv, serializeTerrainCsv } from '../src/workbench/terrain.js';
import { linkageAtAngle, simulateScenario, serializeResultsCsv } from '../src/workbench/engine.js';
const flat = lengthM => buildTerrain({ lengthM, gradePercent: 0, roughnessRmsM: 0, obstacleHeightM: 0 });
const close = (a, b, tolerance = 1e-8) => assert.ok(Math.abs(a - b) <= tolerance, `${a} differs from ${b}`);
test('periodic layers use declared RMS and wavelength; slope stays independent', () => {
  const terrain = buildTerrain({ lengthM: 10, obstacleHeightM: 0 });
  close(terrain.summary.realizedRoughnessRmsM, .04, .00003);
  close(terrain.samples[25].roughness, Math.SQRT2 * .04);
  close(terrain.samples[125].roughness, terrain.samples[25].roughness);
  close(terrain.samples.at(-1).baseline, .8);
  const restored = parseTerrainCsv(serializeTerrainCsv(terrain));
  assert.deepEqual(restored.samples, terrain.samples);
  assert.equal(buildTerrain().summary.obstacleCount, 20);
});
test('stochastic seeded master realization is unchanged by crop length', () => {
  const a = buildTerrain({ mode: 'stochastic', seed: 12, lengthM: 100 });
  const b = buildTerrain({ mode: 'stochastic', seed: 12, lengthM: 1000 });
  assert.deepEqual(a.samples, b.samples.slice(0, a.samples.length));
  assert.equal(a.summary.cycles, null);
  assert.notEqual(a.samples[20].roughness, buildTerrain({ mode: 'stochastic', seed: 13, lengthM: 1 }).samples[20].roughness);
});
test('Class 3 grade cycle accumulates elevation and has 25% plateau', () => {
  const terrain = buildTerrain({ mode: 'class3', lengthM: 1000, stepM: .1, roughnessRmsM: 0, obstacleHeightM: 0, obstacleWidthM: 1, wavelengthM: 3 });
  close(terrain.samples[1000].z, 12.25); close(terrain.samples.at(-1).z, 122.5);
  assert.equal(terrain.summary.cycles, 10); assert.equal(terrain.summary.gradeCycles, 10); assert.equal(terrain.summary.roughnessCycles, 0);
  close((terrain.samples[500].z - terrain.samples[490].z), .25);
});
test('selected terrain overrides are assumptions with retained source preset values', () => {
  const terrain = buildTerrain({ roughnessRmsM: .02 });
  assert.equal(terrain.metadata.evidence.roughnessRmsM.type, 'engineering assumption');
  assert.equal(terrain.metadata.evidence.roughnessRmsM.sourcePresetValue, .04);
  assert.equal(terrain.metadata.evidence.roughnessRmsM.selectedValue, .02);
  assert.equal(terrain.metadata.evidence.wavelengthM.type, 'illustrative design preset');
  assert.equal(flat(1).summary.cycles, 0);
});
test('measured USGS import preserves source-scale data; fine roughness is unknown', async () => {
  const text = await readFile(new URL('../data/terrain/usgs-shenandoah-transect-1000m.csv', import.meta.url), 'utf8');
  const terrain = parseTerrainCsv(text);
  assert.equal(terrain.samples.length, 1001); assert.equal(terrain.summary.realizedRoughnessRmsM, null);
  assert.equal(terrain.metadata.sourceResolutionM, 1); close(terrain.summary.netElevationM, 118.392028809, .001);
  const reimported = parseTerrainCsv(serializeTerrainCsv(terrain));
  assert.equal(reimported.summary.realizedRoughnessRmsM, null);
  assert.equal(reimported.metadata.layersProvided, false);
  assert.deepEqual(reimported.samples, terrain.samples);
  terrain.metadata.evidenceType = 'observed DEM';
  const crop = buildTerrain({ mode: 'measured', terrain, lengthM: 100.5 });
  close(crop.samples.at(-1).x, 100.5); assert.equal(crop.metadata.evidenceType, 'observed DEM');
  assert.equal(crop.summary.realizedRoughnessRmsM, null);
});
test('CSV handles original atlas layout and safely rejects bad rows', () => {
  const a = parseTerrainCsv('distance_m,relative_elevation_m,provenance\n0,0,"test, quoted"\n1,0.1,test');
  assert.equal(a.metadata.provenance, 'test, quoted');
  for (const bad of ['x,y\n0,0\n1,1', 'distance_m,height_m\n0,\n1,1', 'distance_m,height_m\n0,0\n0,1', 'distance_m,height_m\n0,0\n1,NaN', 'distance_m,height_m\n0,0\n1,=1+1']) assert.throws(() => parseTerrainCsv(bad));
});
test('analytic linkage derivative, vertical wheel path and generalized power', () => {
  const q = Math.PI / 4, h = 1e-6, g = linkageAtAngle(q);
  close((linkageAtAngle(q + h).extensionM - linkageAtAngle(q - h).extensionM) / (2 * h), g.jacobianMPerRad);
  close(g.wheel.x, 0); close(g.kneeAngleRad, -2 * q);
  const force = 20, qdot = 3; close(force * g.jacobianMPerRad * qdot, force * (g.jacobianMPerRad * qdot));
});
test('gravity-balanced static equilibrium for all control modes', () => {
  for (const controlMode of ['passive', 'active-damping', 'body-isolation']) {
    const result = simulateScenario(flat(2), { controlMode });
    for (const pass of [result.ideal, result.limited]) {
      assert.equal(pass.status, 'completed'); close(pass.summary.peakTorqueNm, 0); close(pass.summary.peakBodyAccelerationMps2, 0);
      close(pass.history.at(-1).normalForceN, 6 * 9.80665);
      close(pass.history.at(-1).springForceN, 5 * 9.80665);
      close(pass.history.at(-1).extensionM, linkageAtAngle(Math.PI / 4).extensionM);
    }
  }
});
test('hardware envelope changes forward dynamics; ideal power is consistent', () => {
  const terrain = buildTerrain({ lengthM: 10, gradePercent: 0, roughnessRmsM: .006, wavelengthM: 1, obstacleHeightM: 0 });
  const result = simulateScenario(terrain, { speedMps: 2 }, {}, { peakTorqueNm: .04, continuousTorqueNm: .02 });
  assert.equal(result.ideal.status, 'completed'); assert.equal(result.limited.status, 'completed');
  assert.ok(result.limited.summary.saturationTimeS > 0);
  assert.ok(result.limited.summary.rmsBodyAccelerationMps2 > result.ideal.summary.rmsBodyAccelerationMps2 * 1.1);
  assert.ok(result.limited.summary.peakTorqueNm <= .04 + 1e-10);
  for (const r of result.ideal.history) { close(r.mechanicalPowerW, r.torqueNm * r.jointSpeedRadPs); close(r.mechanicalPowerW, r.activeForceN * r.jointSpeedRadPs * linkageAtAngle(r.angleRad).jacobianMPerRad); }
  assert.ok(result.ideal.operatingPoints.some(p => p.timeS === result.ideal.summary.peakTorqueLocation.timeS));
  assert.ok(serializeResultsCsv(result).startsWith('pass,timeS,xM,'));
});
test('integration refinement has stable torque and acceleration on smooth terrain', () => {
  const terrain = buildTerrain({ lengthM: 3, gradePercent: 0, roughnessRmsM: .004, wavelengthM: 1, obstacleHeightM: 0 });
  const a = simulateScenario(terrain, { timeStepS: .001 }).ideal.summary;
  const b = simulateScenario(terrain, { timeStepS: .0005 }).ideal.summary;
  close(a.rmsTorqueNm, b.rmsTorqueNm, .003); close(a.rmsBodyAccelerationMps2, b.rmsBodyAccelerationMps2, .003);
});
test('travel failure has explicit location and cannot claim complete-route sizing', () => {
  const terrain = buildTerrain({ lengthM: 10, gradePercent: 0, roughnessRmsM: .08, wavelengthM: 1, obstacleHeightM: 0 });
  const result = simulateScenario(terrain, { speedMps: 2 }, { minAngleDeg: 44, maxAngleDeg: 46 });
  assert.equal(result.ideal.status, 'failed'); assert.ok(result.ideal.firstFailure.xM < 10);
  assert.ok(result.ideal.summary.completedDistanceM < 10);
});
test('passive smooth response matches independent harmonic two-mass solution', () => {
  const omega = 2 * Math.PI, A = Math.SQRT2 * .001;
  const add = (a,b) => [a[0]+b[0],a[1]+b[1]], sub = (a,b) => [a[0]-b[0],a[1]-b[1]];
  const mul = (a,b) => [a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]], abs = a => Math.hypot(...a);
  const ks = [1000, omega * 20], kt = [12000, omega * 35];
  const determinant = sub(mul(add(ks, [-5 * omega ** 2, 0]), add(add(ks,kt),[-(omega**2),0])), mul(ks,ks));
  const amplitude = abs(mul(ks,kt)) * A / abs(determinant);
  const result = simulateScenario(buildTerrain({ lengthM: 20, gradePercent: 0, roughnessRmsM: .001, wavelengthM: 1, obstacleHeightM: 0 }), { controlMode: 'passive' });
  const steady = result.ideal.fullHistory.filter(r => r.timeS > 17).map(r => r.bodyM);
  const measured = (Math.max(...steady) - Math.min(...steady)) / 2;
  close(measured, amplitude, amplitude * .015);
});
test('invalid and nonfinite configurations are rejected', () => {
  assert.throws(() => buildTerrain({ roughnessRmsM: NaN })); assert.throws(() => buildTerrain({ stepM: 1 }));
  assert.throws(() => buildTerrain({ obstacleSpacingM: .02, obstacleWidthM: 100 }));
  assert.throws(() => simulateScenario(flat(1), { sprungMassKg: 0 }));
  assert.throws(() => simulateScenario(flat(1), {}, { minAngleDeg: 70, maxAngleDeg: 50 }));
  assert.throws(() => simulateScenario(flat(1), {}, {}, { noLoadSpeedRadPs: 0 }));
});
test('unilateral tire contact cannot pull or generate damping force across a gap', () => {
  const terrain = buildTerrain({ lengthM: 2, gradePercent: 0, roughnessRmsM: .05, wavelengthM: .5, obstacleHeightM: 0 });
  const result = simulateScenario(terrain, { speedMps: 2, controlMode: 'passive' });
  let gaps = 0;
  for (const row of result.ideal.fullHistory) {
    assert.ok(row.normalForceN >= 0);
    if (row.groundM + .08 < row.wheelM) { gaps++; close(row.normalForceN, 0); }
  }
  assert.ok(gaps > 0); assert.ok(result.ideal.summary.contactLossTimeS > 0);
});
