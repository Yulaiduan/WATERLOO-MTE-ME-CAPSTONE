/** Fixed-GR frequency sweep UI. Browser entry create(hooks), read-only study.
 * Uses current geometry, selected motor and all supply profiles; W/s/A and kHz.
 * Background search, cancellation and plots; does not write libraries.
 */
const VSLFixedFrequencyUI=(()=>{
 const keys=[['heightM','Max fall height','m'],['speedSafetyFactor','SF',''],['torqueCeilingNm','Torque ceiling','Nm'],['initialOmega2Rpm','Hip speed at touchdown','rpm'],['omega2Rpm','Max hip speed','rpm'],['powerW','Max power','W'],['timeS','Recovery time','s'],['payload','Total payload','kg']];
 const num=v=>Number.isFinite(v)?Number(v.toPrecision(4)).toString():'—';
 function create(hooks){
  const $=id=>document.getElementById(id);let worker=null,serial=0,data=null,runKey='';
  $('frequency').insertAdjacentHTML('beforebegin',`<details id="fixed-frequency" open><summary>Switching frequency sweep, selected Kv, fixed GR</summary><div class="lab-row"><button id="fixed-frequency-go">Calculate switching freq sweep</button><button id="fixed-frequency-cancel" hidden>Cancel</button><label>Restriction<select id="fixed-frequency-mode"><option value="0">Unrestricted</option><option value="1">Power limit</option><option value="2">Power + thermal</option></select></label><span id="fixed-frequency-status" role="status">Ready</span></div><div class="frequency-scroll"><div class="frequency-grid">${keys.map(([k,title,u])=>`<div class="frequency-plot"><strong>${title} <small>${u}</small></strong><svg id="fixed-frequency-${k}" viewBox="0 0 300 180" aria-label="${title} versus switching frequency"></svg></div>`).join('')}</div></div><div class="frequency-legend" id="fixed-frequency-legend"></div></details>`);
  function key(){return VSLFallAnalysis.key(hooks.getParameters(),1)+JSON.stringify([hooks.getLibraries().conditions,hooks.getGearRatio()]);}
  function stop(){worker?.terminate();worker=null;$('fixed-frequency-go').disabled=false;$('fixed-frequency-cancel').hidden=true;}
  function sync(){
   $('fixed-frequency-mode').value=hooks.getParameters().fixedMotorSweepRestriction??'2';
   if(runKey&&runKey!==key()){$('fixed-frequency-status').textContent='Inputs changed — calculate again';$('fixed-frequency').classList.add('stale');stop();serial++;}
  }
  function render(){
   if(!data)return;
   const mode=+$('fixed-frequency-mode').value,reference=data.results[0]?.motor.id;
   const motors=[...new Map(data.results.map(r=>[r.motor.id,r.motor])).values()];
   const colors=['#168b93','#386cc2','#c06722','#7756a3','#9c4279'];
   for(const [k,,unit] of keys){
    const svg=$('fixed-frequency-'+k),all=false,series=motors.filter(m=>all||m.id===reference).map(m=>data.results.filter(r=>r.motor.id===m.id).sort((a,b)=>a.supply.khz-b.supply.khz).map(r=>({x:r.supply.khz,y:k==='payload'?(r.payload?.valid?r.payload.totalKg:null):r.rows[mode]?.valid?r.rows[mode][k]:null,source:r})));
    const values=series.flat().map(r=>r.y),bounds=VSLPlot.bounds(values,false),xs=series.flat().map(r=>r.x),lo=Math.min(...xs),hi=Math.max(...xs),x=v=>45+(v-lo)/(hi-lo||1)*240,y=v=>150-(v-bounds.min)/(bounds.max-bounds.min)*125;
    let markup=VSLPlot.ticks(bounds.min,bounds.max,k==='speedSafetyFactor'?[1]:[0]).map(v=>`<line x1="45" x2="285" y1="${y(v)}" y2="${y(v)}" stroke="#e5ecef"/><text x="40" y="${y(v)+4}" text-anchor="end">${num(v)}</text>`).join('');
    for(const f of Array.from({length:6},(_,i)=>lo+(hi-lo)*i/5))markup+=`<text x="${x(f)}" y="166" text-anchor="middle">${num(f)}</text>`;
    series.forEach((s,i)=>{let d='',pen=false;for(const r of s){if(!Number.isFinite(r.y)){pen=false;continue;}d+=(pen?' L ':' M ')+x(r.x)+' '+y(r.y);pen=true;}markup+=`<path fill="none" stroke="${colors[i%colors.length]}" stroke-dasharray="${i?'5 3':''}" stroke-width="2" d="${d}"/>`+s.filter(r=>Number.isFinite(r.y)).map(r=>`<circle cx="${x(r.x)}" cy="${y(r.y)}" r="2.5" fill="${colors[i%colors.length]}"/>`).join('');});
    if(!values.some(Number.isFinite))markup+='<text x="150" y="80" text-anchor="middle">No feasible result</text>';
    markup+=`<text x="130" y="178">Switching frequency (kHz)</text>`;svg.innerHTML=markup;svg.dataset.seriesCount=series.length;
    svg.onpointermove=ev=>{const rect=svg.getBoundingClientRect(),target=lo+((ev.clientX-rect.left)/rect.width*300-45)/240*(hi-lo),nearest=series[0].reduce((a,r)=>!a||Math.abs(r.x-target)<Math.abs(a.x-target)?r:a,null);svg.querySelector('title')?.remove();const title=document.createElementNS('http://www.w3.org/2000/svg','title');title.textContent=nearest?.source.supply.comment+'\n'+series.map((s,i)=>motors[i].kv+' KV: '+num(s.find(r=>r.x===nearest?.x)?.y)+' '+unit).join('\n');if(nearest&&k!=='payload'&&!nearest.source.rows[mode]?.valid)title.textContent+='\n'+(nearest.source.rows[mode]?.reason??nearest.source.reason??'No feasible catch.');svg.prepend(title);};
   }
   $('fixed-frequency-legend').innerHTML=motors.map((m,i)=>`<span style="color:${colors[i%colors.length]}">${m.kv} KV</span>`).join('')+'<p>Fixed GR '+num(data.gearRatio)+' · selected '+num(data.motorKV)+' KV. Hip speed means immediately after touchdown; max hip speed is the recovery peak.</p><p>Supply ratings determine free speed and limits; the selected phase KV/Kt overrides are retained. Static payload uses this same GR.</p>';
  }
  $('fixed-frequency-mode').onchange=()=>{hooks.onChange({fixedMotorSweepRestriction:$('fixed-frequency-mode').value});render();};
  $('fixed-frequency-cancel').onclick=()=>{stop();serial++;$('fixed-frequency-status').textContent='Cancelled';};
  $('fixed-frequency-go').onclick=()=>{
   stop();const gr=hooks.getGearRatio();if(!(Number.isFinite(gr)&&gr>0)){$('fixed-frequency-status').textContent='Resolve a positive GR in the motor input box first.';return;}const id=++serial;runKey=key();$('fixed-frequency-go').disabled=true;$('fixed-frequency-cancel').hidden=false;$('fixed-frequency-status').textContent='Calculating…';
   const libs=hooks.getLibraries(),src=hooks.getModelSources()+'\n'+VSLFallModel.toString()+'\nconst VSLFall=VSLFallModel();\n'+VSLMotorLimitsModel.toString()+`\nonmessage=e=>{try{postMessage({result:VSLMotorLimitsModel().fixedSweep(e.data.p,e.data.gr,e.data.s,progress=>postMessage({progress}))});}catch(error){postMessage({error:error.message});}};`;
   const url=URL.createObjectURL(new Blob([src],{type:'text/javascript'}));worker=new Worker(url);URL.revokeObjectURL(url);
   worker.onmessage=e=>{if(id!==serial)return;if(e.data.progress!=null){$('fixed-frequency-status').textContent='Calculating… '+Math.round(e.data.progress*100)+'%';return;}stop();if(e.data.error){$('fixed-frequency-status').textContent=e.data.error;return;}data=e.data.result;$('fixed-frequency-status').textContent='Complete';$('fixed-frequency').classList.remove('stale');render();};
   worker.onerror=e=>{stop();$('fixed-frequency-status').textContent='Failed: '+e.message;};worker.postMessage({p:hooks.getParameters(),gr,s:libs.conditions});
  };
  return {sync};
 }
 return {create};
})();
