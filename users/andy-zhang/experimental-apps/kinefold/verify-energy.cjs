/** Independent fixtures and invariants for the standalone drop/torque screen.
 * Run node verify-energy.cjs. Inputs mm/deg/kg/N and SI energy fixtures;
 * outputs assertions. No trajectory, impact peak or hardware validation.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({});for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','energy-analysis.js','dynamic-analysis.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx);
const P=ctx.KinefoldProjects,A=ctx.KinefoldEnergyAnalysis,D=ctx.KinefoldDynamicAnalysis;
const realm=v=>{ctx.raw=JSON.stringify(v);return vm.runInContext('JSON.parse(raw)',ctx);};const clone=v=>realm(v);let checks=0;const ok=(v,m)=>{assert.ok(v,m);checks++;},near=(a,b,t=1e-8)=>ok(Math.abs(a-b)<t,`${a} versus ${b}`);
const p=P.baseline(),original=JSON.stringify(p),z=A.calculate(p);
// Separately evaluated Python baseline supplied in architecture review.
near(z.requiredJointNm,11.6103416382814);near(z.capacityMm,172.214939135932);near(z.qStartDeg,121.666666666667);near(z.qEndDeg,164);near(z.endClearanceMm,315.3824134902);near(z.springReleasedJ,-29.6440023420835);near(z.dropJ,8.58375);near(z.impactSpeedMS**2,2*9.81*.1);
ok(JSON.stringify(p)===original,'pure calculation does not mutate input');ok(!('energyConfig' in P.validate(p)),'legacy absence retained');
const off=clone(p);off.params.springEnabled=false;const bare=A.calculate(off);near(bare.requiredJointNm,51.7318271992,1e-7);
const H=clone(off);H.energyConfig={...P.energyDefaults,dropHeightMm:200};const high=A.calculate(H);near(high.requiredJointNm-bare.requiredJointNm,p.params.m1*p.params.g*.1/z.angularTravelRad);
const atCapacity=clone(p);atCapacity.energyConfig={...P.energyDefaults,dropHeightMm:z.capacityMm};near(A.calculate(atCapacity).requiredJointNm,20);
const clearance=clone(p);clearance.energyConfig={...P.energyDefaults,targetClearanceMm:500};const limited=A.calculate(clearance);near(limited.endClearanceMm,500,1e-7);ok(limited.qEndDeg<164&&limited.limiter==='Target ground clearance','clearance constraint can dominate stop');
near(limited.qEndDeg,180-Math.asin((500-p.params.rw+50)/(2*p.params.L2))*180/Math.PI,1e-8);
const constant=clone(p);constant.params.springLaw='constant';const cf=A.calculate(constant),ref=ctx.Kinefold.reference(constant.params),sp=ctx.KinefoldV4.VSLSpring;
near(cf.springReleasedJ,constant.params.p0*(sp.geometry(ref,cf.qStartDeg).payout-sp.geometry(ref,cf.qEndDeg).payout)/1000);
const wheel=clone(p);wheel.params.m6=20;near(A.calculate(wheel).requiredJointNm,z.requiredJointNm);
const boundary=clone(p);boundary.energyConfig={...P.energyDefaults,compressionReserveDeg:0};ok(A.calculate(boundary).boundaryOnly,'zero reserve is labeled boundary only');near(A.calculate(boundary).qEndDeg,165);
const geared=clone(p);geared.motorConfig={...P.motorDefaults,enabled:true,gearRatio:10,rotorInertiaKgM2:.2,coulombFrictionNm:1,viscousFrictionNms:1,commandBasis:'motor'};const gear=A.calculate(geared);near(gear.requiredJointNm,z.requiredJointNm);near(gear.requiredShaftNm,z.requiredJointNm/10);near(gear.availableShaftNm,2);
geared.motorConfig.coggingAmplitudeNm=.1;geared.motorConfig.coggingPeriodsPerRev=3;geared.motorConfig.coggingPhaseDeg=25;const cog=A.calculate(geared);const U=q=>.1/3*Math.cos((3*10*q+25)*Math.PI/180);near(cog.coggingReleasedJ,U(z.qStartDeg)-U(z.qEndDeg));near((cog.requiredJointNm-z.requiredJointNm)*z.angularTravelRad,cog.coggingReleasedJ);
for(const edit of [q=>q.params.m2=.1,q=>q.params.alpha=5,q=>q.params.g=0,q=>q.params.loadMode='contact',q=>q.caseConfig={...P.caseDefaults,undersideOffsetMm:null},q=>q.energyConfig={...P.energyDefaults,targetClearanceMm:1000},q=>q.energyConfig={...P.energyDefaults,compressionReserveDeg:60}]){const value=clone(p);edit(value);assert.throws(()=>A.calculate(value));checks++;}
const saved=P.validate(realm({...p,energyConfig:{...P.energyDefaults,dropHeightMm:230}}));ok(P.content(saved)!==P.content(p),'energy state marks named design dirty');ok(D.snapshotKey(saved)===D.snapshotKey(p),'energy-only edits do not stale physical results');near(P.decode(clone(saved)).project.energyConfig.dropHeightMm,230);
for(const value of [null,{...P.energyDefaults,dropHeightMm:-1},{...P.energyDefaults,targetClearanceMm:NaN},{...P.energyDefaults,extra:1}]){assert.throws(()=>P.validateEnergy(realm(value)));checks++;}
console.log('PASS '+checks+' standalone energy assertions');
