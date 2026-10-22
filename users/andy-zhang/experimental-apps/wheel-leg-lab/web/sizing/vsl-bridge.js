/** App bridge for unchanged Jonathan V4. Loaded after its original inline scripts.
 * Inputs: VSLApp profile (mm/deg/kg/N/Nm), requested vertical hub speed (mm/s).
 * Outputs: explicit frozen hip-torque/speed sweep to sizing and browser library.
 * Limits: fixed-A prescribed contact loads, no added dynamic or wheel-drive sizing.
 */
(() => {
  const bar=document.createElement('div');bar.className='vsl-lab-bar';
  bar.innerHTML='<strong>JON V4 → ACTUATOR SIZING</strong><label>Vertical hub speed (mm/s)<input id="vsl-speed" type="number" value="100" min="0" max="3000" step="any"></label><button id="vsl-to-sizing">Compare this V4 design with motors</button><button id="vsl-save-study">Save V4 sweep to Profiles & data</button><a href="v4-model.md" target="_blank">Source model notes ↗</a>';
  document.querySelector('.topbar').after(bar);
  const note=document.createElement('p');note.className='vsl-lab-note';note.id='vsl-lab-status';note.textContent='Original V4 solver and fitter. Export takes a snapshot of the current valid parameters, with applied CCW hip torque. Contact loads stay prescribed; speed is a kinematic screen without dynamic torque.';bar.after(note);
  const pause=()=>{if(window.VSLApp?.playing)document.getElementById('play')?.click();for(const button of document.querySelectorAll('button.running'))button.click();};
  pause();
  function packet(){
    if(document.querySelector('input[aria-invalid="true"]'))throw Error('Correct the invalid V4 input before transferring.');
    const p=window.VSLApp.parameters,errors=VSLStatic.validate(p),speed=document.getElementById('vsl-speed').valueAsNumber;
    if(errors.length)throw Error(errors.join(' '));if(!Number.isFinite(speed)||speed<0||speed>3000)throw Error('Use a vertical speed from 0 to 3000 mm/s.');
    const rows=[];
    for(let i=0;i<=180;i++){
      const theta2=p.te+(p.tc-p.te)*i/180,s=VSLStatic.solve(p,theta2,false),J=s.spring?.Jz;
      if(!s.valid)throw Error(`V4 pose ${theta2.toFixed(2)}° is invalid: ${s.reason}`);
      if(!Number.isFinite(J)||Math.abs(J)<1e-5)throw Error(`Vertical Jacobian is singular at ${theta2.toFixed(2)}°. Narrow the V4 angle window before sizing.`);
      if(rows.length&&rows.at(-1).Jz_mm_per_rad*J<0)throw Error('The V4 window crosses a vertical turning point. Narrow it to a monotonic height branch before imposing nonzero vertical speed.');
      rows.push({theta2,hipTorque:s.tau2,gravityTorque:s.tauG,springTorque:s.tauS,outputRpm:Math.abs(speed/J)*60/(2*Math.PI),Jz_mm_per_rad:J,springForce:s.spring.force,compensationPercent:VSLStatic.compensationPercent(s),dz_mm:s.dz});
    }
    return {schema:'motion-lab-v4-sizing/v1',parameters:p,springDriven:window.VSLApp.springDriven,verticalSpeed_mm_s:speed,rows,
      units:{theta2:'deg',hipTorque:'N m',gravityTorque:'N m',springTorque:'N m',outputRpm:'rpm',Jz_mm_per_rad:'mm/rad',springForce:'N',compensationPercent:'%',dz_mm:'mm'},
      source:'users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-pulley.html',sourceSha256:document.querySelector('meta[name="vsl-source-sha256"]').content,
      torqueConvention:'applied-ccw-hip',generated:new Date().toISOString(),scope:'Fixed-A V4 quasi-static torque with prescribed contact loads; kinematic speed only; no inertia/contact/thermal validation.'};
  }
  for(const [id,type]of [['vsl-to-sizing','motion-lab-v4-sizing'],['vsl-save-study','motion-lab-v4-save']])document.getElementById(id).onclick=()=>{
    try{pause();const data=packet();sessionStorage.setItem('motion-lab-v4-sizing/v1',JSON.stringify(data));if(parent!==window)parent.postMessage({type,packet:data},location.origin);else if(type==='motion-lab-v4-sizing')location.href='/?tab=sizing';else throw Error('Open V4 from the Motion Lab tab to save to its library.');note.classList.remove('vsl-lab-error');note.textContent='V4 snapshot captured. Editing the solver later requires a new transfer.';}catch(error){note.classList.add('vsl-lab-error');note.textContent=error.message;}
  };
  window.addEventListener('message',event=>{if(event.origin!==location.origin)return;if(event.data?.type==='motion-lab-deactivate')pause();});
  parent.postMessage({type:'motion-lab-ready'},location.origin);
})();
