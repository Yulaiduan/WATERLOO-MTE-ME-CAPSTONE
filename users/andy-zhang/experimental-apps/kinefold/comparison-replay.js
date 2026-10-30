/** Paired saved-case playback with one clock and the existing contact SVG renderer.
 * Load after contact-render.js. Inputs: comparison-replay-v1 exact captured payloads,
 * SI seconds and aligned world-mm/degree result rows/frames. Outputs: read-only
 * synchronized pair/single-engine mirrors and standalone SVG previews. No physics,
 * interpolation, network requests, Studio writes or hardware-validation claims.
 */
(function(root){
  'use strict';
  const ENGINES=['analytical','pymunk'],KINDS=['landing','jump','terrain'],EPS=1e-9;
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt=(v,n=3)=>Number.isFinite(v)?v.toFixed(n):'—';
  const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
  const canonical=v=>Array.isArray(v)?'['+v.map(canonical).join(',')+']':object(v)?'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}':JSON.stringify(v);
  function copy(value){
    return JSON.parse(JSON.stringify(value,(_key,v)=>{
      if(typeof v==='number'&&!Number.isFinite(v))throw Error('Replay contains a nonfinite number.');
      if(typeof v==='function'||typeof v==='symbol'||typeof v==='bigint')throw Error('Replay contains a non-JSON value.');
      return v;
    }));
  }
  function freeze(v){if(v&&typeof v==='object'){Object.freeze(v);for(const x of Object.values(v))freeze(x);}return v;}
  function equal(a,b,label){if(canonical(a)!==canonical(b))throw Error('Captured '+label+' do not match. Reload the exact saved case.');}
  function point(v,label){if(!Array.isArray(v)||v.length!==3||!v.every(Number.isFinite))throw Error(label+' must be a finite world-mm point.');}
  function finite(v,label){if(!Number.isFinite(v))throw Error(label+' must be finite.');}
  function settings(payload){const {engine,...rest}=payload;return rest;}
  function validate(raw){
    const b=copy(raw);
    if(!object(b)||b.schema!=='kinefold/comparison-replay-v1'||!KINDS.includes(b.kind))throw Error('Choose a saved landing, jump or terrain replay.');
    if(typeof b.originalJobId!=='string'||!/^[a-f0-9]{32}$/.test(b.originalJobId))throw Error('Replay has no valid original job identity.');
    if(!object(b.candidate)||typeof b.candidateId!=='string'||b.candidate.id!==b.candidateId)throw Error('Replay candidate identities do not match.');
    if(typeof b.settingsHash!=='string'||!/^[a-f0-9]{64}$/.test(b.settingsHash))throw Error('Replay has no valid captured settings hash.');
    if(!object(b.runs)||ENGINES.some(e=>!object(b.runs[e])))throw Error('Both saved engines are required for synchronized replay.');
    let firstSettings=null;
    for(const engine of ENGINES){
      const record=b.runs[engine],p=record.payload,r=record.result;
      if(!object(p)||!object(r)||p.engine!==engine||r.engine!==engine)throw Error('Replay engine identities do not match '+engine+'.');
      if(r.schema!=='kinefold/contact-v2')throw Error('Replay requires a captured actual-contact trajectory.');
      if(record.candidateId!==undefined&&record.candidateId!==b.candidateId)throw Error('Saved engine belongs to another candidate.');
      if(record.kind!==undefined&&record.kind!==b.kind)throw Error('Saved record belongs to another case.');
      if(record.engine!==undefined&&record.engine!==engine)throw Error('Saved record belongs to another engine.');
      const kind=b.kind==='terrain'?'terrain-stability':b.kind;
      if(p.caseConfig?.kind!==kind||r.caseConfig?.kind!==kind)throw Error('Saved engine belongs to another case.');
      for(const key of ['params','runConfig','contactConfig','caseConfig','motorConfig','actuatorConfig']){
        if(!object(p[key])||!object(r[key]))throw Error(engine+' replay is missing captured '+key+'.');
        equal(p[key],r[key],engine+' '+key);
        const snapshotKey=key==='runConfig'?'solverConfig':key;
        if(r.snapshot?.[snapshotKey]!==undefined)equal(p[key],r.snapshot[snapshotKey],engine+' snapshot '+key);
      }
      const numericParams=new Set(['m1','rw',...Object.entries(root.Kinefold?.defaults||{}).filter(([,v])=>typeof v==='number').map(([k])=>k)]);
      for(const key of numericParams)finite(p.params[key],engine+' geometry '+key);
      if(!(p.params.m1>0&&p.params.rw>0))throw Error('Replay needs positive captured chassis mass and wheel radius.');
      equal(p.terrainConfig,r.terrainConfig,engine+' terrain');
      if(r.snapshot?.terrainConfig!==undefined)equal(p.terrainConfig,r.snapshot.terrainConfig,engine+' snapshot terrain');
      if(p.contactConfig.mode!=='terrain-contact')throw Error('Saved motor replay requires actual terrain-contact results.');
      if(b.candidate.hardware?.actuatorConfig)equal(p.actuatorConfig,b.candidate.hardware.actuatorConfig,'candidate actuator limits');
      if(b.candidate.hardware?.rotorInertiaKgM2!==undefined)equal(p.motorConfig.rotorInertiaKgM2,b.candidate.hardware.rotorInertiaKgM2,'candidate rotor inertia');
      if(b.project?.params)equal(p.params,b.project.params,'saved mechanism geometry');
      if(firstSettings===null)firstSettings=settings(p);else equal(firstSettings,settings(p),'analytical/Pymunk payload settings');
      if(!Array.isArray(r.rows)||!r.rows.length||!Array.isArray(r.frames)||r.frames.length!==r.rows.length)throw Error(engine+' replay rows and frames are missing or misaligned.');
      if(r.rows.length>100000)throw Error('Replay exceeds the supported frame budget.');
      let previous=-Infinity;
      for(let i=0;i<r.rows.length;i++){
        const row=r.rows[i],frame=r.frames[i];
        if(!object(row)||!object(frame))throw Error(engine+' has an invalid saved sample.');
        finite(row.t,engine+' row time');finite(frame.t,engine+' frame time');
        if(row.t<0||row.t<previous||Math.abs(row.t-frame.t)>EPS)throw Error(engine+' replay timestamps are not aligned and monotonic.');
        previous=row.t;
        for(const key of ['A','B','C'])point(frame[key],engine+' '+key);
        for(const key of ['theta2','theta4','theta5','theta6','wheelAngle'])finite(frame[key],engine+' frame '+key);
        finite(row.theta2,engine+' row hip angle');
        if(Math.abs(frame.theta2-row.theta2)>1e-7)throw Error(engine+' hip angle disagrees with its saved frame.');
        for(const [key,value]of [['chassisZMm',frame.A[2]],['wheelZMm',frame.C[2]],['wheelAngle',frame.wheelAngle]]){
          finite(row[key],engine+' row '+key);
          if(Math.abs(row[key]-value)>1e-6)throw Error(engine+' '+key+' disagrees with its saved frame.');
        }
        if(!object(frame.indexAnglesDeg)||['a','b','c','d','e','f'].some(k=>!Number.isFinite(frame.indexAnglesDeg[k])))throw Error(engine+' frame lacks saved pulley indices.');
        if(frame.terrainOffsetMm!==undefined)point(frame.terrainOffsetMm,engine+' terrain offset');
        if(frame.terrainPolygonsMm!==undefined){
          if(!Array.isArray(frame.terrainPolygonsMm))throw Error(engine+' frame terrain is malformed.');
          for(const poly of frame.terrainPolygonsMm){if(!Array.isArray(poly)||poly.length<3)throw Error(engine+' frame polygon is malformed.');poly.forEach(p=>point(p,engine+' frame polygon'));}
        }
      }
      if(Math.abs(r.rows[0].t)>EPS)throw Error(engine+' replay must retain the shared t = 0 origin.');
      if(!object(r.terrain)||!Array.isArray(r.terrain.polygonsMm)||!Array.isArray(r.terrain.baseSegmentMm)||r.terrain.baseSegmentMm.length!==2)throw Error(engine+' replay has no captured terrain geometry.');
      r.terrain.baseSegmentMm.forEach(p=>point(p,engine+' base segment'));
      for(const poly of r.terrain.polygonsMm){if(!Array.isArray(poly)||poly.length<3)throw Error(engine+' terrain polygon is malformed.');poly.forEach(p=>point(p,engine+' terrain polygon'));}
      if(r.terrain.contourMm!==undefined){if(!Array.isArray(r.terrain.contourMm)||r.terrain.contourMm.length<2)throw Error(engine+' terrain contour is malformed.');r.terrain.contourMm.forEach(p=>point(p,engine+' terrain contour'));}
    }
    const hashes=ENGINES.map(e=>b.runs[e].result.designHash);
    if(hashes.every(h=>typeof h==='string'))equal(hashes[0],hashes[1],'captured engine design identities');
    return freeze(b);
  }
  function sampleIndex(rows,time){
    let lo=0,hi=rows.length;
    while(lo<hi){const mid=(lo+hi)>>1;if(rows[mid].t<=time)lo=mid+1;else hi=mid;}
    return Math.max(0,lo-1);
  }
  function unionCamera(bundle,drawing){
    if(!drawing?.bounds||!drawing?.render)throw Error('Contact mechanism drawing is unavailable. Reload the app.');
    const all=ENGINES.map(e=>drawing.bounds(bundle.runs[e].result,bundle.runs[e].payload.params));
    const camera={minX:Math.min(...all.map(x=>x.minX)),maxX:Math.max(...all.map(x=>x.maxX)),minZ:Math.min(...all.map(x=>x.minZ)),maxZ:Math.max(...all.map(x=>x.maxZ))};
    if(!Object.values(camera).every(Number.isFinite)||camera.maxX<=camera.minX||camera.maxZ<=camera.minZ)throw Error('Captured replay has an invalid shared camera.');
    return freeze(camera);
  }
  function create(raw,options={}){
    const bundle=validate(raw),drawing=options.drawing||root.KinefoldContactDrawing,camera=unionCamera(bundle,drawing);
    const now=options.now||(()=>root.performance?.now?.()??Date.now());
    const request=options.requestFrame||(fn=>root.requestAnimationFrame(fn));
    const cancel=options.cancelFrame||(id=>root.cancelAnimationFrame(id));
    const ends=Object.fromEntries(ENGINES.map(e=>[e,bundle.runs[e].result.rows.at(-1).t]));
    const duration=Math.max(...Object.values(ends));
    let time=0,speed=1,playing=false,destroyed=false,frameId=null,generation=0,publication=0,baseTime=0,baseWall=now();
    const listeners=new Set(),cache=new Map();
    function engineState(engine){const rows=bundle.runs[engine].result.rows,index=sampleIndex(rows,time),sampleTime=rows[index].t;return {index,t:sampleTime,sampleTimeS:sampleTime,ended:time>=ends[engine],held:time>ends[engine],termination:bundle.runs[engine].result.diagnostics?.termination||'unknown'};}
    function getState(){return {time,timeS:time,duration,durationS:duration,playing,speed,destroyed,kind:bundle.kind,candidateId:bundle.candidateId,settingsHash:bundle.settingsHash,ends:{...ends},engines:Object.fromEntries(ENGINES.map(e=>[e,engineState(e)]))};}
    function publish(){const token=++publication,value=getState();for(const fn of [...listeners]){if(token!==publication)break;fn(value);}}
    function stopFrame(){generation++;if(frameId!==null)cancel(frameId);frameId=null;}
    function advance(wall){if(playing){time=Math.min(duration,Math.max(time,baseTime+Math.max(0,wall-baseWall)/1000*speed));if(time>=duration)playing=false;}}
    function schedule(){if(!playing||destroyed||frameId!==null)return;const token=generation;frameId=request(wall=>{if(destroyed||token!==generation||!playing)return;frameId=null;advance(Number.isFinite(wall)?wall:now());publish();if(playing)schedule();});}
    function play(){if(destroyed||playing||duration<=0)return;if(time>=duration)time=0;playing=true;baseTime=time;baseWall=now();stopFrame();publish();schedule();}
    function pause(){if(destroyed)return;advance(now());playing=false;stopFrame();publish();}
    function seek(value){if(destroyed)return;finite(value,'Replay time');time=Math.max(0,Math.min(duration,value));if(time>=duration)playing=false;baseTime=time;baseWall=now();stopFrame();publish();if(playing)schedule();}
    function setSpeed(value){if(destroyed)return;if(!Number.isFinite(value)||value<.1||value>4)throw Error('Replay speed must be between 0.1× and 4×.');advance(now());speed=value;baseTime=time;baseWall=now();stopFrame();publish();if(playing)schedule();}
    function render(engine,at=time){
      if(destroyed)throw Error('This captured replay has been replaced or closed.');
      if(!ENGINES.includes(engine))throw Error('Choose analytical or Pymunk replay.');finite(at,'Replay render time');
      const record=bundle.runs[engine],result=record.result,clock=Math.max(0,Math.min(duration,at)),index=sampleIndex(result.rows,clock);
      let view=cache.get(engine);
      if(!view||view.index!==index){const rendered=drawing.render({result,snapshot:{params:record.payload.params},index,contactBounds:camera});view={html:rendered.html,row:result.rows[index],frame:result.frames[index],index,camera};cache.set(engine,view);}
      return {...view,engine,sampleTimeS:result.rows[index].t,clockTimeS:clock,ended:clock>=ends[engine],held:clock>ends[engine]};
    }
    const api={play,pause,seek,setSpeed,restart(autoplay=false){pause();seek(0);if(autoplay)play();},getState,getBundle:()=>bundle,getCamera:()=>camera,render,subscribe(fn){if(destroyed)return()=>{};listeners.add(fn);fn(getState());return()=>listeners.delete(fn);},destroy(){if(destroyed)return;playing=false;stopFrame();destroyed=true;publish();listeners.clear();cache.clear();}};
    return api;
  }
  function mount(host,controller,options={}){
    if(!host||!controller?.subscribe||!controller?.render)throw Error('Replay mount requires a host and shared controller.');
    if(controller.getState().destroyed)throw Error('This captured replay has been replaced or closed.');
    const engines=options.engines||ENGINES;
    if(!Array.isArray(engines)||!engines.length||new Set(engines).size!==engines.length||engines.some(e=>!ENGINES.includes(e)))throw Error('Choose one or both replay engines.');
    const bundle=controller.getBundle(),title=(bundle.candidate.motorName||bundle.candidate.motorId||'Saved motor')+' / '+(bundle.candidate.gearboxName||bundle.candidate.gearboxId||'saved gearbox');
    host.classList.add('comparison-replay');
    host.innerHTML=`<div class="replay-heading"><div><span class="eyebrow">SAVED COMPARISON REPLAY · ¼ MODEL</span><h3>${esc(title)}</h3><p>${esc(bundle.kind==='terrain'?'Terrain stability':bundle.kind==='jump'?'Jump':'Landing')} · same captured settings · +x left / +z up</p></div><span class="replay-capture">Job ${esc(bundle.originalJobId.slice(0,8))}<br>Settings ${esc(bundle.settingsHash.slice(0,12))}</span></div><div class="replay-controls"><button type="button" data-replay-action="play" aria-pressed="false">Play both</button><button type="button" data-replay-action="restart">Replay from start</button><label>Playback speed<select data-replay-speed><option value="0.25">0.25×</option><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="4">4×</option></select></label><output data-replay-time></output></div><label class="replay-scrubber">Shared simulation clock<input data-replay-seek type="range" min="0" max="${controller.getState().duration}" step="0.001" value="0" aria-label="Shared comparison replay time"></label><div class="replay-error" data-replay-error role="alert"></div><div class="replay-views" data-replay-count="${engines.length}">${engines.map(e=>`<section class="replay-engine" data-replay-engine="${e}"><div class="replay-engine-heading"><strong>${e==='analytical'?'Analytical':'Pymunk'}</strong><span data-replay-sample="${e}"></span><span class="replay-verdict">${esc(bundle.runs[e].assessment?.status||'unassessed')}</span></div><svg data-replay-svg="${e}" viewBox="0 0 740 450" role="img" aria-label="${e} saved ${esc(bundle.kind)} mechanism animation"></svg><div class="replay-readouts" data-replay-readout="${e}"></div><p class="replay-events" data-replay-events="${e}"></p></section>`).join('')}</div><p class="replay-note">Playback uses saved frames at or before the shared clock, without interpolating contacts or rerunning physics. Both views use one fixed camera. An engine that ended earlier holds its last actual frame and is labelled ended.</p>`;
    const $=s=>host.querySelector(s),last=new Map();let closed=false;
    function refresh(state=controller.getState()){
      if(closed)return;
      $('[data-replay-time]').textContent=fmt(state.time)+' / '+fmt(state.duration)+' s';
      $('[data-replay-seek]').value=String(state.time);$('[data-replay-speed]').value=String(state.speed);
      const button=$('[data-replay-action="play"]');button.textContent=state.playing?'Pause both':'Play both';button.setAttribute('aria-pressed',String(state.playing));button.disabled=state.destroyed;
      if(state.destroyed){$('[data-replay-error]').textContent='This captured replay has been replaced or closed.';return;}
      if(host.hidden||host.closest?.('[hidden]'))return;
      try{
        for(const engine of engines){
          const meta=state.engines[engine],sample=$('[data-replay-sample="'+engine+'"]');
          sample.textContent='Actual sample '+fmt(meta.t)+' s'+(meta.held?' · ended; holding last frame':meta.ended?' · ended':'');
          if(last.get(engine)===meta.index)continue;
          const v=controller.render(engine),svg=$('[data-replay-svg="'+engine+'"]');svg.innerHTML=v.html;svg.dataset.time=String(v.sampleTimeS);svg.dataset.index=String(v.index);svg.dataset.theta2=String(v.frame.theta2);svg.dataset.wheelAngle=String(v.frame.wheelAngle);svg.dataset.terrainOffset=JSON.stringify(v.frame.terrainOffsetMm||[0,0,0]);
          $('[data-replay-readout="'+engine+'"]').textContent='Hip '+fmt(v.row.theta2,2)+'° · chassis '+fmt(v.row.chassisZMm,1)+' mm · clearance '+fmt(v.row.chassisClearanceMm,1)+' mm · delivered hip '+fmt(v.row.motorTorqueNm,2)+' N·m';
          const events=(bundle.runs[engine].result.events||[]).filter(e=>Number.isFinite(e.t)&&e.t<=v.sampleTimeS).slice(-3);
          $('[data-replay-events="'+engine+'"]').textContent=events.map(e=>e.type+' @ '+fmt(e.t)+' s').join(' · ')||'No captured event yet.';
          last.set(engine,meta.index);
        }
        $('[data-replay-error]').textContent='';
      }catch(error){$('[data-replay-error]').textContent='Replay drawing unavailable: '+error.message;button.disabled=true;}
    }
    const unsubscribe=controller.subscribe(refresh);
    function onClick(event){const action=event.target.closest('[data-replay-action]')?.dataset.replayAction;if(action==='play'){if(controller.getState().playing)controller.pause();else controller.play();}else if(action==='restart')controller.restart(true);}
    function onInput(event){try{if(event.target.matches('[data-replay-seek]'))controller.seek(Number(event.target.value));else if(event.target.matches('[data-replay-speed]'))controller.setSpeed(Number(event.target.value));}catch(error){$('[data-replay-error]').textContent=error.message;}}
    host.addEventListener('click',onClick);host.addEventListener('input',onInput);host.addEventListener('change',onInput);
    return {refresh(){last.clear();refresh();},destroy(){if(closed)return;closed=true;unsubscribe();host.removeEventListener('click',onClick);host.removeEventListener('input',onInput);host.removeEventListener('change',onInput);host.innerHTML='';}};
  }
  function renderFrame(value,engine,time,options={}){if(value?.render)return value.render(engine,time);const controller=create(value,options);try{return controller.render(engine,time);}finally{controller.destroy();}}
  function renderSVG(value,engine,time,options={}){
    const view=renderFrame(value,engine,time,options),colors={paper:'#fffdf7',ink:'#303c31',muted:'#737a68',line:'#dedfd1',soft:'#eeeee4',sage:'#526941','sage-soft':'#e6ebdc',amber:'#efb33e',blue:'#37839a',red:'#bd5743',purple:'#8d729e',...options.colors};
    const html=view.html.replace(/var\(--([a-z-]+)\)/g,(match,key)=>colors[key]||match);
    return `<svg xmlns="http://www.w3.org/2000/svg" width="740" height="450" viewBox="0 0 740 450" role="img"><title>${esc(engine)} saved mechanism · actual sample ${fmt(view.sampleTimeS)} s</title>${html}</svg>`;
  }
  const api={create,mount,validate,sampleIndex,renderFrame,renderSVG};root.KinefoldComparisonReplay=api;
  if(typeof module==='object'&&module.exports)module.exports=api;
})(globalThis);
