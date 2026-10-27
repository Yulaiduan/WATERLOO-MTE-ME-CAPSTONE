/** Verify contact work charts using both real engines and signed traversal.
 * Run node verify-contact-work.cjs after Setup; KINEFOLD_PYTHON can select an
 * installed app interpreter. Inputs: copied default geometry, SI contact case.
 * Outputs assertion count; no live saved profile or server is read or mutated.
 * VM/trace checks do not certify browser layout, tires or hardware performance.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),cp=require('node:child_process'),assert=require('node:assert/strict');
const ctx=vm.createContext({});
for(const name of ['reference-v4.js','model.js','variables.js','project-store.js','dynamic-analysis.js','dynamic-results.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,name),'utf8'),ctx);
const A=ctx.KinefoldDynamicAnalysis,D=ctx.KinefoldDynamicResults,P=ctx.KinefoldProjects;
let count=0;function ok(value,message){assert.ok(value,message);count++;}
const python=process.env.KINEFOLD_PYTHON||path.join(__dirname,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
const request={params:{...ctx.Kinefold.defaults,m6:1.5},runConfig:{...P.baseline().solverConfig,dt:.00025,duration:.8,outputHz:17},contactConfig:{...P.contactDefaults,mode:'terrain-contact'},caseConfig:{...P.caseDefaults,kind:'landing',landingDropMm:100,landingBrakeTorqueNm:40,landingBrakeLimitNm:400}};
const outputs=[];
for(const engine of ['analytical','pymunk']){
 const child=cp.spawnSync(python,[engine==='analytical'?'analytical_contact.py':'contact_dynamics.py','--request-stdin'],{cwd:__dirname,input:JSON.stringify({...request,engine}),encoding:'utf8',maxBuffer:16*1024*1024});
 assert.equal(child.status,0,child.stderr||child.stdout||String(child.error));
 const result=JSON.parse(child.stdout),before=JSON.stringify(result),rows=A.enrich(result),impact=result.events.find(e=>e.type==='first-contact'),arrest=result.events.find(e=>e.type==='chassis-arrest');
 ok(impact?.state&&arrest?.state,'actual integration event snapshots available');
 const interval=A.integralRows(result,rows,true),full=A.integralRows(result,rows,false);
 ok(interval[0].t===impact.t&&interval.at(-1).t===arrest.t,'exact contact/arrest endpoints injected despite sparse output');
 ok(interval[0].contactSpringStoredJ===0,'contact baseline exact zero');
 ok(Math.abs(interval.at(-1).contactSpringStoredJ-arrest.sinceContact.springStoredJ)<1e-12,'arrest uses exact potential difference');
 ok(full[0].t===0&&full.at(-1).t===result.rows.at(-1).t,'full trajectory retained');
 const velocities=A.velocityRows(result,interval);
 ok(velocities[0].t===velocities[1].t&&velocities[0].eventSide==='before wheel impulse','pre/post impulse velocity discontinuity retained at one timestamp');
 ok(velocities[0].wheelVelocityZMmS===impact.preImpulseWheelVelocityZMmS,'actual wheel pre-impulse speed retained');
 for(const item of A.integralManifest){
  const config={...item,rows:item.id==='integral-event-speed'?velocities:interval},traces=D.traces(config);
  ok(traces.length===item.series.length,'all integral series present in '+engine);
  traces.forEach((trace,index)=>{
   ok(trace.type==='scatter','offline BASIC-compatible scatter only');
   ok(trace.customdata.length===config.rows.length,'all signed trajectory samples retained');
   config.rows.forEach((row,i)=>{
    const x=item.xKey?row[item.xKey]:row.t;
    ok(trace.x[i]===(Number.isFinite(x)?x:null),'correct physical abscissa including signed backtracking');
    ok(trace.customdata[i][2]===row.t,'parametric hover/seek retains actual time');
   });
   if(item.fill)ok(trace.fill==='tozeroy','requested integral areas shaded');
  });
 }
 const html=D.integralSummary(result);
 ok(html.includes('recoverable')&&html.includes('speculative'),'storage and contact detection meanings visible');
 ok(html.includes('not a successful landing')===false,'passing case has no false bottom-out warning');
 ok(html.includes('Unresolved numerical residual'),'residual never hidden as absorbed energy');
 ok(JSON.stringify(result)===before,'plot enrichment never mutates captured result');
 outputs.push(result);
}
const comparison=A.comparison(...outputs);
ok(comparison.valid,'same captured case still compares');
for(const field of ['springStoredJ','motorRemovedJ','gravityReleasedJ','externalWorkJ','contactSpringStoredJ','contactMotorRemovedJ'])ok(comparison.fields.some(item=>item[0]===field),'work term directly compares without shifting engine event time');
for(const engine of ['analytical','pymunk']){
 const child=cp.spawnSync(python,[engine==='analytical'?'analytical_contact.py':'contact_dynamics.py','--request-stdin'],{cwd:__dirname,input:JSON.stringify({...request,engine,caseConfig:{...request.caseConfig,landingDropMm:2000,landingBrakeTorqueNm:0}}),encoding:'utf8',maxBuffer:16*1024*1024});
 assert.equal(child.status,0,child.stderr||child.stdout);
 const result=JSON.parse(child.stdout),stop=result.events.find(e=>e.type==='compression-stop'),interval=A.integralRows(result,A.enrich(result),true);
 ok(stop?.state&&interval.at(-1).t===stop.t,'failed landing includes exact compression-stop state before later arrest');
 ok(D.integralSummary(result).includes('not a successful landing'),'real bottom-out warning survives later zero velocity');
}
const synthetic={rows:[{t:0,theta2:1}],events:[],params:{m1:2}};
const reversal=[{t:0,x:0,y:3},{t:1,x:1,y:4},{t:2,x:.5,y:3.5}];
const trace=D.traces({rows:reversal,xKey:'x',xLabel:'rad',unit:'Nm',fill:true,series:[['y','Torque','sage']]})[0];
ok(trace.x.join(',')==='0,1,0.5','no sorting or absolute-angle accumulation destroys reversal');
ok(A.integralRows(synthetic,synthetic.rows,true).length===1,'no-contact result remains usable');
const ui=fs.readFileSync(path.join(__dirname,'dynamic-results.js'),'utf8');
ok(ui.includes("key === 'integrals'"),'work group opens initially');
ok(ui.includes('A.velocityRows(result,plotRows)')&&ui.includes('A.integralRows(result,rows'),'both engine mounts use same work/event helpers');
const failed={...outputs[0],events:[...outputs[0].events,{type:'compression-stop',t:0}]};
ok(D.integralSummary(failed).includes('not a successful landing'),'later arrest never relabels bottom-out success');
console.log(`PASS ${count} actual-engine contact work / Plotly trace assertions`);
