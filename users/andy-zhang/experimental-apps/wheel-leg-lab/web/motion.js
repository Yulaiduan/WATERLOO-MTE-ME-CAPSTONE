/* Unified motion workspace: local solver results, append-only browser records,
 * portable JSON and the actual Pymunk viewer. No remote data upload.
 */
import {saveRecord,downloadJSON} from './library.js';
import {mountDataBrowser} from './data-browser.js';
const $=id=>document.getElementById(id),frames=new Map(),pending=new Map(),ready=new Set(),configs={},runs={};
let tab='home',mathModel='scipy',theme=document.documentElement.dataset.theme||'light',guiResult=null;
const studies=[['gallery','All motion studies','/animations/'],['ratio','Wheel / link force & travel','/force-plots/'],['linear','Straight 2:1 leg','/animations/linear-leg/'],['coaxial','Independent coaxial wheel drive','/animations/coaxial-wheel-leg/'],['tilt','Tilted invertible leg','/animations/tilted-invertible-leg/'],['mirror','Mirrored left tilt','/animations/left-tilted-leg/'],['reindex','Historical reindexing alternative','/animations/two-position-left-leg/'],['fixed','Fixed 4:1 working strokes','/animations/fixed-ratio-left-leg/'],['paths','Mathematical path family','/animations/leg-path-family/'],['recorded','Recorded Pymunk playback','/recorded/']];
function status(text){$('lab-status').textContent=text;}
function error(cause){$('lab-error').hidden=false;$('lab-error').textContent=cause instanceof Error?cause.message:String(cause);}
function clearError(){$('lab-error').hidden=true;}
function name(backend,config){return `${$(tab==='physics'?'physics-profile-name':'profile-name').value||'Wheel leg study'} · ${backend}${config?.wave?' · '+config.wave:''}`;}
function send(key,message){const frame=frames.get(key);if(!frame)return;if(ready.has(key))frame.contentWindow.postMessage(message,location.origin);else{const queue=pending.get(key)||[];queue.push(message);pending.set(key,queue);}}
function markReady(key){ready.add(key);const frame=frames.get(key);for(const message of pending.get(key)||[])frame.contentWindow.postMessage(message,location.origin);pending.delete(key);}
function ensureFrame(key,host,url,title){
 if(frames.has(key))return frames.get(key);
 const frame=document.createElement('iframe');frame.title=title;frame.src=url;frame.dataset.key=key;
 frame.addEventListener('load',()=>{frame.contentWindow.postMessage({type:'motion-lab-theme',theme},location.origin);if(key==='studies')markReady(key);});
 $(host).append(frame);frames.set(key,frame);return frame;
}
function showMathModel(model){
 mathModel=model==='linkage'?'linkage':'scipy';
 document.querySelectorAll('[data-math-model]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.mathModel===mathModel)));
 ensureFrame(mathModel==='scipy'?'math':'linkage','math-host',mathModel==='scipy'?'/mathematical/?embedded=1':'/linkage/?embedded=1',mathModel==='scipy'?'Independent SciPy mathematical simulation':'Detailed two-coordinate linkage model');
 for(const key of ['math','linkage'])if(frames.has(key))frames.get(key).hidden=key!==(mathModel==='scipy'?'math':'linkage');
 $('compare-models').hidden=mathModel==='linkage';
 $('math-caption').textContent=mathModel==='scipy'?'Independent Python / SciPy model · MATLAB ode45 companion':'Two-coordinate guide / wheel-drive mathematical bench';
}
function selectTab(next){
 if(!['home','math','physics','studies','data'].includes(next))next='home';tab=next;clearError();
 document.querySelectorAll('[data-panel]').forEach(panel=>panel.hidden=panel.dataset.panel!==tab);
 document.querySelectorAll('[data-tab]').forEach(button=>{if(button.dataset.tab===tab)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');});
 if(tab==='math')showMathModel(mathModel);
 if(tab==='physics')ensureFrame('physics','physics-host','/physics/?embedded=1','Actual 2D Pymunk physical model');
 if(tab==='studies')openStudy($('study-select').value||'gallery');
 if(tab==='data'){void dataBrowser.refresh();requestAnimationFrame(()=>$('data-panel').querySelectorAll('.js-plotly-plot').forEach(plot=>Plotly.Plots.resize(plot)));}
 const url=new URL(location.href);url.searchParams.set('tab',tab);if(tab==='math')url.searchParams.set('model',mathModel);else url.searchParams.delete('model');history.replaceState(null,'',url);
}
function openStudy(id){const study=studies.find(s=>s[0]===id)||studies[0];$('save-study').disabled=study[0]==='gallery';$('save-study-data').disabled=!['ratio','paths','recorded'].includes(study[0]);let frame=frames.get('studies');if(!frame)frame=ensureFrame('studies','studies-host',study[2]+'?embedded=1',study[1]);else{frame.src=study[2]+'?embedded=1';frame.title=study[1];ready.delete('studies');}}
async function keepRun(backend,result){
 runs[backend]=result;if(result.config)configs[backend]=result.config;
 const record=await saveRecord({kind:'run',name:name(backend,result.config),backend,config:result.config,result});
 status(`${backend==='math'?'Mathematical':backend==='pymunk'?'Pymunk':'Detailed linkage'} run saved · ${record.result.rows?.length||record.result.samples?.length||0} samples · inspect/export in Profiles & data`);
 await dataBrowser.refresh();return record;
}
async function keepProfile(backend,config,reference_inputs){const record=await saveRecord({kind:'profile',name:name(backend,config),backend,config,...(reference_inputs?{reference_inputs}:{})});status(`Saved profile: ${record.name}`);await dataBrowser.refresh();}
function requestProfile(){const key=tab==='physics'?'physics':mathModel==='linkage'?'linkage':'math';if(!frames.has(key)){selectTab('math');status('Open a model, set its inputs, then save the profile.');return;}send(key,{type:'motion-lab-save-profile'});}
function loadProfile(record,backend){
 if(backend==='math')ensureFrame('math','math-host','/mathematical/?embedded=1&loadOnly=1','Independent SciPy mathematical simulation');
 if(backend==='pymunk')ensureFrame('physics','physics-host','/physics/?embedded=1&loadOnly=1','Actual 2D Pymunk physical model');
 if(backend==='linkage'){mathModel='linkage';selectTab('math');send('linkage',{type:'motion-lab-load-profile',config:record.config});}
 else{if(backend==='math')mathModel='scipy';selectTab(backend==='math'?'math':'physics');send(backend==='math'?'math':'physics',{type:'motion-lab-load-profile',config:record.config,reference_inputs:record.reference_inputs});}
 configs[backend]=record.config;const label=record.name.replace(/ · (math|pymunk|linkage)( · (step|square|pulse|impulse))?$/,'').slice(0,100);$('profile-name').value=label;$('physics-profile-name').value=label;status('Profile loaded into controls. Run simulation to generate new data.');
}
function loadStudy(record){
 const settings=record.result?.study_settings;if(!settings||!studies.some(study=>study[0]===settings.id))throw Error('Unknown motion study.');
 $('study-select').value=settings.id;selectTab('studies');
 const frame=frames.get('studies');frame.addEventListener('load',()=>requestAnimationFrame(()=>{
  for(const control of settings.controls){const node=frame.contentDocument.getElementById(control.id);if(!node||!['INPUT','SELECT'].includes(node.tagName)||node.type==='file')continue;
   if(node.type==='checkbox')node.checked=Boolean(control.value);else node.value=String(control.value);
   node.dispatchEvent(new Event('input',{bubbles:true}));node.dispatchEvent(new Event('change',{bubbles:true}));
  }
  if(settings.widget_state)frame.contentWindow.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:settings.widget_state}}}));
  status('Motion-study settings restored. Plotly data remains available in the saved JSON.');
 }),{once:true});
}
async function saveStudy(withData){
 clearError();try{
  const frame=frames.get('studies'),doc=frame?.contentDocument;if(!doc)throw Error('Open a study first.');
  const id=$('study-select').value,study=studies.find(s=>s[0]===id);
  const controls=[...doc.querySelectorAll('input[id],select[id]')].filter(node=>node.type!=='file').map(node=>({id:node.id,type:node.type||'select',value:node.type==='checkbox'?node.checked:node.value}));
  const plots=[],rows=[];
  if(withData)for(const plot of doc.querySelectorAll('.js-plotly-plot')){
   const title=plot.closest('section')?.querySelector('h3')?.textContent||plot.getAttribute('aria-label')||'Study plot';
   const traces=[];for(const trace of plot.data||[]){if(!trace.x||!trace.y)continue;const x=Array.from(trace.x),y=Array.from(trace.y),label=trace.name||'Series';
    traces.push({name:label,x,y});for(let i=0;i<Math.min(x.length,y.length);i++)if(Number.isFinite(x[i])&&Number.isFinite(y[i]))rows.push({mode:title+' · '+label,x:x[i],y:y[i]});
   }
   plots.push({title,x_unit:plot.layout?.xaxis?.title?.text,y_unit:plot.layout?.yaxis?.title?.text,traces});
  }
  const packet={schema:'motion-lab-study/v1',name:study[1]+(withData?' · plotted data':' · settings'),study_settings:{id,route:study[2],controls,widget_state:frame.contentWindow.openai?.widgetState||null},plots,rows,scope:'Miscellaneous study controls and displayed Plotly samples. No solver configuration or full-resolution rerun is inferred.'};
  const values=Object.fromEntries(controls.filter(c=>Number.isFinite(Number(c.value))).map(c=>[c.id,Number(c.value)]));
  await saveRecord({kind:'dataset',name:packet.name,result:{...packet,rows:rows.length?rows:[values]}});downloadJSON(packet,id+(withData?'-data':'-settings')+'.json');await dataBrowser.refresh();status('Study settings/data saved to the browser library and JSON.');
 }catch(cause){error(cause);}
}
const dataBrowser=mountDataBrowser($('data-panel'),{theme,onLoadProfile:loadProfile,onPymunk:record=>showGui(record.config,record.result),onLoadStudy:loadStudy});
async function simulate(endpoint,config){
 for(let attempt=0;attempt<49;attempt++){
  const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config)}),value=await response.json();
  if(response.status===409&&attempt<48){await new Promise(resolve=>setTimeout(resolve,250));continue;}
  if(!response.ok)throw Error(value.error||'Simulation failed.');return value;
 }
}
async function showGui(config=null,result=null){
 const separateLinkage=!config&&tab==='math'&&mathModel==='linkage';
 clearError();$('gui-error').hidden=true;if(!$('gui-dialog').open)$('gui-dialog').showModal();ensureFrame('gui','gui-host','/physics/?viewer=1','Pymunk engine visual GUI');
 try{
  if(!config){config=configs[tab==='math'&&mathModel==='scipy'?'math':'pymunk'];if(!config)config=await (await fetch('/api/defaults')).json();}
  $('gui-status').textContent='Preparing actual Pymunk space for this wheel-height profile…';
  if(result&&JSON.stringify(result.config)===JSON.stringify(config)&&(result.backend==='pymunk'||(result.engine==='7.3.0'&&result.frames?.[0]?.debug_draw)))guiResult=result;
  else guiResult=await simulate('/api/pymunk/simulate',config);
  send('gui',{type:'motion-lab-load-result',result:guiResult});
  $('gui-status').textContent=`Actual Pymunk ${guiResult.engine} · ${guiResult.rows.length.toLocaleString()} solver steps · ${separateLinkage?'separate wheel-height fixture; not the two-axis drive case':'play/scrub the engine shapes and constraints'}`;
 }catch(cause){$('gui-error').hidden=false;$('gui-error').textContent=cause.message;}
}
function changeTheme(next){theme=next==='dark'?'dark':'light';document.documentElement.dataset.theme=theme;document.documentElement.style.colorScheme=theme;try{localStorage.setItem('motion-lab-theme',theme);}catch{}
 $('theme-toggle').textContent=theme==='dark'?'Light mode':'Dark mode';$('theme-toggle').setAttribute('aria-pressed',String(theme==='dark'));
 for(const frame of frames.values())frame.contentWindow.postMessage({type:'motion-lab-theme',theme},location.origin);dataBrowser.setTheme(theme);if(!$('comparison').hidden)drawComparison();
}
function drawComparison(){
 const a=runs.math,b=runs.pymunk;if(!a||!b)return;const css=getComputedStyle(document.documentElement),color=key=>css.getPropertyValue(key).trim();
 Plotly.react($('comparison-plot'),[{name:'SciPy chassis',x:a.rows.map(r=>r.t),y:a.rows.map(r=>r.chassis_displacement_mm),mode:'lines',line:{color:color('--blue')}},{name:'Pymunk chassis',x:b.rows.map(r=>r.t),y:b.rows.map(r=>r.chassis_displacement_mm),mode:'lines',line:{color:color('--orange'),dash:'dash'}},{name:'Wheel command',x:a.rows.map(r=>r.t),y:a.rows.map(r=>r.input_mm),mode:'lines',line:{color:color('--muted'),width:1}}],{paper_bgcolor:color('--panel'),plot_bgcolor:color('--panel'),font:{color:color('--text')},xaxis:{title:{text:'Time (s)'},gridcolor:color('--line')},yaxis:{title:{text:'Vertical displacement (mm)'},gridcolor:color('--line')},margin:{l:65,r:20,t:25,b:70},legend:{orientation:'h',y:-.22},hovermode:'x unified',uirevision:'comparison'}, {responsive:true,scrollZoom:true,displaylogo:false});
}
$('compare-models').onclick=async()=>{clearError();$('compare-models').disabled=true;try{const config=configs.math||await (await fetch('/api/defaults')).json();status('Running independent SciPy and Pymunk with the same profile…');const [a,b]=await Promise.all([simulate('/api/math/simulate',config),simulate('/api/pymunk/simulate',config)]);await keepRun('math',a);await keepRun('pymunk',b);send('math',{type:'motion-lab-load-result',result:a});$('comparison').hidden=false;$('comparison-note').textContent=`Identical input and masses · SciPy ${a.solver.method} · Pymunk dt ${(b.config.dt*1000).toFixed(3)} ms. Mathematical limits terminate before impact; Pymunk limits transmit constraint impulses.`;drawComparison();status('Both runs saved. Compare curves here or inspect all channels in Profiles & data.');}catch(cause){error(cause);}finally{$('compare-models').disabled=false;}};
window.addEventListener('message',event=>{
 if(event.origin!==location.origin||!event.data||typeof event.data!=='object')return;
 const key=[...frames].find(([,frame])=>frame.contentWindow===event.source)?.[0];if(!key)return;const data=event.data;
 if(data.type==='motion-lab-height'&&Number.isFinite(data.height))frames.get(key).style.height=Math.min(18000,Math.max(key==='gui'?680:600,data.height))+'px';
 else if(data.type==='motion-lab-ready'||data.type==='motion-lab-viewer-ready')markReady(key);
 else if(data.type==='motion-lab-config'&&['math','pymunk','linkage'].includes(data.backend))configs[data.backend]=data.config;
 else if(data.type==='motion-lab-run'&&key!=='gui'){markReady(key);void keepRun(data.backend,data.result).catch(error);}
 else if(data.type==='motion-lab-profile')void keepProfile(data.backend,data.config,data.reference_inputs).catch(error);
 else if(data.type==='motion-lab-save-run')void keepRun(data.backend,data.result).catch(error);
 else if(data.type==='motion-lab-show-gui')void showGui(data.config,data.result);
 else if(data.type==='motion-lab-theme')changeTheme(data.theme);
});
document.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>selectTab(button.dataset.tab));document.querySelectorAll('[data-open]').forEach(button=>button.onclick=()=>selectTab(button.dataset.open));document.querySelectorAll('[data-math-model]').forEach(button=>button.onclick=()=>showMathModel(button.dataset.mathModel));
for(const [id,title] of studies){const option=document.createElement('option');option.value=id;option.textContent=title;$('study-select').append(option);}
$('study-select').onchange=()=>openStudy($('study-select').value);$('theme-toggle').onclick=()=>changeTheme(theme==='dark'?'light':'dark');$('show-gui').onclick=()=>showGui(null,tab==='physics'?runs.pymunk:null);$('close-gui').onclick=()=>$('gui-dialog').close();$('save-profile').onclick=requestProfile;$('physics-save-profile').onclick=requestProfile;$('open-data').onclick=()=>selectTab('data');
$('save-study').onclick=()=>saveStudy(false);$('save-study-data').onclick=()=>saveStudy(true);
const query=new URLSearchParams(location.search);mathModel=query.get('model')==='linkage'?'linkage':'scipy';if(studies.some(s=>s[0]===query.get('study')))$('study-select').value=query.get('study');changeTheme(theme);selectTab(query.get('tab')||'home');
if(query.get('gui')==='1'){let config=null;try{config=JSON.parse(sessionStorage.getItem('motion-lab-gui-profile')||'null');}catch{}void showGui(config);}
