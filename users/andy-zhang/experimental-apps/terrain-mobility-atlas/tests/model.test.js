import test from 'node:test';
import assert from 'node:assert/strict';
import { DEFAULT_VEHICLE, clone, evaluate, coverage, comparison, normalizeVehicle, isFeasible } from '../src/model.js';
import { CELLS, REGIONS, polygonArea, defaultCell } from '../src/data.js';

const gentle = { grade: 10, cross: 5, roughness: 40, obstacle: 60, spacing: 3, corridor: 3, surface: 'hard' };
test('a hard cross-slope failure overrides all favorable constraints', () => {
  const result = evaluate({ ...gentle, cross: 17 }, DEFAULT_VEHICLE);
  assert.equal(result.status, 'fail');
  assert.equal(result.margin, 0);
  assert.deepEqual(result.failures.map(c => c.key), ['cross']);
});
test('missing critical geometry remains unknown; established failure still wins', () => {
  assert.equal(evaluate({ ...gentle, obstacle: null }, DEFAULT_VEHICLE).status, 'unknown');
  assert.equal(evaluate({ ...gentle, obstacle: null, corridor: 0.8 }, DEFAULT_VEHICLE).status, 'fail');
});
test('surface failure cannot be averaged away', () => {
  assert.equal(evaluate({ ...gentle, surface: 'soft' }, DEFAULT_VEHICLE).status, 'fail');
  assert.equal(evaluate(gentle, { ...DEFAULT_VEHICLE, surfaces: [] }).status, 'fail');
});
test('clearance and spacing use the inverse inequality and include equality', () => {
  assert.equal(evaluate({ ...gentle, corridor: 1.2 }, DEFAULT_VEHICLE).status, 'near');
  assert.equal(evaluate({ ...gentle, corridor: 1.19 }, DEFAULT_VEHICLE).status, 'fail');
  assert.equal(evaluate({ ...gentle, spacing: 0.9 }, DEFAULT_VEHICLE).status, 'fail');
  assert.ok(isFeasible(evaluate(gentle, { ...DEFAULT_VEHICLE, corridor: 0.9 })));
});
test('minimum margin reflects the limiting constraint rather than an average', () => {
  const result = evaluate({ ...gentle, obstacle: 190 }, DEFAULT_VEHICLE);
  assert.equal(result.status, 'near');
  assert.equal(result.margin, 5);
  assert.equal(result.limiting.key, 'obstacle');
});
test('coverage uses area and keeps unknown area in its denominator', () => {
  const cells = [{ area: 1, terrain: gentle }, { area: 3, terrain: { ...gentle, obstacle: null } }];
  const result = coverage(cells, DEFAULT_VEHICLE);
  assert.equal(result.percent, 25);
  assert.equal(result.unknown, 3);
  assert.equal(coverage([], DEFAULT_VEHICLE).percent, 0);
});
test('upgrade comparisons measure gained and lost cell area', () => {
  const cells = [{ area: 5, terrain: { ...gentle, obstacle: 250 } }, { area: 3, terrain: gentle }];
  const improved = { ...DEFAULT_VEHICLE, obstacle: 300 };
  assert.equal(comparison(cells, DEFAULT_VEHICLE, improved).gained, 5);
  assert.equal(comparison(cells, improved, DEFAULT_VEHICLE).lost, 5);
});
test('increasing any single capability never loses coverage', () => {
  for (const key of ['grade', 'cross', 'roughness', 'obstacle']) {
    const vehicle = clone(DEFAULT_VEHICLE); vehicle[key] *= 1.5;
    assert.equal(comparison(CELLS, DEFAULT_VEHICLE, vehicle).lost, 0);
  }
  assert.equal(comparison(CELLS, DEFAULT_VEHICLE, { ...DEFAULT_VEHICLE, corridor: 0.6, spacing: 0.3, surfaces: ['hard', 'mixed', 'loose', 'soft'] }).lost, 0);
});
test('spherical cell area accounts for latitude', () => {
  const square = [[0,0],[1,0],[1,1],[0,1],[0,0]];
  const high = square.map(([x,y]) => [x,y + 60]);
  assert.ok(polygonArea(high) < polygonArea(square) * 0.51);
  assert.ok(polygonArea(high) > polygonArea(square) * 0.48);
});
test('all scenarios have valid deterministic cells and no measured provenance', () => {
  assert.ok(CELLS.length > 300);
  for (const region of REGIONS) assert.ok(defaultCell(region.id));
  for (const cell of CELLS) { assert.ok(cell.area > 0); assert.deepEqual(cell.geometry.coordinates[0][0], cell.geometry.coordinates[0].at(-1)); }
});
test('invalid saved profile fields are clamped or fall back safely', () => {
  const result = normalizeVehicle({ grade: 999, corridor: -2, surfaces: ['hard', 'unknown'], name: '<script>' });
  assert.equal(result.grade, 60); assert.equal(result.corridor, 0.5);
  assert.deepEqual(result.surfaces, ['hard']);
  assert.equal(normalizeVehicle(null).obstacle, DEFAULT_VEHICLE.obstacle);
});
