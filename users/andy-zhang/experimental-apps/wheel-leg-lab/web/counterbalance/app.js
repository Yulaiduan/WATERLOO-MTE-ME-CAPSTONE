/** Constant-lift lever browser tool; loaded by /counterbalance/index.html.
 * Inputs: SI backend profiles, displayed mm/degree controls and recorded math/Pymunk JSON.
 * Outputs: Plotly static/dynamic plots, SVG recorded geometry, portable JSON and library records.
 * Ideal routing study only; native Pymunk opens on the simulation host, not inside the browser.
 */
import {normalizeImport,saveRecord,downloadJSON} from '/library.js';
const $=id=>document.getElementById(id),embedded=parent!==window,NS='http://www.w3.org/2000/svg';
const backends=['counterbalance_math','counterbalance_pymunk'];
let config={},defaults={},result=null,results={},time=0,playing=false,animation=0,lastStamp=0,plots=[],nativeTimer=0,nativeSession=null,nativeConfig=null;
const fmt=(value,n=3)=>Number.isFinite(value)?value.toFixed(n):'—';
const emit=value=>{if(embedded)parent.postMessage(value,location.origin);};
function error(cause){$('error').hidden=false;$('error').textContent=cause instanceof Error?cause.message:String(cause);}
function clearError(){$('error').hidden=true;}
function color(key){return getComputedStyle(document.documentElement).getPropertyValue('--'+key).trim();}
function backend(){return $('backend').value;}
function packet(kind,run=null){return {schema:'wheel-leg-lab-record/v1',kind,backend:run?.backend||backend(),name:'Constant-lift lever · '+(run?.backend||backend()),config:run?.config||config,...(run?{result:run}:{})};}
async function retain(message){if(embedded)emit(message);else if(message.result)await saveRecord(packet('run',message.result));else await saveRecord(packet('profile'));}

function controls(){
 const field=(key,label,unit,scale=1,min=0,max=1e6)=>`<label>${label}<em>${unit}</em><input id="c-${key}" data-key="${key}" data-scale="${scale}" type="number" step="any" min="${min}" max="${max}" value="${config[key]*scale}"></label>`;
 const select=(key,label,options)=>`<label class="full">${label}<select id="c-${key}" data-key="${key}">${options.map(([value,title])=>`<option value="${value}" ${config[key]===value?'selected':''}>${title}</option>`).join('')}</select></label>`;
 const check=(key,label)=>`<label class="lever-check"><input id="c-${key}" data-key="${key}" type="checkbox" ${config[key]?'checked':''}>${label}</label>`;
 $('controls').innerHTML=`<details open><summary>Geometry & gravity</summary><div class="lever-fields">${field('length','Lever L','mm',1000,20,3000)}${field('spring_radius','Spring radius R','mm',1000,5,3000)}${field('anchor_height','Anchor H','mm',1000,5,3000)}${field('payload_mass','Payload at C','kg',1,0,100)}${field('lever_mass','Uniform lever','kg',1,.001,100)}${field('gravity','Gravity','m/s²',1,0,20)}</div></details>
 <details open><summary>Spring law & physical coil</summary><div class="lever-fields">${select('law','Spring law',[['zero_effective','Zero effective length · T=k·d'],['ordinary','Ordinary coil · T=k·max(d−d₀,0)']])}${check('stiffness_auto','Auto k for zero-length gravity balance')}${field('stiffness','Manual spring k','N/m',1,0,100000)}${field('physical_free_length','Physical coil free length','mm',1000,1,5000)}${field('effective_free_length','Ordinary effective d₀','mm',1000,0,5000)}${field('damping','Span damping','N·s/m',1,0,2000)}</div><p id="coil-note" class="muted"></p></details>
 <details open><summary>Motion / free dynamics</summary><div class="lever-fields">${select('mode','Experiment',[['prescribed','Prescribed angle · measure loads'],['free','Free lever · spring / gravity response']])}${field('initial_angle_deg','Initial θ','° from horizontal',1,-178,178)}${field('initial_speed_deg','Initial speed','°/s · free mode',1,-720,720)}${field('theta_min_deg','Minimum θ','°',1,-179,178)}${field('theta_max_deg','Maximum θ','°',1,-178,179)}${select('wave','Prescribed waveform',[['step','Angle step'],['square','Angle square wave'],['pulse','Angle pulse']])}${field('angle_amplitude_deg','Angle change','°',1,-300,300)}${field('start','Start','s',1,0,20)}${field('rise','Smooth C2 rise','ms',1000,0,5000)}${field('fall','Smooth C2 fall','ms',1000,0,5000)}${field('period','Square period','s',1,.02,10)}${field('duty','Square duty','%',100,1,99)}${field('pulse_width','Pulse width','ms',1000,1,5000)}</div><p class="muted">Finite C2 ramps avoid instantaneous angle jumps. Free motion ends at bounds before an impact model.</p></details>
 <details><summary>Integration</summary><div class="lever-fields">${field('duration','Duration','s',1,.1,20)}${field('dt','Output / Pymunk step','ms',1000,.25,4)}${field('iterations','Pymunk iterations','integer',1,20,300)}</div></details>`;
 $('controls').querySelectorAll('[data-key]').forEach(node=>node.addEventListener('change',()=>{
  config[node.dataset.key]=node.type==='checkbox'?node.checked:node.tagName==='SELECT'?node.value:node.valueAsNumber/Number(node.dataset.scale||1);
  if(node.dataset.key==='mode'&&config.mode==='prescribed')config.initial_speed_deg=0;
  $('status').textContent='Inputs changed. Static setup updates now; recorded motion keeps its saved configuration until Run.';
  updateControls();staticPlots();if(!result)draw();emit({type:'motion-lab-config',backend:backend(),config});
 }));updateControls();
}
function rate(c){return c.stiffness_auto?c.gravity*c.length*(c.payload_mass+.5*c.lever_mass)/(c.anchor_height*c.spring_radius):c.stiffness;}
function updateControls(){
 const find=key=>$('controls').querySelector(`[data-key="${key}"]`),free=config.mode==='free';
 find('stiffness').disabled=config.stiffness_auto;
 find('effective_free_length').disabled=false;
 find('physical_free_length').disabled=config.law==='ordinary';
 find('initial_speed_deg').disabled=!free;
 find('initial_speed_deg').value=config.initial_speed_deg;
 for(const key of ['wave','angle_amplitude_deg','start','rise'])find(key).disabled=free;
 find('fall').disabled=free||config.wave==='step';
 for(const key of ['period','duty'])find(key).disabled=free||config.wave!=='square';
 find('pulse_width').disabled=free||config.wave!=='pulse';
 $('coil-note').textContent=config.law==='zero_effective'?`Resolved k = ${fmt(rate(config),3)} N/m. Ideal routing: physical coil length = physical free length + span d; tension k·d. Free length is not assumed to be zero physically.`:`Ordinary law uses effective d₀; slack at d≤d₀. Auto k remains the zero-length reference and cannot make this ordinary law exactly constant.`;
}
function plot(id,title,xTitle,yTitle,traces){
 let panel=$(id);if(!panel){panel=document.createElement('section');panel.id=id;panel.className='lever-plot';const heading=document.createElement('h3');heading.textContent=title;const chart=document.createElement('div');chart.className='lever-chart';panel.append(heading,chart);$('plots').append(panel);plots.push(id);}
 const chart=panel.querySelector('.lever-chart');
 Plotly.react(chart,traces.map((trace,i)=>({type:'scatter',mode:'lines',...trace,line:{width:1.8,color:color(['blue','orange','purple','red'][i%4]),...trace.line}})),{paper_bgcolor:color('panel'),plot_bgcolor:color('panel'),font:{color:color('text'),size:11},xaxis:{title:{text:xTitle},gridcolor:color('line'),automargin:true},yaxis:{title:{text:yTitle},gridcolor:color('line'),automargin:true},margin:{l:65,r:18,t:18,b:70},legend:{orientation:'h',y:-.25},hovermode:'x unified',uirevision:id+'-'+(result?.backend||'setup')},{responsive:true,scrollZoom:true,displaylogo:false,toImageButtonOptions:{filename:id,scale:2}}).catch(error);
}
function staticPlots(){
 if(!['length','spring_radius','anchor_height'].every(key=>Number.isFinite(config[key])&&config[key]>0)||!Object.values(config).every(v=>typeof v!=='number'||Number.isFinite(v)))return;
 const c=config,k=rate(c),angles=[],ideal=[],ordinary=[],tension=[],torque=[],weight=[],coils=[],ordinaryCoils=[],required=c.gravity*(c.payload_mass+.5*c.lever_mass);
 for(let i=0;i<=160;i++){
  const a=c.theta_min_deg+(c.theta_max_deg-c.theta_min_deg)*i/160,q=a*Math.PI/180,d=Math.hypot(c.spring_radius*Math.cos(q),c.anchor_height-c.spring_radius*Math.sin(q)),valid=d>1e-9&&Math.abs(Math.cos(q))>1e-8;
  const selected=k*Math.max(0,d-(c.law==='ordinary'?c.effective_free_length:0));
  angles.push(a);ideal.push(valid?k*c.anchor_height*c.spring_radius/c.length:null);ordinary.push(valid?k*Math.max(0,d-c.effective_free_length)*c.anchor_height*c.spring_radius/(c.length*d):null);
  tension.push(selected);torque.push(d>1e-9?selected*c.anchor_height*c.spring_radius*Math.cos(q)/d:null);weight.push(required*c.length*Math.cos(q));coils.push((c.physical_free_length+d)*1000);ordinaryCoils.push(Math.max(d,c.effective_free_length)*1000);
 }
 plot('lift-angle','Current static setup · equivalent lift','θ from horizontal (°)','Equivalent upward force (N)',[{name:'Ideal zero-effective length',x:angles,y:ideal},{name:'Ordinary coil comparison',x:angles,y:ordinary},{name:'Gravity balance required',x:angles,y:angles.map(()=>required),line:{dash:'dot'}}]);
 plot('tension-angle','Current static setup · coil tension','θ from horizontal (°)','Spring tension (N)',[{name:'Selected spring law · tension varies',x:angles,y:tension}]);
 plot('moment-angle','Current static setup · lever moments','θ from horizontal (°)','Moment magnitude (N·m)',[{name:'Selected spring opening moment',x:angles,y:torque},{name:'Weight closing moment',x:angles,y:weight}]);
 plot('coil-angle','Physical coil / routing length','θ from horizontal (°)','Coil length (mm)',[{name:'Emulated zero-effective routing',x:angles,y:coils},{name:'Ordinary direct span',x:angles,y:ordinaryCoils}]);
}
function dynamicPlots(){
 if(!result)return;const rows=result.rows,x=rows.map(r=>r.t),series=items=>items.map(([key,name])=>({name,x,y:rows.map(r=>key==='equivalent_support_N'&&!r.equivalent_defined?null:r[key])}));
 plot('angle-time','Recorded lever angle','Time (s)','θ (°)',series([['theta_deg','Achieved'],['angle_command_deg',result.config.mode==='free'?'Initial-angle reference':'Prescribed command']]));
 plot('force-time','Recorded spring / equivalent lift / pivot','Time (s)','Force (N)',series([['spring_force_N','Spring tension'],['equivalent_support_N','Equivalent lift'],['joint_force_N','Pivot resultant']]));
 plot('torque-time','Recorded torques','Time (s)','Torque (N·m)',series([['spring_moment_Nm','Spring'],['gravity_moment_Nm','Gravity'],['driver_torque_Nm','Ideal motion driver']]));
 plot('speed-time','Recorded angular velocity','Time (s)','Angular velocity (rad/s)',series([['angular_velocity_rad_s','Lever angular speed']]));
 plot('acceleration-time','Recorded angular acceleration','Time (s)','Angular acceleration (rad/s²)',series([['angular_acceleration_rad_s2','Lever angular acceleration']]));
 plot('tip-acceleration','Recorded tip acceleration','Time (s)','Vertical acceleration (m/s²)',series([['tip_acceleration_y','Payload point C']]));
 plot('energy-time','Recorded energy','Time (s)','Mechanical energy (J)',series([['mechanical_energy_J','Kinetic + spring + gravity']]));
 const comparison=Object.entries(results).map(([key,run])=>({name:key==='counterbalance_math'?'SciPy':'Pymunk',x:run.rows.map(r=>r.t),y:run.rows.map(r=>r.theta_deg)}));
 if(comparison.length>1)plot('comparison-time','Independent model comparison','Time (s)','θ (°)',comparison);
}
function closest(rows,t){let lo=0,hi=rows.length-1;while(lo<hi){const mid=Math.floor((lo+hi)/2);if(rows[mid].t<t)lo=mid+1;else hi=mid;}return rows[lo];}
function svgNode(tag,attrs,text){const node=document.createElementNS(NS,tag);for(const[key,value]of Object.entries(attrs))node.setAttribute(key,value);if(text)node.textContent=text;$('mechanism').append(node);return node;}
function draw(){
 const c=result?.config||config;if(!c.length)return;
 const row=result?closest(result.rows,time):null,q=(row?.theta_deg??c.initial_angle_deg)*Math.PI/180;
 const frame=result?.frames?.length?closest(result.frames,time):{pivot:[0,0],anchor:[0,c.anchor_height],attach:[c.spring_radius*Math.cos(q),c.spring_radius*Math.sin(q)],tip:[c.length*Math.cos(q),c.length*Math.sin(q)]};
 const all=result?.frames?.length?result.frames.flatMap(f=>[f.pivot,f.anchor,f.tip]):[frame.pivot,frame.anchor,[-c.length,-c.length],[c.length,c.length]],xs=all.map(p=>p[0]),ys=all.map(p=>p[1]);
 const W=700,H=340,x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys),scale=Math.min((W-110)/Math.max(x1-x0,.1),(H-90)/Math.max(y1-y0,.1));
 const point=p=>[W/2+(p[0]-(x0+x1)/2)*scale,H/2-(p[1]-(y0+y1)/2)*scale];
 $('mechanism').replaceChildren();$('mechanism').setAttribute('viewBox',`0 0 ${W} ${H}`);
 const O=point(frame.pivot),A=point(frame.anchor),B=point(frame.attach),C=point(frame.tip);
 svgNode('line',{x1:O[0],y1:O[1],x2:A[0],y2:A[1],stroke:color('muted'),'stroke-width':2,'stroke-dasharray':'5 4'});
 svgNode('line',{x1:O[0],y1:O[1],x2:C[0],y2:C[1],stroke:color('blue'),'stroke-width':8,'stroke-linecap':'round'});
 const dx=B[0]-A[0],dy=B[1]-A[1],span=Math.hypot(dx,dy),normal=[-dy/span,dx/span],springPoints=[];
 for(let i=0;i<=24;i++){const s=i/24,w=i<3||i>21?0:(i%2?6:-6);springPoints.push([A[0]+dx*s+normal[0]*w,A[1]+dy*s+normal[1]*w].join(','));}
 svgNode('polyline',{points:springPoints.join(' '),fill:'none',stroke:color('orange'),'stroke-width':2.4});
 [[O,'O · pivot'],[A,'A · anchor'],[B,'B · spring'],[C,'C · payload']].forEach(([p,label])=>{svgNode('circle',{cx:p[0],cy:p[1],r:5,fill:color('panel'),stroke:color('text'),'stroke-width':2});svgNode('text',{x:p[0]+9,y:p[1]-10,fill:color('text'),'font-size':13},label);});
 svgNode('text',{x:20,y:H-14,fill:color('muted'),'font-size':12},result?`${result.engine} recorded geometry · ${c.mode} · θ ${fmt(row.theta_deg,2)}°`:'Current setup geometry · run to generate loads and motion');
 $('time-label').textContent=fmt(time,3)+' s';
 if(row){const stats=[['Spring tension',fmt(row.spring_force_N,2)+' N'],['Equivalent lift',row.equivalent_defined?fmt(row.equivalent_support_N,2)+' N':'Undefined at vertical'],['Pivot resultant',fmt(row.joint_force_N,2)+' N'],['Driver torque',fmt(row.driver_torque_Nm,3)+' N·m'],['Spring span',fmt(row.span_m*1000,1)+' mm'],['Physical coil length',fmt(row.coil_length_m*1000,1)+' mm']];$('values').replaceChildren(...stats.map(([label,value])=>{const box=document.createElement('div'),strong=document.createElement('strong');box.textContent=label;strong.textContent=value;box.append(strong);return box;}));}
}
function pause(){playing=false;lastStamp=0;cancelAnimationFrame(animation);$('play').textContent='Play';}
function showResult(run){
 if(!backends.includes(run.backend)||!run.rows?.length)throw Error('This is not a recorded counterbalance lever run.');
 pause();result=run;results[run.backend]=run;config={...run.config};$('backend').value=run.backend;time=0;controls();staticPlots();dynamicPlots();draw();
 $('time').max=run.rows.at(-1).t;$('time').value=0;$('time').disabled=false;$('play').disabled=false;$('save-run').disabled=false;
 $('snapshot').textContent=`${run.engine} · ${run.config.law==='zero_effective'?'zero effective free length':'ordinary coil'} · L ${fmt(run.config.length*1000,0)} / R ${fmt(run.config.spring_radius*1000,0)} / H ${fmt(run.config.anchor_height*1000,0)} mm`;
 $('diagnostics').textContent=JSON.stringify({config:run.config,parameters:run.parameters,model:run.model,diagnostics:run.diagnostics},null,2);$('scope').textContent=run.scope||'';
 $('warnings').replaceChildren(...(run.warnings||[]).map(message=>{const node=document.createElement('p');node.textContent=message;return node;}));
 $('status').textContent=`Recorded ${run.rows.length.toLocaleString()} samples · ${run.engine} · equivalent lift and coil tension are separate channels.`;emit({type:'motion-lab-config',backend:run.backend,config});
}
function loadConfiguration(value,which=backend()){
 pause();result=null;config={...defaults,...value};if(backends.includes(which))$('backend').value=which;
 $('play').disabled=$('time').disabled=$('save-run').disabled=true;$('values').replaceChildren();$('snapshot').textContent='Current setup · generate a run to record loads and motion';$('scope').textContent='';$('diagnostics').textContent='';$('warnings').replaceChildren();
 for(const id of plots.filter(id=>!['lift-angle','tension-angle','moment-angle','coil-angle'].includes(id))){const panel=$(id);if(panel){Plotly.purge(panel.querySelector('.lever-chart'));panel.remove();}}
 plots=plots.filter(id=>$(id));controls();staticPlots();draw();$('status').textContent='Lever profile loaded. Run to generate data.'+(Object.keys(defaults).some(key=>!(key in value))?' Missing controls use the displayed illustrative model defaults.':'');emit({type:'motion-lab-config',backend:backend(),config});
}
async function requestRun(which,snapshot){
 const endpoint='/api/counterbalance/'+(which==='counterbalance_math'?'math':'pymunk');
 for(let attempt=0;attempt<49;attempt++){
  const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(snapshot)});let run;
  try{run=await response.json();}catch{throw Error(`Counterbalance API unavailable (HTTP ${response.status}). Restart Motion Lab with its launcher.`);}
  if(response.status===409&&attempt<48){await new Promise(resolve=>setTimeout(resolve,250));continue;}
  if(!response.ok)throw Error(run.error||'Lever simulation failed.');return run;
 }
}
async function run(compare=false){
 clearError();pause();$('run').disabled=$('compare').disabled=true;$('status').textContent='Running independent counterbalance lever model…';
 try{
  const snapshot=normalizeImport(packet('profile')).config;
  for(const which of compare?backends:[backend()]){const value=await requestRun(which,snapshot);results[value.backend]=value;await retain({type:'motion-lab-run',backend:value.backend,result:value});}
  showResult(results[backend()]||results.counterbalance_math);
 }catch(cause){error(cause);}finally{$('run').disabled=$('compare').disabled=false;}
}
function saveProfile(){clearError();try{const p=normalizeImport(packet('profile'));downloadJSON(p,'counterbalance-profile.json');void retain({type:'motion-lab-profile',backend:backend(),config}).catch(error);}catch(cause){error(cause);}}
async function native(){
 clearError();if(embedded){emit({type:'motion-lab-show-gui',config:{model:'counterbalance',config}});return;}
 $('native').disabled=true;
 async function request(url,options){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);try{const response=await fetch(url,{...options,signal:controller.signal});let value;try{value=await response.json();}catch{throw Error('Native GUI endpoint unavailable. Restart Motion Lab with its launcher.');}if(!response.ok){const cause=Error(value.error||'Native GUI request failed.');cause.status=response.status;throw cause;}return value;}catch(cause){if(cause.name==='AbortError')throw Error('Native GUI request timed out. Check the simulation host and app log.');throw cause;}finally{clearTimeout(timer);}}
 try{
  const key=JSON.stringify(config);let session=null;
  if(nativeSession&&nativeConfig===key&&['starting','ready','running'].includes(nativeSession.status)){
   try{session=await request('/api/native-gui/'+encodeURIComponent(nativeSession.id)+'/show',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});if(!['starting','ready','running'].includes(session.status))session=null;}catch(cause){if(cause.status!==404)throw cause;}
  }
  if(!session)session=await request('/api/native-gui',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:'counterbalance',config})});
  nativeSession=session;nativeConfig=key;const started=Date.now();
  $('status').textContent='Opening live Pymunk lever on the simulation host desktop…';clearTimeout(nativeTimer);
  const poll=async()=>{try{const state=await request('/api/native-gui/'+encodeURIComponent(session.id));nativeSession=state;if(state.status==='failed')throw Error(state.error||'Native GUI unavailable.');if(state.status==='starting'&&Date.now()-started>15000)throw Error('Native lever has not reported readiness after 15 seconds. Check its .preview/native-gui log.');$('status').textContent=`Native lever on simulation host · ${state.status} · ${state.solver_steps||0} live steps · PID ${state.pid}. Close the desktop window to stop it.`;if(state.status!=='closed')nativeTimer=setTimeout(poll,1200);}catch(cause){error(cause);}};void poll();
 }catch(cause){error(cause);}finally{$('native').disabled=false;}
}
$('run').onclick=()=>run();$('compare').onclick=()=>run(true);$('save-profile').onclick=saveProfile;$('save-run').onclick=()=>{if(result){downloadJSON(packet('run',result),'counterbalance-full-run.json');void retain({type:'motion-lab-save-run',backend:result.backend,result}).catch(error);}};$('native').onclick=native;
$('architecture').onclick=()=>{if(embedded)emit({type:'motion-lab-open-architecture'});else location.assign('/?tab=physics&architecture=constant-lift');};
$('backend').onchange=()=>{pause();emit({type:'motion-lab-config',backend:backend(),config});if(results[backend()])showResult(results[backend()]);else $('status').textContent='Backend selected. Run this lever model to generate its own recorded data.';};
$('time').oninput=()=>{pause();time=Number($('time').value);draw();};
$('play').onclick=()=>{if(playing){pause();return;}if(time>=result.rows.at(-1).t)time=0;playing=true;lastStamp=0;$('play').textContent='Pause';function tick(stamp){if(!playing)return;if(lastStamp)time=Math.min(result.rows.at(-1).t,time+(stamp-lastStamp)/1000);lastStamp=stamp;$('time').value=time;draw();if(time>=result.rows.at(-1).t){pause();return;}animation=requestAnimationFrame(tick);}animation=requestAnimationFrame(tick);};
$('import').onchange=async()=>{clearError();try{const file=$('import').files?.[0];if(!file)return;if(file.size>80*1024*1024)throw Error('JSON exceeds 80 MiB.');const record=normalizeImport(JSON.parse(await file.text()),file.name);if(!backends.includes(record.backend))throw Error('Import a counterbalance lever profile or run.');if(record.result)showResult(record.result);else loadConfiguration(record.config,record.backend);emit({type:'motion-lab-config',backend:backend(),config});}catch(cause){error(cause);}finally{$('import').value='';}};
function theme(){const dark=document.documentElement.dataset.theme==='dark';$('theme').textContent=dark?'Light mode':'Dark mode';staticPlots();dynamicPlots();draw();}
$('theme').onclick=()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';if(embedded)emit({type:'motion-lab-theme',theme:next});else{localStorage.setItem('motion-lab-theme',next);document.documentElement.dataset.theme=next;document.documentElement.style.colorScheme=next;theme();}};
document.addEventListener('motion-lab-theme',theme);
window.addEventListener('message',event=>{if(event.origin!==location.origin||event.source!==parent)return;const value=event.data;try{if(value?.type==='motion-lab-save-profile')saveProfile();else if(value?.type==='motion-lab-load-profile')loadConfiguration(value.config,value.backend);else if(value?.type==='motion-lab-load-result')showResult(value.result);}catch(cause){error(cause);}});
window.addEventListener('pagehide',()=>{pause();clearTimeout(nativeTimer);});
fetch('/api/counterbalance/defaults').then(async response=>{if(!response.ok)throw Error('Counterbalance defaults unavailable. Restart Motion Lab with its launcher.');return response.json();}).then(async value=>{defaults={...value};config=value;controls();staticPlots();draw();emit({type:'motion-lab-config',backend:backend(),config});emit({type:'motion-lab-ready',backend:backend()});if(!new URLSearchParams(location.search).has('loadOnly'))await run();}).catch(error);
