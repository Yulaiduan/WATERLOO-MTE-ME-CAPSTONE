/** Interactive sizing UI. Load /sizing/ through Start Motion Lab.cmd.
 * Inputs: SI model controls and verified spreadsheet snapshot / user CSV imports.
 * Outputs: Plotly envelopes/contours, schematic, candidate table, JSON/CSV downloads.
 * Conditional analytical screening only; no live cloud authentication or hardware solve.
 */
import {DEFAULTS,G,validate,support,spring,sweep,capacity,maxRpm,utilization,designMap,catalogCSV} from './model.js';
import {saveRecord} from '../library.js';
const $=id=>document.getElementById(id),colors=['#008e98','#4874b8','#c68729','#a05b9e'];
const mm=new Set(['upper','lower','anchor','speed','mapMinLink','mapMaxLink']);
let catalog,snapshot,results,timer,rendering=false,rerender=false;
let v4=null;
function acceptV4(packet){
  if(packet?.schema!=='motion-lab-v4-sizing/v1'||packet.torqueConvention!=='applied-ccw-hip'||!Array.isArray(packet.rows)||packet.rows.length<2||packet.rows.length>5000)throw Error('Invalid V4 sizing packet.');
  for(const row of packet.rows)for(const key of ['theta2','hipTorque','outputRpm'])if(!Number.isFinite(row[key])||(key==='outputRpm'&&row[key]<0))throw Error('Nonfinite V4 sizing sample.');
  v4=packet;
}
const v4Rows=()=>v4?.rows.map(r=>({variants:[{torque:r.hipTorque,rpm:r.outputRpm}]}));
const fmt=(n,d=1)=>Number.isFinite(n)?n.toFixed(d):'—';
const safe=text=>String(text??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function fail(error){$('error').hidden=false;$('error').textContent=error.message||String(error);}
function read(){const p={};for(const [key,value]of Object.entries(DEFAULTS)){const el=$(key);if(typeof value==='string')p[key]=el.value;else {if(!el.value.trim()||!el.checkValidity())throw Error(`Check ${el.closest('label')?.textContent.trim()||key}.`);p[key]=Number(el.value)/(mm.has(key)?1000:1);}}return validate(p);}
function write(p){for(const [key,value]of Object.entries(DEFAULTS))$(key).value=typeof value==='number'?p[key]*(mm.has(key)?1000:1):p[key];}
function options(){const oldMotor=$('motor').value,oldGear=$('gear').value;
  $('motor').replaceChildren(...catalog.motors.map(m=>new Option(m.model,m.model)));
  $('gear').replaceChildren(...catalog.gearboxes.map(g=>new Option(`${g.model} · ${g.ratio}:1`,g.model)));
  $('motor').value=catalog.motors.some(m=>m.model===oldMotor)?oldMotor:catalog.motors.find(m=>m.model.includes('6374 140'))?.model||catalog.motors[0].model;
  $('gear').value=catalog.gearboxes.some(g=>g.model===oldGear)?oldGear:catalog.gearboxes.find(g=>g.ratio===20)?.model||catalog.gearboxes[0].model;
  $('source-status').textContent=`${catalog.sourceMode} • ${catalog.retrieved} • ${catalog.motors.length} motors / ${catalog.gearboxes.length} gearbox listings`;
}
function layout(x,y,extra={}){const dark=document.documentElement.dataset.theme==='dark';return {paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:dark?'#192937':'#fff',font:{family:'system-ui',size:11,color:dark?'#dce7ef':'#294154'},margin:{l:65,r:35,t:20,b:65},xaxis:{title:{text:x},gridcolor:dark?'#334858':'#e5ebef',zerolinecolor:'#8b9ca8'},yaxis:{title:{text:y},gridcolor:dark?'#334858':'#e5ebef',zerolinecolor:'#8b9ca8'},legend:{orientation:'h',y:-.23,font:{size:10}},hovermode:'closest',...extra};}
const config={responsive:true,displaylogo:false,toImageButtonOptions:{format:'png',scale:2}};
function plot(id,traces,axes){return Plotly.react($(id),traces,axes,config);}
function diagram(p){const mid=(p.minAngle+p.maxAngle)/2*Math.PI/180,a=p.upper,b=p.lower,{H,R}=spring(p);
  const points={hip:[0,0],knee:[a*Math.cos(mid),a*Math.sin(mid)],wheel:[(a-b)*Math.cos(mid),(a+b)*Math.sin(mid)],anchor:[0,H],attach:[R*Math.cos(mid),R*Math.sin(mid)]};
  const scale=220/Math.max(a+b,H,.2),xy=key=>[90+points[key][0]*scale,40+points[key][1]*scale];
  const line=(from,to,color,width)=>`<line x1="${xy(from)[0]}" y1="${xy(from)[1]}" x2="${xy(to)[0]}" y2="${xy(to)[1]}" stroke="${color}" stroke-width="${width}" stroke-linecap="round"/>`;
  const [ax,ay]=xy('anchor'),[tx,ty]=xy('attach'),dx=tx-ax,dy=ty-ay,d=Math.hypot(dx,dy)||1;
  const coil=Array.from({length:21},(_,i)=>{const t=i/20,off=i===0||i===20?0:(i%2?5:-5);return `${ax+dx*t-dy/d*off},${ay+dy*t+dx/d*off}`;}).join(' ');
  $('mechanism').innerHTML=`<rect x="36" y="18" width="180" height="22" rx="4" fill="#97aaba"/><text x="230" y="33" fill="currentColor" font-size="12">Chassis + payload</text>${line('hip','anchor','#97aaba',5)}${line('hip','knee','#168e9a',9)}${line('knee','wheel','#4f74af',9)}<polyline points="${coil}" fill="none" stroke="#d3942f" stroke-width="3"/>${Object.keys(points).map(k=>`<circle cx="${xy(k)[0]}" cy="${xy(k)[1]}" r="5" fill="#fff" stroke="#536b7d" stroke-width="2"/>`).join('')}<circle cx="${xy('wheel')[0]}" cy="${xy('wheel')[1]}" r="16" fill="none" stroke="#536b7d" stroke-width="5"/><text x="250" y="95" fill="currentColor" font-size="12">Upper ${fmt(a*1000,0)} mm</text><text x="250" y="118" fill="currentColor" font-size="12">Lower ${fmt(b*1000,0)} mm</text><text x="250" y="155" fill="#bc8124" font-size="12">T = k × span</text><text x="250" y="180" fill="currentColor" font-size="12">Ideal 2:1 guide</text><text x="250" y="205" fill="currentColor" font-size="12">θ = ${fmt(mid*180/Math.PI,0)}°</text>`;
}
async function render(){if(rendering){rerender=true;return;}rendering=true;$('error').hidden=true;
  try{const p=read(),motor=catalog.motors.find(m=>m.model===$('motor').value),gear=catalog.gearboxes.find(g=>g.model===$('gear').value);
    const rows=sweep(p),use=utilization(rows,motor,gear,p),map=designMap(p,motor,gear),sp=spring(p);
    const peak=Math.max(...rows.map(r=>r.requiredTorque)),speed=Math.max(...rows.map(r=>Math.abs(r.rpm))),travel=rows.at(-1).height-rows[0].height;
    const list=catalog.motors.flatMap(m=>catalog.gearboxes.map(g=>({motor:m,gear:g,...utilization(rows,m,g,p)}))).sort((a,b)=>a.ratio-b.ratio||a.gear.ratio-b.gear.ratio);
    results={schema:'motion-lab-sizing-result/v1',generated:new Date().toISOString(),assumptions:p,catalog,selected:{motor:motor.model,gearbox:gear.model},rows,map,v4,candidates:list.map(r=>({motor:r.motor.model,gearbox:r.gear.model,...utilization(rows,r.motor,r.gear,p),v4Utilization:v4?utilization(v4Rows(),r.motor,r.gear,p):null})),limitations:'Conditional analytical envelope; no continuous motor thermal, voltage-drop, rotor inertia, contact, mechanical adapter or hardware validation.'};
    window.sizingResults=results;
    results.units={angle:'deg',theta:'rad',height:'m',x:'m',J:'m/rad',qdot:'rad/s',qddot:'rad/s²',torque:'N m',gravity:'N m',assist:'N m',dynamic:'N m',requiredTorque:'N m',rpm:'rpm',power:'W',span:'m',tension:'N',inertia:'kg m²'};
    results.scope=results.limitations;
    try{localStorage.setItem('motion-lab-sizing/v1',JSON.stringify({p,motor:motor.model,gear:gear.model}));}catch{}
    const metrics=[['Design torque',`${fmt(peak)} N·m`,'includes design factor'],['Output speed',`${fmt(speed)} rpm`,'worst pose at requested lift speed'],['Vertical travel',`${fmt(travel*1000,0)} mm`,'over the entered angle window'],['Selected utilization',`${fmt(use.ratio,2)}×`,use.fits?'within assumed limits':'exceeds assumed limits']];
    $('metrics').innerHTML=metrics.map(([label,value,note])=>`<div class="metric"><span>${label}</span><b>${value}</b><small>${note}</small></div>`).join('');
    $('design-summary').textContent=`Static equivalent load ${fmt(support(p))} N/corner; spring support ${fmt(p.springForce)} N (${fmt(p.springForce/support(p)*100,0)}%). Required rate ${fmt(sp.k/1000,2)} N/mm, attachment radius ${fmt(sp.R*1000,0)} mm. Spring tension spans ${fmt(Math.min(...rows.map(r=>r.tension)))}–${fmt(Math.max(...rows.map(r=>r.tension)))} N. Geometric take-up ${fmt((Math.max(...rows.map(r=>r.span))-Math.min(...rows.map(r=>r.span)))*1000)} mm. Physical free length and preload routing still require design.`;
    $('hardware-summary').textContent=`${gear.model}: ${gear.nominalTorque} N·m nominal / ${gear.momentaryTorque} N·m momentary, ${gear.ratedRpm}/${gear.maxRpm} rpm at input; ${fmt(100*gear.efficiency,0)}% catalog efficiency. ${gear.inputBore??'Unverified'} mm input bore; motor flange/shaft engagement is not verified. Effective current cap ${fmt(Math.min(p.current,motor.maxCurrent))} A, Kt ${fmt(motor.kt,4)} N·m/A. Voltage ${p.voltage} V is a scenario input, not a certified winding rating.`;
    $('motor-notes').textContent=motor.notes;diagram(p);
    $('candidates').innerHTML=list.map(r=>`<tr tabindex="0" data-motor="${safe(r.motor.model)}" data-gear="${safe(r.gear.model)}" class="${r.motor===motor&&r.gear===gear?'selected':''}"><td>${safe(r.motor.model.replace('Flipsky ',''))}</td><td>${safe(r.gear.model)}</td><td>${fmt(capacity(r.motor,r.gear,p,0))} N·m</td><td>${fmt(maxRpm(r.motor,r.gear,p),0)}</td><td>${fmt(r.torqueRatio*100,0)}%</td><td>${fmt(r.speedRatio*100,0)}%</td><td class="${r.fits?'fits':'exceeds'}">${r.fits?'Within assumed limits':'Exceeds limits'}</td><td>${v4?fmt(utilization(v4Rows(),r.motor,r.gear,p).ratio,2)+'×':'—'}</td></tr>`).join('');
    $('v4-overlay').hidden=!v4;
    if(v4){const vu=utilization(v4Rows(),motor,gear,p);$('v4-summary').textContent=`Frozen V4 design: ${v4.parameters.L2}/${v4.parameters.L3} mm, θ₂ ${v4.parameters.te}–${v4.parameters.tc}°, vertical hub speed ${v4.verticalSpeed_mm_s} mm/s. Selected pair utilization ${fmt(vu.ratio,3)}× after ${p.safety}× torque factor (${vu.fits?'within assumed limits':'exceeds limits'}). Direct hip drive only; basic model hip/knee selector does not change this overlay. Fixed-A prescribed forces, no dynamic torque. Mass/length map below still describes the basic constant-lift model. Re-transfer after editing V4.`;}
    const standard=catalog.gearboxes.filter((g,i,arr)=>arr.findIndex(v=>v.ratio===g.ratio)===i),traces=[];
    for(const [i,g] of standard.entries())for(const mode of ['nominal','momentary']){const trial={...p,mode},limit=maxRpm(motor,g,trial),x=Array.from({length:121},(_,i)=>limit*i/120),y=x.map(n=>capacity(motor,g,trial,n));x.push(limit);y.push(0);traces.push({x,y,type:'scatter',mode:'lines',name:`${g.ratio}:1 ${mode}`,legendgroup:String(g.ratio),line:{color:colors[i%4],width:mode==='nominal'?2.5:1.5,dash:mode==='nominal'?'solid':'dash'},fill:mode==='nominal'?'tozeroy':undefined,fillcolor:mode==='nominal'?['rgba(0,142,152,.09)','rgba(72,116,184,.09)','rgba(198,135,41,.09)','rgba(160,91,158,.09)'][i%4]:undefined,hovertemplate:'%{x:.1f} rpm · %{y:.2f} N·m<extra>%{fullData.name}</extra>'});}
    traces.push({x:rows.map(r=>Math.abs(r.rpm)),y:rows.map(r=>r.requiredTorque),type:'scatter',mode:'lines+markers',name:'Motion demand × factor',line:{color:'#596674',width:3},marker:{size:4,color:'#172b3a'},customdata:rows.map(r=>r.angle),hovertemplate:'θ %{customdata:.1f}°<br>%{x:.2f} rpm<br>%{y:.2f} N·m<extra>Design demand</extra>'});
    traces.push({x:[0],y:[Math.max(...rows.map(r=>Math.abs(r.variants[0].torque)*p.safety))],type:'scatter',mode:'markers',name:'Static holding demand',marker:{symbol:'diamond',size:10,color:'#a74839'}});
    if(v4)traces.push({x:v4.rows.map(r=>r.outputRpm),y:v4.rows.map(r=>Math.abs(r.hipTorque)*p.safety),type:'scatter',mode:'lines+markers',name:'Jon V4 · direct hip × factor',line:{color:'#b83e88',width:3},marker:{size:4},customdata:v4.rows.map(r=>r.theta2),hovertemplate:'V4 θ₂ %{customdata:.1f}°<br>%{x:.2f} rpm · %{y:.4f} N·m<extra>Quasi-static V4 hip</extra>'});
    const heat=[{x:map.lengths.map(x=>x*1000),y:map.masses,z:map.z,type:'heatmap',zmin:0,zmax:2,colorscale:[[0,'#d8f0eb'],[.49,'#69bca9'],[.5,'#fff3c3'],[1,'#c45b4b']],colorbar:{title:{text:'Use / limit'},thickness:12,len:.85},hovertemplate:'Upper %{x:.0f} mm<br>Chassis %{y:.1f} kg<br>Utilization %{z:.3f}<extra></extra>'},
      {x:map.lengths.map(x=>x*1000),y:map.masses,z:map.z,type:'contour',contours:{start:1,end:1,size:1,coloring:'none',showlabels:true},line:{color:'#243c50',width:2},showscale:false,hoverinfo:'skip',name:'Limit = 1'},
      {x:[p.upper*1000],y:[p.chassis],type:'scatter',mode:'markers',name:'Current',marker:{size:11,color:'#172d40',symbol:'x'}}];
    const loads=[{x:rows.map(r=>r.angle),y:rows.map(r=>Math.min(...r.variants.map(v=>v.torque))),type:'scatter',mode:'lines',name:'Lower demand',line:{color:'#bb654d',width:1}},
      {x:rows.map(r=>r.angle),y:rows.map(r=>Math.max(...r.variants.map(v=>v.torque))),type:'scatter',mode:'lines',fill:'tonexty',fillcolor:'rgba(192,108,81,.14)',name:'Upper demand',line:{color:'#bb654d',width:1}},
      ...[['gravity','Gravity','#4874b8'],['assist','Spring assistance','#008e98']].map(([key,name,color])=>({x:rows.map(r=>r.angle),y:rows.map(r=>r[key]),type:'scatter',mode:'lines',name,line:{color,width:2}})),
      {x:rows.map(r=>r.angle),y:rows.map(r=>r.gravity-r.assist),type:'scatter',mode:'lines',name:'Static motor residual',line:{color:'#8e5b99',width:2}}];
    await Promise.all([plot('envelope',traces,layout('Gearbox output speed magnitude (rpm)','Output torque magnitude (N·m)')),
      plot('contour',heat,layout('Upper-link length (mm)','Chassis assembly mass (kg)',{showlegend:false,margin:{l:65,r:80,t:20,b:55}})),
      plot('loads',loads,layout('Upper-link angle θ (°)','Actuator torque before factor (N·m)'))]);
    $('contour').removeAllListeners('plotly_click');$('contour').on('plotly_click',event=>{const pt=event.points[0];if(pt.curveNumber!==0)return;const ratio=p.lower/p.upper;$('upper').value=fmt(pt.x,2);$('lower').value=fmt(pt.x*ratio,2);$('chassis').value=fmt(pt.y,2);schedule();});
    document.body.dataset.ready='true';
  }catch(error){fail(error);}finally{rendering=false;if(rerender){rerender=false;void render();}}
}
function schedule(){clearTimeout(timer);timer=setTimeout(()=>void render(),180);}
async function currentResult(){read();clearTimeout(timer);timer=null;while(rendering)await new Promise(resolve=>setTimeout(resolve,30));await render();if(!$('error').hidden)throw Error($('error').textContent);return results;}
function download(name,text,type){const url=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('controls').onsubmit=e=>e.preventDefault();$('controls').addEventListener('input',e=>{if(e.target.type!=='file')schedule();});$('controls').addEventListener('change',e=>{if(e.target.type!=='file')schedule();});
$('balance').onclick=()=>{try{$('springForce').value=fmt(.9*support(read()),3);schedule();}catch(e){fail(e);}};
$('reset').onclick=()=>{write(DEFAULTS);schedule();};
function choose(event){const tr=event.target.closest('tr[data-motor]');if(!tr)return;$('motor').value=tr.dataset.motor;$('gear').value=tr.dataset.gear;schedule();}
$('candidates').onclick=choose;$('candidates').onkeydown=e=>{if(e.key==='Enter')choose(e);};
$('export').onclick=async()=>{try{download('suspension-sizing.json',JSON.stringify(await currentResult(),null,2),'application/json');}catch(e){fail(e);}};
$('export-csv').onclick=async()=>{try{await currentResult();const keys=['angle','height','x','rpm','gravity','assist','dynamic','torque','requiredTorque','span','tension'];download('suspension-demand.csv',['angle_deg,height_m,wheel_x_m,output_rpm,gravity_Nm,assist_Nm,dynamic_Nm,steady_torque_Nm,design_peak_Nm,span_m,tension_N',...results.rows.map(r=>keys.map(k=>r[k]).join(','))].join('\n'),'text/csv');}catch(e){fail(e);}};
$('save-library').onclick=async()=>{try{const result=await currentResult();await saveRecord({kind:'dataset',name:`Suspension sizing · ${result.selected.motor} · ${result.selected.gearbox}`,result});$('source-status').textContent='Sizing study saved in Profiles & data, including assumptions and catalog provenance.';}catch(e){fail(e);}};
for(const [id,kind,key]of [['motors-file','motors','motors'],['gears-file','gears','gearboxes']])$(id).onchange=async()=>{try{const file=$(id).files[0];if(!file)return;if(file.size>1e6)throw Error('CSV is limited to 1 MB. Export only the catalog tab.');const parsed=catalogCSV(await file.text(),kind);catalog={...catalog,[key]:parsed,retrieved:new Date().toISOString(),sourceMode:`User CSV import (${file.name}); other catalog retains its prior source`};try{sessionStorage.setItem('motion-lab-sizing-catalog/v1',JSON.stringify(catalog));}catch{}options();schedule();}catch(e){fail(e);}finally{$(id).value='';}};
$('restore-catalog').onclick=()=>{catalog=structuredClone(snapshot);sessionStorage.removeItem('motion-lab-sizing-catalog/v1');options();schedule();};
window.addEventListener('message',event=>{if(event.origin===location.origin&&event.data?.type==='motion-lab-theme'){document.documentElement.dataset.theme=event.data.theme;schedule();}});
window.addEventListener('message',event=>{if(event.origin===location.origin&&event.data?.type==='motion-lab-v4-overlay'){try{acceptV4(event.data.packet);schedule();}catch(e){fail(e);}}});
$('clear-v4').onclick=()=>{v4=null;sessionStorage.removeItem('motion-lab-v4-sizing/v1');schedule();};
new ResizeObserver(()=>{for(const id of ['envelope','contour','loads'])if($(id).data)Plotly.Plots.resize($(id));}).observe(document.querySelector('main'));
try{try{const stored=JSON.parse(sessionStorage.getItem('motion-lab-v4-sizing/v1'));if(stored)acceptV4(stored);}catch{}const response=await fetch('./catalog.json');if(!response.ok)throw Error('Could not read spreadsheet snapshot.');snapshot=await response.json();catalog=structuredClone(snapshot);try{const stored=JSON.parse(sessionStorage.getItem('motion-lab-sizing-catalog/v1'));if(stored?.schema===snapshot.schema)catalog=stored;}catch{}
  $('sheet-link').href=snapshot.spreadsheet+'#gid=20261020';options();write(DEFAULTS);try{const saved=JSON.parse(localStorage.getItem('motion-lab-sizing/v1'));if(saved){validate(saved.p);write(saved.p);if(catalog.motors.some(m=>m.model===saved.motor))$('motor').value=saved.motor;if(catalog.gearboxes.some(g=>g.model===saved.gear))$('gear').value=saved.gear;}}catch{write(DEFAULTS);}await render();
}catch(error){fail(error);}
parent.postMessage({type:'motion-lab-ready'},location.origin);
