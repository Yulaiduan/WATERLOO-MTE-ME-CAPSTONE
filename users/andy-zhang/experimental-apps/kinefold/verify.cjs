/** Verify Kinefold's actual adapter and preserved V4 blocks. Run: node verify.cjs.
 * Inputs: deterministic mm/deg/kg/N cases. Outputs: assertion count and max errors.
 * Covers coordinate/force/torque transformations and cable work, not hardware.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=__dirname,read=f=>fs.readFileSync(path.join(root,f),'utf8');
for(const f of ['reference-v4.js','model.js','variables.js','app.js','conventions.js'])new vm.Script(read(f),{filename:f});
const ctx=vm.createContext({});vm.runInContext(read('reference-v4.js')+'\n'+read('model.js')+'\n'+read('variables.js'),ctx);
const {Kinefold:M,KinefoldV4:R,KinefoldFields:F}=ctx;
let checks=0,maxGeometryError=0,maxEnergyError=0;
const near=(a,b,tol=1e-8)=>{assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=tol,`${a} versus ${b} (tolerance ${tol})`);checks++;};
const ok=v=>{assert.ok(v);checks++;};
const provenance=JSON.parse(read('reference.json')),source=path.resolve(root,'../../../..',provenance.source);
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
ok(hash(fs.readFileSync(source,'utf8').replace(/\r\n/g,'\n'))===provenance.source_sha256);
const scripts=[...fs.readFileSync(source,'utf8').replace(/\r\n/g,'\n').matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
const retained=[...scripts.slice(0,2),scripts[2].split('const VSLDomains=')[0]].join('\n');
ok(hash(retained)===provenance.retained_blocks_sha256);ok(read('reference-v4.js').includes(retained));
for(const angle of [100,115,132.5,145,165])for(const alpha of [0,15,45])for(const springLaw of ['v4','constant']){
const p={...M.defaults,theta2:angle,alpha,springLaw},z=M.evaluate(p),r=M.reference(p),s=R.VSLStatic.solve(r,angle);
ok(z.valid);near(z.A[0],0);near(z.B[0],-s.Bg[0]);near(z.B[2],s.Bg[1]);near(z.C[0],-s.Cg[0]);near(z.C[2],s.Cg[1]);near(z.C[1],0);
near(Math.hypot(...z.B),p.L2);near(Math.hypot(...z.C.map((v,i)=>v-z.B[i])),p.L3);near(z.spring.force,s.Fs);near(z.raw.tau2+s.tauG+s.tauS,0);
near(z.travel,(2*p.L2*(Math.sin(p.te*Math.PI/180)-Math.sin(p.tc*Math.PI/180)))*Math.cos(alpha*Math.PI/180),1e-7);
if(springLaw==='constant')near(z.spring.force,p.p0);
const step=1e-5,plus=M.evaluate({...p,theta2:angle+step*180/Math.PI,te:90,tc:270}),minus=M.evaluate({...p,theta2:angle-step*180/Math.PI,te:90,tc:270});
if(plus.valid&&minus.valid){const error=Math.abs((plus.spring.energy-minus.spring.energy)/(2*step)+z.spring.tauS);maxEnergyError=Math.max(maxEnergyError,error);ok(error<1e-5);}
}
for(let i=0;i<150;i++){
const p={...M.defaults,L2:250+i*.4,L3:230+i*.6,alpha:i%46,phi0:i%31,theta2:105+i%55,m2:.3,m3:.4,m5:.2,m6:.9,loadMode:i%2?'global':'contact',Fx:40-i,Fz:90+i,Fn:70+i,Ft:i-65,beta:i%91,Tab0:i,Tcd0:i*.2,Tef0:i*.3};
const z=M.evaluate(p);ok(z.valid);const r=z.reference,s=z.raw;
near(z.force[0],-s.FcontactG[0]);near(z.force[2],s.FcontactG[1]);
const b=p.beta*Math.PI/180,arm=z.P.map((v,i)=>v-z.C[i]);near(arm[0],p.rw*Math.sin(b));near(arm[2],-p.rw*Math.cos(b));
const momentY=(arm[2]*z.force[0]-arm[0]*z.force[2])/1000;near(momentY,s.Mw);
near(s.maxForce,0,1e-8);near(s.maxMoment,0,1e-8);near(s.virtualWorkError,0,1e-8);
// Independent full three-dimensional cross product: new tau_y = old tau_x.
const rr=[-s.Cg[0],0,s.Cg[1]],ff=z.force;
near(rr[2]*ff[0]-rr[0]*ff[2],s.Cg[0]*s.FcontactG[1]-s.Cg[1]*s.FcontactG[0]);
const expected=R.VSL.state(r,p.theta2);maxGeometryError=Math.max(maxGeometryError,Math.abs(z.C[0]+expected.Pg[0]),Math.abs(z.C[2]-expected.Pg[1]));
}
for(const mass of [0,2,20]){const p={...M.defaults,m1:mass,m2:.3,g:9.7};near(M.evaluate(p).force[2],(mass+.3)*9.7);}
const params={...M.defaults,loadMode:'global',Fx:31,Fz:81};near(M.evaluate({...params,m1:99}).force[0],31);near(M.evaluate({...params,m1:99}).force[2],81);
const disabled=M.evaluate({...M.defaults,springEnabled:false,Sv:0,Su:0,rs:1000});ok(disabled.valid);near(disabled.raw.Fs,0);
for(const change of [{L2:0},{rs:1000},{te:170,tc:160},{theta2:99},{loadMode:'unknown'},{springLaw:'unknown'},{Fx:NaN},{springEnabled:'true'},{springK:-1}])ok(M.validate({...M.defaults,...change}).length>0);
const snapshot=M.pack(params,{projection:'iso'},'Case 1');const restored=M.unpack(JSON.parse(JSON.stringify(snapshot)));near(restored.params.Fx,31);ok(restored.name==='Case 1');ok(restored.view.projection==='iso');
for(const value of [{schema:'other',params}, {...snapshot,params:{...params,L2:-1}}, {...snapshot,params:{...params,springK:'8'}}])assert.throws(()=>M.unpack(value));checks+=3;
const fields=F.flatMap(g=>g.sections.flatMap(([,fields])=>fields));ok(fields.length===34);ok(new Set(fields.map(f=>f[0])).size===fields.length);
for(const field of fields){ok(field[0] in M.defaults);ok(field[7].length>15);}
console.log(JSON.stringify({status:'PASS',assertions:checks,sourceBlocks:'preserved with LF newline normalization',maxGeometryError_mm:maxGeometryError,maxCableEnergyDerivativeError_Nm:maxEnergyError,limitations:'Analytical consistency only; no hardware, terrain or canonical robot validation.'},null,2));
