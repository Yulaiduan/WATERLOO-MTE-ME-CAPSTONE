/** Independent endpoint-work and signed-stroke checks for Energy workspace.
 * Run node verify-energy-workspace.cjs. Inputs temporary baseline projects in
 * mm/deg/kg/N; outputs assertions for equations, ledgers, ranges and purity.
 * Sampling does not validate contact trajectories, transient peaks or hardware.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({});for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','energy-analysis.js','dynamic-analysis.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx,{filename:f});
const P=ctx.KinefoldProjects,A=ctx.KinefoldEnergyAnalysis,V=ctx.KinefoldV4,R=Math.PI/180;
const clone=v=>{ctx.raw=JSON.stringify(v);return vm.runInContext('JSON.parse(raw)',ctx);};
let checks=0;const ok=(v,s)=>{assert.ok(v,s);checks++;},near=(a,b,t=1e-8)=>ok(Math.abs(a-b)<t,`${a} != ${b}`);
const base=P.baseline(),before=JSON.stringify(base),two=clone(base);two.energyConfig={...P.energyDefaults,dropHeightMm:2000};
near(A.workspace(two,'landing').requiredJointNm,232.3451518866197);
for(const kind of ['jump','landing'])for(const law of ['v4','constant'])for(const enabled of [false,true]){
  const p=clone(two);p.params.springLaw=law;p.params.springEnabled=enabled;p.params.m6=1.5;
  p.motorConfig={...P.motorDefaults,enabled:true,gearRatio:7,coggingAmplitudeNm:.7,coggingPeriodsPerRev:3,coggingPhaseDeg:27};
  const original=JSON.stringify(p),z=A.workspace(p,kind,{heightMinMm:50,heightMaxMm:2500,samples:181}),ref=ctx.Kinefold.reference(p.params),m=p.params;
  const height=q=>m.rw-2*m.L2*Math.cos((q-(180+m.phi0)/2)*R)*(-Math.sin(((180+m.phi0)/2-m.alpha)*R));
  const geom90=V.VSLSpring.geometry(ref,90),spring=q=>{const d=V.VSLSpring.geometry(ref,q).payout-geom90.payout;return enabled?(m.p0*d+.5*(law==='constant'?0:m.springK)*d*d)/1000:0;};
  const cog=q=>.7/3*Math.cos((3*7*q+27)*R),start=z.qStartDeg,end=z.qEndDeg,dh=(height(end)-height(start))/1000;
  const springDelta=spring(end)-spring(start),cogDelta=cog(end)-cog(start),gravityDelta=m.m1*m.g*dh;
  const expectedWork=kind==='jump'?gravityDelta+(m.m1+m.m6)*m.g*.1+springDelta+cogDelta:m.m1*m.g*2-gravityDelta-springDelta-cogDelta;
  near(z.workJ,expectedWork);near(z.requiredJointNm,Math.max(0,expectedWork/z.angularTravelRad));near(z.requiredShaftNm,z.requiredJointNm/7);
  near(z.stroke[0].motorWorkJ,0);near(z.stroke[0].kineticBudgetJ,z.initialKineticBudgetJ);near(z.stroke.at(-1).gravityDeltaJ,gravityDelta);near(z.stroke.at(-1).springDeltaJ,springDelta);near(z.stroke.at(-1).coggingDeltaJ,cogDelta);
  for(const row of z.stroke){near(row.hipHeightMm,height(row.hipAngleDeg));near(row.underbodyClearanceMm,height(row.hipAngleDeg)-50);near(row.kineticBudgetJ,z.initialKineticBudgetJ+row.motorWorkJ-row.gravityDeltaJ-row.springDeltaJ-row.coggingDeltaJ);}
  near(z.endpointKineticBudgetJ,kind==='jump'?(m.m1+m.m6)*m.g*.1:0);
  near(z.curve[0].heightMm,50);near(z.curve.at(-1).heightMm,2500);
  const a=z.curve[40],b=z.curve[60];near((b.netMotorWorkJ-a.netMotorWorkJ)/(b.heightMm-a.heightMm),(kind==='jump'?m.m1+m.m6:m.m1)*m.g/1000);
  near(z.generalizedJointCommandNm,-z.requiredJointNm);ok(JSON.stringify(p)===original,'all endpoint calculations pure');
}
ok(JSON.stringify(base)===before&&!('energyConfig'in base)&&!('torqueTargetConfig'in base),'opening calculator does not inject metadata');
const candidate=clone(two);candidate.motorConfig={...P.motorDefaults,enabled:true,gearRatio:9,coggingAmplitudeNm:.4,coggingPeriodsPerRev:5,coggingPhaseDeg:11};candidate.energyConfig.screening={motorId:'flipsky-80100-130',gearboxId:'eg20',peakShaftNm:17,customRatio:1,customMomentaryNm:null};
for(const kind of ['jump','landing']){const z=A.workspace(clone(candidate),kind);near(z.gearRatio,20);near(z.physicalGearRatio,9);near(z.availableJointNm,60);near(z.stroke.at(-1).coggingDeltaJ,.4/5*(Math.cos((5*20*z.qEndDeg+11)*R)-Math.cos((5*20*z.qStartDeg+11)*R)));ok(z.screening.gearboxPass!==null,'known gear assessed');}
const zero=clone(base);zero.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:0};const zeroJump=A.workspace(zero,'jump');ok(zeroJump.workJ<0&&zeroJump.requiredJointNm===0&&zeroJump.endpointKineticBudgetJ>0,'negative demand keeps residual kinetic budget instead of pretending target met');
const barrier=clone(base);barrier.params.springEnabled=false;barrier.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:0};const bz=A.workspace(barrier,'jump');ok(bz.sampledNegativeInteriorCount>0&&bz.minKineticBudgetJ<0&&bz.pathWarning.includes('cannot traverse'),'interior barriers explicit and unclipped');
for(const kind of ['jump','landing'])for(const edit of [p=>p.params.L2=NaN,p=>p.params.m2=.1,p=>p.params.alpha=5,p=>p.params.p0=-10000,p=>p.params.ra=0,p=>p.params.te=p.params.tc,p=>p.motorConfig={...P.motorDefaults,gearRatio:0}]){const p=clone(base);edit(p);assert.throws(()=>A.workspace(p,kind));checks++;}
for(const options of [{heightMinMm:100,heightMaxMm:10},{heightMinMm:-1},{heightMaxMm:5001},{heightMaxMm:NaN},{samples:1}]){assert.throws(()=>A.workspace(base,'jump',options));checks++;}
const meta=clone(base);meta.energyConfig={...P.energyDefaults,dropHeightMm:2000};meta.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:300};ok(ctx.KinefoldDynamicAnalysis.snapshotKey(meta)===ctx.KinefoldDynamicAnalysis.snapshotKey(base),'analysis targets do not stale trajectories');
console.log('PASS '+checks+' detailed energy workspace assertions');
