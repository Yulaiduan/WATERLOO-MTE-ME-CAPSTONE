/** Verify explicit flat-ground captures and unchanged saved terrain inputs.
 * Run node verify-contact-mode.cjs. Temporary project-v3 fixtures use builder
 * mm/deg/kg/N and run seconds/Nm. Outputs mode, JSON/reload, comparison, payload,
 * stationary drawing and strict-guard assertions. No live data/network writes.
 * Real browser wiring and integrators require the separate UI/engine checks.
 */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const files=['reference-v4.js','model.js','variables.js','project-store.js','contact-ui.js','dynamic-analysis.js'];
function context(){const c=vm.createContext({KinefoldStudio:{}});for(const f of files)vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),c,{filename:f});return c;}
const ctx=context(),P=ctx.KinefoldProjects,U=ctx.KinefoldContactUI,A=ctx.KinefoldDynamicAnalysis;
const copy=v=>v===undefined?v:JSON.parse(JSON.stringify(v)),realm=v=>{ctx.raw=JSON.stringify(v);return vm.runInContext('JSON.parse(raw)',ctx);};
let count=0;const ok=(a,label)=>{assert.ok(a,label);count++;},same=(a,b,label)=>{assert.deepEqual(copy(a),copy(b),label);count++;};
const p=realm(P.v45());p.params.te=95;p.params.tc=175;p.params.rc=25;p.params.rd=50;p.params.re=25;p.params.rf=50;
const initial=JSON.stringify(p),contact=U.transition(p,'terrain-contact').project;
ok(contact.solverConfig.inputRiseMm===0,'actual contact clears legacy prescribed rise');ok(contact.contactConfig.mode==='terrain-contact');ok(U.guards(contact).length===0);ok(JSON.stringify(p)===initial,'source unchanged');
same(U.capture(contact),contact,'actual-contact capture unchanged');same(contact.params,p.params,'geometry/masses unchanged');P.validate(contact);count++;
const bench=U.transition(contact,'prescribed-height').project,stored=JSON.stringify(bench),effective=U.capture(bench);
same(bench.solverConfig,contact.solverConfig,'entering bench retains all stored terrain inputs');ok(bench.contactConfig.mode==='prescribed-height');ok(U.prescribedGuards(bench).length===0);P.validate(bench);count++;
for(const key of ['inputHeightMm','inputSpeedMmS','inputRiseMm','inputDelayS'])ok(effective.solverConfig[key]===0,'effective '+key+' explicitly zero');
for(const key of Object.keys(bench.solverConfig).filter(k=>!['fixture','inputHeightMm','inputSpeedMmS','inputRiseMm','inputDelayS'].includes(k)))same(effective.solverConfig[key],bench.solverConfig[key],'unrelated run setting '+key+' retained');
ok(effective.solverConfig.fixture==='floating-chassis');same(effective.params,bench.params,'capture preserves mechanism/spring');same(effective.motorConfig,bench.motorConfig,'capture preserves motor/loss settings');
ok(JSON.stringify(bench)===stored,'capture is pure');same(U.capture(effective),effective,'capture is idempotent');same(P.decode(realm(effective)).project,effective,'effective snapshot JSON decodes exactly');
const reloaded=context(),reloadedBench=JSON.parse(stored),restored=reloaded.KinefoldContactUI.transition(reloadedBench,'terrain-contact').project;
same(restored.solverConfig,contact.solverConfig,'contact terrain survives fresh runtime / JSON reload');same(restored.params,contact.params,'reload changes no physical design');
for(const engine of ['analytical','pymunk']){const payload=U.payload(bench,engine);same(payload.runConfig,effective.solverConfig,'exact effective '+engine+' request');same(payload.params,bench.params);ok(payload.engine===engine);same(U.payload(contact,engine).runConfig,contact.solverConfig,'contact input is not flattened');}
ok(A.snapshotKey(bench)===A.snapshotKey(effective),'stored and effective bench snapshots compare');
const differentInput=realm(bench);differentInput.solverConfig.inputHeightMm=333;differentInput.solverConfig.inputSpeedMmS=222;differentInput.solverConfig.inputDelayS=2;
ok(A.snapshotKey(differentInput)===A.snapshotKey(bench),'inactive terrain settings do not change effective benchmark');
const differentMass=realm(bench);differentMass.params.m1+=1;ok(A.snapshotKey(differentMass)!==A.snapshotKey(bench),'physical changes invalidate benchmark');
const legacy=realm(P.baseline());legacy.solverConfig.inputRiseMm=10;
same(U.capture(legacy).solverConfig,{...legacy.solverConfig,fixture:'floating-chassis',inputHeightMm:0,inputSpeedMmS:0,inputRiseMm:0,inputDelayS:0},'legacy imported square cannot drive bench terrain');
ok(U.prescribedGuards(legacy).length===0,'legacy terrain resolves explicitly flat without massless jump guards');
const zeroSpeed=realm(contact);zeroSpeed.solverConfig.inputSpeedMmS=0;const zeroBench=U.transition(zeroSpeed,'prescribed-height').project;
P.validate(zeroBench);count++;ok(zeroBench.solverConfig.inputSpeedMmS===0,'stationary contact speed retained');same(U.transition(zeroBench,'terrain-contact').project.solverConfig,zeroSpeed.solverConfig,'stationary terrain survives switch back');
const pinned=realm(contact);pinned.solverConfig.fixture='pinned-chassis';const floating=U.transition(pinned,'prescribed-height').project;
ok(floating.solverConfig.fixture==='floating-chassis','bench explicitly chooses free heave');ok(pinned.solverConfig.fixture==='pinned-chassis','source fixture unchanged');
const invalid=realm(contact);invalid.params.te=90;invalid.params.tc=180;
ok(U.guards(invalid).some(s=>s.includes('Energy-only')),'contact singular guard retained');ok(U.prescribedGuards(U.transition(invalid,'prescribed-height').project).some(s=>s.includes('Energy-only')),'flat bench singular guard retained');
for(const t of [-1,0,.5,4,30]){const floor=A.floor(effective.solverConfig,{t},37,-500,500);same(floor.requested,[[-500,0],[500,0]]);same(floor.applied,floor.requested);same(floor.atWheel,{requested:0,applied:0});ok(floor.distance===0&&!floor.dense,'no moving floor or dense sampling');}
assert.throws(()=>U.transition(p,'unknown'));count++;
const solverSource=fs.readFileSync(__dirname+'/solvers.js','utf8');ok(solverSource.includes('Contact.capture(capture||KinefoldStudio.getSnapshot())'),'single runs capture resolved settings');ok(solverSource.includes('Contact.capture(KinefoldStudio.getSnapshot());pairBusy=true'),'paired run freezes one resolved snapshot');ok(solverSource.includes('captured=Contact.capture(KinefoldStudio.getSnapshot());'),'desktop capture resolves same settings');
console.log('PASS '+count+' flat-ground capture, terrain persistence, request, comparison, floor and strict-guard assertions.');
