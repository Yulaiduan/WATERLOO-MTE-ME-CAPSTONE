/** Exercise captured preset combinations through both actual quarter engines.
 * Run: node verify-preset-batch.cjs [--http] from this app directory after Setup;
 * --http requires the app-local Start Kinefold.cmd service on 127.0.0.1:4191.
 * Inputs: explicitly illustrative SI motor properties, V4 mm/deg/kg mechanism,
 * the user-approved 1.5 kg free wheel and a short flat translating-floor case.
 * Outputs: compact console/ignored .preview evidence; no live library writes.
 * Limits: integration/provenance check, not motor data or hardware validation.
 */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=__dirname;
for(const file of ['reference-v4.js','model.js','variables.js','project-store.js','preset-store.js','energy-analysis.js','preset-analysis.js','dynamic-analysis.js'])require(path.join(root,file));
const P=globalThis.KinefoldProjects,Q=globalThis.KinefoldPresets,A=globalThis.KinefoldPresetAnalysis;
const http=process.argv.includes('--http'),url='http://127.0.0.1:4191';
const python=path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
function fixture(){
  const project=P.baseline();
  project.params.m6=1.5;
  Object.assign(project.solverConfig,{duration:.3,dt:.00025,outputHz:50,inputHeightMm:0,hipTorqueNm:0});
  project.contactConfig={...P.contactDefaults,mode:'terrain-contact',friction:.8,restitution:0,drive:'free'};
  const suspension=Q.make('suspension','V4 test mechanism / explicit 1.5 kg wheel',Q.captureSuspension(project));
  const input=Q.make('input','Illustrative 0.3 s flat-floor contact input',Q.captureInput(project));
  const candidates=[5,10].map(N=>{
    const values=Q.captureActuator(project);
    Object.assign(values.motorConfig,{gearRatio:N,rotorInertiaKgM2:.0002,coggingAmplitudeNm:.002,coggingPeriodsPerRev:1,coulombFrictionNm:.001,viscousFrictionNms:.0001});
    values.catalog.notes='Explicit numerical test inputs; not measured or catalog motor properties.';
    const actuator=Q.make('actuator','Illustrative N='+N+' numerical fixture',values);
    return {project:Q.compose(project,suspension,actuator,input),suspension,input,actuator};
  });
  return {project,suspension,input,candidates};
}
async function run(project,engine){
  const payload={engine,params:project.params,runConfig:project.solverConfig,motorConfig:project.motorConfig,contactConfig:project.contactConfig};
  if(project.caseConfig)payload.caseConfig=project.caseConfig;
  if(http){
    const response=await fetch(url+'/api/dynamics',{method:'POST',headers:{'Content-Type':'application/json','Origin':url,'X-Kinefold-Request':'coupled-dynamics'},body:JSON.stringify(payload)});
    const result=await response.json();assert.equal(response.status,200,result.error);return result;
  }
  const script=engine==='analytical'?'analytical_contact.py':'contact_dynamics.py';
  const process=spawnSync(python,[path.join(root,script),'--request-stdin'],{input:JSON.stringify(payload),encoding:'utf8',maxBuffer:20*1024*1024,timeout:90000,cwd:root,windowsHide:true});
  assert.ifError(process.error);assert.equal(process.status,0,process.stderr||process.stdout);
  const result=JSON.parse(process.stdout);assert.ok(!result.error,result.error);return result;
}
(async()=>{
  const {project,suspension,input,candidates}=fixture(),before=JSON.stringify({project,suspension,input,candidates});
  const progress=[];
  const result=await A.batch(candidates,['analytical','pymunk'],run,event=>progress.push(event));
  assert.equal(result.jobs.length,4);assert.equal(result.cancelled,false);assert.equal(progress.length,4);
  assert.equal(JSON.stringify({project,suspension,input,candidates}),before,'batch mutated input records');
  const pairs=[];
  for(const candidate of candidates){
    const jobs=result.jobs.filter(job=>job.candidate.actuator.id===candidate.actuator.id);
    assert.equal(jobs.length,2);
    for(const job of jobs){
      assert.equal(job.status,'complete',job.error);
      assert.deepEqual(job.candidate.input,input);
      assert.deepEqual(job.candidate.suspension,suspension);
      assert.deepEqual(job.result.params,candidate.project.params);
      assert.deepEqual(job.result.runConfig,candidate.project.solverConfig);
      assert.deepEqual(job.result.motorConfig,candidate.project.motorConfig);
      assert.equal(job.result.diagnostics.termination,'duration');
      assert.ok(job.summary.ranges.shaftRpm.count>0,'actual shaft speed is absent');
      assert.ok(job.summary.ranges.shaftTorqueNm.count>0,'actual electromagnetic shaft torque is absent');
      assert.equal(job.summary.ratings.maxShaftRpm.status,'unassessed','unknown rating became a bound');
      assert.equal(job.summary.ratings.gearboxPeakNm.status,'unassessed','contact impulse output torque was invented');
    }
    const [analytical,pymunk]=jobs.map(job=>job.result),comparison=KinefoldDynamicAnalysis.comparison(analytical,pymunk);
    assert.ok(comparison.valid,comparison.reason);
    const rows=analytical.rows.map((row,i)=>({a:row,b:pymunk.rows[i]}));
    assert.equal(analytical.rows.length,pymunk.rows.length);
    for(const row of rows)assert.equal(row.a.t,row.b.t,'different observation schedule');
    const maxHeaveMm=Math.max(...rows.map(({a,b})=>Math.abs(a.chassisZMm-b.chassisZMm)));
    assert.ok(Number.isFinite(maxHeaveMm));
    pairs.push({ratio:candidate.project.motorConfig.gearRatio,matchedSamples:rows.length,maxChassisDifferenceMm:maxHeaveMm,engines:jobs.map(job=>({engine:job.engine,termination:job.result.diagnostics.termination,ranges:job.summary.ranges}))});
  }
  const evidence={status:'PASS',mode:http?'actual same-origin HTTP API':'actual engine subprocesses',jobs:4,sameCapturedSuspensionAndInput:true,sourcePresetsUnchanged:true,pairs,limits:['Illustrative motor values, not component estimates','Short flat-floor integration only; not terrain-edge, hardware or continuous-time peak validation']};
  fs.mkdirSync(path.join(root,'.preview'),{recursive:true});
  fs.writeFileSync(path.join(root,'.preview/preset-batch-validation.json'),JSON.stringify(evidence,null,2)+'\n');
  console.log(JSON.stringify({...evidence,pairs:pairs.map(({engines,...rest})=>rest)},null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
