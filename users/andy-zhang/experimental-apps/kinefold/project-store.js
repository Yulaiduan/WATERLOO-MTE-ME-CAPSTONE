/** Versioned project validation, legacy browser recovery and app-folder library.
 * Load after model.js/variables.js; Node verification uses a VM. Inputs are
 * builder mm/deg/kg/N parameters, view flags and SI solver settings. Outputs are
 * validated project-v3 snapshots and explicit storage results; no runs are saved.
 * App-folder profiles and portable exports persist independently of the browser.
 */
globalThis.KinefoldProjects=(()=>{
'use strict';
const schema='kinefold/project-v3',workingKey='kinefold-project-v3',libraryKey='kinefold-library-v3';
const viewDefaults={projection:'side',labels:true,dimensions:true,belts:true,path:true,loads:false,axes:true,grid:true,indices:true,beltMarkers:true};
const legacyDefaults={fixture:'fixed-hip',duration:2,dt:.001,outputHz:100,initialVelocityDegS:0,hipTorqueNm:0,dampingNms:.1,hipRotorInertiaKgM2:.05,inertiaModel:'uniform-rods-discs',I2:0,I3:0,I5:0,I6:0,iterations:80};
const solverDefaults={...legacyDefaults,fixture:'floating-chassis',duration:6.5,dampingNms:0,hipRotorInertiaKgM2:0,inputHeightMm:150,inputPlateauMm:150,inputGapMm:150,inputSpeedMmS:100,inputRiseMm:0,inputDelayS:.5};
const motorDefaults={enabled:false,gearRatio:1,rotorInertiaKgM2:0,coggingAmplitudeNm:0,coggingPeriodsPerRev:1,coggingPhaseDeg:0,coulombFrictionNm:0,viscousFrictionNms:0,frictionVelocityScaleRadS:.01,commandBasis:'joint'};
function validateMotor(value){
 keys(value,Object.keys(motorDefaults),'motor configuration');
 for(const key of Object.keys(motorDefaults))if(!(key in value))throw Error('Missing motor setting: '+key);
 if(typeof value.enabled!=='boolean'||!['joint','motor'].includes(value.commandBasis))throw Error('Choose motor enable state and joint/motor command basis.');
 const limits={gearRatio:[1e-6,1e4],rotorInertiaKgM2:[0,1000],coggingAmplitudeNm:[0,10000],coggingPeriodsPerRev:[1,10000],coggingPhaseDeg:[-360,360],coulombFrictionNm:[0,10000],viscousFrictionNms:[0,10000],frictionVelocityScaleRadS:[1e-6,1000]};
 for(const [key,[lo,hi]]of Object.entries(limits))if(!Number.isFinite(value[key])||value[key]<lo||value[key]>hi)throw Error(key+' must be finite between '+lo+' and '+hi+'.');
 if(!Number.isInteger(value.coggingPeriodsPerRev))throw Error('Cogging periods must be a whole number.');
 return {...value};
}
const contactDefaults={mode:'terrain-contact',friction:.8,restitution:0,drive:'free'};
const caseDefaults={kind:'terrain-stability',jumpTorqueNm:20,landingDropMm:100,landingOpenFraction:2/3,landingBrakeTorqueNm:20,landingBrakeLimitNm:200,brakeStrategy:'entered',undersideOffsetMm:50,energyMethod:true};
function validateCase(value){
 keys(value,Object.keys(caseDefaults),'case configuration');
 for(const key of Object.keys(caseDefaults))if(!(key in value))throw Error('Missing case setting: '+key);
 if(!['terrain-stability','jump','landing'].includes(value.kind)||!['entered','energy-sized'].includes(value.brakeStrategy)||typeof value.energyMethod!=='boolean')throw Error('Choose a known case and braking strategy.');
 for(const [key,[lo,hi]]of Object.entries({jumpTorqueNm:[0,10000],landingDropMm:[0,5000],landingOpenFraction:[.01,.99],landingBrakeTorqueNm:[0,10000],landingBrakeLimitNm:[0,10000]}))if(!Number.isFinite(value[key])||value[key]<lo||value[key]>hi)throw Error(key+' must be between '+lo+' and '+hi+'.');
 if(value.undersideOffsetMm!==null&&(!Number.isFinite(value.undersideOffsetMm)||value.undersideOffsetMm<0||value.undersideOffsetMm>5000))throw Error('Underside offset must be blank (unassessed) or 0–5000 mm below hip A.');
 return {...value};
}
function validateContact(value){
 keys(value,Object.keys(contactDefaults),'contact configuration');
 if(!['prescribed-height','terrain-contact'].includes(value.mode)||value.drive!=='free'||value.restitution!==0||!Number.isFinite(value.friction)||value.friction<0||value.friction>2)throw Error('Contact mode requires finite friction 0–2, zero bounce and a freely backdrivable drive.');
 return {...value};
}
const clone=v=>JSON.parse(JSON.stringify(v));
const plain=v=>v!==null&&typeof v==='object'&&!Array.isArray(v)&&Object.getPrototypeOf(v)===Object.prototype;
function object(v,label){if(!plain(v))throw Error(label+' must be an object.');for(const k of Object.keys(v))if(['__proto__','prototype','constructor'].includes(k))throw Error('Unsafe key in '+label+'.');}
function keys(v,allowed,label){object(v,label);for(const k of Object.keys(v))if(!allowed.includes(k))throw Error('Unknown '+label+' field: '+k);}
function id(){return 'design-'+(globalThis.crypto?.randomUUID?.()||Date.now().toString(36)+'-'+Math.random().toString(36).slice(2));}
function title(v){if(typeof v!=='string'||!v.trim()||v.length>80||/[\u0000-\u001f]/.test(v))throw Error('Design name must contain 1–80 readable characters.');return v.trim();}
function validateConfig(v,legacy=false){const defaults=legacy?legacyDefaults:solverDefaults;
 keys(v,Object.keys(defaults),'solver configuration');const out={};
 for(const [k,fallback]of Object.entries(defaults)){if(!(k in v))throw Error('Missing solver setting: '+k);if(typeof v[k]!==typeof fallback||(typeof fallback==='number'&&!Number.isFinite(v[k])))throw Error(k+' must be a finite '+typeof fallback+'.');out[k]=v[k];}
 if(out.fixture!==defaults.fixture)throw Error('Unknown dynamic fixture.');
 if(!['uniform-rods-discs','custom'].includes(out.inertiaModel))throw Error('Choose a known inertia model.');
 const limits={duration:[.05,30],dt:[.0001,.01],outputHz:[1,1000],initialVelocityDegS:[-720,720],hipTorqueNm:[-10000,10000],dampingNms:[0,10000],hipRotorInertiaKgM2:[0,1000],I2:[0,1000],I3:[0,1000],I5:[0,1000],I6:[0,1000],iterations:[10,500]};
 for(const [k,[lo,hi]]of Object.entries(limits))if(out[k]<lo||out[k]>hi)throw Error(k+' must be between '+lo+' and '+hi+'.');
 if(!legacy){const inputLimits={inputHeightMm:[0,1000],inputPlateauMm:[.1,10000],inputGapMm:[.1,10000],inputSpeedMmS:[.1,10000],inputRiseMm:[0,1000],inputDelayS:[0,30]};for(const [key,[lo,hi]]of Object.entries(inputLimits))if(out[key]<lo||out[key]>hi)throw Error(key+' must be between '+lo+' and '+hi+'.');if(2*out.inputRiseMm>out.inputPlateauMm)throw Error('Rise distance must fit twice inside the plateau.');const period=(out.inputPlateauMm+out.inputGapMm)/out.inputSpeedMmS;if(4*Math.ceil(Math.max(0,out.duration-out.inputDelayS)/period)>10000)throw Error('Run exceeds 10000 input transition boundaries; reduce speed or duration.');}
 if(!Number.isInteger(out.iterations))throw Error('iterations must be a whole number.');
 if(Math.ceil(out.duration/out.dt)>100000)throw Error('Run exceeds 100000 integration steps.');
 if(out.outputHz>1/out.dt)throw Error('Output rate exceeds the integration rate.');
 return out;
}
function validate(value){
 keys(value,['schema','id','name','params','view','solverConfig','createdAt','updatedAt','legacySolverConfig','contactConfig','caseConfig','motorConfig'],'project');if(value.schema!==schema)throw Error('Unsupported project schema.');
 if(typeof value.id!=='string'||!/^design-[a-zA-Z0-9-]{1,100}$/.test(value.id))throw Error('Invalid design identifier.');
 keys(value.params,Object.keys(Kinefold.defaults),'parameter');const params={};
 for(const [k,v]of Object.entries(Kinefold.defaults)){if(!(k in value.params))throw Error('Missing design parameter: '+k);if(typeof value.params[k]!==typeof v)throw Error('Invalid type for '+k);params[k]=value.params[k];}
 const errors=Kinefold.validate(params);if(errors.length)throw Error(errors.join(' '));
 for(const g of KinefoldFields)for(const [,fields]of g.sections)for(const [k,,,,,min,max]of fields)if(params[k]<min||params[k]>max)throw Error(k+' is outside its supported input range.');
 keys(value.view,Object.keys(viewDefaults),'view');const view={};for(const [k,v]of Object.entries(viewDefaults)){if(!(k in value.view))throw Error('Missing view setting: '+k);if(k==='projection'?!['side','iso'].includes(value.view[k]):typeof value.view[k]!=='boolean')throw Error('Invalid view setting: '+k);view[k]=value.view[k];}
 const now=new Date().toISOString(),out={schema,id:value.id,name:title(value.name),params,view,solverConfig:validateConfig(value.solverConfig),createdAt:value.createdAt||now,updatedAt:value.updatedAt||now};
 for(const k of ['createdAt','updatedAt'])if(typeof out[k]!=='string'||!/^\d{4}-\d\d-\d\dT/.test(out[k])||!Number.isFinite(Date.parse(out[k])))throw Error('Invalid '+k+'.');
 if('contactConfig' in value)out.contactConfig=validateContact(value.contactConfig);
 if('caseConfig' in value)out.caseConfig=validateCase(value.caseConfig);
 if('motorConfig' in value)out.motorConfig=validateMotor(value.motorConfig);
 if('legacySolverConfig' in value)out.legacySolverConfig=validateConfig(value.legacySolverConfig,true);
 return out;
}
function baseline(){const now=new Date().toISOString();return {schema,id:id(),name:'V4 baseline / 150 mm square',params:{...Kinefold.defaults},view:{...viewDefaults},solverConfig:{...solverDefaults},createdAt:now,updatedAt:now};}
function decode(value){
 if(value?.schema==='kinefold/project-v2'){keys(value,['schema','id','name','params','view','solverConfig','createdAt','updatedAt'],'legacy project');const old=validateConfig(value.solverConfig,true),finite=['m2','m3','m5','m6'].some(k=>value.params?.[k]>0);return {project:validate({...value,schema,solverConfig:{...solverDefaults,inputRiseMm:finite?10:0},legacySolverConfig:old}),migrated:true,notice:'Fixed-hip project migrated to vertical-chassis dynamics. Geometry is unchanged; the previous profile is retained read-only. '+(finite?'A declared 10 mm finite transition was selected for the moving-mass design.':'The exact 150 mm square baseline uses zero added rotor inertia and damping.')};}
 if(value?.schema===Kinefold.schema){keys(value,['schema','name','params','view'],'legacy design');keys(value.params,Object.keys(Kinefold.defaults),'legacy parameter');const d=Kinefold.unpack(value),p=baseline();return {project:validate({...p,name:d.name,params:d.params,view:{...viewDefaults,...d.view},solverConfig:{...solverDefaults,inputRiseMm:['m2','m3','m5','m6'].some(k=>d.params[k]>0)?10:0}}),migrated:true,notice:'Legacy mechanism migrated with unchanged geometry and the new vertical-chassis input profile. Review and save the profile.'};}
 return {project:validate(value),migrated:false};
}
const content=p=>JSON.stringify([p.name,p.params,p.view,p.solverConfig,p.legacySolverConfig||null,p.contactConfig||null,p.caseConfig||null,p.motorConfig||null]);
function createStore(storage){
 let library=[],error='',notice='',libraryBlocked=false,persistedLibraryRaw=null;
 try{const currentRaw=storage.getItem(libraryKey),raw=currentRaw||storage.getItem('kinefold-library-v2');persistedLibraryRaw=currentRaw;if(raw){const data=JSON.parse(raw);keys(data,['schema','designs'],'library');if(!['kinefold/library-v3','kinefold/library-v2'].includes(data.schema)||!Array.isArray(data.designs)||data.designs.length>200)throw Error('Invalid library format.');library=data.designs.map(p=>decode(p).project);if(data.schema==='kinefold/library-v2')notice='Saved designs migrated to vertical-chassis profiles. Original v2 library data remains untouched; prior profiles are retained with each migrated design.';if(new Set(library.map(p=>p.id)).size!==library.length)throw Error('Duplicate design identifiers.');}}
 catch(e){error='Saved library could not be read: '+e.message+' Existing browser data was retained; export your working design before recovery.';libraryBlocked=true;}
 function writeLibrary(next){if(libraryBlocked)throw Error(error);if(storage.getItem(libraryKey)!==persistedLibraryRaw)throw Error('The saved library changed in another tab. Reload this page before saving; export your working copy first.');const raw=JSON.stringify({schema:'kinefold/library-v3',designs:next});storage.setItem(libraryKey,raw);persistedLibraryRaw=raw;library=next;}
 return {
  get error(){return error;},get notice(){return notice;},list:()=>clone(library),
  restore(){const raw=storage.getItem(workingKey)||storage.getItem('kinefold-project-v2')||storage.getItem('kinefold-design-v1');return raw?decode(JSON.parse(raw)):null;},
  autosave(project){storage.setItem(workingKey,JSON.stringify(validate(project)));},
  save(project){const p=validate(project),next=library.filter(x=>x.id!==p.id);if(next.length>=200)throw Error('Library limit is 200 designs. Export or remove a design first.');p.updatedAt=new Date().toISOString();next.push(p);writeLibrary(next);return clone(p);},
  remove(projectId){const found=library.find(p=>p.id===projectId);if(!found)throw Error('Design is no longer in this library.');writeLibrary(library.filter(p=>p.id!==projectId));return clone(found);},
  duplicate(project,name){return validate({...project,id:id(),name:title(name),createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()});}
 };
}
function createDiskStore(storage,request=async payload=>{
 const response=await fetch('/api/profiles',{method:'POST',headers:{'Content-Type':'application/json','X-Kinefold-Request':'coupled-dynamics'},body:JSON.stringify(payload),keepalive:JSON.stringify(payload).length<60000});
 let result;try{result=await response.json();}catch{throw Error('The profile server returned an unreadable response. Restart Kinefold and reload.');}
 if(!response.ok||!result.ok)throw Error(result.error||'Profile storage request failed.');return result;
}){
 let state={designs:[],working:null,revision:0},error='',notice='',initialized=false,blocked=false,pending=0,queue=Promise.resolve();
 const legacy=createStore(storage),legacyRestore=()=>legacy.restore();
 const adopt=result=>{if(!Array.isArray(result.designs)||!Number.isInteger(result.revision))throw Error('Invalid profile-server response.');const designs=result.designs.map(validate),working=result.working===null?null:validate(result.working);state={designs,working,revision:result.revision};};
 const ready=(async()=>{try{
  const disk=await request({action:'list'});adopt(disk);
  if(!disk.migrated){if(legacy.error)throw Error(legacy.error);const restored=legacyRestore(),browserBackup={};for(const key of ['kinefold-library-v3','kinefold-library-v2','kinefold-project-v3','kinefold-project-v2','kinefold-design-v1']){const raw=storage.getItem(key);if(raw!==null)browserBackup[key]=raw;}
   const migrated=await request({action:'migrate',expectedRevision:state.revision,designs:legacy.list(),working:restored?.project||null,browserBackup});adopt(migrated);
   notice=Object.keys(browserBackup).length?'Browser profiles and the exact working copy were copied to profiles/library.json. Original browser keys and profiles/browser-backup.json are retained unchanged.':'Profiles now save in this app’s profiles/ folder.';
  }else notice='Loaded profiles/library.json. App-folder profiles are authoritative. Older data in this browser was not imported again; use Recover browser profiles below to recover it without replacing current designs.';
  initialized=true;return store;
 }catch(e){error=e.message;blocked=true;throw e;}})();
 // Initialization is exposed through ready; attach a handler before later modules run.
 ready.catch(()=>{});
 function enqueue(action,values){pending++;const operation=queue.then(async()=>{await ready;if(blocked)throw Error(error||'Profile writes are blocked. Reload to recover.');const result=await request({action,expectedRevision:state.revision,...values});adopt(result);return result;});queue=operation.catch(e=>{error=e.message;blocked=true;}).finally(()=>{pending--;});return operation;}
 const store={ready,get pending(){return pending;},get initialized(){return initialized;},get error(){return error;},get notice(){return notice;},
  list:()=>clone(state.designs),restore:()=>initialized?(state.working?{project:clone(state.working),migrated:false}:null):legacyRestore(),
  committedWorking:()=>state.working?clone(state.working):null,
  async autosave(project){const p=validate(project);await enqueue('working',{project:p});return clone(p);},
  async save(project){const p=validate(project);p.updatedAt=new Date().toISOString();await enqueue('save',{project:p});return clone(p);},
  async remove(projectId){const found=state.designs.find(p=>p.id===projectId);if(!found)throw Error('Design is no longer in this library.');await enqueue('remove',{id:projectId});return clone(found);},
  duplicate:legacy.duplicate,
  async recoverBrowser(){await ready;if(legacy.error)throw Error(legacy.error);const old=legacy.list(),working=legacyRestore()?.project;if(working&&!old.some(p=>content(p)===content(working)))old.push({...working,name:(working.name+' · recovered working copy').slice(0,80)});let added=0;for(const project of old){if(state.designs.some(p=>content(p)===content(project)))continue;await store.save({...project,id:id(),name:project.name});added++;}return added;},
  async saveArtifact(filename,value,mime='application/json'){await ready;const content=typeof value==='string'?value:JSON.stringify(value,null,2)+'\n';const result=await request({action:'export',name:filename,content,mime});return result.path;}
 };return store;
}
return {schema,viewDefaults,solverDefaults,contactDefaults,caseDefaults,motorDefaults,validateMotor,validateCase,validateContact,validateConfig,validate,baseline,decode,clone,content,createStore,createDiskStore,id,title};
})();
