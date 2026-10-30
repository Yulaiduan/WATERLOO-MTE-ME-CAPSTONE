/** Load exact saved actuator cases into shared browser replay views.
 * Load after comparison-replay.js and the live solver shells. Inputs: immutable
 * job/candidate IDs, captured case payloads and actual engine mm/deg/SI frames.
 * Outputs: synchronized pair/mirror playback, captured Plotly charts and explicit
 * app-folder exports. No Studio parameter, motor or physical profile is changed.
 * Numerical quarter-model evidence; browser playback is not a new physics solve.
 */
(function(root){
  'use strict';
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const cases=['landing','jump','terrain'],names={landing:'Landing',jump:'Jump',terrain:'Terrain'};
  const terminal=new Set(['complete','completed','failed','cancelled','timed-out']);
  const mirrors=new Map();
  let controller=null,capture=null,owner=null,pairView=null,clockSubscription=null;
  const defaultRequest=async body=>{
    const response=await fetch('/api/actuator-comparison',{method:'POST',headers:{'Content-Type':'application/json','X-Kinefold-Request':'coupled-dynamics'},body:JSON.stringify(body)});
    const data=await response.json();
    if(!response.ok||data.error||data.ok===false)throw Error(data.error||'Replay request failed ('+response.status+').');
    return data;
  };
  function pause(){controller?.pause();root.KinefoldLiveDynamics?.pauseAll();}
  function disposePlayback(){
    pause();clockSubscription?.();clockSubscription=null;pairView?.destroy();pairView=null;
    for(const m of mirrors.values()){m.view?.destroy();m.view=null;root.KinefoldPlotly?.purge(m.host);m.host.innerHTML='';}
    controller?.destroy();controller=null;capture=null;
  }
  function ensureMirror(engine){
    if(mirrors.has(engine))return mirrors.get(engine);
    const panel=document.getElementById(engine);if(!panel)throw Error('Dynamic '+engine+' workspace is unavailable.');
    const live=document.createElement('div');live.dataset.liveDynamics='true';
    while(panel.firstChild)live.append(panel.firstChild);
    const host=document.createElement('section');host.className='captured-solver-replay';host.hidden=true;
    panel.append(live,host);
    const m={engine,live,host,view:null};mirrors.set(engine,m);return m;
  }
  function message(text,busy=false,canRun=false){
    for(const m of mirrors.values()){
      const status=m.host.querySelector('[data-captured-status]');if(status)status.textContent=text;
      for(const b of m.host.querySelectorAll('[data-captured-case]'))b.disabled=busy;
      const run=m.host.querySelector('[data-captured-run]');if(run){run.disabled=busy;run.hidden=!canRun;}
      const cancel=m.host.querySelector('[data-captured-cancel]');if(cancel)cancel.hidden=!busy;
    }
  }
  function showLive(){
    pause();for(const m of mirrors.values()){m.host.hidden=true;m.live.hidden=false;}
    root.dispatchEvent?.(new Event('resize'));
  }
  function cursor(state){
    for(const m of mirrors.values())for(const plot of m.host.querySelectorAll('[data-replay-time-plot]'))root.KinefoldPlotly?.cursor(plot,state.time);
  }
  function mirrorCharts(m){
    const group=m.host.querySelector('[data-captured-plots]');if(!group?.open||group.dataset.loaded==='true'||!capture)return;
    group.dataset.loaded='true';const host=group.querySelector('div');
    const kind=capture.kind,run=capture.runs[m.engine].result;
    const specs=root.KinefoldAutomaticComparison?.plotSpecs({candidate:capture.candidate,runs:{[m.engine]:{[kind]:run}}})||[];
    for(const spec of specs){
      const card=document.createElement('section');card.className='actuator-chart';card.innerHTML='<h3>'+esc(spec.title)+'</h3><div></div>';
      host.append(card);const graph=card.querySelector('div');
      if(spec.xLabel.startsWith('Time'))graph.dataset.replayTimePlot='true';
      const key='captured-'+m.engine+'-'+capture.settingsHash+'-'+spec.id;
      root.KinefoldPlotly?.react(graph,spec.traces,{height:360,xaxis:{title:{text:spec.xLabel}},yaxis:{title:{text:spec.yLabel}}},{key}).catch(error=>{if(card.isConnected)card.insertAdjacentHTML('beforeend','<p>'+esc(error.message)+'</p>');});
    }
    cursor(controller.getState());
  }
  function pendingMirrors(text){
    for(const m of mirrors.values()){
      m.host.innerHTML='<div class="captured-replay-heading"><div><span class="eyebrow">SAVED COMPARISON CASE</span><h2>Captured '+esc(names[owner?.getState().kind]||'case')+' · awaiting paired frames</h2></div><button type="button" data-captured-live>Return to live design</button></div><nav class="dyn-toolbar">'+cases.map(k=>'<button type="button" data-captured-case="'+k+'">'+names[k]+'</button>').join('')+'<button type="button" data-captured-run hidden>Run captured case in both engines</button><button type="button" data-captured-cancel hidden>Cancel calculation</button><button type="button" data-captured-compare>View both together</button></nav><p data-captured-status role="status">'+esc(text)+'</p>';
      m.host.querySelector('[data-captured-live]').onclick=showLive;
      m.host.querySelector('[data-captured-run]').onclick=()=>owner?.run();
      m.host.querySelector('[data-captured-cancel]').onclick=()=>owner?.cancel();
      m.host.querySelector('[data-captured-compare]').onclick=()=>owner?.showPair();
      for(const button of m.host.querySelectorAll('[data-captured-case]'))button.onclick=()=>owner?.selectCase(button.dataset.capturedCase);
    }
  }
  function renderMirror(m){
    if(!capture||!controller)return;
    m.view?.destroy();root.KinefoldPlotly?.purge(m.host);
    const c=capture.candidate,record=capture.runs[m.engine],payload=record.payload;
    m.host.innerHTML='<div class="captured-replay-heading"><div><span class="eyebrow">SAVED COMPARISON REPLAY · READ ONLY</span><h2>'+esc(m.engine==='analytical'?'Analytical':'Pymunk')+' · '+esc(names[capture.kind])+'</h2><p>'+esc(c.motorName||c.motorId)+' / '+esc(c.gearboxName||c.gearboxId)+' · exact saved input and motor limits</p></div><button type="button" data-captured-live>Return to live design</button></div><nav class="dyn-toolbar" aria-label="Saved comparison cases">'+cases.map(k=>'<button type="button" data-captured-case="'+k+'" aria-pressed="'+(k===capture.kind)+'">'+names[k]+'</button>').join('')+'<button type="button" data-captured-compare>View both together</button><button type="button" data-captured-run hidden>Run captured case in both engines</button><button type="button" data-captured-cancel hidden>Cancel calculation</button><button type="button" data-captured-export>Save captured replay JSON</button></nav><p data-captured-status role="status">Captured result · '+esc(record.assessment?.status||'recorded')+' · source study '+esc(capture.originalJobId)+'</p><div data-captured-player></div><details data-captured-plots><summary>Captured '+esc(names[capture.kind].toLowerCase())+' result plots</summary><div class="auto-charts"></div></details><details><summary>Exact saved simulation settings</summary><pre>'+esc(JSON.stringify({settingsHash:capture.settingsHash,engine:m.engine,payload},null,2))+'</pre></details>';
    m.view=root.KinefoldComparisonReplay.mount(m.host.querySelector('[data-captured-player]'),controller,{engines:[m.engine]});
    m.host.querySelector('[data-captured-live]').onclick=showLive;
    m.host.querySelector('[data-captured-compare]').onclick=()=>owner?.showPair();
    m.host.querySelector('[data-captured-run]').onclick=()=>owner?.run();
    m.host.querySelector('[data-captured-cancel]').onclick=()=>owner?.cancel();
    for(const button of m.host.querySelectorAll('[data-captured-case]'))button.onclick=()=>owner?.selectCase(button.dataset.capturedCase);
    m.host.querySelector('[data-captured-export]').onclick=async()=>{
      try{await root.KinefoldStudio.saveArtifact('kinefold-captured-'+capture.originalJobId+'-'+capture.kind+'.json',controller.getBundle());}
      catch(error){message('Export failed: '+error.message);}
    };
    m.host.querySelector('[data-captured-plots]').addEventListener('toggle',()=>mirrorCharts(m));
  }
  function openInTab(engine){
    if(!controller||!capture)throw Error('Load a recorded pair before opening a solver view.');
    root.KinefoldLiveDynamics?.pauseAll();const m=ensureMirror(engine);if(!m.view)renderMirror(m);
    m.live.hidden=true;m.host.hidden=false;
    root.KinefoldStudio.showTab(engine);m.view?.refresh();root.KinefoldPlotly?.resizeAll(m.host);
  }
  function mount(host,options){
    const request=options.request||defaultRequest,jobId=options.jobId,candidateId=options.candidateId;
    let closed=false,generation=0,timer=null,replayId=null,working=false,kind='landing',readyPair=false;
    host.classList.add('comparison-case-replay');
    host.innerHTML='<h3>Replay this motor / gearbox combination</h3><p>Both engines use the study’s exact captured mechanism, contact input, motor limits and controller settings. One shared clock drives the two animations. Additional case runs are saved separately; the original comparison table remains the captured batch.</p><div class="dyn-toolbar">'+cases.map(k=>'<button type="button" data-case-kind="'+k+'" aria-pressed="'+(k===kind)+'">'+names[k]+'</button>').join('')+'<button type="button" data-case-run hidden>Run captured case in both engines</button><button type="button" data-case-cancel hidden>Cancel calculation</button><button type="button" data-case-tab="analytical" disabled>Open in Analytical tab</button><button type="button" data-case-tab="pymunk" disabled>Open in Pymunk tab</button></div><p data-case-status role="status">Loading saved landing frames…</p><div data-case-player></div>';
    const $=s=>host.querySelector(s),player=$('[data-case-player]');
    const alive=n=>!closed&&generation===n;
    const clearPoll=()=>{if(timer!==null)clearTimeout(timer);timer=null;};
    const api=async body=>{const r=await request(body);if(r?.error||r?.ok===false)throw Error(r.error||'Replay service rejected the request.');return r;};
    function status(text,canRun=false){
      if(closed)return;$('[data-case-status]').textContent=text;
      for(const b of host.querySelectorAll('[data-case-kind]')){b.disabled=working;b.setAttribute('aria-pressed',String(b.dataset.caseKind===kind));}
      $('[data-case-run]').hidden=!canRun;$('[data-case-run]').disabled=working;
      $('[data-case-cancel]').hidden=!working;
      for(const b of host.querySelectorAll('[data-case-tab]'))b.disabled=!readyPair;
      message(text,working,canRun);
    }
    function attach(bundle){
      if(closed)return;
      const next=root.KinefoldComparisonReplay.create(bundle);
      disposePlayback();controller=next;capture=next.getBundle();owner=view;readyPair=true;
      pairView=root.KinefoldComparisonReplay.mount(player,controller);
      for(const m of mirrors.values())renderMirror(m);
      clockSubscription=controller.subscribe(cursor);
      status('Saved '+names[kind].toLowerCase()+' pair ready · '+capture.settingsHash.slice(0,12)+' · press Play or scrub.');
    }
    async function selectCase(next){
      if(closed)return;if(working){status('Finish or cancel the current captured-case calculation before changing cases.');return;}
      if(!cases.includes(next))throw Error('Unknown replay case.');
      kind=next;const n=++generation;clearPoll();readyPair=false;disposePlayback();player.innerHTML='';owner=view;
      const loading='Loading the exact saved '+names[kind].toLowerCase()+' frames…';pendingMirrors(loading);status(loading);
      try{
        const r=await api({action:'replay',jobId,candidateId,kind});if(!alive(n))return;
        if(r.ready)attach(r.bundle);
        else if(r.replayJob?.state==='running'){replayId=r.replayJob.id;working=true;await poll(n);}
        else status('This case has no complete saved engine pair. Run it with the captured settings to enable replay.',true);
      }catch(error){if(alive(n)){readyPair=false;status('Replay unavailable: '+error.message);}}
    }
    async function poll(n){
      if(!alive(n)||!replayId)return;
      try{
        const r=await api({action:'replay-status',replayId});if(!alive(n))return;
        const job=r.replayJob;
        if(terminal.has(job.state)){
          working=false;const result=await api({action:'replay-result',replayId});if(!alive(n))return;
          if(result.ready)attach(result.bundle);
          else status('Captured-case calculation '+job.state+': '+(job.error||job.message||'No complete engine pair was recorded.'),true);
        }else{status(job.message||'Calculating the captured case in both engines…');timer=setTimeout(()=>{timer=null;poll(n);},options.pollMs??600);}
      }catch(error){if(alive(n)){working=true;status('Monitoring paused: '+error.message+'. Cancel the retained job before retrying; existing results are preserved.');}}
    }
    async function run(){
      if(closed||working)return;const n=++generation;clearPoll();working=true;readyPair=false;pause();status('Starting only the captured '+names[kind].toLowerCase()+' case in both engines…');
      try{
        const r=await api({action:'run-replay',jobId,candidateId,kind});if(!alive(n))return;
        if(r.ready){working=false;attach(r.bundle);}else{replayId=r.replayJob.id;await poll(n);}
      }catch(error){if(alive(n)){working=false;status('Captured case could not start: '+error.message,true);}}
    }
    async function cancel(){
      if(!replayId||closed)return;const n=++generation;clearPoll();
      try{await api({action:'replay-cancel',replayId});if(alive(n)){working=false;status('Captured-case calculation cancelled. Existing study data is preserved.',true);}}
      catch(error){if(alive(n))status('Cancellation failed: '+error.message);}
    }
    async function onClick(event){
      const c=event.target.closest('[data-case-kind]'),tab=event.target.closest('[data-case-tab]');
      if(c){await selectCase(c.dataset.caseKind);return;}
      if(tab){try{openInTab(tab.dataset.caseTab);}catch(error){status(error.message);}return;}
      if(event.target.closest('[data-case-run]'))await run();
      if(event.target.closest('[data-case-cancel]'))await cancel();
    }
    host.addEventListener('click',onClick);
    const view={selectCase,run,cancel,isBusy:()=>working,getState:()=>({jobId,candidateId,kind,replayId,working,ready:readyPair}),showPair(){root.KinefoldStudio.showTab('actuator');pairView?.refresh();host.scrollIntoView?.({block:'start',behavior:'smooth'});},destroy(){if(closed)return;closed=true;generation++;clearPoll();host.removeEventListener('click',onClick);if(owner===view){showLive();disposePlayback();owner=null;}}};
    owner=view;view.ready=selectCase(kind);return view;
  }
  root.addEventListener?.('kinefold-solver-tab',event=>{
    if(!controller)return;
    if(!['actuator','analytical','pymunk'].includes(event.detail?.id))controller?.pause();
    else if(event.detail.id==='actuator')pairView?.refresh();
    else mirrors.get(event.detail.id)?.view?.refresh();
  });
  root.KinefoldComparisonReplayBridge={mount,openInTab,showLive,pause,getController:()=>controller,getBundle:()=>capture,isBusy:()=>owner?.isBusy()||false};
})(globalThis);
