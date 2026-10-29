/** Verify V5 fall-mode force reconstruction and new sweep/plot semantics.
 * Run: node verify-analysis.cjs [--output]. Inputs local app models in mm/deg/kg/m.
 * Output assertions and optional v5-analysis-verification.json. No workbook writes.
 * Checks analytical consistency and endpoint definitions, not physical ratings.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),dir=__dirname;
const html=fs.readFileSync(path.join(dir,'v5-fall.html'),'utf8'),scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].filter(m=>!m[1].includes('src=')).map(m=>m[2]);for(const s of scripts)new vm.Script(s);
const source=scripts.slice(0,2).join('\n')+'\n'+['plot-utils.js','fall-model.js','fall-analysis.js','fall-ui.js'].map(f=>fs.readFileSync(path.join(dir,f),'utf8')).join('\n');
const {VSLFall:fall,VSLFallAnalysis:analysis,VSLFallUI:ui,VSLStatic:stat,VSLSpring:spring}=vm.runInNewContext(source+';({VSLFall,VSLFallAnalysis,VSLFallUI,VSLStatic,VSLSpring});');
let checks=0;const near=(a,b,t=1e-8)=>{assert(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} != ${b}`);checks++;},ok=(x,msg)=>{assert(x,msg);checks++;};
const p={...stat.defaults},a=analysis.create(),h=.25,r=fall.solve(p,h),original=JSON.stringify(p);a.seed(p,h,r);
for(const alpha of [0,10,25])for(const height of [.15,.25,.6])for(let theta=100;theta<=165;theta+=2.5){
 const pp={...p,alpha},s=a.solve(pp,height,theta),tr=a.trajectory(pp,height);ok(s.valid,s.reason);near(s.tau2,-tr.brakingTorqueNm);near(s.Fy,0);near(s.Mw,0);near(s.Fz,tr.massKg*pp.g*(1+s.fall.aG));near(s.maxForce,0,1e-8);near(s.maxMoment,0,1e-8);near(s.virtualWorkError,0,1e-8);
}
const start=a.solve(p,h,p.te),end=a.solve(p,h,p.tc);near(start.fall.vz,-Math.sqrt(2*p.g*h));near(end.fall.vz,0);near(end.fall.time,r.catchTimeS);ok(end.fall.aG>0,'braking acceleration does not have to vanish at first rest');near(end.Fz/(r.massKg*p.g),1+end.fall.aG);
const held=stat.solve({...p,Fy:0,Fz:r.massKg*p.g,beta:0,loadMode:'yz'},p.tc);near(held.Fz/(r.massKg*p.g),1);near(held.Fz/r.massKg-p.g,0);
const mixed={...p,m1:7,m2:1,m3:.5,m5:.2,m6:.3},ms=a.solve(mixed,h,130);ok(ms.valid,ms.reason);near(ms.tau2,-a.trajectory(mixed,h).brakingTorqueNm);near(ms.Fz,9*mixed.g*(1+ms.fall.aG));
const differentManual=a.solve({...p,beta:80,Fy:400,Fz:2,Fn:20,Ft:-300,loadMode:'nt'},h,130);near(differentManual.tau2,a.solve(p,h,130).tau2);near(differentManual.Fz,a.solve(p,h,130).Fz);
ok(!a.solve(p,h,95).valid);ok(!a.solve({...p,tc:270},h,130).valid);ok(!a.solve(p,0,130).valid);ok(JSON.stringify(p)===original,'input mutated');
const peaks=a.globalPeaks(p,h);ok(peaks.valid);near(peaks.tau2.value,-r.brakingTorqueNm);near(peaks.tau4.value,0);near(peaks.Fs.value,spring.maximum(p,p.te,p.tc).value);near(peaks.dz.value,r.strokeM*1000);
const study=fall.study(p,h,{min:10,max:20},{samples:160,sweepSamples:80,heightRange:{min:.1,max:.8}});near(study.heightSweep[0].height,.1);near(study.heightSweep.at(-1).height,.8);ok(study.heightSweep.every(z=>z.valid));ok(study.sweep.every(z=>Number.isFinite(z.catchTimeS)));ok(study.heightSweep[0].catchTimeS>study.heightSweep.at(-1).catchTimeS);ok(study.heightSweep[0].peaks.tau2<study.heightSweep.at(-1).peaks.tau2);
const tight=ui.plotRange([18,19],false),zero=ui.plotRange([18,19],true),negative=ui.plotRange([-3,-2],false),constant=ui.plotRange([20,20]);ok(tight.min>17&&tight.max<20);near(zero.min,0);ok(negative.max<0);ok(constant.min<20&&constant.max>20);const state=ui.normalize({heightM:.5,analysisMode:true,includeZero:true,absolute:true},8.75);ok(state.analysisMode&&state.includeZero&&state.absolute);
const result={checks,brakingTorqueNm:r.brakingTorqueNm,brakingEndAccelerationG:end.fall.aG,brakingEndLoadG:end.Fz/(r.massKg*p.g),holdingAccelerationG:0,holdingLoadG:1,finalVelocityMps:end.fall.vz,alphaSamples:study.sweep.length,heightSamples:study.heightSweep.length,scope:'analytical vertical point-mass fall reconstruction; no hardware rating'};
if(process.argv.includes('--output'))fs.writeFileSync(path.join(dir,'v5-analysis-verification.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
