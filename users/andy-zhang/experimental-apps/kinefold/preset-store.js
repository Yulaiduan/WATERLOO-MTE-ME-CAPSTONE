/** Independent component/study presets and optimistic app-folder persistence.
 * Load after project-store.js (model/variables required). Browser API; verify with
 * node verify-presets.cjs. Inputs retain builder mm/deg/kg/N and solver/motor SI
 * units; outputs are cloned validated records/projects and disk-library replies.
 * Studies freeze component snapshots. Unknown passive terms block composition
 * until explicitly idealized; catalog ratings never change controller commands.
 */
globalThis.KinefoldPresets=(()=>{
'use strict';
const P=KinefoldProjects,schema='kinefold/preset-library-v1',bundleSchema='kinefold/preset-bundle-v1';
const optional=['contactConfig','caseConfig','energyConfig','torqueTargetConfig','terrainConfig'];
const unknownKeys=['rotorInertiaKgM2','coggingAmplitudeNm','coulombFrictionNm','viscousFrictionNms'];
const ratingKeys=['peakShaftNm','maxShaftRpm','gearboxContinuousNm','gearboxPeakNm'];
const clone=P.clone;
function finiteTree(v,depth=0){
 if(depth>16)throw Error('Preset nesting exceeds the storage limit.');
 if(v===null||typeof v==='boolean')return;
 if(typeof v==='number'){if(!Number.isFinite(v)||Math.abs(v)>1e12)throw Error('Preset numbers must be finite and bounded.');return;}
 if(typeof v==='string'){if(v.length>2000)throw Error('Preset string exceeds the storage limit.');return;}
 if(Array.isArray(v)){if(v.length>200)throw Error('Too many preset records.');for(const x of v)finiteTree(x,depth+1);return;}
 if(!v||typeof v!=='object'||Object.getPrototypeOf(v)!==Object.prototype)throw Error('Preset values must be plain JSON.');
 if(Object.keys(v).length>200)throw Error('Too many preset fields.');
 for(const [k,x]of Object.entries(v)){if(['__proto__','prototype','constructor'].includes(k))throw Error('Unsafe preset field.');finiteTree(x,depth+1);}
}
function keys(v,required,label,extra=[]){if(!v||typeof v!=='object'||Array.isArray(v))throw Error(label+' must be an object.');if(required.some(k=>!Object.hasOwn(v,k))||Object.keys(v).some(k=>![...required,...extra].includes(k)))throw Error('Unknown or missing '+label+' fields.');}
function stamp(v){if(typeof v!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(v)||!Number.isFinite(Date.parse(v))||new Date(v).toISOString()!==v)throw Error('Preset timestamps must use canonical UTC ISO milliseconds.');}
function identifier(v){if(typeof v!=='string'||!/^preset-[a-zA-Z0-9-]{1,100}$/.test(v))throw Error('Invalid preset identifier.');}
function newId(){return 'preset-'+P.id().slice(7);}
function values(kind,v){
 if(kind==='suspension'){
  keys(v,['params'],'suspension values');P.validate({...P.baseline(),params:v.params});
 }else if(kind==='input'){
  keys(v,['solverConfig'],'input values',optional);const fixture={...P.baseline(),...v};P.validate(fixture);
 }else if(kind==='actuator'){
  keys(v,['motorConfig','ratings','unknownFields','idealizeUnknowns','catalog'],'actuator values');P.validateMotor(v.motorConfig);if(v.motorConfig.enabled!==true)throw Error('An actuator preset must contain an enabled motor model.');
  keys(v.ratings,ratingKeys,'actuator ratings');for(const k of ratingKeys){const n=v.ratings[k];if(n!==null&&(!Number.isFinite(n)||n<0||(k==='maxShaftRpm'&&n===0)))throw Error('Rating '+k+' must be unknown or finite '+(k==='maxShaftRpm'?'positive.':'nonnegative.'));}
  if(!Array.isArray(v.unknownFields)||v.unknownFields.some(k=>!unknownKeys.includes(k))||new Set(v.unknownFields).size!==v.unknownFields.length)throw Error('Unknown passive fields must be distinct documented motor keys.');
  if(typeof v.idealizeUnknowns!=='boolean'||v.unknownFields.some(k=>v.motorConfig[k]!==0))throw Error('Unknown passive terms require zero placeholders and an explicit idealization flag.');
  keys(v.catalog,['motorId','gearboxId','notes'],'catalog');if(Object.values(v.catalog).some(x=>typeof x!=='string'))throw Error('Catalog provenance must contain strings.');
 }else if(kind==='study'){
  keys(v,['suspension','input','actuators','sweep'],'study values');
  for(const [k,type]of [['suspension','suspension'],['input','input']])if(validateRecord(v[k]).kind!==type)throw Error('Study requires a '+type+' snapshot.');
  if(!Array.isArray(v.actuators)||v.actuators.length<1||v.actuators.length>40)throw Error('Study requires 1–40 actuator snapshots.');
  for(const r of v.actuators)if(validateRecord(r).kind!=='actuator')throw Error('Study actuator snapshots cannot contain other kinds.');
  if(new Set(v.actuators.map(r=>r.id)).size!==v.actuators.length)throw Error('Study actuators must have distinct identifiers.');
  validateSweep(v.sweep);
 }else throw Error('Unknown preset kind.');
 return clone(v);
}
function validateSweep(v){keys(v,['maxJointSpeedRadS','jointAccelerationRadS2','samples'],'sweep');if(!Number.isFinite(v.maxJointSpeedRadS)||v.maxJointSpeedRadS<=0||v.maxJointSpeedRadS>100||!Number.isFinite(v.jointAccelerationRadS2)||Math.abs(v.jointAccelerationRadS2)>1000||!Number.isInteger(v.samples)||v.samples<11||v.samples>101||v.samples%2!==1)throw Error('Sweep requires speed (0,100] rad/s, acceleration ±1000 rad/s² and odd 11–101 samples.');return clone(v);}
function validateRecord(r){finiteTree(r);keys(r,['id','kind','name','version','createdAt','updatedAt','values'],'preset');identifier(r.id);P.title(r.name);if(!Number.isInteger(r.version)||r.version<1||r.version>Number.MAX_SAFE_INTEGER)throw Error('Preset version must be a positive safe integer.');stamp(r.createdAt);stamp(r.updatedAt);if(Date.parse(r.updatedAt)<Date.parse(r.createdAt))throw Error('Preset updated time precedes creation.');return {...clone(r),values:values(r.kind,r.values)};}
function validateLibrary(v){finiteTree(v);keys(v,['schema','revision','presets'],'preset library');if(v.schema!==schema||!Number.isSafeInteger(v.revision)||v.revision<0||!Array.isArray(v.presets)||v.presets.length>200)throw Error('Invalid preset library metadata.');const out={schema,revision:v.revision,presets:v.presets.map(validateRecord)};if(new Set(out.presets.map(r=>r.id)).size!==out.presets.length)throw Error('Duplicate preset identifiers.');return out;}
function make(kind,name,v,existing){const old=existing?validateRecord(existing):null;if(old&&(old.kind!==kind||kind==='study'))throw Error('Studies are immutable; create a new study copy.');const now=new Date().toISOString();return validateRecord({id:old?.id||newId(),kind,name:P.title(name),version:old?old.version+1:1,createdAt:old?.createdAt||now,updatedAt:now,values:v});}
function captureSuspension(project){return {params:clone(P.validate(project).params)};}
function captureInput(project){const p=P.validate(project),v={solverConfig:p.solverConfig};for(const k of optional)if(k in p)v[k]=p[k];return clone(v);}
function captureActuator(project){const p=P.validate(project),active=p.motorConfig?.enabled===true;return {motorConfig:clone(active?p.motorConfig:{...P.motorDefaults,enabled:true}),ratings:Object.fromEntries(ratingKeys.map(k=>[k,null])),unknownFields:[],idealizeUnknowns:false,catalog:{motorId:'captured-input',gearboxId:'captured-input',notes:active?'Captured enabled saved model inputs, not measured hardware data.':'Captured current ideal actuator model; compatibility zeros, not measured motor data; inactive stored motor values not applied.'}};}
function assertRunnableActuator(record){const r=validateRecord(record);if(r.kind!=='actuator')throw Error('Choose an actuator preset.');if(r.values.unknownFields.length&&!r.values.idealizeUnknowns)throw Error('Unknown passive motor terms: '+r.values.unknownFields.join(', ')+'. Explicitly treat unknown passive terms as ideal zero for this study before composing or running.');return r;}
function compose(base,suspension,actuator,input){const p=P.validate(base),s=validateRecord(suspension),a=assertRunnableActuator(actuator),i=validateRecord(input);if(s.kind!=='suspension'||i.kind!=='input')throw Error('Composition requires suspension, actuator and input presets.');for(const k of [...optional,'legacySolverConfig'])delete p[k];Object.assign(p,clone(i.values),{params:clone(s.values.params),motorConfig:{...a.values.motorConfig,enabled:true},id:P.id(),name:P.title((s.name+' · '+a.name+' · '+i.name).slice(0,80)),createdAt:new Date().toISOString(),updatedAt:new Date().toISOString()});return P.validate(p);}
function bundle(records){const library=validateLibrary({schema,revision:0,presets:records});return {schema:bundleSchema,presets:library.presets};}
function validateBundle(v){finiteTree(v);keys(v,['schema','presets'],'preset bundle');if(v.schema!==bundleSchema)throw Error('Unsupported preset bundle.');return bundle(v.presets);}
async function defaultRequest(payload){const response=await fetch('/api/profiles',{method:'POST',headers:{'Content-Type':'application/json','X-Kinefold-Request':'coupled-dynamics'},body:JSON.stringify(payload)});let result;try{result=await response.json();}catch{throw Error('Preset server returned an unreadable response. Reload after restarting Kinefold.');}if(!response.ok||!result.ok)throw Error(result.error||'Preset storage request failed.');return result;}
function createStore(request=defaultRequest){
 let state={schema,revision:0,presets:[]},error='',blocked=false,pending=0,queue=Promise.resolve();
 function adopt(reply){if(!reply||reply.ok!==true)throw Error(reply?.error||'Invalid preset server response.');const {ok,...library}=reply;const next=validateLibrary(library);state=next;return clone(state);}
 const ready=request({action:'preset-list'}).then(adopt).catch(e=>{error=e.message;blocked=true;throw e;});ready.catch(()=>{});
 function enqueue(action,data){pending++;const operation=queue.then(async()=>{await ready;if(blocked)throw Error(error||'Preset writes are blocked until reload.');return adopt(await request({action,expectedRevision:state.revision,...data}));});queue=operation.catch(e=>{blocked=true;error=e.message;}).finally(()=>{pending--;});return operation;}
 return {ready,list:()=>clone(state.presets),get revision(){return state.revision;},get pending(){return pending;},get blocked(){return blocked;},get error(){return error;},save(record){return enqueue('preset-save',{record:validateRecord(record)});},remove(id){identifier(id);return enqueue('preset-remove',{id});},importBundle(v){return enqueue('preset-import',{bundle:validateBundle(v)});}};
}
return {schema,bundleSchema,unknownKeys,ratingKeys,make,validateRecord,validateLibrary,validateBundle,validateSweep,captureSuspension,captureInput,captureActuator,assertRunnableActuator,compose,createStore,bundle};
})();
