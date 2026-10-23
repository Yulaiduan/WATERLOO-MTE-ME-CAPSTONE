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
// Independent work reference for above-takeoff jump target, including stance gravity.
const jump=clone(p);jump.params.m6=1.5;const j=A.jumpEstimate(jump,100);near(j.jointNm,8.85912332332764);near(j.stanceRiseMm,435.59322474581217);near(j.angularTravelRad,1.134464013796314);near(A.jumpEstimate(jump,200).jointNm,17.722560045618735);
jump.params.springEnabled=false;near(A.jumpEstimate(jump,100).jointNm,41.821937806867446);jump.motorConfig={...P.motorDefaults,enabled:true,gearRatio:10};near(A.jumpEstimate(jump,100).shaftNm,A.jumpEstimate(jump,100).jointNm/10);
for(const edit of [q=>q.params.alpha=5,q=>q.params.g=0,q=>{q.params.te=70;q.params.tc=110;},q=>q.params.p0=-10000]){const value=clone(p);edit(value);assert.throws(()=>A.jumpEstimate(value,100));checks++;}
const target=clone(p);target.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:250};const targetSaved=P.validate(realm(target));near(P.decode(clone(targetSaved)).project.torqueTargetConfig.jumpHeightMm,250);ok(D.snapshotKey(targetSaved)===D.snapshotKey(p),'target-only edit keeps physical result identity');ok(P.content(targetSaved)!==P.content(p),'targets mark named profile dirty');ok(!('torqueTargetConfig' in P.validate(p)),'legacy targets remain absent');
for(const value of [null,{}, {...P.torqueTargetDefaults,jumpHeightMm:-1},{...P.torqueTargetDefaults,jumpTorqueLimitNm:Infinity}]){assert.throws(()=>P.validateTorqueTargets(realm(value)));checks++;}
// Catalog selections are saved analysis metadata, never physical motor changes.
const twoMetre=clone(p);twoMetre.energyConfig={...P.energyDefaults,dropHeightMm:2000};
near(A.calculate(twoMetre).requiredJointNm,232.3451518866197);
near(A.calculate(twoMetre).workJ,171.66962116213807);
const selection={motorId:'flipsky-80100-130',gearboxId:'eg20',peakShaftNm:17,customRatio:1,customMomentaryNm:null};
const selected=clone(twoMetre);selected.energyConfig.screening=clone(selection);const unmodified=JSON.stringify(selected),screen=A.calculate(selected);
near(screen.gearRatio,20);near(screen.requiredShaftNm,232.3451518866197/20);near(screen.availableJointNm,60);near(screen.screening.idealJointPeakNm,340);
ok(screen.screening.motorPass&&!screen.screening.gearboxPass&&!screen.passes,'motor meeting peak cannot bypass gearbox output cap');
ok(JSON.stringify(selected)===unmodified&&!('motorConfig' in selected),'candidate does not create or mutate the physical motor');
ok(D.snapshotKey(selected)===D.snapshotKey(twoMetre),'catalog edits do not stale physical trajectories');
const roundtrip=P.decode(clone(P.validate(selected))).project;ok(JSON.stringify(roundtrip.energyConfig.screening)===JSON.stringify(selection),'selection roundtrips with saved design');
ok(P.content(roundtrip)!==P.content(twoMetre),'candidate selection marks named design dirty');
for(const [id,N,nominal,limit] of [['eg5',5,28,56],['eg10',10,10,20],['eg20',20,30,60],['eg50',50,25,50]]){const q=clone(selected);q.energyConfig.screening.gearboxId=id;const r=A.calculate(q);near(r.gearRatio,N);near(r.screening.nominalNm,nominal);near(r.screening.momentaryNm,limit);near(r.availableJointNm,Math.min(17*N,limit));ok(!r.passes,'2 m baseline exceeds every listed gearbox momentary limit');}
ok(A.motors.length===9&&A.gearboxes.length===4,'nine motor variants and four deduplicated gearbox models');
ok(JSON.stringify(A.motors.map(m=>m.peakShaftNm))===JSON.stringify([8,9,7,9,8,9.5,5,10,17]),'all nine source peak ratings retained');
near(A.motors.find(m=>m.id==='flipsky-7070-110').peakShaftNm,9.5);ok(A.motors.find(m=>m.id==='flipsky-63100-140').duration.includes('30 s'),'limited peak duration retained');
const direct=clone(selected);direct.energyConfig.screening.gearboxId='direct';const dr=A.calculate(direct);near(dr.gearRatio,1);near(dr.availableJointNm,17);ok(dr.screening.gearboxPass&&!dr.screening.motorPass,'direct drive has no gearbox cap but motor still limits');
const custom=clone(selected);custom.energyConfig.screening=clone({motorId:'custom',gearboxId:'custom',peakShaftNm:20,customRatio:20,customMomentaryNm:null});let customResult=A.calculate(custom);ok(!customResult.passes&&customResult.screening.gearboxPass===null,'unknown gearbox rating cannot pass');
custom.energyConfig.screening.customMomentaryNm=300;customResult=A.calculate(custom);near(customResult.availableJointNm,300);ok(customResult.passes,'explicit adequate custom capacity passes endpoint screen');
custom.energyConfig.screening.peakShaftNm=1;customResult=A.calculate(custom);near(customResult.availableJointNm,20);ok(!customResult.screening.motorPass&&!customResult.passes,'editable peak override controls capacity');
const candidateCog=clone(geared);candidateCog.energyConfig={...P.energyDefaults,screening:clone(selection)};const candidateCogOriginal=JSON.stringify(candidateCog),candidateCogResult=A.calculate(candidateCog),candidateU=q=>.1/3*Math.cos((3*20*q+25)*Math.PI/180);
near(candidateCogResult.coggingReleasedJ,candidateU(z.qStartDeg)-candidateU(z.qEndDeg));near(candidateCog.motorConfig.gearRatio,10);ok(JSON.stringify(candidateCog)===candidateCogOriginal,'candidate cogging recomputation does not mutate physical reduction');
const disabledCog=clone(candidateCog);disabledCog.motorConfig.enabled=false;near(A.calculate(disabledCog).coggingReleasedJ,0);
const physicalGuidance=A.landingEstimate(candidateCog,2000,50),physicalU=q=>.1/3*Math.cos((3*10*q+25)*Math.PI/180);
near(physicalGuidance.gearRatio,10);near(physicalGuidance.requiredJointNm,(171.675+z.gravityCompressionJ+z.springReleasedJ+physicalU(z.qStartDeg)-physicalU(z.qEndDeg))/z.angularTravelRad);near(physicalGuidance.requiredShaftNm,physicalGuidance.requiredJointNm/10);
ok(physicalGuidance.screening===null&&physicalGuidance.config.dropHeightMm===2000,'dynamic-case estimate uses actual motor and requested case height, not candidate');
ok(JSON.stringify(candidateCog)===candidateCogOriginal,'dynamic guidance keeps saved candidate and physical motor intact');
for(const patch of [{motorId:'unknown'},{gearboxId:'unknown'},{peakShaftNm:-1},{customRatio:0},{customMomentaryNm:-1},{extra:true}]){const bad=clone(selected);Object.assign(bad.energyConfig.screening,clone(patch));assert.throws(()=>P.validate(bad));checks++;}
console.log('PASS '+checks+' standalone energy assertions');
