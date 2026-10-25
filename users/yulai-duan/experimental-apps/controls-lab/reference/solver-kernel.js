
/** General VSL planar kinematics. Embedded in v1-kinematics.html; open in a browser.
 * Inputs: positive pitch radii/link lengths in mm, angles in deg; open belts.
 * Outputs: unwrapped angles, local/global positions/displacements and belt geometry.
 * Limitations: ideal nonslip planar constraints, no contact/forces or manufacturing checks.
 */
const VSL = (() => {
  const rad = Math.PI / 180, tau = 2 * Math.PI;
  function inclination(horizontal,vertical) {if(Math.hypot(horizontal,vertical)<1e-9)return null;return Math.atan2(Math.abs(horizontal)<1e-9?0:horizontal,Math.abs(vertical)<1e-9?0:vertical)/rad;}
  const defaults = {L2:300,L3:300,ra:50,rb:25,rc:35,rd:35,re:25,rf:25,rw:100,alpha:0,phi0:0,te:100,tc:165};
  function ratios(p) { return {q23:p.L2/p.L3,qab:p.ra/p.rb,qdc:p.rd/p.rc,qfe:p.rf/p.re}; }
  function coefficient(p) {const q=ratios(p);return 1-q.qab+(1/q.qfe)*(q.qab-(1/q.qdc));}
  function raw(p,t) {
    const q=ratios(p),t3=p.phi0+(180-t)*(q.qab-1),a=t*rad,b=t3*rad;
    const B=[-p.L2*Math.cos(a),-p.L2*Math.sin(a)];
    return {B,P:[B[0]-p.L3*Math.cos(b),B[1]-p.L3*Math.sin(b)],t3};
  }
  function global(p,xy) {const a=p.alpha*rad;return [Math.cos(a)*xy[0]+Math.sin(a)*xy[1],-Math.sin(a)*xy[0]+Math.cos(a)*xy[1]];}
  function state(p,t) {
    const q=ratios(p),r=raw(p,t),e=raw(p,p.te),dt=t-p.te;
    const du=r.P[0]-e.P[0],dv=r.P[1]-e.P[1],[dy,dz]=global(p,[du,dv]);
    return {...r,t2:t,t4:0,t5:(1-(1/q.qdc))*dt,t6:coefficient(p)*dt,du,dv,dy,dz,gammaUV:inclination(du,dv),gammaYZ:inclination(dy,dz),Bg:global(p,r.B),Pg:global(p,r.P)};
  }
  function validate(p) {
    const errors=[];
    for(const k of ['L2','L3','ra','rb','rc','rd','re','rf','rw'])if(!Number.isFinite(p[k])||p[k]<=0)errors.push(`${k} must be finite and greater than zero.`);
    for(const k of ['alpha','phi0'])if(!Number.isFinite(p[k])||p[k]<0||p[k]>30)errors.push(`${k} must be between 0° and 30°.`);
    for(const k of ['te','tc'])if(!Number.isFinite(p[k])||p[k]<90||p[k]>270)errors.push(`${k} must be between 90° and 270°.`);
    if(p.te>p.tc)errors.push('Extension θ₂ᵉ must be less than or equal to compression θ₂ᶜ.');
    if(!errors.length)for(const t of [90,p.te,p.tc,180])if(Object.values(state(p,t)).some(v=>typeof v==='number'&&!Number.isFinite(v)))errors.push('These parameters exceed the numerical range.');
    return [...new Set(errors)];
  }
  function warnings(p) {
    const w=[];for(const [r,s,L,name] of [['ra','rb','L2','a–b'],['rc','rd','L2','c–d'],['re','rf','L3','e–f']])if(p[r]+p[s]>=p[L])w.push(`${name}: pulley pitch circles overlap or touch (${p[r]+p[s]} ≥ ${p[L]} mm). This belt stage is not physically feasible.`);
    if(p.te===p.tc)w.push('The working range is zero; animation and endpoint travel are stationary.');
    if(ratios(p).qab>15)w.push('Large q_ab: graphs and the displacement envelope use finite sampling; narrow features may be missed.');
    return w;
  }
  // Clockwise perimeter in a carrier frame: upper straight, right arc, lower straight, left arc.
  function belt(D,R,r) {
    if(!(D>R+r))return null;
    const beta=Math.acos((R-r)/D),n=[Math.cos(beta),Math.sin(beta)];
    const a=[R*n[0],R*n[1]],b=[D+r*n[0],r*n[1]],c=[D+r*n[0],-r*n[1]],d=[R*n[0],-R*n[1]];
    const straight=Math.hypot(b[0]-a[0],b[1]-a[1]),right=2*beta*r,left=(tau-2*beta)*R,total=2*straight+right+left;
    function at(s) {
      s=((s%total)+total)%total;
      if(s<straight){const f=s/straight;return [a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1])];}s-=straight;
      if(s<right){const t=beta-s/r;return [D+r*Math.cos(t),r*Math.sin(t)];}s-=right;
      if(s<straight){const f=s/straight;return [c[0]+f*(d[0]-c[0]),c[1]+f*(d[1]-c[1])];}s-=straight;
      const t=-beta-s/R;return [R*Math.cos(t),R*Math.sin(t)];
    }
    return {at,total,straight,right,left,beta};
  }
  function envelope(p) {
    const q=ratios(p),n=Math.min(12000,Math.max(1200,Math.ceil(Math.abs(q.qab-1)*(p.tc-p.te)*12))),out={};
    for(const k of ['du','dv','dy','dz'])out[k]={min:Infinity,max:-Infinity,h:state(p,p.tc)[k]};
    for(let i=0;i<=n;i++){const s=state(p,p.te+(p.tc-p.te)*i/n);for(const k in out){out[k].min=Math.min(out[k].min,s[k]);out[k].max=Math.max(out[k].max,s[k]);}}
    return {values:out,n};
  }
  return {rad,tau,defaults,ratios,coefficient,raw,global,state,validate,warnings,belt,envelope,inclination};
})();
