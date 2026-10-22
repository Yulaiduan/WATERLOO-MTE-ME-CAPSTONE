/** Verify selected browser poses against the retained study and original V2.
 * Run: node --test tests/design-examples.test.js from Motion Lab.
 * Inputs: configs in mm/degrees, original Jonathan solver, retained study JSON.
 * Outputs: numerical assertions, including inversion and fixed-phase identities.
 * Limits: geometry consistency only; no physics/hardware certification.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {data} from '../web/design-examples/data.js';
import {pose,phaseAngle,trace} from '../web/design-examples/model.js';
const source=new URL('../../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html',import.meta.url);
const text=fs.readFileSync(source,'utf8'),context=vm.createContext({Math});
vm.runInContext(text.match(/<script id="solver-model">([\s\S]*?)<\/script>/)[1],context);
vm.runInContext('globalThis.original=VSL;',context);
const close=(a,b,e=1e-8)=>assert.ok(Math.abs(a-b)<=e,`${a} versus ${b}`);
test('selected configs and metrics are exact retained evidence with matching source hash',()=>{
 const file=new URL('../../leg-design-study/docs/inversion-path-results.json',import.meta.url),bytes=fs.readFileSync(file),e=JSON.parse(bytes);
 assert.equal(data.source_sha256,crypto.createHash('sha256').update(bytes).digest('hex'));
 const all=[...e.selected,...e.examples,...e.practical];
 for(const d of data.designs){const c=all.find(v=>v.id===d.id);assert.deepEqual(d.config,c.config);assert.deepEqual(d.metrics,c.metrics);assert.deepEqual(d.full,c.full_inversion);assert.equal(d.config.alpha,0);}
});
test('working and full inversion positions agree with Jonathan V2 at every sampled pose',()=>{
 for(const d of data.designs)for(const mode of ['working','inversion'])for(let i=0;i<=300;i++){
  const q=phaseAngle(d,mode,i/300),p=pose(d.config,q),r=context.original.state(d.config,q);
  for(let a=0;a<2;a++){close(p.B[a],r.Bg[a]);close(p.C[a],r.Pg[a]);}
  close(Math.hypot(p.B[0]-p.C[0],p.B[1]-p.C[1]),d.config.L3);
 }
});
test('zero-phase full paths mirror, with a vertical fold tangent and projected overlap',()=>{
 for(const d of data.designs.filter(d=>d.config.phi0===0)){
  const a=pose(d.config,115),b=pose(d.config,245),fold=pose(d.config,180);
  close(a.C[0],b.C[0]);close(a.C[1],-b.C[1]);close(fold.J[0],0);assert.ok(fold.J[1]>0);assert.ok(fold.hipDistance<220);
 }
});
test('fixed indexing creates the exact equal-link line without changing phase during playback',()=>{
 const d=data.designs.find(d=>d.slug==='exact-line-indexed');
 for(const mode of ['working','inversion'])for(const [x,z] of trace(d,mode))close(x*Math.cos(12.5*Math.PI/180)-z*Math.sin(12.5*Math.PI/180),0);
 close(d.config.phi0,-25);
});
