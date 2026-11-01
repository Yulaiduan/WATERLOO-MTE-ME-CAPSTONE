/** Verify independent saved Jump/Landing endpoint bands and work accounting.
 * Run node verify-energy-jump-travel.cjs. Temporary mm/deg/kg/N fixtures produce
 * assertion counts only; no profiles, services or trajectories are modified.
 * Checks geometry, signed endpoint work and metadata, not contact/hardware peaks.
 */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),ctx=vm.createContext({});
for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','energy-analysis.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx,{filename:f});
const P=ctx.KinefoldProjects,A=ctx.KinefoldEnergyAnalysis,V=ctx.KinefoldV4,R=Math.PI/180;
let checks=0;const ok=(a,label)=>{assert.ok(a,label);checks++;},near=(a,b,t=1e-7)=>ok(Math.abs(a-b)<t,`${a} != ${b}`);
const copy=x=>{ctx.data=JSON.stringify(x);return vm.runInContext('JSON.parse(data)',ctx);};
for(const alpha of [0,20])for(const springEnabled of [false,true])for(const includeLegMasses of [false,true]){
 const p=copy(P.v45());p.params.alpha=alpha;p.params.springEnabled=springEnabled;
 p.energyConfig=copy({...P.energyDefaults,dropHeightMm:2000});p.torqueTargetConfig=copy({...P.torqueTargetDefaults,jumpHeightMm:2000});
 p.motorConfig=copy({...P.motorDefaults,enabled:true,gearRatio:10,hipBeltRatio:2,coggingAmplitudeNm:.4,coggingPeriodsPerRev:3,coggingPhaseDeg:17});
 const legacy=A.workspace(p,'landing',{includeLegMasses}),jb=A.jumpTravel(p),mb=A.mechanicalTravel(p),span=mb.availableMaxClearanceMm-mb.availableMinClearanceMm;
 near(jb.qStartDeg,p.params.tc);near(jb.qEndDeg,p.params.te);near(legacy.qEndDeg,p.params.tc-1);
 p.energyConfig.travelRanges=copy({jump:{minClearanceMm:mb.availableMinClearanceMm+.1*span,maxClearanceMm:mb.availableMaxClearanceMm-.1*span},landing:{minClearanceMm:mb.availableMinClearanceMm+.2*span,maxClearanceMm:mb.availableMaxClearanceMm-.2*span}});
 const saved=JSON.stringify(p),decoded=P.decode(copy(p)).project;ok(JSON.stringify(decoded.energyConfig)===JSON.stringify(p.energyConfig),'portable decode preserves both independent bands');
 for(const kind of ['landing','jump']){
  const range=p.energyConfig.travelRanges[kind],z=A.workspace(p,kind,{includeLegMasses}),ref=ctx.Kinefold.reference(p.params),q0=z.qStartDeg,q1=z.qEndDeg;
  const body=q=>{const s=V.VSL.state(ref,q),h=p.params.rw-s.Pg[1],m=includeLegMasses?p.params:{...p.params,m2:0,m3:0,m5:0};return p.params.g/1000*(m.m1*h+m.m2*(h+s.Bg[1]/2)+m.m3*(h+(s.Bg[1]+s.Pg[1])/2)+m.m5*(h+s.Bg[1])+m.m6*p.params.rw);};
  const spring=q=>springEnabled?V.VSLSpring.state(ref,q).energy:0;
  const cog=q=>.4/3*Math.cos(3*20*q*R+17*R),gravity=body(q1)-body(q0),springDelta=spring(q1)-spring(q0),cogDelta=cog(q1)-cog(q0);
  const flight=(p.params.m1+(includeLegMasses?p.params.m2+p.params.m3+p.params.m5:0)+p.params.m6)*p.params.g*2;
  const drop=(p.params.m1+(includeLegMasses?p.params.m2+p.params.m3+p.params.m5:0))*p.params.g*2;
  const work=kind==='jump'?gravity+springDelta+cogDelta+flight:drop-gravity-springDelta-cogDelta;
  near(z.initialClearanceMm,kind==='jump'?range.minClearanceMm:range.maxClearanceMm);near(z.endClearanceMm,kind==='jump'?range.maxClearanceMm:range.minClearanceMm);
  near(z.angularTravelRad,Math.abs(q1-q0)*R);near(z.workJ,work);near(z.requiredJointNm,Math.max(0,work/z.angularTravelRad));
  near(z.stroke[0].hipAngleDeg,q0);near(z.stroke.at(-1).hipAngleDeg,q1);near(z.stroke.at(-1).gravityDeltaJ,gravity);near(z.stroke.at(-1).springDeltaJ,springDelta);near(z.stroke.at(-1).coggingDeltaJ,cogDelta);near(z.endpointKineticBudgetJ,kind==='jump'?flight:0);
  const other=kind==='jump'?'landing':'jump',beforeOther=A.workspace(p,other,{includeLegMasses}).requiredJointNm,altered=copy(p);altered.energyConfig.travelRanges[kind].maxClearanceMm-=.05*span;
  ok(Math.abs(A.workspace(altered,kind,{includeLegMasses}).requiredJointNm-z.requiredJointNm)>1,'changing maximum changes work/travel torque');near(A.workspace(altered,other,{includeLegMasses}).requiredJointNm,beforeOther);
 }
 near(A.landingEstimate(p,2000,50,{includeLegMasses}).requiredJointNm,legacy.requiredJointNm);
 const noRanges=copy(p);delete noRanges.energyConfig.travelRanges;
 near(A.jumpEstimate(p,2000,{includeLegMasses}).jointNm,A.jumpEstimate(noRanges,2000,{includeLegMasses}).jointNm);
 ok(JSON.stringify(p)===saved,'all calculations are pure');
 const stale=copy(p);stale.params.L2=100;stale.params.L3=100;assert.throws(()=>A.workspace(stale,'jump',{includeLegMasses}),/envelope/);checks++;
}
const p=copy(P.v45()),b=A.mechanicalTravel(p),valid={minClearanceMm:b.availableMinClearanceMm,maxClearanceMm:b.availableMaxClearanceMm};
for(const bad of [null,[],{minClearanceMm:10},{...valid,extra:1},{minClearanceMm:valid.maxClearanceMm,maxClearanceMm:valid.minClearanceMm},{minClearanceMm:1,maxClearanceMm:1},{minClearanceMm:-1,maxClearanceMm:100},{minClearanceMm:NaN,maxClearanceMm:100},{minClearanceMm:0,maxClearanceMm:Infinity},{minClearanceMm:false,maxClearanceMm:100},{minClearanceMm:'0',maxClearanceMm:100}]){
 ctx.bad=bad;ctx.base=copy(P.energyDefaults);assert.throws(()=>vm.runInContext('KinefoldProjects.validateEnergy({...base,travelRanges:{jump:bad}})',ctx));checks++;
}
assert.throws(()=>P.validateEnergy(copy({...P.energyDefaults,travelRanges:{terrain:valid}})));checks++;
console.log('PASS '+checks+' independent Jump/Landing range, saved schema, endpoint work, geometry drift and physical-guidance assertions.');
