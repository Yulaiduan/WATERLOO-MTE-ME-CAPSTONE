/** Verify frame-driven spring SVG against actual Python-engine fixtures.
 * Invocation: called by verify_spring_playback.py with JSON on stdin.
 * Inputs: captured constant-force/contact and prescribed results (mm/deg/N).
 * Outputs: bounded assertions and two ignored .preview SVG frame illustrations.
 * Pure geometry/data checks; no browser screenshot or hardware claim.
 */
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const ctx=vm.createContext({});
for(const file of ['reference-v4.js','model.js','preview-geometry.js','contact-render.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,file),'utf8'),ctx);
const fixtures=JSON.parse(fs.readFileSync(0,'utf8')),D=ctx.KinefoldDrawing,C=ctx.KinefoldContactDrawing;
let assertions=0;
const near=(a,b,t=1e-8)=>{assert.ok(Number.isFinite(a)&&Math.abs(a-b)<t,`${a} vs ${b}`);assertions++;};
const point=(a,b)=>a.forEach((value,i)=>near(value,b[i]));
const dist=(a,b)=>Math.hypot(...a.map((n,i)=>n-b[i]));
for(const result of fixtures){
 const p=result.params;
 for(const i of [0,Math.floor(result.frames.length/2),result.frames.length-1]){
  const f=result.frames[i],z=D.spring(p,f);
  assert.equal(z.law,'Ideal constant cable force');assertions++;
  near(z.forceN,p.p0);point(z.D,f.D);point(z.Q,f.Q);
  near(dist(z.S,z.Q),p.rs);near(dist(z.S,z.out),p.rs);
  point(z.arc[0],z.Q);point(z.arc.at(-1),z.out);
  const radial=z.Q.map((n,k)=>n-z.S[k]),tangent=z.D.map((n,k)=>n-z.Q[k]);
  near(radial.reduce((sum,n,k)=>sum+n*tangent[k],0),0,1e-7);
  const shift=[37,0,93],moved=D.spring(p,{...f,A:f.A.map((n,k)=>n+shift[k]),actualA:f.A.map((n,k)=>n+shift[k])});
  for(const key of ['D','Q','S','out','remote'])point(moved[key],z[key].map((n,k)=>n+shift[k]));
  near(moved.deltaMm,z.deltaMm);
  const html=D.springSvg(z,v=>[-v[0],-v[2]],.4);
  assert.ok(html.includes('data-spring-force-n=')&&html.includes('Cable payout')&&html.includes('Spring · schematic'));assertions++;
 }
 const first=D.spring(p,result.frames[0]),last=D.spring(p,result.frames.at(-1));
 assert.ok(Math.abs(first.deltaMm-last.deltaMm)>5);assertions++;
 assert.ok(Math.abs(first.witnessAngle-last.witnessAngle)>.2);assertions++;
 const fixedA=D.spring(p,{...result.frames.at(-1),A:result.frames[0].A,actualA:result.frames[0].A});
 point(fixedA.S,first.S);assert.ok(dist(fixedA.D,first.D)>5);assertions++;
 const disabled=D.spring({...p,springEnabled:false},result.frames[0]);
 assert.equal(disabled.enabled,false);assert.ok(D.springSvg(disabled,v=>v,.4).includes('Spring disabled'));assertions+=2;
}
const contact=fixtures.find(r=>r.scope?.mode==='terrain-contact');
if(contact){
 const out=path.join(__dirname,'.preview');fs.mkdirSync(out,{recursive:true});
 for(const index of [0,contact.frames.length-1]){
  const state={snapshot:{params:contact.params},result:contact,index},render=C.render(state);
  assert.ok(render.html.includes('Ideal constant cable force')&&render.html.includes('data-spring-payout-mm'));assertions++;
  const style=':root{--paper:#f6f5ee;--line:#e3e7df;--sage-soft:#e2ebdf;--sage:#557b64;--ink:#263c34;--blue:#527e98;--amber:#bb8b3c;--muted:#68736b;--red:#ad6054;--soft:#e9eee2}';
  fs.writeFileSync(path.join(out,`spring-contact-frame-${index}.svg`),`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 450"><style>${style}</style>${render.html}</svg>`);
 }
}
console.log(JSON.stringify({status:'PASS',assertions,scope:'Actual engine q/chassis transforms, exact tangent/wrap and schematic payout witness; SVG illustration snapshots only.'}));
