(() => {
  const $=id=>document.getElementById(id),D=window.d3;
  let config={},result=null,charts=[],time=0,playing=false,raf=0,last=0,dirty=false;
  const fmt=(v,n=2)=>Number(v).toFixed(n),colors=['var(--blue)','var(--orange)','var(--accent)','var(--purple)','var(--red)','var(--muted)'];
  const KGF=9.80665,forceFmt=v=>`${fmt(v)} N / ${fmt(v/KGF)} kgf`,forceCell=v=>`${fmt(v)} / ${fmt(v/KGF)}`;
  let referenceT0N=null;
  try{const value=JSON.parse(localStorage.getItem('pymunk-reference-T0-N'));if(typeof value==='number'&&Number.isFinite(value)&&value>=0)referenceT0N=value;}catch{}
  const field=(key,label,unit='',scale=1,min=0,max=1e6,step='any')=>`<label class="field">${label}${unit?` <em>${unit}</em>`:''}<input data-key="${key}" data-scale="${scale}" type="number" min="${min}" max="${max}" step="${step}" value="${config[key]*scale}"></label>`;
  const select=(key,label,choices)=>`<label class="field full">${label}<select data-key="${key}">${choices.map(([v,l])=>`<option value="${v}" ${config[key]===v?'selected':''}>${l}</option>`).join('')}</select></label>`;
  function controls(){
    $('controls').innerHTML=`<details open><summary>Geometry & masses</summary><div class="fields">${field('length','Each link','mm',1000,80,800)}${field('extension','r₂ past knee','mm',1000,5,150)}${field('radius','Wheel radius','mm',1000,50,400)}${field('theta','Initial θ','°',1,3,87)}${field('theta_min','Minimum θ','°',1,3,86)}${field('theta_max','Maximum θ','°',1,4,87)}${field('upper_mass','Upper link','kg',1,.01,20)}${field('lower_mass','Full lower link','kg',1,.01,20)}${field('wheel_mass','Wheel','kg',1,.01,30)}${field('chassis_mass','Chassis corner','kg',1,.01,100)}${select('fixture','Fixture',[['hip','Fixed hip · wheel response'],['wheel','Fixed wheel · chassis response']])}</div></details>
    <details open><summary>Physical spring & damper</summary><div class="fields">${field('stiffness','Spring k','N/m',1,0,100000)}${field('damping','Damper c','N·s/m',1,0,2000)}${field('rest_length','Manual free length','mm',1000,5,1000)}${field('bias_force','Vertical load bias','N, up +',1,-5000,5000)}${field('bias_force_x','Horizontal load bias','N, right +',1,-5000,5000)}<label class="check"><input data-key="balance_spring" type="checkbox" ${config.balance_spring?'checked':''}>Balance spring at initial pose</label></div><p class="hint">Hip J1 → tip of r₂ extension. Bilateral linear spring + damper; initial balance sets free length, not a controller.</p></details>
    <details open><summary>Disturbance input</summary><div class="fields">${select('target','Apply input',[['force','Vertical force at moving endpoint'],['knee','Opening torque at knee']])}${select('load_point','Wheel force point',[['hub','Wheel hub · no radius moment'],['contact','Tire bottom · includes Fx × radius']])}<label class="check"><input data-key="wheel_drive_locked" type="checkbox" ${config.wheel_drive_locked?'checked':''}>Lock wheel drive to lower link</label>${select('wave','Waveform',[['square','Square wave with linear edges'],['impulse','Impulse area · finite pulse']])}${field('amplitude','Square amplitude',config.target==='force'?'N':'N·m',1,-10000,10000)}${field('impulse','Impulse area',config.target==='force'?'N·s':'N·m·s',1,-1000,1000)}${field('start','Start time','s',1,0,20)}${field('period','Square period','s',1,.02,10)}${field('duty','On-time','%',100,1,99)}${field('pulse_width','Impulse width','ms',1000,1,5000)}${field('rise','Rise time','ms',1000,0,5000)}${field('fall','Fall time','ms',1000,0,5000)}</div><p class="hint">Tire-bottom horizontal force spins a free wheel. A locked drive transmits its reaction into the leg and adds wheel rotational inertia. No tire/ground collision is simulated.</p><p class="hint" id="slopes"></p></details>
    <details><summary>Optional knee impedance</summary><div class="fields">${field('knee_kp','Kp','N·m/rad',1,0,2000)}${field('knee_kd','Kd','N·m·s/rad',1,0,200)}${field('torque_limit','Torque limit','N·m',1,.01,2000)}</div><p class="hint">Acts across the actual knee opening angle α = 2θ. Reference is the initial pose; physical spring remains separate.</p></details>
    <details><summary>Solver</summary><div class="fields">${field('duration','Duration','s',1,.1,20)}${field('dt','Solver step','ms',1000,.25,4)}${field('iterations','Iterations','',1,20,300,1)}${field('gravity','Gravity','m/s²',1,0,20)}</div></details>`;
    $('controls').querySelectorAll('[data-key]').forEach(node=>node.addEventListener('change',()=>{
      const key=node.dataset.key;
      config[key]=node.type==='checkbox'?node.checked:node.tagName==='SELECT'?node.value:Number(node.value)/Number(node.dataset.scale||1);
      if(key==='fixture'){config.bias_force=config.fixture==='hip'?80:0;if(config.fixture==='wheel'){config.load_point='hub';config.wheel_drive_locked=false;}}
      dirty=true;$('status').textContent='Inputs changed. Run simulation to update the saved traces.';
      if(['fixture','target'].includes(key))controls();else updateControls();
    }));updateControls();
  }
  function updateControls(){
    for(const key of ['amplitude','period','duty'])$('controls').querySelector(`[data-key="${key}"]`).disabled=config.wave!=='square';
    for(const key of ['impulse','pulse_width'])$('controls').querySelector(`[data-key="${key}"]`).disabled=config.wave!=='impulse';
    $('controls').querySelector('[data-key="rest_length"]').disabled=config.balance_spring;
    $('controls').querySelector('[data-key="load_point"]').disabled=config.fixture==='wheel';
    $('controls').querySelector('[data-key="wheel_drive_locked"]').disabled=config.fixture==='wheel';
    const width=config.wave==='square'?config.period*config.duty:config.pulse_width;
    const area=width-(config.rise+config.fall)/2;
    const amplitude=config.wave==='square'?config.amplitude:config.impulse/area;
    const units=config.target==='force'?'N/s':'N·m/s';
    $('slopes').textContent=`Rise slope: ${config.rise?fmt(amplitude/config.rise,0)+' '+units:'instant edge'} · fall slope: ${config.fall?fmt(-amplitude/config.fall,0)+' '+units:'instant edge'}. Positive vertical input is upward.`;
  }
  function nearest(rows,t){const i=D.bisector(r=>r.t).center(rows,t);return rows[Math.max(0,Math.min(rows.length-1,i))];}
  function decimate(rows,key){if(rows.length<=1800)return rows;const out=[],stride=Math.ceil(rows.length/700);for(let i=0;i<rows.length;i+=stride){const chunk=rows.slice(i,i+stride),lo=chunk.reduce((a,b)=>a[key]<b[key]?a:b),hi=chunk.reduce((a,b)=>a[key]>b[key]?a:b);out.push(chunk[0],lo,hi,chunk.at(-1));}return [...new Map(out.map(r=>[r.t,r])).values()].sort((a,b)=>a.t-b.t);}
  function makePlots(){
    if(!result)return;charts=[];$('plots').innerHTML='';const c=result.config,moving=c.fixture==='hip'?'hub':'chassis',view=$('force-view').value,probe=$('probe').value;
    const definitions=[
      ['Disturbance input',c.target==='force'?'Input force (N)':'Input torque (N·m)',[['input','Disturbance']]],
      ['Link angle & travel','θ from horizontal (°)',[['theta_deg','Link angle']]],
      ['Joint reactions',view==='force'?'Joint resultant (N)':`Joint ${view.toUpperCase()} (N)`,[1,2,3].map(j=>['j'+j+'_'+view,'J'+j])],
      ['Torque channels','Torque (N·m)',[['actuator_torque','Knee actuator'],['spring_knee_moment','Spring about knee'],['guide_link_torque','Guide on lower link'],['stop_knee_torque','Knee travel stop'],['guide_hip_reaction','Grounded guide / J1'],['wheel_drive_reaction','Wheel drive → lower link']]],
      [probe.toUpperCase()+' pin velocity','Velocity (m/s)',[[probe+'_vx','Horizontal'],[probe+'_vy','Vertical']]],
      [probe.toUpperCase()+' pin acceleration','Acceleration (m/s²)',[[probe+'_ax','Horizontal'],[probe+'_ay','Vertical']]],
      ['Knee angular velocity','Opening velocity (rad/s)',[['knee_speed','Knee α̇']]],
      ['Knee angular acceleration','Opening acceleration (rad/s²)',[['knee_accel','Knee α̈']]],
    ];
    for(const [title,label,series] of definitions){
      const panel=document.createElement('section');panel.className='plot';panel.innerHTML=`<h3>${title}</h3><div class="chart"></div><div class="legend">${series.map(([key,name],i)=>`<span><i class="swatch" style="--series:${colors[i]}"></i>${name}</span>`).join('')}</div>`;$('plots').append(panel);
      const container=panel.querySelector('.chart'),W=container.clientWidth,H=245,left=72,right=15,top=12,bottom=44;
      const svg=D.select(container).append('svg').attr('viewBox',`0 0 ${W} ${H}`).attr('height',H).attr('role','img').attr('aria-label',title+' versus time');
      svg.append('title').text(title+'; solver-step measurements over time');
      const values=series.flatMap(([key])=>result.rows.map(r=>r[key])),extent=D.extent(values),pad=Math.max((extent[1]-extent[0])*.06,Math.max(Math.abs(extent[0]),Math.abs(extent[1]))*.03,.001);
      const x=D.scaleLinear().domain([0,result.rows.at(-1).t]).range([left,W-right]);
      const y=D.scaleLinear().domain([extent[0]-pad,extent[1]+pad]).nice().range([H-bottom,top]);
      svg.append('g').attr('transform',`translate(0,${H-bottom})`).call(D.axisBottom(x).ticks(W<400?4:6));
      svg.append('g').attr('transform',`translate(${left},0)`).call(D.axisLeft(y).ticks(5).tickFormat(D.format('.3~g')));
      svg.append('text').attr('x',(left+W-right)/2).attr('y',H-8).attr('text-anchor','middle').text('Time (s)');
      svg.append('text').attr('transform',`translate(14,${(top+H-bottom)/2}) rotate(-90)`).attr('text-anchor','middle').text(label);
      const id='clip-'+charts.length;svg.append('defs').append('clipPath').attr('id',id).append('rect').attr('x',left).attr('y',top).attr('width',W-left-right).attr('height',H-top-bottom);
      const marks=svg.append('g').attr('clip-path',`url(#${id})`);
      series.forEach(([key],i)=>marks.append('path').datum(decimate(result.rows,key)).attr('fill','none').attr('stroke',colors[i]).attr('stroke-width',1.7).attr('d',D.line().x(r=>x(r.t)).y(r=>y(r[key]))));
      const cursor=marks.append('line').attr('stroke','var(--muted)').attr('stroke-width',1).attr('y1',top).attr('y2',H-bottom),dots=marks.append('g');
      svg.append('rect').attr('x',left).attr('y',top).attr('width',W-left-right).attr('height',H-top-bottom).attr('fill','transparent').on('pointermove',event=>{
        const t=x.invert(D.pointer(event,svg.node())[0]),row=nearest(result.rows,t);$('tooltip').hidden=false;$('tooltip').textContent=fmt(row.t,3)+' s\n'+series.map(([key,name])=>name+': '+(label.endsWith('(N)')?forceFmt(row[key]):fmt(row[key],3))).join('\n');$('tooltip').style.left=Math.max(5,Math.min(innerWidth-300,event.clientX+12))+'px';$('tooltip').style.top=Math.max(5,Math.min(innerHeight-140,event.clientY+12))+'px';
      }).on('pointerleave',()=>{$('tooltip').hidden=true;}).on('click',event=>{pause();time=x.invert(D.pointer(event,svg.node())[0]);updatePlayback();});
      charts.push({series,x,y,cursor,dots});
    }updatePlayback();
  }
  function drawMechanism(){
    if(!result)return;const svg=D.select($('mechanism')),W=$('mechanism').clientWidth,H=$('mechanism').clientHeight,c=result.config;
    const modelHeight=H-90;
    const frame=nearest(result.frames,time),points=result.frames.flatMap(f=>[f.hip,f.knee,f.hub,f.tip,[f.hub[0]-c.radius,f.hub[1]-c.radius],[f.hub[0]+c.radius,f.hub[1]+c.radius]]);
    const xe=D.extent(points,p=>p[0]),ye=D.extent(points,p=>p[1]),scale=Math.min((W-100)/(xe[1]-xe[0]),(modelHeight-65)/(ye[1]-ye[0]));
    const x=v=>W/2+(v-(xe[0]+xe[1])/2)*scale,y=v=>modelHeight/2-(v-(ye[0]+ye[1])/2)*scale;
    svg.attr('viewBox',`0 0 ${W} ${H}`);svg.selectAll('*').remove();svg.append('title').text('Actual recorded Pymunk poses; spring runs from hip to lower-link tip, '+fmt(c.extension*1000,0)+' mm past knee.');
    const A=frame.hip,B=frame.knee,C=frame.hub,E=frame.tip,row=nearest(result.rows,time);
    const point=p=>[x(p[0]),y(p[1])];
    const path=p=>D.line()(p.map(point));
    const engineView=$('model-view').value==='engine'&&frame.debug_draw;
    if(engineView){
      const factor=result.model.debug_scale,position=p=>[x(p[0]/factor),y(p[1]/factor)],color=c=>`rgba(${c[0]},${c[1]},${c[2]},${c[3]/255})`;
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
    svg.append('path').attr('d',`M${fp[0]-24},${fp[1]-10}h48`).attr('stroke','var(--text)').attr('stroke-width',3);
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
    drawDisturbance(svg,W,H,point(c.target==='knee'?B:c.fixture==='wheel'?A:c.load_point==='contact'?[C[0],C[1]-c.radius]:C),row);
  }
  function drawDisturbance(svg,W,H,target,row){
    const c=result.config,unit=c.target==='knee'?'N·m':'N',peak=Math.max(...result.rows.map(r=>Math.abs(r.input)),.000001),value=row.input;
    const base=H-38,pps=(W-32)/3,amp=18,x=t=>target[0]+(t-time)*pps,y=v=>base-v/peak*amp;
    const lane=svg.append('g').attr('class','disturbance-lane').attr('data-input',value);
    lane.append('text').attr('x',16).attr('y',H-80).text(`Moving input (${unit})`);
    lane.append('text').attr('class','disturbance-label').attr('x',W-16).attr('y',H-80).attr('text-anchor','end').text(`Δ ${value>=0?'+':''}${fmt(value,2)} ${unit}`);
    const clip='disturbance-clip';lane.append('defs').append('clipPath').attr('id',clip).append('rect').attr('x',16).attr('y',H-73).attr('width',W-32).attr('height',57);
    const marks=lane.append('g').attr('clip-path',`url(#${clip})`);
    marks.append('line').attr('x1',16).attr('x2',W-16).attr('y1',base).attr('y2',base).attr('stroke','var(--line)');
    marks.append('path').datum(decimate(result.rows,'input')).attr('class','disturbance-profile').attr('d',D.line().x(r=>x(r.t)).y(r=>y(r.input))).attr('fill','none').attr('stroke','var(--blue)').attr('stroke-width',2.5);
    marks.append('line').attr('x1',target[0]).attr('x2',target[0]).attr('y1',H-73).attr('y2',H-16).attr('stroke','var(--orange)').attr('stroke-width',1);
    marks.append('circle').attr('class','disturbance-marker').attr('cx',target[0]).attr('cy',y(value)).attr('r',4).attr('fill','var(--orange)');
    lane.append('text').attr('x',16).attr('y',H-2).text(W<420?'← Applied input · bias separate':'Force / torque profile travels right → left; bias is separate.');
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
    $('equation-values').innerHTML=[['L₂(−Fz cosθ + Fy sinθ): hub lever','ref_Min_wheel_moment','check_lower_moment_Nm','N·m'],['L₂(−Fz cosθ + Fy sinθ) + Fy r_w: contact lever','ref_Min_contact_moment','check_contact_moment_Nm','N·m'],['L₁(Bz cosθ + By sinθ)','ref_Mact_knee_moment','check_upper_moment_Nm','N·m'],['√(By² + Bz²)','ref_Br','check_Br_N','N']].map(([label,key,error,unit])=>`<tr><td>${label}</td><td>${fmt(row[key],3)} ${unit}</td><td>${row[error].toExponential(2)} ${unit}</td></tr>`).join('');
    $('torque-values').innerHTML=[['Spring tension','spring_tension','N'],['Spring moment about knee','spring_knee_moment','N·m'],['Knee actuator','actuator_torque','N·m'],['Guide on lower link','guide_link_torque','N·m'],['Grounded guide at J1','guide_hip_reaction','N·m'],['Knee travel stop','stop_knee_torque','N·m'],['Wheel contact torque','wheel_external_moment','N·m'],['Wheel drive → lower link','wheel_drive_reaction','N·m'],['Wheel angular speed','wheel_speed','rad/s'],[c.fixture==='hip'?'Hub velocity':'Chassis velocity',(c.fixture==='hip'?'hub':'chassis')+'_vy','m/s'],[c.fixture==='hip'?'Hub acceleration':'Chassis acceleration',(c.fixture==='hip'?'hub':'chassis')+'_ay','m/s²']].map(([name,key,unit])=>`<dt>${name}</dt><dd>${unit==='N'?forceFmt(row[key]):fmt(row[key])+' '+unit}</dd>`).join('');
    for(const chart of charts){chart.cursor.attr('x1',chart.x(row.t)).attr('x2',chart.x(row.t));chart.dots.selectAll('*').remove();chart.series.forEach(([key],i)=>chart.dots.append('circle').attr('cx',chart.x(row.t)).attr('cy',chart.y(row[key])).attr('r',3.5).attr('fill',colors[i]));}
    drawMechanism();
  }
  function pause(){playing=false;cancelAnimationFrame(raf);last=0;$('play').textContent='Play';}
  $('play').onclick=()=>{if(playing){pause();return;}if(time>=result.rows.at(-1).t)time=0;playing=true;$('play').textContent='Pause';last=0;
    function frame(stamp){if(!playing)return;if(last)time+=(stamp-last)/1000*Number($('speed').value);last=stamp;updatePlayback();if(time>=result.rows.at(-1).t){pause();return;}raf=requestAnimationFrame(frame);}raf=requestAnimationFrame(frame);
  };
  $('time').oninput=()=>{pause();time=Number($('time').value);updatePlayback();};$('forces').onchange=drawMechanism;$('model-view').onchange=drawMechanism;$('force-view').onchange=makePlots;$('probe').onchange=makePlots;
  async function run(){
    pause();$('run').disabled=true;$('error').hidden=true;$('status').textContent='Running Pymunk rigid-body solver…';
    try{const response=await fetch('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config)}),data=await response.json();if(!response.ok)throw Error(data.error||'Simulation failed.');result=data;dirty=false;time=0;
      $('engine').textContent='Pymunk '+data.engine;$('model-objects').textContent=JSON.stringify(data.model,null,2);$('snapshot').textContent=`${data.config.fixture==='hip'?'Hip fixed':'Wheel fixed'} · ${data.config.radius*1000} mm wheel radius · ${fmt(data.config.extension*1000,0)} mm extension`;
      $('status').textContent=`Recorded ${data.rows.length.toLocaleString()} solver steps · dt ${data.config.dt*1000} ms · actual spring free length ${fmt(data.actual_rest_length*1000,1)} mm`;
      $('warnings').innerHTML=data.warnings.map(w=>`<div class="warning">${w}</div>`).join('');
      $('equation-formulas').textContent=data.equation_reference.visible_equations.join('\n')+'\n\nDerived identity: '+data.equation_reference.derived_identity;
      $('equation-errors').textContent='Maximum residuals across saved run:\n'+JSON.stringify(data.equation_check_errors,null,2);
      $('reference-validation').textContent='Screenshot torque reproduction (separate from current run):\n'+data.equation_reference.torque_reproduction.assumptions+'\n'+data.equation_reference.torque_reproduction.samples.map(s=>`${s.theta_deg}°: reported ${s.reported_Nm} N·m; reproduced ${s.reproduced_Nm.toFixed(10)} N·m`).join('\n');
      $('equation-scope').textContent=data.equation_reference.status+' '+data.equation_reference.limitations.join(' ');
      $('scope').textContent=data.scope;$('diagnostics').innerHTML='<pre>'+JSON.stringify(data.diagnostics,null,2)+'</pre>';
      const moving=data.config.fixture==='hip'?'hub':'chassis';$('peaks').textContent=`Peak J2 ${forceFmt(data.peaks.j2_force.value)} · peak vertical accel ${fmt(data.peaks[moving+'_ay'].value,1)} m/s²`;
      $('probe').value=data.config.fixture==='hip'?'j3':'j1';$('time').max=data.rows.at(-1).t;$('time').disabled=false;$('play').disabled=false;$('export').disabled=false;$('case').disabled=false;makePlots();
    }catch(error){$('error').hidden=false;$('error').textContent=error.message;$('status').textContent='Run failed; any previous plots retain their saved inputs.';}finally{$('run').disabled=false;}
  }
  $('run').onclick=run;$('export').onclick=()=>{if(!result)return;const keys=Object.keys(result.rows[0]),csv=keys.join(',')+'\r\n'+result.rows.map(row=>keys.map(key=>row[key]).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv'})),a=document.createElement('a');a.href=url;a.download='pymunk-linkage-full-trace.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  $('case').onclick=()=>{if(!result)return;const data={engine:result.engine,config:result.config,actual_rest_length:result.actual_rest_length,diagnostics:result.diagnostics,equation_reference:result.equation_reference,equation_check_errors:result.equation_check_errors,reference_inputs:{T0_N:referenceT0N,T0_kgf:referenceT0N===null?null:referenceT0N/KGF,applied_to_solver:false},scope:result.scope},url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='pymunk-linkage-run-config.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
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
  let resizePending=0;new ResizeObserver(()=>{cancelAnimationFrame(resizePending);resizePending=requestAnimationFrame(()=>{if(result)makePlots();});}).observe($('plots'));
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  fetch('/api/defaults').then(r=>r.json()).then(data=>{config=data;controls();run();}).catch(error=>{$('status').textContent='Could not connect to Pymunk backend: '+error.message;});
})();
