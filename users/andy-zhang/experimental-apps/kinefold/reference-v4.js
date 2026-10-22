/** Vendored Jon VSL V4 analytical reference. Load before model.js in the browser.
 * Inputs: mm, degrees, kg, N. Outputs: planar kinematics and quasi-static state.
 * Source blocks are unchanged; see reference.json. No hardware/contact validation.
 */

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


/** Ideal quasi-static VSL statics, embedded into v2-quasi-static.html.
 * Inputs: VSL geometry in mm/deg, masses kg, contact forces/preloads N.
 * Outputs: motor torques Nm, nonnegative span tensions N, pin reactions and FBDs.
 * No inertia/acceleration, friction, compliance, spring or rolling constraint.
 */
const VSLUnassisted = (() => {
const R=Math.PI/180;
const add=(...vs)=>vs.reduce((a,b)=>[a[0]+b[0],a[1]+b[1]],[0,0]);
const mul=(v,s)=>[v[0]*s,v[1]*s];
const sub=(a,b)=>add(a,mul(b,-1));
const cross=(a,b)=>a[0]*b[1]-a[1]*b[0];
const dot=(a,b)=>a[0]*b[0]+a[1]*b[1];
const norm=v=>Math.hypot(...v);
const local=(p,v)=>{const a=p.alpha*R;return [Math.cos(a)*v[0]-Math.sin(a)*v[1],Math.sin(a)*v[0]+Math.cos(a)*v[1]];};
const defaults={...VSL.defaults,m1:10,m2:0,m3:0,m5:0,m6:0,g:9.81,beta:0,Fn:98.1,Ft:0,Fy:0,Fz:98.1,loadMode:'nt',Tab0:0,Tcd0:0,Tef0:0};
function resolveLoads(p){const b=p.beta*R,s=Math.sin(b),c=Math.cos(b);return p.loadMode==='yz'?{...p,Fn:p.Fy*s+p.Fz*c,Ft:p.Fy*c-p.Fz*s}:{...p,loadMode:p.loadMode??'nt',Fy:p.Fn*s+p.Ft*c,Fz:p.Fn*c-p.Ft*s};}
function validate(p){const e=VSL.validate({...p,alpha:Math.min(p.alpha,30)});for(const k of ['m1','m2','m3','m5','m6','g','Tab0','Tcd0','Tef0'])if(!Number.isFinite(p[k])||p[k]<0)e.push(`${k} must be finite and nonnegative.`);for(const k of p.loadMode==='yz'?['Fy','Fz']:['Fn','Ft'])if(!Number.isFinite(p[k]))e.push(`${k} must be finite.`);if(p.loadMode!==undefined&&!['nt','yz'].includes(p.loadMode))e.push('Unknown driving force convention.');if(!Number.isFinite(p.beta)||p.beta<0||p.beta>90)e.push('β must be between 0° and 90°.');if(!Number.isFinite(p.alpha)||p.alpha<0||p.alpha>45)e.push('α must be between 0° and 45°.');return [...new Set(e)];}
function thetaSamples(p,lo,hi,n=240){return [...new Set([...Array.from({length:n+1},(_,i)=>lo+(hi-lo)*i/n),...[p.te,p.tc].filter(t=>t>=lo&&t<=hi)])].sort((a,b)=>a-b);}
function dzDomain(p,lo,hi,n=720){const values=thetaSamples(p,lo,hi,n).map(t=>VSL.state(p,t).dz);let min=Math.min(...values),max=Math.max(...values);if(max-min<1e-9){min-=.5;max+=.5;}return {min,max};}
// Root brackets retain all sampled branches; no monotonic inverse is assumed.
function posesAtDz(p,z,lo,hi,n=240){const ts=thetaSamples(p,lo,hi,n),roots=[],f=t=>VSL.state(p,t).dz-z,push=t=>{if(!roots.some(x=>Math.abs(x-t)<1e-6))roots.push(t);};for(let i=0;i<ts.length;i++){const fa=f(ts[i]);if(Math.abs(fa)<1e-7)push(ts[i]);if(i===0)continue;let a=ts[i-1],b=ts[i],va=f(a),vb=fa;if(va*vb<0){for(let j=0;j<45;j++){const mid=(a+b)/2,vm=f(mid);if(va*vm<=0){b=mid;vb=vm;}else{a=mid;va=vm;}}push((a+b)/2);}}return roots;}
// U is the geometrical upper strand in the standard folded pose.
// side=+1 on A→B (ab,cd), side=-1 on B→P (ef). Names stay on those sides.
function belt(O,C,r1,r2,side,delta,preload,name){
 const D=norm(sub(C,O));if(!(D>r1+r2))return null;
 const e=mul(sub(C,O),1/D),n=[-e[1],e[0]],k=(r1-r2)/D,h=Math.sqrt(1-k*k);
 const U=preload+Math.max(delta,0),L=preload+Math.max(-delta,0),spans=[];
 for(const [tag,sgn,T] of [['U',side,U],['L',-side,L]]){const normal=add(mul(e,k),mul(n,sgn*h)),dir=add(mul(e,h),mul(n,-sgn*k));spans.push({tag,T,normal,dir,left:{name:`T_${name},${tag}`,pos:add(O,mul(normal,r1)),vec:mul(dir,T)},right:{name:`T_${name},${tag}`,pos:add(C,mul(normal,r2)),vec:mul(dir,-T)}});}
 return {name,O,C,r1,r2,side,delta,U,L,extra:Math.abs(delta),active:Math.abs(delta)<1e-10?'balanced':delta>0?'U':'L',spans,Fleft:add(...spans.map(x=>x.left.vec)),Fright:add(...spans.map(x=>x.right.vec)),Mleft:-side*r1*delta/1000,Mright:side*r2*delta/1000};
}
function solve(p,t,detail=true){
 p=resolveLoads(p);
 const s=VSL.state(p,t),q=VSL.ratios(p),A=[0,0],B=s.B,Cwheel=s.P,l3=sub(Cwheel,B),C2=mul(B,.5),C3=add(B,mul(l3,.5));
 const weight=m=>local(p,[0,-m*p.g]),W1=weight(p.m1),W2=weight(p.m2),W3=weight(p.m3),W5=weight(p.m5),W6=weight(p.m6);
 const nb=[Math.sin(p.beta*R),Math.cos(p.beta*R)],tb=[Math.cos(p.beta*R),-Math.sin(p.beta*R)],FnG=mul(nb,p.Fn),FtG=mul(tb,p.Ft),FcontactG=add(FnG,FtG),Fcontact=local(p,FcontactG),Pcontact=add(Cwheel,local(p,mul(nb,-p.rw))),Mw=p.rw*p.Ft/1000;
 const ef=belt(B,Cwheel,p.re,p.rf,-1,p.rw*p.Ft/p.rf,p.Tef0,'ef');
 const cd=belt(A,B,p.rc,p.rd,1,-(p.re/p.rd)*(ef?.delta??0),p.Tcd0,'cd');
 if(!ef||!cd||p.ra+p.rb>=p.L2)return {valid:false,reason:'Overlapping pulley pitch circles: statics and FBDs are unavailable until each belt stage has centre distance greater than the sum of its radii.',...s,Fn:p.Fn,Ft:p.Ft,Fy:p.Fy,Fz:p.Fz};
 const Fw=add(Fcontact,W6,ef.Fright),M3=cross(l3,Fw)+cross(mul(l3,.5),W3);
 const ab=belt(A,B,p.ra,p.rb,1,-M3/p.rb,p.Tab0,'ab');
 const F32=add(Fw,W3,ab.Fright),F25=mul(add(cd.Fright,ef.Fleft,W5),-1),F12=mul(add(F32,mul(F25,-1),W2),-1),F14=mul(cd.Fleft,-1),F36=mul(Fw,-1);
 const tau2=-(cross(B,add(F32,mul(F25,-1)))+cross(C2,W2))/1000,tau4=p.rc*cd.delta/1000;
 const Fground=add(F12,F14,mul(ab.Fleft,-1),mul(W1,-1)),Mground=tau2+tau4+p.ra*ab.delta/1000;
 if(!detail)return {...s,valid:true,Fn:p.Fn,Ft:p.Ft,Fy:p.Fy,Fz:p.Fz,tau2,tau4,ab,cd,ef,Fw,F32,F25,F12,F14};
 const force=(name,pos,vec)=>({name,pos,vec});
 const bodies={
  2:{angle:s.t2,origin:A,ends:[A,B],forces:[force('F_12',A,F12),force('F_32',B,F32),force('F_52',B,mul(F25,-1)),force('W_2',C2,W2)],couples:[{name:'τ₂',pos:A,value:tau2}]},
  3:{angle:s.t3,origin:B,ends:[B,Cwheel],forces:[force('F_23',B,mul(F32,-1)),force('F_w',Cwheel,Fw),force('W_3',C3,W3),...ab.spans.map(x=>x.right)],couples:[]},
  4:{angle:s.t4,origin:A,ends:[A],radius:p.rc,forces:[force('F_14',A,F14),...cd.spans.map(x=>x.left)],couples:[{name:'τ₄',pos:A,value:tau4}]},
  5:{angle:s.t5,origin:B,ends:[B],radius:Math.max(p.rd,p.re),forces:[force('F_25',B,F25),force('W_5',B,W5),...cd.spans.map(x=>x.right),...ef.spans.map(x=>x.left)],couples:[]},
  6:{angle:s.t6,origin:Cwheel,ends:[Cwheel],radius:p.rw,forces:[force('F_36',Cwheel,F36),force('F_n',Pcontact,local(p,FnG)),force('F_t',Pcontact,local(p,FtG)),force('W_6',Cwheel,W6),...ef.spans.map(x=>x.right)],couples:[]}
 };
 let maxForce=0,maxMoment=0;
 for(const b of Object.values(bodies)){b.residualF=add(...b.forces.map(f=>f.vec));b.residualM=b.forces.reduce((m,f)=>m+cross(sub(f.pos,b.origin),f.vec)/1000,0)+b.couples.reduce((m,c)=>m+c.value,0);maxForce=Math.max(maxForce,norm(b.residualF));maxMoment=Math.max(maxMoment,Math.abs(b.residualM));}
 const dB=[p.L2*Math.sin(t*R),-p.L2*Math.cos(t*R)],d3=1-q.qab,dP=add(dB,[p.L3*Math.sin(s.t3*R)*d3,-p.L3*Math.cos(s.t3*R)*d3]);
 const gravityWork=dot(W2,mul(dB,.5))+dot(W3,mul(add(dB,dP),.5))+dot(W5,dB)+dot(W6,dP);
 const tau2VW=-(dot(Fcontact,dP)+gravityWork)/1000-Mw*VSL.coefficient(p),tau4VW=-Mw*(1/q.qdc)*(1/q.qfe);
 const mT=p.m1+p.m2+p.m3+p.m5+p.m6,inertia={I2:p.m2*(p.L2/1000)**2/12,I3:p.m3*(p.L3/1000)**2/12,I6:p.m6*(p.rw/1000)**2};
 return {...s,valid:true,A,C:Cwheel,P:Pcontact,Cg:s.Pg,Pg:VSL.global(p,Pcontact),C2,C3,Fn:p.Fn,Ft:p.Ft,Fy:p.Fy,Fz:p.Fz,Fcontact,FcontactG,FnG,FtG,Mw,tau2,tau4,tau2VW,tau4VW,Fw,F32,F25,F12,F14,F36,Fground,Mground,W1,W2,W3,W5,W6,ab,cd,ef,bodies,mT,inertia,maxForce,maxMoment,virtualWorkError:Math.max(Math.abs(tau2-tau2VW),Math.abs(tau4-tau4VW))};
}
return {defaults,validate,solve,belt,add,mul,sub,cross,dot,norm,local,resolveLoads,thetaSamples,dzDomain,posesAtDz};
})();

/** V4 constant-radius idler and remote linear tension spring.
 * Local u/v geometry mm, angles deg; p0 N at theta2=90; k N/mm. Derivatives
 * per radian. Clockwise wrap; automatic fixed exit direction over working travel.
 * Exact tangency and changing wrap are included; no cable elasticity/friction.
 */
const VSLSpring=(()=>{
 const R=Math.PI/180,TAU=2*Math.PI,EPS=1e-9;
 const defaults={"springEnabled":true,"springK":8,"hornR":62.22694951186731,"Sv":100,"rs":10,"p0":330.8692828089511,"nu":0,"Su":9.387776728149294};
 const totalMass=p=>p.m1+p.m2+p.m3+p.m5+p.m6;
 const target=p=>2*totalMass(p)*p.g*p.L2*Math.cos(p.alpha*R);
 function resolveDriven(p,key){if(key===null||key===undefined)return {...p};if(!['springK','hornR','Sv'].includes(key))throw Error('Unknown spring driven variable.');const other=['springK','hornR','Sv'].filter(k=>k!==key),den=p[other[0]]*p[other[1]];if(!(den>0)||!Number.isFinite(den))throw Error('The two undriven k / r_h / S_v values must have a positive finite product.');return {...p,[key]:target(p)/den};}
 function position(p,t){const phi=(t+p.nu)*R,D=[p.hornR*Math.cos(phi),p.hornR*Math.sin(phi)],v=[D[0]-p.Su,D[1]-p.Sv],d=Math.hypot(...v);return {phi,D,v,d};}
 // Continuous polar angle of the horn point relative to S on the 90–270° branch.
 function polar(p,z){const radius=Math.hypot(p.Su,p.Sv);if(radius<p.hornR)return z.phi+Math.atan2(p.Su*Math.sin(z.phi)-p.Sv*Math.cos(z.phi),p.hornR-p.Su*Math.cos(z.phi)-p.Sv*Math.sin(z.phi));const center=Math.atan2(-p.Sv,-p.Su),raw=Math.atan2(z.v[1],z.v[0]);return center+Math.atan2(Math.sin(raw-center),Math.cos(raw-center));}
 // Raw incoming tangent and continuous clockwise wrap relative to the old +u exit.
 function rawGeometry(p,t){
  const z=position(p,t),S=[p.Su,p.Sv];
  if(p.rs===0){const unit=z.d>EPS?[-z.v[0]/z.d,-z.v[1]/z.d]:[0,0];return {...z,valid:true,S,Q:S,unit,tangentLength:z.d,baseWrap:0,psi:0,derivative:z.D[1]*unit[0]-z.D[0]*unit[1]};}
  const ref=position(p,90);if(ref.d<=p.rs+EPS)return {...z,valid:false,reason:'The 90° preload reference is inside/on pulley S. Require |D(90°)−S| > r_s, or use r_s=0.'};
  if(z.d<=p.rs+EPS)return {...z,valid:false,reason:'Horn cable pin lies inside/on pulley S; no tangent cable exists at this pose.'};
  const psi=polar(p,z)-Math.acos(p.rs/z.d),psi0=polar(p,ref)-Math.acos(p.rs/ref.d),turns=Math.ceil((Math.PI/2-psi0-1e-12)/TAU),baseWrap=psi-Math.PI/2+turns*TAU,Q=[p.Su+p.rs*Math.cos(psi),p.Sv+p.rs*Math.sin(psi)],tangentLength=Math.sqrt(z.d*z.d-p.rs*p.rs),unit=[(Q[0]-z.D[0])/tangentLength,(Q[1]-z.D[1])/tangentLength];
  return {...z,valid:true,S,Q,unit,tangentLength,baseWrap,psi,derivative:z.D[1]*unit[0]-z.D[0]*unit[1]};
 }
 const exitCache=new Map();
 function exit(p){
  if(p.rs===0)return {valid:true,required:0,applied:0,direction:[1,0],out:[p.Su,p.Sv],minWrap:0,maxWrap:0};
  const key=JSON.stringify([p.hornR,p.Su,p.Sv,p.rs,p.nu,p.te,p.tc]);if(exitCache.has(key))return exitCache.get(key);
  // Wrap-angle extrema occur at endpoints or common-tangent configurations:
  // S dot [cos(phi),sin(phi)] = rh ± rs. candidates includes both roots exactly.
  const zs=candidates(p,p.te,p.tc).map(t=>rawGeometry(p,t)),bad=zs.find(z=>!z.valid);
  let result;if(bad)result={valid:false,reason:bad.reason};else{const rawMin=Math.min(...zs.map(z=>z.baseWrap)),rawMax=Math.max(...zs.map(z=>z.baseWrap)),turnShift=TAU*Math.floor((TAU-rawMax+1e-12)/TAU),min=rawMin+turnShift,max=rawMax+turnShift,required=-min,applied=Math.max(0,required),angle=Math.PI/2-applied,referenceWrap=rawGeometry(p,90).baseWrap+turnShift+applied;result=max+applied>TAU+1e-8?{valid:false,reason:'This range requires more than one full pulley wrap even after redirecting the exit. Reduce travel or change S / horn geometry.'}:{valid:true,required,applied,turnShift,direction:[Math.cos(applied),-Math.sin(applied)],out:[p.Su+p.rs*Math.cos(angle),p.Sv+p.rs*Math.sin(angle)],minWrap:min+applied,maxWrap:max+applied,referenceExtrapolated:referenceWrap < -1e-8||referenceWrap>TAU+1e-8};}
  if(exitCache.size>128)exitCache.clear();exitCache.set(key,result);return result;
 }
 function geometry(p,t){
  const z=rawGeometry(p,t);if(!z.valid)return z;const route=exit(p);if(!route.valid)return {...z,...route};
  const wrap=z.baseWrap+(route.turnShift??0)+route.applied;if(p.rs>0&&Math.abs(t-90)>1e-9&&(wrap < -1e-8||wrap>TAU+1e-8))return {...z,valid:false,reason:'Pose lies outside the wrap retained by the exit direction chosen for the working range.'};
  return {...z,...route,valid:true,wrap,zeta:route.required/R,zetaApplied:route.applied/R,payout:z.tangentLength+p.rs*wrap};
 }

 function roots(p,A,B,c,lo,hi){const mag=Math.hypot(A,B),out=[];if(mag<EPS||Math.abs(c)>mag+EPS)return out;const phase=Math.atan2(B,A),a=Math.acos(Math.max(-1,Math.min(1,c/mag)));for(const x of [phase+a,phase-a])for(let n=Math.ceil(((lo+p.nu)*R-x)/TAU);n<=Math.floor(((hi+p.nu)*R-x)/TAU);n++)out.push((x+n*TAU)/R-p.nu);return out;}
 function candidates(p,lo,hi){const rad=Math.hypot(p.Su,p.Sv);return [...new Set([lo,hi,...roots(p,-p.Sv,p.Su,p.rs,lo,hi),...roots(p,-p.Sv,p.Su,-p.rs,lo,hi),...roots(p,p.Su,p.Sv,rad,lo,hi),...roots(p,p.Su,p.Sv,-rad,lo,hi),...roots(p,p.Su,p.Sv,p.hornR-p.rs,lo,hi),...roots(p,p.Su,p.Sv,p.hornR+p.rs,lo,hi)])].sort((a,b)=>a-b);}
 function interval(p,lo,hi){const ts=candidates(p,lo,hi),zs=ts.map(t=>geometry(p,t)),bad=zs.find(z=>!z.valid);if(bad)return {valid:false,reason:bad.reason};let imin=0,imax=0;for(let i=1;i<zs.length;i++){if(zs[i].payout<zs[imin].payout)imin=i;if(zs[i].payout>zs[imax].payout)imax=i;}return {valid:true,min:zs[imin].payout,max:zs[imax].payout,minTheta:ts[imin],maxTheta:ts[imax],dmin:Math.min(...zs.map(z=>z.d)),dmax:Math.max(...zs.map(z=>z.d))};}
 function state(p,t){
  const z=geometry(p,t),ref=geometry(p,90);if(!z.valid||!ref.valid)return {...z,valid:false,reason:z.reason??ref.reason,force:null,tauS:null,supportRatio:null,Feq:null};
  const delta=z.payout-ref.payout,rawForce=p.p0+p.springK*delta,force=p.springEnabled?Math.max(0,rawForce):0;if(z.d<EPS&&force>0)return {...z,valid:false,reason:'Coincident point-pulley and horn pin have no force direction at this pose.',force:null,tauS:null,supportRatio:null,Feq:null};const Flocal=z.unit.map(v=>v*force),Fg=VSL.global(p,Flocal),tauS=-force*z.derivative/1000;
  const q=VSL.ratios(p),b=(p.phi0+(180-t)*(q.qab-1))*R,a=p.alpha*R,k=1-q.qab,du=p.L2*Math.sin(t*R)+p.L3*k*Math.sin(b),dv=-p.L2*Math.cos(t*R)-p.L3*k*Math.cos(b),Jz=-Math.sin(a)*du+Math.cos(a)*dv,Feq=Math.abs(Jz)>1e-7?-tauS/(Jz/1000):null,mg=totalMass(p)*p.g;
  const energy=!p.springEnabled?0:p.springK>0?force*force/(2*p.springK)/1000:p.p0*delta/1000;
  return {...z,referencePayout:ref.payout,delta,rawForce,force,Flocal,Fg,tauS,Jz,Feq,supportRatio:Feq!==null&&mg>0?Feq/mg:null,slack:force===0,energy,Dg:VSL.global(p,z.D),Qg:VSL.global(p,z.Q),Sg:VSL.global(p,z.S),outg:VSL.global(p,z.out),remote:distance=>[z.out[0]+z.direction[0]*distance,z.out[1]+z.direction[1]*distance],length:z.d};
 }
 function validate(p){const e=[];for(const k of Object.keys(defaults).filter(k=>k!=='springEnabled'))if(!Number.isFinite(p[k]))e.push(k+' must be finite.');if(!(p.hornR>0))e.push('r_h must be positive.');for(const k of ['springK','rs','p0'])if(p[k]<0)e.push(k+' must be nonnegative.');if(typeof p.springEnabled!=='boolean')e.push('Spring enabled must be boolean.');if(!e.length&&p.springEnabled){const ref=geometry(p,90);if(!ref.valid)e.push(ref.reason);else{const b=interval(p,p.te,p.tc);if(!b.valid)e.push(b.reason);}}return e;}
 function maximum(p,lo,hi){if(!p.springEnabled)return {valid:true,value:0,theta2:lo,error:0,converged:true};const b=interval(p,lo,hi),ref=geometry(p,90);if(!b.valid||!ref.valid)return {valid:false,reason:b.reason??ref.reason};const value=Math.max(0,p.p0+p.springK*(b.max-ref.payout));return {valid:true,value,theta2:b.maxTheta,error:0,converged:true};}
 // Bounds on interpolation of Fs*c' remain conservative across slack transitions.
 function interpolationBound(p,lo,hi){if(!p.springEnabled)return 0;const b=interval(p,lo,hi),ref=geometry(p,90);if(!b.valid||!ref.valid)return Infinity;const Fmax=Math.max(0,p.p0+p.springK*(b.max-ref.payout));if(Fmax===0)return 0;const r=p.hornR,span=(hi-lo)*R,tan=Math.sqrt(Math.max(b.dmin*b.dmin-p.rs*p.rs,1e-20)),l2=r+r*r/tan,l3=r+3*r*r/tan+b.dmax*r*r*r/(tan*tan*tan)+2*r*r*r/(tan*tan),L=(p.springK*r*r+Fmax*l2)/1000,M=(3*p.springK*r*l2+Fmax*l3)/1000;return p.p0+p.springK*(b.min-ref.payout)>=0?Math.min(L*span/2,M*span*span/8):L*span/2;}
 return {defaults,totalMass,target,resolveDriven,position,geometry,rawGeometry,exit,interval,state,validate,maximum,interpolationBound,candidates};
})();
const VSLStatic=(()=>{
 const base=VSLUnassisted,defaults={...base.defaults,...VSLSpring.defaults,te:100,tc:165,loadMode:'yz',m1:8.75,rw:200,Fn:85.8375,Fz:85.8375};
 function solve(p,t,detail=true){
  const s=base.solve(p,t,detail),spring=VSLSpring.state(p,t);if(!s.valid)return {...s,spring};if(!spring.valid&&p.springEnabled)return {...s,spring,valid:false,reason:spring.reason};
  const Fs=spring.valid?spring.force:0,tauG=-s.tau2,tauS=spring.valid?spring.tauS:0,tau2=-tauG-tauS,tau2Applied=tau2,Fspring=spring.valid?spring.Flocal:[0,0],D=VSLSpring.position(p,t).D,F12=base.sub(s.F12,Fspring);
  if(!detail)return {...s,spring,tauG,tauS,tau2,tau2Applied,F12,Fs};
  const b=s.bodies[2];b.forces[0].vec=F12;b.forces.push({name:'F_s',pos:D,vec:Fspring});b.couples[0]={name:'τ₂ motor',pos:s.A,value:tau2Applied};
  b.residualF=base.add(...b.forces.map(f=>f.vec));b.residualM=b.forces.reduce((m,f)=>m+base.cross(base.sub(f.pos,b.origin),f.vec)/1000,0)+tau2Applied;
  const tau2VW=s.tau2VW-tauS,virtualWorkError=Math.max(Math.abs(tau2-tau2VW),Math.abs(s.tau4-s.tau4VW));
  const Fpulley=spring.valid?[Fs*spring.direction[0]-Fspring[0],Fs*spring.direction[1]-Fspring[1]]:[0,0],FspringAnchor=spring.valid?spring.direction.map(v=>-Fs*v):[0,0];
  return {...s,spring,Fs,tauG,tauS,tau2,tau2Applied,tau2VW,F12,Fspring,D,Fpulley,FspringAnchor,maxForce:Math.max(s.maxForce,base.norm(b.residualF)),maxMoment:Math.max(s.maxMoment,Math.abs(b.residualM)),virtualWorkError};
 }
 const percent=(torque,gravity)=>Number.isFinite(torque)&&Number.isFinite(gravity)&&Math.abs(gravity)>1e-9?100*torque/Math.abs(gravity):null;
 const compensationPercent=s=>Number.isFinite(s?.spring?.supportRatio)?100*(s.spring.supportRatio-1):null;
 const forceMemory={yz:[0,1],nt:[1,0]};
 function followMass(previous,next){const old=VSLSpring.totalMass(previous)*previous.g,weight=VSLSpring.totalMass(next)*next.g,mode=previous.loadMode,keys=mode==='yz'?['Fy','Fz']:['Fn','Ft'];if(old>0)forceMemory[mode]=keys.map(k=>previous[k]/old);if(weight!==old){next={...next};keys.forEach((k,i)=>next[k]=forceMemory[mode][i]*weight);}return next;}
 return {...base,defaults,solve,percent,compensationPercent,followMass,validate:p=>[...base.validate(p),...VSLSpring.validate(p)]};
})();
const VSLDomains=(()=>{
 function padded(min,max,lo=-Infinity,hi=Infinity){return max-min>1e-9?{min,max}:{min:Math.max(lo,min-.5),max:Math.min(hi,max+.5)};}
 function theta(p,expanded=false,clamp=true){return clamp?padded(p.te,p.tc,90,270):{min:90,max:expanded?270:180};}
 function axis(p,ranges,key,expanded=false,clamp=true){const t=theta(p,expanded,clamp);if(key==='t2')return t;if(key==='dz')return VSLStatic.dzDomain(p,t.min,t.max);if(clamp)return padded(ranges[key].min,ranges[key].max,0,key==='beta'?90:45);return {min:0,max:key==='beta'?90:45};}
 return {theta,axis,padded};
})();

/** Bounded numerical 1mg fit. Holds k,Sv,rs,nu and leg geometry; solves Su,rh,p0.
 * mm/N/deg. Eliminates p0 with affine Chebyshev interval feasibility, then
 * multistart 2D Nelder-Mead; sampled validation, not a global/exactness proof.
 */
const VSLLegacySupportFit=(()=>{
 function fit(p,{samples=181,iterations=230,verification=6501}={}){
  const mg=VSLSpring.totalMass(p)*p.g,h=p.Sv,r0=VSLSpring.target(p)/(p.springK*h);
  if(!(mg>0&&p.springK>0&&h>0&&r0>0)||p.tc<=p.te)return {valid:false,reason:'Fit requires positive total weight, k, Sv, nominal horn size and a nonzero operating range.'};
  const bounds={Su:{min:-Math.max(.6*h,3*p.rs),max:Math.max(.6*h,3*p.rs)},hornR:{min:Math.max(.1,.2*r0),max:Math.max(1.9*r0,1.8*h)},p0:{min:0,max:20*mg+8*p.springK*p.rs}},ts=Array.from({length:samples},(_,i)=>p.te+(p.tc-p.te)*i/(samples-1));
  let evaluations=0;
  function profile(v){
   evaluations++;const Su=v[0]*h,hornR=v[1]*r0;
   if(Su<bounds.Su.min||Su>bounds.Su.max||hornR<bounds.hornR.min||hornR>bounds.hornR.max)return {score:1e6};
   const a={...p,Su,hornR,p0:0,springEnabled:true},ref=VSLSpring.geometry(a,90),window=VSLSpring.interval(a,p.te,p.tc);if(!ref.valid||!window.valid)return {score:1e6};
   let pmin=Math.max(0,-p.springK*(window.min-ref.payout)),pmax=bounds.p0.max;const rows=[];
   if(pmin>pmax)return {score:1e6};
   for(const t of ts){const z=VSLSpring.state(a,t),A=z.derivative/(z.Jz*mg);if(!z.valid||!Number.isFinite(A)||A<=0||Math.abs(z.Jz)<1e-7)return {score:1e6};rows.push([A,A*p.springK*z.delta-1]);}
   const feasible=error=>{let lo=pmin,hi=pmax;for(const [A,B] of rows){lo=Math.max(lo,(-error-B)/A);hi=Math.min(hi,(error-B)/A);if(lo>hi)return null;}return [lo,hi];};
   let lo=0,hi=Math.max(...rows.map(([A,B])=>Math.abs(A*pmin+B)));for(let i=0;i<43;i++){const mid=(lo+hi)/2;if(feasible(mid))hi=mid;else lo=mid;}
   const range=feasible(hi*(1+1e-12)+1e-14);if(!range)return {score:1e6};const p0=(range[0]+range[1])/2;
   return {score:Math.max(...rows.map(([A,B])=>Math.abs(A*p0+B))),Su,hornR,p0};
  }
  function search(start){let points=[start,[start[0]+.025,start[1]],[start[0],start[1]+.025]].map(v=>({v,z:profile(v)}));
   for(let i=0;i<iterations;i++){
    points.sort((a,b)=>a.z.score-b.z.score);const [a,b,c]=points,center=a.v.map((x,j)=>(x+b.v[j])/2),at=v=>({v,z:profile(v)}),reflect=at(center.map((x,j)=>2*x-c.v[j]));
    if(reflect.z.score<a.z.score){const expand=at(center.map((x,j)=>3*x-2*c.v[j]));points[2]=expand.z.score<reflect.z.score?expand:reflect;}
    else if(reflect.z.score<b.z.score)points[2]=reflect;
    else{const outside=reflect.z.score<c.z.score,target=outside?reflect:c,contract=at(center.map((x,j)=>(x+target.v[j])/2));if(contract.z.score<target.z.score)points[2]=contract;else points=[a,...[b,c].map(q=>at(q.v.map((x,j)=>(x+a.v[j])/2)))];}
    if(i>40&&Math.max(...points.flatMap(q=>q.v.map((x,j)=>Math.abs(x-points[0].v[j]))))<1e-10)break;
   }return points.sort((a,b)=>a.z.score-b.z.score)[0];
  }
  const seeds=[[p.Su/h,p.hornR/r0],[.07,.9],[0,.8],[.2,1],[.3,1.2]],results=seeds.map(search).filter(x=>x.z.score<1e5);if(!results.length)return {valid:false,reason:'No valid taut route found within fitting bounds; change k, Sv, rs, nu or travel.'};
  const best=results.sort((a,b)=>a.z.score-b.z.score)[0].z,next={...p,Su:best.Su,hornR:best.hornR,p0:best.p0,springEnabled:true};let maxError=0,maxTorque=0;
  for(let i=0;i<verification;i++){const t=p.te+(p.tc-p.te)*i/(verification-1),s=VSLStatic.solve(next,t,false);if(!s.valid||s.spring.supportRatio===null)return {valid:false,reason:'Fitted route failed full-model verification.'};maxError=Math.max(maxError,Math.abs(s.spring.supportRatio-1));maxTorque=Math.max(maxTorque,Math.abs(s.tau2));}
  return {valid:true,parameters:next,maxError,maxTorque,bounds,evaluations,samples,verification,method:'bounded sampled multistart fit; not a global optimum certificate'};
 }
 return {fit};
})();
/** Flexible bounded minimax fit of physical Link-2 motor torque.
 * Inputs mm/deg/kg/N/Nm; checked driving variables are held, unchecked fitted.
 * Linear k/p0 are solved by interval/polygon Chebyshev feasibility; geometry
 * uses multistart bounded Nelder-Mead. Dense verification is sampled evidence,
 * not a global optimum certificate or hardware validation.
 */
const VSLFit=(()=>{
 const keys=['springK','hornR','Sv','rs','p0','nu','Su'],defaults={springK:true,hornR:false,Sv:true,rs:true,p0:false,nu:true,Su:false},labels={springK:'k',hornR:'r_h',Sv:'S_v',rs:'r_s',p0:'p₀',nu:'ν',Su:'S_u'};
 function normalize(value){const result={...defaults};if(value!==undefined&&value!==null){for(const key of keys){if(value[key]!==undefined&&typeof value[key]!=='boolean')throw Error('Driving selections must be true or false.');if(value[key]!==undefined)result[key]=value[key];}}return result;}
 const clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
 function boundsFor(p){const h=Math.max(10,Math.abs(p.Sv),p.hornR,3*p.rs),mg=VSLSpring.totalMass(p)*p.g,nominal=p.hornR*Math.abs(p.Sv)>0?Math.abs(VSLSpring.target(p)/(p.hornR*p.Sv)):0;return {springK:{min:0,max:Math.max(1,4*p.springK,4*nominal)},hornR:{min:.1,max:Math.max(2*h,2*p.hornR)},Sv:{min:.1,max:Math.max(3*h,2*p.Sv)},rs:{min:0,max:Math.max(.6*h,3*p.rs)},p0:{min:0,max:Math.max(100,4*p.p0,20*mg,8*p.springK*p.rs)},nu:{min:p.nu-90,max:p.nu+90},Su:{min:p.Su-Math.max(.75*h,3*p.rs),max:p.Su+Math.max(.75*h,3*p.rs)}};}
 // Convex polygon clipped by a*x+b*y <= c. Degenerate feasible sets retained.
 function clip(poly,a,b,c){if(!poly.length)return [];const out=[];let prev=poly.at(-1),fp=a*prev[0]+b*prev[1]-c;for(const at of poly){const f=a*at[0]+b*at[1]-c,inside=f<=1e-11,before=fp<=1e-11;if(inside!==before){const u=fp/(fp-f);out.push([prev[0]+u*(at[0]-prev[0]),prev[1]+u*(at[1]-prev[1])]);}if(inside)out.push(at);prev=at;fp=f;}return out;}
 function linearFit(rows,p,free,bounds){
  const linear=['springK','p0'].filter(k=>free.includes(k));
  const score=(k,p0)=>Math.max(...rows.map(z=>Math.abs(z.base+z.a*Math.max(0,p0+k*z.delta))));
  if(!linear.length)return {springK:p.springK,p0:p.p0,score:score(p.springK,p.p0)};
  if(linear.length===1){
   const key=linear[0];let low=bounds[key].min,high=bounds[key].max;const list=[];
   for(const z of rows){const A=key==='p0'?1:z.delta,B=key==='p0'?p.springK*z.delta:p.p0;if(A>0)low=Math.max(low,-B/A);else if(A<0)high=Math.min(high,-B/A);else if(B<0)return null;list.push([z.a*A,z.base+z.a*B]);}
   if(low>high)return null;
   function feasible(error){let lo=low,hi=high;for(const [A,B] of list){if(Math.abs(A)<1e-16){if(Math.abs(B)>error+1e-10)return null;}else{const a=(-error-B)/A,b=(error-B)/A;lo=Math.max(lo,Math.min(a,b));hi=Math.min(hi,Math.max(a,b));if(lo>hi+1e-12)return null;}}return [lo,hi];}
   const initial=clamp(p[key],low,high);let lo=0,hi=Math.max(...list.map(([A,B])=>Math.abs(A*initial+B)));
   for(let i=0;i<36;i++){const mid=(lo+hi)/2;if(feasible(mid))hi=mid;else lo=mid;}
   const interval=feasible(hi+1e-10);if(!interval)return null;const value=(interval[0]+interval[1])/2,k=key==='springK'?value:p.springK,p0=key==='p0'?value:p.p0;
   return {springK:k,p0,score:score(k,p0)};
  }
  let initial=[[bounds.springK.min,bounds.p0.min],[bounds.springK.max,bounds.p0.min],[bounds.springK.max,bounds.p0.max],[bounds.springK.min,bounds.p0.max]];
  for(const z of rows){initial=clip(initial,-z.delta,-1,0);if(!initial.length)return null;}
  const center=poly=>[0,1].map(j=>poly.reduce((sum,z)=>sum+z[j],0)/poly.length),point=center(initial);
  const feasible=error=>{let poly=initial;for(const z of rows){poly=clip(poly,z.a*z.delta,z.a,error-z.base);if(!poly.length)return null;poly=clip(poly,-z.a*z.delta,-z.a,error+z.base);if(!poly.length)return null;}return poly;};
  let lo=0,hi=score(...point);for(let i=0;i<36;i++){const mid=(lo+hi)/2;if(feasible(mid))hi=mid;else lo=mid;}
  const poly=feasible(hi+1e-9);if(!poly)return null;const [springK,p0]=center(poly);return {springK,p0,score:score(springK,p0)};
 }
 function fit(p,{driving=defaults,samples=181,iterations=240,verification=6501,starts=6,progress=()=>{}}={}){
  driving=normalize(driving);const free=keys.filter(k=>!driving[k]),geom=free.filter(k=>!['springK','p0'].includes(k)),bounds=boundsFor(p),bad=VSLUnassisted.validate(p);
  if(bad.length)return {valid:false,reason:bad.join(' ')};
  if(!p.springEnabled)return {valid:false,reason:'Enable spring assistance before fitting.'};
  if(keys.some(k=>!Number.isFinite(p[k])))return {valid:false,reason:'Enter finite spring inputs.'};
  if(['springK','rs','p0'].some(k=>driving[k]&&p[k]<0)||driving.hornR&&p.hornR<=0)return {valid:false,reason:'Held k, r_s and p₀ must be nonnegative; held r_h must be positive.'};
  if(p.tc<=p.te)return {valid:false,reason:'Fit requires a nonzero working θ₂ range.'};
  samples=Math.max(11,Math.floor(samples));verification=Math.max(samples,Math.floor(verification));
  const ts=Array.from({length:samples},(_,i)=>p.te+(p.tc-p.te)*i/(samples-1)),base=ts.map(t=>VSLUnassisted.solve(p,t,false).tau2);
  let evaluations=0;
  const encode=a=>geom.map(k=>clamp((a[k]-bounds[k].min)/(bounds[k].max-bounds[k].min),0,1)),decode=v=>Object.fromEntries(geom.map((k,i)=>[k,bounds[k].min+clamp(v[i],0,1)*(bounds[k].max-bounds[k].min)]));
  function profile(v){evaluations++;const candidate={...p,...decode(v)},ref=VSLSpring.geometry(candidate,90),window=VSLSpring.interval(candidate,p.te,p.tc);if(!ref.valid||!window.valid)return {score:1e100};const rows=[];
   for(let i=0;i<ts.length;i++){const g=VSLSpring.geometry(candidate,ts[i]);if(!g.valid)return {score:1e100};rows.push({base:base[i],a:g.derivative/1000,delta:g.payout-ref.payout});}
   rows.push({base:0,a:0,delta:window.min-ref.payout},{base:0,a:0,delta:window.max-ref.payout});
   const linear=linearFit(rows,candidate,free,bounds);return linear?{...linear,parameters:{...candidate,springK:linear.springK,p0:linear.p0}}:{score:1e100};
  }
  const evaluate=v=>{v=v.map(x=>clamp(x,0,1));return {v,z:profile(v)};};
  function search(seed){if(!geom.length)return evaluate([]);const first=evaluate(seed);if(first.z.score<1e-9)return first;let simplex=[first,...geom.map((_,i)=>evaluate(seed.map((x,j)=>j===i?x+(x>.94?-.035:.035):x)))];
   for(let step=0;step<iterations;step++){simplex.sort((a,b)=>a.z.score-b.z.score);const best=simplex[0],worst=simplex.at(-1),center=geom.map((_,j)=>simplex.slice(0,-1).reduce((sum,z)=>sum+z.v[j],0)/geom.length),reflect=evaluate(center.map((x,j)=>2*x-worst.v[j]));
    if(reflect.z.score<best.z.score){const expand=evaluate(center.map((x,j)=>3*x-2*worst.v[j]));simplex[simplex.length-1]=expand.z.score<reflect.z.score?expand:reflect;}
    else if(reflect.z.score<simplex.at(-2).z.score)simplex[simplex.length-1]=reflect;
    else{const outside=reflect.z.score<worst.z.score,target=outside?reflect:worst,contract=evaluate(center.map((x,j)=>(x+target.v[j])/2));if(contract.z.score<target.z.score)simplex[simplex.length-1]=contract;else simplex=[best,...simplex.slice(1).map(z=>evaluate(z.v.map((x,j)=>(x+best.v[j])/2)))];}
    if(step>35&&simplex[0].z.score<1e99&&Math.max(...simplex.flatMap(z=>z.v.map((x,j)=>Math.abs(x-simplex[0].v[j]))))<1e-9)break;
   }return simplex.sort((a,b)=>a.z.score-b.z.score)[0];
  }
  const target=p.springK>0&&p.Sv>0?VSLSpring.target(p)/(p.springK*p.Sv):p.hornR;
  const pointSeed={...p,Su:0,rs:0,nu:0,hornR:target},candidateSeeds=[p,{...p,Su:p.rs,hornR:.97*target},{...p,Su:.7*p.rs,hornR:.9*target},pointSeed,{...p,Su:0,hornR:.8*target},{...p,Su:1.3*p.rs,hornR:1.1*target}];
  if(free.includes('rs')&&free.includes('Su')&&(free.includes('nu')||p.nu===0))candidateSeeds.unshift(pointSeed);
  const seeds=[...new Map(candidateSeeds.map(a=>{const v=encode(a);return [JSON.stringify(v),v];})).values()].slice(0,Math.max(1,starts));
  let best=null;for(let i=0;i<seeds.length;i++){const found=search(seeds[i]);if(!best||found.z.score<best.z.score)best=found;progress({completed:i+1,total:seeds.length});if(best.z.score<1e-9)break;}
  // Keep a valid current point if a limited search fails to improve it.
  const original=profile(encode(p));if(!best||original.score<best.z.score)best={v:encode(p),z:original};
  if(!best.z.parameters||best.z.score>1e99)return {valid:false,reason:'No valid route/taut spring found within fitting bounds. Free more variables or adjust the starting geometry.'};
  const next=best.z.parameters;for(const key of keys)if(driving[key])next[key]=p[key];
  let maxTorque=0,peakTheta=p.te,maxError=0,minForce=Infinity;
  for(let i=0;i<verification;i++){const theta=p.te+(p.tc-p.te)*i/(verification-1),s=VSLStatic.solve(next,theta,false);if(!s.valid)return {valid:false,reason:'Candidate failed dense geometry verification.'};if(Math.abs(s.tau2)>maxTorque){maxTorque=Math.abs(s.tau2);peakTheta=theta;}if(Number.isFinite(s.spring.supportRatio))maxError=Math.max(maxError,Math.abs(s.spring.supportRatio-1));minForce=Math.min(minForce,s.Fs);}
  const warnings=[];if(!free.length)warnings.push('No driven variables selected; current design evaluated without fitting.');else if(free.length<3)warnings.push('Too few variables left driven; the solution may not be ideal.');if(!(VSLSpring.totalMass(p)*p.g>0))warnings.push('Zero total weight: 1mg compensation is undefined; fitting current loads only.');
  const limited=free.filter(k=>Math.abs(next[k]-bounds[k].min)<=1e-5*Math.max(1,bounds[k].max-bounds[k].min)||Math.abs(next[k]-bounds[k].max)<=1e-5*Math.max(1,bounds[k].max-bounds[k].min));if(limited.length)warnings.push('At numerical search bound: '+limited.map(k=>labels[k]).join(', ')+'.');
  if(next.rs<1e-5)warnings.push('Zero-radius point-pulley limit; a physical pulley needs positive radius.');if(minForce<1e-7)warnings.push('The spring reaches zero tension.');if(maxTorque>best.z.score+1e-4)warnings.push('Dense check found a larger between-sample peak.');
  return {valid:true,parameters:next,driving,free,maxTorque,peakTheta,maxError,sampledObjective:best.z.score,bounds,evaluations,samples,verification,warnings,method:'bounded sampled minimax |tau2| at current loads; no global optimum certificate'};
 }
 return {keys,defaults,labels,normalize,boundsFor,fit,fitSupport:VSLLegacySupportFit.fit};
})();




/** Global headline extrema over the closed theta2 × alpha × beta box.
 * Units: mm/deg/kg/N/Nm. Embedded standalone; no dynamics. Alpha/beta extrema
 * are analytic sinusoid candidates; theta branch-and-bound uses conservative
 * second-derivative bounds. Returns attained value/pose and remaining error gap.
 */
const VSLPeaks=(()=>{
 const R=Math.PI/180,TAU=2*Math.PI;
 function stationary(c,s,lo,hi){const points=[lo,hi],phase=Math.atan2(s,c);if(Math.hypot(c,s)>0)for(let k=Math.ceil((lo-phase)/Math.PI);k<=Math.floor((hi-phase)/Math.PI);k++)points.push(phase+k*Math.PI);return points;}
 function unassistedCoefficients(p,theta){
  const q=VSL.ratios(p),k=1-q.qab,t=theta*R,t3=(p.phi0+(180-theta)*(q.qab-1))*R;
  const bu=p.L2*Math.sin(t),bv=-p.L2*Math.cos(t),cu=bu+p.L3*k*Math.sin(t3),cv=bv-p.L3*k*Math.cos(t3),lu=-p.L3*Math.cos(t3),lv=-p.L3*Math.sin(t3),a=.5*p.m2+.5*p.m3+p.m5,b=.5*p.m3+p.m6,Gu=p.g*(a*bu+b*cu),Gv=p.g*(a*bv+b*cv),mg=p.g*(p.m6+.5*p.m3),K=VSL.coefficient(p),h=(p.re-p.rf)*p.rw/(p.rf*p.rb);
  const raw=VSL.raw(p,theta),ext=VSL.raw(p,p.te),dz={kind:'separable',c:0,G:raw.P[1]-ext.P[1],H:-(raw.P[0]-ext.P[0]),A:0,B:0};
  if(p.loadMode==='yz')return {
   tau2:{kind:'separable',c:0,G:(Gv-p.Fy*cu-p.Fz*cv)/1000,H:(-Gu+p.Fz*cu-p.Fy*cv)/1000,A:-p.rw*K*p.Fy/1000,B:p.rw*K*p.Fz/1000},
   tau4:{kind:'separable',c:0,G:0,H:0,A:-p.rw*(1/q.qdc)*(1/q.qfe)*p.Fy/1000,B:p.rw*(1/q.qdc)*(1/q.qfe)*p.Fz/1000},
   ab:{kind:'separable',c:0,G:(mg*lu-lu*p.Fz+lv*p.Fy)/p.rb,H:(mg*lv-lu*p.Fy-lv*p.Fz)/p.rb,A:h*p.Fy,B:-h*p.Fz},dz
  };
  return {
   tau2:{kind:'coupled',c:-p.rw*p.Ft*K/1000,A:-(p.Ft*cu+p.Fn*cv)/1000,B:-(p.Fn*cu-p.Ft*cv)/1000,G:Gv/1000,H:-Gu/1000},
   tau4:{kind:'separable',c:-p.rw*p.Ft*(1/q.qdc)*(1/q.qfe)/1000,A:0,B:0,G:0,H:0},
   ab:{kind:'coupled',c:h*p.Ft,A:-(lu*p.Fn-lv*p.Ft)/p.rb,B:(lu*p.Ft+lv*p.Fn)/p.rb,G:mg*lu/p.rb,H:mg*lv/p.rb},dz
  };
 }
 function coefficients(p,theta){
  const f=unassistedCoefficients(p,theta),v=f.tau2;
  f.tau2={...v,c:v.c-VSLSpring.state(p,theta).tauS};
  return f;
 }
 function value(f,a,b){return f.c+f.G*Math.cos(a)+f.H*Math.sin(a)+f.A*Math.cos(f.kind==='coupled'?b-a:b)+f.B*Math.sin(f.kind==='coupled'?b-a:b);}
 function angularPeak(f,ar,br){
  const al=ar.min*R,ah=ar.max*R,bl=br.min*R,bh=br.max*R;let best=null;
  const visit=(a,b)=>{const v=value(f,a,b);if(!best||Math.abs(v)>best.score)best={value:v,score:Math.abs(v),alpha:a/R,beta:b/R};};
  if(f.kind==='separable')for(const a of stationary(f.G,f.H,al,ah))for(const b of stationary(f.A,f.B,bl,bh))visit(a,b);
  else{
   for(const b of [bl,bh])for(const a of stationary(f.G+f.A*Math.cos(b)+f.B*Math.sin(b),f.H+f.A*Math.sin(b)-f.B*Math.cos(b),al,ah))visit(a,b);
   for(const a of [al,ah])for(const b of stationary(f.A*Math.cos(a)-f.B*Math.sin(a),f.A*Math.sin(a)+f.B*Math.cos(a),bl,bh))visit(a,b);
   for(const a of stationary(f.G,f.H,al,ah))for(const d of stationary(f.A,f.B,bl-a,bh-a))visit(a,a+d);
  }
  return best;
 }
 function curvature(p){const k=Math.abs(1-VSL.ratios(p).qab),F=Math.hypot(...(p.loadMode==='yz'?[p.Fy,p.Fz]:[p.Fn,p.Ft])),a=.5*p.m2+.5*p.m3+p.m5,b=.5*p.m3+p.m6;return {tau2:(F*(p.L2+p.L3*k**3)+p.g*((a+b)*p.L2+b*p.L3*k**3))/1000,tau4:0,ab:p.L3*k*k*(F+p.g*(p.m6+.5*p.m3))/p.rb,dz:p.L2+p.L3*k*k};}
 function calculate(p,ranges,{tolerance=.001,maxIterations=20000}={}){
  if(VSLStatic.validate(p).length||!VSLStatic.solve(p,p.te,false).valid)return {valid:false};
  if(!(tolerance>0)||!Number.isFinite(tolerance)||!Number.isInteger(maxIterations)||maxIterations<0)throw Error('Invalid extrema search settings.');
  for(const [axis,limit] of [['alpha',45],['beta',90]]){const b=ranges[axis];if(!b||!Number.isFinite(b.min)||!Number.isFinite(b.max)||b.min<0||b.max>limit||b.min>b.max)throw Error('Invalid '+axis+' search bounds.');}
  if(p.springEnabled&&ranges.alpha.min!==ranges.alpha.max)throw Error('V4 headline extrema require fixed alpha.');
  const M=curvature(p),result={valid:true,tolerance,bounds:{theta2:{min:p.te,max:p.tc},alpha:{...ranges.alpha},beta:{...ranges.beta}},evaluations:0};
  for(const key of ['tau2','tau4','ab','dz']){
   const evaluate=theta=>{result.evaluations++;return {...angularPeak(coefficients(p,theta)[key],ranges.alpha,ranges.beta),theta2:theta};};
   const left=evaluate(p.te),right=evaluate(p.tc);let best=left.score>=right.score?left:right,iterations=0;const heap=[];
   const upper=(a,b)=>Math.max(a.score,b.score)+M[key]*((b.theta2-a.theta2)*R)**2/8+(key==='tau2'?VSLSpring.interpolationBound(p,a.theta2,b.theta2):0)+32*Number.EPSILON*Math.max(1,a.score,b.score);
   const push=(a,b)=>{const node={a,b,upper:upper(a,b)};if(node.upper<=best.score)return;heap.push(node);let i=heap.length-1;while(i>0){const j=(i-1)>>1;if(heap[j].upper>=node.upper)break;heap[i]=heap[j];i=j;}heap[i]=node;};
   const pop=()=>{const root=heap[0],end=heap.pop();if(heap.length){let i=0;while(2*i+1<heap.length){let j=2*i+1;if(j+1<heap.length&&heap[j+1].upper>heap[j].upper)j++;if(heap[j].upper<=end.upper)break;heap[i]=heap[j];i=j;}heap[i]=end;}return root;};
   if(p.tc>p.te&&(M[key]>0||(key==='tau2'&&p.springEnabled)))push(left,right);
   while(heap.length&&heap[0].upper-best.score>tolerance&&iterations<maxIterations){const node=pop(),mid=evaluate((node.a.theta2+node.b.theta2)/2);if(mid.score>best.score)best=mid;push(node.a,mid);push(mid,node.b);iterations++;}
   const error=Math.max(0,(heap[0]?.upper??best.score)-best.score),signedValue=best.value;
   result[key]={...best,signedValue,value:key==='ab'?p.Tab0+best.score:key==='dz'?best.score:signedValue,active:key==='ab'?(Math.abs(signedValue)<1e-10?'balanced':signedValue>0?'U':'L'):null,error,converged:error<=tolerance,iterations};
  }
  result.Fs=VSLSpring.maximum(p,p.te,p.tc);
  return result;
 }
 function fixedAlpha(p,ranges,options){return calculate(p,{alpha:{min:p.alpha,max:p.alpha},beta:ranges.beta},options);}
 return {coefficients,value,angularPeak,curvature,calculate,fixedAlpha};
})();


globalThis.KinefoldV4 = {VSL,VSLUnassisted,VSLSpring,VSLStatic};
