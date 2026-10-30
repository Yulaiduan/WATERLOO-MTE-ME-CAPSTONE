/** Compose automatic comparison and the independent quick calculator in tab 06.
 * Load after both feature modules and Studio. Inputs: read-only saved project
 * (builder mm/deg/kg), local comparison assumptions and explicit job actions.
 * Outputs: selected workspace, bounded HTTP jobs and Plotly resize notifications.
 * Neither subview applies candidates to the active mechanism or motor settings.
 */
(function(root){
  'use strict';
  const host=document.getElementById('actuator');
  if(!host||!root.KinefoldAutomaticComparison||!root.KinefoldStudio)return;
  const automatic=document.getElementById('automatic-comparison');
  const quick=document.getElementById('actuator-quick');
  const controller=root.KinefoldAutomaticComparison.mount(automatic,{studio:root.KinefoldStudio});
  root.KinefoldAutomaticStudy=controller;
  function select(mode){
    automatic.hidden=mode!=='automatic';quick.hidden=mode!=='quick';
    for(const button of host.querySelectorAll('[data-actuator-view]'))
      button.setAttribute('aria-pressed',String(button.dataset.actuatorView===mode));
    if(mode==='quick')root.KinefoldQuickActuator?.recompute();
    else controller.refresh?.();
    root.dispatchEvent(new Event('resize'));
  }
  host.addEventListener('click',event=>{
    const button=event.target.closest('[data-actuator-view]');
    if(button)select(button.dataset.actuatorView);
  });
  root.addEventListener('kinefold-solver-tab',event=>{
    if(event.detail?.id==='actuator'){
      if(!automatic.hidden)controller.refresh?.();
      root.dispatchEvent(new Event('resize'));
    }
  });
})(globalThis);
