import './style.css';
import {TERRAIN_PRESETS, DEFAULT_TERRAIN_CONFIG, buildTerrain, parseTerrainCsv, serializeTerrainCsv} from './terrain.js';
import {DEFAULT_MECHANISM, DEFAULT_SCENARIO, DEFAULT_ACTUATOR, linkageAtAngle, serializeResultsCsv} from './engine.js';
import measuredCsv from '../../data/terrain/usgs-shenandoah-transect-1000m.csv?raw';
import measuredProvenance from '../../data/terrain/usgs-shenandoah-provenance.json';
import {attachCharts, chartMarkup, resetCharts, nodeGraphMarkup, escapeHtml as esc, formatNumber as fmt} from './charts.js';

const root = document.querySelector('#app');
const DEM_SOURCE = measuredProvenance.service_url;
const CHAT_SOURCE = 'https://chatgpt.com/c/6abb5d6d-029c-83ea-8d0d-cab0e6a3ef19';
const SPECS_SOURCE = 'https://app.notion.com/p/3ebb26c7416c801aa3acd33e730cba0c';
const USFS_SOURCE = 'https://www.fs.usda.gov/eng/pubs/pdfpubs/pdf11232804/pdf11232804dpi100.pdf';
const measured = parseTerrainCsv(measuredCsv);
measured.metadata = {...measured.metadata, evidenceType:'observed DEM-derived profile',source:DEM_SOURCE,sourceResolutionM:1, sourceName:'USGS 3DEP · VA_Shenandoah_2014',provenance:measuredProvenance};

const state = {
  view:'terrain',terrainConfig:{...DEFAULT_TERRAIN_CONFIG},mechanism:{...DEFAULT_MECHANISM},scenario:{...DEFAULT_SCENARIO},actuator:{...DEFAULT_ACTUATOR},
  terrain:null, imported:null, importName:'', sourceMode:'periodic',cropStart:0,detailStart:0, result:null,snapshot:null,pendingSnapshot:null,stale:false,
  running:false,runId:0,error:'',resultAxis:'time',selectedNode:'terrain',exportKind:'terrain',inputRevision:0,
};
let worker;
function createSimulationWorker() {
  const simulationWorker = new Worker(new URL('./worker.js',import.meta.url),{type:'module'});
  simulationWorker.addEventListener('message',({data})=> {
    if(data.id !== state.runId) return;
    state.running = false;
    if(data.error) state.error = String(data.error);
    else {
      state.result = data.result;
      state.snapshot = state.pendingSnapshot;
      state.stale = state.inputRevision !== state.snapshot.revision;
      state.view = 'results';
    }
    state.pendingSnapshot = null;
    render();
  });
  simulationWorker.addEventListener('error',event=>{state.running=false;state.pendingSnapshot=null;state.error=`Simulation could not finish: ${event.message || 'worker error'}`;render();});
  return simulationWorker;
}
try {
  worker = createSimulationWorker();
} catch(error) {state.error = `Simulation worker unavailable: ${error.message}`;}

function updateTerrain() {
  const config = state.terrainConfig;
  if(state.sourceMode === 'measured') state.terrain = buildTerrain({...config,mode:'measured',terrain:measured,lengthM:config.lengthM});
  else if(state.sourceMode === 'import') {
    if(!state.imported) {state.terrain=null;return;}
    state.terrain=buildTerrain({...config,mode:'measured',terrain:state.imported,lengthM:Math.min(config.lengthM,state.imported.samples.at(-1).x-state.imported.samples[0].x)});
  } else state.terrain=buildTerrain({...config,mode:state.sourceMode});
}
updateTerrain();

const tabs = [['terrain','Terrain'],['mechanism','Mechanism'],['results','Results'],['graph','Node graph']];
const units = {mm:1000,deg:180/Math.PI,rpm:60/(2*Math.PI)};
function badge(text='Assumption',type='assumption'){return `<span class="evidence-tag ${type}">${esc(text)}</span>`;}
function numberInput(group,key,label,{scale=1,min=0,max,step='any',tag='Chosen',tagType='assumption',note='',disabled=false}={}) {
  if(group==='terrainConfig' && tag==='Preset' && state[group][key]!==currentPreset().defaults[key]){tag='Chosen';tagType='assumption';}
  const value = state[group][key] * scale;
  return `<label class="field"><span class="field-label"><span>${esc(label)}</span>${tag?badge(tag,tagType):''}</span><input type="number" data-group="${group}" data-key="${key}" data-scale="${scale}" value="${Number.isFinite(value)?Number(value.toFixed(6)):''}" min="${min}" ${max===undefined?'':`max="${max}"`} step="${step}" ${disabled?'disabled':''} required aria-label="${esc(label)}">${note?`<span class="field-note">${esc(note)}</span>`:''}</label>`;
}
function selectInput(group,key,label,options,note='') {
  return `<label class="field"><span class="field-label">${esc(label)}</span><select data-group="${group}" data-key="${key}" aria-label="${esc(label)}">${options.map(([value,text])=>`<option value="${value}" ${state[group][key]===value?'selected':''}>${esc(text)}</option>`).join('')}</select>${note?`<span class="field-note">${esc(note)}</span>`:''}</label>`;
}
function metric(label,value,note=''){return `<div class="metric"><span>${esc(label)}</span><strong>${value}</strong>${note?`<small>${esc(note)}</small>`:''}</div>`;}
function currentPreset(){return TERRAIN_PRESETS.find(p=>p.id===state.terrainConfig.presetId)||TERRAIN_PRESETS[2];}
function terrainName(){if(state.sourceMode==='measured')return 'USGS Shenandoah transect';if(state.sourceMode==='class3')return 'USFS Class 3 grade cycle';if(state.sourceMode==='import')return state.importName || 'Imported terrain';return `${currentPreset().label} · ${state.sourceMode==='stochastic'?'seeded random':'periodic'}`;}
function markChanged(){state.inputRevision++;if(state.result)state.stale=true;state.error='';}
function points(samples,key,scale=1){return samples.map(s=>({x:s.x,y:s[key]*scale}));}
function histPoints(pass,key,{scale=1,axis=state.resultAxis,absolute=false}={}){return (pass.fullHistory||pass.history).map(s=>({x:axis==='time'?s.timeS:s.xM,y:(absolute?Math.abs(s[key]):s[key])*scale}));}
function curve(title,yLabel,key,options={}) {
  const result=state.result;
  return chartMarkup({title,subtitle:options.subtitle || '',xLabel:state.resultAxis==='time'?'Time (s)':'Distance (m)',yLabel,series:[{label:'Ideal demand',color:'#b96a00',points:histPoints(result.ideal,key,options)},{label:'Candidate achieved',color:'#246b8e',points:histPoints(result.limited,key,options)}],referenceLines:options.referenceLines||[]});
}

function terrainInputs(){
  const synthetic=!['measured','import'].includes(state.sourceMode), class3=state.sourceMode==='class3';
  return `<aside class="input-panel" aria-label="Terrain inputs"><h3>Terrain definition</h3><label class="field"><span class="field-label">Profile source</span><select id="source-mode" aria-label="Profile source"><option value="periodic" ${state.sourceMode==='periodic'?'selected':''}>Periodic engineering cycle</option><option value="stochastic" ${state.sourceMode==='stochastic'?'selected':''}>Seeded random scenario</option><option value="class3" ${class3?'selected':''}>USFS Class 3 grade cycle</option><option value="measured" ${state.sourceMode==='measured'?'selected':''}>Observed USGS 1 m DEM</option><option value="import" ${state.sourceMode==='import'?'selected':''}>Import a terrain CSV</option></select></label>
    ${synthetic&&!class3?selectInput('terrainConfig','presetId','Terrain context',TERRAIN_PRESETS.map(p=>[p.id,p.label]),'Preset values are illustrative engineering tests, not measured biome averages.'):''}
    ${selectInput('terrainConfig','lengthM','Route length',[[100,'100 m'],[1000,'1 km']],'100 m is the start of the same 1 km realization.')}
    ${state.sourceMode==='import'?`<label class="field"><span class="field-label">CSV file</span><input id="terrain-file" type="file" accept=".csv,text/csv" aria-label="Import terrain CSV"><span class="field-note">Read on this device. No file is uploaded.</span></label><p class="import-status">${state.imported?`${esc(state.importName)} · ${fmt(state.imported.samples.length,0)} samples`:'Columns: distance_m and relative_elevation_m (or height_m). Optional baseline_m, roughness_m, obstacle_m.'}</p>`:''}
    ${synthetic?`${class3?`<p class="field-note">Published limits: 5–15% target grade; 25% short pitches. Chosen cycle: 8% base, 20 m plateau, 5 m transitions per 100 m.</p>`:numberInput('terrainConfig','gradePercent','Baseline grade (%)',{min:-100,max:100,note:'Macro slope; excludes roughness and obstacles.'})}
    <div class="section"><h3>Fine terrain layers</h3><div class="field-row">${numberInput('terrainConfig','roughnessRmsM','Roughness RMS (mm)',{scale:1000,max:1000,tag:class3?'Chosen':'Preset',tagType:class3?'assumption':'',note:'RMS of this layer only.'})}${numberInput('terrainConfig','wavelengthM',state.sourceMode==='stochastic'?'Reference length (m)':'Wavelength (m)',{min:.02,max:1000,tag:class3?'Chosen':'Preset',tagType:class3?'assumption':''})}</div><div class="field-row">${numberInput('terrainConfig','obstacleHeightM','Obstacle height (mm)',{scale:1000,max:2000,tag:class3?'Chosen':'Preset',tagType:class3?'assumption':''})}${numberInput('terrainConfig','obstacleSpacingM','Obstacle spacing (m)',{min:.02,max:1000,tag:class3?'Chosen':'Preset',tagType:class3?'assumption':''})}</div>${numberInput('terrainConfig','obstacleWidthM','Obstacle width FWHM (mm)',{scale:1000,min:10,max:100000,note:'Chosen rounded Gaussian shape.'})}</div>
    <details class="disclosure"><summary>Sampling${state.sourceMode==='stochastic'?' and seed':''}</summary>${numberInput('terrainConfig','stepM','Sample spacing (mm)',{scale:1000,min:1,max:10000,note:'More samples preserve geometry; they add no source evidence.'})}${state.sourceMode==='stochastic'?numberInput('terrainConfig','seed','Random seed',{min:0,max:4294967295,step:1,note:'Stored with the case for exact replay.'}):''}</details>`:`<div class="section"><h3>Source scale</h3><p class="field-note">${state.sourceMode==='measured'?'1 m DEM samples establish local elevation and grade. Centimetre-scale roots, rocks, roughness and soil mechanics are unresolved.':'Imported data retain their spacing. A finer display does not add measured detail. Unknown source resolution remains unknown.'}</p></div>`}
    <div class="section"><button class="run-button" data-action="export-terrain" ${state.terrain?'':'disabled'}>Preview & export terrain</button></div></aside>`;
}

function sourceCard(){
  const c=state.terrainConfig, terrain=state.terrain;
  if(!terrain)return '';
  let title,type,kind,description,links,assumptions;
  if(state.sourceMode==='measured') {
    title='Observed elevation · VA_Shenandoah_2014';type='Observed';kind='observed';description='A 1 m bare-earth DEM, sampled along a straight 1 km line in Shenandoah, Virginia. This is local topography; route traversability and biome classification are unverified.';
    links=`<a href="${DEM_SOURCE}" target="_blank" rel="noopener">USGS 3DEP source</a> · <a href="${measuredProvenance.source_attributes.URL}" target="_blank" rel="noopener">Source raster</a>`;
    assumptions=['Resolution and sample interval: 1 m. NAVD 88 elevation datum.','Fine roughness RMS, roots/rocks and cross-slope are unresolved.','Source-specific vertical accuracy was not established in this extraction.'];
  } else if(state.sourceMode==='class3') {
    title='Grade constraints from USFS ATV Class 3';type='Guideline';kind='guideline';description='Historical trail design guidance supplies slope limits. The repeating 100 m layout is a chosen test, with continuing elevation rather than a reset.';
    links=`<a href="${USFS_SOURCE}" target="_blank" rel="noopener">Original trail guide · figure 4-4</a>`;
    assumptions=['8% baseline, 25% plateau for 20 m, two 5 m transitions per 100 m are chosen.','Roughness, obstacle spacing and width are independent assumptions, not USFS values.','Pure grade case starts with roughness and obstacle layers at zero.'];
  } else if(state.sourceMode==='import') {
    title=`Imported profile · ${state.importName}`;type='Imported';kind='';description='The CSV is validated for finite, increasing distance and consistent component layers. Its source and measurement scale require your own provenance.';
    links='Source: provided file; no provenance is inferred.';assumptions=terrain.metadata.assumptions || ['Imported source resolution is unknown unless supplied.'];
  } else {
    title=`${currentPreset().label} · engineering test preset`;type='Illustrative';kind='';description=state.sourceMode==='stochastic'?'A fixed, seeded spatial realization uses a band of smooth roughness waves and variable obstacle spacing. It is not a fitted natural biome distribution.':'A sine roughness layer and regularly spaced rounded obstacles make this a reproducible engineering cycle. Terrain names provide context for explicitly chosen test values.';
    links=`<a href="${CHAT_SOURCE}" target="_blank" rel="noopener">Terrain Variability Studies</a> · <a href="${SPECS_SOURCE}" target="_blank" rel="noopener">Original terrain envelopes</a>`;
    assumptions=[`Baseline grade ${fmt(c.gradePercent)}%; Gaussian width ${fmt(c.obstacleWidthM*1000)} mm are chosen.`,state.sourceMode==='stochastic'?`Seed ${c.seed}; reference length does not imply a single repeat cycle.`:`Cycle wavelength ${fmt(c.wavelengthM)} m; frequency at ${fmt(state.scenario.speedMps)} m/s is ${fmt(state.scenario.speedMps/c.wavelengthM)} Hz.`,`Sample spacing ${fmt(c.stepM*1000)} mm; preset values are not biome measurements.`];
  }
  return `<section class="source-card"><div class="source-header"><h3>${esc(title)}</h3>${badge(type,kind)}</div><p>${esc(description)}</p><details><summary>Evidence, assumptions & source</summary><p>${links}</p><ul>${assumptions.map(a=>`<li>${esc(a)}</li>`).join('')}</ul></details></section>`;
}

function terrainPage(){
  const terrain=state.terrain, c=state.terrainConfig, isMeasured=['measured','import'].includes(state.sourceMode);
  if(!terrain)return `<div class="workbench-grid">${terrainInputs()}<div class="empty-state"><h3>Choose a terrain CSV</h3><p>Import distance and elevation columns in metres to inspect the profile and run the leg model.</p></div></div>`;
  const s=terrain.summary;
  const cropStart=Math.max(terrain.samples[0].x,Math.min(state.cropStart,terrain.samples.at(-1).x-1));
  const detailStart=Math.max(terrain.samples[0].x,Math.min(state.detailStart,terrain.samples.at(-1).x-1));
  const crop=terrain.samples.filter(p=>p.x>=cropStart&&p.x<=cropStart+100);
  const detail=terrain.samples.filter(p=>p.x>=detailStart&&p.x<=detailStart+5);
  const series=[{label:'Total terrain',color:'#23251d',points:points(terrain.samples,'z')},{label:'Macro elevation',color:'#b96a00',points:points(terrain.samples,'baseline'),dashed:true}];
  let layerPlot;
  if(state.sourceMode==='class3'&&c.roughnessRmsM===0&&c.obstacleHeightM===0) layerPlot=chartMarkup({title:'100 m grade cycle · published limits, chosen layout',subtitle:'Grade repeats; elevation accumulates. The 25% plateau occupies 20 m of each 100 m cycle.',xLabel:'Distance (m)',yLabel:'Macro longitudinal grade (%)',series:[{label:'Chosen grade pattern',color:'#b96a00',points:crop.slice(1).map((p,i)=>({x:p.x,y:100*(p.baseline-crop[i].baseline)/(p.x-crop[i].x)}))}],referenceLines:[{label:'Class 3 short-pitch maximum',value:25}]});
  else if(isMeasured) layerPlot=chartMarkup({title:'100 m source-scale detail',subtitle:'Direct source samples; fine terrain layers remain unknown.',xLabel:'Distance (m)',yLabel:'Elevation relative to start (m)',series:[{label:'Observed elevation',color:'#246b8e',points:points(crop,'z')}]});
  else layerPlot=chartMarkup({title:'100 m detail · baseline removed',subtitle:'Roughness and obstacles shown separately. Full-route elevation includes the baseline.',xLabel:'Distance (m)',yLabel:'Height above baseline (mm)',series:[{label:'Combined fine layers',color:'#23251d',points:crop.map(p=>({x:p.x,y:(p.z-p.baseline)*1000}))},{label:'Roughness',color:'#246b8e',points:points(crop,'roughness',1000)},{label:'Obstacles',color:'#b96a00',points:points(crop,'obstacle',1000)}]});
  const details=chartMarkup({title:'5 m close-up',subtitle:isMeasured?'Only existing 1 m samples are shown. No root/rock geometry is inferred.':'Inspect individual roughness cycles and obstacle shapes.',xLabel:'Distance (m)',yLabel:isMeasured?'Elevation (m)':'Height above baseline (mm)',series:isMeasured?[{label:'Observed elevation',color:'#246b8e',points:points(detail,'z')}]:[{label:'Roughness',color:'#246b8e',points:points(detail,'roughness',1000)},{label:'Obstacles',color:'#b96a00',points:points(detail,'obstacle',1000)},{label:'Combined',color:'#23251d',points:detail.map(p=>({x:p.x,y:(p.z-p.baseline)*1000}))}]});
  const cycleLabel=isMeasured?'Observed profile':state.sourceMode==='class3'?'Grade cycles':state.sourceMode==='stochastic'?'Reference wavelength':'Roughness cycles';
  const cycles=isMeasured?'No repeat assumed':state.sourceMode==='class3'?fmt(s.lengthM/100):state.sourceMode==='stochastic'?`${fmt(c.wavelengthM)} <small>m</small>`:fmt(c.roughnessRmsM>0?s.lengthM/c.wavelengthM:0,1);
  const cycleNote=isMeasured?'Single source transect':state.sourceMode==='class3'?'One grade motif per 100 m':state.sourceMode==='stochastic'?`No single cycle · seed ${c.seed}`:`${fmt(s.obstacleCount,0)} obstacle peaks`;
  return `<div class="workbench-grid">${terrainInputs()}<div class="plot-area"><div class="summary-strip">${metric('Route length',`${fmt(s.lengthM,0)} <small>m</small>`,`${fmt(s.sampleCount,0)} samples`)}${metric('Net elevation change',`${fmt(s.netElevationM)} <small>m</small>`,'Macro + fine layers')}${metric('Roughness layer RMS',isMeasured?'Unknown':`${fmt(s.realizedRoughnessRmsM*1000)} <small>mm</small>`,isMeasured?'Unresolved at source scale':'Realized, excludes grade/obstacles')}${metric(cycleLabel,cycles,cycleNote)}</div>${sourceCard()}${chartMarkup({title:`Full route · ${fmt(s.lengthM,0)} m`,subtitle:terrainName(),xLabel:'Distance (m)',yLabel:'Elevation relative to start (m)',series})}<div class="section-heading"><h3>Same-route detail</h3><div class="inline-controls"><label for="crop-start">100 m window starts at (m)</label><input id="crop-start" type="number" value="${cropStart}" min="${terrain.samples[0].x}" max="${Math.max(terrain.samples[0].x,terrain.samples.at(-1).x-1)}" step="1"></div></div>${layerPlot}<div class="section-heading"><h3>Cycle scale</h3><div class="inline-controls"><label for="detail-start">5 m window starts at (m)</label><input id="detail-start" type="number" value="${detailStart}" min="${terrain.samples[0].x}" max="${Math.max(terrain.samples[0].x,terrain.samples.at(-1).x-1)}" step=".1"></div></div>${details}<p class="scope-note">All exported samples are retained. Plots preserve local extrema when simplified. Changing route length crops the same deterministic realization.</p></div></div>`;
}

function mechanismSketch(){
  const m=state.mechanism,q=m.nominalAngleDeg*Math.PI/180,pose=linkageAtAngle(q,m),L=m.linkLengthM,scale=510,ax=170,ay=37;
  const bx=ax+L*Math.sin(q)*scale,by=ay+L*Math.cos(q)*scale,cx=ax,cy=ay+pose.extensionM*scale;
  return `<svg class="mechanism-sketch" viewBox="0 0 450 280" role="img" aria-label="Equal-link grounded 2 to 1 belt leg. Fold angle measured from downward vertical. Wheel below chassis pivot."><line x1="90" x2="255" y1="${ay}" y2="${ay}" stroke="#586249" stroke-width="6"/><line x1="${ax}" x2="${ax}" y1="${ay}" y2="${cy+40}" stroke="#b9bea9" stroke-dasharray="5 5"/><line x1="${ax}" x2="${bx}" y1="${ay}" y2="${by}" stroke="#b57b09" stroke-width="12" stroke-linecap="round"/><line x1="${bx}" x2="${cx}" y1="${by}" y2="${cy}" stroke="#677c51" stroke-width="12" stroke-linecap="round"/><circle cx="${ax}" cy="${ay}" r="14" fill="#f7a501" stroke="#8a6a28"/><circle cx="${bx}" cy="${by}" r="8" fill="#f4f6ed" stroke="#858c74"/><circle cx="${cx}" cy="${cy}" r="${m.wheelRadiusM*scale}" fill="#f0f2e8" stroke="#69725c" stroke-width="3"/><circle cx="${cx}" cy="${cy}" r="5" fill="#798469"/><text x="${ax-33}" y="${ay-10}">A</text><text x="${bx+16}" y="${by+2}">B</text><text x="${cx-10}" y="${cy+4}">C</text><text x="284" y="54">Grounded pulley 2:1</text><text x="284" y="78" class="sketch-label">q = ${fmt(m.nominalAngleDeg)}°</text><text x="284" y="101" class="sketch-label">L = ${fmt(L*1000)} mm × 2</text><text x="284" y="124" class="sketch-label">extension = ${fmt(pose.extensionM*1000)} mm</text><text x="284" y="147" class="sketch-label">|dℓ/dq| = ${fmt(Math.abs(pose.jacobianMPerRad)*1000)} mm/rad</text><text x="54" y="265">q: upper link from downward vertical. C follows the vertical line.</text></svg>`;
}

function mechanismInputs(){return `<aside class="input-panel" aria-label="Mechanism and scenario inputs"><h3>Belt leg geometry</h3>${numberInput('mechanism','linkLengthM','Equal link length (mm)',{scale:1000,min:50,max:1000})}<div class="field-row">${numberInput('mechanism','minAngleDeg','Minimum q (°)',{min:1,max:85})}${numberInput('mechanism','maxAngleDeg','Maximum q (°)',{min:2,max:89})}</div>${numberInput('mechanism','nominalAngleDeg','Nominal fold q (°)',{min:1,max:89})}${numberInput('mechanism','wheelRadiusM','Wheel radius (mm)',{scale:1000,min:10,max:1000})}<div class="section"><h3>One-corner scenario</h3>${numberInput('scenario','speedMps','Forward speed (m/s)',{min:.05,max:10})}<div class="field-row">${numberInput('scenario','sprungMassKg','Supported mass (kg)',{min:.1,max:500,note:'One corner, not total robot.'})}${numberInput('scenario','unsprungMassKg','Wheel / leg mass (kg)',{min:.05,max:100})}</div>${numberInput('scenario','springRateNpm','Spring stiffness (N/m)',{min:1,max:1e6})}${numberInput('scenario','damperNsPm','Passive damping (N·s/m)',{max:10000})}${selectInput('scenario','controlMode','Suspension control',[['passive','Passive / backdrivable'],['active-damping','Active damping'],['body-isolation','Body isolation']])}<details class="disclosure"><summary>Contact & controller</summary>${numberInput('scenario','tireRateNpm','Tire stiffness (N/m)',{min:100,max:1e7})}${numberInput('scenario','tireDamperNsPm','Tire damping (N·s/m)',{max:10000})}${numberInput('scenario','skyhookNsPm','Active damping gain (N·s/m)',{max:10000})}${numberInput('scenario','positionGainNpm','Body position gain (N/m)',{max:1e6})}${numberInput('scenario','velocityGainNsPm','Body velocity gain (N·s/m)',{max:10000})}</details></div><div class="section"><h3>Candidate actuator · output shaft</h3><p class="field-note">Generic illustrative ratings. Replace with verified output-shaft data for sizing.</p><div class="field-row">${numberInput('actuator','peakTorqueNm','Peak torque (N·m)',{min:.01,max:10000})}${numberInput('actuator','continuousTorqueNm','Continuous (N·m)',{min:.01,max:10000})}</div>${numberInput('actuator','noLoadSpeedRadPs','No-load speed (rpm)',{scale:units.rpm,min:1,max:20000})}<details class="disclosure"><summary>Response & integration</summary>${numberInput('actuator','responseTimeS','Response time (ms)',{scale:1000,min:.1,max:10000})}${numberInput('actuator','slewRateNmPs','Torque slew (N·m/s)',{min:.1,max:1e6})}${numberInput('scenario','timeStepS','Integration step (ms)',{scale:1000,min:.05,max:10,note:'Check timestep convergence before hardware sizing.'})}</details></div><div class="section"><button class="primary run-button" data-action="run" ${state.running?'disabled':''}>${state.running?'Running scenario…':'Run scenario'}</button></div></aside>`;}

function mechanismPage(){
  const m=state.mechanism, mass=state.scenario.sprungMassKg;
  let extension=[],lever=[],holding=[];
  for(let i=0;i<=150;i++){const deg=m.minAngleDeg+(m.maxAngleDeg-m.minAngleDeg)*i/150;const pose=linkageAtAngle(deg*Math.PI/180,m);extension.push({x:deg,y:pose.extensionM*1000});lever.push({x:deg,y:Math.abs(pose.jacobianMPerRad)*1000});holding.push({x:deg,y:mass*9.81*Math.abs(pose.jacobianMPerRad)});}
  const p=linkageAtAngle(m.nominalAngleDeg*Math.PI/180,m), maxExt=2*m.linkLengthM*Math.cos(m.minAngleDeg*Math.PI/180),minExt=2*m.linkLengthM*Math.cos(m.maxAngleDeg*Math.PI/180);
  return `<div class="workbench-grid">${mechanismInputs()}<div class="plot-area"><div class="summary-strip">${metric('Nominal extension',`${fmt(p.extensionM*1000)} <small>mm</small>`)}${metric('Available travel',`${fmt((maxExt-minExt)*1000)} <small>mm</small>`)}${metric('Supported weight',`${fmt(mass*9.81)} <small>N</small>`,`${fmt(mass)} kg supported mass`)}${metric('Unassisted holding torque',`${fmt(mass*9.81*Math.abs(p.jacobianMPerRad))} <small>N·m</small>`,'Nominal pose; spring not included')}</div><section class="content-card"><div class="section-heading"><h3>Geometry from the rough animation</h3><p>Equal links · grounded 2:1 suspension belt</p></div>${mechanismSketch()}<p class="scope-note">The independent wheel drive has two 1:1 stages; ideal wheel rotation relative to the chassis follows its chassis-mounted drive input through folding. Belt routing and internal pin/belt loads remain unvalidated.</p></section><div class="plot-pair">${chartMarkup({title:'Extension vs. fold angle',xLabel:'Fold angle q (°)',yLabel:'Pivot to wheel centre (mm)',series:[{label:'ℓ = 2L cos(q)',points:extension}],height:255})}${chartMarkup({title:'Joint leverage',xLabel:'Fold angle q (°)',yLabel:'|dℓ/dq| (mm/rad)',series:[{label:'Motion ratio',points:lever,color:'#246b8e'}],height:255})}</div>${chartMarkup({title:'Static holding torque · without spring',subtitle:`Supported load ${fmt(mass)} kg; output joint shaft. Not an internal belt reaction.`,xLabel:'Fold angle q (°)',yLabel:'Holding torque magnitude (N·m)',series:[{label:'Weight × linkage motion ratio',points:holding}],referenceLines:[{label:'Candidate continuous torque',value:state.actuator.continuousTorqueNm}]})}<section class="source-card"><h3>What this V1 model resolves</h3><p>Vertical body and wheel motion, compliant unilateral tire contact, passive spring/damping and an actuated folding joint. Ideal demand and a finite-response candidate run are calculated separately.</p><p>Pitch, roll, traction drive, step climbing, structural stress and thermal limits require later models or measurements. Controller and tire values here are chosen assumptions.</p></section></div></div>`;
}

function failureText(pass){
  if(!pass.firstFailure)return 'No travel or numerical stop';
  const f=pass.firstFailure;
  return typeof f==='string'?f:`${f.reason || f.type || f.message || 'Constraint failure'}${Number.isFinite(f.xM)?` at ${fmt(f.xM)} m`:''}${Number.isFinite(f.timeS)?` (${fmt(f.timeS)} s)`:''}`;
}
function statusLabel(pass){const status=pass.status||'unknown',bad=!['completed','complete','success'].includes(status);return `<span class="status-label ${bad?'failed':''}">${esc(status.replaceAll('_',' '))}</span>`;}
function resultTable(){
  const {ideal,limited}=state.result;
  const rows=[['Peak active joint torque (N·m)','peakTorqueNm',1],['RMS active joint torque (N·m)','rmsTorqueNm',1],['Peak total joint torque incl. spring (N·m)','peakTotalJointTorqueNm',1],['Peak joint speed (rpm)','peakJointSpeedRadPs',units.rpm],['Peak shaft power (W)','peakPowerW',1],['RMS body acceleration (m/s²)','rmsBodyAccelerationMps2',1],['Minimum travel reserve (mm)','minTravelMarginM',1000],['Contact loss duration (s)','contactLossTimeS',1],['Envelope saturation duration (s)','saturationTimeS',1],['Response tracking mismatch (s)','responseLimitedTimeS',1],['Above continuous torque (s)','continuousOverloadTimeS',1],['Longest continuous overload (s)','longestContinuousOverloadS',1],['Above 90% of peak torque rating (s)','above90PercentPeakTimeS',1],['Longest interval above 90% peak (s)','longestAbove90PercentPeakS',1],['Completed distance (m)','completedDistanceM',1],['Simulated duration (s)','simulatedTimeS',1]];
  return `<div class="table-wrap"><table><thead><tr><th>Metric · output joint shaft</th><th class="number">Ideal demand</th><th class="number">Candidate achieved</th></tr></thead><tbody><tr><td>Run status</td><td class="number">${statusLabel(ideal)}</td><td class="number">${statusLabel(limited)}</td></tr>${rows.map(([label,key,scale])=>`<tr><td>${label}</td><td class="number">${fmt(ideal.summary[key]*scale,3)}</td><td class="number">${fmt(limited.summary[key]*scale,3)}</td></tr>`).join('')}<tr><td>Thermal / electrical / structural rating</td><td colspan="2">Unknown · requires measured or verified hardware data</td></tr></tbody></table></div>`;
}

function torqueSpeedChart(){
  const a=state.snapshot.actuator,speed=a.noLoadSpeedRadPs*units.rpm;
  const envelope=[{x:0,y:a.peakTorqueNm},{x:speed,y:0}];
  const pointsOf=p=>p.operatingPoints.map(s=>({x:Math.abs(s.speedRadPs)*units.rpm,y:Math.abs(s.torqueNm),meta:`${fmt(s.timeS,3)} s · ${fmt(s.xM,3)} m`}));
  return chartMarkup({title:'Torque–speed operating points',subtitle:'Magnitude at the output joint shaft; both signs folded. Generic linear peak envelope, no thermal rating.',xLabel:'Joint speed magnitude (rpm)',yLabel:'Joint torque magnitude (N·m)',scatter:true,series:[{label:'Ideal demand',color:'#b96a00',points:pointsOf(state.result.ideal)},{label:'Candidate achieved',color:'#246b8e',points:pointsOf(state.result.limited)},{label:'Candidate peak envelope',color:'#697840',line:true,points:envelope}],referenceLines:[{label:'Continuous torque assumption',value:a.continuousTorqueNm}]});
}

function resultsPage(){
  if(!state.result)return `<div class="workbench-grid">${mechanismInputs()}<div class="empty-state"><h3>Run a one-corner scenario</h3><p>Your terrain, speed, mass and belt-leg geometry produce joint demand. A second pass applies the candidate's torque–speed and response limits.</p><p>Results will show actual calculations with run status and constraint failures.</p><button data-view="mechanism">Review mechanism inputs</button></div></div>`;
  const result=state.result, snap=state.snapshot, summary=result.limited.summary;
  const axisLabel=state.resultAxis==='time'?'Time (s)':'Distance (m)';
  const m=snap.mechanism,min=2*m.linkLengthM*Math.cos(m.maxAngleDeg*Math.PI/180),max=2*m.linkLengthM*Math.cos(m.minAngleDeg*Math.PI/180);
  const xyz=chartMarkup({title:'Terrain, wheel and body motion',subtitle:'Elevation relative to the saved route datum.',xLabel:axisLabel,yLabel:'Height (m)',series:[{label:'Ground',color:'#23251d',points:histPoints(result.limited,'groundM')},{label:'Wheel centre · candidate',color:'#697840',points:histPoints(result.limited,'wheelM')},{label:'Body · candidate',color:'#246b8e',points:histPoints(result.limited,'bodyM')},{label:'Body · ideal',color:'#b96a00',dashed:true,points:histPoints(result.ideal,'bodyM')}]});
  const peak=result.ideal.summary.peakTorqueLocation;
  const peakNote=peak?`Ideal peak at ${fmt(peak.xM)} m, ${fmt(peak.timeS)} s; joint speed ${fmt(Math.abs(peak.speedRadPs)*units.rpm)} rpm.`:'';
  const a=snap.actuator;
  const outsideEnvelope=result.ideal.operatingPoints.some(p=>Math.abs(p.torqueNm)>a.peakTorqueNm*Math.max(0,1-Math.abs(p.speedRadPs)/a.noLoadSpeedRadPs)+1e-8);
  const rmsOver=summary.rmsTorqueNm>a.continuousTorqueNm;
  const actuatorChecks=`<div class="actuator-checks"><strong>Preliminary actuator checks</strong><p>${outsideEnvelope?'Ideal demand exceeds the chosen torque–speed envelope.':'Recorded ideal demand stays inside the chosen peak envelope.'} Candidate RMS torque ${rmsOver?'exceeds':'is below'} the assumed ${fmt(a.continuousTorqueNm)} N·m continuous rating. Response tracking mismatch: ${fmt(summary.responseLimitedTimeS,3)} s.</p><p>“Completed” means the route calculation finished within travel bounds. Thermal suitability and hardware approval remain unknown.</p></div>`;
  return `<div class="results-toolbar"><div><h3>${esc(snap.terrainName)}</h3><p class="scope-note">Saved run: ${fmt(snap.scenario.speedMps)} m/s · ${fmt(snap.scenario.sprungMassKg)} kg supported · ${esc(snap.scenario.controlMode.replaceAll('-',' '))} · V1 single corner</p></div><div class="inline-controls"><div class="view-switch" aria-label="Plot horizontal axis"><button data-axis="time" class="${state.resultAxis==='time'?'active':''}" aria-pressed="${state.resultAxis==='time'}">Time</button><button data-axis="distance" class="${state.resultAxis==='distance'?'active':''}" aria-pressed="${state.resultAxis==='distance'}">Distance</button></div><button data-action="export-results">Preview & export run</button></div></div>${state.stale?'<p class="notice">Previous run — inputs changed. These plots retain the saved inputs shown above. Run again to evaluate your current case.</p>':''}<div class="summary-strip">${metric('Candidate peak torque',`${fmt(summary.peakTorqueNm)} <small>N·m</small>`,'Output joint shaft')}${metric('Candidate RMS torque',`${fmt(summary.rmsTorqueNm)} <small>N·m</small>`)}${metric('Candidate saturation',`${fmt(summary.saturationTimeS,3)} <small>s</small>`,'Torque–speed envelope only')}${metric('Completed route',`${fmt(summary.completedDistanceM)} <small>m</small>`,`${fmt(summary.simulatedTimeS)} s simulated`)}</div><div class="content-card"><div class="section-heading"><h3>Run status and constraints</h3><div class="inline-controls">${statusLabel(result.ideal)} <span>ideal</span> ${statusLabel(result.limited)} <span>candidate</span></div></div><p class="scope-note"><strong>Ideal:</strong> ${esc(failureText(result.ideal))}<br><strong>Candidate:</strong> ${esc(failureText(result.limited))}</p><p class="scope-note">${esc(peakNote)} Full histories and failure locations are included in the export. A stopped run does not establish a suitable motor.</p></div>${actuatorChecks}${resultTable()}${xyz}<div class="plot-pair">${curve('Fold angle q','Angle from downward vertical (°)','angleRad',{scale:units.deg,referenceLines:[{label:'min q',value:m.minAngleDeg},{label:'max q',value:m.maxAngleDeg}]})}${curve('Suspension extension','Pivot to wheel centre (mm)','extensionM',{scale:1000,referenceLines:[{label:'min extension',value:min*1000},{label:'max extension',value:max*1000}]})}</div><div class="plot-pair">${curve('Output joint torque','Joint torque (N·m)','torqueNm',{referenceLines:[{label:'+ continuous',value:snap.actuator.continuousTorqueNm},{label:'− continuous',value:-snap.actuator.continuousTorqueNm}]})}${curve('Output joint speed','Joint speed (rpm)','jointSpeedRadPs',{scale:units.rpm})}</div>${torqueSpeedChart()}<div class="plot-pair">${curve('Body acceleration','Acceleration (m/s²)','bodyAccelerationMps2')}${curve('Ground contact force','Normal force (N)','normalForceN',{referenceLines:[{label:'No contact',value:0}]})}</div>${chartMarkup({title:'Spring and active force · candidate',subtitle:'Vertical force components. Holding load and spring assistance are distinct.',xLabel:axisLabel,yLabel:'Vertical force (N)',series:[{label:'Spring',color:'#697840',points:histPoints(result.limited,'springForceN')},{label:'Actuator',color:'#b96a00',points:histPoints(result.limited,'activeForceN')}]})}<p class="scope-note">Reduced single-corner screening model. Step climbing, pitch/roll, traction and internal belt/pin reactions are unresolved. Candidate ratings are assumptions; structural, electrical and thermal suitability remain unknown.</p>`;
}

const NODES=[
  {id:'terrain',label:'Terrain profile',short:'Elevation + evidence',stage:'V1 · input',description:'Select an observed source or create a reproducible engineering profile. Keep slope, roughness and obstacles separate.',inputs:['Source data or CSV','Terrain context and evidence','Route length, sample spacing, seed'],outputs:['Distance and height samples (m)','Component layers and statistics','Sources, assumptions and resolution']},
  {id:'scenario',label:'Scenario',short:'Speed · mass · control',stage:'V1 · input',description:'Define one-corner support, speed, compliance and the control objective.',inputs:['Forward speed (m/s)','Supported and wheel/leg masses (kg)','Spring, damping and controller values'],outputs:['Time–distance mapping','Support and compliance values','Control law and solver settings']},
  {id:'geometry',label:'Mechanism',short:'2:1 belt leg',stage:'V1 · input',description:'Map vertical extension to the folding joint through the equal-link, grounded-belt geometry.',inputs:['Equal link length (m)','Nominal angle and working limits','Wheel radius (m)'],outputs:['ℓ = 2L cos(q)','q, joint motion ratio, travel','Analytic holding-load curve']},
  {id:'dynamics',label:'Contact & dynamics',short:'Guided body + wheel',stage:'V1 · solve',description:'Integrate a vertically guided body and wheel with unilateral tire contact. Run ideal actuation, then the limited candidate.',inputs:['Terrain elevation at wheel location','Mass, spring, damping and control','Travel and actuator constraints'],outputs:['Body and wheel histories','Contact forces and travel reserve','Completed, failed or invalid status']},
  {id:'joint',label:'Joint demand',short:'Torque · speed · duration',stage:'V1 · calculate',description:'Convert active vertical force and leg motion through the linkage Jacobian at each pose.',inputs:['Active force and extension history','q and dℓ/dq','Body/wheel response'],outputs:['Output-shaft torque and speed','Peak location and RMS demand','Mechanical power and work']},
  {id:'actuator',label:'Actuator candidate',short:'Limits feed back into motion',stage:'V1 · compare',description:'Apply a generic output-shaft torque–speed envelope, lag and slew. Candidate limitations change the simulated body and wheel response.',inputs:['Peak and continuous output torque','No-load output speed','Response time and torque slew'],outputs:['Achieved torque and motion','Saturation and overload duration','Thermal/electrical gaps remain unknown']},
  {id:'report',label:'Plots & saved run',short:'Compare · inspect · export',stage:'V1 · output',description:'Compare ideal demand with achieved motion, retaining failure reasons and the complete input snapshot.',inputs:['Both simulation passes','Input and source snapshots','Constraint/failure records'],outputs:['Readable histories and envelope plot','Sizing metrics with durations','Full CSV and metadata JSON']},
  {id:'validation',label:'Measured validation',short:'Leg test + source-scale terrain',stage:'V2 / V3 · planned',description:'Compare predictions with physical leg tests and suitable measured terrain. Revise assumptions using held-out tests.',inputs:['Synchronized leg-test records','Verified actuator/contact data','Profiles at matching spatial scales'],outputs:['Prediction error and uncertainty','Updated parameters','Evidence for broader operating envelopes']},
];
function graphPage(){const node=NODES.find(n=>n.id===state.selectedNode);return `<div class="graph-layout">${nodeGraphMarkup(NODES,state.selectedNode)}<aside class="node-detail" aria-live="polite"><h3>${esc(node.label)}</h3><p>${esc(node.description)}</p><div><h4>Inputs</h4><ul>${node.inputs.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div><div><h4>Outputs</h4><ul>${node.outputs.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div></aside></div><div class="stage-table"><div class="current"><strong>V1 · single-corner screening</strong><p>Terrain ingestion, belt geometry, static checks, guided-body dynamics and candidate sizing. Implemented here.</p></div><div><strong>V2 · planar vehicle</strong><p>Front/rear support, shared chassis pitch, traction and explicit obstacle contact. Calibrate against a leg test.</p></div><div><strong>V3 · whole vehicle</strong><p>Four corners, roll, turning, uncertainty and validated mission/thermal models where data supports them.</p></div></div>`;}

function render(){
  resetCharts();
  const titles={terrain:['Terrain definition','Trace each terrain parameter to its evidence, then inspect the same route at three scales.'],mechanism:['Mechanism & scenario','Set one-corner loads and the belt-leg geometry. Numeric values here are illustrative assumptions.'],results:['Joint loads & actuator sizing','Compare ideal demand with the motion a finite-response candidate can achieve.'],graph:['How the calculation connects','Select a node to inspect its inputs and outputs. Candidate limits feed back into the dynamics.']};
  const [title,description]=titles[state.view];
  const page=state.view==='terrain'?terrainPage():state.view==='mechanism'?mechanismPage():state.view==='results'?resultsPage():graphPage();
  root.innerHTML=`<header class="app-header"><div class="brand"><div class="brand-symbol" aria-hidden="true">↗</div><div><h1>Terrain → Loads</h1><p>Capstone · numerical design workbench</p></div></div><div class="header-actions"><a href="/linkage/">Linkage simulator →</a><span class="version-badge">V1 · SINGLE CORNER</span><button class="primary" data-action="run" ${state.running?'disabled':''}>${state.running?'Running…':'Run scenario'}</button></div></header><nav class="tabs" role="tablist" aria-label="Workbench views">${tabs.map(([id,label])=>`<button id="tab-${id}" role="tab" data-view="${id}" aria-selected="${state.view===id}" aria-controls="view-panel" tabindex="${state.view===id?0:-1}">${label}</button>`).join('')}</nav><main class="page" id="view-panel" role="tabpanel" aria-labelledby="tab-${state.view}"><div class="page-heading"><div><h2>${title}</h2><p>${description}</p></div></div>${state.error?`<p class="notice error" role="alert">${esc(state.error)}</p>`:''}${state.running?`<p class="run-status" role="status">Calculating ideal and candidate passes on a background worker. Current inputs are saved with this run. <button class="link-button" data-action="cancel-run">Cancel</button></p>`:''}${page}</main><footer class="app-footer"><span>SI calculations · plots retain extrema · source and assumptions travel with each export</span><span><a href="/">Terrain atlas</a> · <a href="${CHAT_SOURCE}" target="_blank" rel="noopener">Terrain study</a></span></footer><dialog id="export-dialog" class="export-dialog" aria-labelledby="export-title"></dialog>`;
  attachCharts(root);
}

function runScenario(){
  if(state.running)return;
  try {
    updateTerrain();
    if(!state.terrain)throw new Error('Import a terrain CSV before running.');
    if(!worker)throw new Error('Simulation worker is unavailable. Reload this page.');
    const m=state.mechanism;
    if(m.minAngleDeg>=m.maxAngleDeg||m.nominalAngleDeg<=m.minAngleDeg||m.nominalAngleDeg>=m.maxAngleDeg)throw new Error('Nominal fold angle must be between the minimum and maximum q.');
    if(state.actuator.continuousTorqueNm>state.actuator.peakTorqueNm)throw new Error('Continuous torque must not exceed peak torque.');
    state.error='';state.running=true;state.runId++;
    state.pendingSnapshot={terrainName:terrainName(),terrainConfig:{...state.terrainConfig},terrainMetadata:structuredClone(state.terrain.metadata),mechanism:{...state.mechanism},scenario:{...state.scenario},actuator:{...state.actuator},revision:state.inputRevision,createdAt:new Date().toISOString()};
    worker.postMessage({id:state.runId,terrain:state.terrain,scenario:state.scenario,mechanism:state.mechanism,actuator:state.actuator});
    render();
  } catch(error){state.error=error.message;render();}
}

function download(text,name,type){const url=URL.createObjectURL(new Blob([text],{type}));const anchor=document.createElement('a');anchor.href=url;anchor.download=name;document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);}
function exportPayload(kind){
  if(kind==='results')return {name:'terrain-loads-run',csv:serializeResultsCsv(state.result),metadata:{...state.result.metadata,inputs:state.snapshot,ideal:{status:state.result.ideal.status,summary:state.result.ideal.summary,firstFailure:state.result.ideal.firstFailure},candidate:{status:state.result.limited.status,summary:state.result.limited.summary,firstFailure:state.result.limited.firstFailure},limits:{thermal:'unknown',structural:'unknown',electrical:'unknown'}}};
  return {name:`terrain-${state.sourceMode}-${fmt(state.terrain.summary.lengthM,0).replaceAll(',','')}m`,csv:serializeTerrainCsv(state.terrain),metadata:{...state.terrain.metadata,summary:state.terrain.summary,requestedConfig:state.terrainConfig,name:terrainName()}};
}
function showExport(kind){
  if(kind==='terrain'&&!state.terrain)return;if(kind==='results'&&!state.result)return;
  state.exportKind=kind;
  const payload=exportPayload(kind),dialog=document.querySelector('#export-dialog');
  const lines=payload.csv.trim().split('\n');
  dialog.innerHTML=`<h2 id="export-title">${kind==='results'?'Saved simulation run':'Terrain profile'} export</h2><p>Full CSV: ${fmt(lines.length-1,0)} rows. Metadata includes source, assumptions, inputs and ${kind==='results'?'run status and failure locations':'profile statistics'}.</p><h3>CSV · first ${Math.min(8,lines.length)} lines</h3><pre>${esc(lines.slice(0,8).join('\n'))}</pre><details><summary>Metadata JSON preview</summary><pre>${esc(JSON.stringify(payload.metadata,null,2))}</pre></details><div class="actions"><button data-action="close-export">Close</button><button data-action="download-json">Download metadata JSON</button><button class="primary" data-action="download-csv">Download full CSV</button></div>`;
  dialog.showModal();
}

root.addEventListener('click',event=>{
  const target=event.target.closest('button');if(!target)return;
  if(target.dataset.view){state.view=target.dataset.view;state.error='';render();document.querySelector(`#tab-${state.view}`)?.focus();return;}
  if(target.dataset.node){state.selectedNode=target.dataset.node;render();document.querySelector(`[data-node="${state.selectedNode}"]`)?.focus();return;}
  if(target.dataset.axis){state.resultAxis=target.dataset.axis;render();return;}
  const action=target.dataset.action;
  if(action==='run')runScenario();
  if(action==='export-terrain')showExport('terrain');
  if(action==='export-results')showExport('results');
  if(action==='close-export')document.querySelector('#export-dialog').close();
  if(action==='download-csv'||action==='download-json') {const p=exportPayload(state.exportKind);download(action==='download-csv'?p.csv:JSON.stringify(p.metadata,null,2),p.name+(action==='download-csv'?'.csv':'.json'),action==='download-csv'?'text/csv;charset=utf-8':'application/json');}
  if(action==='cancel-run'){
    worker.terminate();state.runId++;state.running=false;state.pendingSnapshot=null;state.error='Run cancelled. No new result was accepted.';
    worker=createSimulationWorker();render();
  }
});
root.addEventListener('keydown',event=>{
  if(event.target.getAttribute('role')!=='tab')return;
  if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) {
    event.preventDefault();let index=tabs.findIndex(([id])=>id===state.view);
    if(event.key==='Home')index=0;else if(event.key==='End')index=tabs.length-1;else index=(index+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
    state.view=tabs[index][0];render();document.querySelector(`#tab-${state.view}`).focus();
  }
});
root.addEventListener('change',async event=>{
  const input=event.target;
  try {
    if(input.id==='source-mode'){
      markChanged();state.sourceMode=input.value;state.cropStart=0;state.detailStart=0;
      if(state.sourceMode==='class3')Object.assign(state.terrainConfig,{roughnessRmsM:0,obstacleHeightM:0,gradePercent:8});
      else if(['periodic','stochastic'].includes(state.sourceMode))Object.assign(state.terrainConfig,currentPreset().defaults);
      updateTerrain();render();return;
    }
    if(input.id==='terrain-file'){
      const file=input.files?.[0];if(!file)return;
      const parsed=parseTerrainCsv(await file.text());state.imported=parsed;state.importName=file.name;state.cropStart=parsed.samples[0].x;state.detailStart=parsed.samples[0].x;markChanged();updateTerrain();render();return;
    }
    if(input.id==='crop-start'||input.id==='detail-start'){
      if(!input.checkValidity()){input.reportValidity();return;}
      state[input.id==='crop-start'?'cropStart':'detailStart']=Number(input.value);render();return;
    }
    if(input.dataset.group){
      if(!input.checkValidity()){input.reportValidity();return;}
      const group=input.dataset.group,key=input.dataset.key;
      const oldValue=state[group][key];
      let value=input.tagName==='SELECT'?input.value:Number(input.value)/Number(input.dataset.scale||1);
      if(key==='lengthM')value=Number(value);
      state[group][key]=value;markChanged();
      try {
        if(key==='presetId')Object.assign(state.terrainConfig,currentPreset().defaults);
        if(group==='terrainConfig')updateTerrain();
        render();
      }catch(error){state[group][key]=oldValue;throw error;}
    }
  }catch(error){state.error=error.message;render();}
});
render();
