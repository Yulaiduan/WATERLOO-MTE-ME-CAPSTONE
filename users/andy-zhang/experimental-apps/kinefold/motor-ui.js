/** Shared optional hip-motor model controls, conversion and saved-profile identity.
 * Load before solvers.js. Inputs: project-v3 motorConfig, SI motor parameters;
 * outputs synchronized controls only. Physical laws live in backend motor_model.
 * All zero/default values are compatibility settings, not measured motor data.
 */
globalThis.KinefoldMotorUI = (() => {
  'use strict';
  const S=KinefoldStudio,P=KinefoldProjects;
  const fields=[
    ['gearRatio','Motor → hip reduction N','ω motor / ω hip',1e-6,1e4],
    ['rotorInertiaKgM2','Rotor inertia J motor','kg·m²',0,1000],
    ['coggingAmplitudeNm','Cogging amplitude · motor shaft','N·m',0,10000],
    ['coggingPeriodsPerRev','Cogging periods / motor revolution','cycles',1,10000,1],
    ['coggingPhaseDeg','Cogging phase at joint q = 0','°',-360,360],
    ['coulombFrictionNm','Regularized Coulomb friction · motor shaft','N·m',0,10000],
    ['viscousFrictionNms','Viscous friction · motor shaft','N·m·s/rad',0,10000],
    ['frictionVelocityScaleRadS','Coulomb smoothing speed · motor shaft','rad/s',1e-6,1000]
  ];
  const fmt=v=>Number(v).toLocaleString('en-CA',{maximumSignificantDigits:6});
  const basis=p=>p.motorConfig?.enabled&&p.motorConfig.commandBasis==='motor'?'motor shaft':'hip joint';
  function balanceCommand(project,staticJointTorque){
    const c={...P.motorDefaults,...project.motorConfig};
    if(!c.enabled)return staticJointTorque;
    const phase=(c.coggingPeriodsPerRev*c.gearRatio*project.params.theta2+c.coggingPhaseDeg)*Math.PI/180;
    const joint=staticJointTorque-c.gearRatio*c.coggingAmplitudeNm*Math.sin(phase);
    return c.commandBasis==='motor'?joint/c.gearRatio:joint;
  }
  function mount(id,root){
    const panel=document.createElement('details');panel.className='motor-panel contact-mode-panel';panel.dataset.motorPanel=id;
    panel.innerHTML=`<summary><strong>Hip motor, gearing & losses</strong> <small data-motor-summary></small></summary><p>The hip actuator is separate from the freely spinning wheel drive. Enter motor data explicitly; enabling this model does not add link or wheel mass.</p><label><input data-motor-key="enabled" type="checkbox"> Enable physical motor model</label><div class="contact-controls"><label>Entered torque basis<select data-motor-key="commandBasis"><option value="joint">Hip joint · existing command semantics</option><option value="motor">Motor shaft · converted through N</option></select></label>${fields.map(([key,label,unit,lo,hi,step])=>`<label>${label} · ${unit}<input data-motor-key="${key}" type="number" min="${lo}" max="${hi}" step="${step||'any'}"></label>`).join('')}</div><p data-motor-conversion></p><p>Cogging is a conservative sinusoidal detent, with rotor angle θm = Nq and fixed q = 0 phase reference. Friction = −F_c tanh(ωm/ωε) − bωm; it models smooth losses, not static stiction. Existing hip viscous damping stays joint-side and adds to motor-side losses. The legacy additional joint inertia adds to N²Jm.</p><p>Terrain, jump and landing torque inputs and search ceilings use the selected basis. Energy-sized braking is calculated joint-side before conversion; the hold controller compensates passive torques. Ripple curves and impact forces are sampled; refine the integration step. Native contact with rotor inertia reports signed numerical constraint work separately; contact/stop loss partition can be unavailable. Exact-elimination constraint residuals are identically zero.</p><button data-motor-remove>Remove motor block · legacy ideal profile</button>`;
    root.querySelector('.dyn-settings-panel').before(panel);
    for(const field of panel.querySelectorAll('[data-motor-key]'))field.onchange=()=>{
      try{const value={...P.motorDefaults,...S.getSnapshot().motorConfig};for(const input of panel.querySelectorAll('[data-motor-key]'))value[input.dataset.motorKey]=input.type==='checkbox'?input.checked:input.tagName==='SELECT'?input.value:input.value===''?NaN:Number(input.value);S.setMotorConfig(value);}
      catch(error){S.toast(error.message);update(S.getSnapshot());}
    };
    panel.querySelector('[data-motor-remove]').onclick=()=>S.setMotorConfig(null);
  }
  function update(project){
    const c={...P.motorDefaults,...project.motorConfig},where=basis(project),N=c.enabled?c.gearRatio:1,J=c.enabled?N*N*c.rotorInertiaKgM2:0;
    for(const panel of document.querySelectorAll('[data-motor-panel]')){
      for(const input of panel.querySelectorAll('[data-motor-key]')){const key=input.dataset.motorKey;if(input.type==='checkbox')input.checked=c[key];else input.value=c[key];input.disabled=key!=='enabled'&&!c.enabled;}
      panel.querySelector('[data-motor-summary]').textContent=c.enabled?`N ${fmt(N)} · J reflected ${fmt(J)} kg·m²`:'Ideal / disabled';
      panel.querySelector('[data-motor-conversion]').textContent=`Commands: ${where}. ωm = ${fmt(N)} q̇; τjoint = ${fmt(N)} τshaft; reflected rotor inertia = ${fmt(J)} kg·m²; joint cogging amplitude ${fmt(c.enabled?N*c.coggingAmplitudeNm:0)} N·m; joint Coulomb ${fmt(c.enabled?N*c.coulombFrictionNm:0)} N·m; joint viscous ${fmt(c.enabled?N*N*c.viscousFrictionNms:0)} N·m·s/rad; cogging ${fmt(N*c.coggingPeriodsPerRev)} cycles per joint revolution. Ideal rigid reduction; losses come from entered friction.`;
      panel.querySelector('[data-motor-remove]').disabled=!project.motorConfig;
      const workspace=panel.closest('[role=tabpanel]'),label=workspace.querySelector('[data-run-key="hipTorqueNm"]').closest('label').querySelector('span');
      label.textContent=`Constant ${where} torque · N·m`;
      for(const [key,title]of [['jumpTorqueNm','Extension torque'],['landingBrakeTorqueNm','Entered resisting torque'],['landingBrakeLimitNm','Brake/search torque ceiling']]){
        const input=workspace.querySelector(`[data-case-key="${key}"]`);if(input?.closest('label')?.firstChild?.nodeType===3)input.closest('label').firstChild.textContent=`${title} · ${where} N·m`;
      }
    }
  }
  return {mount,update,basis,balanceCommand};
})();
