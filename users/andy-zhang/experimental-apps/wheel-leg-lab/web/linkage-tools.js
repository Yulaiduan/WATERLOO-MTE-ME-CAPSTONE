/** Jonathan features merged into the existing suspension bench controls/output.
 * Import from app.js; inputs are existing SI profiles and original run/frame state.
 * Outputs: ratio controls, exact three-belt overlay, fixed-A reference FBDs/sweeps/maxima.
 * Uses source-built JonReference math verbatim; does not copy Jonathan's editor.
 * Limits: fixed-A reference loads are labelled separately from actual dynamic solver loads.
 */
const groups=[['lengths','length','lower_length','L₂ / L₃'],['guide','guide_hip_radius','guide_knee_radius','a / b guide'],['cd','drive_hip_radius','drive_knee_radius','c / d drive'],['ef','drive_output_radius','wheel_pulley_radius','e / f drive']];
export function angleTrace(rows,key,xKey='x'){let last=null;const x=[],y=[];for(const r of rows){const v=r[key];if(key.startsWith('gamma')&&last!==null&&v!==null&&Math.abs(v-last)>180){x.push(null);y.push(null);}x.push(r[xKey]);y.push(v);last=v;}return {x,y};}
const referenceDefaults={drive_hip_radius:.035,drive_knee_radius:.035,drive_output_radius:.035,wheel_pulley_radius:.035,compound_mass:0,compound_inertia_radius:.035,belt_preload_ab:0,belt_preload_cd:0,belt_preload_ef:0,contact_beta:0,contact_beta_min:0,contact_beta_max:90,contact_force_mode:'yz',contact_normal_force:0,contact_tangent_force:0};
const f=n=>Number.isFinite(n)?n.toFixed(3):'—';
export {fromJon} from './jon-profile.js';
export function applyPreset(c,name){if(!['straight','spin','cancel'].includes(name))throw Error('Unknown linkage preset.');Object.assign(c,{lower_length:c.length,guide_knee_radius:c.guide_hip_radius/2,mount_angle:0,link_phase:0,drive_hip_radius:.035,drive_knee_radius:.035,drive_output_radius:.035,wheel_pulley_radius:.035});if(name==='spin')Object.assign(c,{drive_hip_radius:.05,drive_knee_radius:.025});if(name==='cancel')Object.assign(c,{drive_hip_radius:.045,drive_knee_radius:.03,drive_output_radius:.04,wheel_pulley_radius:.02});}
export function controls(c,field,select){
 const general=c.linkage_design==='general';
 return `<details open class="linkage-controls"><summary>Linkage design & transmission</summary><div class="fields">${select('linkage_design','Geometry',['original','general'].map(x=>[x,x==='original'?'Original equal-link 2:1':'Editable links · three carrier belts']))}</div><p class="hint">Same spring, motion input and SciPy/Pymunk workflow. θ₂ = 180° − θ. The editable design supports unequal links, mounting/phase and independent guide/drive ratios.</p>${general?`<div><button data-linkage-preset="straight">Straight 2:1</button><button data-linkage-preset="spin">Wheel spin</button><button data-linkage-preset="cancel">Cancel spin</button></div>`+groups.map(([id,a,b,label])=>`<div class="linkage-triplet" data-triplet="${id}"><strong>${label}</strong><button type="button" data-dimension-swap="${id}" aria-label="Swap ${id} dimensions">↔ Swap</button><div class="fields"><label>Ratio<input data-ratio="${id}" type="number" min="0.001" step="any" value="${c[a]/c[b]}" ${c['linkage_driven_'+id]==='ratio'?'disabled':''}></label>${field(a,id==='lengths'?'L₂':{guide:'r_a',cd:'r_c',ef:'r_e'}[id],'mm',1000,id==='lengths'?80:.001,800)}${field(b,id==='lengths'?'L₃':{guide:'r_b',cd:'r_d',ef:'r_f'}[id],'mm',1000,id==='lengths'?80:.001,800)}</div><div class="linkage-driven">Driven ${['ratio','first','second'].map((value,i)=>`<label><input data-driven="${id}" value="${value}" type="checkbox" ${c['linkage_driven_'+id]===value?'checked':''}>${['Ratio',a,b][i]}</label>`).join('')}</div></div>`).join('')+`<div class="fields">${field('mount_angle','α clockwise mounting','°',1,0,45)}${field('link_phase','φ₀ lower-link phase','°',1,0,30)}${field('compound_mass','m₅ compound at knee','kg',1,0,20)}${field('compound_inertia_radius','Compound rim inertia radius','mm',1000,1,250)}${field('belt_preload_ab','a/b slack-side preload','N',1,0,5000)}${field('belt_preload_cd','c/d slack-side preload','N',1,0,5000)}${field('belt_preload_ef','e/f slack-side preload','N',1,0,5000)}${field('contact_beta','β contact angle','°',1,0,90)}${select('contact_force_mode','Driving force components',[['yz','Global Fy / Fz'],['nt','Wheel normal / tangent']])}${field('contact_normal_force','Fn signed normal','N',1,-5000,5000)}${field('contact_tangent_force','Ft signed tangent','N',1,-5000,5000)}${field('contact_beta_min','β sweep / peak minimum','°',1,0,90)}${field('contact_beta_max','β sweep / peak maximum','°',1,0,90)}</div><p class="hint">Dynamic bodies require positive link/wheel/chassis masses; m₅ may be zero. Wheel and compound inertias use thin-rim formulas in this design. All radii use pitch circles. Preloads determine the reference span loads; the ideal dynamic angular constraints do not apply extra belt bearing forces.</p>`:''}</details>`;
}
export function bind(root,c,onChange){
 root.querySelectorAll('[data-linkage-preset]').forEach(button=>button.onclick=()=>{applyPreset(c,button.dataset.linkagePreset);onChange();});
 for(const key of ['bias_force','bias_force_x','contact_normal_force','contact_tangent_force']){const n=root.querySelector(`[data-key="${key}"]`);if(n&&c.linkage_design==='general')n.disabled=key.startsWith('contact_')?c.contact_force_mode==='yz':c.contact_force_mode==='nt';}
 for(const [id,a,b] of groups){
  const driven=c['linkage_driven_'+id];
  const swap=root.querySelector(`[data-dimension-swap="${id}"]`);if(swap)swap.onclick=()=>{[c[a],c[b]]=[c[b],c[a]];onChange();};
  for(const key of [a,b]){const node=root.querySelector(`[data-triplet="${id}"] [data-key="${key}"]`);if(node)node.disabled=(driven==='first'&&key===a)||(driven==='second'&&key===b);}
  root.querySelectorAll(`[data-driven="${id}"]`).forEach(n=>n.onchange=()=>{c['linkage_driven_'+id]=n.value;onChange();});
  const ratio=root.querySelector(`[data-ratio="${id}"]`);if(ratio)ratio.onchange=()=>{const q=Number(ratio.value);if(!Number.isFinite(q)||q<=0){ratio.setCustomValidity('Ratio must be positive.');ratio.reportValidity();return;}ratio.setCustomValidity('');if(driven==='first')c[a]=q*c[b];else if(driven==='second')c[b]=c[a]/q;onChange();};
 }
}
export function resolveEdit(c,key,old){
 for(const [id,a,b] of groups){if(![a,b].includes(key))continue;const d=c['linkage_driven_'+id],q=old[a]/old[b];if(d==='first'&&key===b)c[a]=q*c[b];if(d==='second'&&key===a)c[b]=c[a]/q;}
 const beta=c.contact_beta*Math.PI/180,s=Math.sin(beta),co=Math.cos(beta);
 if(key==='contact_force_mode'){
  if(c.contact_force_mode==='nt'){c.contact_normal_force=old.bias_force_x*s+old.bias_force*co;c.contact_tangent_force=old.bias_force_x*co-old.bias_force*s;}
  else{c.bias_force_x=old.contact_normal_force*s+old.contact_tangent_force*co;c.bias_force=old.contact_normal_force*co-old.contact_tangent_force*s;}
 }
 if(c.contact_force_mode==='nt'){c.bias_force_x=c.contact_normal_force*s+c.contact_tangent_force*co;c.bias_force=c.contact_normal_force*co-c.contact_tangent_force*s;}
 else{c.contact_normal_force=c.bias_force_x*s+c.bias_force*co;c.contact_tangent_force=c.bias_force_x*co-c.bias_force*s;}
}
export function reference(c){
 c={...referenceDefaults,...c};
 const {VSLStatic}=window.JonReference,g=c.linkage_design==='general';
 return VSLStatic.resolveLoads({...VSLStatic.defaults,L2:c.length*1000,L3:(g?c.lower_length:c.length)*1000,ra:c.guide_hip_radius*1000,rb:(g?c.guide_knee_radius:c.guide_hip_radius/2)*1000,
  rc:c.drive_hip_radius*1000,rd:c.drive_knee_radius*1000,re:c.drive_output_radius*1000,rf:c.wheel_pulley_radius*1000,rw:c.radius*1000,
  alpha:g?c.mount_angle:0,phi0:g?c.link_phase:0,te:180-c.theta_max,tc:180-c.theta_min,
  m1:c.chassis_mass,m2:c.upper_mass,m3:c.lower_mass,m5:g?c.compound_mass:0,m6:c.wheel_mass,g:c.gravity,r5I:c.compound_inertia_radius*1000,
  beta:c.contact_beta,loadMode:c.contact_force_mode,Fy:c.bias_force_x,Fz:c.bias_force,Fn:c.contact_normal_force,Ft:c.contact_tangent_force,
  Tab0:c.belt_preload_ab,Tcd0:c.belt_preload_cd,Tef0:c.belt_preload_ef});
}
export function draw(svg,frame,point,scale,c){
 if(c.linkage_design!=='general'||!window.JonReference)return;
 const {VSL}=window.JonReference,group=svg.append('g').attr('class','merged-carrier-belts');
 for(const [name,A,B,R,r,color] of [['a/b',frame.hip,frame.knee,c.guide_hip_radius,c.guide_knee_radius,'var(--accent)'],['c/d',frame.hip,frame.knee,c.drive_hip_radius,c.drive_knee_radius,'var(--purple)'],['e/f',frame.knee,frame.hub,c.drive_output_radius,c.wheel_pulley_radius,'var(--red)']]){
  const dx=B[0]-A[0],dy=B[1]-A[1],D=Math.hypot(dx,dy),belt=VSL.belt(D,R,r);if(!belt)continue;const cs=dx/D,sn=dy/D;
  const pts=Array.from({length:120},(_,i)=>{const v=belt.at(belt.total*i/119);return point([A[0]+cs*v[0]-sn*v[1],A[1]+sn*v[0]+cs*v[1]]);});
  group.append('path').attr('data-belt',name).attr('d',window.d3.line()(pts)+'Z').attr('fill','none').attr('stroke',color).attr('stroke-width',1.5).attr('stroke-dasharray',name==='a/b'?null:'4 2');
  for(const [center,radius] of [[A,R],[B,r]]){const p=point(center);group.append('circle').attr('cx',p[0]).attr('cy',p[1]).attr('r',radius*scale).attr('fill','none').attr('stroke',color);}
 }
 const p=point(frame.hip);group.append('text').attr('x',p[0]+45).attr('y',p[1]+8).text('a/c · chassis');
 const b=point(frame.knee);group.append('text').attr('x',b[0]+12).attr('y',b[1]+35).text('b · tibia / d/e · independent');
 if(Number.isFinite(frame.wheel_angle)){const center=point(frame.hub),end=point([frame.hub[0]+c.radius*Math.cos(frame.wheel_angle),frame.hub[1]+c.radius*Math.sin(frame.wheel_angle)]);group.append('line').attr('class','merged-wheel-angle').attr('x1',center[0]).attr('y1',center[1]).attr('x2',end[0]).attr('y2',end[1]).attr('stroke','var(--red)').attr('stroke-width',2);}
}
export function mount(main,publish){
 const node=document.createElement('details');node.className='merged-linkage-audit';node.open=true;node.innerHTML='<summary>Linkage math & force audit · validated against Jonathan</summary><p class="hint">Fixed-A quasi-static reference using Jon’s exact equations. The original dynamic fixture has a moving chassis, a spring and acceleration; holding torques here are reference values, not measured dynamic actuator loads. C = wheel centre; P = contact. Reference m₃ is at the knee/hub midpoint; the solver retains its full lower-link extension/COM.</p><div class="audit-cards"></div><div class="audit-state"></div><details><summary>Five reference free-body diagrams</summary><div class="audit-fbds"></div></details><details><summary>Geometry, torques, belt tensions and pin-load sweeps</summary><div class="audit-plots"></div></details><button class="audit-export">Export reference sweeps CSV</button><button class="audit-save">Save reference audit to library</button>';
 main.querySelector('.mechanism-panel').after(node);let latest=null,key='',peaks=null,plotKey='';
 function dataset(c,t){const {VSLStatic}=window.JonReference,p=reference(c),rows=[];
  for(const axis of ['theta2','dz','beta','alpha'])for(let i=0;i<=180;i++){
   const theta=axis==='theta2'?90+i*.5:axis==='dz'?p.te+(p.tc-p.te)*i/180:t;
   const pp=axis==='beta'?{...p,beta:i*.5}:axis==='alpha'?{...p,alpha:i*.25}:p,s=VSLStatic.solve(pp,theta,false);if(!s.valid)continue;
   const item={mode:axis,x:axis==='dz'?s.dz:axis==='theta2'?theta:axis==='beta'?pp.beta:pp.alpha,x_unit:axis==='dz'?'mm':'deg',theta2_deg:theta,alpha_deg:pp.alpha,beta_deg:pp.beta,Fn_N:s.Fn,Ft_N:s.Ft,Fy_N:s.Fy,Fz_N:s.Fz,
    theta3_deg:s.t3,theta5_deg:s.t5,theta6_deg:s.t6,du_mm:s.du,dv_mm:s.dv,dy_mm:s.dy,dz_mm:s.dz,gamma_uv_deg:s.gammaUV,gamma_yz_deg:s.gammaYZ,tau2_Nm:s.tau2,tau4_Nm:s.tau4,
    Tab_U_N:s.ab.U,Tab_L_N:s.ab.L,Tcd_U_N:s.cd.U,Tcd_L_N:s.cd.L,Tef_U_N:s.ef.U,Tef_L_N:s.ef.L,
    F12_N:Math.hypot(...s.F12),F14_N:Math.hypot(...s.F14),F25_N:Math.hypot(...s.F25),F32_N:Math.hypot(...s.F32),Fw_N:Math.hypot(...s.Fw)};for(const name of ['F12','F14','F25','F32','Fw']){item[name+'_u_N']=s[name][0];item[name+'_v_N']=s[name][1];}rows.push(item);
  }
  return {engine:'Jonathan fixed-A quasi-static reference',rows,reference_config:{...c},reference_parameters:p,source:window.JonReference.source,units:Object.fromEntries(Object.keys(rows[0]||{}).filter(k=>k.endsWith('_N')||k.endsWith('_Nm')||k.endsWith('_mm')||k.endsWith('_deg')).map(k=>[k,k.endsWith('_Nm')?'Nm':k.endsWith('_mm')?'mm':k.endsWith('_deg')?'deg':'N'])),scope:'Reference parameter sweeps; no t/time and no dynamic trajectory. Original full lower-link extension COM is outside this reference model.'};
 }
 node.querySelector('.audit-export').onclick=()=>{if(!latest)return;const data=dataset(...latest),cols=Object.keys(data.rows[0]);const text=['# '+JSON.stringify({source:data.source,parameters:data.reference_parameters}),cols.join(','),...data.rows.map(r=>cols.map(k=>r[k]??'').join(','))].join('\n'),a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'text/csv'}));a.download='linkage-reference-sweeps.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
 node.querySelector('.audit-save').onclick=()=>{if(latest)publish('motion-lab-reference-audit',{result:dataset(...latest)});};
 function update(c,row={},plots=true){
  c={...referenceDefaults,...c};
  if(!window.JonReference)return;const {VSL,VSLStatic,VSLPeaks}=window.JonReference,p=reference(c),t=180-(row.theta_deg??c.theta);latest=[c,t];
  const errors=VSLStatic.validate(p);if(!Number.isFinite(c.contact_beta_min)||!Number.isFinite(c.contact_beta_max)||c.contact_beta_min<0||c.contact_beta_min>c.contact_beta_max||c.contact_beta_max>90)errors.push('Require 0 ≤ beta minimum ≤ maximum ≤ 90 degrees.');
  const s=errors.length?{valid:false,reason:errors.join(' ')}:VSLStatic.solve(p,t),signature=JSON.stringify(p);
  node.querySelectorAll('button').forEach(button=>button.disabled=!s.valid);
  if(!s.valid){node.querySelector('.audit-state').textContent=s.reason;node.querySelector('.audit-cards').replaceChildren();node.querySelector('.audit-fbds').replaceChildren();return;}
  if(signature!==key){key=signature;peaks=VSLPeaks.fixedAlpha(p,{beta:{min:c.contact_beta_min,max:c.contact_beta_max}});}
  const quantities=[['Leg hold τ₂',s.tau2,'Nm'],['Drive hold τ₄',s.tau4,'Nm'],['T_ab tight · '+s.ab.active,Math.max(s.ab.U,s.ab.L),'N'],['C travel d_z',s.dz,'mm']];
  node.querySelector('.audit-cards').innerHTML=quantities.map(([label,value,unit])=>`<div><small>${label}</small><strong>${f(value)} ${unit}</strong></div>`).join('')+(peaks.valid?['tau2','tau4','ab','dz'].map(k=>`<div><small>Global max |${k}| · α fixed</small><strong>${f(peaks[k].value)} ${k==='ab'?'N':k==='dz'?'mm':'Nm'}</strong><small>θ₂ ${f(peaks[k].theta2)}° · β ${f(peaks[k].beta)}° · ${peaks[k].converged?'bounded gap ≤ 0.001':'estimate gap '+f(peaks[k].error)}</small></div>`).join(''):'');
  node.querySelector('.audit-state').textContent=`θ₂ ${f(t)}°, θ₃ ${f(s.t3)}°, θ₅ ${f(s.t5)}°, θ₆ ${f(s.t6)}° · d_u ${f(s.du)}, d_v ${f(s.dv)}, d_y ${f(s.dy)}, d_z ${f(s.dz)} mm · γ_uv ${f(s.gammaUV)}°, γ_yz ${f(s.gammaYZ)}° · ΣF ${s.maxForce.toExponential(2)} N, ΣM ${s.maxMoment.toExponential(2)} Nm, virtual work ${s.virtualWorkError.toExponential(2)} Nm · total mass ${f(s.mT)} kg`;
  node.querySelector('.audit-fbds').innerHTML=Object.entries(s.bodies).map(([id,b])=>{
   const global=id==='6',transform=v=>global?VSL.global(p,v):v,origin=transform(b.origin),ends=b.ends.map(transform),forces=b.forces.map(x=>({...x,pos:transform(x.pos),vec:transform(x.vec)}));
   const extent=Math.max(p.L2,p.L3,p.rw*2),scale=180/extent,map=v=>[140+(v[0]-origin[0])*scale,140-(v[1]-origin[1])*scale],max=Math.max(...forces.map(x=>Math.hypot(...x.vec)),1);
   const segments=ends.length>1?`<polyline points="${ends.map(x=>map(x).join(',')).join(' ')}" fill="none" stroke="#8fa7b6" stroke-width="7"/>`:`<circle cx="140" cy="140" r="${b.radius*scale}" fill="none" stroke="#8fa7b6"/>`;
   const arrows=forces.map(x=>{const point=map(x.pos),n=Math.hypot(...x.vec),end=[point[0]+x.vec[0]/max*50,point[1]-x.vec[1]/max*50];return `<path d="M${point}L${end}" stroke="#c9773e" stroke-width="2" marker-end="url(#force-arrow-${id})"/><circle cx="${end[0]}" cy="${end[1]}" r="2"/><text x="${end[0]+3}" y="${end[1]-3}" font-size="8" fill="currentColor">${x.name}</text>`;}).join('');
   return `<article><h3>Link ${id} · ${global?'global y/z':'local u/v'}</h3><svg viewBox="0 0 280 280"><defs><marker id="force-arrow-${id}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0L8,4L0,8Z" fill="#c9773e"/></marker></defs>${segments}${arrows}</svg><p class="hint">Residual F ${Math.hypot(...b.residualF).toExponential(1)} N / M ${Math.abs(b.residualM).toExponential(1)} Nm</p><table>${forces.map(x=>`<tr><td>${x.name}</td><td>${f(Math.hypot(...x.vec))} N</td><td>${Math.hypot(...x.vec)<1e-12?'—':f((Math.atan2(x.vec[1],x.vec[0])*180/Math.PI+360)%360)+'°'}</td></tr>`).join('')}${b.couples.map(x=>`<tr><td>${x.name}</td><td>${f(x.value)} Nm</td><td>${x.value>=0?'CCW':'CW'}</td></tr>`).join('')}</table></article>`;
  }).join('');
  if(plots&&node.querySelector('.audit-plots').parentElement.open&&plotKey!==signature+'|'+t){plotKey=signature+'|'+t;const data=dataset(c,t),holder=node.querySelector('.audit-plots');holder.replaceChildren();
   const types=[['Holding torques',['tau2_Nm','tau4_Nm']],['Tight span tensions',['Tab_U_N','Tab_L_N','Tcd_U_N','Tcd_L_N','Tef_U_N','Tef_L_N']],['Pin loads',['F12_N','F14_N','F25_N','F32_N','Fw_N']]];
   for(const axis of ['theta2','dz','beta','alpha'])for(const [title,keys] of types){const rows=data.rows.filter(x=>x.mode===axis),plot=document.createElement('div');holder.append(plot);window.Plotly.newPlot(plot,keys.map(k=>({x:rows.map(r=>r.x),y:rows.map(r=>r[k]),name:k,mode:'lines'})),{title:{text:axis+' · '+title,font:{size:12}},height:310,margin:{t:40,l:45,r:15,b:95},xaxis:{title:{text:axis==='dz'?'d_z (mm)':axis+' (deg)'}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{color:getComputedStyle(document.documentElement).getPropertyValue('--text').trim()},legend:{orientation:'h',y:-.35,font:{size:9}}},{responsive:true,displayModeBar:false});}
   for(const keys of [['theta3_deg','theta5_deg','theta6_deg','gamma_uv_deg','gamma_yz_deg'],['du_mm','dv_mm','dy_mm','dz_mm']]){const rows=data.rows.filter(x=>x.mode==='theta2'),plot=document.createElement('div');holder.append(plot);window.Plotly.newPlot(plot,keys.map(k=>({...angleTrace(rows,k),name:k,mode:'lines',connectgaps:false})),{height:310,margin:{t:25,l:45,r:15,b:95},legend:{orientation:'h',y:-.35,font:{size:9}},xaxis:{title:{text:'theta2 (deg)'}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{color:getComputedStyle(document.documentElement).getPropertyValue('--text').trim()}},{responsive:true,displayModeBar:false});}
   const rows=data.rows.filter(x=>x.mode==='theta2'),plot=document.createElement('div');holder.append(plot);
   window.Plotly.newPlot(plot,['theta3_deg','theta5_deg','theta6_deg','gamma_uv_deg','gamma_yz_deg'].map(k=>({...angleTrace(rows,k,'dz_mm'),name:k,mode:'lines',connectgaps:false,hovertemplate:'dz %{x} mm<br>%{y}<extra>%{fullData.name}</extra>'})),{title:{text:'Angles vs signed vertical travel · all branches',font:{size:12}},height:310,margin:{t:40,l:45,r:15,b:95},xaxis:{title:{text:'d_z (mm)'}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{color:getComputedStyle(document.documentElement).getPropertyValue('--text').trim()}},{responsive:true,displayModeBar:false});
  }
 }
 node.addEventListener('toggle',()=>{if(latest){plotKey='';update(latest[0],{theta_deg:180-latest[1]});}},true);
 return {update,node};
}
