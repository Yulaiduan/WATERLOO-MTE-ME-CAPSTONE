/** Verify atomic contact/prescribed mode transitions without persistence or runs.
 * Run node verify-contact-mode.cjs. Temporary project-v3 fixtures use mm/deg/kg/N
 * and solver seconds/Nm. Outputs assertions for matching transition distances,
 * fixture validity, remembered bench rises and preserved physical parameters.
 * UI pointer/storage and actual integrators require separate scenario checks.
 */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),ctx=vm.createContext({KinefoldStudio:{}});
for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','contact-ui.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx,{filename:f});
const P=ctx.KinefoldProjects,U=ctx.KinefoldContactUI;
const realm=v=>{ctx.raw=JSON.stringify(v);return vm.runInContext('JSON.parse(raw)',ctx);};
let count=0;const ok=(a,label)=>{assert.ok(a,label);count++;};
const p=realm(P.v45());p.params.te=95;p.params.tc=175;p.params.rc=25;p.params.rd=50;p.params.re=25;p.params.rf=50;
const initial=JSON.stringify(p),contact=U.transition(p,'terrain-contact').project;
ok(contact.solverConfig.inputRiseMm===0,'contact clears prescribed rise');ok(contact.contactConfig.mode==='terrain-contact');ok(U.guards(contact).length===0);ok(JSON.stringify(p)===initial,'transition does not mutate source');
ok(JSON.stringify(contact.params)===JSON.stringify(p.params),'masses/geometry unchanged');ok(contact.solverConfig.hipTorqueNm===p.solverConfig.hipTorqueNm,'command unchanged');P.validate(contact);count++;
const bench=U.transition(contact,'prescribed-height').project;
ok(bench.solverConfig.inputRiseMm===10,'finite bench restores10mm');ok(U.prescribedGuards(bench).length===0);P.validate(bench);count++;
const twenty=realm(bench);twenty.id='design-bench20';twenty.solverConfig.inputRiseMm=20;
const contact20=U.transition(twenty,'terrain-contact').project,bench20=U.transition(contact20,'prescribed-height').project;
ok(contact20.solverConfig.inputRiseMm===0);ok(bench20.solverConfig.inputRiseMm===20,'previous custom bench rise retained');
const fresh=realm(contact);fresh.id='design-fresh';const freshBench=U.transition(fresh,'prescribed-height');ok(freshBench.project.solverConfig.inputRiseMm===10);ok(freshBench.note.includes('10 mm'));
const small=realm(contact);small.id='design-small';small.solverConfig.inputPlateauMm=.1;
ok(U.transition(small,'prescribed-height').project.solverConfig.inputRiseMm===.05,'ramp fits narrow plateau');
const pinned=realm(contact);pinned.solverConfig.fixture='pinned-chassis';const floating=U.transition(pinned,'prescribed-height').project;
ok(floating.solverConfig.fixture==='floating-chassis','mode switch atomically selects supported fixture');P.validate(floating);count++;
const exact=realm(P.baseline());exact.id='design-massless';const exactContact=U.transition(exact,'terrain-contact').project;
ok(U.transition(exactContact,'prescribed-height').project.solverConfig.inputRiseMm===0,'massless exact square retained');
const invalid=realm(contact);invalid.params.te=90;invalid.params.tc=180;
ok(U.guards(invalid).some(s=>s.includes('Energy-only')),'contact keeps singular guard');
ok(U.prescribedGuards(U.transition(invalid,'prescribed-height').project).some(s=>s.includes('Energy-only')),'bench keeps singular guard');
const mismatched=realm(contact);mismatched.contactConfig.mode='prescribed-height';mismatched.solverConfig.inputRiseMm=0;
ok(U.prescribedGuards(mismatched).some(s=>s.includes('positive prescribed-height transition')),'loaded mismatched state is explained');
assert.throws(()=>U.transition(p,'unknown'));count++;
console.log('PASS '+count+' contact-mode transition, fixture, ramp, preservation and strict-guard assertions.');
