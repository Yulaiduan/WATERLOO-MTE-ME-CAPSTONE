/** Validate generalized VSL study against the immutable Jonathan v2 source and
 * independent derivatives/work/integrals. Run: node --test tests/design-study.test.js.
 * Inputs mm/deg/kg/N; assertions Nm/N/mm; no hardware or dynamics certification.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import '../model.js';
import {metrics as equalMetrics} from '../../wheel-leg-lab/web/force-plots/link-sweep-model.js';
const M=globalThis.DesignStudyModel;
const cfg=(changes={})=>({...structuredClone(M.DEFAULT_CONFIG),...changes});
const near=(a,b,tol=1e-8)=>assert.ok(Math.abs(a-b)<=tol,`${a} vs ${b}`);
const original=fs.readFileSync(new URL('../../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html',import.meta.url),'utf8');
const context=vm.createContext({Math});
for(const id of ['solver-model','statics-model']) {
  const script=original.match(new RegExp(`<script id="${id}">([\\s\\S]*?)<\\/script>`))[1];
  vm.runInContext(script,context);
}
vm.runInContext('globalThis.reference={VSL,VSLStatic};',context);
const originalModel=context.reference;
test('screenshot baseline retains original pose, forces and signed torque',()=>{
  const p=cfg(),s=M.statics(p,100.135),end=M.kinematics(p,165);
  near(s.t3,53.2433333333333);near(s.tau2,-25.6296597,1e-7);near(s.tau4,-14.7784911,1e-7);
  near(Math.max(s.ab.U,s.ab.L),84.4859843,1e-7);assert.equal(s.ab.active,'L');
  near(end.dy,101.157121828,1e-7);near(end.dz,338.615930749,1e-7);
});
test('general ratios and masses reproduce actual original statics and kinematics',()=>{
  for(let i=0;i<40;i++){
    const p=cfg({L2:230+i*3,L3:310-i,ra:62+i,rb:40,rc:30+i*.2,rd:32,re:25+i*.1,rf:28,
      alpha:i%30,beta:i*2,phi0:i%9,m2:.2+i*.01,m3:.4,m5:.1,m6:1,Tab0:20,Tcd0:12,Tef0:8,Fy:-70+i*4,Fz:120});
    const t=100+i*1.5,a=M.statics(p,t),b=originalModel.VSLStatic.solve(p,t,true);
    for(const k of ['tau2','tau4','dy','dz','t3','t5','t6'])near(a[k],b[k],1e-10);
    for(const k of ['ab','cd','ef'])for(const j of ['U','L','delta'])near(a[k][j],b[k][j],1e-9);
    for(const k of ['F12','F14','F25','F32','Fw','Fground'])for(let j=0;j<2;j++)near(a[k][j],b[k][j],1e-9);
    near(a.virtualWorkError,0,1e-10);
  }
});
test('analytic generalized Jacobian matches central difference after clockwise frame transform',()=>{
  const p=cfg({L2:280,L3:240,ra:87,rb:53,alpha:22,phi0:7});
  for(const t of [105,130,160]){const s=M.kinematics(p,t),h=1e-5;
    const a=M.kinematics(p,t-h).Cg,b=M.kinematics(p,t+h).Cg;
    for(let j=0;j<2;j++)near((b[j]-a[j])/(2*h*Math.PI/180),s.dCg[j],2e-6);
  }
});
test('equal-link 2:1 special case agrees with Andy torque integrals',()=>{
  const L=250,p=cfg({ra:100,rb:50,Fy:0,Fz:100,beta:0,loadCases:'nominal',startBuffer:{value:0,unit:'mm'},endBuffer:{value:0,unit:'mm'},maxDrift:1e-5,samples:2001,weighting:'angle'});
  const r=M.profile(p),a=(p.te-90)*Math.PI/180,b=(p.tc-90)*Math.PI/180;
  const ref=equalMetrics({load:100,shaft:'hip',weighting:'angle'},L,a,b);
  near(r.metrics.peakTau2,ref.peak,1e-9);near(r.metrics.rmsTau2,ref.rms,2e-6);near(r.metrics.meanAbs,ref.mean,2e-6);
  near(r.metrics.drift,0,1e-10);near(r.metrics.absoluteWorkJ,100*r.metrics.usableTravel/1000,1e-5);
});
test('mm/degree buffer round trips are geometry preserving',()=>{
  const p=cfg();for(const key of ['startBuffer','endBuffer']){
    const d=M.convertBuffer(p,key,'deg'),pp={...p,[key]:{value:d,unit:'deg'}};
    near(M.convertBuffer(pp,key,'mm'),20,1e-8);
  }
  const r=M.profile(p);near(r.metrics.usableTravel,r.metrics.totalTravel-40,1e-8);
});
test('time RMS uses the same explicit one-second quintic height lift as the dynamic fixture',()=>{
  const p=cfg({samples:101}),r=M.profile(p),s=r.samples[25],u=.25;
  near(s.usableDz,r.metrics.usableTravel*(10*u**3-15*u**4+6*u**5),1e-8);
  near(s.timeSeconds,.25);near(r.samples.at(-1).timeSeconds,1);
});
test('radius changes clearance, contact torque and belts, not vertical centre travel',()=>{
  const p=cfg(),a=M.statics(p,130),b=M.statics({...p,rw:120},130);
  near(a.dz,b.dz);near(a.dy,b.dy);near(a.K,b.K);assert.notEqual(a.groundGap,b.groundGap);assert.notEqual(a.tau4,b.tau4);
});
test('preloads and fixed chassis mass affect reactions without changing torque',()=>{
  const p=cfg(),a=M.statics(p,130),b=M.statics({...p,Tab0:80,Tcd0:80,Tef0:80,m1:50},130);
  near(a.tau2,b.tau2);near(a.tau4,b.tau4);assert.notDeepEqual(a.Fground,b.Fground);assert.notDeepEqual(a.F12,b.F12);
});
test('load convention conversion and signed loads preserve physical force and torque',()=>{
  const p=cfg({Fy:-100}),a=M.statics(p,133),r=M.resolveLoads(p),b=M.statics({...r,loadMode:'nt',loadCases:'nominal'},133);
  near(a.tau2,b.tau2);near(a.tau4,b.tau4);assert.ok(a.tau4>0);
});
test('robust objective prevents horizontal assistance from concealing opposite load demand',()=>{
  const p=cfg(),r=M.profile(p),a=M.profile({...p,loadCases:'nominal'}),b=M.profile({...p,Fy:-100,loadCases:'nominal'});
  near(r.metrics.peak,Math.max(...r.loadCases.map(c=>c.peak)));
  assert.ok(r.metrics.peak>=a.metrics.peak&&r.metrics.peak>=b.metrics.peak);assert.ok(r.metrics.robustPeakTau2>b.metrics.peakTau2-1e-7);
  near(r.samples[30].tau2,a.samples[30].tau2);
});
test('reversals, overlap, consumed buffers and drift limits report actual infeasibility',()=>{
  assert.ok(M.validateConfig(cfg({L2:150})).some(s=>s.includes('overlap')));
  assert.equal(M.profile(cfg({startBuffer:{value:400,unit:'mm'}})).feasible,false);
  assert.ok(M.profile(cfg({maxDrift:20})).reasons.some(s=>s.includes('drift')));
  assert.ok(M.profile(cfg({ra:180,rb:60,phi0:90})).reasons.some(s=>s.includes('reverses')));
  assert.ok(M.profile(cfg()).reasons.some(s=>s.includes('assumed hip')));
  assert.equal(M.profile(cfg({enforceHipRim:false})).feasible,true);
});
test('bounded single-objective refinement preserves exact 325 total and 285 usable target',()=>{
  const p=cfg({samples:61}),options={domains:{L2:[220,300,40],L3:[220,300,40],qab:[1.6,2.2,.3],alpha:[0,10,10],te:[100,110,10]},refineIterations:3};
  const r=M.optimize(p,options);assert.ok(r.best);near(r.best.metrics.totalTravel,325,1e-7);near(r.best.metrics.usableTravel,285,1e-7);
  const coarse=r.convergence[0].best;assert.ok(r.convergence.at(-2).best<=coarse+1e-8);
  assert.ok(r.best.profile.feasible);assert.equal(r.best.config.Fz,p.Fz);assert.equal(r.best.config.Fy,p.Fy);
  assert.ok(r.best.profile.samples.length>=721);assert.ok(r.evaluations>0);
});
test('Pareto method returns nondominated torque/size/drift alternatives and bounded domains',()=>{
  const p=cfg({samples:51}),domains={L2:[200,320,40],L3:[200,320,40],qab:[1.5,2.5,.25],alpha:[0,20,10],te:[100,120,10]};
  const r=M.optimize(p,{method:'pareto',domains,refineIterations:2});assert.ok(r.pareto.length>1);
  const vector=c=>[c.metrics.peak,c.metrics.size,c.metrics.drift];
  for(const a of r.pareto)for(const b of r.pareto)if(a!==b){const x=vector(a),y=vector(b);assert.ok(!(x.every((v,i)=>v<=y[i]+1e-9)&&x.some((v,i)=>v<y[i]-1e-9)));}
  assert.throws(()=>M.optimize(p,{domains:{Fy:[0,100,10]}}),/geometry only/);
  assert.throws(()=>M.optimize(p,{domains:{L2:[100,500,1]},maxEvaluations:10}),/limit/);
});
