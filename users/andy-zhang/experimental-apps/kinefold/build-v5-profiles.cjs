/** Build two full-travel-fitted V5 gravity-compensation member-app designs.
 * Run node build-v5-profiles.cjs [--refit] from any cwd. Inputs retained V4.5
 * geometry/masses in mm/deg/kg/N; fixed k/p0/nu/rs and stated geometry freedoms.
 * Outputs two project-v3 JSON files and compact mass/tuning evidence in existing
 * saved-configurations. --refit repeats the sampled minimax geometry fitting.
 * The135-degree initial pose retains its actual fit residual; zero initial speed,
 * motor torque and damping do not conceal imperfect compensation or its drift.
 * A full-travel fit is not terrain height regulation; rejected restoring trials are
 * evidence only. No live library/network writes or new dynamic capability claim.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
function context(){const c=vm.createContext({});for(const file of ['reference-v4.js','model.js','variables.js','project-store.js','suspension-fit.js','energy-analysis.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,file),'utf8'),c,{filename:file});return c;}
const frozen={0:{hornR:66.46229020513717,Sv:103.67851472091354},20:{hornR:64.01702612917234,Sv:91.6516837588036,Su:45.479599863518544}};
const neutral={0:{hornR:66.46229020513717,Sv:103.67851472091354},20:{hornR:64.01702612917234,Sv:91.6516837588036,Su:45.479599863518544}};
const settings={samples:241,iterations:800,starts:6,verification:6501};
const restoringCandidates=[
 {id:'geom-k0102',hornR:71.7443799849134,Su:50,Sv:130},
 {id:'geom-k0150',hornR:76.4497995392885,Su:50,Sv:150},
 {id:'geom-k0249',hornR:89.64885309734382,Su:80,Sv:280},
 {id:'geom-k0398',hornR:109.30893920990638,Su:40,Sv:280},
 {id:'geom-k0598',hornR:130.60783566138707,Su:10,Sv:240},
 {id:'geom-k0818',hornR:144.1907328197267,Su:0,Sv:190},
 {id:'geom-k1218',hornR:188.65374813019298,Su:-10,Sv:290},
 {id:'geom-k1173',hornR:188.01422964478843,Su:-10,Sv:300}
];
const positiveAssistTrials=[
 {id:'positive-0',hornR:70.40564411482774,Su:40,Sv:110},
 {id:'positive-1',hornR:73.1363567376975,Su:80,Sv:180},
 {id:'positive-3',hornR:87.77875445480458,Su:90,Sv:290}
];
const clone=v=>JSON.parse(JSON.stringify(v));
function realm(c,value){c.raw=JSON.stringify(value);return vm.runInContext('JSON.parse(raw)',c);}
function statistics(c,p,count=6501){
 const M=c.Kinefold,V=c.KinefoldV4,r=M.reference(p);let maxTorqueNm=0,peakThetaDeg=p.te,sum=0,maxForceErrorN=0,sumForce=0,minForceN=Infinity,maxForceN=-Infinity,minRequiredN=Infinity,maxRequiredN=-Infinity;
 for(let i=0;i<count;i++){
  const q=p.te+(p.tc-p.te)*i/(count-1),s=V.VSLStatic.solve(r,q,false);
  if(!s.valid||!Number.isFinite(s.tau2)||!Number.isFinite(s.spring.Jz)||Math.abs(s.spring.Jz)<1e-8)throw Error('Non-finite or singular V5 static pose.');
  const forceErrorN=s.tau2/(s.spring.Jz/1000),requiredN=s.tauG/(s.spring.Jz/1000);
  if(Math.abs(s.tau2)>maxTorqueNm){maxTorqueNm=Math.abs(s.tau2);peakThetaDeg=q;}
  sum+=s.tau2*s.tau2;sumForce+=forceErrorN*forceErrorN;maxForceErrorN=Math.max(maxForceErrorN,Math.abs(forceErrorN));
  minForceN=Math.min(minForceN,s.spring.Feq);maxForceN=Math.max(maxForceN,s.spring.Feq);minRequiredN=Math.min(minRequiredN,requiredN);maxRequiredN=Math.max(maxRequiredN,requiredN);
 }
 return {samples:count,maxTorqueNm,peakThetaDeg,rmsTorqueNm:Math.sqrt(sum/count),maxEquivalentForceErrorN:maxForceErrorN,rmsEquivalentForceErrorN:Math.sqrt(sumForce/count),springEquivalentLiftN:[minForceN,maxForceN],requiredEquivalentLiftN:[minRequiredN,maxRequiredN]};
}
function passiveStatistics(c,p,{count=6501,curve=false}={}){
 const V=c.KinefoldV4,r=c.Kinefold.reference(p),q0=135,R=Math.PI/180,e=.001;
 const potential=q=>{const s=V.VSL.state(r,q),h=p.rw-s.Pg[1];return p.g/1000*(p.m1*h+p.m2*(h+s.Bg[1]/2)+p.m3*(h+(s.Bg[1]+s.Pg[1])/2)+p.m5*(h+s.Bg[1])+p.m6*p.rw)+V.VSLSpring.state(r,q).energy;};
 const at=V.VSLStatic.solve(r,q0,false),slope=(V.VSLStatic.solve(r,q0+e,false).tau2-V.VSLStatic.solve(r,q0-e,false).tau2)/(2*e*R),U0=potential(q0),er=.0005;
 let restoring=true,minPotential=Infinity,maxForce=0,minForce=Infinity,minLift=Infinity,maxLift=-Infinity;const rows=[];
 for(let i=0;i<count;i++){const q=p.te+(p.tc-p.te)*i/(count-1),s=V.VSLStatic.solve(r,q,false),d=potential(q)-U0;if(Math.abs(q-q0)>1e-6&&s.tau2*(q-q0)<=0)restoring=false;minPotential=Math.min(minPotential,d);minForce=Math.min(minForce,s.spring.force);maxForce=Math.max(maxForce,s.spring.force);minLift=Math.min(minLift,s.spring.Feq);maxLift=Math.max(maxLift,s.spring.Feq);if(curve)rows.push({thetaDeg:q,hipHeightMm:p.rw-s.Pg[1],holdingTorqueNm:s.tau2,springEquivalentLiftN:s.spring.Feq,gravityEquivalentLiftN:s.tauG/(s.spring.Jz/1000),netPotentialDeltaJ:d});}
 return {rideThetaDeg:q0,rideHoldingTorqueNm:at.tau2,netPotentialCurvatureNmPerRad:slope,independentPotentialCurvatureNmPerRad:(potential(q0+er/R)-2*U0+potential(q0-er/R))/(er*er),rideTangentStiffnessNPerM:slope/(at.spring.Jz/1000)**2,restoringAllSampledTravel:restoring,minNetPotentialDeltaJ:minPotential,cableForceN:[minForce,maxForce],equivalentLiftN:[minLift,maxLift],samples:count,...(curve?{curve:rows}:{})};
}
function input(c,alpha){
 const P=c.KinefoldProjects,p=P.v45();p.id='design-v5-alpha'+alpha+'-4to1';p.name='V5 · α '+alpha+'° · 4:1 free wheel · fitted g-comp';
 p.params={...p.params,alpha,te:95,tc:175,theta2:135,rc:25,rd:50,re:25,rf:50,loadMode:'weight'};
 p.solverConfig={...p.solverConfig,duration:3,dt:.000125,outputHz:50,inputRiseMm:0,hipTorqueNm:0,dampingNms:0,initialVelocityDegS:0};
 p.contactConfig={...P.contactDefaults,mode:'terrain-contact'};
 p.caseConfig={...P.caseDefaults,kind:'terrain-stability',jumpTorqueNm:250,landingDropMm:2000,landingBrakeTorqueNm:300,landingBrakeLimitNm:500,brakeStrategy:'entered',undersideOffsetMm:50};
 p.energyConfig={...P.energyDefaults,dropHeightMm:2000,targetClearanceMm:50,torqueLimitNm:300,compressionReserveDeg:1};
 p.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:2000,landingClearanceMm:50,jumpTorqueLimitNm:500};
 p.motorConfig={...P.motorDefaults};p.createdAt=p.updatedAt='2026-11-01T00:00:00.000Z';return p;
}
function build({refit=false}={}){
 const c=context(),P=c.KinefoldProjects,A=c.KinefoldSuspensionFit,profiles=[],fits=[];
 for(const alpha of [0,20]){
  const original=input(c,alpha),free=alpha===0?['hornR','Sv']:['hornR','Sv','Su'],locks=Object.fromEntries(A.keys.map(k=>[k,!free.includes(k)]));
  const seed=alpha===0?{...original.params}:{...original.params,hornR:66,Sv:103,Su:46};let values={...frozen[alpha]};
  if(refit){const fit=A.solve(seed,locks,settings);if(!fit.valid)throw Error(fit.reason);values=Object.fromEntries(free.map(k=>[k,fit.params[k]]));}
  const p={...original,params:{...original.params,...values}},validated=P.validate(realm(c,p)),r=c.Kinefold.reference(p.params),masses=Object.fromEntries(['m1','m2','m3','m5','m6'].map(k=>[k,p.params[k]]));profiles.push(clone(validated));
  const source=vm.runInContext('VSLFit',c),bounds=source.boundsFor(alpha===0?c.Kinefold.reference(seed):seed);
  fits.push({alphaDeg:alpha,profileId:p.id,file:'v5-alpha'+alpha+'-4to1.json',free,locks,settings,bounds,fitInputParams:seed,baselineParams:original.params,params:p.params,before:statistics(c,original.params),after:statistics(c,p.params),initialState:{thetaDeg:135,velocityDegS:0,appliedHipTorqueNm:0,dampingNms:0,postFitRideCalibrationApplied:false,holdingResidualNm:c.KinefoldV4.VSLStatic.solve(r,135,false).tau2,predictedInitialDrift:'Increasing hip angle / leg compression / chassis down, from the negative unbalanced holding torque; initial velocity remains zero.'},passiveSupport:passiveStatistics(c,p.params),curve:passiveStatistics(c,p.params,{count:81,curve:true}).curve,massBasis:{massesKg:masses,totalMassKg:Object.values(masses).reduce((a,b)=>a+b,0),gravityMS2:p.params.g,automaticGroundReactionN:{x:-r.Fy,z:r.Fz},loadMode:p.params.loadMode,wheelTreatment:'With fixed world wheel height and zero contact moment, wheel gravity has zero stance work. Its weight remains in the ground reaction and in dynamic wheel mass/inertia. Moving link/compound gravity is included at each actual COM; alpha changes its world-height work.'},method:'Bounded sampled minimax static holding-torque fit over the full95..175deg working range, with no post-fit ride-pose root. The initial135deg residual is retained, so zero-input drift is expected. Not a guaranteed global optimum, height controller or terrain stability guarantee.',springConvention:c.Kinefold.springConvention});
 }
 const base20=input(c,20).params,trialSummary=({id,...parameters})=>({id,parameters,...passiveStatistics(c,{...base20,...parameters},{count:81})});
 return {profiles,evidence:{schema:'kinefold/v5-fit-evidence-v1',date:'2026-11-01',sourceBase:'a75e19582f11a163ff4026e176989ae10313b221',operatingAngleDeg:[95,175],operatingTravelDeg:80,idealFullTravelDeg:90,driveStages:{hipToKnee:{driverMm:25,drivenMm:50,reduction:2},kneeToWheel:{driverMm:25,drivenMm:50,reduction:2},overallHeldLegReduction:4,driveBoundary:'Freely backdrivable massless/unforced input in actual contact; prescribed-height bench holds the drive input and retains its coupled inertia.'},fixedSpring:{springK:8,p0:330.8692828089511,rs:10,nu:0},alpha20SuPermission:'Owner approved Su geometry adjustment, while explicitly retaining the spring rate and reference preload.',minimaxReferences:[0,20].map(alpha=>({alphaDeg:alpha,parameters:neutral[alpha],holding:statistics(c,{...input(c,alpha).params,...neutral[alpha]}),passive:passiveStatistics(c,{...input(c,alpha).params,...neutral[alpha]})})),alpha20RejectedTwoVariableCandidate:{hornR:164.14980167094618,Sv:59.3727038447344,Su:9.387776728149294,peakResidualNm:9.212657177971249,rmsResidualNm:6.585304158337688,maxEquivalentForceErrorN:76.67373428870155,search:'Bounded coarse horn1..301mm/Sv−300..900mm plus targeted refinement and local multistart; not an infeasibility proof.'},rejectedRestoringStudy:{bounds:{hornR:[2,302],Su:[-80,180],Sv:[10,300]},evaluationsPerScreen:40752,balanceRoots:474,initialCandidates:restoringCandidates.map(trialSummary),upwardAssistCandidates:positiveAssistTrials.map(trialSummary),promoted:false,rejection:'Strong K1173 tune gave downward equivalent assist near extension and both prescribed-height runs reached travel limits near1.98s. Of three upward-assist candidates, two ran the prescribed bench but none avoided terrain endstops. No restoring trial is saved as a final design. Exact final benchmark outcomes belong to the separate paired-engine report.'},fits,limits:'Supported-stance gravity compensation only. Both saved designs retain their actual nonzero135deg fit residual, zero initial velocity and upward spring-equivalent assist. No post-fit ride balancing is applied; initial downward drift is expected. Near-neutral support is not passive world-height regulation. Geometry-only trials did not solve the150mm terrain case without other failures; no hidden motor bias, damping or changes to k/preload are used. At alpha20 finite-link COM gravity makes the equivalent support target pose-dependent. Working stops are inset from the singular ideal90-degree endpoint. The app bench uses a stationary flat input; actual contact uses zero prescribed transition. Entered250/300Nm commands are illustrative ideal joint torques, not certified actuator capability. Actual outcomes, impact losses, packaging and strength require separate validation.'}};
}
if(require.main===module){const result=build({refit:process.argv.includes('--refit')}),folder=path.join(__dirname,'saved-configurations');for(const p of result.profiles)fs.writeFileSync(path.join(folder,'v5-alpha'+p.params.alpha+'-4to1.json'),JSON.stringify(p,null,2)+'\n');fs.writeFileSync(path.join(folder,'v5-fit-evidence.json'),JSON.stringify(result.evidence,null,2)+'\n');console.log(JSON.stringify(result.evidence.fits.map(f=>({alpha:f.alphaDeg,values:Object.fromEntries(f.free.map(k=>[k,f.params[k]])),after:f.after,passive:f.passiveSupport}))));}
module.exports={build,context,statistics,passiveStatistics,frozen,neutral,restoringCandidates,settings};
