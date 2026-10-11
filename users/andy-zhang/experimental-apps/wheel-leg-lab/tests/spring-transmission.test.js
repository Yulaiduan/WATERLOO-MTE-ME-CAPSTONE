/** Recorded-length adapter checks. Run npm test; SI inputs, no solver integration. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {transmissionState} from '../web/spring-transmission.js';
test('uses actual recorded coil geometry and signed payout rather than inferred angle',()=>{
 const c={spring_transmission:'pullrod',rest_length:.23,spring_mode:'compression'};
 const s=transmissionState(c,{spring_geometry:{input_length:.24},spring_coil_length:.16},{spring_coil_length:.15},{spring_geometry:{input_length:.2}});
 assert.equal(s.coil,.16);assert.ok(Math.abs(s.travel-.04)<1e-12);assert.ok(Math.abs(s.strain+.07)<1e-12);
});
test('preserves disengaged finite coil and compensation identity',()=>{
 const s=transmissionState({spring_transmission:'ideal_rope',rest_length:.25,spring_force_law:'zero_effective'},
  {spring_geometry:{input_length:.1},spring_coil_length:.25,spring_slack:true});
 assert.equal(s.slack,true);assert.equal(s.strain,0);assert.equal(s.compensated,true);assert.equal(s.transmission,'ideal_rope');
});
