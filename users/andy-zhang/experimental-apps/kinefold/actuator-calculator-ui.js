/** Read-only-profile UI for the independent actuator calculator.
 * Load after actuator-calculator.js/catalog.js and app.js. Inputs are the current
 * Studio snapshot plus local catalog/assumption controls; outputs Plotly charts,
 * equation tables and explicit JSON exports in the app folder. No simulation,
 * physical profile, motorConfig or saved-library write is performed here.
 */
(function(root){
  'use strict';
  const A=root.KinefoldActuatorCalculator,esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt=(n,d=3)=>Number.isFinite(n)?n.toLocaleString('en-CA',{maximumFractionDigits:d}):'—';
  const hardwareFields=[
    ['motorPeakNm','Motor peak shaft torque','N·m',0],['motorNoLoadRpm','Illustrative motor no-load / speed cap','rpm',1],
    ['ratio','Selected gearbox reduction','motor / gearbox output speed',.000001],['hipBeltRatio','Gearbox output to hip belt reduction B','1 to 3',1],['efficiency','Torque transfer factor η','0–1',.000001],
    ['rotorInertiaKgM2','Estimated motor rotor inertia Jₘ','kg·m²',0],['gearboxInputInertiaKgM2','Gearbox input-equivalent inertia Jg,in','kg·m²',0],
    ['gearboxOutputInertiaKgM2','Additional output inertia · outside source gearbox','kg·m²',0],
    ['gearboxPeakNm','Gearbox momentary output torque cap','N·m',0],['gearboxInputMaxRpm','Gearbox maximum input speed','rpm',0],['gearboxOutputMaxRpm','Gearbox maximum output speed','rpm',0]
  ];
  function mount(host,studio=root.KinefoldStudio,catalog=root.KinefoldActuatorCatalog){
    if(!host||!studio||!A||!catalog)throw Error('Calculator requires a host, Studio, core and catalog.');
    let selection=null,comparisons=[],profile=studio.getSnapshot(),result=null,timer=0,closed=false,losses=null,controller=null;
    const fields=new Map();
    host.classList.add('actuator-workspace');
    host.innerHTML=`<div class="workspace-heading"><div><span class="eyebrow">INDEPENDENT ACTUATOR STUDY</span><h2>Motor, gearing &amp; joint acceleration</h2><p>Search hardware, compare reflected inertia, estimate a finite leg stroke and a conditional jump.</p></div><button type="button" data-action="export">Save calculator JSON</button></div>
      <div class="actuator-boundary">Info calculator · reads the mechanism profile · changes here stay separate from the Energy and Dynamic tabs.</div>
      <div data-actuator-profile class="actuator-profile"></div><div data-actuator-catalog></div>
      <section class="actuator-assumptions"><h3>Calculation assumptions · editable</h3><p>Motor speed cells in the source are unresolved. The example below is a demonstration assumption, not a manufacturer speed envelope.</p>
      <div class="actuator-controls"><label>Unsourced example speed cap <span>rpm</span><input data-example-rpm type="number" min="1" max="1000000" value="6000" step="100"></label>
      <label>Unsourced torque transfer factor η <span>dimensionless</span><input data-example-efficiency type="number" min="0.001" max="1" value="0.9" step="0.01"></label>
      <label>Fixed-hip gravity / suspension<select data-fixed-balance><option value="ideal-balance">Exact gravity balance · isolate inertia</option><option value="profile">All-body gravity + saved spring</option><option value="gravity-only">All-body gravity · spring off</option></select></label>
      <label>Jump gravity / suspension<select data-jump-balance><option value="profile">All-body gravity + saved spring</option><option value="gravity-only">All-body gravity · spring off</option><option value="ideal-balance">Ideal gravity balance · external assistance</option></select></label>
      <label>Illustrative torque-speed law<select data-torque-model><option value="linear">Peak → zero torque at example no-load speed</option><option value="constant">Constant peak up to speed cap · optimistic</option></select></label>
      <label>Target COM jump height <span>m above takeoff COM</span><input data-target-height type="number" min="0" max="100" value="2" step="0.1"></label></div>
      <label class="actuator-check"><input data-omit-inertia type="checkbox" checked> Provisional assumption: omit an unknown gearbox inertia (0 kg·m²). This is optimistic and is disclosed in results.</label>
      <p class="hint">The source input-equivalent gearbox inertia is reflected once. Additional output inertia defaults to zero because it is not another copy of the same gearbox train. η and the drag terms below are independent study assumptions; using a measured total efficiency plus measured drag could count losses twice.</p>
      <details class="actuator-hardware"><summary>Resolved hardware values &amp; overrides</summary><p>Blank ratings stay unassessed. Select another catalog SKU to change reduction; the ideal sweep below separately illustrates hypothetical ratios.</p><div class="actuator-controls" data-hardware-fields></div><div data-source-notes></div></details></section>
      <section class="actuator-losses"><div class="actuator-section-heading"><div><h3>Coulomb / cogging envelope &amp; viscous drag</h3><p>Output-side preliminary estimates. Constant opposing torque is a worst-case proxy for cogging; actual cogging is position-periodic.</p></div><button type="button" data-action="reset-losses">Reset preliminary estimates</button></div>
      <div data-loss-fields></div><p class="hint">Low / medium / high start at 1% / 3% / 8% of the selected usable joint peak for Coulomb torque, plus the same fractions of drag at 10 rad/s. These are adjustable sensitivity cases, not measured loss data. τloss = τC + b|q̇|.</p></section>
      <div data-actuator-error role="status"></div><div data-actuator-results></div>
      <details class="actuator-equations"><summary>Equations, definitions &amp; model boundaries</summary>
        <dl><dt>Coordinate and linkage</dt><dd>q = θ₂ in radians, increasing toward compression. Extension progresses s = q_c − q. Upper / lower link masses are profile m₂ / m₃ (r1 / r2 leg links), lengths L₂ / L₃. The saved mounting α rotates all positions and Jacobians; +x is screen-left and +z is up.</dd>
        <dt>Joint-side inertia</dt><dd>Jleg(q) = Σ[mᵢ‖∂rᵢ/∂q‖² + Iᵢ(∂θᵢ/∂q)²]. Uniform rod I = mL²/12. Compound pulley disc I = ½m₅ max(r_d,r_e)². A freely spinning wheel has no enforced spin-vs-fold rate; its translation still contributes.</dd>
        <dt>Motor and gearbox inertia</dt><dd>Total N = motor speed / hip q speed = selected gearbox ratio × extra hip belt B (1 to 3). B=2 means two gearbox-output turns per hip turn. This ideal extra stage is separate from the leg’s r_a/r_b belt constraint. Jtotal = Jleg + N²Jmotor + N²Jgear,input + Jadditional,output. Additional output inertia is at the hip; efficiency never scales inertia. Source input-equivalent gearbox inertia represents the train and is reflected once.</dd>
        <dt>Acceleration</dt><dd>J s̈ + ½(dJ/ds)ṡ² = τdrive − τC − bṡ − dU/ds. The finite-stroke integration uses E = ½Jṡ² and dE/ds = τdrive − τloss − dU/ds. A zero-speed scan and time-trajectory sampled peak are different quantities; peaks are finite samples. Acceleration-versus-speed also includes the ½J′ term, so it need not follow the assumed motor torque line.</dd>
        <dt>Hip versus relative knee</dt><dd>Hip speed is q̇. Lower-link absolute speed is (1−r_a/r_b)q̇; relative-knee speed is −(r_a/r_b)q̇. Accelerations have the same constant multipliers. At the V4 2:1 belt ratio, the lower absolute rate is −q̇ and the relative-knee rate is −2q̇.</dd>
        <dt>Illustrative motor envelope</dt><dd>τdrive = min[η N τmotor,peak max(0,1−N ṡ/ω₀), B τgear,peak]. The constant-torque option omits the linear factor. Both are demonstration curves, not fitted BLDC voltage/current/thermal models. The extra belt multiplies the source gearbox torque cap by B and divides its output-speed cap by B. Known gear input/output rpm caps stop the calculation before extrapolation. Unknown caps remain unassessed.</dd>
        <dt>Gravity compensation</dt><dd>Exact balance is an explicitly ideal external assistance that cancels the selected fixture’s gravity; compensation work is reported. Profile mode uses the saved spring’s exact potential and all body COM gravity. Changing masses or α does not retune the spring.</dd>
        <dt>Conditional jump</dt><dd>The wheel centre stays at r_w on a horizontal floor and may slide in x; chassis x and pitch stay fixed. Grounded-wheel inertia includes m₁(∂h/∂q)² and both links. From the endpoint velocity, vCOM,z = Σmᵢvᵢ,z / Σmᵢ and ΔhCOM = vCOM,z²/(2g). This is above the takeoff COM, not the initial chassis height. Rotor/internal/horizontal kinetic energy is not magically converted into vertical COM energy.</dd>
        <dt>Unassessed</dt><dd>No unilateral ground reaction, liftoff event, traction, wheel rolling impulse, stop collision, compliance, controller, battery, thermal duration or structural rating is solved. A completed stroke and a peak rating do not establish a safe jump. Jump screening requires a straight, monotonic nonsingular guide.</dd></dl></details>`;
    const $=s=>host.querySelector(s),fieldHost=$('[data-hardware-fields]');
    fieldHost.innerHTML=hardwareFields.map(([k,label,unit,min])=>`<label>${esc(label)} <span>${esc(unit)}</span><input data-hardware="${k}" type="number" min="${min}" ${k==='efficiency'?'max="1"':k==='hipBeltRatio'?'max="3"':''} step="any" aria-label="${esc(label)}"></label>`).join('');
    for(const node of host.querySelectorAll('[data-hardware]'))fields.set(node.dataset.hardware,node);
    fields.get('ratio').readOnly=true;fields.get('ratio').setAttribute('aria-readonly','true');
    function notes(){
      if(!selection)return [];
      const n=[];
      if(selection.motorNoLoadRpm===null)n.push('Motor no-load/speed: unsourced editable example '+$('[data-example-rpm]').value+' rpm.');
      if(selection.efficiency===null)n.push('Torque transfer factor: unsourced editable example '+$('[data-example-efficiency]').value+'.');
      n.push('Motor rotor inertia: source Rev2 geometry/model estimate; low and high values are scenario bounds, not measurement confidence intervals.');
      if(selection.gearboxInputInertiaKgM2===null)n.push($('[data-omit-inertia]').checked?'Unknown gearbox inertia explicitly omitted (optimistic 0).':'Gearbox inertia unresolved; enter an explicit estimate to calculate.');
      if(selection.gearPeakOutputNm===null)n.push('Gearbox momentary output torque is unresolved; capability remains unassessed.');
      if(Number(fields.get('ratio').value)!==selection.gearRatio)n.push('Reduction override is hypothetical; it does not identify a new catalog SKU.');
      n.push('Extra hip belt is ideal and lossless, with no added inertia. Total N = '+fields.get('ratio').value+' gearbox x '+fields.get('hipBeltRatio').value+' belt. Gearbox caps apply before this belt. Additional output inertia is entered at the hip.');
      n.push('Profile chassis mass stays fixed across candidates; catalog motor/gearbox masses are not added. Include their installed mass in the chassis budget.');
      n.push('Peak motor torque is a transient rating; no continuous duty/thermal assessment.');return n;
    }
    function refreshProfile(){const p=profile.params;const mass=p.m1+p.m2+p.m3+p.m5+p.m6;
      $('[data-actuator-profile]').innerHTML=`<div><span class="eyebrow">CURRENT PROFILE · READ ONLY</span><strong>${esc(profile.name)}</strong><small>α ${fmt(p.alpha,1)}° · hip θ₂ ${fmt(p.theta2,1)}° · ${fmt(p.L2,0)} / ${fmt(p.L3,0)} mm links</small></div><div class="actuator-masses"><span>Chassis <b>${fmt(p.m1,2)} kg</b></span><span>Upper link <b>${fmt(p.m2,2)} kg</b></span><span>Lower link <b>${fmt(p.m3,2)} kg</b></span><span>Wheel <b>${fmt(p.m6,2)} kg</b></span><span>Total corner <b>${fmt(mass,2)} kg</b></span></div>`;}
    function select(c){selection=c;losses=null;const h=A.fromCombination(c,{motorNoLoadRpm:c.motorNoLoadRpm??Number($('[data-example-rpm]').value),efficiency:c.efficiency??Number($('[data-example-efficiency]').value),gearboxInputInertiaKgM2:c.gearboxInputInertiaKgM2??($('[data-omit-inertia]').checked?0:null)});
      for(const [k,node]of fields)node.value=h[k]??'';
      $('[data-source-notes]').innerHTML='<ul>'+notes().map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>';schedule();}
    function readHardware(){
      if(!selection)throw Error('Choose a motor and SO gearbox from the catalog.');
      const h=A.fromCombination(selection,{torqueModel:$('[data-torque-model]').value});
      for(const [k,node]of fields){const optional=['gearboxPeakNm','gearboxInputMaxRpm','gearboxOutputMaxRpm'].includes(k);h[k]=node.value.trim()===''?(optional?null:NaN):Number(node.value);}
      h.name=selection.name;return A.hardware(h);
    }
    function renderLosses(){
      $('[data-loss-fields]').innerHTML='<div class="actuator-loss-grid">'+losses.map((l,i)=>`<fieldset><legend>${esc(l.name)}</legend><label>Constant opposing torque τC <span>N·m at output</span><input data-loss="${i}" data-key="coulombNm" type="number" min="0" step="any" value="${l.coulombNm}"></label><label>Viscous coefficient b <span>N·m·s/rad at output</span><input data-loss="${i}" data-key="viscousNms" type="number" min="0" step="any" value="${l.viscousNms}"></label></fieldset>`).join('')+'</div>';
    }
    function compareHardware(c){return {name:c.name,hardware:A.fromCombination(c,{motorNoLoadRpm:c.motorNoLoadRpm??Number($('[data-example-rpm]').value),efficiency:c.efficiency??Number($('[data-example-efficiency]').value),gearboxInputInertiaKgM2:c.gearboxInputInertiaKgM2??($('[data-omit-inertia]').checked?0:null),torqueModel:$('[data-torque-model]').value,hipBeltRatio:Number(fields.get('hipBeltRatio').value)})};}
    function render(){
      if(closed)return;refreshProfile();if(host.hidden||host.closest('[hidden]'))return;
      const error=$('[data-actuator-error]'),out=$('[data-actuator-results]');
      try{
        const h=readHardware();
        if(!losses){losses=A.defaultLosses(h);renderLosses();}
        result=A.calculate(profile,h,{losses,fixedBalance:$('[data-fixed-balance]').value,jumpBalance:$('[data-jump-balance]').value,targetJumpHeightM:Number($('[data-target-height]').value),candidates:comparisons.map(compareHardware),assumptions:notes(),steps:700});
        error.innerHTML='';root.KinefoldPlotly?.purge(out);
        const middle=result.cases[Math.min(1,result.cases.length-1)],z=result.current,formatState=r=>r.complete?fmt(r.strokeTimeS,4)+' s':r.status;
        const cards=[['Leg motion inertia',fmt(z.legKgM2,6)+' kg·m²','Fixed hip, saved pose'],['Reflected motor + gearbox',fmt(z.motorKgM2+z.gearboxKgM2,6)+' kg·m²',fmt(z.reflectedFraction*100,1)+'% of total at saved pose'],['Initial extension acceleration',fmt(middle.free.initialAccelerationRadS2,1)+' rad/s²','Medium loss · starts at compression stop'],['Conditional jump · medium',middle.jump?.estimatedJumpHeightM===null||!middle.jump?'Unresolved / no complete release':fmt(middle.jump.estimatedJumpHeightM,3)+' m','COM apex above takeoff · no liftoff test']];
        out.innerHTML=`<div class="actuator-readouts">${cards.map(([label,value,note])=>`<div><span>${esc(label)}</span><strong>${esc(value)}</strong><small>${esc(note)}</small></div>`).join('')}</div>
          <div class="actuator-notes"><b>Assumptions carried into these results</b><ul>${notes().map(n=>'<li>'+esc(n)+'</li>').join('')}</ul><p>${esc(result.warning)}</p></div>
          <div class="actuator-table-wrap"><table><caption>Three loss sensitivity cases · same profile and selected hardware</caption><thead><tr><th>Case</th><th>Initial accel rad/s²</th><th>Sampled peak rad/s²</th><th>Free-leg stroke</th><th>End speed rad/s</th><th>Jump stroke</th><th>COM launch m/s</th><th>COM jump m</th></tr></thead><tbody>${result.cases.map(c=>`<tr><th>${esc(c.loss.name)}</th><td>${fmt(c.free.initialAccelerationRadS2,2)}</td><td>${fmt(c.free.sampledPeakAccelerationRadS2,2)}</td><td>${esc(formatState(c.free))}</td><td>${fmt(c.free.end.speedRadS,3)}</td><td>${c.jump?esc(formatState(c.jump)):esc(c.jumpError)}</td><td>${fmt(c.jump?.takeoffComSpeedMS,3)}</td><td>${fmt(c.jump?.estimatedJumpHeightM,3)}</td></tr>`).join('')}</tbody></table></div>
          <p class="hint">Target ${fmt(result.options.targetJumpHeightM,2)} m is a visual comparison only. There is no claim that the selected motor meets it. A null height means stalled, speed-capped or unsupported; the intermediate jump-height curve is a hypothetical instantaneous-release speed screen.</p>
          ${result.compare.length?`<div class="actuator-table-wrap"><table><caption>Pinned exact catalog combinations · the same medium output-side drag coefficients in every row</caption><thead><tr><th>Motor + gearbox</th><th>Ratio</th><th>Peak joint N·m</th><th>Total J kg·m²</th><th>Initial accel rad/s²</th><th>Free stroke s</th><th>End speed rad/s</th><th>Conditional COM jump m</th></tr></thead><tbody>${result.compare.map(c=>c.error?'<tr><th>'+esc(c.name)+'</th><td colspan="7">'+esc(c.error)+'</td></tr>':`<tr><th>${esc(c.name)}</th><td>${fmt(c.ratio,2)}</td><td>${fmt(c.peakJointNm,2)}</td><td>${fmt(c.totalInertiaKgM2,6)}</td><td>${fmt(c.initialAccelerationRadS2,2)}</td><td>${c.strokeTimeS===null?esc(c.status):fmt(c.strokeTimeS,4)}</td><td>${fmt(c.terminalSpeedRadS,3)}</td><td>${fmt(c.jumpHeightM,3)}</td></tr>`).join('')}</tbody></table></div>`:''}
          <div data-actuator-charts class="actuator-chart-grid"></div>
          <details class="actuator-detail-table"><summary>Full numerical quantities and energy ledger</summary><div class="actuator-table-wrap"><table><thead><tr><th>Quantity</th><th>Value</th><th>Definition / units</th></tr></thead><tbody>
          ${[['Upper rod contribution',z.parts.upper,'kg·m²'],['Lower rod contribution',z.parts.lower,'kg·m²'],['Wheel translation contribution',z.parts.wheel,'kg·m²'],['Compound pulley contribution',z.parts.compound,'kg·m²'],['Motor reflected inertia',z.motorKgM2,'kg·m² = N²Jmotor'],['Gearbox reflected inertia',z.gearboxKgM2,'kg·m² = N²Jgear,in + Jadditional,out'],['Total fixed-hip inertia',z.totalKgM2,'kg·m² at saved pose'],['Reflected / leg inertia ratio',z.reflectedToLegRatio,'dimensionless'],['Joint peak after known cap',h.jointPeakNm,'N·m; unknown gearbox cap is unassessed'],['Joint speed bound',h.jointSpeedCapRadS,'rad/s from example motor + known gearbox caps'],['Ideal uncapped zero-speed optimum N',result.idealRatioSweep.optimumRatio,'sqrt((Jleg+Jextra,out)/(Jmotor+Jgear,in)); hypothetical'],['Medium free-leg motor work',middle.free.end.motorWorkJ,'J'],['Medium free-leg drag work',middle.free.end.lossWorkJ,'J'],['Medium free-leg balancing work',middle.free.end.compensationWorkJ,'J external ideal assistance'],['Medium free-leg max ledger residual',middle.free.maxAbsLedgerResidualJ,'J numerical quadrature'],['Medium jump total kinetic',middle.jump?.end.kineticJ,'J; includes reflected rotor'],['Medium jump vertical COM kinetic',middle.jump?.ballisticComEnergyJ,'J allocated to vertical COM flight'],['Medium jump excluded kinetic',middle.jump?.excludedInternalOrHorizontalKineticJ,'J; rotor/internal/horizontal'],['Medium jump gravity increase',middle.jump?.end.gravityDeltaJ,'J all body masses'],['Medium jump spring change',middle.jump?.end.springDeltaJ,'J; positive stores, negative releases'],['Medium jump compensation work',middle.jump?.end.compensationWorkJ,'J external ideal assistance if chosen'],['Medium jump max ledger residual',middle.jump?.maxAbsLedgerResidualJ,'J numerical quadrature']].map(([n,v,u])=>'<tr><th>'+esc(n)+'</th><td>'+fmt(v,8)+'</td><td>'+esc(u)+'</td></tr>').join('')}
          </tbody></table></div></details>`;
        const chartHost=$('[data-actuator-charts]');
        for(const spec of A.plotSpecs(result)){
          const card=document.createElement('section');card.className='actuator-chart';card.innerHTML='<h3>'+esc(spec.title)+'</h3><div></div>';
          if(spec.id==='actuator-ideal-ratio')card.insertAdjacentHTML('beforeend','<p class="hint">'+esc(result.idealRatioSweep.meaning)+'</p>');
          chartHost.append(card);const chart=card.querySelector('div');
          const layout={xaxis:{title:{text:spec.xLabel}},yaxis:{title:{text:spec.yLabel}},height:365};
          root.KinefoldPlotly?.react(chart,spec.traces,layout,{key:spec.id}).catch(e=>{error.textContent='Plot could not be drawn: '+e.message;});
        }
      }catch(e){result=null;root.KinefoldPlotly?.purge(out);out.innerHTML='';error.innerHTML='<p class="notice error">'+esc(e.message)+'</p>';}
    }
    function schedule(){clearTimeout(timer);timer=setTimeout(render,260);}
    function onInput(e){const node=e.target;if(node.matches('[data-loss]')){const i=Number(node.dataset.loss);losses[i][node.dataset.key]=node.value===''?NaN:Number(node.value);schedule();return;}
      if(node.matches('[data-example-rpm]')&&selection?.motorNoLoadRpm===null)fields.get('motorNoLoadRpm').value=node.value;
      if(node.matches('[data-example-efficiency]')&&selection?.efficiency===null)fields.get('efficiency').value=node.value;
      if(node.matches('[data-omit-inertia]')&&selection?.gearboxInputInertiaKgM2===null)fields.get('gearboxInputInertiaKgM2').value=node.checked?'0':'';
      if(node.closest('.actuator-assumptions'))schedule();
    }
    host.addEventListener('input',onInput);host.addEventListener('change',onInput);
    async function onClick(e){const action=e.target.closest('[data-action]')?.dataset.action;
      if(action==='reset-losses'){try{losses=A.defaultLosses(readHardware());renderLosses();schedule();}catch(error){$('[data-actuator-error]').textContent=error.message;}}
      if(action==='export'){try{render();if(!result)throw Error('Resolve the calculator inputs before exporting.');await studio.saveArtifact('kinefold-actuator-calculator-'+new Date().toISOString().replace(/[:.]/g,'-')+'.json',{...result,selection,comparisons,plotSpecs:A.plotSpecs(result)});}catch(error){$('[data-actuator-error]').textContent='Export unavailable: '+error.message;}}
    }
    host.addEventListener('click',onClick);
    controller=catalog.mount($('[data-actuator-catalog]'),{onSelect:select,onCompare:list=>{comparisons=list;schedule();},onExport:async f=>studio.saveArtifact(f.filename,f.text,f.mimeType)});
    controller.ready?.catch(e=>{$('[data-actuator-error]').textContent='Catalog unavailable: '+e.message;});
    const unsubscribe=studio.subscribe(value=>{profile=value;refreshProfile();schedule();});
    const onTab=e=>{if(e.detail?.id==='actuator')schedule();};root.addEventListener?.('kinefold-solver-tab',onTab);refreshProfile();
    return {ready:controller.ready,getResult:()=>result,getSelection:()=>selection,getState:()=>({selection,comparisons,hardware:selection?readHardware():null,losses:losses?cloneLosses(losses):null}),recompute:render,destroy(){closed=true;clearTimeout(timer);unsubscribe?.();controller.destroy?.();root.removeEventListener?.('kinefold-solver-tab',onTab);host.removeEventListener('input',onInput);host.removeEventListener('change',onInput);host.removeEventListener('click',onClick);root.KinefoldPlotly?.purge(host);}};
  }
  const cloneLosses=v=>JSON.parse(JSON.stringify(v));
  root.KinefoldActuatorCalculatorUI={mount};
  if(typeof document!=='undefined'){const host=document.getElementById('actuator-quick')||document.getElementById('actuator');if(host&&root.KinefoldStudio&&root.KinefoldActuatorCatalog)root.KinefoldQuickActuator=mount(host);}
})(globalThis);
