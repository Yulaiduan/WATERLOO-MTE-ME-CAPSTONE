/** Pure periodic terrain configuration/geometry with an offline sheet catalog.
 * Load before project-store.js; init(catalog) in Node or load() in the browser.
 * Inputs: mm, sheet severity and obstacle/RMS representation. Outputs: strict
 * terrain-v1 values and exact piecewise-linear statistics. Rigid 2D proxy only.
 */
globalThis.KinefoldTerrainProfiles=(()=>{
'use strict';
const schema='kinefold/terrain-v1',revision='2026-10-29',segments=96;
let catalog=null,pending=null;
const clone=v=>JSON.parse(JSON.stringify(v));
function init(value){if(value?.schema!=='kinefold/terrain-catalog-v1'||value.revision!==revision||value.profiles?.length!==16)throw Error('Unknown terrain catalog.');catalog=clone(value);return clone(catalog);}
async function load(){if(catalog)return clone(catalog);pending||=fetch('terrain-catalog.json').then(r=>{if(!r.ok)throw Error('Terrain catalog unavailable.');return r.json();}).then(init);return pending;}
function validate(v){
 const keys=['schema','catalogRevision','profileId','severity','representation','periodMm','heightMm','rmsMm'];
 if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).length!==keys.length||keys.some(k=>!Object.hasOwn(v,k)))throw Error('Unknown or missing terrain settings.');
 if(v.schema!==schema||v.catalogRevision!==revision||typeof v.profileId!=='string'||!/^[a-z0-9-]{1,100}$/.test(v.profileId)||catalog&&!catalog.profiles.some(p=>p.id===v.profileId))throw Error('Unknown terrain schema, catalog or source profile.');
 if(!['typical','difficult','extreme'].includes(v.severity)||!['obstacles','roughness'].includes(v.representation))throw Error('Choose terrain severity and representation.');
 for(const [k,lo,hi]of [['periodMm',100,100000],['heightMm',0,1000],['rmsMm',0,1000]]){if(k!=='periodMm'&&v[k]===null)continue;if(!Number.isFinite(v[k])||v[k]<lo||v[k]>hi)throw Error(k+' is outside its finite terrain range.');}
 if(v[v.representation==='obstacles'?'heightMm':'rmsMm']===null)throw Error('This source metric is unresolved for the selected terrain/severity.');
 return clone(v);
}
function profile(id){if(!catalog)throw Error('Terrain catalog is loading.');const p=catalog.profiles.find(p=>p.id===id);if(!p)throw Error('Choose a source terrain.');return clone(p);}
function config(id,severity='typical',representation='obstacles',periodMm=null){const p=profile(id),spacing=p.obstacleSpacingM[severity]??(severity==='extreme'?p.obstacleSpacingM.difficult:null);return validate({schema,catalogRevision:revision,profileId:id,severity,representation,periodMm:periodMm??(spacing===null?NaN:spacing*1000),heightMm:p.obstacleMm[severity],rmsMm:p.rmsMm[severity]});}
function contour(value){const c=validate(value),rough=c.representation==='roughness',ys=[];for(let i=0;i<=segments;i++){const p=i/segments;ys.push(rough?1-Math.cos(2*Math.PI*p):(p>.25&&p<.75?.5*(1-Math.cos(4*Math.PI*(p-.25))):0));}
 const moments=ys=>{let mean=0,second=0;for(let i=0;i<segments;i++){const a=ys[i],b=ys[i+1];mean+=(a+b)/2/segments;second+=(a*a+a*b+b*b)/3/segments;}return [mean,second];};
 const [mu,sq]=moments(ys),scale=rough?c.rmsMm/Math.sqrt(sq-mu*mu):c.heightMm;const values=ys.map(y=>y*scale),[mean,second]=moments(values);
 return {pointsMm:values.map((y,i)=>[i*c.periodMm/segments,y]),peakMm:Math.max(...values),meanMm:mean,rmsMm:Math.sqrt(Math.max(0,second-mean*mean)),periodMm:c.periodMm,segmentsPerPeriod:segments,maxLocalGradePercent:Math.max(...values.slice(1).map((v,i)=>Math.abs(v-values[i])/(c.periodMm/segments)*100))};
}
function at(value,distanceMm){const wave=contour(value),p=((distanceMm%wave.periodMm)+wave.periodMm)%wave.periodMm/ wave.periodMm*segments,i=Math.floor(p),u=p-i;return wave.pointsMm[i][1]*(1-u)+wave.pointsMm[i+1][1]*u;}
function shortRun(value,solver){const c=validate(value);if(c.periodMm/6>10000)throw Error('The 6 s repeat exceeds the 10000 mm/s speed bound. Apply at entered speed instead.');return {...solver,inputSpeedMmS:c.periodMm/6,inputDelayS:.5,duration:6.5,inputRiseMm:0};}
return {schema,revision,segments,init,load,validate,profile,config,contour,at,shortRun,get catalog(){return catalog?clone(catalog):null;}};
})();
