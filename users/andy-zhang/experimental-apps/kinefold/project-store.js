/** Versioned Kinefold project validation and browser-local design library.
 * Load after model.js/variables.js; Node verification uses a VM. Inputs are
 * builder mm/deg/kg/N parameters, view flags and SI solver settings. Outputs are
 * validated project-v2 snapshots and explicit storage results; no runs are saved.
 * Browser-local persistence is not a backup; portable JSON is the recovery path.
 */
globalThis.KinefoldProjects=(()=>{
'use strict';
const schema='kinefold/project-v2',workingKey='kinefold-project-v2',libraryKey='kinefold-library-v2';
const viewDefaults={projection:'side',labels:true,dimensions:true,belts:true,path:true,loads:false,axes:true,grid:true,indices:true,beltMarkers:true};
const solverDefaults={fixture:'fixed-hip',duration:2,dt:.001,outputHz:100,initialVelocityDegS:0,hipTorqueNm:0,dampingNms:.1,hipRotorInertiaKgM2:.05,inertiaModel:'uniform-rods-discs',I2:0,I3:0,I5:0,I6:0,iterations:80};
const clone=v=>JSON.parse(JSON.stringify(v));
const plain=v=>v!==null&&typeof v==='object'&&!Array.isArray(v)&&Object.getPrototypeOf(v)===Object.prototype;
function object(v,label){if(!plain(v))throw Error(label+' must be an object.');for(const k of Object.keys(v))if(['__proto__','prototype','constructor'].includes(k))throw Error('Unsafe key in '+label+'.');}
function keys(v,allowed,label){object(v,label);for(const k of Object.keys(v))if(!allowed.includes(k))throw Error('Unknown '+label+' field: '+k);}
function id(){return 'design-'+(globalThis.crypto?.randomUUID?.()||Date.now().toString(36)+'-'+Math.random().toString(36).slice(2));}
function title(v){if(typeof v!=='string'||!v.trim()||v.length>80||/[\u0000-\u001f]/.test(v))throw Error('Design name must contain 1–80 readable characters.');return v.trim();}
function validateConfig(v){
 keys(v,Object.keys(solverDefaults),'solver configuration');const out={};
 for(const [k,fallback]of Object.entries(solverDefaults)){if(!(k in v))throw Error('Missing solver setting: '+k);if(typeof v[k]!==typeof fallback||(typeof fallback==='number'&&!Number.isFinite(v[k])))throw Error(k+' must be a finite '+typeof fallback+'.');out[k]=v[k];}
 if(out.fixture!=='fixed-hip')throw Error('Only the fixed-hip fixture is supported.');
 if(!['uniform-rods-discs','custom'].includes(out.inertiaModel))throw Error('Choose a known inertia model.');
 const limits={duration:[.05,30],dt:[.0001,.01],outputHz:[1,1000],initialVelocityDegS:[-720,720],hipTorqueNm:[-10000,10000],dampingNms:[0,10000],hipRotorInertiaKgM2:[0,1000],I2:[0,1000],I3:[0,1000],I5:[0,1000],I6:[0,1000],iterations:[10,500]};
 for(const [k,[lo,hi]]of Object.entries(limits))if(out[k]<lo||out[k]>hi)throw Error(k+' must be between '+lo+' and '+hi+'.');
 if(!Number.isInteger(out.iterations))throw Error('iterations must be a whole number.');
 if(Math.ceil(out.duration/out.dt)>100000)throw Error('Run exceeds 100000 integration steps.');
 if(out.outputHz>1/out.dt)throw Error('Output rate exceeds the integration rate.');
 return out;
}
function validate(value){
 keys(value,['schema','id','name','params','view','solverConfig','createdAt','updatedAt'],'project');if(value.schema!==schema)throw Error('Unsupported project schema.');
 if(typeof value.id!=='string'||!/^design-[a-zA-Z0-9-]{1,100}$/.test(value.id))throw Error('Invalid design identifier.');
 keys(value.params,Object.keys(Kinefold.defaults),'parameter');const params={};
 for(const [k,v]of Object.entries(Kinefold.defaults)){if(!(k in value.params))throw Error('Missing design parameter: '+k);if(typeof value.params[k]!==typeof v)throw Error('Invalid type for '+k);params[k]=value.params[k];}
 const errors=Kinefold.validate(params);if(errors.length)throw Error(errors.join(' '));
 for(const g of KinefoldFields)for(const [,fields]of g.sections)for(const [k,,,,,min,max]of fields)if(params[k]<min||params[k]>max)throw Error(k+' is outside its supported input range.');
 keys(value.view,Object.keys(viewDefaults),'view');const view={};for(const [k,v]of Object.entries(viewDefaults)){if(!(k in value.view))throw Error('Missing view setting: '+k);if(k==='projection'?!['side','iso'].includes(value.view[k]):typeof value.view[k]!=='boolean')throw Error('Invalid view setting: '+k);view[k]=value.view[k];}
 const now=new Date().toISOString(),out={schema,id:value.id,name:title(value.name),params,view,solverConfig:validateConfig(value.solverConfig),createdAt:value.createdAt||now,updatedAt:value.updatedAt||now};
 for(const k of ['createdAt','updatedAt'])if(typeof out[k]!=='string'||!/^\d{4}-\d\d-\d\dT/.test(out[k])||!Number.isFinite(Date.parse(out[k])))throw Error('Invalid '+k+'.');
 return out;
}
function baseline(){const now=new Date().toISOString();return {schema,id:id(),name:'Front-left / V4 baseline',params:{...Kinefold.defaults},view:{...viewDefaults},solverConfig:{...solverDefaults},createdAt:now,updatedAt:now};}
function decode(value){if(value?.schema===Kinefold.schema){keys(value,['schema','name','params','view'],'legacy design');keys(value.params,Object.keys(Kinefold.defaults),'legacy parameter');const d=Kinefold.unpack(value),p=baseline();return {project:validate({...p,name:d.name,params:d.params,view:{...viewDefaults,...d.view}}),migrated:true};}return {project:validate(value),migrated:false};}
const content=p=>JSON.stringify([p.name,p.params,p.view,p.solverConfig]);
function createStore(storage){
 let library=[],error='',libraryBlocked=false,persistedLibraryRaw=null;
 try{const raw=storage.getItem(libraryKey);persistedLibraryRaw=raw;if(raw){const data=JSON.parse(raw);keys(data,['schema','designs'],'library');if(data.schema!=='kinefold/library-v2'||!Array.isArray(data.designs)||data.designs.length>200)throw Error('Invalid library format.');library=data.designs.map(validate);if(new Set(library.map(p=>p.id)).size!==library.length)throw Error('Duplicate design identifiers.');}}
 catch(e){error='Saved library could not be read: '+e.message+' Existing browser data was retained; export your working design before recovery.';libraryBlocked=true;}
 function writeLibrary(next){if(libraryBlocked)throw Error(error);if(storage.getItem(libraryKey)!==persistedLibraryRaw)throw Error('The saved library changed in another tab. Reload this page before saving; export your working copy first.');const raw=JSON.stringify({schema:'kinefold/library-v2',designs:next});storage.setItem(libraryKey,raw);persistedLibraryRaw=raw;library=next;}
 return {
  get error(){return error;},list:()=>clone(library),
  restore(){const raw=storage.getItem(workingKey)||storage.getItem('kinefold-design-v1');return raw?decode(JSON.parse(raw)):null;},
  autosave(project){storage.setItem(workingKey,JSON.stringify(validate(project)));},
  save(project){const p=validate(project),next=library.filter(x=>x.id!==p.id);if(next.length>=200)throw Error('Library limit is 200 designs. Export or remove a design first.');p.updatedAt=new Date().toISOString();next.push(p);writeLibrary(next);return clone(p);},
  remove(projectId){const found=library.find(p=>p.id===projectId);if(!found)throw Error('Design is no longer in this library.');writeLibrary(library.filter(p=>p.id!==projectId));return clone(found);},
  duplicate(project,name){return validate({...project,id:id(),name:title(name),createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()});}
 };
}
return {schema,viewDefaults,solverDefaults,validateConfig,validate,baseline,decode,clone,content,createStore,id,title};
})();
