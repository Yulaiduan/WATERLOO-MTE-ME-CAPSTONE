/** Validate portable GUI profile/data contracts without a browser.
 * Run: npm test. Inputs: SI JSON records; no files or simulation are produced.
 * Storage rendering is tested separately in verify_motion_lab.cjs.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeImport,extractTables,numericRow} from '../web/library.js';
import {defaultConfig} from '../src/linkage/model.js';
const config={length:.273,radius:.2,target:'position',dt:.001,duration:1.2};
test('GUI profile JSON roundtrips math and Pymunk config/reference inputs',()=>{
 for(const backend of ['math','pymunk']){
  const record=normalizeImport({schema:'wheel-leg-lab-profile/v1',backend,config,reference_inputs:{T0_N:98.0665,applied_to_solver:false}});
  assert.equal(record.kind,'profile');assert.equal(record.backend,backend);assert.deepEqual(record.config,config);assert.equal(record.reference_inputs.T0_N,98.0665);
  assert.deepEqual(normalizeImport(record),record);
 }
});
test('full suspension run retains source data through record JSON',()=>{
 const data={backend:'math',config,rows:[{t:0,chassis_displacement_mm:0},{t:1,chassis_displacement_mm:30}],scope:'Independent model'};
 const record=normalizeImport(data);assert.equal(record.kind,'run');assert.deepEqual(record.result,data);assert.deepEqual(normalizeImport(record),record);
});
test('detailed linkage exports keep comparison modes in distinct tables',()=>{
 const run={schema:'motion-lab-linkage-run',version:1,backend:'linkage',config:defaultConfig(),samples:[{t:0,q:1,mode:'passive'},{t:1,q:2,mode:'passive'},{t:0,q:3,mode:'finite'}]};
 const record=normalizeImport(run);assert.equal(record.backend,'linkage');assert.deepEqual(extractTables(record.result).map(t=>[t.name,t.rows.length]),[['passive',2],['finite',1]]);
});
test('MATLAB column JSON becomes a plot-ready run while preserving columns',()=>{
 const matlab={backend:'matlab-ode45',config,t:[0,1],theta_deg:[45,46],j2_force:[100,120],stop_event_time:[]};
 const record=normalizeImport(matlab,'MATLAB run.json');assert.equal(record.backend,'math');assert.equal(record.result.source_backend,'matlab-ode45');assert.deepEqual(record.result.rows[1],{t:1,theta_deg:46,j2_force:120});assert.deepEqual(record.result.theta_deg,matlab.theta_deg);
});
test('row-only imports remain read-only datasets',()=>{
 const record=normalizeImport([{t:0,f:100},{t:1,f:110}]);assert.equal(record.kind,'dataset');assert.equal(record.backend,null);assert.equal(record.config,null);
});
test('miscellaneous study JSON retains restorable controls without inventing a solver',()=>{
 const packet={schema:'motion-lab-study/v1',name:'Wheel ratios',study_settings:{id:'ratio',controls:[{id:'wl-radius',value:'250'},{id:'projection',value:true}]},plots:[]};
 const record=normalizeImport(packet);assert.equal(record.kind,'dataset');assert.equal(record.config,null);assert.equal(record.result.study_settings.id,'ratio');assert.equal(record.result.rows[0]['wl-radius'],250);
});
test('numeric channels flatten vectors without discarding original values',()=>{
 assert.deepEqual(numericRow({t:1,pose:{position:[2,3]},mode:'passive'}),{t:1,'pose.position.0':2,'pose.position.1':3});
});
test('unknown schemas, invalid configuration and unsafe payloads are rejected',()=>{
 for(const value of [{schema:'unknown',config},{backend:'other',config},{config:{...config,length:-1}},{rows:[]},JSON.parse('{"__proto__":{"pollute":true}}'),{backend:'matlab-ode45',config,t:[0,'bad']},{schema:'motion-lab-linkage-run',version:2,backend:'linkage',config:defaultConfig(),samples:[{t:0}]}])assert.throws(()=>normalizeImport(value));
 assert.throws(()=>normalizeImport({backend:'math',config,rows:[{t:NaN}]}));
});
