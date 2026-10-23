/** Check native FBD transforms and exact finite-idler drawing data.
 * Run: node verify-equilibrium-diagrams.cjs. Inputs: baseline and varied static
 * designs in mm/deg/kg/N, independent original V4 analytical blocks. Outputs:
 * assertion count and maximum force/moment errors. Tests analytical geometry,
 * frame/sign conversion, force inventory and SVG finiteness; not hardware or
 * automated visual layout correctness. No runtime dependencies beyond Node.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const read=f=>fs.readFileSync(path.join(__dirname,f),'utf8'),ctx=vm.createContext({});
for(const f of ['reference-v4.js','model.js','equilibrium-diagrams.js'])vm.runInContext(read(f),ctx,{filename:f});
const {Kinefold:M,KinefoldV4:R,KinefoldEquilibriumDiagrams:D}=ctx;
const provenance=JSON.parse(read('reference.json')),source=fs.readFileSync(path.resolve(__dirname,'../../../..',provenance.source),'utf8').replace(/\r\n/g,'\n');
assert.equal(crypto.createHash('sha256').update(source).digest('hex'),provenance.source_sha256);
const scripts=[...source.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]),original=vm.createContext({});
vm.runInContext([...scripts.slice(0,2),scripts[2].split('const VSLDomains=')[0],'globalThis.ORIGINAL={VSL,VSLStatic,VSLSpring};'].join('\n'),original);
let count=1,maxForce=0,maxMoment=0,maxSpringEndpoint=0;
const near=(a,b,tol=1e-8)=>{assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=tol,`${a} vs ${b}, tol ${tol}`);count++;};
const ok=v=>{assert.ok(v);count++;};
for(let i=0;i<45;i++){
  const p={...M.defaults,alpha:i%46,theta2:105+i%55,L2:270+i,L3:230+i*.7,m1:8.75,m2:.25,m3:.3,m5:.2,m6:.8,
    loadMode:i%2?'global':'contact',Fx:35-i,Fz:90+i,Fn:70+i,Ft:i-22,beta:i%91,Tab0:20+i,Tcd0:15+i,Tef0:10+i,
    springLaw:i%3?'v4':'constant'},r=M.reference(p),z=M.evaluate(p),s=original.ORIGINAL.VSLStatic.solve(r,p.theta2,true),data=D.bodyData(p,z.raw);
  ok(z.valid&&s.valid&&data.valid);near(data.bodies.length,5);
  for(const b of data.bodies){
    const old=s.bodies[b.id];near(b.forces.length,old.forces.length);near(b.couples.length,old.couples.length);
    near(Math.hypot(...b.residualF),Math.hypot(...old.residualF),1e-9);near(b.residualM,old.residualM,1e-9);
    maxForce=Math.max(maxForce,Math.hypot(...b.residualF));maxMoment=Math.max(maxMoment,Math.abs(b.residualM));
    for(let j=0;j<b.forces.length;j++){
      const f=b.forces[j],q=old.forces[j],g=original.ORIGINAL.VSL.global(r,q.vec),gp=original.ORIGINAL.VSL.global(r,q.pos);
      ok(f.name===q.name);near(f.vector[0],-g[0]);near(f.vector[1],0);near(f.vector[2],g[1]);
      near(f.point[0],-gp[0]);near(f.point[2],gp[1]);near(f.magnitude,Math.hypot(...q.vec));near(Math.hypot(...f.vector),Math.hypot(...q.vec));
      const arm=f.point.map((v,k)=>v-b.origin[k]),uv=q.pos.map((v,k)=>v-old.origin[k]);
      near(D.momentY(arm,f.vector),(uv[0]*q.vec[1]-uv[1]*q.vec[0])/1000);
    }
    for(let j=0;j<b.couples.length;j++)near(b.couples[j].value,old.couples[j].value);
  }
  const sp=D.springData(p,z),raw=s.spring;ok(sp.valid);near(sp.forceMagnitude,raw.force);near(sp.tauS,raw.tauS);
  near(Math.hypot(...sp.D),p.hornR);near(Math.hypot(...sp.Q.map((v,k)=>v-sp.S[k])),p.rs);
  const tangent=sp.Q.map((v,k)=>v-sp.D[k]),radius=sp.Q.map((v,k)=>v-sp.S[k]);
  near(tangent.reduce((v,x,k)=>v+x*radius[k],0),0,1e-8);near(Math.hypot(...tangent),sp.tangentLength);
  near(sp.payout,sp.tangentLength+p.rs*sp.wrap);near(sp.delta,sp.payout-sp.referencePayout);
  for(const [point,index] of [[sp.Q,0],[sp.out,sp.arc.length-1]]){
    const error=Math.hypot(...point.map((v,k)=>v-sp.arc[index][k]));near(error,0);maxSpringEndpoint=Math.max(maxSpringEndpoint,error);
  }
  const bodyHtml=D.renderBodies(p,z.raw),springHtml=D.renderSpring(p,z);ok(!/NaN|Infinity|undefined/.test(bodyHtml+springHtml));
}
// World +x force renders left and preserves the source-positive axial moment.
const force=D.world({...M.defaults,alpha:0},[-20,0]);near(force[0],20);near(force[2],0);near(D.momentY([0,0,100],force),2);
const disabled={...M.defaults,springEnabled:false,rs:1000};ok(D.springData(disabled,M.evaluate(disabled)).disabled);ok(/disabled/.test(D.renderSpring(disabled,M.evaluate(disabled))));
const invalid={...M.defaults,rs:1000};ok(!D.springData(invalid,M.evaluate(invalid)).valid);ok(!/NaN|Infinity|undefined/.test(D.renderSpring(invalid,M.evaluate(invalid))));
const point={...M.defaults,rs:0},pd=D.springData(point,M.evaluate(point));ok(pd.valid);near(pd.arc.length,0);near(pd.wrap,0);near(Math.hypot(...pd.Q.map((v,k)=>v-pd.S[k])),0);
console.log(JSON.stringify({status:'PASS',assertions:count,cases:45,maxWorldForceResidualN:maxForce,maxWorldMomentResidualNm:maxMoment,maxSpringArcEndpointErrorMm:maxSpringEndpoint,source:'hash-verified original V4 analytical blocks',limitations:'Analytical diagram consistency; no browser visual or hardware validation.'},null,2));
