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
    try { P.validateFixture(project); } catch (error) { errors.push(error.message); }
    if (!(p.m1 > 0)) errors.push('Chassis mass m₁ must be positive.');
    if (!(p.m6 > 0)) errors.push('Wheel mass m₆ must be positive; no wheel mass is added automatically.');
    if (Math.abs(p.L2 - p.L3) > 1e-10 || Math.abs(p.ra / p.rb - 2) > 1e-12)
      errors.push('This exact straight-path contact model requires L₂ = L₃ and r_a/r_b = 2 (a straight wheel path).');
    if (p.m5 !== 0 || !((p.m2 === 0 && p.m3 === 0) || (p.m2 > 0 && p.m3 > 0))) errors.push('Use either both massless links or two positive uniform-rod link masses; compound mass m₅ must remain zero in actual-contact mode.');
    if (c.inertiaModel !== 'uniform-rods-discs' || ['I2','I3','I5','I6'].some(key => c[key] !== 0))
      errors.push('Custom link/wheel inertias are unsupported; the separate motor rotor model and legacy additional joint inertia are handled explicitly.');
    if (c.inputRiseMm !== 0) errors.push('Actual square terrain requires zero transition distance; a smoothed height-driver profile is a different test.');
    if(p.loadMode==='contact')errors.push('Prescribed contact loads are unsupported with actual terrain contact; use weight reference or explicit global additional loads.');
    if(p.te===p.tc)errors.push('Contact mode requires a nonempty working range.');
    const mean=(180+p.phi0)/2,R=Math.PI/180;
    if(Array.from({length:6},(_,i)=>mean+(i-2)*180).some(q=>q>=p.te-1e-8&&q<=p.tc+1e-8))errors.push('Working travel must stay on a nonsingular monotonic branch of the straight path.');
    const kind=project.caseConfig?.kind||'terrain-stability',axisZ=Math.sin((p.alpha-mean)*R),J=-2*p.L2/1000*Math.sin(((p.te+p.tc)/2-mean)*R);
    if(kind!=='terrain-stability'&&axisZ*J<=0)errors.push('Jump/landing require θ_c to be the geometrically compressed endpoint; this branch reverses that convention.');
    if(kind==='landing'&&project.caseConfig?.brakeStrategy==='energy-sized'&&Math.abs(Math.cos((mean-p.alpha)*R))>1e-10)errors.push('Energy-sized braking requires a vertical guide on flat ground. Entered torque and dynamic search remain available for tilted geometry.');
    return errors;
  }
  function payload(project, engine) {
    const value = {engine, params: project.params, runConfig: project.solverConfig};
    if (project.contactConfig) value.contactConfig = project.contactConfig;
    if (project.caseConfig) value.caseConfig = project.caseConfig;
    if (project.motorConfig) value.motorConfig = project.motorConfig;
    if (project.terrainConfig) value.terrainConfig = project.terrainConfig;
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
    panel.innerHTML = `<div class="contact-mode-heading"><div><span class="eyebrow">INTERACTION MODEL</span><h3>Terrain contact or prescribed-height bench</h3></div><button data-contact-demo>Save & open contact demo</button></div><div class="contact-controls"><label>Mode<select data-contact-mode><option value="prescribed-height">Prescribed wheel-height bench</option><option value="terrain-contact">Actual wheel / terrain contact</option></select></label><label>Chassis fixture<select data-contact-fixture><option value="floating-chassis">Floating · vertical motion</option><option value="pinned-chassis">Pinned · force diagnostic</option></select></label><label>Effective friction μ<input data-contact-friction type="number" min="0" max="2" step=".05"></label><span>Restitution 0 · freely backdrivable drive</span></div><div data-contact-description></div>`;
    root.querySelector('.quarter-scope').before(panel);
    {
      panel.querySelector('[data-contact-demo]').onclick = demo;
      panel.querySelector('[data-contact-mode]').onchange = event => {
        try { const current = S.getSnapshot(); S.setContactConfig({...P.contactDefaults, ...(current.contactConfig || {}), mode: event.target.value}); }
        catch (error) { S.toast(error.message); update(S.getSnapshot()); }
      };
      panel.querySelector('[data-contact-fixture]').onchange = event => {
        try { const current = S.getSnapshot(); S.setSolverConfig({...current.solverConfig, fixture:event.target.value}); }
        catch (error) { S.toast(error.message); update(S.getSnapshot()); }
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
      const errors = contact ? guards(project) : [], pinned=project.solverConfig.fixture==='pinned-chassis';
      description.innerHTML = contact ? `<p><strong>Actual unilateral wheel / terrain collision · ¼ model</strong>. The wheel can spin, slip, separate and bridge gaps. Terrain stability moves the saved world mesh toward −x; jump and landing use a stationary flat floor. Wheel height is solved by contact. θ₄ is freely backdriven through the ideal belts. This bounded straight-path model supports either massless links or two finite uniform rods. V4.5 uses 1 kg per rod and a 0.5 kg freely spinning wheel.</p><p>Both engines now solve this same actual-contact model: independent generalized-mass impulse dynamics and native Pymunk rigid bodies. Finite-link mode has chassis, two rods and wheel with pivot and belt constraints. Run both captures one exact saved mechanism, material and case.</p>${errors.length ? '<div class="notice error"><strong>Unsupported contact setup</strong><ul>' + errors.map(error => '<li>' + esc(error) + '</li>').join('') + '</ul></div>' : '<p>Geometry guards pass. Solver validation also checks the complete route, stops, initial separation and numerical limits.</p>'}<p>Plateau and gap settings are actual terrain dimensions, not commanded wheel travel. Terrain-stability first-contact delay includes circular-rim clearance; the wheel is never forced down into every gap.</p>` : '<p><strong>Prescribed wheel-height bench</strong> · no wheel/terrain collision. The original analytical/Pymunk comparison remains available. The belt drive is locked and the baseline wheel index can remain stationary (K = 0). Use the separate saved contact demo for frictional wheel spin and collision.</p>';
      if(contact)description.insertAdjacentHTML('beforeend',pinned?'<p><strong>Chassis pinned at its initial hip height.</strong> Only the chassis fixture is fixed; the wheel is free to rotate, separate and recontact the terrain. Pin force is an interval mean, positive upward from the fixture onto the chassis. Positive means the fixture supplies missing support; negative means it holds down excess suspension force. The unchanged height controller sees no chassis-height error here: this is a force-transmission diagnostic, not a direct rise-time test.</p>':'<p><strong>Chassis floats vertically.</strong> Its height, tracking delay and settling follow the actual coupled dynamics. The wheel is never pinned to terrain.</p>');
      const legacyScope = document.getElementById(id).querySelector('.quarter-scope');
      legacyScope.hidden = contact;
      const title=document.getElementById(id).querySelector('.solver-heading p');
      title.textContent=contact?(id==='pymunk'?(project.params.m2>0?'Native chassis + two rods + wheel · actual contact':'Real chassis + wheel · actual terrain contact'):'Independent reduced contact dynamics · unilateral friction impulses'):(id==='pymunk'?'Pymunk chassis body · ideal belt-coupled transmission':'Reduced equations · SciPy DOP853');
      const hold=document.getElementById(id).querySelector('[data-hold]');hold.disabled=contact;hold.title=contact?'Locked-drive static balance is not the freely backdriven contact model.':'';
      {
        panel.querySelector('[data-contact-mode]').value = contact ? 'terrain-contact' : 'prescribed-height';
        panel.querySelector('[data-contact-fixture]').value=project.solverConfig.fixture;
        panel.querySelector('[data-contact-fixture]').disabled=!contact||(project.caseConfig?.kind||'terrain-stability')!=='terrain-stability';
        panel.querySelector('[data-contact-friction]').value = config.friction;
        panel.querySelector('[data-contact-friction]').disabled = !contact;
        panel.querySelector('.contact-controls span').hidden=!contact;
      }
    }
  }
  return {isContact, guards, payload, mount, update, demo};
})();
