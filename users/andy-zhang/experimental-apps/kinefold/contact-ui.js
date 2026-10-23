/** Native interaction-mode controls and explicit saved contact-demo creation.
 * Load after the shared Studio/project bridge. Inputs: project-v3 optional
 * contactConfig, builder mm/deg/kg/N and saved run settings. Outputs: clear
 * mode/scope guards and deliberate disk-backed demo/working-copy backup.
 * Old prescribed-height projects remain unchanged when this block is absent.
 */
globalThis.KinefoldContactUI = (() => {
  'use strict';
  const S = KinefoldStudio, P = KinefoldProjects;
  const esc = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const isContact = project => project.contactConfig?.mode === 'terrain-contact';
  function guards(project) {
    const p = project.params, c = project.solverConfig, errors = [];
    if (!(p.m1 > 0)) errors.push('Chassis mass m₁ must be positive.');
    if (!(p.m6 > 0)) errors.push('Wheel mass m₆ must be positive; no wheel mass is added automatically.');
    if (Math.abs(p.L2 - p.L3) > 1e-10 || Math.abs(p.ra / p.rb - 2) > 1e-12)
      errors.push('This exact massless-link contact model requires L₂ = L₃ and r_a/r_b = 2 (a straight wheel path).');
    if (['m2','m3','m5'].some(key => p[key] !== 0)) errors.push('Moving link/compound masses m₂, m₃ and m₅ must be zero in this two-body contact model.');
    if (c.inertiaModel !== 'uniform-rods-discs' || ['I2','I3','I5','I6','hipRotorInertiaKgM2'].some(key => c[key] !== 0))
      errors.push('Additional joint/rotor inertias are unsupported; they are never replaced by hidden masses.');
    if (c.inputRiseMm !== 0) errors.push('Actual square terrain requires zero transition distance; a smoothed height-driver profile is a different test.');
    if(p.loadMode==='contact')errors.push('Prescribed contact loads are unsupported with actual terrain contact; use weight reference or explicit global additional loads.');
    if(p.te===p.tc)errors.push('Contact mode requires a nonempty working range.');
    const lo = p.te - p.phi0 / 2, hi = p.tc - p.phi0 / 2;
    if (lo <= 90 + 1e-5 || hi >= 270 - 1e-5) errors.push('Working travel must stay on a nonsingular monotonic branch of the straight path.');
    return errors;
  }
  function payload(project, engine) {
    const value = {engine, params: project.params, runConfig: project.solverConfig};
    if (project.contactConfig) value.contactConfig = project.contactConfig;
    return value;
  }
  async function demo() {
    const accepted = await S.ask('Create a separate saved terrain-contact demo? Your current working snapshot will be preserved as a named backup. The new demo uses the V4 geometry, a 1.5 kg wheel, μ = 0.8, zero bounce and a freely backdrivable drive.', {accept: 'Save & open contact demo'});
    if (!accepted) return;
    try {
      await S.ready;
      const current = S.exportProject(), store = S.getStore();
      const matching = store.list().some(item => P.content(item) === P.content(current));
      if (!matching) await store.save({...current, id: P.id(), name: ('Before contact / ' + current.name).slice(0, 80)});
      const value = P.baseline();
      value.name = 'Terrain contact / V4 + 1.5 kg free wheel';
      value.params.m6 = 1.5;
      value.solverConfig.dt = .00025;
      value.contactConfig = {...P.contactDefaults};
      const saved = await store.save(value);
      if (await S.applySnapshot(saved)) {
        S.showTab('pymunk');
        S.toast('Saved contact demo in profiles/library.json. Original named designs and the prior working snapshot are preserved.');
      }
    } catch (error) { S.toast('Contact demo was not opened: ' + error.message); }
  }
  function mount(id, root) {
    const panel = document.createElement('section');
    panel.className = 'contact-mode-panel'; panel.dataset.contactPanel = id;
    panel.innerHTML = id === 'pymunk' ? `<div class="contact-mode-heading"><div><span class="eyebrow">INTERACTION MODEL</span><h3>Terrain contact or prescribed-height bench</h3></div><button data-contact-demo>Save & open contact demo</button></div><div class="contact-controls"><label>Mode<select data-contact-mode><option value="prescribed-height">Prescribed wheel-height bench</option><option value="terrain-contact">Actual wheel / square-terrain contact</option></select></label><label>Effective friction μ<input data-contact-friction type="number" min="0" max="2" step=".05"></label><span>Restitution 0 · freely backdrivable drive</span></div><div data-contact-description></div>` : '<div data-contact-description></div>';
    root.querySelector('.quarter-scope').before(panel);
    if (id === 'pymunk') {
      panel.querySelector('[data-contact-demo]').onclick = demo;
      panel.querySelector('[data-contact-mode]').onchange = event => {
        const current = S.getSnapshot();
        S.setContactConfig({...P.contactDefaults, ...(current.contactConfig || {}), mode: event.target.value});
      };
      panel.querySelector('[data-contact-friction]').onchange = event => {
        try { const current = S.getSnapshot(); S.setContactConfig({...P.contactDefaults, ...(current.contactConfig || {}), friction: event.target.value===''?NaN:Number(event.target.value)}); }
        catch (error) { S.toast(error.message); update(S.getSnapshot()); }
      };
    }
  }
  function update(project) {
    const contact = isContact(project), config = project.contactConfig || P.contactDefaults;
    for (const id of ['analytical', 'pymunk']) {
      const panel = document.querySelector(`[data-contact-panel="${id}"]`); if (!panel) continue;
      const description = panel.querySelector('[data-contact-description]');
      const errors = contact ? guards(project) : [];
      description.innerHTML = contact ? `<p><strong>Actual unilateral wheel / terrain collision · ¼ model</strong>. The wheel can spin, slip, separate and bridge gaps. The saved world mesh moves toward −x; wheel height is solved by contact. θ₄ is freely backdriven through the ideal belts. This bounded model uses a real chassis and wheel with exact massless straight-path links.</p>${id === 'analytical' ? '<p class="notice">The analytical height-driven bench is a different model. Its Run and paired comparison are disabled for this saved contact profile; use the Pymunk tab.</p>' : ''}${errors.length ? '<div class="notice error"><strong>Unsupported contact setup</strong><ul>' + errors.map(error => '<li>' + esc(error) + '</li>').join('') + '</ul></div>' : '<p>Geometry guards pass. Solver validation also checks the complete route, stops, initial separation and numerical limits.</p>'}<p>Plateau and gap settings are actual terrain dimensions, not commanded wheel travel. First-contact delay includes circular-rim clearance; the wheel is never forced down into every gap.</p>` : '<p><strong>Prescribed wheel-height bench</strong> · no wheel/terrain collision. The original analytical/Pymunk comparison remains available. The belt drive is locked and the baseline wheel index can remain stationary (K = 0). Use the separate saved contact demo for frictional wheel spin and collision.</p>';
      const legacyScope = document.getElementById(id).querySelector('.quarter-scope');
      legacyScope.hidden = contact;
      const title=document.getElementById(id).querySelector('.solver-heading p');
      title.textContent=contact?(id==='pymunk'?'Real chassis + wheel · actual terrain contact':'Analytical prescribed-height bench · unavailable for this contact profile'):(id==='pymunk'?'Pymunk chassis body · ideal belt-coupled transmission':'Reduced equations · SciPy DOP853');
      const hold=document.getElementById(id).querySelector('[data-hold]');hold.disabled=contact;hold.title=contact?'Locked-drive static balance is not the freely backdriven contact model.':'';
      if (id === 'pymunk') {
        panel.querySelector('[data-contact-mode]').value = contact ? 'terrain-contact' : 'prescribed-height';
        panel.querySelector('[data-contact-friction]').value = config.friction;
        panel.querySelector('[data-contact-friction]').disabled = !contact;
        panel.querySelector('.contact-controls span').hidden=!contact;
      }
    }
  }
  return {isContact, guards, payload, mount, update, demo};
})();
