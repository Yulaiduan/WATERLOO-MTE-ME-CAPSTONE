/* Verify the standalone analytical dashboard: node verify.cjs [--write].
 * Inputs: HTML model and pinned reference kernel/DP#3/gain fixtures, SI units.
 * Outputs: assertion summary; --write refreshes verification.json/default-setup.json.
 * No dependencies. Source parity is not hardware or chassis dynamic validation. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const ctx=vm.createContext({});
vm.runInContext(html.match(/<script id="camel-model">([\s\S]*?)<\/script>/)[1],ctx);
const M=ctx.CamelModel, d={...M.DEFAULTS},c=M.calculate(d);
let checks=0;
function near(a,b,tol=1e-9){assert.ok(Math.abs(a-b)<=tol,`${a} != ${b}`);checks++;}
const source=path.join(__dirname,'reference/solver-kernel.js');
const sourceKernel=fs.readFileSync(source,'utf8');
const sourceCtx=vm.createContext({});
vm.runInContext(sourceKernel+'\nglobalThis.reference=VSL;',sourceCtx);
const p=JSON.parse(fs.readFileSync(path.join(__dirname,'reference/dp3.json'),'utf8')).snapshot.parameters;
const saved=JSON.parse(fs.readFileSync(path.join(__dirname,'reference/candidate-gains.json'),'utf8'));
near(c.kh,saved.height_stiffness_N_m);near(c.ch,saved.height_damping_Ns_m);
let maxPathError=0,maxJacobianError=0;
for(let i=0;i<=650;i++){
  const deg=100+i/10,g=M.geometry(deg),r=sourceCtx.reference.state(p,deg);
  for(let k=0;k<2;k++){maxPathError=Math.max(maxPathError,Math.abs(g.hub[k]-r.Pg[k]/1000),Math.abs(g.knee[k]-r.Bg[k]/1000));near(g.hub[k],r.Pg[k]/1000,1e-14);near(g.knee[k],r.Bg[k]/1000,1e-14);}
  const eps=1e-5,degEps=eps*180/Math.PI;
  const fd=-(sourceCtx.reference.state(p,deg+degEps).Pg[1]-sourceCtx.reference.state(p,deg-degEps).Pg[1])/1000/(2*eps);
  maxJacobianError=Math.max(maxJacobianError,Math.abs(g.J-fd));near(g.J,fd,1e-9);
}
for(const row of saved.pose_examples){const c=M.calculate({...d,pose:row.q_deg});near(c.h,row.h_m);near(c.J,row.Jh_m_rad);near(c.kp,row.Kp_current_pose_ff_Nm_rad);near(c.kd,row.Kd_Nms_rad);}
// Independent modal calculation by virtual-work matrix B^T diag(k) B.
const supports=[[.6,.4],[.6,-.4],[-.6,.4],[-.6,-.4]];
const B=supports.map(([x,y])=>[1,y,-x]);
for(const [j,k] of ['heave','roll','pitch'].entries()){
  near(c[k].k,B.reduce((sum,b)=>sum+saved.height_stiffness_N_m*b[j]**2,0));
  near(c[k].c,B.reduce((sum,b)=>sum+saved.height_damping_Ns_m*b[j]**2,0));
  for(let l=0;l<3;l++)if(l!==j)near(B.reduce((sum,b)=>sum+b[j]*b[l],0),0);
}
const doubled=M.calculate({...d,frequency:4});near(doubled.kh,4*c.kh);near(doubled.ch,2*c.ch);
const wide=M.calculate({...d,width:1.6});near(wide.roll.k,4*c.roll.k);near(wide.heave.k,c.heave.k);near(wide.pitch.k,c.pitch.k);
const long=M.calculate({...d,length:2.4});near(long.pitch.c,4*c.pitch.c);near(long.roll.c,c.roll.c);
const direct={...d,mode:'direct',stiffness:c.kh,verticalDamping:c.ch};near(M.calculate(direct).fn,2);near(M.calculate(direct).zeta,.8);
for(const s of [d,direct,{...direct,pose:165,stiffness:2500,verticalDamping:0,view:'chassis',width:1,length:1.4}]){
  const encoded=JSON.stringify(M.serialize(s));const restored=M.deserialize(JSON.parse(encoded));assert.equal(JSON.stringify(M.serialize(restored)),encoded);assert.equal(JSON.stringify(M.calculate(restored)),JSON.stringify(M.calculate(s)));checks+=2;
}
for(const s of [{...d,chassisMass:0},{...d,chassisMass:-1},{...d,frequency:NaN},{...d,frequency:0},{...d,damping:-.1},{...d,pose:99.9},{...d,pose:165.1},{...d,width:0},{...d,length:Infinity},{...direct,stiffness:0},{...direct,verticalDamping:-1},{...d,chassisMass:1e308},{...d,frequency:1e-300},{...d,view:'unknown'},{...d,mode:'unknown'}]){assert.ok(Object.keys(M.validate(s)).length);assert.throws(()=>M.serialize(s));checks+=2;}
for(const s of [{...d,damping:0},{...direct,verticalDamping:0}]){assert.equal(Object.keys(M.validate(s)).length,0);near(M.calculate(s).kd,0);}
for(const mutate of [o=>o.schemaVersion=3,o=>o.modelVersion='bad',o=>o.geometry.id='dp1',o=>o.geometry.revision='new',o=>o.chassisMassKg='35',o=>o.linkage=null,o=>o.linkage.model='bad',o=>o.linkage.upperLinkMassKg=-1,o=>delete o.linkage.lowerLinkMassKg,o=>o.gainInput.frequencyHz=null,o=>o.support=null,o=>o.activeView='other']){const o=JSON.parse(JSON.stringify(M.serialize(d)));mutate(o);assert.throws(()=>M.deserialize(o));checks++;}
assert.throws(()=>M.deserialize(null));assert.throws(()=>M.deserialize([]));checks+=2;
// Chassis quartering, no linkage double-counting, and explicit schema-1 migration.
near(c.cornerMass,35/4);near(c.linkEquivalentMass,0);near(c.effectiveMass,8.75);near(c.modeledMass,35);
const heavy=M.calculate({...d,chassisMass:70});near(heavy.kh,2*c.kh);near(heavy.ch,2*c.ch);
const loaded={...d,upperMass:.6,lowerMass:.65}, lc=M.calculate(loaded);
near(lc.modeledMass,40);assert.ok(lc.effectiveMass>lc.cornerMass);checks++;
for(const s of [loaded,{...loaded,mode:'direct',stiffness:2000,verticalDamping:150,pose:100}]){
  const restored=M.deserialize(JSON.parse(JSON.stringify(M.serialize(s))));
  assert.equal(JSON.stringify(M.serialize(restored)),JSON.stringify(M.serialize(s)));checks++;
}
const old={schemaVersion:1,modelVersion:'camel-controls/1.0.0',geometry:{...M.GEOMETRY},poseDeg:135,massKg:8.75,gainInput:{mode:'response',frequencyHz:2,dampingRatio:.8},support:{frontRearM:1.2,leftRightM:.8},activeView:'leg'};
const migrated=M.deserialize(old);near(migrated.chassisMass,35);near(migrated.upperMass,0);near(migrated.lowerMass,0);near(M.calculate(migrated).kp,c.kp);
for(const bad of ['8.75',null,-1,Infinity]){assert.throws(()=>M.deserialize({...old,massKg:bad}));checks++;}
const oldDirect={...old,gainInput:{mode:'direct',stiffnessNPerM:2000,dampingNsPerM:150}};
near(M.calculate(M.deserialize(oldDirect)).kh,2000);
for(const s of [{...d,upperMass:-1},{...d,lowerMass:NaN},{...d,upperMass:'1'},{...d,upperMass:1e308},{...d,chassisMass:NaN}]){assert.ok(Object.keys(M.validate(s)).length);checks++;}
// Independently integrate velocity squared along rods, using finite differences of
// retained source endpoints. Two-point Gauss integration is exact for a uniform rod.
let maxLinkInertiaError=0;
for(let deg=100;deg<=165;deg+=.5){
  const eps=1e-5, de=eps*180/Math.PI;
  function points(q){const g=sourceCtx.reference.state(p,q),hip=[0,-g.Pg[1]/1000];return [hip,[g.Bg[0]/1000,hip[1]+g.Bg[1]/1000],[g.Pg[0]/1000,0]];}
  const plus=points(deg+de),minus=points(deg-de);
  const velocities=plus.map((v,i)=>v.map((x,j)=>(x-minus[i][j])/(2*eps)));
  const m=M.calculate({...loaded,pose:deg}), J=m.J;
  let inertia=(35/4)*velocities[0][1]**2;
  for(const [i,mass] of [[0,.6],[1,.65]]){
    for(const t of [.5-.5/Math.sqrt(3),.5+.5/Math.sqrt(3)]){
      const v=velocities[i].map((x,j)=>(1-t)*x+t*velocities[i+1][j]);
      inertia+=mass*.5*(v[0]**2+v[1]**2);
    }
  }
  const actual=m.effectiveMass*J*J;
  maxLinkInertiaError=Math.max(maxLinkInertiaError,Math.abs(actual-inertia));near(actual,inertia,3e-9);
  near(m.kh,m.effectiveMass*(2*Math.PI*2)**2);
  near(M.calculate({...loaded,pose:deg,mode:'direct',stiffness:2000,verticalDamping:150}).kh,2000);
}
// Direct gains stay fixed as mass changes; the inferred response slows down.
near(M.calculate({...direct,chassisMass:70}).fn,c.fn/Math.sqrt(2));
assert.ok(M.calculate({...direct,upperMass:1}).fn<c.fn);checks++;
// No remote assets, imports, fetches, framework runtime, or bridge needed offline.
assert.ok(!/<(?:script|link|img)[^>]+(?:src|href)\s*=\s*["'](?:https?:|\/\/)/i.test(html));
assert.ok(!/\bfetch\s*\(|\bimport\s*\(|\bXMLHttpRequest\b|localhost/.test(html));checks+=2;
new vm.Script(html.match(/<script id="camel-ui">([\s\S]*?)<\/script>/)[1]);checks++;
const report={date:'2026-10-26',runtime:{node:process.version},model:M.MODEL,geometry:M.GEOMETRY,checks,sourcePoses:651,linkInertiaPoses:131,maxLinkInertiaErrorKgM2:maxLinkInertiaError,maxPathErrorM:maxPathError,maxFiniteDifferenceJacobianErrorMPerRad:maxJacobianError,defaultResults:c,htmlSha256:crypto.createHash('sha256').update(html).digest('hex'),referenceKernelSha256:crypto.createHash('sha256').update(sourceKernel).digest('hex'),sourceNormalizedSha256:'37767388cfd20ae6fe7a03fd932a75f13660f773db5c875b6d902f3a35208cff',sourceNormalization:'Kernel extracted verbatim from the retained LF-normalized HTML; see reference/README.md.',sourceOriginalGitBlob:'1aef847b69c4cba4c63960870cea4fd37c59f16f',limitations:'Arithmetic and source parity only; not hardware gains, body dynamics or contact validation.'};
if(process.argv.includes('--write')){
  fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(report,null,2)+'\n');
  fs.writeFileSync(path.join(__dirname,'default-setup.json'),JSON.stringify(M.serialize(d),null,2)+'\n');
}
console.log(JSON.stringify(report,null,2));
