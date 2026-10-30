/** Check saved terrain replay clocks, snapshot identity and bounded frame selection.
 * Run node verify-terrain-animation.cjs from Kinefold. Inputs are small explicit
 * synthetic world-mm/time fixtures; outputs assertion count and no retained data.
 * This validates exporter contracts, not contact physics, GIF rendering or UI.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const E=require('./export_terrain_animation.cjs');
let checks=0;const ok=(value,message)=>{assert.ok(value,message);checks++;};
ok(E.settings({engine:'analytical',x:{b:2,a:1}})===E.settings({x:{a:1,b:2},engine:'pymunk'}),'Only engine differs; object order is irrelevant');
ok(E.settings({engine:'analytical',x:1})!==E.settings({engine:'pymunk',x:2}),'Physical setting differences stay distinct');
const clock=[{t:0},{t:.049},{t:.101}];
for(const [time,index] of [[0,0],[.025,0],[.049,1],[.05,1],[.101,2],[1,2]]){assert.equal(E.selectIndex(clock,time),index);checks++;}
assert.throws(()=>E.args(['--fps','99','--analytical','a','--pymunk','p','--frames-dir','x']),/fps/);checks++;
assert.throws(()=>E.args(['--fps']),/value/);checks++;
const preview=path.join(__dirname,'.preview');fs.mkdirSync(preview,{recursive:true});
const temporary=fs.mkdtempSync(path.join(preview,'verify-terrain-animation-')),file=path.join(temporary,'capture.json');
const p={engine:'analytical',params:{m1:1},runConfig:{duration:.1},caseConfig:{kind:'terrain-stability'},terrainConfig:{seed:481}},
  result={engine:'analytical',params:p.params,snapshot:{params:p.params,solverConfig:p.runConfig,caseConfig:p.caseConfig,terrainConfig:p.terrainConfig},rows:[{t:0},{t:.1}],frames:[0,.1].map(t=>({t,A:[0,0,1],B:[1,0,0],C:[0,0,0],terrainOffsetMm:[-t,0,0]})),terrain:{contourMm:[[1,0,0],[-1,0,0]]}};
const save=value=>fs.writeFileSync(file,JSON.stringify(value));
try{
  save({payload:p,result});ok(E.readCapture(file,'analytical').result.rows.length===2,'Valid finite actual-frame shape');
  assert.throws(()=>E.readCapture(file,'pymunk'),/engine/);checks++;
  const mismatch=structuredClone(result);mismatch.snapshot.terrainConfig.seed=482;save({payload:p,result:mismatch});assert.throws(()=>E.readCapture(file,'analytical'),/snapshot differs/);checks++;
  const badclock=structuredClone(result);badclock.frames[1].t=.09;save({payload:p,result:badclock});assert.throws(()=>E.readCapture(file,'analytical'),/clock/);checks++;
  const duplicate=structuredClone(result);duplicate.rows[1].t=0;duplicate.frames[1].t=0;save({payload:p,result:duplicate});assert.throws(()=>E.readCapture(file,'analytical'),/increasing/);checks++;
}finally{fs.unlinkSync(file);fs.rmdirSync(temporary);}
console.log(`PASS ${checks} terrain animation clock/snapshot/selection assertions; no physics or media generation.`);
