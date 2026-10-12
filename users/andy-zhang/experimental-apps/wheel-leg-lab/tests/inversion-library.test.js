/** Portable inversion records keep model/units separate. Run npm test, no solver. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeImport} from '../web/library.js';
import {modelFamily,channelUnit} from '../web/comparison-data.js';
test('inversion profiles/recordings roundtrip with explicit units and distinct family',()=>{
 const config={preset:'dual_rope',fixture:'hip_fixed',length:.273,radius:.2,dt:.00025,duration:1,femur_torque:100};
 for(const backend of ['inversion_math','inversion_pymunk']){
  const profile=normalizeImport({backend,config});assert.equal(profile.backend,backend);assert.deepEqual(normalizeImport(JSON.parse(JSON.stringify(profile))),profile);
  const run=normalizeImport({backend,config,rows:[{t:0,theta_deg:-135,red_tension_N:3}],units:{theta_deg:'deg',red_tension_N:'N'}});
  assert.equal(modelFamily(run),'invertible wheel leg');assert.equal(channelUnit(run,'red_tension_N').unit,'N');assert.notEqual(modelFamily(run),modelFamily({backend:'pymunk'}));
 }
 assert.throws(()=>normalizeImport({backend:'inversion_pymunk',config:{...config,preset:'unknown'}}));
});
