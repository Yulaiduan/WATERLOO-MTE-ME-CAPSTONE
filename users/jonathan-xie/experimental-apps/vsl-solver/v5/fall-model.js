/** Vertical point-mass fall catch for VSL V5. Browser/Node, no dependencies.
 * Inputs: V4 geometry mm/deg, total mass kg, g m/s2, fall height m.
 * Output: signed Link2 torque Nm, upward az/g, ground Fz N, vz m/s, dz mm,
 * touchdown-relative time s, feasibility and sampled alpha peaks.
 * Assumes massless rigid links, fixed pitch, beta0, ideal motor/cable and contact.
 * Constant-braking energy bound is a minimum peak only when its full path exists.
 */
function VSLFallModel(){
 const R=Math.PI/180;
 const mass=p=>VSLSpring.totalMass(p);
 function solve(input,heightM,options={}){
  const p={...input,beta:0},m=mass(p),g=p.g,n=Math.max(80,Math.floor(options.samples??800)),Q=(p.tc-p.te)*R;
  const invalid=(reason,extra={})=>({valid:false,reason,rows:[],warnings:[],heightM,massKg:m,impactSpeed:Number.isFinite(g*heightM)&&g*heightM>=0?Math.sqrt(2*g*heightM):null,...extra});
  if(!(m>0&&g>0&&Number.isFinite(m)&&Number.isFinite(g)))return invalid('Positive total mass and gravity are required.');
  if(!(Number.isFinite(heightM)&&heightM>=0))return invalid('Fall height must be finite and nonnegative.');
  if(!(Q>1e-8&&Number.isFinite(Q)))return invalid('Require θ₂ᶜ > θ₂ᵉ with a nonzero compression stroke.');
  const start=VSLSpring.state(p,p.te),finish=VSLSpring.state(p,p.tc);
  if(!start.valid||!finish.valid)return invalid(start.reason??finish.reason??'Invalid spring geometry.');
  const endDz=VSL.state(p,p.tc).dz/1000,deltaU=finish.energy-start.energy,E0=m*g*heightM,energyScale=Math.max(1,E0,Math.abs(m*g*endDz),Math.abs(deltaU)),eps=energyScale*1e-10,T=(E0+m*g*endDz-deltaU)/Q;
  const base={strokeM:endDz,deltaSpringEnergyJ:deltaU,impactEnergyJ:E0,brakingTorqueNm:T,energyTorqueNm:T,angleStrokeRad:Q};
  if(!(endDz>1e-8))return invalid('The working range must give positive upward wheel travel (downward chassis travel).',base);
  if(T < -eps/Q)return invalid('The spring absorbs more than the available energy. Reaching θ₂ᶜ requires motor drive, not this constant-braking catch.',base);
  const torque=Math.max(0,T),at=theta=>{
   const spring=VSLSpring.state(p,theta),dz=VSL.state(p,theta).dz/1000,q=(theta-p.te)*R,J=spring.Jz/1000;
   if(!spring.valid)return {valid:false,reason:spring.reason};
   if(!(J>1e-9))return {valid:false,reason:'Vertical travel reverses or reaches a dead centre within the working range.'};
   const K=E0+m*g*dz-(spring.energy-start.energy)-torque*q,Fz=(torque-spring.tauS)/J,aG=Fz/(m*g)-1;
   return {valid:true,theta,tau2:-torque,aG,Fz,vz:-Math.sqrt(2*Math.max(0,K)/m),dz:dz*1000,K,J,Fs:spring.force,Kprime:m*g*J+spring.tauS-torque};
  };
  const first=at(p.te),last=at(p.tc);
  if(!first.valid||!last.valid)return invalid(first.reason??last.reason,base);
  if(last.Kprime>=-energyScale*1e-10)return invalid('The endpoint is not a finite-time decelerating stop under constant braking.',base);
  if(E0===0&&first.Kprime<=energyScale*1e-10)return invalid('Starting at rest, this constant torque cannot initiate compression. Increase h or change the spring/working range.',base);
  // q=qe+Q sin²(pi eta/2) removes the integrable endpoint speed singularities.
  const evaluate=eta=>{
   const theta=p.te+(p.tc-p.te)*Math.sin(Math.PI*eta/2)**2,row=at(theta);
   if(!row.valid)return row;
   if(row.K < -eps)return {valid:false,reason:'Constant maximum braking stops the robot before θ₂ᶜ. The energy-only torque bound is not a feasible full-stroke trajectory.'};
   if(row.Fz < -m*g*1e-9)return {valid:false,reason:'This trajectory requires negative ground force (loss of unilateral contact).'};
   if(eta>0&&eta<1&&row.K<=0)return {valid:false,reason:'An interior zero-speed point prevents a single forward finite-time catch.'};
   let dt;
   if(eta===1)dt=last.J*Math.PI*Math.sqrt(m*Q/(-2*last.Kprime));
   else if(eta===0)dt=E0>0?0:first.J*Math.PI*Math.sqrt(m*Q/(2*first.Kprime));
   else dt=row.J*Q*Math.PI/2*Math.sin(Math.PI*eta)/Math.sqrt(2*row.K/m);
   if(!Number.isFinite(dt)||dt<0)return {valid:false,reason:'No finite forward time mapping is available.'};
   return {...row,dt};
  };
  const rows=[],warnings=[];let previous=evaluate(0),time=0;
  if(!previous.valid)return invalid(previous.reason,base);
  rows.push({...previous,time:0});
  for(let i=1;i<=n;i++){
   const row=evaluate(i/n),mid=evaluate((i-.5)/n);
   if(!row.valid||!mid.valid)return invalid(row.reason??mid.reason,base);
   time+=(previous.dt+4*mid.dt+row.dt)/(6*n);
   rows.push({...row,time});previous=row;
  }
  rows[0].vz=-Math.sqrt(2*g*heightM);rows.at(-1).vz=0;rows.at(-1).K=0;
  const peak=(key,absolute=true)=>rows.reduce((best,row)=>!best||(absolute?Math.abs(row[key]):row[key])>(absolute?Math.abs(best[key]):best[key])?row:best,null);
  const aPeak=peak('aG'),vPeak=peak('vz'),forcePeak=peak('Fz',false),minA=Math.min(...rows.map(r=>r.aG));
  if(minA < -1e-6)warnings.push('Some travel accelerates downward before braking; actual peak speed can exceed impact speed.');
  if(heightM===0)warnings.push('Zero drop: compression starts under gravity/spring imbalance, rather than impact.');
  if(Math.abs(p.m2)+Math.abs(p.m3)+Math.abs(p.m5)+Math.abs(p.m6)>0)warnings.push('Fall study lumps all entered mass into vertical translation; moving-link inertia remains excluded.');
  return {valid:true,rows,warnings,heightM,massKg:m,impactSpeed:Math.sqrt(2*g*heightM),...base,brakingTorqueNm:torque,catchTimeS:time,minAccelerationG:minA,monotonicDeceleration:minA>=-1e-6,peaks:{tau2:torque,aG:Math.abs(aPeak.aG),aSigned:aPeak.aG,Fz:forcePeak.Fz,vz:Math.abs(vPeak.vz),dz:endDz*1000},peakPoses:{aG:aPeak.theta,vz:vPeak.theta,Fz:forcePeak.theta},energyResidualJ:E0+m*g*endDz-deltaU-torque*Q};
 }
 function sample(input,heightM,theta,result){
  const p={...input,beta:0},r=result??solve(p,heightM,{samples:160});
  if(!r.valid)return {valid:false,reason:r.reason};
  if(theta<p.te-1e-8||theta>p.tc+1e-8)return {valid:false,reason:'Pose lies outside the fall working stroke.'};
  theta=Math.max(p.te,Math.min(p.tc,theta));const spring=VSLSpring.state(p,theta),J=spring.Jz/1000,m=mass(p),dz=VSL.state(p,theta).dz/1000,start=VSLSpring.state(p,p.te),T=r.brakingTorqueNm,K=m*p.g*heightM+m*p.g*dz-(spring.energy-start.energy)-T*(theta-p.te)*R,Fz=(T-spring.tauS)/J;
  if(!spring.valid||!(J>1e-9)||K < -Math.max(1,r.impactEnergyJ)*1e-8||Fz < -1e-7)return {valid:false,reason:'Invalid fall state at this pose.'};
  let lo=0,hi=r.rows.length-1;while(hi-lo>1){const mid=(lo+hi)>>1;if(r.rows[mid].theta<theta)lo=mid;else hi=mid;}const a=r.rows[lo],b=r.rows[hi],f=b.theta===a.theta?0:(theta-a.theta)/(b.theta-a.theta);
  return {valid:true,theta,time:a.time+(b.time-a.time)*f,tau2:-T,aG:Fz/(m*p.g)-1,Fz,Fy:0,vz:theta===p.tc?0:-Math.sqrt(2*Math.max(0,K)/m),dz:dz*1000,K:theta===p.tc?0:Math.max(0,K),Fs:spring.force,J};
 }
 function study(p,heightM,alphaRange,options={}){
  const current=solve(p,heightM,{samples:options.samples??800}),count=alphaRange.min===alphaRange.max?1:61,sweep=[];
  for(let i=0;i<count;i++){
   const alpha=count===1?alphaRange.min:alphaRange.min+(alphaRange.max-alphaRange.min)*i/(count-1),result=solve({...p,alpha},heightM,{samples:options.sweepSamples??240});
   const travel=VSL.envelope({...p,alpha}).values.dz,geometricPeak=Math.max(Math.abs(travel.min),Math.abs(travel.max));
   sweep.push({alpha,valid:result.valid,reason:result.reason??'',peaks:result.peaks??null,catchTimeS:result.catchTimeS??null,strokeMm:Number.isFinite(geometricPeak)?geometricPeak:null,impactSpeed:result.impactSpeed,brakingTorqueNm:result.brakingTorqueNm});
  }
  const travel=VSL.envelope(p).values.dz,heightPeak=Math.max(Math.abs(travel.min),Math.abs(travel.max));
  const heightRange=options.heightRange??{min:heightM,max:heightM},heightSweep=[],nh=heightRange.min===heightRange.max?1:51;
  for(let i=0;i<nh;i++){const h=nh===1?heightRange.min:heightRange.min+(heightRange.max-heightRange.min)*i/(nh-1),r=solve(p,h,{samples:options.sweepSamples??160});heightSweep.push({height:h,strokeMm:Number.isFinite(heightPeak)?heightPeak:null,valid:r.valid,reason:r.reason??'',peaks:r.peaks??null,catchTimeS:r.catchTimeS??null});}
  return {current,sweep,heightSweep,heightRange:{...heightRange},alphaRange:{...alphaRange}};
 }
 return {solve,sample,study};
}
const VSLFall=VSLFallModel();
if(typeof module!=='undefined')module.exports={VSLFallModel,VSLFall};
