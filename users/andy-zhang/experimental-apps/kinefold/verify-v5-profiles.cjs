/** Audit V5 suspension mass accounting, drivetrain and portable profiles.
 * Run node verify-v5-profiles.cjs from any cwd. Temporary mm/deg/kg/N fixtures
 * produce assertion counts; no network, live profiles or generated files change.
 * Independent world-COM potential differences check static work; actual terrain,
 * jump, landing, impacts and numerical convergence require engine scenario tests.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {build,context,statistics,passiveStatistics}=require('./build-v5-profiles.cjs');
const c=context(),M=c.Kinefold,V=c.KinefoldV4,P=c.KinefoldProjects,A=c.KinefoldSuspensionFit,R=Math.PI/180;
const clone=v=>JSON.parse(JSON.stringify(v));
const realm=v=>{c.raw=JSON.stringify(v);return vm.runInContext('JSON.parse(raw)',c);};
let checks=0;const ok=(v,label)=>{assert.ok(v,label);checks++;},near=(a,b,label,t=1e-7)=>ok(Math.abs(a-b)<=t,`${label}: ${a} vs ${b}`);
function potential(p,q){
 const s=V.VSL.state(M.reference(p),q),h=p.rw-s.Pg[1];
 return p.g/1000*(p.m1*h+p.m2*(h+s.Bg[1]/2)+p.m3*(h+(s.Bg[1]+s.Pg[1])/2)+p.m5*(h+s.Bg[1])+p.m6*p.rw);
}
const result=build(),files=['v5-alpha0-4to1.json','v5-alpha20-4to1.json'];
let maxWorkErrorNm=0,maxWheelTorqueDifferenceNm=0;
for(let j=0;j<2;j++){
 const profile=result.profiles[j],disk=JSON.parse(fs.readFileSync(path.join(__dirname,'saved-configurations',files[j]),'utf8')),p=profile.params,baseline=P.v45().params;
 assert.deepEqual(profile,disk);checks++;P.decode(realm(profile));checks++;
 ok(M.validate(p).length===0,'V5 geometry/spring valid');near(p.tc-p.te,80,'operating span');near(p.te,95,'extension inset');near(p.tc,175,'compression inset');
 near(p.ra/p.rb,2,'AB leg coupling');near(p.rd/p.rc,2,'hip to knee reduction');near(p.rf/p.re,2,'knee to wheel reduction');near((p.rd/p.rc)*(p.rf/p.re),4,'held-leg overall wheel reduction');near(V.VSL.coefficient(M.reference(p)),-.25,'moving carrier hip coupling');
 for(const key of ['springK','p0','rs','nu'])near(p[key],baseline[key],key+' remains locked',0);
 if(p.alpha===0)near(p.Su,baseline.Su,'alpha0 Su locked',0);
 ok(profile.contactConfig.mode==='terrain-contact'&&profile.contactConfig.drive==='free','actual freely backdrivable wheel contact');near(profile.solverConfig.inputRiseMm,0,'contact transition');near(profile.solverConfig.dt,.000125,'contact timestep');
 near(profile.params.m1,8.75,'chassis corner mass');near(p.m2,1,'upper mass');near(p.m3,1,'lower mass');near(p.m6,.5,'wheel mass');near(profile.torqueTargetConfig.jumpHeightMm,2000,'jump target');near(profile.caseConfig.landingDropMm,2000,'drop target');
 const projection=M.evaluate(p);near(projection.S[0],-p.Su,'fixed chassis spring x');near(projection.S[2],p.Sv,'fixed chassis spring z');
 const r=M.reference(p),report=A.massBasis(p);near(report.totalMassKg,11.25,'all masses included');near(report.totalWeightN,110.3625,'total weight');near(report.resolvedWheelForceN.z,110.3625,'automatic support reaction');ok(report.automaticWeightReference,'weight reference is explicit');
 const locked=Object.fromEntries(A.keys.map(k=>[k,true])),fit=A.solve(p,locked,{samples:31,verification:401});ok(fit.valid,'all-locked fit valid');
 const stats=statistics(c,p,401);near(fit.after.maxTorqueNm,stats.maxTorqueNm,'reported dense peak');near(fit.after.rmsTorqueNm,stats.rmsTorqueNm,'reported RMS torque');near(fit.after.maxEquivalentResidualForceN,stats.maxEquivalentForceErrorN,'reported equivalent-force peak');near(fit.after.rmsEquivalentResidualForceN,stats.rmsEquivalentForceErrorN,'reported equivalent-force RMS');
 for(const key of ['m1','m2','m3','m5','m6'])near(fit.massBasis.massesKg[key],p[key],'fit captures '+key,0);
 for(const m2 of [.4,1])for(const m3 of [.6,1])for(const m5 of [0,.2])for(const m6 of [.2,.5,1.5])for(const q of [95,115,135,155,175]){
  const z={...p,m2,m3,m5,m6},eps=1e-4,reference=M.reference(z),s=V.VSLUnassisted.solve(reference,q,false),fd=(potential(z,q+eps)-potential(z,q-eps))/(2*eps*R),error=Math.abs(s.tau2-fd);
  maxWorkErrorNm=Math.max(maxWorkErrorNm,error);near(s.tau2,fd,'independent all-body stance work',2e-7);
  const heavy={...z,m6:m6+1},other=V.VSLUnassisted.solve(M.reference(heavy),q,false);maxWheelTorqueDifferenceNm=Math.max(maxWheelTorqueDifferenceNm,Math.abs(other.tau2-s.tau2));near(other.tau2,s.tau2,'grounded wheel gravity torque cancellation',1e-10);near(M.reference(heavy).Fz-reference.Fz,z.g,'wheel mass remains in reaction',1e-10);
 }
 for(const key of ['m1','m2','m3','m5']){const changed={...p,[key]:p[key]+1},q=135;ok(Math.abs(V.VSLUnassisted.solve(M.reference(changed),q,false).tau2-V.VSLUnassisted.solve(r,q,false).tau2)>.01,key+' gravity affects hip demand');}
 const unchanged=JSON.stringify(p),global={...p,loadMode:'global',Fx:0,Fz:120};const globalBasis=A.massBasis(global);near(globalBasis.resolvedWheelForceN.z,120,'prescribed global force retained',0);ok(!globalBasis.automaticWeightReference,'prescribed load is not relabelled as automatic weight');near(A.massBasis({...global,m6:2}).resolvedWheelForceN.z,120,'prescribed load not silently scaled',0);ok(JSON.stringify(p)===unchanged,'audit pure');
 const passive=passiveStatistics(c,p);ok(profile.name.includes('calibrated g-comp'),'profile label states ride calibration');near(passive.rideHoldingTorqueNm,0,'exact135ride balance',1e-6);near(passive.netPotentialCurvatureNmPerRad,passive.independentPotentialCurvatureNmPerRad,'independent net-potential curvature',.001);ok(passive.equivalentLiftN[0]>0,'upward assist throughout6501workingposes');
 ok(result.evidence.fits[j].after.maxTorqueNm<.15,'calibrated fullstroke gravity residual below0.15Nm');ok(result.evidence.fits[j].after.maxEquivalentForceErrorN<2,'calibrated equivalent force error below2N');
 ok(Math.abs(passive.rideTangentStiffnessNPerM)<2,'near-neutral compensation is not reported as strong restoring support');
}
near(result.evidence.fits[0].after.requiredEquivalentLiftN[0],95.6475,'alpha0 effective gravity support');ok(result.evidence.fits[1].after.requiredEquivalentLiftN[1]-result.evidence.fits[1].after.requiredEquivalentLiftN[0]>20,'tilted finite-link COM makes target support pose-dependent');
const refitted=build({refit:true});for(let j=0;j<2;j++){assert.deepEqual(refitted.profiles[j],result.profiles[j]);checks++;near(refitted.evidence.fits[j].passiveSupport.rideHoldingTorqueNm,0,'refit repeats horn-only ride calibration',1e-6);}ok(result.evidence.rejectedRestoringStudy.promoted===false,'failed restoring trials are not promoted as final designs');
console.log(JSON.stringify({status:'PASS',checks,maxIndependentWorkErrorNm:maxWorkErrorNm,maxWheelTorqueDifferenceNm,profiles:files}));
