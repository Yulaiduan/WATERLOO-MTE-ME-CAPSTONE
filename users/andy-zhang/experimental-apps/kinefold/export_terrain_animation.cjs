/** Rasterize exact saved analytical/Pymunk terrain frames with one clock/camera.
 * Run via encode_terrain_animation.py, or node export_terrain_animation.cjs
 * --analytical CAPTURE --pymunk CAPTURE --frames-dir DIR [--fps 20] [--label TEXT].
 * Inputs: captured requests/results in world mm/deg and SI telemetry; optional
 * --sharp-module selects an installed Sharp module (otherwise require('sharp')).
 * Outputs: PNG frame cache and small render-manifest.json; no physics, browser,
 * live design writes or trajectory interpolation. Geometry uses the app's
 * spring/transmission helpers. Chassis/spring package sizes are schematic.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const APP=__dirname,RENDER_FILES=['reference-v4.js','model.js','preview-geometry.js','contact-render.js'];
const C={paper:'#fffdf7',line:'#e4e7db',sage:'#526941','sage-soft':'#e8edde',ink:'#303c31',blue:'#37839a',amber:'#a57b17',muted:'#737a68',red:'#bd5743',soft:'#edf0e7'};
const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const fmt=(x,n=2)=>Number.isFinite(x)?x.toFixed(n):'—';
const canonical=x=>JSON.stringify(x,(key,value)=>value&&typeof value==='object'&&!Array.isArray(value)?Object.fromEntries(Object.entries(value).sort(([a],[b])=>a.localeCompare(b))):value);
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
function args(argv){const out={fps:20,label:'Saved terrain comparison'};for(let i=0;i<argv.length;i+=2){const key=argv[i];if(!key.startsWith('--')||argv[i+1]===undefined)throw Error('Each --option needs one value.');out[key.slice(2)]=argv[i+1];}out.fps=Number(out.fps);if(!Number.isInteger(out.fps)||out.fps<5||out.fps>30)throw Error('fps must be an integer from5to30.');for(const key of ['analytical','pymunk','frames-dir'])if(!out[key])throw Error('Missing --'+key);return out;}
function settings(payload){const {engine,...rest}=payload;return canonical(rest);}
function readCapture(file,engine){const capture=JSON.parse(fs.readFileSync(file,'utf8'));const p=capture.payload,r=capture.result;
  assert.equal(p?.engine,engine,'Capture engine');assert.equal(r?.engine,engine,'Result engine');assert.equal(p.caseConfig?.kind,'terrain-stability','Terrain captures only');
  assert.ok(r.rows?.length>=2&&r.rows.length===r.frames?.length,'Actual matched row/frame arrays required');assert.equal(canonical(r.params),canonical(p.params),'Result params must match capture');
  for(const key of ['params','runConfig','contactConfig','caseConfig','motorConfig','terrainConfig','actuatorConfig'])if(Object.hasOwn(p,key))assert.equal(canonical(r.snapshot?.[key==='runConfig'?'solverConfig':key]),canonical(p[key]),'Saved result snapshot differs: '+key);
  for(let i=0;i<r.rows.length;i++){const row=r.rows[i],f=r.frames[i];assert.ok(Number.isFinite(row.t)&&Math.abs(row.t-f.t)<1e-8,'Row/frame clock');if(i)assert.ok(row.t>r.rows[i-1].t,'Strictly increasing clock');for(const key of ['A','B','C'])assert.ok(f[key]?.length===3&&f[key].every(Number.isFinite),'Finite actual geometry');assert.ok(f.terrainOffsetMm?.every(Number.isFinite),'Actual terrain offset');}
  assert.ok(r.terrain?.contourMm?.length>=2,'Captured terrain contour required');return {capture,payload:p,result:r,file};
}
function selectIndex(rows,t){let lo=0,hi=rows.length;while(lo<hi){const mid=(lo+hi)>>1;if(rows[mid].t<=t+1e-9)lo=mid+1;else hi=mid;}return Math.max(0,lo-1);}
function camera(records,D){let minX=Infinity,maxX=-Infinity,minZ=-100,maxZ=0;for(const record of records){const p=record.payload.params;for(const f of record.result.frames){const spring=D.spring(p,f);assert.ok(!spring.enabled||spring.valid,'Saved spring geometry must be drawable');const points=[f.A,f.B,f.C,...(spring.assemblyPoints||[]),...(spring.valid?[spring.D,spring.Q,spring.S]:[])];for(const v of points){minX=Math.min(minX,v[0]-65);maxX=Math.max(maxX,v[0]+65);maxZ=Math.max(maxZ,v[2]+65);}minX=Math.min(minX,f.C[0]-p.rw-75);maxX=Math.max(maxX,f.C[0]+p.rw+75);maxZ=Math.max(maxZ,f.C[2]+p.rw+65);}}
  return {minX,maxX,minZ,maxZ};}
function text(x,y,value,size=18,color=C.ink,extra=''){return `<text x="${x}" y="${y}" font-size="${size}" fill="${color}" ${extra}>${esc(value)}</text>`;}
function panel(record,i,index,b,D,T){const p=record.payload.params,r=record.result,f=r.frames[index],row=r.rows[index];const x=20+i*550,y=170,w=530,h=520;const scale=Math.min((w-50)/(b.maxX-b.minX),(h-40)/(b.maxZ-b.minZ));
  const P=v=>[x+w/2-(v[0]-(b.minX+b.maxX)/2)*scale,y+h/2-(v[2]-(b.minZ+b.maxZ)/2)*scale];
  const line=(points,color,width=1,extra='')=>`<path d="${points.map((v,j)=>(j?'L':'M')+P(v).map(n=>n.toFixed(3)).join(',')).join(' ')}" fill="none" stroke="${color}" stroke-width="${width}" ${extra}/>`;
  const circle=(v,radius,color,width=1,fill='none')=>`<circle cx="${P(v)[0]}" cy="${P(v)[1]}" r="${radius*scale}" fill="${fill}" stroke="${color}" stroke-width="${width}"/>`;
  let svg=text(x+12,151,i?'Pymunk · actual bodies':'Analytical · finite-link contact',23,i?C.blue:C.sage,'font-weight="600"');
  svg+=`<defs><clipPath id="panel${i}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8"/></clipPath></defs><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="${C.paper}" stroke="${C.line}"/><g clip-path="url(#panel${i})">`;
  for(let gx=Math.ceil(b.minX/100)*100;gx<=b.maxX;gx+=100)svg+=line([[gx,0,b.minZ],[gx,0,b.maxZ]],C.line,gx%500===0?1.2:.65);
  for(let z=Math.ceil(b.minZ/100)*100;z<=b.maxZ;z+=100)svg+=line([[b.minX,0,z],[b.maxX,0,z]],C.line,z%500===0?1.2:.65);
  const offset=f.terrainOffsetMm,top=r.terrain.contourMm.map(v=>v.map((n,k)=>n+offset[k]));
  const polygon=[...top,[top.at(-1)[0],0,b.minZ-500],[top[0][0],0,b.minZ-500]];
  svg+=`<polygon points="${polygon.map(v=>P(v).join(',')).join(' ')}" fill="${C['sage-soft']}"/>`+line(top,C.sage,2.6);
  // Material dots are visual indices on the captured contour, not new collisions.
  for(let n=0;n<top.length;n+=8)if(top[n][0]>=b.minX&&top[n][0]<=b.maxX)svg+=circle(top[n],3,C.muted,.5,C.muted);
  const target=[f.A[0],0,row.rideTargetHeightMm];if(Number.isFinite(target[2]))svg+=line([[b.minX,0,target[2]],[b.maxX,0,target[2]]],C.muted,1.1,'stroke-dasharray="6 5"');
  svg+=line([f.A,f.B],C.sage,9)+line([f.B,f.C],C.blue,8)+circle(f.C,p.rw,C.ink,2.6,C.paper);
  const drawing=T.transmission(p,f);for(const belt of drawing.stages){assert.ok(belt.valid,'Actual transmission geometry');svg+=line(belt.outline,C.muted,1.1);for(const v of belt.markers){const [px,py]=P(v);svg+=`<circle cx="${px}" cy="${py}" r="1.6" fill="${C.sage}"/>`;}}
  for(const a of drawing.indices)svg+=circle(a.centre,a.radius,C.amber,1.1)+line([a.centre,a.primary],C.red,1.5)+line([a.centre,a.secondary],C.red,.8,'stroke-dasharray="3 3"');
  const spring=D.spring(p,f);if(spring.valid){svg+=line([spring.A,spring.D],C.amber,3)+line([spring.D,spring.Q],C.amber,2)+line(spring.arc,C.amber,2.2)+line([spring.out,spring.remote],C.amber,1.2)+circle(spring.S,p.rs,C.amber,1);for(const bar of [spring.fixedBar,spring.movingBar])svg+=line(bar,C.amber,3);svg+=line(spring.wire,C.amber,1.4);for(let side=0;side<2;side++)svg+=line([spring.rails[0][side],spring.rails[1][side]],C.amber,.8,'opacity=".4"');}
  const [ax,ay]=P(f.A);svg+=`<rect x="${ax-38}" y="${ay-29}" width="76" height="24" rx="4" fill="${C.soft}" stroke="${C.sage}"/>`+text(ax,ay-12,`${fmt(p.m1,2)} kg`,13,C.ink,'text-anchor="middle"');
  for(const [label,v] of [['A',f.A],['B',f.B],['C',f.C]]){const a=P(v);svg+=text(a[0]+(label==='A'?-44:10),a[1]+(label==='A'?22:-8),label,16);}
  if(Number.isFinite(r.caseConfig.undersideOffsetMm))svg+=line([f.A,[f.A[0],0,f.A[2]-r.caseConfig.undersideOffsetMm]],C.red,1,'stroke-dasharray="3 3"');
  svg+='</g>';
  svg+=`<path d="M${x+85} ${y+h-23}h-44m7-5-7 5 7 5M${x+85} ${y+h-23}v-40m-5 8 5-8 5 8" fill="none" stroke="${C.ink}" stroke-width="1.5"/>`+text(x+20,y+h-17,'+x',16,C.red)+text(x+95,y+h-55,'+z',16,C.blue);
  svg+=text(x+13,724,`Height ${fmt(row.chassisZMm,1)} mm · error ${fmt(row.chassisZMm-row.rideTargetHeightMm,2)} mm`,18);
  svg+=text(x+13,756,r.runConfig.fixture==='pinned-chassis'?`Pin +z ${Number.isFinite(row.pinForceZN)?fmt(row.pinForceZN,1):'unavailable'} N · motor ${fmt(row.motorTorqueNm,1)} N m`:`Motor ${fmt(row.motorTorqueNm,1)} N m · spring ${fmt(row.Fs,1)} N`,18);
  svg+=text(x+13,788,`Wheel ${fmt(row.wheelAngularVelocityDegS/360,2)} rev/s · hip ${fmt(row.theta2,1)}°`,18);
  svg+=text(x+13,819,`Source frame t=${fmt(row.t,3)} s · ${row.actuatorLimited?'TORQUE LIMITED':'within torque limits'}`,17,row.actuatorLimited?C.red:C.muted);
  return svg;
}
async function main(argv=process.argv.slice(2)){const a=args(argv);let sharp;try{sharp=require(a['sharp-module']||'sharp');}catch(error){throw Error('Sharp is required. Install it or provide --sharp-module / NODE_PATH. '+error.message);}
  const records=[readCapture(a.analytical,'analytical'),readCapture(a.pymunk,'pymunk')];assert.equal(settings(records[0].payload),settings(records[1].payload),'Captured pair settings differ');
  const rows=records[0].result.rows,other=records[1].result.rows;assert.equal(rows.length,other.length,'Paired output clock length');for(let i=0;i<rows.length;i++)assert.ok(Math.abs(rows[i].t-other[i].t)<1e-8,'Paired output clock differs');
  const start=rows[0].t,end=rows.at(-1).t;assert.ok(end>start&&end-start<=10,'Bounded actual duration required');const ctx=vm.createContext({});for(const f of RENDER_FILES)vm.runInContext(fs.readFileSync(path.join(APP,f),'utf8'),ctx,{filename:f});const D=ctx.KinefoldDrawing,T=ctx.KinefoldContactDrawing,b=camera(records,D);
  const dir=path.resolve(a['frames-dir']),allowed=path.join(APP,'.preview')+path.sep;assert.ok(dir.startsWith(allowed),'Frame cache must stay in this app .preview directory');fs.mkdirSync(dir,{recursive:true});
  const times=[];for(let t=start;t<end-1e-9;t=start+times.length/a.fps)times.push(t);times.push(end);const selections=[];
  for(let k=0;k<times.length;k++){const t=times[k],indices=records.map(r=>selectIndex(r.result.rows,t));const p=records[0].payload.params;let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="970" viewBox="0 0 1120 970"><rect width="1120" height="970" fill="${C.paper}"/><g font-family="Segoe UI,Arial,sans-serif">`;
    svg+=text(26,36,a.label,29,C.ink,'font-weight="600"')+text(26,72,`Synced saved terrain replay · t=${fmt(t,2)} s · 1× physical time`,21)+text(26,108,`¼ model · chassis ${fmt(4*p.m1,0)} kg total · links ${fmt(p.m2,0)}/${fmt(p.m3,0)} kg · wheel ${fmt(p.m6,1)} kg · α=${fmt(p.alpha,0)}°`,20,C.muted);
    svg+=records.map((r,i)=>panel(r,i,indices[i],b,D,T)).join('');
    const m=records[0].payload.motorConfig;svg+=text(26,862,`N=${m.gearRatio} x ${m.hipBeltRatio??1} belt = ${m.gearRatio*(m.hipBeltRatio??1)}:1 · Jmotor=${m.rotorInertiaKgM2} · Jgear,input=${m.gearboxInputInertiaKgM2||0} kg m²`,18,C.muted)+text(26,891,`Shaft Coulomb/cogging ${m.coulombFrictionNm} N m + viscous ${m.viscousFrictionNms} N m s/rad · grid 100 mm`,18,C.muted)+text(26,920,records[0].payload.runConfig.fixture==='pinned-chassis'?'CHASSIS PINNED · wheel contact remains physical/free · +pin force supplies support.':'FLOATING CHASSIS · terrain moves right (−x) · noiseless finite-gain feedback.',18,C.muted)+text(26,948,'Spring/chassis package schematic · 0.5 s final reading pause · loop resets the saved replay',17,C.muted);
    svg+='</g></svg>';assert.ok(!svg.includes('NaN')&&!svg.includes('undefined'),'Finite drawing');const name=`frame-${String(k).padStart(4,'0')}.png`;await sharp(Buffer.from(svg)).png().toFile(path.join(dir,name));selections.push({timeS:t,indices,sourceTimesS:records.map((r,i)=>r.result.rows[indices[i]].t),file:name});}
  const manifest={schema:'kinefold/terrain-animation-render-v1',width:1120,height:970,fps:a.fps,label:a.label,startTimeS:start,endTimeS:end,physicalDurationS:end-start,finalPauseMs:500,bounds:b,selectionRule:'Last actual saved row/frame at or before the shared time; no interpolation.',camera:'One fixed camera shared by engines and all frames; world +x left/+z up; mm.',sourceCaptures:records.map(r=>({engine:r.payload.engine,filename:path.basename(r.file),sha256:hash(r.file),sourceSHA256:r.capture.sourceSHA256||null})),rendererSHA256:Object.fromEntries(['export_terrain_animation.cjs',...RENDER_FILES].map(f=>[f,hash(path.join(APP,f))])),settingsSHA256:crypto.createHash('sha256').update(settings(records[0].payload)).digest('hex'),selections};
  fs.writeFileSync(path.join(dir,'render-manifest.json'),JSON.stringify(manifest));console.log(JSON.stringify({frames:selections.length,physicalDurationS:manifest.physicalDurationS,manifest:path.join(dir,'render-manifest.json')}));return manifest;
}
if(require.main===module)main().catch(error=>{console.error(error.stack);process.exitCode=1;});
module.exports={args,canonical,selectIndex,settings,readCapture};
