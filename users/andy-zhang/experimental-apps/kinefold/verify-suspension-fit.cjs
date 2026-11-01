/** Verify Kinefold's adapter to the unchanged retained V4 spring optimizer.
 * Run node verify-suspension-fit.cjs from this app or any cwd.
 * Inputs explicit mm/deg/kg/N designs and Lock/Solve masks; outputs assertions
 * on source parity, coordinate-load mapping, immutability and dense torque Nm.
 * No network, live saved profiles, dynamics, browser or hardware validation.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({console,structuredClone});
for(const file of ['reference-v4.js','model.js','suspension-fit.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,file),'utf8'),ctx,{filename:file});
const A=ctx.KinefoldSuspensionFit,M=ctx.Kinefold,F=vm.runInContext('VSLFit',ctx),clone=x=>JSON.parse(JSON.stringify(x));let checks=0;
function ok(value,message){assert.ok(value,message);checks++;}
function near(a,b,label){ok(Math.abs(a-b)<1e-10*Math.max(1,Math.abs(a),Math.abs(b)),`${label}: ${a} vs ${b}`);}
const fixtures=[
 {label:'V4 baseline',p:clone(M.defaults),locks:clone(A.defaults),options:{starts:2,iterations:90}},
 {label:'Finite links / tilted global force',p:{...clone(M.defaults),alpha:20,m2:1,m3:1,m6:.5,loadMode:'global',Fx:27,Fz:110,p0:220},locks:Object.fromEntries(A.keys.map(k=>[k,k!=='p0'])),options:{}},
 {label:'Contact components',p:{...clone(M.defaults),alpha:15,beta:25,m2:.6,m3:.9,m5:.1,m6:.5,loadMode:'contact',Fn:105,Ft:7,p0:230},locks:Object.fromEntries(A.keys.map(k=>[k,k!=='p0'])),options:{}},
 {label:'Everything locked',p:{...clone(M.defaults),alpha:20,m2:1,m3:1,m6:.5},locks:Object.fromEntries(A.keys.map(k=>[k,true])),options:{}}
];
for(const f of fixtures){
 const before=JSON.stringify(f.p),result=A.solve(f.p,f.locks,f.options);ok(result.valid,f.label+': '+result.reason);ok(JSON.stringify(f.p)===before,f.label+' input immutable');
 const sourceInput=M.reference(f.p),original=F.fit(sourceInput,{...clone(A.settings),...f.options,driving:f.locks});ok(original.valid,'Source fit valid');
 for(const key of A.keys){if(f.p.alpha===0||!['Su','Sv'].includes(key))near(result.params[key],original.parameters[key],f.label+' source '+key);if(f.locks[key])ok(result.params[key]===f.p[key],key+' exactly locked');}
 for(const [key,value] of Object.entries(f.p))if(!A.keys.includes(key))ok(result.params[key]===value,key+' outside solver unchanged');
 ok(result.settings.verification===6501,'6501 verification poses');near(result.after.maxTorqueNm,original.maxTorque,'Dense peak source parity');
 if(f.p.loadMode==='global')near(sourceInput.Fy,-f.p.Fx,'Source transverse sign');
 else if(f.p.loadMode==='weight')near(sourceInput.Fy,0,'Weight-reference transverse force');
 else near(sourceInput.Fy,f.p.Fn*Math.sin(f.p.beta*Math.PI/180)+f.p.Ft*Math.cos(f.p.beta*Math.PI/180),'Resolved contact transverse force');
 const rr=M.reference(result.params);let maximum=0;
 for(let i=0;i<6501;i++){const theta=f.p.te+(f.p.tc-f.p.te)*i/6500,z=ctx.KinefoldV4.VSLStatic.solve(rr,theta,false);ok(z.valid,f.label+' dense valid');maximum=Math.max(maximum,Math.abs(z.tau2));}
 near(maximum,result.after.maxTorqueNm,f.label+' dense reported maximum');
 ok(result.free.every(k=>!f.locks[k]),'Only free variables listed');
 console.log(f.label+': '+result.before?.maxTorqueNm+' → '+result.after.maxTorqueNm+' Nm');
}
ok(A.signature({...M.defaults,theta2:145})===A.signature({...M.defaults,theta2:155}),'Pose-only change keeps candidate current');
ok(A.signature({...M.defaults,alpha:20})!==A.signature(M.defaults),'Alpha change invalidates candidate');
const disabled=A.solve({...clone(M.defaults),springEnabled:false});ok(disabled.valid===false&&/Enable spring/.test(disabled.reason),'Disabled suspension rejected');
const invalidStart={...clone(M.defaults),p0:-10},repaired=A.solve(invalidStart,Object.fromEntries(A.keys.map(k=>[k,k!=='p0'])));
ok(M.validate(invalidStart).length>0&&repaired.valid&&repaired.before===null,'Invalid initial spring has no fabricated finite before peak');
assert.throws(()=>A.solve({...clone(M.defaults),springLaw:'constant'}),/removed/);checks++;
assert.throws(()=>A.solve(clone(M.defaults),{p0:'solve'}),/true or false/);checks++;
// Every transport dependency must be reachable through the app allowlist.
const preview=fs.readFileSync(path.join(__dirname,'preview.py'),'utf8'),html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
for(const name of ['suspension-fit.js','suspension-fit-worker.js'])ok(preview.includes('"'+name+'"'),name+' served');
ok(html.indexOf('src="suspension-fit.js"')>html.indexOf('src="model.js"')&&html.indexOf('src="suspension-fit.js"')<html.indexOf('src="app.js"'),'Adapter loads between model and app');
console.log('PASS '+checks+' retained-fitter adapter assertions; four source-equivalent fixtures, no live writes.');
