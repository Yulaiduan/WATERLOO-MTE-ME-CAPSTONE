/** Frequency sweep UI. Browser entry create(hooks), read-only study.
 * Uses current geometry and all in-memory profiles; W/s/A and kHz.
 * Background search, cancellation and plots; does not write libraries.
 */
const VSLFrequencyUI=(()=>{
 const keys=[['heightM','Max fall height','m'],['gearRatio','GR',''],['torqueCeilingNm','Torque ceiling','Nm'],['omega2Rpm','Max hip speed','rpm'],['powerW','Max power','W'],['timeS','Recovery time','s'],['payload','Total payload','kg']];
 const num=v=>Number.isFinite(v)?Number(v.toPrecision(4)).toString():'—';
 function create(hooks){
  const $=id=>document.getElementById(id);let worker=null,serial=0,data=null,runKey='';
  $('motorCapacity').insertAdjacentHTML('afterend',`<details id="frequency" open><summary>Switching frequency sweep</summary><div class="lab-row"><button id="frequency-go">Calculate switching freq sweep</button><button id="frequency-cancel" hidden>Cancel</button><label>Restriction<select id="frequency-mode"><option value="0">Unrestricted</option><option value="1">Power limit</option><option value="2">Power + thermal</option></select></label><span id="frequency-status" role="status">Ready</span></div><div class="frequency-scroll"><div class="frequency-grid">${keys.map(([k,title,u])=>`<div class="frequency-plot"><strong>${title} <small>${u}</small></strong><svg id="frequency-${k}" viewBox="0 0 300 180" aria-label="${title} versus switching frequency"></svg></div>`).join('')}<div class="frequency-legend" id="frequency-legend"></div></div></div></details>`);
  function key(){return VSLFallAnalysis.key(hooks.getParameters(),1)+JSON.stringify(hooks.getLibraries());}
  function stop(){worker?.terminate();worker=null;$('frequency-go').disabled=false;$('frequency-cancel').hidden=true;}
  function sync(){
   $('frequency-mode').value=hooks.getParameters().motorSweepRestriction??'2';
   if(runKey&&runKey!==key()){$('frequency-status').textContent='Inputs changed — calculate again';$('frequency').classList.add('stale');stop();serial++;}
  }
  function render(){
   if(!data)return;
   const mode=+$('frequency-mode').value,reference=data.results[0]?.motor.id;
   const motors=[...new Map(data.results.map(r=>[r.motor.id,r.motor])).values()];
   const colors=['#168b93','#386cc2','#c06722','#7756a3','#9c4279'];
   let overlap=true;
   for(const [k,,unit] of keys){
    const svg=$('frequency-'+k),all=k==='gearRatio'||k==='payload',series=motors.filter(m=>all||m.id===reference).map(m=>data.results.filter(r=>r.motor.id===m.id).sort((a,b)=>a.supply.khz-b.supply.khz).map(r=>({x:r.supply.khz,y:r.rows[mode]?.valid?(k==='payload'?r.rows[mode].payload?.totalKg:r.rows[mode][k]):null,source:r})));
    const values=series.flat().map(r=>r.y),bounds=VSLPlot.bounds(values,false),xs=series.flat().map(r=>r.x),lo=Math.min(...xs),hi=Math.max(...xs),x=v=>45+(v-lo)/(hi-lo||1)*240,y=v=>150-(v-bounds.min)/(bounds.max-bounds.min)*125;
    let markup=VSLPlot.ticks(bounds.min,bounds.max,[0]).map(v=>`<line x1="45" x2="285" y1="${y(v)}" y2="${y(v)}" stroke="#e5ecef"/><text x="40" y="${y(v)+4}" text-anchor="end">${num(v)}</text>`).join('');
    for(const f of Array.from({length:6},(_,i)=>lo+(hi-lo)*i/5))markup+=`<text x="${x(f)}" y="166" text-anchor="middle">${num(f)}</text>`;
    series.forEach((s,i)=>{let d='',pen=false;for(const r of s){if(!Number.isFinite(r.y)){pen=false;continue;}d+=(pen?' L ':' M ')+x(r.x)+' '+y(r.y);pen=true;}markup+=`<path fill="none" stroke="${colors[i%colors.length]}" stroke-dasharray="${i?'5 3':''}" stroke-width="2" d="${d}"/>`+s.filter(r=>Number.isFinite(r.y)).map(r=>`<circle cx="${x(r.x)}" cy="${y(r.y)}" r="2.5" fill="${colors[i%colors.length]}"/>`).join('');});
    if(!values.some(Number.isFinite))markup+='<text x="150" y="80" text-anchor="middle">No feasible result</text>';
    markup+=`<text x="130" y="178">Switching frequency (kHz)</text>`;svg.innerHTML=markup;svg.dataset.seriesCount=series.length;
    svg.onpointermove=ev=>{const rect=svg.getBoundingClientRect(),target=lo+((ev.clientX-rect.left)/rect.width*300-45)/240*(hi-lo),nearest=series[0].reduce((a,r)=>!a||Math.abs(r.x-target)<Math.abs(a.x-target)?r:a,null);svg.querySelector('title')?.remove();const title=document.createElementNS('http://www.w3.org/2000/svg','title');title.textContent=nearest?.source.supply.comment+'\n'+series.map((s,i)=>motors[i].kv+' KV: '+num(s.find(r=>r.x===nearest?.x)?.y)+' '+unit).join('\n');svg.prepend(title);};
   }
   // Overrides can break the cancellation. Never label a reference curve as shared.
   for(const r of data.results){const ref=data.results.find(x=>x.supply.id===r.supply.id&&x.motor.id===reference);for(const k of ['heightM','torqueCeilingNm','omega2Rpm','powerW','timeS'])if(ref?.rows[mode]?.valid!==r.rows[mode]?.valid||Math.abs((ref.rows[mode]?.[k]??0)-(r.rows[mode]?.[k]??0))>1e-6)overlap=false;}
   $('frequency-legend').innerHTML=motors.map((m,i)=>`<span style="color:${colors[i%colors.length]}">${m.kv} KV</span>`).join('')+'<p>SF=1. Payload uses each result’s GR.</p><p>Library ratings; live power/free-speed overrides are not used.</p>'+(overlap?'<p>Other curves overlap across KV.</p>':'<p>Overrides break overlap: other graphs show the first motor.</p>');
  }
  $('frequency-mode').onchange=()=>{hooks.onChange({motorSweepRestriction:$('frequency-mode').value});render();};
  $('frequency-cancel').onclick=()=>{stop();serial++;$('frequency-status').textContent='Cancelled';};
  $('frequency-go').onclick=()=>{
   stop();const id=++serial;runKey=key();$('frequency-go').disabled=true;$('frequency-cancel').hidden=false;$('frequency-status').textContent='Calculating…';
   const libs=hooks.getLibraries(),src=hooks.getModelSources()+'\n'+VSLFallModel.toString()+'\nconst VSLFall=VSLFallModel();\n'+VSLMotorLimitsModel.toString()+`\nonmessage=e=>{try{postMessage({result:VSLMotorLimitsModel().sweep(e.data.p,e.data.m,e.data.s,progress=>postMessage({progress}))});}catch(error){postMessage({error:error.message});}};`;
   const url=URL.createObjectURL(new Blob([src],{type:'text/javascript'}));worker=new Worker(url);URL.revokeObjectURL(url);
   worker.onmessage=e=>{if(id!==serial)return;if(e.data.progress!=null){$('frequency-status').textContent='Calculating… '+Math.round(e.data.progress*100)+'%';return;}stop();if(e.data.error){$('frequency-status').textContent=e.data.error;return;}data=e.data.result;$('frequency-status').textContent='Complete';$('frequency').classList.remove('stale');render();};
   worker.onerror=e=>{stop();$('frequency-status').textContent='Failed: '+e.message;};worker.postMessage({p:hooks.getParameters(),m:libs.motors,s:libs.conditions});
  };
  return {sync};
 }
 return {create};
})();
