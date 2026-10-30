/** Pure periodic terrain configuration/geometry with an offline sheet catalog.
 * Load before project-store.js; init(catalog) in Node or load() in the browser.
 * Inputs: mm, sheet severity and obstacle/RMS representation. Outputs: strict
 * terrain-v1/v2 values and exact piecewise-linear statistics. Rigid 2D proxy only.
 */
globalThis.KinefoldTerrainProfiles=(()=>{
'use strict';
const schema='kinefold/terrain-v1',schemaV2='kinefold/terrain-v2',revision='2026-10-29',segments=96;
let catalog=null,pending=null;
const clone=v=>JSON.parse(JSON.stringify(v));
function init(value){if(value?.schema!=='kinefold/terrain-catalog-v1'||value.revision!==revision||value.profiles?.length!==16)throw Error('Unknown terrain catalog.');catalog=clone(value);return clone(catalog);}
async function load(){if(catalog)return clone(catalog);pending||=fetch('terrain-catalog.json').then(r=>{if(!r.ok)throw Error('Terrain catalog unavailable.');return r.json();}).then(init);return pending;}
function validate(v){
 const v2=v?.schema===schemaV2,keys=['schema','catalogRevision','profileId','severity','representation','periodMm','heightMm','rmsMm',...(v2?['seed','variationPercent','gradePercent']:[])];
 if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).length!==keys.length||keys.some(k=>!Object.hasOwn(v,k)))throw Error('Unknown or missing terrain settings.');
 if(![schema,schemaV2].includes(v.schema)||v.catalogRevision!==revision||typeof v.profileId!=='string'||!/^[a-z0-9-]{1,100}$/.test(v.profileId)||catalog&&!catalog.profiles.some(p=>p.id===v.profileId))throw Error('Unknown terrain schema, catalog or source profile.');
 if(!['typical','difficult','extreme'].includes(v.severity)||!['obstacles','roughness'].includes(v.representation))throw Error('Choose terrain severity and representation.');
 for(const [k,lo,hi]of [['periodMm',100,100000],['heightMm',0,1000],['rmsMm',0,1000]]){if(k!=='periodMm'&&v[k]===null)continue;if(!Number.isFinite(v[k])||v[k]<lo||v[k]>hi)throw Error(k+' is outside its finite terrain range.');}
 if(v[v.representation==='obstacles'?'heightMm':'rmsMm']===null)throw Error('This source metric is unresolved for the selected terrain/severity.');
 if(v2){if(!Number.isInteger(v.seed)||v.seed<0||v.seed>0xffffffff)throw Error('Terrain seed must be a uint32 integer.');for(const [k,lo,hi]of [['variationPercent',0,50],['gradePercent',-100,100]])if(!Number.isFinite(v[k])||v[k]<lo||v[k]>hi)throw Error(k+' is outside its finite terrain range.');}
 return clone(v);
}
function profile(id){if(!catalog)throw Error('Terrain catalog is loading.');const p=catalog.profiles.find(p=>p.id===id);if(!p)throw Error('Choose a source terrain.');return clone(p);}
function config(id,severity='typical',representation='obstacles',periodMm=null){const p=profile(id),spacing=p.obstacleSpacingM[severity]??(severity==='extreme'?p.obstacleSpacingM.difficult:null);return validate({schema,catalogRevision:revision,profileId:id,severity,representation,periodMm:periodMm??(spacing===null?NaN:spacing*1000),heightMm:p.obstacleMm[severity],rmsMm:p.rmsMm[severity]});}
function contour(value,cycle=0){const c=validate(value);if(c.schema===schemaV2)return randomContour(c,cycle);const rough=c.representation==='roughness',ys=[];for(let i=0;i<=segments;i++){const p=i/segments;ys.push(rough?1-Math.cos(2*Math.PI*p):(p>.25&&p<.75?.5*(1-Math.cos(4*Math.PI*(p-.25))):0));}
 const moments=ys=>{let mean=0,second=0;for(let i=0;i<segments;i++){const a=ys[i],b=ys[i+1];mean+=(a+b)/2/segments;second+=(a*a+a*b+b*b)/3/segments;}return [mean,second];};
 const [mu,sq]=moments(ys),scale=rough?c.rmsMm/Math.sqrt(sq-mu*mu):c.heightMm;const values=ys.map(y=>y*scale),[mean,second]=moments(values);
 return {pointsMm:values.map((y,i)=>[i*c.periodMm/segments,y]),peakMm:Math.max(...values),meanMm:mean,rmsMm:Math.sqrt(Math.max(0,second-mean*mean)),periodMm:c.periodMm,segmentsPerPeriod:segments,maxLocalGradePercent:Math.max(...values.slice(1).map((v,i)=>Math.abs(v-values[i])/(c.periodMm/segments)*100))};
}
function at(value,distanceMm){const c=validate(value);if(c.schema===schemaV2){const cycle=Math.floor(distanceMm/c.periodMm),wave=contour(c,cycle),phase=(distanceMm-cycle*c.periodMm)/c.periodMm*segments,i=Math.min(segments-1,Math.floor(phase)),u=phase-i;return wave.pointsMm[i][1]*(1-u)+wave.pointsMm[i+1][1]*u;}const wave=contour(c),p=((distanceMm%wave.periodMm)+wave.periodMm)%wave.periodMm/ wave.periodMm*segments,i=Math.floor(p),u=p-i;return wave.pointsMm[i][1]*(1-u)+wave.pointsMm[i+1][1]*u;}
function configV2(id,severity='typical',representation='obstacles',periodMm=null,options={}){return validate({...config(id,severity,representation,periodMm),schema:schemaV2,seed:481,variationPercent:20,gradePercent:profile(id).gradePercent[severity],...options});}
function randomUnit(seed,cycle,channel){let x=(seed^Math.imul(cycle,0x9e3779b1)^Math.imul(channel,0x85ebca77))>>>0;x=(x^(x>>>16))>>>0;x=Math.imul(x,0x7feb352d)>>>0;x=(x^(x>>>15))>>>0;x=Math.imul(x,0x846ca68b)>>>0;x=(x^(x>>>16))>>>0;return x/4294967296;}
function moments(points){const width=points.at(-1)[0]-points[0][0];let mean=0,second=0;for(let i=0;i<points.length-1;i++){const [x,a]=points[i],[y,b]=points[i+1],w=(y-x)/width;mean+=(a+b)/2*w;second+=(a*a+a*b+b*b)/3*w;}return [mean,Math.sqrt(Math.max(0,second-mean*mean))];}
function randomContour(c,cycle){
 if(!Number.isInteger(cycle)||cycle<-2147483648||cycle>2147483647)throw Error('Cycle index must be a signed int32.');
 const {seed,variationPercent,gradePercent,...base}=c;base.schema=schema;const old=contour(base),variation=variationPercent/100,period=c.periodMm;
 let heights,center,width,asymmetry,amplitude;
 if(variation===0){heights=old.pointsMm.map(p=>p[1]);center=.5;width=c.representation==='roughness'?1:.5;asymmetry=.5;amplitude=1;}
 else{
  const rand=channel=>2*randomUnit(seed,cycle,channel)-1,rough=c.representation==='roughness',guard=2/segments;
  width=Math.min(1-2*guard,rough?1-variation*(.4+.2*rand(2)):.5*(1+variation*.4*rand(2)));
  center=Math.max(width/2+guard,Math.min(1-width/2-guard,.5+.16*variation*rand(1)));
  asymmetry=.5+.25*variation*rand(3);amplitude=1+variation*rand(4);heights=[];
  for(let i=0;i<=segments;i++){const t=(i/segments-center+width/2)/width;if(t<=0||t>=1){heights.push(0);continue;}const u=t<=asymmetry?t/(2*asymmetry):.5+(t-asymmetry)/(2*(1-asymmetry));heights.push(.5*(1-Math.cos(2*Math.PI*u)));}
  const unitPoints=heights.map((y,i)=>[i*period/segments,y]),scale=(rough?c.rmsMm/moments(unitPoints)[1]:c.heightMm/Math.max(...heights))*amplitude;heights=heights.map(y=>y*scale);
 }
 const roughnessPointsMm=heights.map((y,i)=>[i*period/segments,y]),grade=gradePercent/100,baselinePointsMm=roughnessPointsMm.map(([x])=>[x,grade*(cycle*period+x)]),pointsMm=roughnessPointsMm.map(([x,y],i)=>[x,y+baselinePointsMm[i][1]]),[meanMm,rmsMm]=moments(roughnessPointsMm);
 return {pointsMm,roughnessPointsMm,baselinePointsMm,peakMm:Math.max(...heights),meanMm,rmsMm,periodMm:period,segmentsPerPeriod:segments,maxLocalGradePercent:Math.max(...pointsMm.slice(1).map((b,i)=>Math.abs(b[1]-pointsMm[i][1])/(b[0]-pointsMm[i][0])*100)),gradePercent,gradeDegrees:Math.atan(grade)*180/Math.PI,cycleIndex:cycle,seed,variationPercent,shape:{centerFraction:center,widthFraction:width,peakFraction:asymmetry,amplitudeFactor:amplitude}};
}
function sequence(value,count=3,startCycle=0){
 const c=validate(value);if(!Number.isInteger(count)||count<1||count>52)throw Error('Sequence count must be 1–52 cells.');if(!Number.isInteger(startCycle)||startCycle<-2147483648||startCycle>2147483647-count+1)throw Error('Sequence start must keep all cycle indices within int32.');
 const cells=Array.from({length:count},(_,i)=>contour(c,startCycle+i)),pointsMm=[],roughnessPointsMm=[],baselinePointsMm=[];
 for(let n=0;n<cells.length;n++){const cell=cells[n],cycle=startCycle+n;for(let i=0;i<cell.pointsMm.length;i++){if(n&&i===0)continue;const [x,y]=cell.pointsMm[i],absolute=cycle*c.periodMm+x;pointsMm.push([absolute,y]);roughnessPointsMm.push([absolute,(cell.roughnessPointsMm||cell.pointsMm)[i][1]]);baselinePointsMm.push([absolute,cell.baselinePointsMm?.[i][1]||0]);}}
 const [meanMm,rmsMm]=moments(roughnessPointsMm),gradePercent=c.gradePercent||0;
 return {pointsMm,roughnessPointsMm,baselinePointsMm,cells,cellCount:count,startCycle,spanMm:count*c.periodMm,peakMm:Math.max(...roughnessPointsMm.map(p=>p[1])),meanMm,rmsMm,detrendedRmsMm:rmsMm,minHeightMm:Math.min(...pointsMm.map(p=>p[1])),maxHeightMm:Math.max(...pointsMm.map(p=>p[1])),gradePercent,gradeDegrees:Math.atan(gradePercent/100)*180/Math.PI,seed:c.seed??null,variationPercent:c.variationPercent||0,periodMm:c.periodMm};
}
function shortRun(value,solver){const c=validate(value);if(c.periodMm/6>10000)throw Error('The 6 s repeat exceeds the 10000 mm/s speed bound. Apply at entered speed instead.');return {...solver,inputSpeedMmS:c.periodMm/6,inputDelayS:.5,duration:6.5,inputRiseMm:0};}
return {schema,schemaV2,revision,segments,init,load,validate,profile,config,configV2,contour,sequence,randomUnit,at,shortRun,get catalog(){return catalog?clone(catalog):null;}};
})();
