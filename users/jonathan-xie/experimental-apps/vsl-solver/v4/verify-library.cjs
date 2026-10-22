/** Verify VSL configuration snapshots, inverse reductions, mass-following loads
 * and automatic wrap redirection. Run node verify-library.cjs. Deterministic
 * mm/deg/kg/N/Nm cases; consistency checks, not hardware validation.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),lib=require('./config-library-model.js');
const html=fs.readFileSync(path.join(__dirname,'v4-pulley.html'),'utf8'),scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const {VSL:k,VSLStatic:s,VSLSpring:sp}=vm.runInNewContext(scripts.slice(0,3).join('\n')+';({VSL,VSLStatic,VSLSpring});');
let checks=0;const near=(a,b,e=1e-8)=>{assert.ok(Math.abs(a-b)<e,`${a} != ${b}`);checks++;},p={...s.defaults};
let doc=lib.empty();for(let i=0;i<5;i++)doc=lib.add(doc).document;
assert.deepEqual(doc.rows.map(r=>r.dp),[1,2,3,4,5]);checks++;
let snap=JSON.parse(fs.readFileSync(path.join(__dirname,'v4-default-library.json'))).rows[0].snapshot;
const legacy=JSON.parse(fs.readFileSync(path.join(__dirname,'v4-default-library.json'))),oldGravity=legacy.rows[0].snapshot.outputs.tauG;
lib.validate(legacy);near(legacy.rows[0].snapshot.outputs.tauG,-oldGravity);const once=legacy.rows[0].snapshot.outputs.tauG;lib.validate(legacy);near(legacy.rows[0].snapshot.outputs.tauG,once);assert.deepEqual(legacy.rows[0].snapshot.springDriving,lib.drivingDefaults);checks++;
const chosen={...lib.drivingDefaults,rs:false,p0:true},custom={...legacy.rows[0].snapshot,springDriving:chosen};const restored=lib.load(lib.save(legacy,1,custom),1);assert.deepEqual(restored.snapshot.springDriving,chosen);checks++;
doc=lib.save(doc,3,snap,'2026-10-21T18:00:00Z');snap.parameters.m1=999;
near(doc.rows[2].snapshot.parameters.m1,8.75);const loaded=lib.load(doc,3);loaded.snapshot.parameters.L2=123;near(doc.rows[2].snapshot.parameters.L2,300);assert.equal(loaded.document.loadedDp,3);checks++;
assert.deepEqual(lib.move(doc,[2,3],'up').rows.map(r=>r.dp),[2,3,1,4,5]);assert.deepEqual(lib.move(doc,[2,4],'down').rows.map(r=>r.dp),[1,3,2,5,4]);checks+=2;
const reordered=lib.move(doc,[5],'up');assert.equal(lib.add(reordered).dp,6);assert.throws(()=>lib.load(doc,1));assert.throws(()=>lib.validate({...doc,rows:[doc.rows[0],doc.rows[0]]}));checks+=3;
assert.ok(Object.keys(lib.palette).length>=7);assert.deepEqual(lib.columns.slice(5,12).map(c=>c.key),['totalMass','L2','L3','qab','alpha','globalMaxDz','springK']);checks+=2;
near(k.ratios({...p,rd:70,rc:35,rf:100,re:25}).qdc,2);near(k.ratios({...p,rd:70,rc:35,rf:100,re:25}).qfe,4);
// A wheel contact couple is reduced by qdc*qfe at the motor input.
const drive=s.solve({...p,rd:70,rc:35,rf:100,re:25,Fy:20,Fz:0,springEnabled:false},135);near(drive.tau4,-drive.Mw/8);
for(const mode of ['yz','nt']){const keys=mode==='yz'?['Fy','Fz']:['Fn','Ft'],a={...p,loadMode:mode,[keys[0]]:.9*8.75*9.81,[keys[1]]:-.2*8.75*9.81};let b=s.followMass(a,{...a,m1:10});near(b[keys[0]],.9*10*9.81);near(b[keys[1]],-.2*10*9.81);let zero=s.followMass(b,{...b,m1:0});near(zero[keys[0]],0);b=s.followMass(zero,{...zero,m1:12});near(b[keys[0]],.9*12*9.81);b=s.followMass(b,{...b,g:3});near(b[keys[0]],.9*12*3);}
const normal=sp.exit(p);assert.ok(normal.required<0);near(normal.applied,0);near(normal.direction[0],1);
const positive={...p,hornR:80,Sv:30,Su:0,rs:10,te:100,tc:270},route=sp.exit(positive);assert.ok(route.valid&&route.required>0&&route.referenceExtrapolated);assert.equal(s.validate(positive).length,0);near(sp.state(positive,90).force,positive.p0);checks+=2;
let min=Infinity,max=-Infinity;
for(let i=0;i<=3000;i++){const t=100+170*i/3000,z=sp.state(positive,t);assert.ok(z.valid);assert.ok(z.wrap>=-1e-8&&z.wrap<=2*Math.PI+1e-8);min=Math.min(min,z.wrap);max=Math.max(max,z.wrap);const eq=s.solve(positive,t);near(eq.maxForce,0);near(eq.maxMoment,0);const anchor=z.remote(300),moment=(s.cross(z.S,eq.Fpulley)+s.cross(anchor,eq.FspringAnchor))/1000;near(moment,-z.tauS);checks+=2;}
near(min,route.minWrap,1e-5);near(max,route.maxWrap,1e-5);
const bad={...p,hornR:100,Sv:100,Su:0,nu:0,rs:10};assert.ok(s.validate(bad).some(x=>x.includes('90°')));checks++;
console.log(JSON.stringify({checks,columns:lib.columns.length,defaultZetaDeg:normal.required/k.rad,positiveZetaDeg:route.required/k.rad,referenceExtrapolated:route.referenceExtrapolated},null,2));
