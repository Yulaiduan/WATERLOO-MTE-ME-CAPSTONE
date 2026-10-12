/** Browser link-length/ROM sweep. Served at /force-plots/ by Start Motion Lab.cmd.
 * Controls use mm, degrees and N; outputs are static torque charts, table, CSV
 * and config JSON. Constant net vertical load, ideal equal links; no solver run.
 */
import {defaultSweep,validate,limits,convert,sweep,compare,rad,deg,height} from './link-sweep-model.js';
const host=document.getElementById('link-sweep'),$=id=>document.getElementById('ls-'+id);
const number=(id,label,min=0,step=1)=>`<label>${label}<input id="ls-${id}" type="number" min="${min}" step="${step}"></label>`;
const options=(values)=>values.map(([value,label])=>`<option value="${value}">${label}</option>`).join('');
const select=(id,label,values)=>`<label>${label}<select id="ls-${id}">${options(values)}</select></label>`;
const segment=(id,label)=>`<label>${label}<span class="ls-pair"><input id="ls-${id}" type="number" min="0" step="0.1"><select id="ls-${id}-unit" aria-label="${label} units">${options([['mm','mm'],['deg','degrees']])}</select></span><output id="ls-${id}-equiv"></output></label>`;
host.innerHTML=`<h2>Find a link length for your wheel and usable lift</h2>
<p class="ls-intro">Reserve motion for spring preload near full extension and ground clearance near compression, then compare equal-link lengths and working angles. Choose minimum peak, minimum average, or flattest torque. All torques use a constant net vertical load per leg.</p>
<div class="ls-box"><div class="ls-grid">
${number('diameter','Wheel diameter (mm)',1)}${number('radius','Wheel radius (mm)',.5,.5)}${number('previewLink','Each link / conversion reference (mm)',1)}
${segment('start','Start buffer from full extension')}${segment('rom','Usable lift / ROM')}${segment('end','End buffer from full compression')}
<label class="ls-check"><input id="ls-nominal" type="checkbox">Nominal usable lift = wheel radius (diameter ÷ 2)</label>
</div><p class="ls-small">Fold angle q is measured from downward vertical: 0° = fully extended, 90° = fully compressed. Hip-to-hub height h = 2L cos(q). Buffer and ROM equivalents below use the reference link and its earliest allowed start. Changing units preserves that geometry at this reference length; during a sweep the chosen units stay fixed.</p></div>
<details class="ls-box" open><summary>Sweep, load & clearance</summary><div class="ls-grid">
${number('minLink','Minimum link (mm)',1)}${number('maxLink','Maximum link (mm)',1)}${number('linkStep','Link increment (mm)',.01,.1)}
${number('angleStep','Start-angle increment (degrees)',.01,.1)}${number('load','Net vertical load per leg (N)',.01,.1)}
${select('shaft','Torque coordinate',[['hip','Hip-equivalent fold torque'],['knee','Relative-knee torque (half hip)']])}
${select('weighting','Average / RMS weighting',[['travel','Uniform vertical travel'],['angle','Uniform fold angle']])}
${select('objective','Rank candidates by',[['peak','Lowest peak torque'],['mean','Lowest average torque'],['flat','Flattest torque (lowest CV)']])}
${number('chassisDepth','Chassis underside below hip (mm)',0)}${number('airGap','Minimum chassis-to-ground gap (mm)',0)}
</div><p class="ls-small">Editable demo: 100 N net load, 20 mm buffers, 200 mm chassis depth and 20 mm minimum air gap. Load excludes spring assistance and distributed link weight; enter your net load estimate. A start buffer reserves leg motion, not a calculated spring preload. Ground gap = hip-to-hub height + wheel radius − chassis depth. The stricter end-buffer / air-gap constraint applies.</p></details>
<div class="ls-actions"><button id="ls-run">Run length & angle sweep</button><button id="ls-inspect">Inspect reference link</button><button id="ls-export" disabled>Export all candidates CSV</button><button id="ls-save" disabled>Save configuration JSON</button><label>Load configuration <input id="ls-import" type="file" accept=".json,application/json"></label></div>
<p id="ls-error" role="alert" hidden></p><p id="ls-status" aria-live="polite"></p>
<div id="ls-results" hidden><div id="ls-winners" class="ls-winners"></div><p id="ls-boundary" class="ls-warning" hidden></p>
<div class="ls-plots"><div id="ls-length-plot" class="ls-plot"></div><div id="ls-trade-plot" class="ls-plot"></div></div>
<section class="ls-box"><h3>Selected geometry & torque</h3><p id="ls-selected" class="ls-small"></p><svg id="ls-diagram" viewBox="0 0 780 265" role="img" aria-label="Extended, mid-stroke and compressed leg poses"></svg><div id="ls-curve" class="ls-plot"></div><p class="ls-small">The chart shows the usable stroke only. Start/end reserves are excluded from torque averages. For a constant vertical load, required hip torque is 2FL sin(q); relative-knee torque is FL sin(q). Flatness CV = torque standard deviation ÷ mean. No motor reduction or efficiency is applied.</p></section>
<h3>Best 30 candidates for the selected ranking</h3><p class="ls-small">Click or focus a row and press Enter to inspect it. The CSV contains every feasible sampled candidate, including both limiting angle placements.</p>
<div class="ls-table"><table><thead><tr><th>Rank / link</th><th>Fold q start → end</th><th>Lift</th><th>Mean N·m</th><th>Peak N·m</th><th>RMS N·m</th><th>CV</th><th>Gap</th></tr></thead><tbody id="ls-rows"></tbody></table></div></div>
<details class="ls-box"><summary>How to interpret the optimum</summary><p class="ls-small">Results are best within your sampled lengths, angles, buffers and load assumptions. Larger links can make torque flatter while increasing its magnitude. Refine the increments and expand a boundary-winning search before choosing hardware. Uniform-travel averaging corresponds to constant vertical speed; uniform-angle averaging corresponds to constant fold speed. Neither is a mission-time average without that motion assumption. Singular full-extension poses, real spring characteristics, link weight, impacts, strength, tire deformation and 3D collisions require separate checks. The flat-ground clearance estimate assumes a level chassis and grounded wheel.</p><p class="ls-small">Force mapping follows <a href="https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-2-statics-of-open-chains/" target="_blank" rel="noreferrer">Modern Robotics: Jacobian transpose and virtual work</a>. This is an experimental sizing study.</p></details>`;
let config=defaultSweep(),result=null,selected=null,resultConfig=null,dirty=false;
const memory='motion-lab-link-sweep/v1';
try { const saved=JSON.parse(sessionStorage.getItem(memory)||'null');if(saved){validate(saved);config=saved;} } catch {}
const fmt=(x,n=2)=>Number(x).toFixed(n);
function sync() {
  for (const key of ['diameter','previewLink','minLink','maxLink','linkStep','angleStep','load','shaft','weighting','objective','chassisDepth','airGap']) $(key).value=config[key];
  $('radius').value=config.diameter/2;$('nominal').checked=config.nominal;
  for (const key of ['start','rom','end']) {$(key).value=config[key].value;$(key+'-unit').value=config[key].unit;}
  equivalents();
}
function read() {
  const c={...config};
  for(const key of ['diameter','previewLink','minLink','maxLink','linkStep','angleStep','load','chassisDepth','airGap'])
    c[key]=$(key).value.trim()===''?NaN:Number($(key).value);
  for(const key of ['shaft','weighting','objective']) c[key]=$(key).value;
  c.nominal=$('nominal').checked;
  for(const key of ['start','rom','end']) c[key]={value:$(key).value.trim()===''?NaN:Number($(key).value),unit:$(key+'-unit').value};
  if (c.nominal) c.rom={value:c.diameter/2,unit:'mm'};
  validate(c);return c;
}
function error(e){$('error').hidden=false;$('error').textContent=e.message;}
function equivalents() {
  $('rom').disabled=config.nominal;$('rom-unit').disabled=config.nominal;
  if(config.nominal){config.rom={value:config.diameter/2,unit:'mm'};$('rom').value=config.rom.value;$('rom-unit').value='mm';}
  for(const key of ['start','rom','end']) {
    const other=config[key].unit==='mm'?'deg':'mm';
    try {$(key+'-equiv').textContent=`≈ ${fmt(convert(config,config.previewLink,key,other))} ${other==='deg'?'°':other} at L = ${config.previewLink} mm`;} catch(e){$(key+'-equiv').textContent=e.message;}
  }
  const bound=limits(config,config.previewLink);
  if(bound)$('end-equiv').textContent+=` · allowed q ≤ ${fmt(deg(bound.qMax))}° incl. clearance`;
}
function persist(){try{sessionStorage.setItem(memory,JSON.stringify(config));}catch{}}
function markDirty() {dirty=true;$('results').classList.add('ls-stale');$('export').disabled=true;$('save').disabled=true;$('status').textContent='Inputs changed. Run the sweep to update the results.';}
host.querySelectorAll('input:not([type=file]),select').forEach(node=>{
  node.addEventListener('change',()=>{
    try {
      if(node.id.endsWith('-unit')) {
        const key=node.id.slice(3,-5),target=node.value;
        // Use the previous unit but all current numeric dimensions.
        const previous=config[key].unit;node.value=previous;const c=read();node.value=target;
        const value=convert(c,c.previewLink,key,target);$(key).value=Number(value.toFixed(target==='mm'?6:10));
      }
      if(node.id==='ls-radius') $('diameter').value=Number(node.value)*2;
      config=read();$('radius').value=config.diameter/2;equivalents();persist();$('error').hidden=true;markDirty();
    } catch(e) {if(node.id.endsWith('-unit'))node.value=config[node.id.slice(3,-5)].unit;error(e);markDirty();}
  });
});
const plotOptions={responsive:true,scrollZoom:true,displaylogo:false,toImageButtonOptions:{format:'png',scale:2}};
function style(title,x,y) {
  const dark=document.documentElement.dataset.theme==='dark';
  return {title:{text:title,font:{size:16}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
    font:{color:getComputedStyle(host).color|| (dark?'#ddd':'#222')},height:340,
    margin:{l:65,r:20,t:60,b:65},legend:{orientation:'h',y:1.13},
    xaxis:{title:{text:x},automargin:true},yaxis:{title:{text:y},automargin:true}};
}
function charts() {
  if(!result?.best)return;
  const c=resultConfig,e=result.envelope;
  Plotly.react($('length-plot'),['peak','mean','rms'].map((key,i)=>({x:e.map(r=>r.link),y:e.map(r=>r[key]),name:key,type:'scatter',mode:'lines+markers',line:{color:['#cf7540','#287eb8','#238b77'][i]},customdata:e.map(r=>[r.startDeg,r.endDeg]),hovertemplate:'L %{x:.1f} mm<br>%{y:.3f} N·m<br>q %{customdata[0]:.2f}–%{customdata[1]:.2f}°<extra>%{fullData.name}</extra>'})),style('Best angle window at each link length','Each link L (mm)',`${c.shaft} torque (N·m)`),plotOptions);
  Plotly.react($('trade-plot'),[{x:e.map(r=>r.peak),y:e.map(r=>100*r.cv),text:e.map(r=>`L ${fmt(r.link,1)} mm · q ${fmt(r.startDeg,1)}–${fmt(r.endDeg,1)}°`),type:'scatter',mode:'markers',marker:{size:9,color:e.map(r=>r.link),colorscale:'Viridis',showscale:true,colorbar:{title:{text:'L mm'}}},hovertemplate:'%{text}<br>Peak %{x:.3f} N·m<br>CV %{y:.2f}%<extra></extra>'}],style('Torque magnitude / flatness tradeoff','Peak torque (N·m)','Torque CV (%)'),plotOptions);
  for(const id of ['length-plot','trade-plot']) {
    $(id).removeAllListeners('plotly_click');$(id).on('plotly_click',e=>{if(!dirty)choose(result.envelope[e.points[0].pointIndex]);});
  }
  if(selected)drawSelected();
}
function choose(row) {selected=row;drawSelected();host.querySelectorAll('#ls-rows tr').forEach(tr=>tr.setAttribute('aria-selected',result.rows[Number(tr.dataset.row)]===row?'true':'false'));}
function drawSelected() {
  const r=selected,c=resultConfig;
  $('selected').textContent=`L = ${fmt(r.link,1)} mm each (L/D = ${fmt(r.ratio,3)}). Fold q ${fmt(r.startDeg)}° → ${fmt(r.endDeg)}°; from horizontal θ ${fmt(r.thetaStartDeg)}° → ${fmt(r.thetaEndDeg)}°. Usable lift ${fmt(r.travel)} mm (${fmt(r.endDeg-r.startDeg)}°). Actual start reserve ${fmt(r.startMM)} mm (${fmt(r.startDeg)}°); end reserve ${fmt(r.endMM)} mm (${fmt(90-r.endDeg)}°). End ground gap ${fmt(r.groundGap)} mm. ${c.weighting}-average ${fmt(r.mean)} / peak ${fmt(r.peak)} / RMS ${fmt(r.rms)} N·m; CV ${fmt(100*r.cv)}%.`;
  const scale=Math.min(.36,170/(2*r.link+c.diameter/2+c.chassisDepth)),R=c.diameter/2;
  const poses=[rad(r.startDeg),Math.acos((height(r.link,rad(r.startDeg))+height(r.link,rad(r.endDeg)))/(4*r.link)),rad(r.endDeg)];
  $('diagram').innerHTML=poses.map((q,i)=>{
    const x=65+i*255,y=42,kx=x+r.link*Math.sin(q)*scale,ky=y+r.link*Math.cos(q)*scale,wy=y+height(r.link,q)*scale,ground=wy+R*scale,under=y+c.chassisDepth*scale;
    return `<g><text x="${x-40}" y="18">${['Start after buffer','Half lift','End before buffer'][i]}</text><rect x="${x-35}" y="${y-4}" width="70" height="${Math.max(4,c.chassisDepth*scale)}" fill="currentColor" opacity=".1"/><path d="M${x},${y}L${kx},${ky}L${x},${wy}" stroke="#287eb8" stroke-width="5" fill="none"/><circle cx="${x}" cy="${wy}" r="${R*scale}" fill="none" stroke="currentColor" stroke-width="2"/><path d="M${x-45},${ground}h155" stroke="currentColor"/><path d="M${x+95},${under}V${ground}" stroke="#238b77" stroke-dasharray="3 3"/><text x="${x-40}" y="${Math.max(ground,under)+22}">q ${fmt(deg(q),1)}° · gap ${fmt(height(r.link,q)+R-c.chassisDepth,1)} mm</text></g>`;
  }).join('');
  const points=Array.from({length:201},(_,i)=>{
    const lift=r.travel*i/200,q=Math.acos((height(r.link,rad(r.startDeg))-lift)/(2*r.link));
    return {lift,q:deg(q),torque:c.load*(c.shaft==='hip'?2:1)*r.link/1000*Math.sin(q)};
  });
  Plotly.react($('curve'),[{x:points.map(p=>p.lift),y:points.map(p=>p.torque),customdata:points.map(p=>p.q),type:'scatter',mode:'lines',name:'Required torque',line:{color:'#287eb8',width:3},hovertemplate:'Lift %{x:.2f} mm<br>q %{customdata:.2f}°<br>%{y:.3f} N·m<extra></extra>'}],{...style('Required torque through the usable lift','Upward wheel lift from start (mm)',`${c.shaft} torque (N·m)`),shapes:[{type:'line',x0:0,x1:r.travel,y0:r.mean,y1:r.mean,line:{color:'#238b77',dash:'dash'}}]},plotOptions);
}
function run() {
  try {
    config=read();equivalents();persist();result=sweep(config);resultConfig=structuredClone(config);selected=null;dirty=false;
    $('error').hidden=true;$('results').classList.remove('ls-stale');$('results').hidden=!result.best;
    $('export').disabled=!result.best;$('save').disabled=false;
    if(!result.best){$('status').textContent='No feasible candidates. Increase link length, reduce lift/buffers, or revise chassis depth/air gap.';return;}
    $('status').textContent=`${result.rows.length.toLocaleString()} feasible length/angle candidates · ${result.envelope.length} feasible lengths · ${config.weighting} weighting · ${config.shaft} torque · static ${config.load} N per leg.`;
    $('boundary').hidden=!result.boundary;$('boundary').textContent='The selected winner lies on a link-length search boundary. Expand the range and refine the increments before interpreting an optimum.';
    const winners=[['peak','Lowest peak'],['mean','Lowest average'],['flat','Flattest torque']].map(([objective,label])=>({label,row:[...result.rows].sort((a,b)=>compare({...config,objective},a,b))[0]}));
    $('winners').innerHTML=winners.map(({label,row},i)=>`<button class="ls-winner" data-winner="${i}"><strong>${label}: ${fmt(row.link,1)} mm links</strong>Mean ${fmt(row.mean)} · peak ${fmt(row.peak)} N·m<br>CV ${fmt(row.cv*100)}% · q ${fmt(row.startDeg,1)}–${fmt(row.endDeg,1)}°</button>`).join('');
    $('winners').querySelectorAll('button').forEach((b,i)=>b.onclick=()=>{if(!dirty)choose(winners[i].row);});
    $('rows').innerHTML=result.rows.slice(0,30).map((r,i)=>`<tr tabindex="0" data-row="${i}" aria-selected="false"><td>${i+1} · ${fmt(r.link,1)} mm</td><td>${fmt(r.startDeg,1)} → ${fmt(r.endDeg,1)}°</td><td>${fmt(r.travel,1)} mm</td><td>${fmt(r.mean)}</td><td>${fmt(r.peak)}</td><td>${fmt(r.rms)}</td><td>${fmt(r.cv*100)}%</td><td>${fmt(r.groundGap,1)} mm</td></tr>`).join('');
    $('rows').querySelectorAll('tr').forEach(tr=>{tr.onclick=()=>{if(!dirty)choose(result.rows[Number(tr.dataset.row)]);};tr.onkeydown=e=>{if(e.key==='Enter')tr.click();};});
    selected=result.best;charts();choose(selected);
  }catch(e){error(e);markDirty();}
}
$('run').onclick=run;
$('inspect').onclick=()=>{
  try {
    if(dirty||!resultConfig)run();if(dirty)return;
    if(!result?.best)throw Error('Include a feasible reference length in the sweep range and run again before inspecting it.');
    const L=Number($('previewLink').value),exact=sweep({...resultConfig,minLink:L,maxLink:L});
    if(!exact.best)throw Error('The reference link cannot fit the requested lift and buffers.');
    $('results').hidden=false;choose(exact.best);
  }catch(e){error(e);}
};
function download(name,data,type){const url=URL.createObjectURL(new Blob([data],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('export').onclick=()=>{
  if(dirty||!result?.best)return;
  const keys=['link','startDeg','endDeg','thetaStartDeg','thetaEndDeg','travel','startMM','endMM','groundGap','min','mean','peak','rms','cv','peakMean','ratio'];
  const headers=['link_mm','q_start_deg','q_end_deg','theta_start_deg','theta_end_deg','usable_lift_mm','actual_start_reserve_mm','actual_end_reserve_mm','ground_gap_mm','min_torque_Nm','mean_torque_Nm','peak_torque_Nm','rms_torque_Nm','cv','peak_to_mean','link_over_diameter'];
  download('wheel-link-candidates.csv',[headers.join(',')+',shaft,weighting,load_N,wheel_diameter_mm',...result.rows.map(r=>keys.map(k=>r[k]).join(',')+`,${resultConfig.shaft},${resultConfig.weighting},${resultConfig.load},${resultConfig.diameter}`)].join('\n'),'text/csv');
};
$('save').onclick=()=>{if(!dirty)download('wheel-link-sweep.json',JSON.stringify({schema:'motion-lab-link-sweep/v1',config:resultConfig,selected,scope:'Ideal equal-link 2:1 guide, constant net load; static sizing only.'},null,2),'application/json');};
$('import').onchange=async e=>{
  try {const file=e.target.files[0];if(!file)return;if(file.size>100000)throw Error('Configuration JSON is too large.');
    const data=JSON.parse(await file.text());if(data.schema!=='motion-lab-link-sweep/v1')throw Error('Unknown sweep configuration schema.');
    validate(data.config);config=data.config;sync();run();
  }catch(err){error(err);}finally{e.target.value='';}
};
document.addEventListener('motion-lab-theme',()=>charts());
window.addEventListener('message',e=>{if(e.origin===location.origin&&e.data?.type==='motion-lab-theme')requestAnimationFrame(charts);});
sync();run();
