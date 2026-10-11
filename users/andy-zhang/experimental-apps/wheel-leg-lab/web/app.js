/** Shared suspension bench: serve /physics/ or /mathematical/ with matching DOM.
 * Inputs: SI JSON profiles/results, same-origin shell messages, Plotly and D3.
 * Outputs: recorded playback, zoomable charts, full CSV/profile/run JSON downloads.
 * Limitations: client playback does not integrate physics; math uses annotated geometry.
 */
(() => {
  const $=id=>document.getElementById(id),D=window.d3;
  const backend=document.body.dataset.backend==='math'?'math':'pymunk',isMath=backend==='math',viewer=new URLSearchParams(location.search).get('viewer')==='1',loadOnly=new URLSearchParams(location.search).get('loadOnly')==='1',architecture=new URLSearchParams(location.search).get('architecture')==='constant-lift';
  let config={},defaults={},result=null,charts=[],time=0,playing=false,raf=0,last=0,dirty=false,runRevision=0,lastReadoutStamp=-Infinity,pendingProfile=null,springCatalog={},mechanismDefaults={},guideModule=null,playbackCache=null;
  let setupPreview=null,setupCache=null,inSetupMode=false,previewTimer=0,previewGeneration=0,previewAbort=null,recordedHeading='Mechanism & live loads';
  const previewNotice=document.createElement('p');previewNotice.className='setup-preview-note';previewNotice.hidden=true;previewNotice.setAttribute('role','status');$('mechanism').before(previewNotice);
  const showRecording=document.createElement('button');showRecording.textContent='Show last recording';showRecording.hidden=true;$('play').after(showRecording);
  const fmt=(v,n=2)=>Number.isFinite(Number(v))?Number(v).toFixed(n):'—',colors=['var(--blue)','var(--orange)','var(--accent)','var(--purple)','var(--red)','var(--muted)'];
  const cssColor=name=>getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const publish=(type,fields={})=>{if(parent!==window)parent.postMessage({type,backend,...fields},location.origin);};
  if(viewer)document.body.classList.add('engine-viewer');
  const KGF=9.80665,forceFmt=v=>`${fmt(v)} N / ${fmt(v/KGF)} kgf`,forceCell=v=>`${fmt(v)} / ${fmt(v/KGF)}`;
  let referenceT0N=null,guidePretensionN=null,guideForcesVisible=true;
  try{const value=JSON.parse(localStorage.getItem('pymunk-reference-T0-N'));if(typeof value==='number'&&Number.isFinite(value)&&value>=0)referenceT0N=value;}catch{}
  const field=(key,label,unit='',scale=1,min=0,max=1e6,step='any')=>`<label class="field">${label}${unit?` <em>${unit}</em>`:''}<input data-key="${key}" data-scale="${scale}" type="number" min="${min}" max="${max}" step="${step}" value="${config[key]*scale}"></label>`;
  const select=(key,label,choices)=>`<label class="field full">${label}<select data-key="${key}">${choices.map(([v,l])=>`<option value="${v}" ${config[key]===v?'selected':''}>${l}</option>`).join('')}</select></label>`;
  function controls(){
    const position=config.target==='position',gravityBalance=config.spring_topology==='gravity_balance',rateBalance=config.spring_force_law==='zero_effective';
    const waves=position?[['step','Position step'],['square','Position square wave'],['pulse','Position bump pulse']]:[['step','Diagnostic force/torque step'],['square','Diagnostic square wave'],['impulse','Diagnostic impulse area']];
    const fixtures=position?[['floating','Wheel height input · floating chassis'],['hip','Wheel height input · fixed hip'],['wheel','Chassis height input · fixed wheel']]:[['hip','Fixed hip · wheel force response'],['wheel','Fixed wheel · chassis force response']];
    const inputFields=position?field('position_amplitude','Step / pulse height','mm, up +',1000,-500,500):field('amplitude','Step / square amplitude',config.target==='force'?'N':'N·m',1,-10000,10000)+field('impulse','Impulse area',config.target==='force'?'N·s':'N·m·s',1,-1000,1000);
    $('controls').innerHTML=`<details open><summary>Geometry & masses</summary><div class="fields">${field('length','Each link','mm',1000,80,800)}${field('extension','r₂ past knee','mm',1000,5,150)}${field('radius','Wheel radius','mm',1000,50,400)}${field('theta','Initial θ','°',1,3,87)}${field('theta_min','Minimum θ','°',1,3,86)}${field('theta_max','Maximum θ','°',1,4,87)}${field('upper_mass','Upper link','kg',1,.01,20)}${field('lower_mass','Full lower link','kg',1,.01,20)}${field('wheel_mass','Wheel','kg',1,.01,30)}${field('chassis_mass','Chassis corner','kg',1,.01,100)}${select('fixture','Fixture',fixtures)}</div></details>
    ${guideControls()}
    ${springControls()}
    ${auxiliaryControls()}
    <details open><summary>Spring rate, damping & static loading</summary><div class="fields">${field('stiffness','Spring k','N/m',1,0,100000)}${field('damping','Damper c','N·s/m',1,0,2000)}${field('rest_length','Manual free length','mm',1000,5,1000)}${field('bias_force','Optional static vertical force','N, up +',1,-5000,5000)}${field('bias_force_x','Optional static horizontal force','N, right +',1,-5000,5000)}${position&&config.fixture==='hip'?field('preload_force','Fixed-hip preload design load','N',1,-5000,5000):''}<label class="check"><input data-key="balance_spring" type="checkbox" ${config.balance_spring?'checked':''}>${rateBalance?'Calibrate spring rate for gravity balance':'Set spring preload at initial pose'}</label></div><p class="hint">${rateBalance?'Gravity balance sets spring rate, with finite physical free length and zero effective length via compensation routing.':'For the selected spring mechanism, preload is resolved at the initial pose.'} In the floating chassis test, preload supports the moving chassis/link weight. Forces are measured responses to the imposed wheel motion.</p></details>
    <details open><summary>Prescribed motion input</summary><div class="fields">${select('target','Input quantity',[['position','Position · prescribed height'],['force','Force · legacy diagnostic'],['knee','Knee torque · legacy diagnostic']])}${select('wave','Waveform',waves)}${inputFields}${position?select('ramp_shape','Ramp shape',[['quintic','Smooth C2 · zero end velocity/acceleration'],['linear','Linear · velocity jumps at joins']]):''}${field('start','Start time','s',1,0,20)}${field('period','Square period','s',1,.02,10)}${field('duty','Square on-time','%',100,1,99)}${field('pulse_width',position?'Position pulse width':'Impulse width','ms',1000,1,5000)}${field('rise','Rise time','ms',1000,0,5000)}${field('fall','Fall time','ms',1000,0,5000)}${select('load_point','Static wheel-force point',[['hub','Hub · no radius moment'],['contact','Tire bottom · Fx × radius']])}<label class="check"><input data-key="wheel_drive_locked" type="checkbox" ${config.wheel_drive_locked?'checked':''}>Lock wheel drive to lower link</label></div><p class="hint">Position mode moves a kinematic support; its reaction is an output, not a commanded force. This is a prescribed boundary, not automatically solved terrain contact.</p><p class="hint" id="slopes"></p></details>
    <details><summary>Optional knee impedance</summary><div class="fields">${field('knee_kp','Kp','N·m/rad',1,0,2000)}${field('knee_kd','Kd','N·m·s/rad',1,0,200)}${field('torque_limit','Torque limit','N·m',1,.01,2000)}</div></details>
    <details><summary>Solver</summary><div class="fields">${field('duration','Duration','s',1,.1,20)}${field('dt','Solver step','ms',1000,.25,4)}${field('iterations','Iterations','',1,20,300,1)}${field('gravity','Gravity','m/s²',1,0,20)}</div></details>`;
    $('controls').querySelectorAll('[data-key]').forEach(node=>node.addEventListener('change',()=>{
      const key=node.dataset.key;
      config[key]=node.type==='checkbox'?node.checked:node.tagName==='SELECT'?node.value:Number(node.value)/Number(node.dataset.scale||1);
      if(key==='target'){
        if(config.target==='position'){config.fixture='floating';config.bias_force=0;config.wave='step';config.rise=config.fall=.25;config.pulse_width=.7;}
        else{config.fixture='hip';config.bias_force=80;config.wave='square';config.rise=config.fall=.05;config.pulse_width=.12;}
      }
      if(key==='spring_direction')config[key]=Number(node.value);
      if(key==='spring_topology'){Object.assign(config,mechanismDefaults,springCatalog[config.spring_topology]?.defaults||{},{spring_topology:node.value});if(config.spring_topology!=='gravity_balance'&&Object.hasOwn(config,'aux_spring_enabled'))config.aux_spring_enabled=false;}
      if(key==='fixture'&&config.fixture==='wheel'){config.bias_force=0;config.load_point='hub';config.wheel_drive_locked=false;}
      dirty=true;$('status').textContent='Inputs changed. Run simulation to update the saved traces.';
      if(['fixture','target','spring_topology','spring_transmission','spring_force_law','guide_hip_radius'].includes(key)||(key==='length'&&config.spring_topology==='gravity_balance'))controls();else updateControls();
      if(key==='guide_pulleys_visible')drawMechanism();
      requestSetupPreview();
      publish('motion-lab-config',{config:{...config},reference_inputs:referenceInputs()});
    }));updateControls();bindGuideControls();showIntegrationWarning();
  }
  function guideControls(){
    if(config.guide_pulleys_visible===undefined)return '';
    return `<details open class="guide-controls"><summary>2:1 guide · pulleys & belt</summary><div class="fields"><label class="check"><input data-key="chassis_shape_enabled" type="checkbox" ${config.chassis_shape_enabled?'checked':''}>Show chassis block geometry</label><label class="check"><input data-key="guide_pulleys_visible" type="checkbox" ${config.guide_pulleys_visible?'checked':''}>Show guide pulleys & material belt marks</label>${field('guide_hip_radius','Hip guide radius','mm',1000,5,100)}<div class="field">Knee guide radius <em>fixed 2:1 ratio</em><output>${fmt(config.guide_hip_radius*500,1)} mm</output></div><label class="field">Assumed slack baseline <em>N · optional</em><input id="guide-pretension-N" type="number" min="0" step="any" placeholder="Unknown" value="${guidePretensionN??''}"></label><label class="field">Same baseline <em>kgf · optional</em><input id="guide-pretension-kgf" type="number" min="0" step="any" placeholder="Unknown" value="${guidePretensionN===null?'':guidePretensionN/KGF}"></label><label class="check"><input id="guide-force-vectors" type="checkbox" ${guideForcesVisible?'checked':''}>Show derived guide-force arrows</label></div><p class="hint" id="guide-force-state">Pretension unspecified; only torque-required ΔT is known.</p><p class="hint">Hip drum is fixed to chassis J1; knee drum is fixed to lower link r₂. Upper link r₁ carries their centers. Belt marks follow the recorded angles. Geometry/radius changes need a new run; the visibility checkbox also hides the current overlay.</p><p class="hint">Baseline is an independent visual assumption, saved with the profile. It never changes the solver or reference-sheet T₀. Belt bearing forces are outside the ideal GearJoint model.</p></details>`;
  }
  function bindGuideControls(){
    for(const [id,unit] of [['guide-pretension-N','N'],['guide-pretension-kgf','kgf']])if($(id))$(id).oninput=()=>{
      const node=$(id),value=node.valueAsNumber;
      if(node.value==='')guidePretensionN=null;
      else if(!Number.isFinite(value)||value<0||!Number.isFinite(value*(unit==='kgf'?KGF:1))){$('guide-force-state').textContent='Enter a finite nonnegative assumed baseline, or leave it unspecified.';return;}
      else guidePretensionN=value*(unit==='kgf'?KGF:1);
      const other=$(unit==='N'?'guide-pretension-kgf':'guide-pretension-N');other.value=guidePretensionN===null?'':String(Number((unit==='N'?guidePretensionN/KGF:guidePretensionN).toPrecision(12)));
      drawMechanism();publish('motion-lab-config',{config:{...config},reference_inputs:referenceInputs()});
    };
    if($('guide-force-vectors'))$('guide-force-vectors').onchange=()=>{guideForcesVisible=$('guide-force-vectors').checked;drawMechanism();publish('motion-lab-config',{config:{...config},reference_inputs:referenceInputs()});};
  }
  function springControls(){
    if(!Object.keys(springCatalog).length)return '';
    const entry=springCatalog[config.spring_topology]||springCatalog.legacy_tip,gravityBalance=config.spring_topology==='gravity_balance';
    return `<details open class="spring-preset"><summary>Spring mechanism preset</summary><div class="fields">${select('spring_topology','Attachment / mechanism',Object.entries(springCatalog).map(([id,preset])=>[id,preset.label]))}${config.spring_force_law!==undefined?select('spring_force_law','Effective force law',[['hooke','Ordinary Hooke spring'],['zero_effective','Zero effective length · compensation route']]):''}${config.spring_effective_free_length!==undefined?field('spring_effective_free_length','Effective free length','mm · zero for exact balance',1000,0,500):''}${select('spring_mode','Coil law',[['compression','Compression only'],['extension','Extension only'],['captured','Captured · bilateral']])}${select('spring_transmission','Transmission',[['direct','Direct coil'],['pullrod','Rigid pull-through rod'],['ideal_rope','Ideal zero-stretch rope']])}${select('spring_direction','Pulley payout sign',[[1,'+1 · default tangent'],[-1,'−1 · opposite tangent']])}${field('spring_pulley_radius','Spring drum radius','mm',1000,1,250)}${field('spring_bellcrank_radius','Crank arm radius','mm',1000,1,250)}${field('spring_bellcrank_offset_deg','Crank offset','°',1,-360,360)}${gravityBalance?field('spring_upper_fraction','Upper arm anchor R','mm from hip',1000*config.length,1,1000*config.length):field('spring_upper_fraction','Upper attachment from hip','% of link',100,0,100)}${field('spring_lower_fraction','Lower attachment from knee','% of link',100,0,100)}${field('spring_chassis_x','Chassis mount x','mm, right +',1000,-500,500)}${gravityBalance?field('spring_chassis_y','Mount below hip H','mm, down +',-1000,1,500):field('spring_chassis_y','Chassis mount y','mm, up +',1000,-500,500)}${field('spring_input_ref','Initial drum payout','mm',1000,1,1500)}${field('spring_coil_ref','Pull-through coil reference','mm',1000,1,1500)}</div><p class="hint" id="spring-preset-description">${entry.description}</p><p class="hint">Illustrative editable dimensions. Selecting a preset resets its demo geometry, spring rate, damping and integration setting; link geometry and mass stay as entered. Ideal transmission is massless and 100% efficient.</p></details>`;
  }
  function auxiliaryControls(){
    if(config.aux_spring_enabled===undefined)return '';
    return `<details open class="auxiliary-preset"><summary>Optional variant / extra tip spring & damper</summary><div class="fields"><label class="check"><input data-key="aux_spring_enabled" type="checkbox" ${config.aux_spring_enabled?'checked':''}>Enable additional original-tip strut (off in replacement profile)</label>${field('aux_stiffness','Ride spring k','N/m',1,0,100000)}${field('aux_damping','Ride damper c','N·s/m',1,0,2000)}${select('aux_mode','Ride coil law',[['captured','Captured · bilateral'],['compression','Compression only'],['extension','Extension only']])}${field('aux_rest_length','Manual ride free length','mm',1000,5,1000)}<label class="check"><input data-key="aux_auto_rest" type="checkbox" ${config.aux_auto_rest?'checked':''}>Zero elastic ride load at initial θ</label></div><p class="hint">The replacement unit connects the upper link to the chassis and contains its own spring and damper. This optional extra hip → original lower-link tip strut adds restoring ride stiffness; it is disabled in the replacement profile. Automatic free length starts this extra spring at zero elastic force.</p><p class="hint">Variant available with gravity balance. Extra-strut damping is independent of the replacement unit damping.</p></details>`;
  }
  function updateControls(){
    const position=config.target==='position',find=k=>$('controls').querySelector(`[data-key="${k}"]`);
    for(const key of ['period','duty'])find(key).disabled=config.wave!=='square';
    find('pulse_width').disabled=!['pulse','impulse'].includes(config.wave);
    find('fall').disabled=config.wave==='step';
    if(find('amplitude'))find('amplitude').disabled=config.wave==='impulse';
    if(find('impulse'))find('impulse').disabled=config.wave!=='impulse';
    find('rest_length').disabled=config.balance_spring&&config.spring_force_law!=='zero_effective';
    find('stiffness').disabled=config.balance_spring&&config.spring_force_law==='zero_effective';
    find('load_point').disabled=config.fixture==='wheel';find('wheel_drive_locked').disabled=config.fixture==='wheel';
    if(isMath){
      for(const key of ['fixture','target','load_point','ramp_shape','iterations'])find(key).disabled=true;
      find('iterations').closest('.field').hidden=true;
      const engineOption=$('model-view').querySelector('option[value="engine"]');if(engineOption)engineOption.disabled=true;
      $('model-view').value='annotated';
      const hints=$('controls').querySelectorAll('.hint');
      $('controls').querySelector('[data-key=target]').closest('details').querySelector('.hint').textContent='The independent equations prescribe wheel height directly. Support reaction and chassis motion are outputs; travel-limit events end the run before impact.';
    }
    if(find('spring_pulley_radius')){
      const topology=config.spring_topology,pulley=springCatalog[topology]?.kind==='pulley';
      for(const key of ['spring_pulley_radius','spring_direction','spring_input_ref'])find(key).disabled=!pulley;
      for(const key of ['spring_bellcrank_radius','spring_bellcrank_offset_deg'])find(key).disabled=!topology.includes('bellcrank');
      find('spring_coil_ref').disabled=config.spring_transmission==='direct';
      if(find('spring_effective_free_length'))find('spring_effective_free_length').disabled=config.spring_force_law!=='zero_effective';
    }
    if(find('aux_spring_enabled')){
      find('aux_spring_enabled').disabled=config.spring_topology!=='gravity_balance';
      for(const key of ['aux_stiffness','aux_damping','aux_mode','aux_auto_rest'])find(key).disabled=!config.aux_spring_enabled;
      find('aux_rest_length').disabled=!config.aux_spring_enabled||config.aux_auto_rest;
    }
    const width=config.wave==='square'?config.period*config.duty:config.pulse_width;
    const amplitude=position?config.position_amplitude*1000:config.wave==='impulse'?config.impulse/(width-(config.rise+config.fall)/2):config.amplitude;
    const units=position?'mm/s':config.target==='force'?'N/s':'N·m/s';
    $('slopes').textContent=position?`Mean rise speed ${fmt(amplitude/config.rise,1)} mm/s${config.ramp_shape==='quintic'?' · peak rise speed '+fmt(1.875*amplitude/config.rise,1)+' mm/s':''}. Positive height is upward.`:`Rise slope: ${config.rise?fmt(amplitude/config.rise,0)+' '+units:'instant edge'}; constant force bias is separate.`;
  }
  function nearest(rows,t){const i=D.bisector(r=>r.t).center(rows,t);return rows[Math.max(0,Math.min(rows.length-1,i))];}
  function decimate(rows,key){if(rows.length<=1800)return rows;const out=[],stride=Math.ceil(rows.length/700);for(let i=0;i<rows.length;i+=stride){const chunk=rows.slice(i,i+stride),lo=chunk.reduce((a,b)=>a[key]<b[key]?a:b),hi=chunk.reduce((a,b)=>a[key]>b[key]?a:b);out.push(chunk[0],lo,hi,chunk.at(-1));}return [...new Map(out.map(r=>[r.t,r])).values()].sort((a,b)=>a.t-b.t);}
  function preparePlayback(data){
    const c=data.config,points=data.frames.flatMap(f=>[f.hip,f.knee,f.hub,f.tip,[f.hub[0]-c.radius,f.hub[1]-c.radius],[f.hub[0]+c.radius,f.hub[1]+c.radius],...Object.values(f.spring_geometry?.anchors||{}).map(a=>a.world),...Object.values(f.auxiliary_spring_geometry?.anchors||{}).map(a=>a.world)]);
    if(c.chassis_shape_enabled||c.aux_spring_enabled)for(const f of data.frames)points.push([f.hip[0],f.hip[1]+.1]);
    return {xe:D.extent(points,p=>p[0]),ye:D.extent(points,p=>p[1]),inputRows:decimate(data.rows,'input'),inputPeak:data.rows.reduce((peak,row)=>Math.max(peak,Math.abs(row.input)),1e-9)};
  }
  function moveChartCursor(chart,row){
    const full=chart.container._fullLayout,value=row?.[chart.xKey];if(!full||!Number.isFinite(value))return;
    // Keep Plotly's serializable shape current for zoom and PNG export, but do
    // not recalculate every trace/axis just to move this one existing SVG line.
    for(const shape of [chart.container.layout?.shapes?.[0],full.shapes?.[0]])if(shape){shape.x0=value;shape.x1=value;}
    const axis=full.xaxis,y=full.yaxis;
    const path=chart.container.querySelector('.shapelayer path[data-index="0"]');
    if(!path||!axis?.d2p||!y)return; // Plotly may briefly replace the layer during a user redraw.
    const x=axis._offset+axis.d2p(value);
    if(Number.isFinite(x))path.setAttribute('d',`M${x},${y._offset+y._length}L${x},${y._offset}`);
  }
  function cancelPreviewRequest(){clearTimeout(previewTimer);previewAbort?.abort();previewAbort=null;previewGeneration++;}
  function previewMode(enabled){
    for(const id of ['time','play','export','case','save-data'])if($(id))$(id).disabled=enabled||!result;
    for(const id of ['passive-stability','warnings','peaks'])if($(id))$(id).hidden=enabled;
    showRecording.hidden=!enabled||!result;
  }
  function requestSetupPreview(){
    if(viewer||!Object.keys(config).length)return;
    pause();cancelPreviewRequest();inSetupMode=true;const generation=previewGeneration;
    previewMode(true);previewNotice.hidden=false;previewNotice.textContent='Preparing setup preview… Existing plots remain from the last run.';
    $('pose-values').textContent='';$('joint-values').textContent='';$('torque-values').textContent='';$('equation-values').textContent='';
    previewTimer=setTimeout(async()=>{
      const controller=new AbortController();previewAbort=controller;
      try{
        const response=await fetch('/api/setup-preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config),signal:controller.signal});
        const data=await response.json();if(generation!==previewGeneration)return;
        if(!response.ok)throw Error(data.error||'Setup preview unavailable.');
        if(data.kind!=='setup-preview'||data.solver_steps!==0)throw Error('Expected initial geometry, not a simulation run.');
        setupPreview={preview:true,config:data.config,model:data.model,frames:[data.frame],rows:[{t:0,input:0,...data.geometry}]};setupCache=preparePlayback(setupPreview);
        const title=springCatalog[data.config.spring_topology]?.label||'Linkage';
        previewNotice.textContent=`Setup preview · ${title}. No simulation or joint loads yet. Press Run; existing plots belong to the last recording.`;
        document.querySelector('.mechanism-panel h2').textContent='System setup preview';
        $('model-objects').textContent=JSON.stringify({preview:true,solver_steps:0,...data.model},null,2);
        $('joint-values').textContent='';$('torque-values').textContent='';$('equation-values').textContent='';
        $('pose-values').textContent=`θ ${fmt(data.geometry.theta_deg,1)}° · height ${fmt(data.geometry.height*1000,0)} mm · input span ${fmt(data.geometry.spring_length*1000,1)} mm`;
        drawMechanism();
      }catch(error){if(error.name==='AbortError'||generation!==previewGeneration)return;setupPreview=null;setupCache=null;previewNotice.textContent='Setup preview unavailable: '+error.message;$('mechanism').replaceChildren();}
    },100);
  }
  showRecording.onclick=()=>{cancelPreviewRequest();setupPreview=null;setupCache=null;inSetupMode=false;previewNotice.hidden=true;previewMode(false);document.querySelector('.mechanism-panel h2').textContent=recordedHeading;$('model-objects').textContent=JSON.stringify(result.model||{},null,2);$('status').textContent='Showing last recording. Run to apply the edited controls.';updatePlayback();};
  function makePlots(){
    if(!result)return;const previousCharts=charts;charts=[];const c=result.config,moving=c.fixture==='hip'?'hub':'chassis',view=$('force-view').value,probe=$('probe').value;
    const definitions=[
      [c.target==='position'?'Prescribed height · command vs achieved':'Diagnostic disturbance',c.target==='position'?'Displacement (mm)':c.target==='force'?'Input force (N)':'Input torque (N·m)',c.target==='position'?[['input_mm','Command'],['position_actual_mm','Achieved']]:[['input','Disturbance']]],
      [c.fixture==='floating'?'Chassis response':'Link angle',c.fixture==='floating'?'Chassis displacement (mm)':'θ from horizontal (°)',c.fixture==='floating'?[['chassis_displacement_mm','Chassis']]:[['theta_deg','Link angle']]],
      ['Joint reactions',view==='force'?(c.target==='position'?'Pin resultant / fixture Fy (N)':'Joint resultant (N)'):`Joint ${view.toUpperCase()} (N)`,[...[1,2,3].map(j=>['j'+j+'_'+view,'J'+j]),...(c.target==='position'&&view!=='fx'?[['driver_force','Fixture vertical']]:[])]],
      ['Torque channels','Torque (N·m)',[['actuator_torque','Knee actuator'],['spring_knee_moment',c.aux_spring_enabled?'Combined springs about knee':'Spring about knee'],['guide_link_torque','Guide on lower link'],['stop_knee_torque','Knee travel stop'],['guide_hip_reaction','Grounded guide / J1'],['wheel_drive_reaction','Wheel drive → lower link']]],
      [probe.toUpperCase()+' pin velocity','Velocity (m/s)',[[probe+'_vx','Horizontal'],[probe+'_vy','Vertical']]],
      [probe.toUpperCase()+' pin acceleration','Acceleration (m/s²)',[[probe+'_ax','Horizontal'],[probe+'_ay','Vertical']]],
      ['Knee angular velocity','Opening velocity (rad/s)',[['knee_speed','Knee α̇']]],
      ['Knee angular acceleration','Opening acceleration (rad/s²)',[['knee_accel','Knee α̈']]],
      ...(result.rows[0].spring_coil_length!==undefined?[[c.aux_spring_enabled?'Weight support coil length':'Coil length','Coil length (mm)',[['spring_coil_length','Coil',1000]]],[c.aux_spring_enabled?'Weight support coil load':'Coil load','Coil load (N)',[['spring_coil_load','Magnitude']]],[c.aux_spring_enabled?'Weight support spring energy':'Spring energy','Stored energy (J)',[['spring_energy_J','Elastic energy']]]]:[]),
      ...(c.spring_topology==='gravity_balance'&&Number.isFinite(result.rows[0].spring_equivalent_lift_N)?[['Equivalent vertical support vs angle','Equivalent lift (N)',[['spring_elastic_equivalent_lift_N','Elastic spring lift'],['spring_gravity_equivalent_N','Gravity requirement']],'theta_deg']]:[]),
      ...(c.aux_spring_enabled?[['Ride strut force components','Ride force (N)',[['aux_spring_elastic_tension','Elastic restoring'],['aux_spring_damper_tension','Damper'],['aux_spring_tension','Total ride strut']]],['Ride spring & total stored energy','Stored energy (J)',[['aux_spring_energy_J','Ride spring'],['spring_energy_J','Weight support stage'],['total_spring_energy_J','Both springs']]],['Suspension support stages','Equivalent support (N)',[['spring_elastic_equivalent_lift_N','Constant weight stage'],['aux_spring_elastic_equivalent_lift_N','Ride restoring stage'],['total_spring_equivalent_lift_N','Total with damping']]]]:[]),
    ];
    if(viewer){updatePlayback();return;}
    if(!window.Plotly)throw Error('Plotly could not load. Restart the app and reload this page.');
    for(const [title,label,requested,xKey='t'] of definitions){
      const series=requested.filter(([key])=>result.rows.some(r=>Number.isFinite(r[key])));
      const index=charts.length;
      let chart=previousCharts[index];
      if(!chart){
        const panel=document.createElement('section');panel.className='plot';
        const heading=document.createElement('h3');heading.textContent=title;
        const container=document.createElement('div');container.className='chart';container.setAttribute('aria-label',title+' versus time');panel.append(heading,container);$('plots').append(panel);
        chart={panel,container,series,revision:-1};
      }else chart.panel.querySelector('h3').textContent=title;
      chart.series=series;chart.xKey=xKey;chart.container.setAttribute('aria-label',title+' versus '+(xKey==='t'?'time':'angle'));
      const palette=colors.map(value=>cssColor(value.slice(4,-1)));
      const traces=series.map(([key,name,multiplier=1],i)=>{
        const rows=decimate(result.rows,key);
        return {type:'scatter',mode:'lines',name,x:rows.map(r=>r[xKey]),y:rows.map(r=>r[key]*multiplier),line:{color:palette[i%palette.length],width:1.8},hovertemplate:label.endsWith('(N)')?'%{x:.3f} '+(xKey==='t'?'s':'°')+'<br>'+name+': %{y:.3f} N<br>%{customdata[0]:.3f} kgf<extra></extra>':'%{x:.3f} '+(xKey==='t'?'s':'°')+'<br>'+name+': %{y:.4g}<extra></extra>',customdata:rows.map(r=>[r[key]/KGF,r.t])};
      });
      const cursor={type:'line',xref:'x',yref:'paper',x0:nearest(result.rows,time)[xKey],x1:nearest(result.rows,time)[xKey],y0:0,y1:1,line:{color:cssColor('--muted'),width:1,dash:'dot'}};
      const revision=backend+'-'+runRevision+'-'+title+'-'+series.map(([key])=>key).join('|');
      const preserveZoom=chart.viewRevision===revision&&chart.container._fullLayout;
      const layout={height:300,margin:{l:75,r:18,t:16,b:78},paper_bgcolor:cssColor('--panel'),plot_bgcolor:cssColor('--panel'),font:{family:'system-ui,Segoe UI,sans-serif',color:cssColor('--text'),size:11},hovermode:'x unified',dragmode:'zoom',uirevision:revision,xaxis:{title:{text:xKey==='t'?'Time (s)':'Link angle θ (°)'},gridcolor:cssColor('--line'),zerolinecolor:cssColor('--line'),...(preserveZoom?{range:[...chart.container._fullLayout.xaxis.range]}:xKey==='t'?{range:[0,result.rows.at(-1).t]}:{autorange:true}),automargin:true},yaxis:{title:{text:label},gridcolor:cssColor('--line'),zerolinecolor:cssColor('--line'),...(preserveZoom&&!chart.container._fullLayout.yaxis.autorange?{range:[...chart.container._fullLayout.yaxis.range]}:{autorange:true}),automargin:true},legend:{orientation:'h',x:0,y:-.24,font:{size:10}},shapes:[cursor]};
      window.Plotly.react(chart.container,traces,layout,{responsive:true,scrollZoom:true,displaylogo:false,toImageButtonOptions:{format:'png',filename:backend+'-'+title.replaceAll(/[^a-z0-9]+/gi,'-')},modeBarButtonsToRemove:['lasso2d','select2d']}).then(()=>{
        if(!chart.clickBound){chart.container.on('plotly_click',event=>{const t=event.points?.[0]?.customdata?.[1];if(Number.isFinite(t)){pause();time=t;updatePlayback();}});chart.container.on('plotly_afterplot',()=>{if(result)moveChartCursor(chart,nearest(result.rows,time));});chart.clickBound=true;}
        moveChartCursor(chart,nearest(result.rows,time));
      });
      chart.revision=runRevision;chart.viewRevision=revision;charts.push(chart);
    }
    for(const stale of previousCharts.slice(charts.length)){window.Plotly.purge(stale.container);stale.panel.remove();}
    lastReadoutStamp=-Infinity;updatePlayback();
  }
  function drawMechanism(){
    if(inSetupMode&&!setupPreview)return;
    const display=setupPreview||result;if(!display)return;const svg=D.select($('mechanism')),W=$('mechanism').clientWidth,H=$('mechanism').clientHeight,c=display.config;
    const modelHeight=H-90;
    if(W<1||H<1)return;
    const frame=nearest(display.frames,setupPreview?0:time);
    const chassisShown=c.chassis_shape_enabled||c.aux_spring_enabled,guideVisible=config.guide_pulleys_visible??c.guide_pulleys_visible;
    const {xe,ye}=setupPreview?setupCache:playbackCache,scale=Math.min((W-100)/(xe[1]-xe[0]),(modelHeight-65)/(ye[1]-ye[0]));
    const x=v=>W/2+(v-(xe[0]+xe[1])/2)*scale,y=v=>modelHeight/2-(v-(ye[0]+ye[1])/2)*scale;
    svg.attr('viewBox',`0 0 ${W} ${H}`).attr('data-mode',setupPreview?'setup-preview':'recorded');svg.selectAll('*').remove();svg.append('title').text((setupPreview?'Initial setup only; ':isMath?'Recorded mathematical-model geometry; ':'Actual recorded Pymunk poses; ')+(springCatalog[c.spring_topology]?.label||'spring runs from hip to lower-link tip')+'.');
    const A=frame.hip,B=frame.knee,C=frame.hub,E=frame.tip,row=nearest(display.rows,setupPreview?0:time);
    const point=p=>[x(p[0]),y(p[1])];
    const path=p=>D.line()(p.map(point));
    const engineView=$('model-view').value==='engine'&&frame.debug_draw;
    if(engineView){
      const factor=display.model?.debug_scale||600,position=p=>[x(p[0]/factor),y(p[1]/factor)],color=c=>`rgba(${c[0]},${c[1]},${c[2]},${c[3]/255})`;
      for(const p of frame.debug_draw){
        if(p.kind==='circle'){const q=position(p.pos),r=p.radius/factor*scale,guideCircle=c.guide_pulleys_visible&&((Math.abs(p.radius/factor-c.guide_hip_radius)<1e-8&&Math.hypot(p.pos[0]/factor-(frame.guide_pulleys?.hip.center||A)[0],p.pos[1]/factor-(frame.guide_pulleys?.hip.center||A)[1])<1e-6)||(Math.abs(p.radius/factor-c.guide_hip_radius/2)<1e-8&&Math.hypot(p.pos[0]/factor-(frame.guide_pulleys?.knee.center||B)[0],p.pos[1]/factor-(frame.guide_pulleys?.knee.center||B)[1])<1e-6));svg.append('circle').attr('class',guideCircle?'engine-shape engine-guide-pulley':'engine-shape').attr('display',guideCircle&&!guideVisible?'none':null).attr('cx',q[0]).attr('cy',q[1]).attr('r',r).attr('fill',color(p.fill)).attr('stroke',color(p.outline));if(!guideCircle)svg.append('line').attr('x1',q[0]).attr('y1',q[1]).attr('x2',q[0]+r*Math.cos(p.angle)).attr('y2',q[1]-r*Math.sin(p.angle)).attr('stroke',color(p.outline));}
        else if(p.kind==='capsule'){const a=position(p.a),b=position(p.b);svg.append('line').attr('class','engine-shape').attr('x1',a[0]).attr('y1',a[1]).attr('x2',b[0]).attr('y2',b[1]).attr('stroke',color(p.outline)).attr('stroke-width',2*p.radius/factor*scale+2).attr('stroke-linecap','round');svg.append('line').attr('x1',a[0]).attr('y1',a[1]).attr('x2',b[0]).attr('y2',b[1]).attr('stroke',color(p.fill)).attr('stroke-width',2*p.radius/factor*scale).attr('stroke-linecap','round');}
        else if(p.kind==='segment'){const a=position(p.a),b=position(p.b);svg.append('line').attr('class','engine-constraint').attr('x1',a[0]).attr('y1',a[1]).attr('x2',b[0]).attr('y2',b[1]).attr('stroke',color(p.color)).attr('stroke-width',1.5);}
        else if(p.kind==='dot'){const q=position(p.pos);svg.append('circle').attr('class','engine-constraint').attr('cx',q[0]).attr('cy',q[1]).attr('r',p.size/2).attr('fill',color(p.color));}
        else if(p.kind==='polygon')svg.append('path').attr('class',chassisShown?'engine-shape engine-chassis':'engine-shape').attr('d',D.line()(p.vertices.map(position))+'Z').attr('fill',color(p.fill)).attr('stroke',color(p.outline));
      }
    }else{
    svg.append('path').attr('d',path([A,B])).attr('stroke','var(--blue)').attr('stroke-width',8).attr('stroke-linecap','round').attr('fill','none');
    svg.append('path').attr('d',path([E,C])).attr('stroke','var(--accent)').attr('stroke-width',8).attr('stroke-linecap','round').attr('fill','none');
    svg.append('circle').attr('cx',x(C[0])).attr('cy',y(C[1])).attr('r',c.radius*scale).attr('fill','none').attr('stroke','var(--text)').attr('stroke-width',2.5);
    svg.append('path').attr('d',`M${x(C[0])-c.radius*scale},${y(C[1])}h${2*c.radius*scale}M${x(C[0])},${y(C[1])-c.radius*scale}v${2*c.radius*scale}`).attr('stroke','var(--line)').attr('stroke-width',1);
    if(!frame.spring_geometry){
    const a=point(A),b=point(E),dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy),normal=[-dy/length,dx/length];
    const coil=Array.from({length:23},(_,i)=>{const f=i/22,offset=(i<3||i>19)?0:(i%2?5:-5);return[a[0]+dx*f+normal[0]*offset,a[1]+dy*f+normal[1]*offset];});
    svg.append('path').attr('d',D.line()(coil)).attr('stroke','var(--orange)').attr('stroke-width',2).attr('fill','none');

    }
    }
    if(chassisShown){const hip=point(A),chassis=svg.append('g').attr('class','chassis-body'),actualChassis=engineView&&frame.debug_draw.some(p=>p.kind==='polygon');if(!actualChassis)chassis.append('rect').attr('x',hip[0]-.07*scale).attr('y',hip[1]-.0275*scale).attr('width',.14*scale).attr('height',.055*scale).attr('rx',3).attr('fill','var(--panel)').attr('stroke','var(--text)').attr('stroke-width',2);chassis.append('text').attr('x',hip[0]).attr('y',hip[1]-.0275*scale-12).attr('text-anchor','middle').text('Chassis · J1 · pitch held');}
    if(guideVisible&&guideModule)drawGuideBelt(svg,frame,row,point,scale,c,engineView,display);
    if(frame.spring_geometry)drawSpringGeometry(svg,frame,row,point,scale,c);
    if(c.aux_spring_enabled&&frame.auxiliary_spring_geometry)drawAuxiliaryGeometry(svg,frame,row,point,scale,c);
    const fixed=c.fixture==='hip'?A:C,fp=point(fixed);
    if(c.fixture!=='floating')svg.append('path').attr('d',`M${fp[0]-24},${fp[1]-10}h48`).attr('stroke','var(--text)').attr('stroke-width',3);
    for(const [p,name,offset] of [[A,'J1 · hip',chassisShown?[-72,12]:[-14,-16]],[B,'J2 · knee',[13,-3]],[C,'J3 · wheel pin',[10,17]],[E,c.spring_topology&&c.spring_topology!=='legacy_tip'?'Lower-link tip':'Spring tip',[10,-12]]]){
      const pp=point(p);svg.append('circle').attr('cx',pp[0]).attr('cy',pp[1]).attr('r',4).attr('fill','var(--panel)').attr('stroke','var(--text)').attr('stroke-width',1.5);
      svg.append('text').attr('x',Math.min(W-105,Math.max(5,pp[0]+offset[0]))).attr('y',Math.min(H-8,Math.max(13,pp[1]+offset[1]))).text(name);
    }
    if(!setupPreview&&$('forces').checked){
      const peak=Math.max(result.peaks.j1_force.value,result.peaks.j2_force.value,result.peaks.j3_force.value,1);
      for(const [p,j] of [[A,1],[B,2],[C,3]]){const pp=point(p),fx=row['j'+j+'_fx'],fy=row['j'+j+'_fy'],mag=Math.hypot(fx,fy);if(mag<1e-8)continue;const k=75/peak,tx=pp[0]+fx*k,ty=pp[1]-fy*k,angle=Math.atan2(ty-pp[1],tx-pp[0]);
        svg.append('path').attr('d',`M${pp[0]},${pp[1]}L${tx},${ty}M${tx-6*Math.cos(angle-.5)},${ty-6*Math.sin(angle-.5)}L${tx},${ty}L${tx-6*Math.cos(angle+.5)},${ty-6*Math.sin(angle+.5)}`).attr('stroke',colors[j-1]).attr('stroke-width',2).attr('fill','none');
      }
    }
    if(setupPreview)return;
    const inputPoint=point(c.target==='knee'?B:c.fixture==='wheel'?A:c.target==='position'?C:c.load_point==='contact'?[C[0],C[1]-c.radius]:C);
    const prescribed=c.target==='position'?{origin:point(result.position_origin||[0,0]),target:point(frame.position_target||C)}:null;
    drawDisturbance(svg,W,H,inputPoint,row,prescribed);
  }
  function guidePose(frame,c){return frame.guide_pulleys||{ratio:2,carrier_angle:frame.upper_angle,hip:{center:frame.hip,angle:0,radius:c.guide_hip_radius||.028,body:'hip'},knee:{center:frame.knee,angle:frame.lower_angle,radius:(c.guide_hip_radius||.028)/2,body:'lower'}};}
  function drawGuideBelt(svg,frame,row,point,scale,c,engineView,display){
    const pose=guidePose(frame,c),initial=guidePose(display.frames[0],c),group=svg.append('g').attr('class','guide-belt-overlay');
    let geometry;
    try{geometry=guideModule.openBeltGeometry(pose.hip.center,pose.knee.center,pose.hip.radius,pose.knee.radius);}catch(error){group.append('text').attr('x',12).attr('y',43).text(error.message);return;}
    const phase=guideModule.beltMaterialPhase(pose.hip.radius,pose.carrier_angle,pose.hip.angle,initial.carrier_angle-initial.hip.angle),difference=display.preview?null:Number.isFinite(row.guide_tension_difference_N)?row.guide_tension_difference_N:row.guide_link_torque/pose.knee.radius;
    group.attr('data-phase-m',phase).attr('data-ratio',pose.ratio).attr('data-tension-difference-N',difference);
    const stations=Array.from({length:193},(_,i)=>point(guideModule.sampleBelt(geometry,i*geometry.length/192).point));
    group.append('path').attr('class','guide-belt-loop').attr('d',D.line()(stations)+'Z').attr('fill','none').attr('stroke','var(--muted)').attr('stroke-width',2);
    for(const [key,body,color] of [['hip','hip','var(--blue)'],['knee','lower','var(--purple)']]){
      const pulley=pose[key],start=initial[key],center=point(pulley.center),radius=pulley.radius*scale,p=group.append('g').attr('class','guide-pulley-'+key).attr('data-radius-m',pulley.radius);
      if(!engineView||!frame.guide_pulleys)p.append('circle').attr('cx',center[0]).attr('cy',center[1]).attr('r',radius).attr('fill','var(--panel)').attr('stroke',color).attr('stroke-width',1.5);
      const marker=point([pulley.center[0]+pulley.radius*.85*Math.cos(pulley.angle),pulley.center[1]+pulley.radius*.85*Math.sin(pulley.angle)]);
      p.append('line').attr('class','guide-body-mark').attr('data-body',body).attr('data-angle',pulley.angle).attr('data-relative-carrier-angle',pulley.angle-pose.carrier_angle).attr('x1',center[0]).attr('y1',center[1]).attr('x2',marker[0]).attr('y2',marker[1]).attr('stroke',color).attr('stroke-width',2.5);
      const change=pulley.angle-start.angle;
      if(Math.abs(change)>1e-7){const arc=Array.from({length:17},(_,i)=>point([pulley.center[0]+pulley.radius*1.2*Math.cos(start.angle+change*i/16),pulley.center[1]+pulley.radius*1.2*Math.sin(start.angle+change*i/16)]));p.append('path').attr('class','guide-body-angle-arc').attr('data-body',body).attr('d',D.line()(arc)).attr('fill','none').attr('stroke',color).attr('stroke-width',1.5);}
      const pivot=p.append('g').attr('class','guide-pivot-center').attr('data-body',body);pivot.append('path').attr('d',`M${center[0]-4},${center[1]}h8M${center[0]},${center[1]-4}v8`).attr('stroke','var(--text)').attr('stroke-width',1);pivot.append('circle').attr('cx',center[0]).attr('cy',center[1]).attr('r',1.7).attr('fill','var(--text)');
    }
    for(const dot of guideModule.beltMaterialDots(geometry,phase,24)){const p=point(dot.point);group.append('circle').attr('class','guide-belt-dot').attr('data-material-index',dot.index).attr('data-station-m',dot.distance).attr('cx',p[0]).attr('cy',p[1]).attr('r',2.1).attr('fill','var(--accent)').attr('stroke','var(--panel)').attr('stroke-width',.7);}
    const loads=display.preview?{forces:[],assumed:false}:guideModule.guideSpanLoads(geometry,difference,guidePretensionN),state=display.preview?'Setup only · run to calculate tension':loads.assumed?`Assumed spans ${fmt(loads.span_tensions_N.plus,1)} / ${fmt(loads.span_tensions_N.minus,1)} N · illustrative`:`Required ΔT ${fmt(difference,1)} N · pretension unspecified`;
    if($('guide-force-state'))$('guide-force-state').textContent=state+'. No belt bearing forces are included in the solver.';
    group.append('text').attr('class','guide-ratio-label').attr('x',12).attr('y',43).text(`Guide 2:1 · radii ${fmt(pose.hip.radius*1000,0)} / ${fmt(pose.knee.radius*1000,0)} mm`);
    group.append('text').attr('class','guide-force-label').attr('x',12).attr('y',59).text(state);
    group.append('text').attr('class','guide-body-role-label').attr('x',12).attr('y',75).text('Hip → chassis · knee → r₂ · carrier → r₁');
    if(guideForcesVisible){const max=Math.max(...loads.forces.map(f=>f.magnitude),1);for(const force of loads.forces){if(force.magnitude<1e-8)continue;const p=point(force.point),length=35*force.magnitude/max,end=[p[0]+force.direction[0]*length,p[1]-force.direction[1]*length],angle=Math.atan2(end[1]-p[1],end[0]-p[0]);group.append('path').attr('class','guide-span-force').attr('data-body',force.body).attr('data-span',force.span).attr('data-role',force.role).attr('data-magnitude-N',force.magnitude).attr('d',`M${p[0]},${p[1]}L${end[0]},${end[1]}M${end[0]-5*Math.cos(angle-.5)},${end[1]-5*Math.sin(angle-.5)}L${end[0]},${end[1]}L${end[0]-5*Math.cos(angle+.5)},${end[1]-5*Math.sin(angle+.5)}`).attr('fill','none').attr('stroke',force.span==='plus'?'var(--blue)':'var(--purple)').attr('stroke-width',1.7).attr('stroke-dasharray',force.role==='difference'?'3 2':null);}}
  }
  function drawSpringGeometry(svg,frame,row,point,scale,c){
    const geometry=frame.spring_geometry,a=geometry.anchors?.a?.world,b=geometry.anchors?.b?.world;
    if(!a||!b)return;
    const group=svg.append('g').attr('class','spring-mechanism-overlay').attr('data-topology',geometry.topology);
    const pa=point(a),pb=point(b),dx=pb[0]-pa[0],dy=pb[1]-pa[1],span=Math.max(Math.hypot(dx,dy),1),u=[dx/span,dy/span],n=[-u[1],u[0]];
    const line=(start,end,color='var(--orange)',width=2)=>group.append('line').attr('x1',start[0]).attr('y1',start[1]).attr('x2',end[0]).attr('y2',end[1]).attr('stroke',color).attr('stroke-width',width);
    if(geometry.topology==='gravity_balance'){
      // The support anchor belongs to the chassis through this ideal rigid mount.
      const hip=point(frame.hip),rx=pb[0]-hip[0],ry=pb[1]-hip[1],r=Math.max(Math.hypot(rx,ry),1),normal=[ry/r,-rx/r];
      line(hip,pa,'var(--muted)',4).attr('class','chassis-spring-mount');
      group.append('text').attr('class','spring-mount-height').attr('x',hip[0]-10).attr('y',(hip[1]+pa[1])/2).attr('text-anchor','end').text(`H ${fmt(Math.abs(a[1]-frame.hip[1])*1000,0)} mm`);
      line([hip[0]+normal[0]*10,hip[1]+normal[1]*10],[pb[0]+normal[0]*10,pb[1]+normal[1]*10],'var(--muted)',1).attr('stroke-dasharray','3 3').attr('class','upper-spring-lever-arm');
      group.append('text').attr('class','spring-lever-radius').attr('x',(hip[0]+pb[0])/2+normal[0]*24).attr('y',(hip[1]+pb[1])/2+normal[1]*24).text(`R ${fmt(Math.hypot(b[0]-frame.hip[0],b[1]-frame.hip[1])*1000,0)} mm`);
    }
    const coil=(start,end,target=group)=>{const delta=[end[0]-start[0],end[1]-start[1]],length=Math.max(Math.hypot(...delta),1),normal=[-delta[1]/length,delta[0]/length];const points=Array.from({length:25},(_,i)=>{const t=i/24,w=i<3||i>21?0:(i%2?5:-5);return[start[0]+t*delta[0]+w*normal[0],start[1]+t*delta[1]+w*normal[1]];});return target.append('path').attr('class','spring-coil').attr('d',D.line()(points)).attr('fill','none').attr('stroke','var(--orange)').attr('stroke-width',2);};
    if(geometry.kind==='pulley'){
      const center=point(geometry.topology==='hip_pulley'?frame.hip:frame.knee),radius=c.spring_pulley_radius*scale;
      group.append('circle').attr('class','spring-drum').attr('cx',center[0]).attr('cy',center[1]).attr('r',radius).attr('fill','var(--panel)').attr('stroke','var(--orange)').attr('stroke-width',2);
      line(center,pa,'var(--orange)',1);line(pa,pb,'var(--orange)',2);
      group.append('text').attr('x',center[0]+radius+8).attr('y',center[1]+radius+15).text(`Drum r ${fmt(c.spring_pulley_radius*1000,0)} mm`);
    }
    if(geometry.topology.includes('bellcrank')){
      const center=point(geometry.topology==='hip_bellcrank'?frame.hip:frame.knee);
      line(center,pb,'var(--purple)',5);group.append('circle').attr('cx',center[0]).attr('cy',center[1]).attr('r',4).attr('fill','var(--purple)');
    }
    const pullThrough=c.spring_transmission!=='direct',zeroEffective=c.spring_force_law==='zero_effective'||(!c.spring_force_law&&c.spring_topology==='gravity_balance');
    if(geometry.topology==='gravity_balance'){
      // A routed unit symbol joins only its real force anchors. Its drawn span
      // is not the finite physical coil length, which remains in the readouts.
      const unit=group.append('g').attr('class','routed-replacement-unit').attr('data-anchor-a',a.join(',')).attr('data-anchor-b',b.join(',')),p=(t,offset)=>[pa[0]+t*dx+n[0]*offset,pa[1]+t*dy+n[1]*offset];
      coil(pa,pb,unit).attr('class','spring-coil replacement-schematic-coil');
      unit.append('path').attr('class','replacement-damper').attr('d',D.line()([pa,p(.12,8),p(.38,8)])+D.line()([p(.38,4),p(.62,4),p(.62,12),p(.38,12),p(.38,4)])+D.line()([p(.48,8),p(.85,8),pb])).attr('fill','none').attr('stroke','var(--orange)').attr('stroke-width',1.5);
      group.append('text').attr('x',12).attr('y',22).attr('class','spring-transfer-label').text('Routed replacement unit (schematic)');
    }
    else if(geometry.kind==='direct'&&!pullThrough&&!zeroEffective)coil(pa,pb);
    else{
      line(pa,pb,'var(--orange)',2).attr('stroke-dasharray',c.spring_transmission==='ideal_rope'?'4 3':null);
      // Coil is a separate ideal transfer element; endpoints remain the real force sites.
      const start=[pa[0]+n[0]*24,pa[1]+n[1]*24],coilPixels=Math.max(28,Math.min(150,(row.spring_coil_length||c.spring_coil_ref)*scale)),end=[start[0]+u[0]*coilPixels,start[1]+u[1]*coilPixels];
      coil(start,end);
      line([start[0]-u[0]*10,start[1]-u[1]*10],[end[0]+u[0]*20,end[1]+u[1]*20],'var(--muted)',1.3);
      for(const p of [start,end])line([p[0]-n[0]*9,p[1]-n[1]*9],[p[0]+n[0]*9,p[1]+n[1]*9],'var(--muted)',3);
      group.append('text').attr('x',zeroEffective?12:(start[0]+end[0])/2+n[0]*18).attr('y',zeroEffective?22:(start[1]+end[1])/2+n[1]*18).attr('class','spring-transfer-label').text(zeroEffective?`Compensated route · finite coil free length ${fmt(c.rest_length*1000,0)} mm`:pullThrough?'Ideal pull-through coil':'Ideal drum coil');
    }
    for(const site of geometry.force_sites||[]){
      const p=point(site.world||site.point);group.append('circle').attr('class','spring-force-anchor').attr('data-body',site.body).attr('cx',p[0]).attr('cy',p[1]).attr('r',4).attr('fill','var(--panel)').attr('stroke','var(--orange)').attr('stroke-width',1.5);
      if($('forces').checked&&Math.abs(row.spring_tension)>1e-8){const length=28*Math.sign(row.spring_tension),end=[p[0]+site.direction[0]*length,p[1]-site.direction[1]*length],angle=Math.atan2(end[1]-p[1],end[0]-p[0]);line(p,end,'var(--orange)',2);group.append('path').attr('d',`M${end[0]-6*Math.cos(angle-.5)},${end[1]-6*Math.sin(angle-.5)}L${end[0]},${end[1]}L${end[0]-6*Math.cos(angle+.5)},${end[1]-6*Math.sin(angle+.5)}`).attr('stroke','var(--orange)').attr('fill','none');}
    }
  }
  function drawAuxiliaryGeometry(svg,frame,row,point,scale,c){
    const geometry=frame.auxiliary_spring_geometry,a=geometry.anchors?.a?.world,b=geometry.anchors?.b?.world;if(!a||!b)return;
    const pa=point(a),pb=point(b),dx=pb[0]-pa[0],dy=pb[1]-pa[1],span=Math.max(Math.hypot(dx,dy),1),u=[dx/span,dy/span],n=[-u[1],u[0]],length=(frame.auxiliary_spring_coil_length||row.aux_spring_coil_length||span/scale)*scale;
    const group=svg.append('g').attr('class','auxiliary-spring-overlay').attr('data-mode',c.aux_mode);
    group.append('line').attr('x1',pa[0]).attr('y1',pa[1]).attr('x2',pb[0]).attr('y2',pb[1]).attr('stroke','var(--purple)').attr('stroke-width',1).attr('stroke-dasharray',row.aux_spring_slack?'4 3':null);
    const coilPoints=Array.from({length:25},(_,i)=>{const t=i/24,w=i<3||i>21?0:(i%2?5:-5);return[pa[0]+t*u[0]*length+w*n[0],pa[1]+t*u[1]*length+w*n[1]];});
    group.append('path').attr('class','ride-spring-coil').attr('d',D.line()(coilPoints)).attr('fill','none').attr('stroke','var(--purple)').attr('stroke-width',2.5);
    // Rod/damper line shares the same actual two attachment points.
    group.append('line').attr('x1',pa[0]+n[0]*8).attr('y1',pa[1]+n[1]*8).attr('x2',pb[0]+n[0]*8).attr('y2',pb[1]+n[1]*8).attr('stroke','var(--purple)').attr('stroke-width',1.5);
    const center=[(pa[0]+pb[0])/2,(pa[1]+pb[1])/2],label=[Math.max(140,center[0]-70),center[1]+24];group.append('path').attr('d',`M${label[0]+7},${label[1]-4}L${center[0]-9},${center[1]+4}`).attr('fill','none').attr('stroke','var(--purple)').attr('stroke-width',1).attr('stroke-dasharray','2 2');group.append('text').attr('class','ride-spring-label').attr('x',label[0]).attr('y',label[1]).attr('text-anchor','end').text('Ride spring + damper');
    for(const site of geometry.force_sites||[]){const p=point(site.world||site.point);group.append('circle').attr('class','auxiliary-force-anchor').attr('cx',p[0]).attr('cy',p[1]).attr('r',4).attr('fill','var(--panel)').attr('stroke','var(--purple)').attr('stroke-width',1.5);if($('forces').checked&&Math.abs(row.aux_spring_tension)>1e-8){const k=26*Math.sign(row.aux_spring_tension),end=[p[0]+site.direction[0]*k,p[1]-site.direction[1]*k],angle=Math.atan2(end[1]-p[1],end[0]-p[0]);group.append('path').attr('d',`M${p[0]},${p[1]}L${end[0]},${end[1]}M${end[0]-6*Math.cos(angle-.5)},${end[1]-6*Math.sin(angle-.5)}L${end[0]},${end[1]}L${end[0]-6*Math.cos(angle+.5)},${end[1]-6*Math.sin(angle+.5)}`).attr('stroke','var(--purple)').attr('stroke-width',2).attr('fill','none');}}
  }
  function drawDisturbance(svg,W,H,target,row,prescribed){
    const c=result.config,multiplier=c.target==='position'?1000:1,unit=c.target==='position'?'mm':c.target==='knee'?'N·m':'N',peak=Math.max(playbackCache.inputPeak*multiplier,.000001),value=row.input*multiplier;
    const base=H-38,pps=(W-32)/3,amp=18,x=t=>target[0]+(t-time)*pps,y=v=>base-v/peak*amp;
    const lane=svg.append('g').attr('class','disturbance-lane').attr('data-input',value);
    lane.append('text').attr('x',16).attr('y',H-80).text(`${c.target==='position'?'Moving height':'Moving input'} (${unit})`);
    lane.append('text').attr('class','disturbance-label').attr('x',W-16).attr('y',H-80).attr('text-anchor','end').text(`Δ ${value>=0?'+':''}${fmt(value,2)} ${unit}`);
    const clip='disturbance-clip';lane.append('defs').append('clipPath').attr('id',clip).append('rect').attr('x',16).attr('y',H-73).attr('width',W-32).attr('height',57);
    const marks=lane.append('g').attr('clip-path',`url(#${clip})`);
    marks.append('line').attr('x1',16).attr('x2',W-16).attr('y1',base).attr('y2',base).attr('stroke','var(--line)');
    marks.append('path').datum(playbackCache.inputRows).attr('class','disturbance-profile').attr('d',D.line().x(r=>x(r.t)).y(r=>y(r.input*multiplier))).attr('fill','none').attr('stroke','var(--blue)').attr('stroke-width',2.5);
    marks.append('line').attr('x1',target[0]).attr('x2',target[0]).attr('y1',H-73).attr('y2',H-16).attr('stroke','var(--orange)').attr('stroke-width',1);
    marks.append('circle').attr('class','disturbance-marker').attr('cx',target[0]).attr('cy',y(value)).attr('r',4).attr('fill','var(--orange)');
    lane.append('text').attr('x',16).attr('y',H-2).text(c.target==='position'?(W<420?'← Height input · force measured':'← Prescribed height · reaction force is an output'):W<420?'← Applied input · bias separate':'Force / torque profile travels right → left; bias is separate.');
    if(prescribed){
      svg.append('line').attr('class','position-reference').attr('x1',prescribed.target[0]-17).attr('x2',prescribed.target[0]+17).attr('y1',prescribed.target[1]).attr('y2',prescribed.target[1]).attr('stroke','var(--orange)').attr('stroke-width',2);
      if(Math.abs(value)>1e-8){
        const px=target[0]-15,sy=prescribed.origin[1],ey=prescribed.target[1],sign=Math.sign(sy-ey);
        const arrow=svg.append('g').attr('class','disturbance-arrow').attr('data-kind','position').attr('data-value',value).attr('stroke','var(--orange)').attr('stroke-width',2).attr('fill','none');
        arrow.append('path').attr('d',`M${px},${sy}V${ey}M${px-4},${ey+sign*5}L${px},${ey}L${px+4},${ey+sign*5}M${px-4},${sy-sign*5}L${px},${sy}L${px+4},${sy-sign*5}`);
      }
      return;
    }
    if(Math.abs(value)<1e-8)return;
    const arrow=svg.append('g').attr('class','disturbance-arrow').attr('data-value',value).attr('stroke','var(--orange)').attr('stroke-width',2.5).attr('fill','none');
    let end,direction;
    if(c.target==='knee'){
      const sign=Math.sign(value),r=29,angles=D.range(31).map(i=>sign*(.35+i/30*4.6));
      const points=angles.map(a=>[target[0]+r*Math.cos(a),target[1]-r*Math.sin(a)]);
      arrow.append('path').attr('d',D.line()(points));end=points.at(-1);const prev=points.at(-2);direction=Math.atan2(end[1]-prev[1],end[0]-prev[0]);
    }else{
      const length=14+32*Math.abs(value)/peak;end=[target[0],target[1]-Math.sign(value)*length];direction=-Math.sign(value)*Math.PI/2;
      arrow.append('line').attr('x1',target[0]).attr('y1',target[1]).attr('x2',end[0]).attr('y2',end[1]);
    }
    arrow.append('path').attr('d',`M${end[0]-7*Math.cos(direction-.5)},${end[1]-7*Math.sin(direction-.5)}L${end[0]},${end[1]}L${end[0]-7*Math.cos(direction+.5)},${end[1]-7*Math.sin(direction+.5)}`);
    svg.append('circle').attr('cx',target[0]).attr('cy',target[1]).attr('r',5).attr('fill','var(--orange)');
  }
  function updateReadouts(row,c){
    $('pose-values').innerHTML=`<span>θ ${fmt(row.theta_deg,1)}°</span><span>Height ${fmt(row.height*1000,0)} mm</span><span>Input span ${fmt(row.spring_length*1000,1)} mm</span>${Number.isFinite(row.spring_coil_length)?`<span>Coil ${fmt(row.spring_coil_length*1000,1)} mm · ${row.spring_slack?'slack':'engaged'}</span>`:''}`;
    $('joint-values').innerHTML=[1,2,3].map(j=>`<tr><td>J${j}</td><td>${forceCell(row['j'+j+'_fx'])}</td><td>${forceCell(row['j'+j+'_fy'])}</td><td>${forceCell(row['j'+j+'_force'])}</td></tr>`).join('');
    $('equation-values').innerHTML=[['L₂(−Fz cosθ + Fy sinθ): hub lever','ref_Min_wheel_moment','check_lower_moment_Nm','N·m'],['L₂(−Fz cosθ + Fy sinθ) + Fy r_w: contact lever','ref_Min_contact_moment','check_contact_moment_Nm','N·m'],['L₁(Bz cosθ + By sinθ)','ref_Mact_knee_moment','check_upper_moment_Nm','N·m'],['√(By² + Bz²)','ref_Br','check_Br_N','N']].map(([label,key,error,unit])=>`<tr><td>${label}</td><td>${fmt(row[key],3)} ${unit}</td><td>${Number.isFinite(row[error])?row[error].toExponential(2):'—'} ${unit}</td></tr>`).join('');
    $('torque-values').innerHTML=[...(c.target==='position'?[['Motion fixture reaction','driver_force','N']]:[]),[c.aux_spring_enabled?'Weight support stage tension':'Spring input tension','spring_tension','N'],...(Number.isFinite(row.spring_coil_load)?[[c.aux_spring_enabled?'Weight support coil load':'Coil load','spring_coil_load','N'],[c.aux_spring_enabled?'Weight support stored energy':'Stored spring energy','spring_energy_J','J']]:[]),...(Number.isFinite(row.spring_equivalent_lift_N)?[['Spring + damper equivalent lift','spring_equivalent_lift_N','N'],['Elastic spring equivalent lift','spring_elastic_equivalent_lift_N','N'],['Gravity equivalent load','spring_gravity_equivalent_N','N'],['Balance residual','spring_balance_residual_N','N']]:[]),[c.aux_spring_enabled?'Both spring moments about knee':'Spring moment about knee','spring_knee_moment','N·m'],...(c.aux_spring_enabled?[['Ride coil length','aux_spring_coil_length','mm'],['Ride elastic force','aux_spring_elastic_tension','N'],['Ride damping force','aux_spring_damper_tension','N'],['Ride total force','aux_spring_tension','N'],['Ride spring energy','aux_spring_energy_J','J'],['Both spring energies','total_spring_energy_J','J']]:[]),['Knee actuator','actuator_torque','N·m'],...(Number.isFinite(row.guide_tension_difference_N)?[['Guide required ΔT','guide_tension_difference_N','N'],['Belt speed relative to carrier','guide_belt_speed_relative','m/s']]:[]),['Guide on lower link','guide_link_torque','N·m'],['Grounded guide at J1','guide_hip_reaction','N·m'],['Knee travel stop','stop_knee_torque','N·m'],['Wheel contact torque','wheel_external_moment','N·m'],['Wheel drive → lower link','wheel_drive_reaction','N·m'],['Wheel angular speed','wheel_speed','rad/s'],[c.fixture==='hip'?'Hub velocity':'Chassis velocity',(c.fixture==='hip'?'hub':'chassis')+'_vy','m/s'],[c.fixture==='hip'?'Hub acceleration':'Chassis acceleration',(c.fixture==='hip'?'hub':'chassis')+'_ay','m/s²']].map(([name,key,unit])=>`<dt>${name}</dt><dd>${unit==='N'?forceFmt(row[key]):unit==='mm'?fmt(row[key]*1000,1)+' mm':fmt(row[key])+' '+unit}</dd>`).join('');
  }
  function updatePlayback(){
    if(inSetupMode){drawMechanism();return;}
    if(!result)return;time=Math.max(0,Math.min(result.rows.at(-1).t,time));const row=nearest(result.rows,time),stamp=performance.now();
    $('time').value=time;$('time-value').textContent=fmt(time,3)+' s';
    // Text needs a readable cadence; motion and the chart cursor use every display frame.
    if(!playing||stamp-lastReadoutStamp>=1000/15){updateReadouts(row,result.config);lastReadoutStamp=stamp;}
    for(const chart of charts)moveChartCursor(chart,row);
    drawMechanism();
  }
  function pause(){const wasPlaying=playing;playing=false;cancelAnimationFrame(raf);last=0;$('play').textContent='Play';if(wasPlaying&&result)updateReadouts(nearest(result.rows,time),result.config);}
  $('play').onclick=()=>{if(playing){pause();return;}if(time>=result.rows.at(-1).t)time=0;playing=true;$('play').textContent='Pause';last=0;
    function frame(stamp){if(!playing)return;if(last)time+=(stamp-last)/1000*Number($('speed').value);last=stamp;updatePlayback();if(time>=result.rows.at(-1).t){pause();return;}raf=requestAnimationFrame(frame);}raf=requestAnimationFrame(frame);
  };
  $('time').oninput=()=>{pause();time=Number($('time').value);updatePlayback();};$('forces').onchange=drawMechanism;$('model-view').onchange=drawMechanism;$('force-view').onchange=makePlots;$('probe').onchange=makePlots;
  function loadResult(data,{emit=false}={}){
    if(!data||!Array.isArray(data.rows)||!data.rows.length||!Array.isArray(data.frames)||!data.frames.length||!data.config)throw Error('This JSON does not contain a playable suspension run.');
    if(data.backend&&data.backend!==backend)throw Error('Open this run in its matching simulation tab. The Pymunk viewer requires a Pymunk result.');
    if(!data.rows.every(r=>Number.isFinite(r.t)))throw Error('Recorded time values must be finite.');
    cancelPreviewRequest();setupPreview=null;setupCache=null;inSetupMode=false;previewNotice.hidden=true;
    pause();result=data;config={...data.config};dirty=false;time=0;runRevision++;restoreReference(data);if(Number.isFinite(data.auxiliary_spring?.actual_rest_length_m))config.aux_rest_length=data.auxiliary_spring.actual_rest_length_m;if(Number.isFinite(data.spring_mechanism?.resolved_stiffness_N_m))config.stiffness=data.spring_mechanism.resolved_stiffness_N_m;if(!viewer)controls();
    playbackCache=preparePlayback(data);
    $('error').hidden=true;showPassiveStability(data.passive_stability);showIntegrationWarning();
    $('engine').textContent=(isMath?'':'Pymunk ')+data.engine;
    const mechanismHeading=document.querySelector('.mechanism-panel h2');if(mechanismHeading)mechanismHeading.textContent=data.config.aux_spring_enabled?'Optional variant · extra tip strut':data.config.spring_topology==='gravity_balance'&&data.config.chassis_shape_enabled?'Replacement suspension · upper link to chassis':'Mechanism & live loads';
    recordedHeading=mechanismHeading?.textContent||recordedHeading;previewMode(false);
    $('model-objects').textContent=JSON.stringify(data.model||{renderer:'Mathematical kinematics'},null,2);
    $('snapshot').textContent=`${data.config.fixture==='floating'?'Floating chassis':data.config.fixture==='hip'?'Hip fixed':'Wheel fixed'} · ${data.config.radius*1000} mm wheel radius · ${fmt(data.config.extension*1000,0)} mm extension`;
    $('status').textContent=`${data.config.target==='position'?'Prescribed position · ':''}Recorded ${data.rows.length.toLocaleString()} ${isMath?'output samples':'solver steps'} · dt ${data.config.dt*1000} ms · actual spring free length ${fmt(data.actual_rest_length*1000,1)} mm${data.spring_mechanism?.automatic_balance==='rate_calibration'?' · calibrated k '+fmt(config.stiffness,2)+' N/m':''}`;
    $('warnings').replaceChildren();
    for(const warning of data.warnings||[]){const node=document.createElement('div');node.className='warning';node.textContent=warning;$('warnings').append(node);}
    const reference=data.equation_reference||{};
    $('equation-formulas').textContent=(reference.visible_equations||[]).join('\n')+(reference.derived_identity?'\n\nDerived identity: '+reference.derived_identity:'');
    $('equation-errors').textContent='Maximum residuals across saved run:\n'+JSON.stringify(data.equation_check_errors||{},null,2);
    const reproduction=reference.torque_reproduction;
    $('reference-validation').textContent=reproduction?'Screenshot torque reproduction (separate from current run):\n'+reproduction.assumptions+'\n'+reproduction.samples.map(s=>`${s.theta_deg}°: reported ${s.reported_Nm} N·m; reproduced ${s.reproduced_Nm.toFixed(10)} N·m`).join('\n'):'';
    $('equation-scope').textContent=(reference.status||'')+' '+(reference.limitations||[]).join(' ');
    const equationHeading=$('equation-checks')?.querySelector('summary');if(equationHeading)equationHeading.textContent=isMath?'Mathematical equations & load balances':'Equation cross-check · reference screenshots';
    $('scope').textContent=data.scope||'';$('diagnostics').textContent=JSON.stringify({...(data.diagnostics||{}),...(data.solver?{solver:data.solver}:{}),...(data.auxiliary_spring?{auxiliary_spring:data.auxiliary_spring}:{})},null,2);
    const moving=data.config.fixture==='hip'?'hub':'chassis';
    $('peaks').textContent=`Peak J2 ${forceFmt(data.peaks?.j2_force?.value)} · peak vertical accel ${fmt(data.peaks?.[moving+'_ay']?.value,1)} m/s²`;
    $('probe').value=data.config.fixture==='hip'?'j3':'j1';$('time').max=data.rows.at(-1).t;
    for(const id of ['time','play','export','case','save-data'])if($(id))$(id).disabled=false;
    $('model-view').value=isMath?'annotated':$('model-view').value;
    makePlots();publish('motion-lab-config',{config:{...config},reference_inputs:referenceInputs()});if(emit)publish('motion-lab-run',{result:{...data,backend,reference_inputs:referenceInputs()}});
  }
  async function run(){
    cancelPreviewRequest();pause();$('run').disabled=true;$('error').hidden=true;$('status').textContent=isMath?'Running independent SciPy equations…':'Running Pymunk rigid-body solver…';
    try{const response=await fetch(isMath?'/api/math/simulate':'/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config)}),data=await response.json();if(!response.ok)throw Error(data.error||'Simulation failed.');loadResult(data,{emit:true});}
    catch(error){showError(error);$('status').textContent='Run failed; any previous plots retain their saved inputs.';}finally{$('run').disabled=false;}
  }
  function showIntegrationWarning(){
    const node=$('spring-integration-warning');if(!node)return;
    node.hidden=config.spring_integration!=='native_legacy';
    node.textContent='Advanced native_legacy spring diagnostic: the Pymunk DampedSpring/constraint split can bias ride response, especially at high damping. Refine dt and compare point_force and independent SciPy results. '+(isMath?'This tab integrates independent equations; the imported legacy setting remains in the profile.':'The imported legacy setting is preserved; selecting a new preset restores its point-force default.');
  }
  function showPassiveStability(stability){
    const card=$('passive-stability');if(!card)return;
    const labels={restoring:'Restoring',neutral:'Neutral',unstable:'Unstable',not_applicable:'N/A'},classification=Object.hasOwn(labels,stability?.classification)?stability.classification:'not_applicable';
    card.dataset.classification=classification;$('stability-classification').textContent=labels[classification];
    for(const [id,key] of [['stability-mean','net_ride_stiffness_N_m'],['stability-left','left_ride_stiffness_N_m'],['stability-right','right_ride_stiffness_N_m']])$(id).textContent=Number.isFinite(stability?.[key])?fmt(stability[key],2)+' N/m':'—';
    $('stability-balance').textContent=Number.isFinite(stability?.initial_force_balance_residual_N)?forceFmt(stability.initial_force_balance_residual_N):'—';
    $('stability-pose').textContent=Number.isFinite(stability?.theta_deg)?`At initial θ = ${fmt(stability.theta_deg,1)}°`:'Initial-pose test';
    $('stability-reason').textContent=stability?.reason||(stability?'':'Stability metadata is unavailable in this saved run. Run the simulation to calculate it.');
    $('stability-notes').replaceChildren();for(const text of stability?.notes||[]){const item=document.createElement('li');item.textContent=text;$('stability-notes').append(item);}
  }
  function showError(error){$('error').hidden=false;$('error').textContent=error.message||String(error);}
  function download(data,name,type='application/json'){
    const url=URL.createObjectURL(new Blob([type==='application/json'?JSON.stringify(data,null,2):data],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function saveProfile(){
    const profile={schema:'wheel-leg-lab-profile/v1',backend,config:{...config},reference_inputs:referenceInputs()};
    publish('motion-lab-profile',{config:{...config},reference_inputs:profile.reference_inputs});download(profile,backend+'-motion-profile.json');
  }
  function referenceInputs(){return {T0_N:referenceT0N,T0_kgf:referenceT0N===null?null:referenceT0N/KGF,applied_to_solver:false,guide_visualization:{pretension_N:guidePretensionN,pretension_kgf:guidePretensionN===null?null:guidePretensionN/KGF,show_force_vectors:guideForcesVisible,applied_to_solver:false,tension_convention:'Assumed lower span baseline; other span = baseline + abs(delta).'}};}
  function restoreReference(value){
    const n=value?.reference_inputs?.T0_N;
    if(n===null||(Number.isFinite(n)&&n>=0)){referenceT0N=n;showReferenceT0();}
    const guide=value?.reference_inputs?.guide_visualization;
    if(guide){
      if(guide.pretension_N!==null&&(!Number.isFinite(guide.pretension_N)||guide.pretension_N<0))throw Error('Guide visualization baseline must be finite, nonnegative or unspecified.');
      guidePretensionN=guide.pretension_N;
      if(typeof guide.show_force_vectors==='boolean')guideForcesVisible=guide.show_force_vectors;
      if($('guide-pretension-N'))$('guide-pretension-N').value=guidePretensionN??'';
      if($('guide-pretension-kgf'))$('guide-pretension-kgf').value=guidePretensionN===null?'':guidePretensionN/KGF;
      if($('guide-force-vectors'))$('guide-force-vectors').checked=guideForcesVisible;
    }
  }
  function applyProfile(value){
    const incoming=value?.config||value;if(!incoming||Array.isArray(incoming)||typeof incoming!=='object')throw Error('Profile must contain a configuration object.');
    if(!Object.keys(defaults).length){pendingProfile=value;return;}
    const next={...defaults};
    const choices={fixture:['floating','hip','wheel'],target:['position','force','knee'],wave:['step','square','pulse','impulse'],ramp_shape:['quintic','linear'],load_point:['hub','contact'],spring_topology:Object.keys(springCatalog),spring_mode:['compression','extension','captured'],spring_transmission:['direct','pullrod','ideal_rope'],spring_force_law:['hooke','zero_effective'],spring_integration:['point_force','native_legacy'],aux_mode:['captured','compression','extension']};
    for(const [key,value] of Object.entries(incoming)){
      if(!Object.hasOwn(defaults,key))throw Error('Unknown profile field: '+key);
      if(typeof value!==typeof defaults[key]||(typeof value==='number'&&!Number.isFinite(value)))throw Error('Invalid profile value for '+key);
      if(key==='spring_direction'&&![1,-1].includes(value))throw Error('Spring payout sign must be +1 or −1.');
      if(choices[key]&&!choices[key].includes(value))throw Error('Unsupported choice for '+key);next[key]=value;
    }
    if(isMath&&(next.fixture!=='floating'||next.target!=='position'||next.ramp_shape!=='quintic'||next.load_point!=='hub'||!['step','square','pulse'].includes(next.wave)))throw Error('The mathematical tab requires a floating chassis, smooth position input and hub loads. Open other profiles in 2D Physics.');
    if(next.aux_spring_enabled&&next.spring_topology!=='gravity_balance')throw Error('The separate ride spring & damper requires the gravity-balance primary preset.');
    pause();config=next;dirty=true;restoreReference(value);controls();requestSetupPreview();$('error').hidden=true;$('status').textContent='Profile loaded. Run simulation to generate a new result.';publish('motion-lab-config',{config:{...config},reference_inputs:referenceInputs()});
  }
  $('run').onclick=run;
  $('export').onclick=()=>{if(!result)return;const keys=Object.keys(result.rows[0]),csv=keys.join(',')+'\r\n'+result.rows.map(row=>keys.map(key=>row[key]).join(',')).join('\r\n');download(csv,backend+'-linkage-full-trace.csv','text/csv');};
  $('case').onclick=()=>{if(!result)return;download({engine:result.engine,config:result.config,actual_rest_length:result.actual_rest_length,diagnostics:result.diagnostics,equation_reference:result.equation_reference,equation_check_errors:result.equation_check_errors,reference_inputs:referenceInputs(),scope:result.scope},backend+'-linkage-run-config.json');};
  if($('profile'))$('profile').onclick=saveProfile;
  if($('save-data'))$('save-data').onclick=()=>{if(!result)return;const data={...result,backend,reference_inputs:referenceInputs()};publish('motion-lab-save-run',{result:data});download(data,backend+'-motion-run.json');};
  if($('gui'))$('gui').onclick=async()=>{
    if(parent!==window){publish('motion-lab-show-gui',{config:{...config},reference_inputs:referenceInputs(),result:result?{...result,backend,reference_inputs:referenceInputs()}:null});return;}
    $('gui').disabled=true;$('error').hidden=true;$('status').textContent='Opening native Pymunk live GUI on the host computer…';
    try{const payload=config.guide_pulleys_visible||guidePretensionN!==null?{model:'wheel_leg',config:{...config},guide_visualization:referenceInputs().guide_visualization}:config,response=await fetch('/api/native-gui',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}),data=await response.json();if(!response.ok)throw Error(data.error||'Native GUI could not start.');$('status').textContent=data.message||'Native Pymunk GUI opened on the host computer. Browser playback remains available here.';}
    catch(error){showError(error);$('status').textContent='Native GUI launch failed; browser playback remains available.';}
    finally{$('gui').disabled=false;}
  };
  if($('profile-import'))$('profile-import').onchange=async event=>{try{const file=event.target.files[0];if(!file)return;if(file.size>80*1024*1024)throw Error('JSON exceeds the 80 MiB import limit.');applyProfile(JSON.parse(await file.text()));}catch(error){showError(error);}event.target.value='';};
  addEventListener('message',event=>{
    if(event.origin!==location.origin||event.source!==parent)return;
    const message=event.data;if(!message||typeof message.type!=='string')return;
    try{
      if(message.type==='motion-lab-load-profile')applyProfile({config:message.config,reference_inputs:message.reference_inputs});
      else if((message.type==='motion-lab-run'&&!message.result)||message.type==='motion-lab-run-simulation')run();
      else if(message.type==='motion-lab-save-profile')saveProfile();
      else if(message.type==='motion-lab-deactivate')pause();
      else if(message.type==='motion-lab-load-result')loadResult(message.result);
      else if(message.type==='motion-lab-theme'){requestAnimationFrame(()=>{if(result)makePlots();});}
    }catch(error){showError(error);}
  });
  function showReferenceT0(source=null){
    if(source!=='N')$('T0-newtons').value=referenceT0N===null?'':String(Number(referenceT0N.toPrecision(12)));
    if(source!=='kgf')$('T0-kgf').value=referenceT0N===null?'':String(Number((referenceT0N/KGF).toPrecision(12)));
    $('T0-conversion').textContent=referenceT0N===null?'T₀ has not been specified.':`T₀ = ${fmt(referenceT0N,5)} N = ${fmt(referenceT0N/KGF,5)} kgf`;
  }
  for(const [id,unit] of [['T0-newtons','N'],['T0-kgf','kgf']])$(id).addEventListener('input',()=>{
    const node=$(id),value=node.valueAsNumber;
    if(node.value==='')referenceT0N=null;
    else if(!Number.isFinite(value)||value<0){$('T0-conversion').textContent='Enter a nonnegative belt tension.';return;}
    else{const converted=value*(unit==='kgf'?KGF:1);if(!Number.isFinite(converted)){$('T0-conversion').textContent='Belt tension is too large to convert.';return;}referenceT0N=converted;}
    showReferenceT0(unit);try{localStorage.setItem('pymunk-reference-T0-N',JSON.stringify(referenceT0N));}catch{}
  });
  showReferenceT0();
  let resizePending=0,lastWidth=0;
  new ResizeObserver(entries=>{
    const width=entries[0].contentRect.width;if(Math.abs(width-lastWidth)<1)return;lastWidth=width;
    cancelAnimationFrame(resizePending);resizePending=requestAnimationFrame(()=>{for(const chart of charts)if(chart.container._fullLayout)window.Plotly.Plots.resize(chart.container);drawMechanism();});
  }).observe($('plots'));
  let heightPending=0,lastHeight=0;
  new ResizeObserver(()=>{cancelAnimationFrame(heightPending);heightPending=requestAnimationFrame(()=>{const height=Math.ceil(document.body.scrollHeight);if(height!==lastHeight){lastHeight=height;publish('motion-lab-height',{height});}});}).observe(document.body);
  new MutationObserver(()=>{if(result)makePlots();}).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  Promise.all([fetch('/api/defaults').then(r=>{if(!r.ok)throw Error('Backend unavailable.');return r.json();}),fetch('/api/spring-presets').then(r=>r.ok?r.json():null),architecture?fetch('/api/suspension-architecture/defaults').then(r=>{if(!r.ok)throw Error('Suspension architecture defaults unavailable; restart the Motion Lab server.');return r.json();}):Promise.resolve(null),import('/guide-belt.js')]).then(([data,presets,architectureDefaults,guide])=>{
    guideModule=guide;
    if(presets){springCatalog=presets.catalog||{};mechanismDefaults=presets.defaults||{};}
    defaults={...data};config={...(architectureDefaults?.config||architectureDefaults||data)};
    if(isMath){config.fixture='floating';config.target='position';config.ramp_shape='quintic';config.load_point='hub';config.wave='step';}
    if(viewer){$('status').textContent='Waiting for a recorded Pymunk run from the main lab.';publish('motion-lab-viewer-ready');publish('motion-lab-ready');return;}
    controls();publish('motion-lab-config',{config:{...config},reference_inputs:referenceInputs()});
    if(pendingProfile){applyProfile(pendingProfile);pendingProfile=null;publish('motion-lab-ready');}
    else if(loadOnly){$('status').textContent='Choose or load a profile, then run the simulation.';requestSetupPreview();publish('motion-lab-ready');}
    else run().finally(()=>publish('motion-lab-ready'));
  }).catch(error=>{$('status').textContent='Could not connect to simulation backend: '+error.message;});
})();
