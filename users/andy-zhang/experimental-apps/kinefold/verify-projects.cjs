/** Verify project/library state safety. Run node verify-projects.cjs.
 * Deterministic mm/deg/kg/N fixture and fake browser storage inputs produce
 * assertion results for migrations, roundtrips and failed persistence. These
 * checks certify state contracts only, not mechanical/hardware performance.
 */
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const read=f=>fs.readFileSync(path.join(__dirname,f),'utf8'),context=vm.createContext({});
for(const file of ['reference-v4.js','model.js','variables.js','project-store.js'])vm.runInContext(read(file),context,{filename:file});
let checks=0;const run=code=>{vm.runInContext(code,context);checks++;};
context.assert=assert;
run(`globalThis.P=KinefoldProjects;globalThis.original=P.baseline();assert.equal(P.validate(original).name,original.name);`);
run(`globalThis.roundtrip=P.decode(JSON.parse(JSON.stringify(original))).project;assert.equal(P.content(roundtrip),P.content(original));`);
run(`globalThis.legacy=Kinefold.pack({...Kinefold.defaults,L2:310,theta2:145},{...P.viewDefaults,projection:'iso',grid:false},'Legacy study');globalThis.migrated=P.decode(legacy);assert.equal(migrated.migrated,true);assert.equal(migrated.project.params.L2,310);assert.equal(migrated.project.params.theta2,145);assert.equal(migrated.project.view.projection,'iso');assert.equal(migrated.project.view.grid,false);`);
run(`globalThis.data=new Map();globalThis.quota=false;globalThis.storage={getItem:k=>data.get(k)||null,setItem:(k,v)=>{if(quota)throw Error('Quota exceeded');data.set(k,v);}};globalThis.store=P.createStore(storage);store.autosave(original);assert.equal(store.restore().project.id,original.id);assert.equal(store.list().length,0);`);
run(`globalThis.saved=store.save(original);globalThis.copy=store.duplicate(saved,'A second design');assert.notEqual(copy.id,saved.id);store.save(copy);assert.equal(store.list().length,2);store.save({...copy,name:'Renamed'});assert.equal(store.list().length,2);`);
run(`globalThis.before=JSON.stringify(store.list());assert.throws(()=>store.save({...saved,params:{...saved.params,L2:NaN}}));assert.equal(JSON.stringify(store.list()),before);assert.throws(()=>P.validate({...saved,solverConfig:{...saved.solverConfig,unknown:1}}));assert.equal(JSON.stringify(store.list()),before);`);
run(`for(const bad of [Infinity,-Infinity,NaN,'300',null]){assert.throws(()=>P.validate({...saved,params:{...saved.params,L2:bad}}));}assert.throws(()=>P.validate({...saved,params:{...saved.params,L2:1e9}}));assert.throws(()=>P.validate({...saved,view:{...saved.view,grid:'yes'}}));assert.throws(()=>P.validate({...saved,name:''}));assert.throws(()=>P.validate({...saved,name:'x'.repeat(81)}));`);
run(`globalThis.removed=store.remove(copy.id);assert.equal(store.list().length,1);store.save(removed);assert.equal(store.list().length,2);globalThis.frozen=JSON.stringify(store.list());quota=true;assert.throws(()=>store.save({...saved,name:'Not actually saved'}),/Quota/);assert.equal(JSON.stringify(store.list()),frozen);quota=false;`);
run(`globalThis.out=store.list();out[0].name='external mutation';assert.notEqual(store.list()[0].name,'external mutation');`);
run(`data.set('kinefold-library-v2','broken');globalThis.corrupt=P.createStore(storage);assert.ok(corrupt.error);assert.throws(()=>corrupt.save(original));assert.equal(data.get('kinefold-library-v2'),'broken');`);
run(`data.delete('kinefold-project-v2');data.set('kinefold-design-v1',JSON.stringify(legacy));assert.equal(store.restore().migrated,true);assert.ok(data.has('kinefold-design-v1'));`);
run(`assert.throws(()=>P.decode(JSON.parse('{"schema":"kinefold/project-v2","__proto__":{}}')));assert.throws(()=>P.validate({...saved,params:{...saved.params,unknown:1}}));`);
run(`globalThis.profile={...original.solverConfig,duration:3,hipTorqueNm:2,inertiaModel:'custom',I2:.02};globalThis.profileProject=P.validate({...original,solverConfig:profile});assert.equal(P.decode(JSON.parse(JSON.stringify(profileProject))).project.solverConfig.I2,.02);for(const value of [Infinity,NaN,'2'])assert.throws(()=>P.validateConfig({...profile,duration:value}));assert.throws(()=>P.validateConfig({...profile,iterations:80.5}));assert.throws(()=>P.validateConfig({...profile,inertiaModel:'unknown'}));`);
run(`data.delete('kinefold-library-v2');globalThis.first=P.createStore(storage);globalThis.second=P.createStore(storage);first.save(original);assert.throws(()=>second.save(copy),/another tab/);assert.equal(JSON.parse(data.get('kinefold-library-v2')).designs.length,1);`);
console.log('PASS '+checks+' project/library scenario groups (migration, state safety, save semantics, storage failure).');
