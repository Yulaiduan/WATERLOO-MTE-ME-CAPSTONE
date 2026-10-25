/** Pure saved-candidate engineering screens and captured sequential batch runner.
 * Load after model, project-store, energy-analysis and preset-store; invoke
 * KinefoldPresetAnalysis.analyze(project, actuatorRecord, sweep) in browser/VM.
 * Inputs builder mm/deg/kg/N and motor/solver SI; outputs JSON SI ranges and
 * Plotly BASIC scatter traces. Fixed-hip prescribed-load screening is separate
 * from actual floating/contact dynamics; no motor curve or hardware validation.
 */
globalThis.KinefoldPresetAnalysis=(()=>{
  'use strict';
  const R=Math.PI/180,clone=v=>JSON.parse(JSON.stringify(v));
  function validateSweep(v){
    if(!v||Object.keys(v).sort().join(',')!=='jointAccelerationRadS2,maxJointSpeedRadS,samples'||!Number.isFinite(v.maxJointSpeedRadS)||v.maxJointSpeedRadS<=0||v.maxJointSpeedRadS>100||!Number.isFinite(v.jointAccelerationRadS2)||Math.abs(v.jointAccelerationRadS2)>1000||!Number.isInteger(v.samples)||v.samples<11||v.samples>101||v.samples%2!==1)throw Error('Sweep requires positive speed ≤100 rad/s, acceleration ±1000 rad/s², and odd 11–101 samples.');
    return {...v};
  }
  function range(values){const finite=values.filter(Number.isFinite);if(!finite.length)return {min:null,max:null,maxAbs:null,count:0};let min=Infinity,max=-Infinity;for(const x of finite){min=Math.min(min,x);max=Math.max(max,x);}return {min,max,maxAbs:Math.max(Math.abs(min),Math.abs(max)),count:finite.length};}
  const seriesRange=(rows,key)=>range(rows.map(r=>r[key]));
  function actuatorValue(record,requireRunnable=true){
    const a=KinefoldPresets.validateRecord(record);if(a.kind!=='actuator')throw Error('An actuator preset is required.');
    if(requireRunnable&&a.values.unknownFields.length&&!a.values.idealizeUnknowns)throw Error('Passive motor data unassessed: '+a.values.unknownFields.join(', ')+'. Explicitly idealize unknown terms before calculating or running.');
    return a;
  }
  function captured(project,record){
    const p=KinefoldProjects.validate(project),a=actuatorValue(record);
    const expected={...a.values.motorConfig,enabled:true};
    if(JSON.stringify(Object.keys(expected).sort().map(k=>[k,expected[k]]))!==JSON.stringify(Object.keys(p.motorConfig||{}).sort().map(k=>[k,p.motorConfig[k]])))throw Error('Candidate project motor does not match its captured actuator preset. Compose the candidate again.');
    return {project:p,actuator:a};
  }
  function fixedHipInertia(params,solver,thetaDeg){
    const q=thetaDeg*R,k3=1-params.ra/params.rb,k5=1-params.rc/params.rd,K=KinefoldV4.VSL.coefficient(params),b=params.phi0*R+(Math.PI-q)*(params.ra/params.rb-1),L=params.L2/1000,l=params.L3/1000;
    const B=[L*Math.sin(q),-L*Math.cos(q)],B2=[L*Math.cos(q),L*Math.sin(q)],E=[l*k3*Math.sin(b),-l*k3*Math.cos(b)],E2=[l*k3*k3*Math.cos(b),l*k3*k3*Math.sin(b)];
    const add=(a,b)=>a.map((v,i)=>v+b[i]),scale=(a,n)=>a.map(v=>v*n),dot=(a,b)=>a[0]*b[0]+a[1]*b[1];
    const sites={2:[scale(B,.5),scale(B2,.5)],3:[add(B,scale(E,.5)),add(B2,scale(E2,.5))],5:[B,B2],6:[add(B,E),add(B2,E2)]};
    const rates={2:1,3:k3,5:k5,6:K};
    const bodyInertias=solver.inertiaModel==='custom'?{2:solver.I2,3:solver.I3,5:solver.I5,6:solver.I6}:{2:params.m2*L*L/12,3:params.m3*l*l/12,5:.5*params.m5*(Math.max(params.rd,params.re)/1000)**2,6:.5*params.m6*(params.rw/1000)**2};
    let movingLegKgM2=0,derivativeKgM2PerRad=0;
    for(const key of Object.keys(sites)){const [v,a]=sites[key],mass=params['m'+key];movingLegKgM2+=mass*dot(v,v)+bodyInertias[key]*rates[key]**2;derivativeKgM2PerRad+=2*mass*dot(v,a);}
    return {movingLegKgM2,legacyJointKgM2:solver.hipRotorInertiaKgM2,legInertiaKgM2:movingLegKgM2+solver.hipRotorInertiaKgM2,legInertiaDerivativeKgM2PerRad:derivativeKgM2PerRad,angularRates:rates,bodyInertias};
  }
  function point(project,thetaDeg,jointSpeedRadS,jointAccelerationRadS2){
    const p=project.params,c=project.solverConfig,m=project.motorConfig,N=m.gearRatio;
    const staticState=KinefoldV4.VSLStatic.solve(Kinefold.reference(p),thetaDeg,false);if(!staticState.valid||!Number.isFinite(staticState.tau2))throw Error(staticState.reason||'Static demand unavailable at '+thetaDeg+'°.');
    const inertia=fixedHipInertia(p,c,thetaDeg),shaftSpeedRadS=N*jointSpeedRadS;
    const coggingJointNm=N*m.coggingAmplitudeNm*Math.sin(m.coggingPeriodsPerRev*N*thetaDeg*R+m.coggingPhaseDeg*R);
    // Friction terms below are positive compensation demands; physical passive
    // friction has the opposite sign. Cogging is a conservative applied torque.
    const coulombJointNm=N*m.coulombFrictionNm*Math.tanh(shaftSpeedRadS/m.frictionVelocityScaleRadS),viscousJointNm=N*m.viscousFrictionNms*shaftSpeedRadS,legacyDampingNm=c.dampingNms*jointSpeedRadS;
    const legAccelerationNm=inertia.legInertiaKgM2*jointAccelerationRadS2,rotorAccelerationNm=N*N*m.rotorInertiaKgM2*jointAccelerationRadS2,coriolisNm=.5*inertia.legInertiaDerivativeKgM2PerRad*jointSpeedRadS**2;
    const gearboxOutputTorqueNm=staticState.tau2+legAccelerationNm+coriolisNm+legacyDampingNm,base=gearboxOutputTorqueNm+rotorAccelerationNm+coulombJointNm+viscousJointNm,amplitude=N*m.coggingAmplitudeNm,jointTorqueNm=base-coggingJointNm;
    return {thetaDeg,jointSpeedRadS,shaftSpeedRadS,shaftRpm:shaftSpeedRadS*60/(2*Math.PI),staticJointNm:staticState.tau2,legInertiaKgM2:inertia.legInertiaKgM2,legInertiaDerivativeKgM2PerRad:inertia.legInertiaDerivativeKgM2PerRad,legAccelerationNm,rotorAccelerationNm,coriolisNm,coggingJointNm,coulombJointNm,viscousJointNm,legacyDampingNm,gearboxOutputTorqueNm,jointTorqueNm,shaftTorqueNm:jointTorqueNm/N,conservativeMinJointNm:base-amplitude,conservativeMaxJointNm:base+amplitude,conservativeMinShaftNm:(base-amplitude)/N,conservativeMaxShaftNm:(base+amplitude)/N};
  }
  function assessment(required,value){return {required:Number.isFinite(required)?required:null,value:value??null,status:!Number.isFinite(required)||!Number.isFinite(value)?'unassessed':required<=value+1e-10?'within-independent-bound':'exceeds-independent-bound'};}
  function ratingsFor(ranges,a){const r=a.values.ratings;return {peakShaftNm:assessment(ranges.shaftTorqueNm?.maxAbs,r.peakShaftNm),maxShaftRpm:assessment(ranges.shaftRpm?.maxAbs,r.maxShaftRpm),gearboxContinuousNm:assessment(ranges.gearboxOutputTorqueNm?.maxAbs,r.gearboxContinuousNm),gearboxPeakNm:assessment(ranges.gearboxOutputTorqueNm?.maxAbs,r.gearboxPeakNm),meaning:'Independent magnitude bounds only; simultaneous capability, duration, regenerative braking and torque–speed curve are unassessed. Joint torque is N times electromagnetic shaft demand; gearbox limits use separate transmitted output torque, excluding motor rotor acceleration and passive compensation. Continuous gearbox bound is compared with sampled maximum, not an RMS or duty-cycle certification.'};}
  const scatter=(name,x,y,extra={})=>({type:'scatter',mode:'lines',name,x,y,...extra});
  // Clip linearly interpolated triangles in scalar space. Isobands tessellate
  // the actual sampled cells; null-separated polygons use BASIC scatter fill.
  function clip(poly,bound,above){const out=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],ia=above?a[2]>=bound:a[2]<=bound,ib=above?b[2]>=bound:b[2]<=bound;if(ia)out.push(a);if(ia!==ib){const t=(bound-a[2])/(b[2]-a[2]);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),bound]);}}return out;}
  function contourTraces(grid,options={}){
    const {x,y,z}=grid;if(!Array.isArray(x)||!Array.isArray(y)||!Array.isArray(z)||x.length<2||y.length<2||z.length!==y.length||z.some(row=>row.length!==x.length))throw Error('Contour grid must have matching x/y/z axes.');
    const r=range(z.flat()),levels=options.levels||Array.from({length:8},(_,i)=>r.min+(r.max-r.min)*i/7);
    if(r.count!==x.length*y.length)throw Error('Contour grid values must all be finite; missing results cannot become zero.');
    if(r.max===r.min)return [scatter('Constant '+r.min.toPrecision(4)+' N·m',[x[0],x.at(-1),x.at(-1),x[0],x[0]],[y[0],y[0],y.at(-1),y.at(-1),y[0]],{fill:'toself',fillcolor:'rgba(58,116,97,.2)'})];
    if(levels.length<2||levels.some((v,i)=>!Number.isFinite(v)||i&&v<=levels[i-1]))throw Error('Contour levels must increase strictly.');
    const colors=['rgba(47,77,104,.23)','rgba(49,111,131,.25)','rgba(51,142,140,.27)','rgba(95,164,132,.29)','rgba(166,184,113,.31)','rgba(214,178,105,.33)','rgba(193,128,101,.35)'];
    const bands=levels.slice(0,-1).map((v,i)=>scatter(v.toPrecision(3)+' to '+levels[i+1].toPrecision(3)+' N·m',[],[],{fill:'toself',fillcolor:colors[i%colors.length],line:{width:0},hoverinfo:'name',showlegend:true})),lines=levels.slice(1,-1).map(v=>scatter(v.toPrecision(4)+' N·m',[],[],{line:{width:1,color:'#405e58'},hoverinfo:'name',showlegend:false}));
    const triangles=[];for(let j=0;j<y.length-1;j++)for(let i=0;i<x.length-1;i++){const a=[x[i],y[j],z[j][i]],b=[x[i+1],y[j],z[j][i+1]],c=[x[i+1],y[j+1],z[j+1][i+1]],d=[x[i],y[j+1],z[j+1][i]];triangles.push([a,b,c],[a,c,d]);}
    for(const tri of triangles){
      for(let n=0;n<bands.length;n++){if(n<bands.length-1&&tri.every(v=>v[2]===levels[n+1]))continue;const poly=clip(clip(tri,levels[n],true),levels[n+1],false);if(poly.length>=3){const t=bands[n];for(const v of [...poly,poly[0]]){t.x.push(v[0]);t.y.push(v[1]);}t.x.push(null);t.y.push(null);}}
      for(let n=0;n<lines.length;n++){const level=levels[n+1],hits=[];for(let k=0;k<3;k++){const a=tri[k],b=tri[(k+1)%3];if((a[2]<level&&b[2]>=level)||(b[2]<level&&a[2]>=level)){const f=(level-a[2])/(b[2]-a[2]);hits.push([a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1])]);}}if(hits.length===2){lines[n].x.push(hits[0][0],hits[1][0],null);lines[n].y.push(hits[0][1],hits[1][1],null);}}
    }
    return [...bands,...lines].filter(t=>t.x.length);
  }
  function energy(project){
    const p=clone(project);if(p.energyConfig)delete p.energyConfig.screening;
    const c={...KinefoldProjects.caseDefaults,...p.caseConfig},e={...KinefoldProjects.energyDefaults,...p.energyConfig},t={...KinefoldProjects.torqueTargetDefaults,...p.torqueTargetConfig};
    const attempt=fn=>{try{return {available:true,result:fn()};}catch(error){return {available:false,reason:error.message};}};
    return {landing:attempt(()=>KinefoldEnergyAnalysis.landingEstimate(p,e.dropHeightMm,e.targetClearanceMm)),jump:attempt(()=>KinefoldEnergyAnalysis.jumpEstimate(p,t.jumpHeightMm)),meaning:'Existing work/endpoint estimates; no trajectory, impact torque peak, motor losses or hardware survival certificate.',caseKind:c.kind};
  }
  function analyze(project,record,sweep){
    const capture=captured(project,record),p=capture.project,a=capture.actuator,s=validateSweep(sweep),N=p.motorConfig.gearRatio;
    const x=Array.from({length:s.samples},(_,i)=>p.params.te+(p.params.tc-p.params.te)*i/(s.samples-1)),y=Array.from({length:s.samples},(_,i)=>s.maxJointSpeedRadS*(2*i/(s.samples-1)-1)),rows=[],staticRows=x.map(thetaDeg=>point(p,thetaDeg,0,0));
    const z=y.map(speed=>x.map(theta=>{const r=point(p,theta,speed,s.jointAccelerationRadS2);rows.push(r);return r.shaftTorqueNm;}));
    const ranges={};for(const k of ['jointTorqueNm','shaftTorqueNm','shaftSpeedRadS','shaftRpm','gearboxOutputTorqueNm'])ranges[k]=seriesRange(rows,k);
    ranges.conservativeJointNm=range(rows.flatMap(r=>[r.conservativeMinJointNm,r.conservativeMaxJointNm]));ranges.conservativeShaftNm=range(rows.flatMap(r=>[r.conservativeMinShaftNm,r.conservativeMaxShaftNm]));
    const leg=seriesRange(staticRows,'legInertiaKgM2'),motor=p.motorConfig,grid={x,y,z,xVariable:'thetaDeg',yVariable:'jointSpeedRadS',zVariable:'shaftTorqueNm'};
    const inertia={rotorShaftKgM2:motor.rotorInertiaKgM2,rotorReflectedJointKgM2:N*N*motor.rotorInertiaKgM2,legacyJointKgM2:p.solverConfig.hipRotorInertiaKgM2,legJointKgM2:leg,legMotorEquivalentKgM2:range(staticRows.map(r=>r.legInertiaKgM2/(N*N))),coggingJointAmplitudeNm:N*motor.coggingAmplitudeNm,coulombJointAmplitudeNm:N*motor.coulombFrictionNm,viscousJointNms:N*N*motor.viscousFrictionNms};
    const speedSlices=y.map((speed,i)=>{const slice=rows.slice(i*x.length,(i+1)*x.length);return {rpm:speed*N*60/(2*Math.PI),min:Math.min(...slice.map(r=>r.conservativeMinShaftNm)),max:Math.max(...slice.map(r=>r.conservativeMaxShaftNm))};});
    const charts={static:[scatter(a.name+' · static joint load',x,staticRows.map(r=>r.staticJointNm)),scatter(a.name+' · static shaft demand with cogging phase',x,staticRows.map(r=>r.shaftTorqueNm),{line:{dash:'dot'}})],torqueSpeed:[scatter(a.name+' · demand envelope ± cogging',speedSlices.map(v=>v.rpm).concat(speedSlices.toReversed().map(v=>v.rpm)),speedSlices.map(v=>v.min).concat(speedSlices.toReversed().map(v=>v.max)),{fill:'toself',fillcolor:'rgba(67,122,104,.12)',line:{width:1}}),scatter(a.name+' · sampled operating points',rows.map(r=>r.shaftRpm),rows.map(r=>r.shaftTorqueNm),{mode:'markers',marker:{size:3,opacity:.35}})],inertia:[scatter('Fixed-hip leg + additional joint inertia',x,staticRows.map(r=>r.legInertiaKgM2)),scatter('Motor-equivalent leg J / N²',x,staticRows.map(r=>r.legInertiaKgM2/(N*N))),scatter('Rotor reflected N² Jm',x,x.map(()=>inertia.rotorReflectedJointKgM2))],contour:contourTraces(grid)};
    return {schema:'kinefold/preset-analysis-v1',actuatorId:a.id,name:a.name,gearRatio:N,sweep:s,scope:'Fixed-hip prescribed-load pose/rate/acceleration screen; separate from floating-chassis and terrain-contact dynamics.',assumptions:['Static demand is the unchanged V4 builder prescribed-load reference, not floating dynamic inverse demand.','Jleg includes moving-body translation, uniform rods/discs or saved custom body inertias, and additional legacy joint inertia; chassis hip is fixed.','τem = τstatic + (Jleg + N²Jm) q̈ + ½ Jleg′ q̇² − N Acog sin(kNq+φ) + N Fc tanh(Nq̇/ε) + N² b q̇ + bjoint q̇.','Cogging has fixed sinusoidal amplitude and conservative potential; Coulomb drag is separately signed and smoothed near zero, not stiction.','Conservative ± cogging bound does not assume the sampled phase finds every peak. Pose/rate grid extrema are sampled, not certified continuous global extrema.','Commands retain the saved '+motor.commandBasis+' basis. Equal numeric inputs in different bases apply different joint torques; catalog bounds never cap dynamics.',...(a.values.unknownFields.length?['Explicit idealization: unknown '+a.values.unknownFields.join(', ')+' treated as zero for this study.']:[])],rows,staticRows,grid,ranges,inertia,ratings:ratingsFor(ranges,a),energy:energy(p),charts};
  }
  function summarizeRun(result,project,record){
    const {project:p,actuator:a}=captured(project,record);if(!result||!Array.isArray(result.rows)||!result.rows.length)throw Error('Dynamic result contains no actual sampled rows.');
    const N=p.motorConfig.gearRatio,rows=result.rows.map(r=>({...r,jointTorqueNm:Number.isFinite(r.jointElectromagneticNm)?r.jointElectromagneticNm:r.motorTorqueNm,shaftTorqueNm:Number.isFinite(r.shaftCommandNm)?r.shaftCommandNm:Number.isFinite(r.jointElectromagneticNm)?r.jointElectromagneticNm/N:Number.isFinite(r.motorTorqueNm)?r.motorTorqueNm/N:null,shaftSpeedRadS:Number.isFinite(r.motorVelocityRadS)?r.motorVelocityRadS:Number.isFinite(r.velocityDegS)?r.velocityDegS*R*N:null}));
    for(const r of rows){r.shaftRpm=Number.isFinite(r.shaftSpeedRadS)?r.shaftSpeedRadS*60/(2*Math.PI):null;r.gearboxOutputTorqueNm=result.scope?.mode!=='terrain-contact'&&!r.eventSide&&[r.jointTorqueNm,r.jointCoggingNm,r.jointFrictionNm,r.accelerationDegS2].every(Number.isFinite)?r.jointTorqueNm+r.jointCoggingNm+r.jointFrictionNm-N*N*p.motorConfig.rotorInertiaKgM2*r.accelerationDegS2*R:null;}
    const ranges={};for(const k of ['t','theta2','velocityDegS','jointTorqueNm','shaftTorqueNm','shaftSpeedRadS','shaftRpm','gearboxOutputTorqueNm','energyJ','kineticJ','potentialJ','rotorKineticJ','motorDissipatedJ','motorFrictionLossJ','motorLossPowerW','jointCoggingNm','jointFrictionNm','chassisZMm'])ranges[k]=seriesRange(rows,k);
    const ratings=ratingsFor(ranges,a),warnings=[];
    if(ranges.gearboxOutputTorqueNm.count!==rows.length){const reason='Transmitted gearbox output is unavailable at rows without finite actual angular acceleration/passive torques or at contact/impulse/event rows. Electromagnetic command is not substituted for output load.';warnings.push(reason);for(const k of ['gearboxContinuousNm','gearboxPeakNm'])ratings[k]={...ratings[k],status:'unassessed',reason};}
    if(result.events?.some(e=>e.type==='exact-square-jump'&&Math.abs(e.theta2JumpDeg)>1e-10)){warnings.push('Ideal input causes an instantaneous pose jump: shaft speed at that discontinuity has no finite peak; the displayed range contains finite one-sided rows only.');ratings.maxShaftRpm={...ratings.maxShaftRpm,status:'unassessed',reason:warnings[0]};}
    return {scope:'Actual backend sampled trajectory; finite row extrema only, not continuous-time peak guarantees.',rowCount:rows.length,ranges,ratings,warnings,outcome:clone(result.caseMetrics?.outcome??null),diagnostics:clone(result.diagnostics??{}),torqueSpeed:scatter(a.name+' · actual '+(result.engine||'engine'),rows.map(r=>r.shaftRpm),rows.map(r=>Number.isFinite(r.shaftTorqueNm)?r.shaftTorqueNm:null),{mode:'lines+markers',marker:{size:3}})};
  }
  async function batch(candidates,engines,runFn,onProgress=()=>{},shouldCancel=()=>false){
    if(!Array.isArray(candidates)||!candidates.length||candidates.length>40||!Array.isArray(engines)||!engines.length||new Set(engines).size!==engines.length||engines.some(e=>!['analytical','pymunk'].includes(e))||typeof runFn!=='function')throw Error('Batch requires 1–40 captured candidates and distinct analytical/pymunk engines.');
    // Clone the entire job list before the first await; external selection edits
    // and mutation inside runFn cannot rewrite captures of scheduled jobs.
    const inputs=clone(candidates),selected=[...engines],jobs=[],totalJobs=inputs.length*selected.length;
    let cancelled=false;for(const candidate of inputs){for(const engine of selected){if(shouldCancel()){cancelled=true;break;}const job={candidate:clone(candidate),engine,status:'error'};try{if(candidate.error)throw Error(String(candidate.error));captured(candidate.project,candidate.actuator);const result=await runFn(clone(candidate.project),engine);job.summary=summarizeRun(result,candidate.project,candidate.actuator);job.result=clone(result);job.status='complete';}catch(error){job.error=String(error?.message||error);}jobs.push(job);onProgress({completed:jobs.length,total:totalJobs,engine,candidateId:candidate.actuator?.id??null,status:job.status});}if(cancelled)break;}
    return {schema:'kinefold/preset-batch-v1',jobs,cancelled,totalJobs,completedJobs:jobs.length};
  }
  return {analyze,summarizeRun,batch,contourTraces,range,validateSweep,fixedHipInertia};
})();
