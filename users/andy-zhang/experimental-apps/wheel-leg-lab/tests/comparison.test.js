/** Numeric and state regression tests for saved-run comparison. Run: node --test tests/comparison.test.js.
 * Inputs: small synthetic SI/mm/degree recordings and saved workspace packets. Outputs: TAP tests.
 * Limits: verifies interpolation, provenance/layout guards, not solver or hardware accuracy.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {COMPARISON_SCHEMA,MAX_PANELS,MAX_TRACES,modelFamily,channelUnit,recordSources,seriesFor,interpolate,compareSeries,leaves,splitPanel,removePanel,normalizeWorkspace} from '../web/comparison-data.js';
const config={length:.273,radius:.2,target:'position',duration:1,dt:.001};
function record(rows,backend='math',name=backend){return {schema:'wheel-leg-lab-record/v1',kind:'run',name,backend,config,result:{rows}};}
function series(rows,backend='math',key='chassis_displacement_mm'){return seriesFor(recordSources(record(rows,backend),'a')[0],key);}
const rows=times=>times.map(t=>({t,chassis_displacement_mm:10*t,theta_deg:45+2*t}));

test('wheel and lever documented units distinguish displacement, derivatives, loads and end force',()=>{
 const wheel=record(rows([0,1]));
 for(const [key,unit]of Object.entries({chassis_displacement_mm:'mm',height:'m',theta_deg:'deg',phase_error:'rad',j2_force:'N',guide_link_torque:'N·m',hub_vy:'m/s',chassis_ay:'m/s²',knee_speed:'rad/s',knee_accel:'rad/s²',input:'m'}))assert.deepEqual(channelUnit(wheel,key),{unit,known:true});
 const lever={...wheel,backend:'counterbalance_math',config:{length:.4,spring_radius:.2,anchor_height:.2,mode:'free',law:'zero_effective'}};
 for(const [key,unit]of Object.entries({end_force_N:'N',end_force_kgf:'kgf',end_force_moment_Nm:'N·m',external_power_W:'W',external_work_J:'J',tip_height_m:'m',tip_velocity_y:'m/s',tip_acceleration_y:'m/s²'}))assert.deepEqual(channelUnit(lever,key),{unit,known:true});
 assert.equal(modelFamily(lever),'constant-lift lever');assert.equal(modelFamily(wheel),'wheel leg');
 assert.deepEqual(channelUnit(wheel,'mystery'),{unit:'source units',known:false});
 assert.deepEqual(channelUnit({...wheel,result:{units:{mystery:'Pa'}}},'mystery'),{unit:'Pa',known:true});
});
test('different sample intervals agree exactly for a linear signal without extrapolation',()=>{
 const candidate=series(rows([.1,.3,.5,.7,.9]),'pymunk'),reference=series(rows([0,.2,.4,.6,.8,1]));
 const delta=compareSeries(candidate,reference);
 assert.ok(delta.y.every(value=>Math.abs(value)<1e-12));assert.equal(delta.stats.start,.1);assert.equal(delta.stats.end,.9);assert.equal(delta.stats.count,9);assert.ok(delta.stats.maxAbs<1e-12);
 assert.equal(interpolate(candidate,0),null);assert.equal(interpolate(reference,1.1),null);
});
test('signed candidate-minus-reference statistics retain units, sign and final time',()=>{
 const candidate=series(rows([0,.5,1]).map(row=>({...row,chassis_displacement_mm:row.chassis_displacement_mm-3})),'pymunk');
 const delta=compareSeries(candidate,series(rows([0,.25,.75,1])));
 assert.deepEqual(delta.y,[-3,-3,-3,-3,-3]);assert.equal(delta.unit,'mm');assert.equal(delta.stats.rms,3);assert.equal(delta.stats.maxAbs,3);assert.equal(delta.stats.final,-3);assert.equal(delta.stats.finalTime,1);assert.equal(delta.stats.count,5);
});
test('shifted recording starts use only actual overlap; same signal at different absolute time differs',()=>{
 const candidate=series([{t:2,chassis_displacement_mm:0},{t:3,chassis_displacement_mm:10}]),reference=series([{t:1,chassis_displacement_mm:0},{t:2,chassis_displacement_mm:10},{t:3,chassis_displacement_mm:20}]);
 assert.deepEqual(compareSeries(candidate,reference).y,[-10,-10]);
 assert.throws(()=>compareSeries(candidate,series(rows([0,1]))),/no time overlap/);
});
test('missing data remains a gap and is never bridged in interpolation or delta',()=>{
 const candidate=series([{t:0,chassis_displacement_mm:0},{t:1,chassis_displacement_mm:null},{t:2,chassis_displacement_mm:20}]);
 assert.equal(interpolate(candidate,.5),null);assert.equal(interpolate(candidate,1),null);assert.equal(interpolate(candidate,1.5),null);
 const delta=compareSeries(candidate,series(rows([0,.5,1,1.5,2])));assert.deepEqual(delta.y,[0,null,null,null,0]);assert.equal(delta.stats.count,2);
 const absent=series([{t:0,chassis_displacement_mm:null},{t:1,chassis_displacement_mm:0}]);
 assert.throws(()=>compareSeries(absent,series([{t:0,chassis_displacement_mm:0},{t:1,chassis_displacement_mm:null}])) ,/No valid matching/);
});
test('nonmonotonic, duplicate, missing, numeric-string and nonfinite times are rejected, never sorted',()=>{
 for(const times of [[1,0],[0,0],[0,NaN],[0,Infinity],[0,'1'],[0,undefined]])assert.throws(()=>series(rows(times)),/times must/);
});
test('delta rejects unknown units, different units, channel names and model families',()=>{
 const baseline=series(rows([0,1]));
 assert.throws(()=>compareSeries({...baseline,known:false},baseline),/documented units/);
 assert.throws(()=>compareSeries({...baseline,unit:'m'},baseline),/documented units/);
 assert.throws(()=>compareSeries({...baseline,key:'theta_deg'},baseline),/same channel/);
 assert.throws(()=>compareSeries({...baseline,model:'constant-lift lever'},baseline),/same mechanism/);
 const indexed=seriesFor(recordSources({name:'Dataset',result:{rows:[{height:1},{height:2}]}},'d')[0],'height');
 assert.deepEqual(indexed.x,[0,1]);assert.equal(indexed.timeBased,false);assert.throws(()=>compareSeries(indexed,baseline),/t\/time/);
});
test('identical traces have exactly zero error including one-sample overlap',()=>{
 const baseline=series(rows([0,1]));const delta=compareSeries(baseline,baseline);assert.equal(delta.stats.maxAbs,0);assert.equal(delta.stats.rms,0);assert.equal(delta.stats.final,0);
 const single=compareSeries(series(rows([1,2])),baseline);assert.deepEqual(single.x,[1]);assert.equal(single.stats.count,1);
});
test('numeric nested vector channels are discoverable and original rows are not changed',()=>{
 const rec=record([{t:0,pose:{point:[2,3]}},{t:1,pose:{point:[4,null]}}]);const snapshot=JSON.stringify(rec);const source=recordSources(rec,'run')[0];
 assert.deepEqual(seriesFor(source,'pose.point.1').y,[3,null]);assert.equal(JSON.stringify(rec),snapshot);assert.throws(()=>seriesFor(source,'missing'),/not recorded/);
});
test('split layout is immutable, nested, safely collapses and enforces eight plots',()=>{
 const base={kind:'panel',id:'a'};let tree=splitPanel(base,'a','horizontal','b');tree=splitPanel(tree,'b','vertical','c');
 assert.deepEqual(leaves(tree).map(p=>p.id),['a','b','c']);assert.deepEqual(base,{kind:'panel',id:'a'});assert.deepEqual(removePanel(tree,'b'),{kind:'split',direction:'horizontal',first:base,second:{kind:'panel',id:'c'}});
 for(let i=3;i<MAX_PANELS;i++)tree=splitPanel(tree,'a','horizontal',String(i));
 assert.equal(leaves(tree).length,8);assert.throws(()=>splitPanel(tree,'a','vertical','more'),/At most 8/);
 assert.throws(()=>splitPanel(base,'a','diagonal','b'),/direction/);assert.throws(()=>splitPanel(base,'missing','horizontal','b'),/Select/);
 assert.equal(removePanel(base,'a'),null);
});
function workspace(){return {schema:COMPARISON_SCHEMA,records:[{id:'source',record:{...record(rows([0,1])),id:'saved-id',created_at:'2026-10-10T00:00:00Z'}}],layout:{kind:'panel',id:'plot'},active:'plot',panels:{plot:{mode:'overlay',legend:false,reference:'source:0',traces:[{sourceId:'source:0',key:'theta_deg',visible:false}]}}};}
test('workspace export/import retains data, provenance, channel visibility, legend and reference',()=>{
 const original=workspace(),restored=normalizeWorkspace(JSON.parse(JSON.stringify(original)));
 assert.deepEqual(restored.panels,original.panels);assert.deepEqual(restored.records[0].record.result,original.records[0].record.result);assert.equal(restored.records[0].record.id,'saved-id');assert.equal(restored.records[0].record.created_at,original.records[0].record.created_at);assert.equal(restored.active,'plot');
});
test('workspace validation rejects unknown sources/channels, excessive traces, unsafe input and bad layout',()=>{
 for(const mutate of [w=>w.schema='bad',w=>w.layout.direction='diagonal',w=>w.panels.plot.traces[0].sourceId='lost',w=>w.panels.plot.traces[0].key='lost',w=>w.panels.plot.legend='yes',w=>w.panels.plot.reference='lost',w=>w.panels.plot.traces[0].visible='yes',w=>w.panels.plot.traces=Array(MAX_TRACES+1).fill(w.panels.plot.traces[0])]){const w=workspace();mutate(w);if(w.layout.direction==='diagonal')w.layout.kind='split';assert.throws(()=>normalizeWorkspace(w));}
 const unsafe=workspace();unsafe.records[0].record.result.danger=JSON.parse('{"__proto__":{}}');assert.throws(()=>normalizeWorkspace(unsafe),/Unsafe JSON key/);
 const duplicate=workspace();duplicate.records.push(duplicate.records[0]);assert.throws(()=>normalizeWorkspace(duplicate),/unique/);
});
