/** Verify exact Plotly dynamic datasets, units, event gaps and engine overlays.
 * Run node verify-dynamic-plotly.cjs. Inputs: current chart manifests and
 * deterministic captured-style rows (s/mm/deg/N/J). Output: assertion count.
 * Pure data verification; browser Plotly layout/click QA is separate.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({});
for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','dynamic-analysis.js','dynamic-results.js']) vm.runInContext(fs.readFileSync(path.join(__dirname,f),'utf8'),ctx);
const A=ctx.KinefoldDynamicAnalysis,D=ctx.KinefoldDynamicResults,P=ctx.KinefoldProjects;
let count=0;
function ok(v,m){assert.ok(v,m);count++;}
const rows=[{t:0},{t:.5,eventSide:'before'},{t:.5,eventSide:'after'},{t:1},{t:1.5}].map((row,i)=>({...row,chassisZMm:600+i,chassisVelocityMmS:1,theta2:130+i,velocityDegS:2,accelerationDegS2:3,CxMm:i,wheelZMm:100,Fs:500+i,inputReactionN:i===3?null:85,kineticJ:1,potentialJ:9,energyJ:10+i,actuatorDampingWorkJ:0,inputWorkJ:i}));
function result(engine,contact=false){return {engine,designHash:'same',params:{...ctx.Kinefold.defaults},runConfig:{...P.baseline().solverConfig},rows:rows.map(r=>({...r,...(contact?{slipMmS:r.t===1?null:4,wheelAngularVelocityDegS:28.6,theta4:30,theta5:20,theta6:10}: {})})),frames:rows.map(()=>({})),diagnostics:{termination:'duration'},...(contact?{scope:{mode:'terrain-contact'},contactConfig:{...P.contactDefaults},caseConfig:{...P.caseDefaults}}:{})};}
function verify(config){
 const traces=D.traces(config);
 ok(traces.length===config.series.length,'all manifest series retained');
 traces.forEach((trace,si)=>{
  const key=config.series[si][0],samples=trace.customdata.map((data,i)=>data&&[data,i]).filter(Boolean);
  ok(samples.length===config.rows.length,'no sample removed/interpolated');
  samples.forEach(([data,i],rowIndex)=>{
   const row=config.rows[rowIndex];
   ok(trace.x[i]===row.t,'exact timestamp including duplicates');
   ok(trace.y[i]===(Number.isFinite(row[key])?row[key]:null),'exact finite value/null gap');
   ok(data[0]===rowIndex&&data[1]===(row.eventSide||'sample')&&data[2]===row.t,'seek event side retained');
  });
  ok(trace.connectgaps===false,'nulls stay disconnected');
  ok(trace.hovertemplate.includes(config.unit),'physical units shown');
  ok(trace.line.dash===(key.endsWith('P')?'dash':'solid'),'engine overlay style');
  if(config.breakJumps)ok(trace.y[2]===null&&trace.customdata[2]===null,'null separates before/after edge');
 });
 const hidden=D.traces(config,new Set());ok(hidden.every(t=>t.visible==='legendonly'),'external unchecked choices preserved');
}
for(const contact of [false,true]){
 const a=result('analytical',contact),b=result('pymunk',contact),enriched=A.enrich(a);
 for(const item of contact?A.contactManifest:A.manifest)verify({...item,rows:enriched,breakJumps:['rates','angular-acceleration','reaction'].includes(item.id)});
 const comparison=A.comparison(a,b);ok(comparison.valid&&comparison.matched===rows.length,'exact comparison catalog');
 for(const [field,label,unit] of comparison.fields){
  verify({rows:comparison.rows,unit,breakJumps:field==='inputReactionN',series:[[field+'A',label+' A','sage'],[field+'P',label+' P','blue']]});
  verify({rows:comparison.rows,unit,breakJumps:field==='inputReactionN',series:[[field+'Error',label+' error','red']]});
 }
}
const source=fs.readFileSync(path.join(__dirname,'dynamic-results.js'),'utf8');
const cursor=source.slice(source.indexOf('  function cursor('),source.indexOf("  if (typeof window"));
ok(cursor.includes('plot().cursor(node, time)')&&!cursor.includes('.react('),'frame cursor never rebuilds traces');
ok(!source.includes('<svg viewBox="0 0 720 340"'),'no handwritten data chart fallback');
console.log(`PASS ${count} dynamic Plotly exact-sample assertions`);
