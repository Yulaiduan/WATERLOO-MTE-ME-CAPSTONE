/** Kinefold mechanism adapter; load after reference-v4.js (browser or Node VM).
 * Inputs: explicit design in mm, deg, kg, N; theta2 in deg. Outputs: points in
 * front-left x/y/z, cable geometry and a static preview. No dynamics/contact solve.
 * Jon's source scalar rotations are preserved about the new +y axis.
 */
globalThis.Kinefold = (() => {
  const {VSL, VSLStatic, VSLSpring} = globalThis.KinefoldV4;
  const schema = 'kinefold/mechanism-v1';
  const springConvention='chassis-fixed-v1',legacySpringConvention='legacy-leg-v1';
  const defaults = {...VSLStatic.defaults, Fx:0, loadMode:'weight', springLaw:'v4', theta2:132.5};
  delete defaults.Fy;
  const point = ([y,z]) => [-y,0,z];
  function reference(p,convention=springConvention) {
    if(p.springLaw!=='v4')throw Error('Constant cable-force spring support has been removed. Use the V4 linear spring for gravity compensation.');
    const r = {...p, Fy:-p.Fx, loadMode:p.loadMode==='contact'?'nt':'yz',
      springK:p.springK};
    if(convention!==legacySpringConvention){const a=p.alpha*Math.PI/180,c=Math.cos(a),s=Math.sin(a);r.Su=c*p.Su-s*p.Sv;r.Sv=s*p.Su+c*p.Sv;}
    if (p.loadMode==='weight') {r.Fy=0; r.Fz=VSLSpring.totalMass(p)*p.g;}
    return VSLStatic.resolveLoads(r);
  }
  // Spring-only world/chassis geometry. The horn phase still follows the leg;
  // the fixed idler and outgoing housing do not inherit the leg's alpha rotation.
  function springReference(p,convention=springConvention){const r=reference(p,convention);return convention===legacySpringConvention?r:{...r,alpha:0,Su:p.Su,Sv:p.Sv,nu:p.nu-p.alpha};}
  function validate(p,convention=springConvention) {
    const errors=[];
    for (const [key,value] of Object.entries(defaults)) {
      if (typeof value==='number' && !Number.isFinite(p[key])) errors.push(`${key} must be a finite number.`);
    }
    if (!['weight','global','contact'].includes(p.loadMode)) errors.push('Choose a known loading convention.');
    if (p.springLaw!=='v4') errors.push('Constant cable-force spring support has been removed. Use the V4 linear spring for gravity compensation.');
    if (errors.length) return errors;
    if (p.springK<0) errors.push('Spring rate k must be nonnegative.');
    if (p.theta2<p.te || p.theta2>p.tc) errors.push('Preview angle must be inside the working range.');
    const r=reference(p,convention);
    errors.push(...VSLStatic.validate(r), ...VSL.warnings(r).filter(x=>x.includes('overlap')));
    if(p.springEnabled&&convention!==legacySpringConvention){const fixed=springReference(p),route=VSLSpring.exit(fixed);errors.push(...VSLSpring.validate(fixed));if(route.valid&&Math.abs(route.applied)>1e-8)errors.push('Fixed chassis spring exit cannot stay horizontal over this travel; change the idler/horn geometry.');}
    return [...new Set(errors)];
  }
  function evaluate(p,convention=springConvention) {
    const errors=validate(p,convention);
    if (errors.length) return {valid:false,errors};
    const r=reference(p,convention), k=VSL.state(r,p.theta2), s=VSLStatic.solve(r,p.theta2,true);
    if (!s.valid) return {valid:false,errors:[s.reason]};
    const sp=s.spring, fixed=springReference(p,convention),drawingSpring=VSLSpring.state(fixed,p.theta2),toWorld=v=>point(VSL.global(r,v));
    const path=Array.from({length:181},(_,i)=>toWorld(VSL.raw(r,r.te+(r.tc-r.te)*i/180).P));
    const zs=path.map(p=>p[2]);
    return {valid:true,reference:r,raw:s,A:[0,0,0],B:point(k.Bg),C:point(k.Pg),P:point(s.Pg),
      D:toWorld(VSLSpring.position(r,p.theta2).D),S:toWorld([r.Su,r.Sv]),
      Q:sp.valid?point(sp.Qg):null,Qout:drawingSpring.valid?point(drawingSpring.outg):null,
      spring:{...drawingSpring,Jz:sp.Jz,Feq:sp.Feq,supportRatio:sp.supportRatio},springConvention:convention,path, travel:Math.max(...zs)-Math.min(...zs),
      mass:VSLSpring.totalMass(r), force:point(s.FcontactG),
      delta:point([k.dy,k.dz]),ratios:VSL.ratios(r),wheelAngle:k.t6,
      warnings:[...VSL.warnings(r).filter(x=>!x.includes('overlap')),
        ...(p.alpha!==0&&convention===springConvention?['Chassis-fixed spring · constants unchanged; refit for gravity compensation.']:[]),
        ...(sp.referenceExtrapolated&&r.springEnabled?['The 90° preload reference is extrapolated beyond the working cable wrap.']:[]),
        ...(sp.slack&&r.springEnabled?['Cable tension is zero at this pose; slack recovery is outside this builder.']:[])]};
  }
  function pack(params,view,name) {return {schema,name,params:{...params},view:{...view}};}
  function unpack(value) {
    if (value?.schema!==schema || !value.params) throw Error('This file is not a Kinefold mechanism-v1 design.');
    const p={};
    for (const key of Object.keys(defaults)) {
      if (!(key in value.params)) throw Error(`Missing design parameter: ${key}`);
      p[key]=value.params[key];
    }
    const errors=validate(p);if(errors.length)throw Error(errors.join(' '));
    return {params:p,name:typeof value.name==='string'?value.name.slice(0,80):'Imported mechanism',view:value.view||{}};
  }
  return {schema,defaults,point,reference,springReference,springConvention,legacySpringConvention,validate,evaluate,pack,unpack};
})();
