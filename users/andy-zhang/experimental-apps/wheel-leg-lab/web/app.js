/** Shared suspension bench: serve /physics/ or /mathematical/ with matching DOM.
 * Inputs: SI JSON profiles/results, same-origin shell messages, Plotly and D3.
 * Outputs: recorded playback, zoomable charts, full CSV/profile/run JSON downloads.
 * Limitations: client playback does not integrate physics; math uses annotated geometry.
 */
(() => {
  const $=id=>document.getElementById(id),D=window.d3;
  const backend=document.body.dataset.backend==='math'?'math':'pymunk',isMath=backend==='math',viewer=new URLSearchParams(location.search).get('viewer')==='1',loadOnly=new URLSearchParams(location.search).get('loadOnly')==='1';
  let config={},defaults={},result=null,charts=[],time=0,playing=false,raf=0,last=0,dirty=false,runRevision=0,lastChartTime=-Infinity,pendingProfile=null;
  const fmt=(v,n=2)=>Number.isFinite(Number(v))?Number(v).toFixed(n):'—',colors=['var(--blue)','var(--orange)','var(--accent)','var(--purple)','var(--red)','var(--muted)'];
  const cssColor=name=>getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const publish=(type,fields={})=>{if(parent!==window)parent.postMessage({type,backend,...fields},location.origin);};
  if(viewer)document.body.classList.add('engine-viewer');
  const KGF=9.80665,forceFmt=v=>`${fmt(v)} N / ${fmt(v/KGF)} kgf`,forceCell=v=>`${fmt(v)} / ${fmt(v/KGF)}`;
  let referenceT0N=null;
  try{const value=JSON.parse(localStorage.getItem('pymunk-reference-T0-N'));if(typeof value==='number'&&Number.isFinite(value)&&value>=0)referenceT0N=value;}catch{}
  const field=(key,label,unit='',scale=1,min=0,max=1e6,step='any')=>`<label class="field">${label}${unit?` <em>${unit}</em>`:''}<input data-key="${key}" data-scale="${scale}" type="number" min="${min}" max="${max}" step="${step}" value="${config[key]*scale}"></label>`;
  const select=(key,label,choices)=>`<label class="field full">${label}<select data-key="${key}">${choices.map(([v,l])=>`<option value="${v}" ${config[key]===v?'selected':''}>${l}</option>`).join('')}</select></label>`;
  function controls(){
    const position=config.target==='position';
    const waves=position?[['step','Position step'],['square','Position square wave'],['pulse','Position bump pulse']]:[['step','Diagnostic force/torque step'],['square','Diagnostic square wave'],['impulse','Diagnostic impulse area']];
    const fixtures=position?[['floating','Wheel height input · floating chassis'],['hip','Wheel height input · fixed hip'],['wheel','Chassis height input · fixed wheel']]:[['hip','Fixed hip · wheel force response'],['wheel','Fixed wheel · chassis force response']];
    const inputFields=position?field('position_amplitude','Step / pulse height','mm, up +',1000,-500,500):field('amplitude','Step / square amplitude',config.target==='force'?'N':'N·m',1,-10000,10000)+field('impulse','Impulse area',config.target==='force'?'N·s':'N·m·s',1,-1000,1000);
    $('controls').innerHTML=`<details open><summary>Geometry & masses</summary><div class="fields">${field('length','Each link','mm',1000,80,800)}${field('extension','r₂ past knee','mm',1000,5,150)}${field('radius','Wheel radius','mm',1000,50,400)}${field('theta','Initial θ','°',1,3,87)}${field('theta_min','Minimum θ','°',1,3,86)}${field('theta_max','Maximum θ','°',1,4,87)}${field('upper_mass','Upper link','kg',1,.01,20)}${field('lower_mass','Full lower link','kg',1,.01,20)}${field('wheel_mass','Wheel','kg',1,.01,30)}${field('chassis_mass','Chassis corner','kg',1,.01,100)}${select('fixture','Fixture',fixtures)}</div></details>
    <details open><summary>Physical spring & static loading</summary><div class="fields">${field('stiffness','Spring k','N/m',1,0,100000)}${field('damping','Damper c','N·s/m',1,0,2000)}${field('rest_length','Manual free length','mm',1000,5,1000)}${field('bias_force','Optional static vertical force','N, up +',1,-5000,5000)}${field('bias_force_x','Optional static horizontal force','N, right +',1,-5000,5000)}${position&&config.fixture==='hip'?field('preload_force','Fixed-hip preload design load','N',1,-5000,5000):''}<label class="check"><input data-key="balance_spring" type="checkbox" ${config.balance_spring?'checked':''}>Set spring preload at initial pose</label></div><p class="hint">Hip J1 → r₂ extension tip. In the floating chassis test, preload supports the moving chassis/link weight. Forces are measured responses to the imposed wheel motion.</p></details>
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
      if(key==='fixture'&&config.fixture==='wheel'){config.bias_force=0;config.load_point='hub';config.wheel_drive_locked=false;}
      dirty=true;$('status').textContent='Inputs changed. Run simulation to update the saved traces.';
      if(['fixture','target'].includes(key))controls();else updateControls();
      publish('motion-lab-config',{config:{...config}});
    }));updateControls();
  }
  function updateControls(){
    const position=config.target==='position',find=k=>$('controls').querySelector(`[data-key="${k}"]`);
    for(const key of ['period','duty'])find(key).disabled=config.wave!=='square';
    find('pulse_width').disabled=!['pulse','impulse'].includes(config.wave);
    find('fall').disabled=config.wave==='step';
    if(find('amplitude'))find('amplitude').disabled=config.wave==='impulse';
    if(find('impulse'))find('impulse').disabled=config.wave!=='impulse';
    find('rest_length').disabled=config.balance_spring;
    find('load_point').disabled=config.fixture==='wheel';find('wheel_drive_locked').disabled=config.fixture==='wheel';
    if(isMath){
      for(const key of ['fixture','target','load_point','ramp_shape','iterations'])find(key).disabled=true;
      find('iterations').closest('.field').hidden=true;
      const engineOption=$('model-view').querySelector('option[value="engine"]');if(engineOption)engineOption.disabled=true;
      $('model-view').value='annotated';
      const hints=$('controls').querySelectorAll('.hint');
      hints[1].textContent='The independent equations prescribe wheel height directly. Support reaction and chassis motion are outputs; travel-limit events end the run before impact.';
    }
    const width=config.wave==='square'?config.period*config.duty:config.pulse_width;
    const amplitude=position?config.position_amplitude*1000:config.wave==='impulse'?config.impulse/(width-(config.rise+config.fall)/2):config.amplitude;
    const units=position?'mm/s':config.target==='force'?'N/s':'N·m/s';
    $('slopes').textContent=position?`Mean rise speed ${fmt(amplitude/config.rise,1)} mm/s${config.ramp_shape==='quintic'?' · peak rise speed '+fmt(1.875*amplitude/config.rise,1)+' mm/s':''}. Positive height is upward.`:`Rise slope: ${config.rise?fmt(amplitude/config.rise,0)+' '+units:'instant edge'}; constant force bias is separate.`;
  }
  function nearest(rows,t){const i=D.bisector(r=>r.t).center(rows,t);return rows[Math.max(0,Math.min(rows.length-1,i))];}
  function decimate(rows,key){if(rows.length<=1800)return rows;const out=[],stride=Math.ceil(rows.length/700);for(let i=0;i<rows.length;i+=stride){const chunk=rows.slice(i,i+stride),lo=chunk.reduce((a,b)=>a[key]<b[key]?a:b),hi=chunk.reduce((a,b)=>a[key]>b[key]?a:b);out.push(chunk[0],lo,hi,chunk.at(-1));}return [...new Map(out.map(r=>[r.t,r])).values()].sort((a,b)=>a.t-b.t);}
  function makePlots(){
    if(!result)return;const previousCharts=charts;charts=[];const c=result.config,moving=c.fixture==='hip'?'hub':'chassis',view=$('force-view').value,probe=$('probe').value;
    const definitions=[
      [c.target==='position'?'Prescribed height · command vs achieved':'Diagnostic disturbance',c.target==='position'?'Displacement (mm)':c.target==='force'?'Input force (N)':'Input torque (N·m)',c.target==='position'?[['input_mm','Command'],['position_actual_mm','Achieved']]:[['input','Disturbance']]],
      [c.fixture==='floating'?'Chassis response':'Link angle',c.fixture==='floating'?'Chassis displacement (mm)':'θ from horizontal (°)',c.fixture==='floating'?[['chassis_displacement_mm','Chassis']]:[['theta_deg','Link angle']]],
      ['Joint reactions',view==='force'?(c.target==='position'?'Pin resultant / fixture Fy (N)':'Joint resultant (N)'):`Joint ${view.toUpperCase()} (N)`,[...[1,2,3].map(j=>['j'+j+'_'+view,'J'+j]),...(c.target==='position'&&view!=='fx'?[['driver_force','Fixture vertical']]:[])]],
      ['Torque channels','Torque (N·m)',[['actuator_torque','Knee actuator'],['spring_knee_moment','Spring about knee'],['guide_link_torque','Guide on lower link'],['stop_knee_torque','Knee travel stop'],['guide_hip_reaction','Grounded guide / J1'],['wheel_drive_reaction','Wheel drive → lower link']]],
      [probe.toUpperCase()+' pin velocity','Velocity (m/s)',[[probe+'_vx','Horizontal'],[probe+'_vy','Vertical']]],
      [probe.toUpperCase()+' pin acceleration','Acceleration (m/s²)',[[probe+'_ax','Horizontal'],[probe+'_ay','Vertical']]],
      ['Knee angular velocity','Opening velocity (rad/s)',[['knee_speed','Knee α̇']]],
      ['Knee angular acceleration','Opening acceleration (rad/s²)',[['knee_accel','Knee α̈']]],
    ];
    if(viewer){updatePlayback();return;}
    if(!window.Plotly)throw Error('Plotly could not load. Restart the app and reload this page.');
    for(const [title,label,requested] of definitions){
      const series=requested.filter(([key])=>result.rows.some(r=>Number.isFinite(r[key])));
      const index=charts.length;
      let chart=previousCharts[index];
      if(!chart){
        const panel=document.createElement('section');panel.className='plot';
        const heading=document.createElement('h3');heading.textContent=title;
        const container=document.createElement('div');container.className='chart';container.setAttribute('aria-label',title+' versus time');panel.append(heading,container);$('plots').append(panel);
        chart={panel,container,series,revision:-1};
      }else chart.panel.querySelector('h3').textContent=title;
      chart.series=series;
      const palette=colors.map(value=>cssColor(value.slice(4,-1)));
      const traces=series.map(([key,name],i)=>{
        const rows=decimate(result.rows,key);
        return {type:'scatter',mode:'lines',name,x:rows.map(r=>r.t),y:rows.map(r=>r[key]),line:{color:palette[i%palette.length],width:1.8},hovertemplate:label.endsWith('(N)')?'%{x:.3f} s<br>'+name+': %{y:.3f} N<br>%{customdata:.3f} kgf<extra></extra>':'%{x:.3f} s<br>'+name+': %{y:.4g}<extra></extra>',customdata:rows.map(r=>r[key]/KGF)};
      });
      const cursor={type:'line',xref:'x',yref:'paper',x0:time,x1:time,y0:0,y1:1,line:{color:cssColor('--muted'),width:1,dash:'dot'}};
      const revision=backend+'-'+runRevision+'-'+title+'-'+series.map(([key])=>key).join('|');
      const preserveZoom=chart.viewRevision===revision&&chart.container._fullLayout;
      const layout={height:300,margin:{l:75,r:18,t:16,b:78},paper_bgcolor:cssColor('--panel'),plot_bgcolor:cssColor('--panel'),font:{family:'system-ui,Segoe UI,sans-serif',color:cssColor('--text'),size:11},hovermode:'x unified',dragmode:'zoom',uirevision:revision,xaxis:{title:{text:'Time (s)'},gridcolor:cssColor('--line'),zerolinecolor:cssColor('--line'),range:preserveZoom?[...chart.container._fullLayout.xaxis.range]:[0,result.rows.at(-1).t],automargin:true},yaxis:{title:{text:label},gridcolor:cssColor('--line'),zerolinecolor:cssColor('--line'),...(preserveZoom&&!chart.container._fullLayout.yaxis.autorange?{range:[...chart.container._fullLayout.yaxis.range]}:{autorange:true}),automargin:true},legend:{orientation:'h',x:0,y:-.24,font:{size:10}},shapes:[cursor]};
      window.Plotly.react(chart.container,traces,layout,{responsive:true,scrollZoom:true,displaylogo:false,toImageButtonOptions:{format:'png',filename:backend+'-'+title.replaceAll(/[^a-z0-9]+/gi,'-')},modeBarButtonsToRemove:['lasso2d','select2d']}).then(()=>{
        if(!chart.clickBound){chart.container.on('plotly_click',event=>{const t=event.points?.[0]?.x;if(Number.isFinite(t)){pause();time=t;updatePlayback();}});chart.clickBound=true;}
      });
      chart.revision=runRevision;chart.viewRevision=revision;charts.push(chart);
    }
    lastChartTime=-Infinity;updatePlayback();
  }
  function drawMechanism(){
    if(!result)return;const svg=D.select($('mechanism')),W=$('mechanism').clientWidth,H=$('mechanism').clientHeight,c=result.config;
    const modelHeight=H-90;
    const frame=nearest(result.frames,time),points=result.frames.flatMap(f=>[f.hip,f.knee,f.hub,f.tip,[f.hub[0]-c.radius,f.hub[1]-c.radius],[f.hub[0]+c.radius,f.hub[1]+c.radius]]);
    const xe=D.extent(points,p=>p[0]),ye=D.extent(points,p=>p[1]),scale=Math.min((W-100)/(xe[1]-xe[0]),(modelHeight-65)/(ye[1]-ye[0]));
    const x=v=>W/2+(v-(xe[0]+xe[1])/2)*scale,y=v=>modelHeight/2-(v-(ye[0]+ye[1])/2)*scale;
    svg.attr('viewBox',`0 0 ${W} ${H}`);svg.selectAll('*').remove();svg.append('title').text((isMath?'Recorded mathematical-model geometry; ':'Actual recorded Pymunk poses; ')+'spring runs from hip to lower-link tip, '+fmt(c.extension*1000,0)+' mm past knee.');
    const A=frame.hip,B=frame.knee,C=frame.hub,E=frame.tip,row=nearest(result.rows,time);
    const point=p=>[x(p[0]),y(p[1])];
    const path=p=>D.line()(p.map(point));
    const engineView=$('model-view').value==='engine'&&frame.debug_draw;
    if(engineView){
      const factor=result.model?.debug_scale||600,position=p=>[x(p[0]/factor),y(p[1]/factor)],color=c=>`rgba(${c[0]},${c[1]},${c[2]},${c[3]/255})`;
      for(const p of frame.debug_draw){
        if(p.kind==='circle'){const q=position(p.pos),r=p.radius/factor*scale;svg.append('circle').attr('class','engine-shape').attr('cx',q[0]).attr('cy',q[1]).attr('r',r).attr('fill',color(p.fill)).attr('stroke',color(p.outline));svg.append('line').attr('x1',q[0]).attr('y1',q[1]).attr('x2',q[0]+r*Math.cos(p.angle)).attr('y2',q[1]-r*Math.sin(p.angle)).attr('stroke',color(p.outline));}
        else if(p.kind==='capsule'){const a=position(p.a),b=position(p.b);svg.append('line').attr('class','engine-shape').attr('x1',a[0]).attr('y1',a[1]).attr('x2',b[0]).attr('y2',b[1]).attr('stroke',color(p.outline)).attr('stroke-width',2*p.radius/factor*scale+2).attr('stroke-linecap','round');svg.append('line').attr('x1',a[0]).attr('y1',a[1]).attr('x2',b[0]).attr('y2',b[1]).attr('stroke',color(p.fill)).attr('stroke-width',2*p.radius/factor*scale).attr('stroke-linecap','round');}
        else if(p.kind==='segment'){const a=position(p.a),b=position(p.b);svg.append('line').attr('class','engine-constraint').attr('x1',a[0]).attr('y1',a[1]).attr('x2',b[0]).attr('y2',b[1]).attr('stroke',color(p.color)).attr('stroke-width',1.5);}
        else if(p.kind==='dot'){const q=position(p.pos);svg.append('circle').attr('class','engine-constraint').attr('cx',q[0]).attr('cy',q[1]).attr('r',p.size/2).attr('fill',color(p.color));}
        else if(p.kind==='polygon')svg.append('path').attr('class','engine-shape').attr('d',D.line()(p.vertices.map(position))+'Z').attr('fill',color(p.fill)).attr('stroke',color(p.outline));
      }
    }else{
    svg.append('path').attr('d',path([A,B])).attr('stroke','var(--blue)').attr('stroke-width',8).attr('stroke-linecap','round').attr('fill','none');
    svg.append('path').attr('d',path([E,C])).attr('stroke','var(--accent)').attr('stroke-width',8).attr('stroke-linecap','round').attr('fill','none');
    // Grounded pulley and knee pulley: physical radius ratio 2:1.
    svg.append('path').attr('d',path([A,B])).attr('stroke','var(--muted)').attr('stroke-width',1).attr('stroke-dasharray','4 3').attr('fill','none');
    for(const [p,r] of [[A,.028],[B,.014]])svg.append('circle').attr('cx',x(p[0])).attr('cy',y(p[1])).attr('r',r*scale).attr('fill','var(--panel)').attr('stroke','var(--muted)').attr('stroke-width',1.5);
    svg.append('circle').attr('cx',x(C[0])).attr('cy',y(C[1])).attr('r',c.radius*scale).attr('fill','none').attr('stroke','var(--text)').attr('stroke-width',2.5);
    svg.append('path').attr('d',`M${x(C[0])-c.radius*scale},${y(C[1])}h${2*c.radius*scale}M${x(C[0])},${y(C[1])-c.radius*scale}v${2*c.radius*scale}`).attr('stroke','var(--line)').attr('stroke-width',1);
    const a=point(A),b=point(E),dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy),normal=[-dy/length,dx/length];
    const coil=Array.from({length:23},(_,i)=>{const f=i/22,offset=(i<3||i>19)?0:(i%2?5:-5);return[a[0]+dx*f+normal[0]*offset,a[1]+dy*f+normal[1]*offset];});
    svg.append('path').attr('d',D.line()(coil)).attr('stroke','var(--orange)').attr('stroke-width',2).attr('fill','none');
    }
    const fixed=c.fixture==='hip'?A:C,fp=point(fixed);
    if(c.fixture!=='floating')svg.append('path').attr('d',`M${fp[0]-24},${fp[1]-10}h48`).attr('stroke','var(--text)').attr('stroke-width',3);
    for(const [p,name,offset] of [[A,'J1 · hip',[-14,-16]],[B,'J2 · knee',[13,-3]],[C,'J3 · wheel pin',[10,17]],[E,'Spring tip',[10,-12]]]){
      const pp=point(p);svg.append('circle').attr('cx',pp[0]).attr('cy',pp[1]).attr('r',4).attr('fill','var(--panel)').attr('stroke','var(--text)').attr('stroke-width',1.5);
      svg.append('text').attr('x',Math.min(W-105,Math.max(5,pp[0]+offset[0]))).attr('y',Math.min(H-8,Math.max(13,pp[1]+offset[1]))).text(name);
    }
    if($('forces').checked){
      const peak=Math.max(result.peaks.j1_force.value,result.peaks.j2_force.value,result.peaks.j3_force.value,1);
      for(const [p,j] of [[A,1],[B,2],[C,3]]){const pp=point(p),fx=row['j'+j+'_fx'],fy=row['j'+j+'_fy'],mag=Math.hypot(fx,fy);if(mag<1e-8)continue;const k=75/peak,tx=pp[0]+fx*k,ty=pp[1]-fy*k,angle=Math.atan2(ty-pp[1],tx-pp[0]);
        svg.append('path').attr('d',`M${pp[0]},${pp[1]}L${tx},${ty}M${tx-6*Math.cos(angle-.5)},${ty-6*Math.sin(angle-.5)}L${tx},${ty}L${tx-6*Math.cos(angle+.5)},${ty-6*Math.sin(angle+.5)}`).attr('stroke',colors[j-1]).attr('stroke-width',2).attr('fill','none');
      }
    }
    const inputPoint=point(c.target==='knee'?B:c.fixture==='wheel'?A:c.target==='position'?C:c.load_point==='contact'?[C[0],C[1]-c.radius]:C);
    const prescribed=c.target==='position'?{origin:point(result.position_origin||[0,0]),target:point(frame.position_target||C)}:null;
    drawDisturbance(svg,W,H,inputPoint,row,prescribed);
  }
  function drawDisturbance(svg,W,H,target,row,prescribed){
    const c=result.config,multiplier=c.target==='position'?1000:1,unit=c.target==='position'?'mm':c.target==='knee'?'N·m':'N',peak=Math.max(...result.rows.map(r=>Math.abs(r.input)*multiplier),.000001),value=row.input*multiplier;
    const base=H-38,pps=(W-32)/3,amp=18,x=t=>target[0]+(t-time)*pps,y=v=>base-v/peak*amp;
    const lane=svg.append('g').attr('class','disturbance-lane').attr('data-input',value);
    lane.append('text').attr('x',16).attr('y',H-80).text(`${c.target==='position'?'Moving height':'Moving input'} (${unit})`);
    lane.append('text').attr('class','disturbance-label').attr('x',W-16).attr('y',H-80).attr('text-anchor','end').text(`Δ ${value>=0?'+':''}${fmt(value,2)} ${unit}`);
    const clip='disturbance-clip';lane.append('defs').append('clipPath').attr('id',clip).append('rect').attr('x',16).attr('y',H-73).attr('width',W-32).attr('height',57);
    const marks=lane.append('g').attr('clip-path',`url(#${clip})`);
    marks.append('line').attr('x1',16).attr('x2',W-16).attr('y1',base).attr('y2',base).attr('stroke','var(--line)');
    marks.append('path').datum(decimate(result.rows,'input')).attr('class','disturbance-profile').attr('d',D.line().x(r=>x(r.t)).y(r=>y(r.input*multiplier))).attr('fill','none').attr('stroke','var(--blue)').attr('stroke-width',2.5);
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
  function updatePlayback(){
    if(!result)return;time=Math.max(0,Math.min(result.rows.at(-1).t,time));const row=nearest(result.rows,time),c=result.config;
    $('time').value=time;$('time-value').textContent=fmt(time,3)+' s';
    $('pose-values').innerHTML=`<span>θ ${fmt(row.theta_deg,1)}°</span><span>Height ${fmt(row.height*1000,0)} mm</span><span>Spring ${fmt(row.spring_length*1000,1)} mm</span>`;
    $('joint-values').innerHTML=[1,2,3].map(j=>`<tr><td>J${j}</td><td>${forceCell(row['j'+j+'_fx'])}</td><td>${forceCell(row['j'+j+'_fy'])}</td><td>${forceCell(row['j'+j+'_force'])}</td></tr>`).join('');
    $('equation-values').innerHTML=[['L₂(−Fz cosθ + Fy sinθ): hub lever','ref_Min_wheel_moment','check_lower_moment_Nm','N·m'],['L₂(−Fz cosθ + Fy sinθ) + Fy r_w: contact lever','ref_Min_contact_moment','check_contact_moment_Nm','N·m'],['L₁(Bz cosθ + By sinθ)','ref_Mact_knee_moment','check_upper_moment_Nm','N·m'],['√(By² + Bz²)','ref_Br','check_Br_N','N']].map(([label,key,error,unit])=>`<tr><td>${label}</td><td>${fmt(row[key],3)} ${unit}</td><td>${Number.isFinite(row[error])?row[error].toExponential(2):'—'} ${unit}</td></tr>`).join('');
    $('torque-values').innerHTML=[...(c.target==='position'?[['Motion fixture reaction','driver_force','N']]:[]),['Spring tension','spring_tension','N'],['Spring moment about knee','spring_knee_moment','N·m'],['Knee actuator','actuator_torque','N·m'],['Guide on lower link','guide_link_torque','N·m'],['Grounded guide at J1','guide_hip_reaction','N·m'],['Knee travel stop','stop_knee_torque','N·m'],['Wheel contact torque','wheel_external_moment','N·m'],['Wheel drive → lower link','wheel_drive_reaction','N·m'],['Wheel angular speed','wheel_speed','rad/s'],[c.fixture==='hip'?'Hub velocity':'Chassis velocity',(c.fixture==='hip'?'hub':'chassis')+'_vy','m/s'],[c.fixture==='hip'?'Hub acceleration':'Chassis acceleration',(c.fixture==='hip'?'hub':'chassis')+'_ay','m/s²']].map(([name,key,unit])=>`<dt>${name}</dt><dd>${unit==='N'?forceFmt(row[key]):fmt(row[key])+' '+unit}</dd>`).join('');
    // Throttle cursor relayout while the SVG/readouts remain at animation speed.
    if(!playing||Math.abs(time-lastChartTime)>=.1){
      lastChartTime=time;
      for(const chart of charts)if(chart.container._fullLayout)window.Plotly.relayout(chart.container,{'shapes[0].x0':row.t,'shapes[0].x1':row.t});
    }
    drawMechanism();
  }
  function pause(){playing=false;cancelAnimationFrame(raf);last=0;$('play').textContent='Play';}
  $('play').onclick=()=>{if(playing){pause();return;}if(time>=result.rows.at(-1).t)time=0;playing=true;$('play').textContent='Pause';last=0;
    function frame(stamp){if(!playing)return;if(last)time+=(stamp-last)/1000*Number($('speed').value);last=stamp;updatePlayback();if(time>=result.rows.at(-1).t){pause();return;}raf=requestAnimationFrame(frame);}raf=requestAnimationFrame(frame);
  };
  $('time').oninput=()=>{pause();time=Number($('time').value);updatePlayback();};$('forces').onchange=drawMechanism;$('model-view').onchange=drawMechanism;$('force-view').onchange=makePlots;$('probe').onchange=makePlots;
  function loadResult(data,{emit=false}={}){
    if(!data||!Array.isArray(data.rows)||!data.rows.length||!Array.isArray(data.frames)||!data.frames.length||!data.config)throw Error('This JSON does not contain a playable suspension run.');
    if(data.backend&&data.backend!==backend)throw Error('Open this run in its matching simulation tab. The Pymunk viewer requires a Pymunk result.');
    if(!data.rows.every(r=>Number.isFinite(r.t)))throw Error('Recorded time values must be finite.');
    pause();result=data;config={...data.config};dirty=false;time=0;runRevision++;if(!viewer)controls();
    $('error').hidden=true;
    $('engine').textContent=(isMath?'':'Pymunk ')+data.engine;
    $('model-objects').textContent=JSON.stringify(data.model||{renderer:'Mathematical kinematics'},null,2);
    $('snapshot').textContent=`${data.config.fixture==='floating'?'Floating chassis':data.config.fixture==='hip'?'Hip fixed':'Wheel fixed'} · ${data.config.radius*1000} mm wheel radius · ${fmt(data.config.extension*1000,0)} mm extension`;
    $('status').textContent=`${data.config.target==='position'?'Prescribed position · ':''}Recorded ${data.rows.length.toLocaleString()} ${isMath?'output samples':'solver steps'} · dt ${data.config.dt*1000} ms · actual spring free length ${fmt(data.actual_rest_length*1000,1)} mm`;
    $('warnings').replaceChildren();
    for(const warning of data.warnings||[]){const node=document.createElement('div');node.className='warning';node.textContent=warning;$('warnings').append(node);}
    const reference=data.equation_reference||{};
    $('equation-formulas').textContent=(reference.visible_equations||[]).join('\n')+(reference.derived_identity?'\n\nDerived identity: '+reference.derived_identity:'');
    $('equation-errors').textContent='Maximum residuals across saved run:\n'+JSON.stringify(data.equation_check_errors||{},null,2);
    const reproduction=reference.torque_reproduction;
    $('reference-validation').textContent=reproduction?'Screenshot torque reproduction (separate from current run):\n'+reproduction.assumptions+'\n'+reproduction.samples.map(s=>`${s.theta_deg}°: reported ${s.reported_Nm} N·m; reproduced ${s.reproduced_Nm.toFixed(10)} N·m`).join('\n'):'';
    $('equation-scope').textContent=(reference.status||'')+' '+(reference.limitations||[]).join(' ');
    const equationHeading=$('equation-checks')?.querySelector('summary');if(equationHeading)equationHeading.textContent=isMath?'Mathematical equations & load balances':'Equation cross-check · reference screenshots';
    $('scope').textContent=data.scope||'';$('diagnostics').textContent=JSON.stringify({...(data.diagnostics||{}),...(data.solver?{solver:data.solver}:{})},null,2);
    const moving=data.config.fixture==='hip'?'hub':'chassis';
    $('peaks').textContent=`Peak J2 ${forceFmt(data.peaks?.j2_force?.value)} · peak vertical accel ${fmt(data.peaks?.[moving+'_ay']?.value,1)} m/s²`;
    $('probe').value=data.config.fixture==='hip'?'j3':'j1';$('time').max=data.rows.at(-1).t;
    for(const id of ['time','play','export','case','save-data'])if($(id))$(id).disabled=false;
    $('model-view').value=isMath?'annotated':$('model-view').value;
    makePlots();publish('motion-lab-config',{config:{...config}});if(emit)publish('motion-lab-run',{result:{...data,backend}});
  }
  async function run(){
    pause();$('run').disabled=true;$('error').hidden=true;$('status').textContent=isMath?'Running independent SciPy equations…':'Running Pymunk rigid-body solver…';
    try{const response=await fetch(isMath?'/api/math/simulate':'/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config)}),data=await response.json();if(!response.ok)throw Error(data.error||'Simulation failed.');loadResult(data,{emit:true});}
    catch(error){showError(error);$('status').textContent='Run failed; any previous plots retain their saved inputs.';}finally{$('run').disabled=false;}
  }
  function showError(error){$('error').hidden=false;$('error').textContent=error.message||String(error);}
  function download(data,name,type='application/json'){
    const url=URL.createObjectURL(new Blob([type==='application/json'?JSON.stringify(data,null,2):data],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function saveProfile(){
    const profile={schema:'wheel-leg-lab-profile/v1',backend,config:{...config},reference_inputs:referenceInputs()};
    publish('motion-lab-profile',{config:{...config},reference_inputs:profile.reference_inputs});download(profile,backend+'-motion-profile.json');
  }
  function referenceInputs(){return {T0_N:referenceT0N,T0_kgf:referenceT0N===null?null:referenceT0N/KGF,applied_to_solver:false};}
  function restoreReference(value){
    const n=value?.reference_inputs?.T0_N;
    if(n===null||(Number.isFinite(n)&&n>=0)){referenceT0N=n;showReferenceT0();}
  }
  function applyProfile(value){
    const incoming=value?.config||value;if(!incoming||Array.isArray(incoming)||typeof incoming!=='object')throw Error('Profile must contain a configuration object.');
    if(!Object.keys(defaults).length){pendingProfile=value;return;}
    const next={...defaults};
    const choices={fixture:['floating','hip','wheel'],target:['position','force','knee'],wave:['step','square','pulse','impulse'],ramp_shape:['quintic','linear'],load_point:['hub','contact']};
    for(const [key,value] of Object.entries(incoming)){
      if(!Object.hasOwn(defaults,key))throw Error('Unknown profile field: '+key);
      if(typeof value!==typeof defaults[key]||(typeof value==='number'&&!Number.isFinite(value)))throw Error('Invalid profile value for '+key);
      if(choices[key]&&!choices[key].includes(value))throw Error('Unsupported choice for '+key);next[key]=value;
    }
    if(isMath&&(next.fixture!=='floating'||next.target!=='position'||next.ramp_shape!=='quintic'||next.load_point!=='hub'||!['step','square','pulse'].includes(next.wave)))throw Error('The mathematical tab requires a floating chassis, smooth position input and hub loads. Open other profiles in 2D Physics.');
    pause();config=next;dirty=true;controls();restoreReference(value);$('error').hidden=true;$('status').textContent='Profile loaded. Run simulation to generate a new result.';publish('motion-lab-config',{config:{...config}});
  }
  $('run').onclick=run;
  $('export').onclick=()=>{if(!result)return;const keys=Object.keys(result.rows[0]),csv=keys.join(',')+'\r\n'+result.rows.map(row=>keys.map(key=>row[key]).join(',')).join('\r\n');download(csv,backend+'-linkage-full-trace.csv','text/csv');};
  $('case').onclick=()=>{if(!result)return;download({engine:result.engine,config:result.config,actual_rest_length:result.actual_rest_length,diagnostics:result.diagnostics,equation_reference:result.equation_reference,equation_check_errors:result.equation_check_errors,reference_inputs:{T0_N:referenceT0N,T0_kgf:referenceT0N===null?null:referenceT0N/KGF,applied_to_solver:false},scope:result.scope},backend+'-linkage-run-config.json');};
  if($('profile'))$('profile').onclick=saveProfile;
  if($('save-data'))$('save-data').onclick=()=>{if(!result)return;const data={...result,backend,reference_inputs:referenceInputs()};publish('motion-lab-save-run',{result:data});download(data,backend+'-motion-run.json');};
  if($('gui'))$('gui').onclick=()=>{
    if(parent!==window){publish('motion-lab-show-gui',{config:{...config},result:result?{...result,backend}:null});return;}
    if(isMath){try{sessionStorage.setItem('motion-lab-gui-profile',JSON.stringify(config));}catch{}location.assign('/?gui=1');return;}
    if(!result){showError(Error('Run a simulation or load a recorded result before opening the Pymunk viewer.'));return;}
    document.body.classList.add('engine-viewer');$('model-view').value='engine';drawMechanism();
    if(!document.getElementById('back-to-controls')){const back=document.createElement('button');back.id='back-to-controls';back.textContent='Back to simulation controls';back.onclick=()=>{document.body.classList.remove('engine-viewer');back.remove();};document.querySelector('.mechanism-panel').prepend(back);}
  };
  if($('profile-import'))$('profile-import').onchange=async event=>{try{const file=event.target.files[0];if(!file)return;if(file.size>80*1024*1024)throw Error('JSON exceeds the 80 MiB import limit.');applyProfile(JSON.parse(await file.text()));}catch(error){showError(error);}event.target.value='';};
  addEventListener('message',event=>{
    if(event.origin!==location.origin||event.source!==parent)return;
    const message=event.data;if(!message||typeof message.type!=='string')return;
    try{
      if(message.type==='motion-lab-load-profile')applyProfile({config:message.config,reference_inputs:message.reference_inputs});
      else if(message.type==='motion-lab-save-profile')saveProfile();
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
  fetch('/api/defaults').then(r=>{if(!r.ok)throw Error('Backend unavailable.');return r.json();}).then(data=>{
    defaults={...data};config={...data};
    if(isMath){config.fixture='floating';config.target='position';config.ramp_shape='quintic';config.load_point='hub';config.wave='step';}
    if(viewer){$('status').textContent='Waiting for a recorded Pymunk run from the main lab.';publish('motion-lab-viewer-ready');publish('motion-lab-ready');return;}
    controls();publish('motion-lab-config',{config:{...config}});
    if(pendingProfile){applyProfile(pendingProfile);pendingProfile=null;publish('motion-lab-ready');}
    else if(loadOnly){$('status').textContent='Choose or load a profile, then run the simulation.';publish('motion-lab-ready');}
    else run().finally(()=>publish('motion-lab-ready'));
  }).catch(error=>{$('status').textContent='Could not connect to simulation backend: '+error.message;});
})();
