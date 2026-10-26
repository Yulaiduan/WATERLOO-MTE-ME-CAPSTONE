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
  for(const key of ['D','Q','S','out','remote','fixedSeat','movingSeat'])point(moved[key],z[key].map((n,k)=>n+shift[k]));
  near(moved.deltaMm,z.deltaMm);
  near(dist(z.fixedSeat,z.movingSeat),z.lengthMm);
  near(dist(z.out,z.fixedSeat),125);point(z.remote,z.movingSeat);
  assert.ok(z.lengthMm>=80-1e-8);assertions++;
  for(const key of ['lengthMm','compressionMm','strokeMm'])near(z[key],result.nativeSpringDrawing[i][key]);
  for(const key of ['fixedSeat','movingSeat'])point(z[key],result.nativeSpringDrawing[i][key]);
  z.wire.forEach((v,k)=>point(v,result.nativeSpringDrawing[i].wire[k]));
  const coil=D.spring({...p,springLaw:'v4'},f),reference=ctx.KinefoldV4.VSLSpring.state(ctx.Kinefold.reference({...p,springLaw:'v4'}),f.theta2);
  near(coil.forceN,reference.force);near(coil.torqueNm,reference.tauS);point(coil.movingSeat,z.movingSeat);
  const b=C.bounds(result,p);
  for(const v of z.assemblyPoints){assert.ok(v.every(Number.isFinite)&&v[0]>=b.minX&&v[0]<=b.maxX&&v[2]>=b.minZ&&v[2]<=b.maxZ);assertions++;}
  const html=D.springSvg(z,v=>[-v[0],-v[2]],.4);
  assert.ok(html.includes('data-spring-force-n=')&&html.includes('Compression spring')&&html.includes('illustrative size')&&html.includes('data-spring-fixed-seat')&&html.includes('data-spring-moving-seat'));assertions++;
  assert.ok(!html.includes('dial')&&!html.includes('witness')&&!html.includes('NaN'));assertions++;
 }
 const first=D.spring(p,result.frames[0]),last=D.spring(p,result.frames.at(-1));
 assert.ok(Math.abs(first.deltaMm-last.deltaMm)>5);assertions++;
 near(last.lengthMm-first.lengthMm,-(last.payoutMm-first.payoutMm));
 near(first.payoutMm+dist(first.out,first.movingSeat),last.payoutMm+dist(last.out,last.movingSeat));
 const fixedA=D.spring(p,{...result.frames.at(-1),A:result.frames[0].A,actualA:result.frames[0].A});
 point(fixedA.S,first.S);point(fixedA.fixedSeat,first.fixedSeat);assert.ok(dist(fixedA.D,first.D)>5);assertions++;
 near(dist(fixedA.movingSeat,first.movingSeat),Math.abs(last.payoutMm-first.payoutMm));
 const reference=ctx.Kinefold.reference(p),envelope=ctx.KinefoldV4.VSLSpring.interval(reference,p.te,p.tc);
 for(const angle of [p.te,p.tc,envelope.minTheta,envelope.maxTheta]){
  const sample=D.spring(p,{...result.frames[0],theta2:angle});
  assert.ok(sample.valid&&sample.lengthMm>=80-1e-8);assertions++;
 }
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
console.log(JSON.stringify({status:'PASS',assertions,scope:'Actual engine frames, exact tangent/wrap, browser/native seat and wire parity, 1:1 compression and continuous cable; SVG illustration snapshots only.'}));
