/** Verify actual embedded V4 finite-radius pulley, preload and solver models.
 * Run: node verify-pulley.cjs [--output]. Inputs: deterministic mm/deg/N/kg cases.
 * Outputs: numerical assertion summary and optional compact JSON evidence.
 * Tangency/energy/equilibrium checks are analytical consistency, not hardware tests.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'v4-pulley.html'),'utf8'),scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);scripts.forEach(s=>new vm.Script(s));
const {VSL:k,VSLStatic:s,VSLUnassisted:base,VSLSpring:sp,VSLPeaks:peaks,VSLDomains:dom,VSLFit:fit}=vm.runInNewContext(scripts.slice(0,3).join('\n')+';({VSL,VSLStatic,VSLUnassisted,VSLSpring,VSLPeaks,VSLDomains,VSLFit});');
let checks=0,seed=9417,maxDerivativeError=0,maxEnergyError=0,maxForceError=0,maxMomentError=0;
const random=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/2**32;},near=(a,b,t=1e-7)=>{assert.ok(Math.abs(a-b)<=t,`${a} != ${b}; tolerance ${t}`);checks++;},p={...s.defaults};
assert.equal(s.validate(p).length,0);
for(let i=0;i<600;i++){
 const r=40+50*random(),pp={...p,hornR:r,Sv:r+30+90*random(),Su:40*random()-20,nu:20*random()-10,rs:i%5?8*random():0,p0:500*random(),springK:i%17?20*random():0,alpha:45*random(),m1:8+random(),m2:random(),m3:random(),m5:random(),m6:random(),Fn:180*random()-30,Ft:70*random()-35,Fy:150*random()-50,Fz:180*random(),beta:90*random(),loadMode:i%2?'yz':'nt',te:100,tc:260},t=102+154*random(),z=s.solve(pp,t),g=z.spring,h=1e-6,plus=sp.state(pp,t+h/k.rad),minus=sp.state(pp,t-h/k.rad);
 assert.ok(z.valid,g.reason);checks++;
 near(sp.state(pp,90).force,pp.p0);near(g.force,Math.max(0,pp.p0+pp.springK*g.delta));near(g.delta,g.payout-sp.geometry(pp,90).payout);
 const dfd=(plus.payout-minus.payout)/(2*h),efd=(plus.energy-minus.energy)/(2*h);near(dfd,g.derivative,2e-6);near(efd,-g.tauS,2e-5);maxDerivativeError=Math.max(maxDerivativeError,Math.abs(dfd-g.derivative));maxEnergyError=Math.max(maxEnergyError,Math.abs(efd+g.tauS));
 near(base.norm(base.sub(g.Q,g.S)),pp.rs,1e-8);near(base.dot(base.sub(g.Q,g.S),g.unit),0,1e-8);near(base.norm(g.unit),1,1e-9);near(base.cross(g.D,g.Flocal)/1000,g.tauS);near(g.tangentLength+pp.rs*g.wrap,g.payout);
 near(z.tau2,z.tauG-z.tauS);near(z.tau2Applied,z.tau2);near(z.maxForce,0,1e-9);near(z.maxMoment,0,1e-9);near(z.virtualWorkError,0,1e-9);maxForceError=Math.max(maxForceError,z.maxForce);maxMomentError=Math.max(maxMomentError,z.maxMoment);
 const b=base.solve(pp,t),off=s.solve({...pp,springEnabled:false},t);near(z.tauG,b.tau2);near(z.tau4,b.tau4);near(z.ab.delta,b.ab.delta);near(z.F12[0],b.F12[0]-g.Flocal[0]);near(z.F12[1],b.F12[1]-g.Flocal[1]);near(off.tau2,b.tau2);near(off.F12[0],b.F12[0]);
 // Include BOTH fixed-pulley force and remote spring-anchor force/moment.
 const anchor=[pp.Su+300,pp.Sv+pp.rs],frameF=base.add(z.Fpulley,z.FspringAnchor),frameM=(base.cross(g.S,z.Fpulley)+base.cross(anchor,z.FspringAnchor))/1000;
 near(frameF[0],-g.Flocal[0]);near(frameF[1],-g.Flocal[1]);near(frameM,-g.tauS);near(z.tau2Applied-frameM,b.tau2);
 for(const key of ['tau2','tauG','tauS','tau4','Fs'])near(s.solve(pp,t,false)[key],z[key]);
 // Independent virtual-work objective used by the maximum search.
 near(peaks.value(peaks.coefficients(pp,t).tau2,pp.alpha*k.rad,pp.beta*k.rad),z.tau2);
}
// Ideal point-pulley cancellation, including tilted A/B and unequal horn/mount lengths.
for(const alpha of [0,20,45])for(const h of [80,120,170]){
 let a={...p,alpha,Sv:h,rs:0,p0:0,Su:0,nu:0};a=sp.resolveDriven(a,'springK');a.p0=a.springK*sp.position(a,90).d;
 for(let t=100;t<=265;t+=1.3){const z=s.solve(a,t);near(z.tau2,0,1e-9);near(z.spring.supportRatio,1,1e-9);}
}
// Free-length independence is embodied in force-reference coordinates; p0 is force.
for(const key of ['springK','hornR','Sv']){const a=sp.resolveDriven({...p,m2:2,m3:1,alpha:20},key);near(a.springK*a.hornR*a.Sv,2*(p.m1+3)*9.81*300*Math.cos(20*k.rad));}
near(sp.resolveDriven({...p,nu:25,Su:20},'springK').springK,sp.resolveDriven(p,'springK').springK);
near(sp.resolveDriven({...p,springK:4},null).springK,4);
assert.throws(()=>sp.resolveDriven({...p,Sv:0},'springK'));assert.ok(s.validate({...p,hornR:120,Sv:120,rs:2,Su:0}).some(x=>x.includes('90°')));assert.ok(!sp.geometry({...p,hornR:120,Sv:120,rs:2,Su:0},90).valid);
// All graph domain combinations, offset windows and zero-width windows.
const ranges={alpha:{min:12,max:27},beta:{min:20,max:65}};
for(const expanded of [false,true])for(const clamp of [false,true]){const th=dom.theta(p,expanded,clamp);near(th.min,clamp?100:90);near(th.max,clamp?165:expanded?270:180);for(const key of ['alpha','beta']){const z=dom.axis(p,ranges,key,expanded,clamp);near(z.min,clamp?ranges[key].min:0);near(z.max,clamp?ranges[key].max:key==='beta'?90:45);}}
assert.ok(dom.theta({...p,te:100,tc:100},false,true).max>100);checks++;
// Exact spring-force extrema and conservative motor bounds, including slack/k=0.
const start=performance.now();let peakCases=0;
for(let i=0;i<24;i++){
 const r=50+30*random(),pp={...p,hornR:r,Sv:r+35+90*random(),Su:30*random()-15,nu:20*random()-10,rs:8*random(),springK:i%6?15*random():0,p0:i%3?400*random():0,alpha:40*random(),te:100,tc:i%2?170:270,loadMode:i%2?'yz':'nt',Fy:80*random()-40,Fz:150*random(),Fn:150*random(),Ft:50*random()-25,m2:random(),m3:random()},z=peaks.fixedAlpha(pp,ranges);
 assert.ok(z.valid);peakCases++;
 const mx=sp.maximum(pp,pp.te,pp.tc);near(sp.state(pp,mx.theta2).force,mx.value);near(z.Fs.value,mx.value);
 for(let j=0;j<240;j++){const t=pp.te+(pp.tc-pp.te)*j/239,ss=s.solve({...pp,beta:ranges.beta.min+(ranges.beta.max-ranges.beta.min)*random()},t,false);assert.ok(ss.valid);assert.ok(ss.Fs<=mx.value+1e-7);checks+=2;for(const key of ['tau2','tau4','ab','dz']){const actual=key==='ab'?Math.max(ss.ab.U,ss.ab.L):Math.abs(ss[key]);assert.ok(actual<=Math.abs(z[key].value)+z[key].error+1e-7,key+' bound');checks++;}}
 for(const key of ['tau2','tau4','ab','dz']){const a=z[key],q=s.solve({...pp,beta:a.beta},a.theta2,false),actual=key==='ab'?Math.max(q.ab.U,q.ab.L):key==='dz'?Math.abs(q.dz):q[key];near(actual,a.value);assert.ok(a.error<=.001);checks++;}
}
const limited=peaks.fixedAlpha(p,ranges,{maxIterations:0});assert.ok(limited.tau2.error>0&&!limited.tau2.converged);checks++;
// Continuous cable branch when S lies inside the horn circle; verify angle unwrapping.
for(const [nu,tc] of [[0,145],[180,200]]){const a={...p,hornR:80,Sv:30,rs:2,nu,te:100,tc,p0:150};assert.equal(s.validate(a).length,0);const mx=sp.maximum(a,a.te,a.tc);for(let j=0;j<=100;j++){const t=a.te+(a.tc-a.te)*j/100,z=sp.state(a,t),eps=1e-6;assert.ok(z.valid);near((sp.geometry(a,t+eps/k.rad).payout-sp.geometry(a,t-eps/k.rad).payout)/(2*eps),z.derivative,2e-6);assert.ok(z.force<=mx.value+1e-7);checks+=2;}}
near(sp.maximum({...p,springEnabled:false,hornR:120,Sv:120},100,165).value,0);
// Applied CCW sign, signed percent normalization, and preload slope.
for(let theta=100;theta<=165;theta+=1){const a=s.solve(p,theta),b=s.solve({...p,p0:p.p0+100},theta);near(a.tau2,a.tau2Applied);assert.ok(b.tau2>a.tau2);checks++;near(b.tau2-a.tau2,100*a.spring.derivative/1000);near(s.percent(a.tau2,a.tauG),100*a.tau2/Math.abs(a.tauG));}
assert.equal(s.percent(1,0),null);near(s.percent(-2,-100),-2);near(s.percent(2,-100),2);checks++;
// Independently optimized sample evidence must reproduce with the full embedded solver.
const fitting=JSON.parse(fs.readFileSync(path.join(__dirname,'v4-tuning.json'),'utf8'));
for(const c of fitting.cases){let maxNm=0,maxPercent=0;const a={...p,m1:13,m2:0,m3:0,m5:0,m6:0,Fy:0,Fz:13*9.81,loadMode:'yz',alpha:0,beta:0,nu:0,Su:c.Su_mm,hornR:c.rh_mm,Sv:100,rs:c.rs_mm,springK:8,p0:c.p0_N};for(let j=0;j<=6500;j++){const z=s.solve(a,100+65*j/6500,false);assert.ok(z.valid);checks++;maxNm=Math.max(maxNm,Math.abs(z.tau2));maxPercent=Math.max(maxPercent,Math.abs(s.percent(z.tau2,z.tauG)));}near(maxNm,c.maxAbsMotor_Nm,1e-7);near(maxPercent,c.maxAbsPercent,1e-7);}

// Compensation means support/weight minus one, independently of external force input.
near(s.compensationPercent({spring:{supportRatio:.9}}),-10);near(s.compensationPercent({spring:{supportRatio:1.1}}),10);near(s.compensationPercent({spring:{supportRatio:1}}),0);assert.equal(s.compensationPercent({spring:{supportRatio:null}}),null);checks++;
for(const radius of [.1,10]){const f=fit.fit({...p,rs:radius,Su:0,hornR:80,p0:0});assert.ok(f.valid);assert.ok(f.maxError<(radius===10?.00063:.00001));assert.equal(f.parameters.springK,p.springK);assert.equal(f.parameters.Sv,p.Sv);assert.equal(f.parameters.rs,radius);assert.equal(f.parameters.nu,p.nu);checks+=6;for(let j=0;j<=200;j++){const z=s.solve(f.parameters,100+65*j/200,false);assert.ok(z.valid);assert.ok(Math.abs(z.spring.supportRatio-1)<=f.maxError+1e-8);checks+=2;}}
assert.ok(!fit.fit({...p,springK:0}).valid);assert.ok(!fit.fit({...p,m1:0}).valid);checks+=2;
const textbook=JSON.parse(fs.readFileSync(path.join(__dirname,'v4-textbook-10mm.json'),'utf8'));let textbookMaxPercent=0,textbookMaxMotor=0;
for(let j=0;j<=6500;j++){const z=s.solve(textbook.parameters,100+65*j/6500,false);assert.ok(z.valid);checks++;textbookMaxPercent=Math.max(textbookMaxPercent,Math.abs(s.compensationPercent(z)));textbookMaxMotor=Math.max(textbookMaxMotor,Math.abs(z.tau2));}
near(textbookMaxPercent,.06208974973862135,1e-6);near(textbookMaxMotor,.037294802385993364,1e-7);
const summary={checks,peakCases,maxDerivativeError_mm_per_rad:maxDerivativeError,maxEnergyError_Nm:maxEnergyError,maxForceError_N:maxForceError,maxMomentError_Nm:maxMomentError,peakMilliseconds:performance.now()-start,defaults:p,defaultPe_N:sp.state(p,p.te).force,defaultMaxFs:sp.maximum(p,p.te,p.tc)};
if(process.argv.includes('--output'))fs.writeFileSync(path.join(__dirname,'v4-verification.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary,null,2));

