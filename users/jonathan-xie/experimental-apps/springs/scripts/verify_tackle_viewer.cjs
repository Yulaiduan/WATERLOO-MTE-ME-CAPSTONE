/** Verify actual V7 Spring Lab calculations against saved 2:1 backend results.
 * Run: node scripts/verify_tackle_viewer.cjs from springs root.
 * Inputs: V7 inline geometry core, viewer functions, campaign JSON (mm,N,Nm).
 * Output: assertion count only; no app/workbook writes; no physical qualification.
 */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..'),v=path.resolve(root,'../vsl-solver/v7');
const html=fs.readFileSync(path.join(v,'v7-springlab.html'),'utf8');
const core=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].filter(m=>!m[1].includes('src=')).slice(0,2).map(m=>m[2]).join('\n');
const js=fs.readFileSync(path.join(v,'spring-lab.js'),'utf8');
function get(name){const start=js.indexOf(' function '+name+'(');assert(start>=0,name);let end=js.indexOf('\n function ',start+3);return js.slice(start,end<0?js.length:end);}
const funcs=['settings','shape','inversion','nesting','calculate','tensionCurve'].map(get).join('\n');
const helpers=['ratio','clearance','gapRequired'].map(n=>js.split('\n').find(l=>l.includes(' const '+n+'='))).join('\n');
const records=JSON.parse(fs.readFileSync(path.join(root,'research/2026-11-22-dp18-tackle/campaign.json'),'utf8'));let checks=0;
for(const original of records){const r=JSON.parse(JSON.stringify(original));const context={input:r};vm.createContext(context);
 const out=vm.runInContext(core+'\nconst app={parameters:input.parameters};let record=input,state={...input.settings,...input.geometry,multi:true,n:2};const clone=x=>JSON.parse(JSON.stringify(x));\n'+helpers+'\n'+funcs+'\n;({result:calculate(),record,curves:input.masks.map(mask=>tensionCurve({...app.parameters,...input.geometry},input.springs.filter((s,i)=>mask[i])))})',context);
 assert.equal(out.result.errors.length,0,original.id+':'+out.result.errors);checks++;
 assert(Math.abs(out.result.g.stroke-original.metrics.stroke)<1e-7);checks++;
 assert(out.result.inverted.clearanceValid);assert(Math.abs(out.result.inverted.radialClearance-original.metrics.inversion.radialClearance)<1e-7);checks+=2;
 original.cases.forEach((c,j)=>{assert(Math.abs(out.record.cases[j].maxAbs-c.maxAbs)<.001,original.id+' residual');checks++;});
 out.curves.forEach((curve,j)=>{for(const row of curve.rows){const p={...r.parameters,...r.geometry},part=r.springs[j];context.p=p;context.theta=row.theta;const d=vm.runInContext('VSLSpring.geometry(p,theta).payout-VSLSpring.geometry(p,90).payout',context);const expected=(part.p0+part.k*d/2)/2;assert(Math.abs(row.force-expected)<1e-7);checks++;}});
}
console.log(JSON.stringify({records:records.length,checks,viewer:'actual calculate/shape/inversion/tensionCurve functions',status:'passed'}));