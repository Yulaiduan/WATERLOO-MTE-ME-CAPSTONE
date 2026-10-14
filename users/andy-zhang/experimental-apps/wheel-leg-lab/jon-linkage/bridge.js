/** Motion Lab adapter loaded after the source-built Jonathan v2 page.
 * Inputs: same-origin shell messages and original parameter controls, mm/deg/kg/N/Nm.
 * Outputs: browser/session snapshots, library profiles/sweeps and height/theme messages.
 * Invocation: /jon-linkage/; retains source JSON/CSV controls and model semantics.
 * Limits: no native Pymunk counterpart, time integration, spring or tire contact solution.
 */
(() => {
 const api=window.JonLinkage,key='motion-lab-jon-linkage/v1';let timer,lastSnapshot='';
 const embedded=window.parent!==window,post=data=>{if(embedded)parent.postMessage(data,location.origin);};
 function snapshot(){const config=api.snapshot(),text=JSON.stringify(config);try{sessionStorage.setItem(key,text);}catch{}if(text!==lastSnapshot){lastSnapshot=text;post({type:'motion-lab-config',backend:'jon_v2',config});}return config;}
 function capture(){try{snapshot();}catch{/* Invalid drafts keep the last valid saved state. */}}
 function height(){post({type:'motion-lab-height',height:document.documentElement.scrollHeight});}
 function report(error){post({type:'motion-lab-error',message:error.message});document.getElementById('lab-linkage-status').textContent=error.message;}
 const note=document.createElement('div');note.className='lab-linkage-note';note.innerHTML='<strong>Separate three-belt linkage · Jonathan v2</strong><span>Kinematics + quasi-static holding loads. A fixed; C wheel centre; P contact. Inertias are stored, without dynamic integration.</span><button id="lab-linkage-sweep">Save four sweeps to Motion Lab</button><span id="lab-linkage-status" role="status"></span>';
 document.querySelector('.topbar').after(note);
 api.pause();
 try{const saved=JSON.parse(sessionStorage.getItem(key)||'null');if(saved)api.restore(saved);}catch(error){document.getElementById('lab-linkage-status').textContent='Saved settings could not be restored: '+error.message;}
 document.getElementById('lab-linkage-sweep').hidden=!embedded;
 document.getElementById('lab-linkage-sweep').onclick=()=>{try{const result=api.sweep(snapshot());post({type:'motion-lab-save-run',backend:'jon_v2',result});document.getElementById('lab-linkage-status').textContent='Four analytical sweeps sent to Profiles & data.';}catch(error){report(error);}};
 document.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(capture,150);});
 document.addEventListener('change',()=>{clearTimeout(timer);timer=setTimeout(capture,150);});
 document.addEventListener('click',()=>{clearTimeout(timer);timer=setTimeout(capture,150);});
 window.addEventListener('pagehide',capture);
 window.addEventListener('message',event=>{
  if(event.origin!==location.origin||event.source!==parent||!embedded)return;
  const data=event.data;
  try{
   if(data.type==='motion-lab-theme'){document.documentElement.dataset.theme=data.theme==='dark'?'dark':'light';document.documentElement.style.colorScheme=data.theme==='dark'?'dark':'light';}
   else if(data.type==='motion-lab-deactivate'){api.pause();capture();}
   else if(data.type==='motion-lab-save-profile')post({type:'motion-lab-profile',backend:'jon_v2',config:snapshot()});
   else if(data.type==='motion-lab-load-profile'){api.restore(data.config);capture();}
   else if(data.type==='motion-lab-evaluate'){const result=api.sweep(data.config);post({type:'motion-lab-evaluated',requestId:data.requestId,result});}
  }catch(error){if(data.type==='motion-lab-evaluate')post({type:'motion-lab-evaluated',requestId:data.requestId,error:error.message});else report(error);}
 });
 new ResizeObserver(height).observe(document.body);
 fetch('/jon-linkage/source.json').then(response=>{if(!response.ok)throw Error('Linkage source manifest unavailable. Rebuild Motion Lab.');return response.json();}).then(source=>{window.JonLinkageSource=source;capture();post({type:'motion-lab-ready',backend:'jon_v2'});height();}).catch(report);
})();
