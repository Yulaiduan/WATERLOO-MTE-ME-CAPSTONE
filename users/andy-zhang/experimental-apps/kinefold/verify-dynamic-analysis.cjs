/** Verify native dynamic comparison, derived plots and spatial input meaning.
 * Run node verify-dynamic-analysis.cjs [--real]. Inputs: deterministic synthetic
 * event samples plus original builder/backend defaults in mm/deg/kg/N/s.
 * Outputs assertion counts; --real checks actual baseline engines and Python
 * Model.input parity. No hardware, contact or certified continuous peak claim.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),cp=require('node:child_process');
const root=__dirname,ctx=vm.createContext({});
vm.runInContext(['reference-v4.js','model.js','variables.js','project-store.js','dynamic-analysis.js'].map(f=>fs.readFileSync(path.join(root,f),'utf8')).join('\n'),ctx);
const A=ctx.KinefoldDynamicAnalysis,M=ctx.Kinefold,P=ctx.KinefoldProjects,config=JSON.parse(JSON.stringify(P.baseline().solverConfig));
let assertions=0;
const ok=(value,message)=>{assert.ok(value,message);assertions++;};
const near=(a,b,tol=1e-8)=>ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<tol,`${a} versus ${b}`);
function result(engine){return {engine,designHash:'same-mechanism',params:{...M.defaults},runConfig:{...config},diagnostics:{termination:'duration'},
rows:[{t:0},{t:.5,eventSide:'before'},{t:.5,eventSide:'after'},{t:1}].map((r,i)=>({...r,chassisZMm:600+i,chassisVelocityMmS:1,theta2:130+i,velocityDegS:2,accelerationDegS2:3,CxMm:i,wheelZMm:100,Fs:500+i,inputReactionN:85,kineticJ:1,potentialJ:9,rotorKineticJ:0,shaftCommandNm:0,motorDissipatedJ:0,energyJ:10+i,actuatorDampingWorkJ:0,inputWorkJ:i})),frames:[{},{},{},{}]};}
const a=result('analytical'),b=result('pymunk');
ok(A.manifest.length===17);ok(new Set(A.manifest.map(x=>x.id)).size===17);
const enriched=A.enrich(a);near(enriched[1].rate3,-2);near(enriched[1].rate6,0);near(enriched[1].theta3,49);near(enriched[1].workEnergyResidualJ,0);
ok(enriched[0].constraintPositionErrorMm===0);ok(A.enrich(b)[0].constraintPositionErrorMm===null);
let comparison=A.comparison(a,b);ok(comparison.valid);ok(comparison.matched===4);ok(comparison.complete);ok(comparison.stats.every(s=>s.maxAbs===0));
ok(!A.comparison(a,{...b,designHash:'wrong'}).valid);
ok(!A.comparison(a,{...b,motorConfig:{...P.motorDefaults,enabled:true,gearRatio:10}}).valid,'different motor model cannot compare');
ok(A.snapshotKey({...P.baseline(),motorConfig:{...P.motorDefaults,enabled:true}})!==A.snapshotKey(P.baseline()),'motor profile invalidates captured snapshot');
ok(!A.comparison(a,{...b,runConfig:{...config,inputSpeedMmS:101}}).valid);
ok(!A.comparison(a,{...b,params:{...M.defaults,m1:10}}).valid);
ok(!A.comparison(a,{...b,engine:'analytical'}).valid);
const shifted={...b,rows:b.rows.map(r=>({...r,t:r.t+.001}))};ok(!A.comparison(a,shifted).valid);
const missingSide={...b,rows:b.rows.map(r=>({...r,eventSide:undefined}))};ok(A.comparison(a,missingSide).matched===2,'never match a jump side with an ordinary sample');
const early={...b,rows:b.rows.slice(0,2),frames:b.frames.slice(0,2),diagnostics:{termination:'travel-limit'}};
comparison=A.comparison(a,early);ok(comparison.valid&&!comparison.complete);near(comparison.end,.5);ok(comparison.matched===2);
near(A.inputAtDistance(config,0,'left').applied,0);near(A.inputAtDistance(config,0,'right').applied,150);
near(A.inputAtDistance(config,150,'left').applied,150);near(A.inputAtDistance(config,150,'right').applied,0);
for(const side of ['before','after']){const row={t:.5,eventSide:side};const floor=A.floor(config,row,45,-500,500);near(floor.atWheel.applied,side==='before'?0:150);ok(floor.applied.every(([x,z])=>Number.isFinite(x+z)));}
const finite={...config,inputRiseMm:10};near(A.inputAtDistance(finite,5).applied,75);near(A.inputAtDistance(finite,145).applied,75);near(A.inputAtDistance(finite,10).applied,150);
const floor0=A.floor(finite,{t:.55},37,-500,500),floor1=A.floor(finite,{t:.65},37,-500,500);
near(A.inputAtDistance(finite,(.55-config.inputDelayS)*100+40).applied,A.inputAtDistance(finite,(.65-config.inputDelayS)*100+30).applied);
const contact={...b,scope:{mode:'terrain-contact'},rows:b.rows.map(row=>({...row,theta4:30,theta5:20,theta6:10,wheelAngularVelocityDegS:28.6,accelerationDegS2:null,inputWorkJ:null}))};
const ce=A.enrich(contact)[0];near(ce.theta6,10);near(ce.rate6,28.6);ok(ce.accel3===null&&ce.accel5===null&&ce.accel6===null);ok(ce.workEnergyResidualJ===null);ok(!A.comparison(a,contact).valid);ok(A.snapshotKey({params:a.params,solverConfig:config})!==A.snapshotKey({params:a.params,solverConfig:config,contactConfig:{mode:'terrain-contact'}}));
const sameContactA={...contact,engine:'analytical',contactConfig:{...P.contactDefaults},caseConfig:{...P.caseDefaults}},sameContactP={...contact,contactConfig:{...P.contactDefaults},caseConfig:{...P.caseDefaults}};
const contactComparison=A.comparison(sameContactA,sameContactP);ok(contactComparison.valid&&contactComparison.matched===4);ok(contactComparison.fields.some(([key])=>key==='wheelAngularVelocityDegS'));ok(!A.comparison(sameContactA,{...sameContactP,caseConfig:{...P.caseDefaults,kind:'jump'}}).valid);ok(!A.comparison(sameContactA,{...sameContactP,contactConfig:{...P.contactDefaults,friction:0}}).valid);ok(A.snapshotKey({params:a.params,solverConfig:config,caseConfig:P.caseDefaults})!==A.snapshotKey({params:a.params,solverConfig:config}));
const differentOutcomes=A.comparison({...sameContactA,caseMetrics:{outcome:'arrested'}},{...sameContactP,caseMetrics:{outcome:'bottom-out-before-arrest'}});ok(differentOutcomes.valid);ok(differentOutcomes.outcomeA==='arrested'&&differentOutcomes.outcomeP==='bottom-out-before-arrest');
if(process.argv.includes('--real')){
 const python=path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
 const probes=[];
 for(const rise of [0,10])for(const t of [0,.499,.5-1e-11,.5,.5+1e-11,.51,.55,.6,1,1.9,1.95,2-1e-11,2,2+1e-11,3.5,6.5])for(const side of ['left','right'])probes.push({rise,t,side});
 const code="import json,sys;from dynamic_model import Model;v=json.load(sys.stdin);print(json.dumps([Model(v['params'],dict(v['config'],inputRiseMm=p['rise'])).input(p['t'],p['side']) for p in v['probes']]))";
 const query=cp.spawnSync(python,['-c',code],{cwd:root,input:JSON.stringify({params:M.defaults,config,probes}),encoding:'utf8',timeout:30000});
 assert.equal(query.status,0,query.stderr);const expected=JSON.parse(query.stdout);
 probes.forEach((p,i)=>{const actual=A.inputAtDistance({...config,inputRiseMm:p.rise},config.inputSpeedMmS*(p.t-config.inputDelayS),p.side);near(actual.requested,expected[i].requested*1000,1e-6);near(actual.applied,expected[i].applied*1000,1e-6);});
 const runs={};
 for(const engine of ['analytical','pymunk']){
   const process=cp.spawnSync(python,['dynamics.py','--request-stdin'],{cwd:root,input:JSON.stringify({engine,params:M.defaults,runConfig:config}),encoding:'utf8',timeout:90000,maxBuffer:32*1024*1024});
   assert.equal(process.status,0,process.stderr);runs[engine]=JSON.parse(process.stdout);
   fs.mkdirSync(path.join(root,'.preview'),{recursive:true});fs.writeFileSync(path.join(root,'.preview',engine+'-comparison-qa.json'),JSON.stringify(runs[engine]));
 }
 comparison=A.comparison(runs.analytical,runs.pymunk);ok(comparison.valid&&comparison.complete);ok(comparison.matched===656);ok(comparison.stats.find(s=>s.field==='chassisDisplacementMm').maxAbs<.005);
 for(const run of Object.values(runs))for(const row of run.rows){const at=A.floor(run.runConfig,row,row.CxMm,row.CxMm-500,row.CxMm+500).atWheel;near(at.applied,row.appliedInputMm,1e-5);near(at.requested,row.requestedInputMm,1e-5);}
 console.log(JSON.stringify({realBaselinePairs:comparison.matched,heaveMaxErrorMm:comparison.stats[0].maxAbs,pythonInputProbes:probes.length}));
}
console.log(`PASS ${assertions} dynamic presentation/comparison assertions`);
