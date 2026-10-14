/** Injected inside Jonathan's browser-UI closure by build_jon_linkage.py.
 * Inputs: original v1/v2 parameter JSON in mm/deg/kg/N/Nm and explicit UI state.
 * Outputs: validated snapshots, original-model equilibrium and four analytical sweeps.
 * Invocation: generated /jon-linkage/ page; no standalone execution or dynamics.
 * Limits: original ranges/contact/preload assumptions; inertias remain unused.
 */
function labNormalize(data) {
 if (!data || !['general-vsl/v1-kinematics','general-vsl/v2-quasi-static'].includes(data.schema)) throw Error('Unsupported Jonathan parameter schema.');
 let next={...VSLStatic.defaults};
 for(const k of Object.keys(next))if(data.parameters?.[k]!==undefined)next[k]=data.parameters[k];
 next=VSLStatic.resolveLoads(next);
 const errors=VSLStatic.validate(next);if(errors.length)throw Error(errors.join(' '));
 const windows=JSON.parse(JSON.stringify(rangeDefaults));
 for(const k in windows){
  if(data.ranges?.[k])windows[k]={...data.ranges[k]};
  const r=windows[k],maximum=k==='alpha'?45:k==='beta'?90:Infinity,minimum=isForce(k)?-Infinity:0;
  if(!Number.isFinite(r.min)||!Number.isFinite(r.max)||r.min>r.max||r.min<minimum||r.max>maximum)throw Error('Invalid '+k+' master window.');
 }
 const ds={};for(const g of groups){const d=data.driven?.[g.q]??g.q;if(![g.q,g.a,g.b].includes(d))throw Error('Invalid driven selection.');ds[g.q]=d;}
 if(data.theta2!==undefined&&!Number.isFinite(data.theta2))throw Error('Current theta2 must be finite degrees.');
 return {...data,schema:'general-vsl/v2-quasi-static',parameters:next,ranges:windows,driven:ds,theta2:data.theta2===undefined?next.te:clamp(data.theta2,next.te,next.tc)};
}
function labSnapshot(){
 if(draftInvalid)throw Error('Correct invalid inputs before saving the linkage.');
 return {schema:'general-vsl/v2-quasi-static',parameters:VSLStatic.resolveLoads(p),driven:{...driven},ranges:JSON.parse(JSON.stringify(ranges)),theta2:t,absoluteTorques:$('absoluteTorques').checked,
  view:Object.fromEntries(['showTau2','showTau4','showWheelForces'].map(id=>[id,$(id).checked])),
  motionLab:{period:$('period').value,geometry:Object.fromEntries(['showAB','showDrive','showWheel'].map(id=>[id,$(id).checked])),series:{...visible},kineticSeries:Object.fromEntries([...document.querySelectorAll('[data-kseries]')].map(el=>[el.dataset.kseries,el.checked]))}};
}
function labRestore(data){
 const next=labNormalize(data); // Validate everything before touching the current solution.
 p=next.parameters;driven=next.driven;ranges=next.ranges;t=next.theta2;
 setPlaying(false);phase=p.te===p.tc?0:Math.acos(clamp(1-2*(t-p.te)/(p.tc-p.te),-1,1));
 draftInvalid=false;noticeError='';document.querySelectorAll('[aria-invalid]').forEach(el=>el.removeAttribute('aria-invalid'));
 $('absoluteTorques').checked=Boolean(next.absoluteTorques);
 for(const id of ['showTau2','showTau4','showWheelForces'])$(id).checked=next.view?.[id]!==false;
 for(const id of ['showAB','showDrive','showWheel'])if(typeof next.motionLab?.geometry?.[id]==='boolean')$(id).checked=next.motionLab.geometry[id];
 for(const key of Object.keys(visible))if(typeof next.motionLab?.series?.[key]==='boolean')visible[key]=next.motionLab.series[key];
 document.querySelectorAll('[data-series]').forEach(el=>el.checked=visible[el.dataset.series]);
 document.querySelectorAll('[data-kseries]').forEach(el=>{const v=next.motionLab?.kineticSeries?.[el.dataset.kseries];if(typeof v==='boolean')el.checked=v;});
 if([...$('period').options].some(o=>o.value===next.motionLab?.period))$('period').value=next.motionLab.period;
 lastKineticPlot=-Infinity;lastAlphaChart=NaN;syncFields();syncKineticFields();recompute();
 return labSnapshot();
}
function labSweep(data=labSnapshot()){
 const config=labNormalize(data),pp=config.parameters,pose=config.theta2,rows=[];
 const units={x:'see x_unit per sweep',theta2_deg:'deg',alpha_deg:'deg',beta_deg:'deg',Fn_N:'N',Ft_N:'N',Fy_N:'N',Fz_N:'N',dz_mm:'mm',gamma_uv_deg:'deg',gamma_yz_deg:'deg',tau2_Nm:'Nm',tau4_Nm:'Nm'};
 for(const key of ['ab','cd','ef'])for(const side of ['U','L'])units[`T${key}_${side}_N`]='N';
 for(const key of ['F12','F14','F25','F32','Fw'])for(const component of ['u','v'])units[`${key}_${component}_N`]='N';
 for(const axis of ['t2','dz','beta','alpha']){
  const lo=axis==='t2'?90:axis==='dz'?pp.te:0,hi=axis==='t2'?180:axis==='dz'?pp.tc:axis==='beta'?90:45;
  const boundaries=axis==='t2'||axis==='dz'?[pp.te,pp.tc,pose]:[config.ranges[axis].min,config.ranges[axis].max,pp[axis]];
  const xs=[...new Set([...Array.from({length:361},(_,i)=>lo+(hi-lo)*i/360),...boundaries])].sort((a,b)=>a-b);
  for(const value of xs){
   const params=axis==='beta'||axis==='alpha'?{...pp,[axis]:value}:pp,theta=axis==='t2'||axis==='dz'?value:pose,s=VSLStatic.solve(params,theta,false);
   if(!s.valid)throw Error(s.reason||'Resolve overlapping belt pitch circles before saving a sweep.');
   const row={mode:axis,x:axis==='dz'?s.dz:value,x_unit:axis==='dz'?'mm':'deg',theta2_deg:theta,alpha_deg:params.alpha,beta_deg:params.beta,Fn_N:s.Fn,Ft_N:s.Ft,Fy_N:s.Fy,Fz_N:s.Fz,dz_mm:s.dz,gamma_uv_deg:s.gammaUV,gamma_yz_deg:s.gammaYZ,tau2_Nm:s.tau2,tau4_Nm:s.tau4};
   for(const key of ['ab','cd','ef'])for(const side of ['U','L'])row[`T${key}_${side}_N`]=s[key][side];
   for(const key of ['F12','F14','F25','F32','Fw'])for(const [i,component] of ['u','v'].entries())row[`${key}_${component}_N`]=s[key][i];
   rows.push(row);
  }
 }
 return {backend:'jon_v2',engine:'Jonathan v2 analytical equilibrium',config,units,rows,source:window.JonLinkageSource,
  scope:'Four parameter sweeps, not recorded time integration. C is wheel centre; P contact. Signed loads are prescribed; inertias unused. Comparison overlays use sample indices, with no time deltas.'};
}
window.JonLinkage={snapshot:labSnapshot,restore:labRestore,normalize:labNormalize,sweep:labSweep,pause:()=>setPlaying(false),solve:(data,theta)=>{const config=labNormalize(data);return VSLStatic.solve(config.parameters,theta??config.theta2);}};
