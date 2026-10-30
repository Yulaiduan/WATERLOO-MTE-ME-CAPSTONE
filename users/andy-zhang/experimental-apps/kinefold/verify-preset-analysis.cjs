/** Independent formulas, negative controls, contours and immutable batch checks.
 * Run node verify-preset-analysis.cjs from the app directory; optionally point
 * KINEFOLD_PRESET_STORE at a development preset-store.js dependency. Inputs use
 * mm/deg/kg/N and SI motor quantities; outputs assertions, not hardware evidence.
 * Fake batch jobs verify orchestration only; actual engines are checked separately.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({});for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','energy-analysis.js',process.env.KINEFOLD_PRESET_STORE||'preset-store.js','preset-analysis.js'])vm.runInContext(fs.readFileSync(path.isAbsolute(f)?f:path.join(__dirname,f),'utf8'),ctx);
const P=ctx.KinefoldProjects,S=ctx.KinefoldPresets,A=ctx.KinefoldPresetAnalysis,R=Math.PI/180;
const realm=v=>{ctx.raw=JSON.stringify(v);return vm.runInContext('JSON.parse(raw)',ctx);},plain=v=>JSON.parse(JSON.stringify(v));let checks=0;
const ok=(v,m)=>{assert.ok(v,m);checks++;},near=(a,b,t=1e-9)=>ok(Math.abs(a-b)<=t,`${a} versus ${b}`),throws=(f,m)=>{assert.throws(f,m);checks++;};
const sweep=realm({maxJointSpeedRadS:2,jointAccelerationRadS2:3,samples:11});
function fixture(edit=()=>{}){let p=P.baseline();edit(p);p=realm(p);const s=S.make('suspension','Suspension',S.captureSuspension(p)),i=S.make('input','Input',S.captureInput(p)),a=S.make('actuator','Motor',S.captureActuator(p));return {project:S.compose(p,s,a,i),actuator:a,suspension:s,input:i};}
const base=fixture(),original=JSON.stringify(base),b=A.analyze(base.project,base.actuator,sweep);
ok(b.rows.length===121&&b.staticRows.length===11,'real sampled 11 by 11 grid');near(b.inertia.rotorReflectedJointKgM2,0);near(b.inertia.legJointKgM2.max,0);ok(b.ratings.maxShaftRpm.status==='unassessed','unknown rpm remains unassessed');ok(b.energy.landing.available&&b.energy.jump.available,'supported original energy APIs');near(b.energy.landing.result.requiredJointNm,11.6103416382814);ok(JSON.stringify(base)===original,'analysis is immutable');ok(JSON.stringify(b)!==undefined,'JSON-compatible output');
const rich=fixture(p=>{Object.assign(p.params,{m2:1.3,m3:.8,m5:.4,m6:2,L3:250,ra:48,rb:20,rc:30,rd:40,re:18,rf:30,springEnabled:false,loadMode:'global',Fx:0,Fz:0});Object.assign(p.solverConfig,{inputRiseMm:10,hipRotorInertiaKgM2:.07,dampingNms:.09});p.motorConfig={...P.motorDefaults,enabled:true,gearRatio:7,rotorInertiaKgM2:.003,coggingAmplitudeNm:.12,coggingPeriodsPerRev:3,coggingPhaseDeg:28,coulombFrictionNm:.08,viscousFrictionNms:.014,frictionVelocityScaleRadS:.05};});
const rr=A.analyze(rich.project,rich.actuator,sweep),p=rich.project.params,c=rich.project.solverConfig,N=7;
// Independent COM position finite differences, not the implementation's analytic
// Jacobians. Angular rates are differentiated from the original angle equations.
const poses=q=>{const k=1-p.ra/p.rb,b=p.phi0*R+(Math.PI-q)*(p.ra/p.rb-1),B=[-p.L2/1000*Math.cos(q),-p.L2/1000*Math.sin(q)],C=[B[0]-p.L3/1000*Math.cos(b),B[1]-p.L3/1000*Math.sin(b)];return {2:B.map(v=>v/2),3:B.map((v,i)=>(v+C[i])/2),5:B,6:C};};
const angular=q=>({2:q,3:p.phi0*R+(Math.PI-q)*(p.ra/p.rb-1),5:(1-p.rc/p.rd)*(q-p.te*R),6:(1-p.ra/p.rb+(p.ra/p.rb-p.rc/p.rd)*p.re/p.rf)*(q-p.te*R)});
const q=rr.staticRows[5].thetaDeg*R,eps=1e-5,sitesLo=poses(q-eps),sitesHi=poses(q+eps),anglesLo=angular(q-eps),anglesHi=angular(q+eps),I={2:p.m2*(p.L2/1000)**2/12,3:p.m3*(p.L3/1000)**2/12,5:.5*p.m5*(Math.max(p.rd,p.re)/1000)**2,6:.5*p.m6*(p.rw/1000)**2};
let independentJ=c.hipRotorInertiaKgM2,gravityNm=0,wrongNoAngular=0;
for(const key of ['2','3','5','6']){const v=sitesHi[key].map((x,i)=>(x-sitesLo[key][i])/(2*eps)),w=(anglesHi[key]-anglesLo[key])/(2*eps);independentJ+=p['m'+key]*(v[0]**2+v[1]**2)+I[key]*w*w;wrongNoAngular+=p['m'+key]*(v[0]**2+v[1]**2)+I[key];gravityNm+=p.g*p['m'+key]*v[1];}
near(rr.staticRows[5].legInertiaKgM2,independentJ,1e-10);near(rr.staticRows[5].staticJointNm,gravityNm,1e-8);ok(Math.abs(independentJ-c.hipRotorInertiaKgM2-wrongNoAngular)>1e-5,'angular-rate squared negative control detects wrong inertia');
const J=q=>A.fixedHipInertia(p,c,q/R).legInertiaKgM2;near(rr.staticRows[5].legInertiaDerivativeKgM2PerRad,(J(q+eps)-J(q-eps))/(2*eps),1e-10);
near(rr.inertia.rotorReflectedJointKgM2,49*.003);near(rr.inertia.legMotorEquivalentKgM2.max,rr.inertia.legJointKgM2.max/49);near(rr.inertia.viscousJointNms,49*.014);ok(!rr.energy.landing.available&&/massless/.test(rr.energy.landing.reason),'unsupported moving masses energy is unavailable, not zero');
const sample=rr.rows.find(r=>r.thetaDeg===rr.staticRows[5].thetaDeg&&r.jointSpeedRadS===2),m=rich.project.motorConfig,phase=3*N*q+28*R;
near(sample.shaftSpeedRadS,14);near(sample.rotorAccelerationNm,49*.003*3);near(sample.legAccelerationNm,independentJ*3,1e-9);near(sample.coulombJointNm,N*.08);near(sample.viscousJointNm,49*.014*2);near(sample.legacyDampingNm,.18);near(sample.coriolisNm,.5*sample.legInertiaDerivativeKgM2PerRad*4);
const U=x=>.12/3*Math.cos(3*N*x+28*R);near(sample.coggingJointNm,-(U(q+eps)-U(q-eps))/(2*eps),1e-8);
const independentTorque=gravityNm+independentJ*3+49*.003*3+.5*sample.legInertiaDerivativeKgM2PerRad*4-N*.12*Math.sin(phase)+N*.08+49*.014*2+.18;
near(sample.jointTorqueNm,independentTorque,1e-8);near(sample.shaftTorqueNm,independentTorque/N,1e-8);near(sample.conservativeMaxJointNm-sample.conservativeMinJointNm,2*N*.12);ok(Math.abs(sample.jointTorqueNm-(independentTorque+2*sample.coggingJointNm))>.01,'cogging compensation sign negative control');
const independentOutput=gravityNm+independentJ*3+.5*sample.legInertiaDerivativeKgM2PerRad*4+.18;near(sample.gearboxOutputTorqueNm,independentOutput,1e-8);ok(Math.abs(sample.gearboxOutputTorqueNm-sample.jointTorqueNm)>.1,'motor EM equivalent is not gearbox output');near(rr.ratings.gearboxPeakNm.required,rr.ranges.gearboxOutputTorqueNm.maxAbs);near(rr.charts.static[1].y[5],rr.staticRows[5].jointTorqueNm/N);
const reverse=rr.rows.find(r=>r.thetaDeg===sample.thetaDeg&&r.jointSpeedRadS===-2);near(reverse.coulombJointNm,-sample.coulombJointNm);near(reverse.viscousJointNm,-sample.viscousJointNm);near(reverse.coriolisNm,sample.coriolisNm);near(reverse.coggingJointNm,sample.coggingJointNm);
const gearProject=realm(rich.project);gearProject.motorConfig.gearboxInputInertiaKgM2=.0004;
const gearActuator=realm(rich.actuator);gearActuator.values.motorConfig.gearboxInputInertiaKgM2=.0004;
const gearAnalysis=A.analyze(gearProject,gearActuator,sweep),gearPoint=gearAnalysis.rows.find(r=>r.thetaDeg===sample.thetaDeg&&r.jointSpeedRadS===2);
near(gearPoint.rotorAccelerationNm-sample.rotorAccelerationNm,49*.0004*3);
near(gearPoint.jointTorqueNm-sample.jointTorqueNm,49*.0004*3);
near(gearPoint.gearboxOutputTorqueNm,sample.gearboxOutputTorqueNm);
near(gearAnalysis.inertia.gearboxReflectedJointKgM2,49*.0004);
const custom=fixture(p=>{p.params.m2=1;p.solverConfig.inertiaModel='custom';p.solverConfig.I2=.21;p.solverConfig.I3=.13;p.solverConfig.I5=.07;p.solverConfig.I6=.04;Object.assign(p.params,{ra:48,rb:20,rc:30,rd:40,re:18,rf:30});p.solverConfig.hipRotorInertiaKgM2=.09;});
const cj=A.fixedHipInertia(custom.project.params,custom.project.solverConfig,130),k3=1-48/20,k5=1-30/40,K=1-48/20+(48/20-30/40)*18/30;
near(cj.legInertiaKgM2,.25*(custom.project.params.L2/1000)**2+.21+.13*k3*k3+.07*k5*k5+.04*K*K+.09);
const unknown=realm(rich.actuator);unknown.values.unknownFields=['rotorInertiaKgM2'];unknown.values.motorConfig.rotorInertiaKgM2=0;throws(()=>A.analyze(rich.project,unknown,sweep),/unassessed/);unknown.values.idealizeUnknowns=true;const ideal=realm(rich.project);ideal.motorConfig.rotorInertiaKgM2=0;ok(A.analyze(ideal,unknown,sweep).assumptions.some(s=>s.includes('Explicit idealization')),'explicit idealization recorded');
const mismatch=realm(rich.project);mismatch.motorConfig.gearRatio=8;throws(()=>A.analyze(mismatch,rich.actuator,sweep),/does not match/);for(const v of [{...plain(sweep),samples:12},{...plain(sweep),maxJointSpeedRadS:0},{...plain(sweep),jointAccelerationRadS2:null},{...plain(sweep),extra:1}])throws(()=>A.validateSweep(realm(v)));
// Scalar plane z=x+2y provides independent contour equations and exact total area.
const grid=realm({x:[0,.5,1],y:[0,.5,1],z:[[0,.5,1],[1,1.5,2],[2,2.5,3]]}),contours=A.contourTraces(grid,realm({levels:[0,1,2,3]}));
ok(contours.every(t=>t.type==='scatter'),'BASIC scatter only');let area=0,segments=0;
for(const t of contours){if(t.fill==='toself'){let polygon=[];for(let i=0;i<t.x.length;i++){if(t.x[i]===null){let a=0;for(let j=0;j<polygon.length-1;j++)a+=polygon[j][0]*polygon[j+1][1]-polygon[j+1][0]*polygon[j][1];area+=Math.abs(a)/2;polygon=[];}else polygon.push([t.x[i],t.y[i]]);}}else{const level=Number(t.name.split(' ')[0]);for(let i=0;i<t.x.length;i++)if(t.x[i]!==null){near(t.x[i]+2*t.y[i],level,1e-12);segments++;}}}
near(area,1,1e-12);ok(segments>4,'actual computed isolines');throws(()=>A.contourTraces(realm({x:[0,1],y:[0,1],z:[[null,0],[1,2]]})),/finite/);
const constant=A.contourTraces(realm({x:[0,1],y:[0,1],z:[[2,2],[2,2]]}));ok(constant.length===1&&constant[0].fill==='toself','constant grid honest single band');
const actual=realm({engine:'analytical',rows:[{t:0,shaftCommandNm:-3,jointElectromagneticNm:-21,motorVelocityRadS:14,energyJ:11},{t:.2,shaftCommandNm:2,jointElectromagneticNm:14,motorVelocityRadS:-7,energyJ:9}],diagnostics:{termination:'test'},caseMetrics:{outcome:{classification:'test'}}});
const summary=A.summarizeRun(actual,rich.project,rich.actuator);near(summary.ranges.shaftTorqueNm.min,-3);near(summary.ranges.jointTorqueNm.max,14);near(summary.ranges.shaftSpeedRadS.max,14);near(summary.ranges.energyJ.min,9);ok(summary.ranges.rotorKineticJ.count===0&&summary.ranges.rotorKineticJ.min===null,'absent row values remain unavailable');
const noSpeed=A.summarizeRun(realm({rows:[{t:0,energyJ:0}]}),rich.project,rich.actuator);ok(noSpeed.ranges.shaftRpm.min===null&&noSpeed.ranges.shaftTorqueNm.min===null,'missing speed/torque cannot become zero');const fromJoint=A.summarizeRun(realm({rows:[{t:0,velocityDegS:180,jointElectromagneticNm:7}]}),rich.project,rich.actuator);near(fromJoint.ranges.shaftSpeedRadS.min,7*Math.PI);near(fromJoint.ranges.shaftTorqueNm.min,1);
throws(()=>A.summarizeRun(realm({rows:[]}),rich.project,rich.actuator),/no actual/);
ok(summary.ratings.gearboxPeakNm.status==='unassessed'&&summary.ranges.gearboxOutputTorqueNm.min===null,'actual gearbox output cannot substitute EM command without acceleration');
const smooth=A.summarizeRun(realm({rows:[{jointElectromagneticNm:21,shaftCommandNm:3,motorVelocityRadS:14,accelerationDegS2:180,jointCoggingNm:.4,jointFrictionNm:-.3}]}),rich.project,rich.actuator);near(smooth.ranges.gearboxOutputTorqueNm.min,21+.4-.3-49*.003*Math.PI);
const contact=A.summarizeRun(realm({scope:{mode:'terrain-contact'},rows:[{jointElectromagneticNm:21,shaftCommandNm:3,motorVelocityRadS:14,accelerationDegS2:180,jointCoggingNm:.4,jointFrictionNm:-.3}]}),rich.project,rich.actuator);ok(contact.ranges.gearboxOutputTorqueNm.min===null,'contact/impulsive output remains unassessed even if a row reports acceleration');
const jump=A.summarizeRun(realm({rows:[{velocityDegS:180,jointElectromagneticNm:7}],events:[{type:'exact-square-jump',theta2JumpDeg:4}]}),rich.project,rich.actuator);ok(jump.ratings.maxShaftRpm.status==='unassessed'&&jump.warnings.some(s=>s.includes('instantaneous')),'ideal pose jumps have no finite peak speed');
(async()=>{
  const candidates=realm([rich,base]),before=JSON.stringify(candidates),calls=[],progress=[];let active=0,maxActive=0;
  const result=await A.batch(candidates,['analytical','pymunk'],async(project,engine)=>{active++;maxActive=Math.max(maxActive,active);calls.push([project.motorConfig.gearRatio,engine]);await Promise.resolve();active--;if(project.motorConfig.gearRatio===7&&engine==='pymunk')throw Error('independent backend failure');project.params.m1=999;return actual;},p=>progress.push(p));
  ok(result.jobs.length===4&&result.jobs.filter(j=>j.status==='error').length===1,'independent job errors retained');near(maxActive,1);ok(JSON.stringify(candidates)===before,'runFn cannot mutate input captures');near(result.jobs[0].candidate.project.params.m1,rich.project.params.m1);ok(calls.map(c=>c.join(':')).join(',')==='7:analytical,7:pymunk,1:analytical,1:pymunk','engines/candidates serial order');near(progress.at(-1).completed,4);
  let cancelled=false;const partial=await A.batch(candidates,['analytical','pymunk'],async()=>actual,()=>{cancelled=true;},()=>cancelled);ok(partial.cancelled&&partial.jobs.length===1&&partial.totalJobs===4,'cancel retains completed captures and stops scheduling');
  let release;const wait=new Promise(resolve=>{release=resolve;});const mutable=realm([rich,base]);const pending=A.batch(mutable,['analytical'],async()=>{await wait;return actual;});mutable[1].project.params.m1=321;release();const captured=await pending;near(captured.jobs[1].candidate.project.params.m1,base.project.params.m1);
  const blocked=realm([rich]);blocked[0].actuator=unknown;blocked[0].actuator.values.idealizeUnknowns=false;let attempted=false;const denied=await A.batch(blocked,['analytical'],async()=>{attempted=true;return actual;});ok(!attempted&&denied.jobs[0].status==='error','unknown terms fail before any backend invocation');
  attempted=false;const invalid=realm([{...rich,project:null,error:'Explicit unknown motor properties require an idealization choice.'}]);const refused=await A.batch(invalid,['analytical'],async()=>{attempted=true;return actual;});ok(!attempted&&refused.jobs[0].error===invalid[0].error,'composition failures retain their actionable explanation without invoking a backend');
  console.log('PASS '+checks+' preset analysis assertions; actual engine integration is separate.');
})().catch(error=>{console.error(error);process.exitCode=1;});
