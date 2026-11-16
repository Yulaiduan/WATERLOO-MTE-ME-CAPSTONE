/** VSL V6 fall catch with distributed masses. Browser/Node, no dependencies.
 * Inputs: V4 geometry mm/deg, total mass kg, g m/s2, fall height m.
 * Output: signed Link2 torque Nm, upward az/g, ground Fz N, vz m/s, dz mm,
 * touchdown-relative time s, feasibility and sampled alpha peaks.
 * Fixed pitch and chassis y, beta=Fy=0, rigid contact after inelastic touchdown.
 * Rod inertia at link centres and translating point masses at knee and wheel.
 * Constant-braking energy bound is a minimum peak only when its full path exists.
 */
function VSLFallModel(){
 const R=Math.PI/180;
 const mass=p=>VSLSpring.totalMass(p);
 function massGeometry(p,theta,spring){
  const pose=VSL.state(p,theta),J=spring.Jz/1000,dz=pose.dz/1000,m=mass(p);
  if(![p.m2,p.m3,p.m5,p.m6].some(x=>x>0))return {J,dz,potential:-m*p.g*dz,gravityTorque:m*p.g*J,H:m*J*J};
  const k=1-VSL.ratios(p).qab,a=theta*R,b=pose.t3*R;
  const hipToKnee=VSL.global(p,pose.B).map(x=>x/1000),hipToWheel=VSL.global(p,pose.P).map(x=>x/1000);
  const B1=VSL.global(p,[p.L2*Math.sin(a)/1000,-p.L2*Math.cos(a)/1000]);
  const link31=VSL.global(p,[p.L3*k*Math.sin(b)/1000,-p.L3*k*Math.cos(b)/1000]);
  const C1=B1.map((x,i)=>x+link31[i]);
  const B2=hipToKnee.map(x=>-x),C2=B2.map((x,i)=>x-k*k*(hipToWheel[i]-hipToKnee[i]));
  const weights=[[1,0,0],[2,.5,0],[3,.5,.5],[5,1,0],[6,0,1]];
  const centre=(B,C,u,v)=>[u*B[0]+v*C[0],u*B[1]+(v-1)*C[1]];
  const bodies=weights.map(([id,u,v])=>({id,m:p['m'+id],z:centre(hipToKnee,hipToWheel,u,v)[1],first:centre(B1,C1,u,v),second:centre(B2,C2,u,v)}));
  let potential=0,gravityTorque=0,H=p.m2*(p.L2/1000)**2/12+p.m3*(p.L3/1000)**2*k*k/12,Hprime=0;
  for(const body of bodies){
   const {m,z,first,second}=body;
   potential+=m*p.g*z;
   gravityTorque-=m*p.g*first[1];
   H+=m*(first[0]**2+first[1]**2);
   Hprime+=2*m*(first[0]*second[0]+first[1]*second[1]);
  }
  return {J,dz,potential,gravityTorque,H,Hprime,bodies};
 }

 function at(p,theta,context){
  const spring=VSLSpring.state(p,theta);
  if(!spring.valid)return {valid:false,reason:spring.reason};
  const geo=massGeometry(p,theta,spring),{J,dz,H,gravityTorque}=geo,m=mass(p),torque=context.brakingTorqueNm;
  if(!(J>1e-9&&H>0))return {valid:false,reason:'Vertical travel reverses or reaches a dead centre within the working range.'};
  const q=(theta-p.te)*R;
  const K=theta===p.tc?0:context.impactEnergyJ+context.startPotentialJ-geo.potential-(spring.energy-context.startSpringEnergyJ)-torque*q;
  const Kprime=gravityTorque+spring.tauS-torque;
  const qdot=Math.sqrt(2*Math.max(0,K)/H);
  let Fz=(torque-spring.tauS)/J,aG=Fz/(m*p.g)-1,motion=null;
  if(geo.bodies){
   const qdd=(Kprime-.5*geo.Hprime*qdot*qdot)/H,acceleration={};
   Fz=m*p.g;
   for(const body of geo.bodies){
    const a=body.first.map((x,i)=>x*qdd+body.second[i]*qdot*qdot);
    acceleration[body.id]=a;
    Fz+=body.m*a[1];
   }
   aG=acceleration[1][1]/p.g;
   motion={qdd,acceleration};
  }
  return {valid:true,theta,tau2:-torque,aG,Fz,vz:-J*qdot,dz:dz*1000,K,J,Fs:spring.force,Kprime,H,qdot,motion,gravityTorque,springTorque:spring.tauS};
 }
 // Signed circulation is positive for increasing theta2; pulley a is chassis-fixed.
 function beltState(p,row){
  const qdot=-row.vz/row.J,vab=p.ra/1000*qdot,geom=VSL.state(p,row.theta);
  if(!(p.ra>0&&p.rb>0&&p.L2>p.ra+p.rb))return {qdot,vab:null,deltaTab:null,tauAB:null,omega32:null,Pab:null,TabU:null,TabL:null,beltReason:'AB pitch circles overlap or have invalid radii.'};
  const [y,z]=geom.Pg.map((value,i)=>value-geom.Bg[i]);
  const aw=row.motion?.acceleration[6]??[0,0],at=row.motion?.acceleration[3]??[0,0];
  const wheelMoment=y*(row.Fz-p.m6*(p.g+aw[1]))+z*p.m6*aw[0];
  const tibiaMoment=.5*p.m3*(-y*(p.g+at[1])+z*at[0]);
  const tibiaInertiaMoment=-1000*p.m3*(p.L3/1000)**2/12*(1-VSL.ratios(p).qab)*(row.motion?.qdd??0);
  const delta=-(wheelMoment+tibiaMoment+tibiaInertiaMoment)/p.rb;
  const ab=VSLStatic.belt([0,0],geom.B,p.ra,p.rb,1,delta,p.Tab0,'ab');
  if(!ab)return {qdot,vab:null,deltaTab:null,tauAB:null,omega32:null,Pab:null,TabU:null,TabL:null,beltReason:'AB tangent geometry unavailable.'};
  // Power is positive from Link 3 into AB at pulley b, in the Link 2 frame.
  const tauAB=-ab.Mright,omega32=-vab/(p.rb/1000)*60/(2*Math.PI);
  return {qdot,vab,deltaTab:ab.delta,tauAB,omega32,Pab:ab.delta*vab,TabU:ab.U,TabL:ab.L,beltReason:null};
 }
 function withBelts(p,result){
  if(!result.valid)return result;
  const rows=result.rows.map(row=>({...row,...beltState(p,row)})),last=rows.at(-1),mg=result.massKg*p.g,holdingBelt=beltState(p,{...last,Fz:mg,vz:0,motion:null});
  const peaks={...result.peaks},peakPoses={...result.peakPoses};
  for(const key of ['deltaTab','vab','tauAB','omega32','Pab']){const finite=rows.filter(row=>Number.isFinite(row[key])),best=finite.reduce((a,r)=>!a||Math.abs(r[key])>Math.abs(a[key])?r:a,null);peaks[key]=best?Math.abs(best[key]):null;peakPoses[key]=best?.theta??null;}
  const warnings=[...result.warnings];if(rows.some(r=>r.beltReason))warnings.push('AB belt plots unavailable: '+rows.find(r=>r.beltReason).beltReason);
  return {...result,rows,peaks,peakPoses,holdingBelt,warnings};
 }
 function solve(input,heightM,options={}){
  const p={...input,beta:0},m=mass(p),g=p.g,n=Math.max(80,Math.floor(options.samples??800)),Q=(p.tc-p.te)*R;
  const invalid=(reason,extra={})=>({valid:false,reason,rows:[],warnings:[],heightM,massKg:m,impactSpeed:Number.isFinite(g*heightM)&&g*heightM>=0?Math.sqrt(2*g*heightM):null,...extra});
  if(!(m>0&&g>0&&Number.isFinite(m)&&Number.isFinite(g)))return invalid('Positive total mass and gravity are required.');
  if(!(Number.isFinite(heightM)&&heightM>=0))return invalid('Fall height must be finite and nonnegative.');
  if(!(Q>1e-8&&Number.isFinite(Q)))return invalid('Require θ₂ᶜ > θ₂ᵉ with a nonzero compression stroke.');
  const start=VSLSpring.state(p,p.te),finish=VSLSpring.state(p,p.tc);
  if(!start.valid||!finish.valid)return invalid(start.reason??finish.reason??'Invalid spring geometry.');
  const e=massGeometry(p,p.te,start),c=massGeometry(p,p.tc,finish),endDz=c.dz;
  const deltaU=finish.energy-start.energy,gravityWorkJ=e.potential-c.potential,dropEnergyJ=m*g*heightM;
  if(!(e.J>1e-9&&e.H>0)||heightM>0&&!(e.gravityTorque>0))return invalid('Touchdown cannot start forward compression.');
  // Project the pre-impact downward translation onto the allowed contact tangent.
  const E0=e.bodies ? (e.gravityTorque/g)**2/e.H*g*heightM : dropEnergyJ;
  const energyScale=Math.max(1,E0,Math.abs(gravityWorkJ),Math.abs(deltaU)),eps=energyScale*1e-10,T=(E0+gravityWorkJ-deltaU)/Q;
  const base={strokeM:endDz,deltaSpringEnergyJ:deltaU,impactEnergyJ:E0,dropEnergyJ,impactLossJ:Math.max(0,dropEnergyJ-E0),gravityWorkJ,
   continuousSpeedEnergyJ:e.H*g*heightM/(e.J*e.J),gravity:g,distributed:Boolean(e.bodies),startPotentialJ:e.potential,startSpringEnergyJ:start.energy,
   brakingTorqueNm:T,energyTorqueNm:T,angleStrokeRad:Q};
  if(!(endDz>1e-8))return invalid('The working range must give positive upward wheel travel (downward chassis travel).',base);
  if(T < -eps/Q)return invalid('The spring absorbs more than the available energy. Reaching θ₂ᶜ requires motor drive, not this constant-braking catch.',base);
  const torque=Math.max(0,T),context={...base,brakingTorqueNm:torque};
  const first=at(p,p.te,context),last=at(p,p.tc,context);
  if(!first.valid||!last.valid)return invalid(first.reason??last.reason,base);
  if(last.Kprime>=-energyScale*1e-10)return invalid('The endpoint is not a finite-time decelerating stop under constant braking.',base);
  if(E0===0&&first.Kprime<=energyScale*1e-10)return invalid('Starting at rest, this constant torque cannot initiate compression. Increase h or change the spring/working range.',base);
  // q=qe+Q sin²(pi eta/2) removes the integrable endpoint speed singularities.
  const evaluate=eta=>{
   const theta=p.te+(p.tc-p.te)*Math.sin(Math.PI*eta/2)**2,row=at(p,theta,context);
   if(!row.valid)return row;
   if(row.K < -eps)return {valid:false,reason:'Constant maximum braking stops the robot before θ₂ᶜ. The energy-only torque bound is not a feasible full-stroke trajectory.'};
   if(row.Fz < -m*g*1e-9)return {valid:false,reason:`Contact would lift at θ₂ = ${row.theta.toFixed(2)}° (required F_z = ${row.Fz.toFixed(1)} N). No full-stroke constant-torque catch at these settings.`};
   if(eta>0&&eta<1&&row.K<=0)return {valid:false,reason:'An interior zero-speed point prevents a single forward finite-time catch.'};
   let dt;
   if(eta===1)dt=Math.PI*Math.sqrt(last.H*Q/(-2*last.Kprime));
   else if(eta===0)dt=E0>0?0:Math.PI*Math.sqrt(first.H*Q/(2*first.Kprime));
   else dt=Q*Math.PI/2*Math.sin(Math.PI*eta)/row.qdot;
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
  const peakRpm=rows.reduce((max,row)=>Math.max(max,-row.vz/row.J*60/(2*Math.PI)),0);
  const peak=(key,absolute=true)=>rows.reduce((best,row)=>!best||(absolute?Math.abs(row[key]):row[key])>(absolute?Math.abs(best[key]):best[key])?row:best,null);
  const aPeak=peak('aG'),vPeak=peak('vz'),forcePeak=peak('Fz',false),minA=Math.min(...rows.map(r=>r.aG));
  if(minA < -1e-6)warnings.push('Some travel accelerates downward before braking; actual peak speed can exceed impact speed.');
  if(heightM===0)warnings.push('Zero drop: compression starts under gravity/spring imbalance, rather than impact.');
  return {valid:true,rows,warnings,heightM,massKg:m,impactSpeed:Math.sqrt(2*g*heightM),...context,
   holdingTau2:-last.gravityTorque-last.springTorque,catchTimeS:time,minAccelerationG:minA,monotonicDeceleration:minA>=-1e-6,peaks:{tau2:torque,omega2:peakRpm,aG:Math.abs(aPeak.aG),aSigned:aPeak.aG,Fz:forcePeak.Fz,vz:Math.abs(vPeak.vz),dz:endDz*1000},peakPoses:{aG:aPeak.theta,vz:vPeak.theta,Fz:forcePeak.theta},energyResidualJ:E0+gravityWorkJ-deltaU-torque*Q};
 }
 function sample(input,heightM,theta,result){
  const p={...input,beta:0},r=result??solve(p,heightM,{samples:160});
  if(!r.valid)return {valid:false,reason:r.reason};
  if(theta<p.te-1e-8||theta>p.tc+1e-8)return {valid:false,reason:'Pose lies outside the fall working stroke.'};
  theta=Math.max(p.te,Math.min(p.tc,theta));const point=at(p,theta,r);
  if(!point.valid||point.K < -Math.max(1,r.impactEnergyJ)*1e-8||point.Fz < -1e-7)return {valid:false,reason:point.reason??'Invalid fall state at this pose.'};
  let lo=0,hi=r.rows.length-1;while(hi-lo>1){const mid=(lo+hi)>>1;if(r.rows[mid].theta<theta)lo=mid;else hi=mid;}const a=r.rows[lo],b=r.rows[hi],f=b.theta===a.theta?0:(theta-a.theta)/(b.theta-a.theta);
  return {...point,time:a.time+(b.time-a.time)*f,Fy:0,K:Math.max(0,point.K)};
 }
 function study(p,heightM,alphaRange,options={}){
  const current=withBelts(p,solve(p,heightM,{samples:options.samples??800})),count=alphaRange.min===alphaRange.max?1:61,sweep=[];
  for(let i=0;i<count;i++){
   const alpha=count===1?alphaRange.min:alphaRange.min+(alphaRange.max-alphaRange.min)*i/(count-1),result=withBelts({...p,alpha},solve({...p,alpha},heightM,{samples:options.sweepSamples??240}));
   const travel=VSL.envelope({...p,alpha}).values.dz,geometricPeak=Math.max(Math.abs(travel.min),Math.abs(travel.max));
   sweep.push({alpha,valid:result.valid,reason:result.reason??'',peaks:result.peaks??null,catchTimeS:result.catchTimeS??null,strokeMm:Number.isFinite(geometricPeak)?geometricPeak:null,impactSpeed:result.impactSpeed,brakingTorqueNm:result.brakingTorqueNm});
  }
  const travel=VSL.envelope(p).values.dz,heightPeak=Math.max(Math.abs(travel.min),Math.abs(travel.max));
  const heightRange=options.heightRange??{min:heightM,max:heightM},heightSweep=[],nh=heightRange.min===heightRange.max?1:51;
  for(let i=0;i<nh;i++){const h=nh===1?heightRange.min:heightRange.min+(heightRange.max-heightRange.min)*i/(nh-1),r=withBelts(p,solve(p,h,{samples:options.sweepSamples??160}));heightSweep.push({height:h,strokeMm:Number.isFinite(heightPeak)?heightPeak:null,valid:r.valid,reason:r.reason??'',peaks:r.peaks??null,catchTimeS:r.catchTimeS??null});}
  return {current,sweep,heightSweep,heightRange:{...heightRange},alphaRange:{...alphaRange}};
 }
 return {solve,sample,study,beltState,withBelts};
}
const VSLFall=VSLFallModel();
if(typeof module!=='undefined')module.exports={VSLFallModel,VSLFall};
