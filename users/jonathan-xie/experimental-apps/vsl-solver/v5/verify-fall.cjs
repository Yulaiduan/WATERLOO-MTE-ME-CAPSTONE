/** Verify V5 vertical catch against analytic and independent time-domain results.
 * Run: node verify-fall.cjs [--output]. Inputs local V5/V4 code; mm/deg/kg/N/Nm/m/s.
 * Outputs assertions and optional v5-verification.json; never writes a workbook.
 * Numerical consistency only: no contact, motor, controller or hardware validation.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const dir=__dirname,html=fs.readFileSync(path.join(dir,'v5-fall.html'),'utf8'),scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].filter(m=>!m[1].includes('src=')).map(m=>m[2]),model=fs.readFileSync(path.join(dir,'fall-model.js'),'utf8');
for(const script of scripts)new vm.Script(script);for(const file of ['fall-model.js','fall-ui.js','config-library-model.js'])new vm.Script(fs.readFileSync(path.join(dir,file),'utf8'));
const {VSLFall:fall,VSLStatic:stat,VSLSpring:spring,VSL:kin}=vm.runInNewContext(scripts.slice(0,2).join('\n')+'\n'+model+'\n;({VSLFall,VSLStatic,VSLSpring,VSL});');
let checks=0;const near=(a,b,t=1e-8)=>{assert(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} != ${b} (tol ${t})`);checks++;};const ok=(x,msg)=>{assert(x,msg);checks++;};
const p={...stat.defaults},original=JSON.stringify(p),normal=fall.solve(p,.25);
ok(normal.valid,normal.reason);near(normal.rows[0].vz,-Math.sqrt(2*p.g*.25));near(normal.rows.at(-1).vz,0);near(normal.rows[0].dz,0);near(normal.rows.at(-1).dz,kin.state(p,p.tc).dz);near(normal.energyResidualJ,0,1e-10);ok(normal.monotonicDeceleration);near(normal.peaks.vz,normal.impactSpeed);
for(let i=0;i<normal.rows.length;i++){const r=normal.rows[i];near(r.Fz,normal.massKg*p.g*(1+r.aG),1e-10);near(r.tau2,-normal.brakingTorqueNm);if(i)ok(r.time>normal.rows[i-1].time,'time must advance');if(i&&i<normal.rows.length-1)ok(r.K>0,'interior kinetic energy');}
near(normal.impactEnergyJ+p.g*normal.massKg*normal.strokeM,normal.deltaSpringEnergyJ+normal.brakingTorqueNm*normal.angleStrokeRad,1e-10);
// Independent constant-J, zero-spring fixture has uniform physical deceleration.
const fixture=(forceWave=false)=>vm.runInNewContext(model+';VSLFall;',{
 VSLSpring:{totalMass:p=>p.m1,state:(p,t)=>{const q=(t-p.te)*Math.PI/180;return {valid:true,Jz:400,tauS:forceWave==='bump'?-10*Math.PI*Math.sin(2*Math.PI*q):forceWave?20*Math.cos(Math.PI*q):0,energy:forceWave==='bump'?10*Math.sin(Math.PI*q)**2:forceWave?-20/Math.PI*Math.sin(Math.PI*q):0,force:0};}},
 VSL:{state:(p,t)=>({dz:400*(t-p.te)*Math.PI/180})}
});
const f=fixture(),fp={m1:10,g:9.81,te:100,tc:100+180/Math.PI},fr=f.solve(fp,.2);
ok(fr.valid,fr.reason);near(fr.brakingTorqueNm,10*9.81*.6);near(fr.peaks.aG,.5);near(fr.peaks.Fz,10*9.81*1.5);near(fr.catchTimeS,Math.sqrt(2*9.81*.2)/(.5*9.81),2e-8);
for(const r of fr.rows){near(r.aG,.5);near(r.vz,-Math.sqrt(2*9.81*.2)+.5*9.81*r.time,3e-8);near(r.dz/1000,Math.sqrt(2*9.81*.2)*r.time-.25*9.81*r.time*r.time,3e-8);}
const noContact=fixture(true).solve({...fp,m1:1},.01);ok(!noContact.valid&&noContact.reason.includes('negative ground force'),noContact.reason);
// Exact point-pulley gravity compensation leaves only drop energy for the motor.
let ideal={...p,rs:0,Su:0,nu:0,hornR:60,Sv:100,alpha:20};ideal.springK=spring.target(ideal)/(ideal.hornR*ideal.Sv);ideal.p0=ideal.springK*Math.abs(ideal.Sv-ideal.hornR);
const ir=fall.solve(ideal,.25);ok(ir.valid,ir.reason);near(ir.deltaSpringEnergyJ,ir.massKg*ideal.g*ir.strokeM,1e-10);near(ir.brakingTorqueNm,ir.massKg*ideal.g*.25/ir.angleStrokeRad,1e-10);
for(const r of ir.rows)near(r.K,ir.impactEnergyJ*(1-(r.theta-ideal.te)/(ideal.tc-ideal.te)),1e-9);
// Integrate xdot=w, wdot=g+(tau2+tauS)/(mJ) independently in real time.
function integrateTime(pp,reference){
 const m=spring.totalMass(pp),L=2*pp.L2*Math.cos(pp.alpha*Math.PI/180)/1000,sinE=Math.sin(pp.te*Math.PI/180),dt=reference.catchTimeS/24000,T=reference.brakingTorqueNm;
 const rhs=(x,w)=>{const arg=sinE-x/L;if(Math.abs(arg)>=1)throw Error('ODE inversion outside branch');const theta=(Math.PI-Math.asin(arg))*180/Math.PI,s=spring.state(pp,theta),J=-L*Math.cos(theta*Math.PI/180);return [w,pp.g+(-T+s.tauS)/(m*J)];};
 let x=0,w=reference.impactSpeed,time=0;
 for(let i=0;i<26000;i++){
  const a=rhs(x,w),b=rhs(x+dt*a[0]/2,w+dt*a[1]/2),c=rhs(x+dt*b[0]/2,w+dt*b[1]/2),d=rhs(x+dt*c[0],w+dt*c[1]);
  const xn=x+dt*(a[0]+2*b[0]+2*c[0]+d[0])/6,wn=w+dt*(a[1]+2*b[1]+2*c[1]+d[1])/6;
  if(wn<=0){const frac=w/(w-wn);return {stroke:x+(xn-x)*frac,time:time+dt*frac};}x=xn;w=wn;time+=dt;
 }
 throw Error('Independent integration did not stop.');
}
const ode=[];for(const pp of [p,ideal,{...p,springEnabled:false,alpha:30}]){const r=fall.solve(pp,.25);ok(r.valid,r.reason);const independent=integrateTime(pp,r);near(independent.stroke,r.strokeM,2e-8);near(independent.time,r.catchTimeS,2e-7);ode.push({alpha:pp.alpha,spring:pp.springEnabled,strokeErrorM:independent.stroke-r.strokeM,timeErrorS:independent.time-r.catchTimeS});}
for(const h of [.1,.25,.8])for(const alpha of [0,15,30]){const pp={...p,alpha},r=fall.solve(pp,h);ok(r.valid,r.reason);near(r.impactSpeed,Math.sqrt(2*pp.g*h));near(r.peaks.dz,kin.state(pp,pp.tc).dz,1e-8);near(r.energyResidualJ,0,1e-8);}
const loads=fall.solve({...p,beta:70,Fz:5,Fy:300,Ft:20,Fn:15,loadMode:'nt'},.25);near(loads.brakingTorqueNm,normal.brakingTorqueNm);near(loads.catchTimeS,normal.catchTimeS);ok(JSON.stringify(p)===original,'input mutation');
for(const pp of [{...p,m1:0},{...p,g:0},{...p,te:90},{...p,tc:270},{...p,tc:p.te},{...p,springK:80,p0:4000}])ok(!fall.solve(pp,.25).valid,'invalid regime accepted');ok(!fall.solve(p,-1).valid);ok(!f.solve(fp,0).valid);
const early=fixture('bump').solve({...fp,m1:1},.1);ok(!early.valid&&early.reason.includes('before θ₂ᶜ'),early.reason);
const low=fall.solve(p,.05),high=fall.solve(p,.5);near(low.strokeM,high.strokeM);ok(high.brakingTorqueNm>low.brakingTorqueNm);near(high.brakingTorqueNm-low.brakingTorqueNm,normal.massKg*p.g*.45/normal.angleStrokeRad);
// Alpha bounds and no coupling to fall height in geometric peaks.
const study=fall.study(p,.25,{min:5,max:25},{samples:160,sweepSamples:80});near(study.sweep[0].alpha,5);near(study.sweep.at(-1).alpha,25);ok(study.sweep.every(s=>s.valid));for(const s of study.sweep)near(s.peaks.vz,normal.impactSpeed);
const library=require(path.join(dir,'config-library-model.js')),columns=JSON.parse(fs.readFileSync(path.join(dir,'config-library-columns.json'),'utf8'));ok(JSON.stringify(columns)===JSON.stringify(library.columns),'browser/server library columns disagree');
const doc=library.add(library.empty()).document;doc.rows[0].snapshot={schema:'general-vsl/v5-fall',parameters:p,torqueConvention:'physical-link2-ccw/v2',fallStudy:{heightM:.7,massBounds:{min:2,max:20},heightBounds:{min:0,max:1}}};ok(library.validate(doc).rows[0].snapshot.fallStudy.heightM===.7);
const corePath=path.join(dir,'../v4/v4-pulley.html');let corePreserved=null;if(fs.existsSync(corePath)){const oldScripts=[...fs.readFileSync(corePath,'utf8').matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].filter(m=>!m[1].includes('src=')).map(m=>m[2]);corePreserved=scripts.slice(0,2).every((s,i)=>s.replace(/\r\n/g,'\n')===oldScripts[i].replace(/\r\n/g,'\n'));ok(corePreserved,'V4 static core changed');}
const summary={checks,corePreserved,modelSha256:require('node:crypto').createHash('sha256').update(model).digest('hex'),normal:{torqueNm:normal.brakingTorqueNm,catchTimeS:normal.catchTimeS,impactSpeed:normal.impactSpeed,peakAccelerationG:normal.peaks.aG,peakForceN:normal.peaks.Fz,strokeMm:normal.strokeM*1000},independentTimeDomain:ode,constantAccelerationTimeErrorS:fr.catchTimeS-Math.sqrt(2*9.81*.2)/(.5*9.81),earlyStopReason:early.reason,scope:'vertical point-mass numerical checks; not hardware validation'};
if(process.argv.includes('--output'))fs.writeFileSync(path.join(dir,'v5-verification.json'),JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary,null,2));
