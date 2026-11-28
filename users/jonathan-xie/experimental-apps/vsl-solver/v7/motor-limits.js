/** V7 motor capacity studies. Load after fall-model.js; browser/Node via factory.
 * Inputs: existing p in mm/deg/kg, supply W/s/A and free speed rpm.
 * Outputs: sampled maximum catch heights m, geared torque Nm and payload kg.
 * Uses the existing vertical contact model and maximum-resistance control law;
 * not a global optimal controller, thermal transient model or hardware rating.
 */
function VSLMotorLimitsModel(){
 const phase=p=>p.motorKvLNOverride??Math.sqrt(3)*(p.motorKV??110);
 const kt=p=>p.motorKtOverride??1.5*60/(2*Math.PI)/phase(p);
 const free=p=>p.motorFreeSpeedOverride??(p.supplyVmaxLN!=null?p.supplyVmaxLN*phase(p):p.motorFreeSpeedRpm);
 function payload(p,gr){
  const cap=kt(p)*(p.supplyIcont??0)*gr;
  if(!(cap>0&&Number.isFinite(cap)))return {valid:false,reason:'A resolved positive GR and continuous current are required.'};
  const q={...p,mp:0,m1:p.m1-(p.mp??0)/4,beta:0,Fy:0,loadMode:'yz'},weight=VSLSpring.totalMass(q)*p.g;
  let lower=0,upper=Infinity,theta=null;
  for(let i=0;i<=1600;i++){
   const t=p.te+(p.tc-p.te)*i/1600,a=VSLStatic.solve({...q,Fz:weight},t,false),b=VSLStatic.solve({...q,Fz:weight+p.g},t,false);
   if(!a.valid||!b.valid)return {valid:false,reason:a.reason??b.reason};
   const slope=b.tau2-a.tau2;
   if(Math.abs(slope)<1e-12){if(Math.abs(a.tau2)>cap+1e-8)return {valid:false,reason:'Baseline holding torque exceeds the continuous limit at a payload-insensitive pose.'};continue;}
   const ends=[(-cap-a.tau2)/slope,(cap-a.tau2)/slope].sort((x,y)=>x-y);
   lower=Math.max(lower,ends[0]);if(ends[1]<upper){upper=ends[1];theta=t;}
  }
  if(upper<lower||upper<0)return {valid:false,reason:'No nonnegative payload can be held throughout this working range.',capNm:cap};
  return {valid:true,perLegKg:upper,totalKg:4*upper,minimumTotalKg:4*lower,limitingTheta:theta,capNm:cap,gearRatio:gr};
 }
 function heights(p,progress=()=>{},options={}){
  const fixed=options.gearRatio!=null;
  if(fixed&&!(Number.isFinite(options.gearRatio)&&options.gearRatio>0))return {rows:[],reason:'A positive resolved GR is required.'};
  const common={...p,fallSolveMode:'maximize',...(fixed?{motorIndependent:'gr',motorGR:options.gearRatio}:{motorIndependent:'sf',speedSF:1})},P=p.fallPowerCeiling??p.supplyPowerW??2000,thermal=p.supplyOverheatS;
  const probe=VSLFall.solve({...common,fallSolveMode:'minimize',fallPowerCeiling:1e12},1,{samples:80});
  const motorProbe=fixed&&!(probe.torqueCeilingNm>0)?VSLFall.solve({...common,fallPowerCeiling:1e12},1,{samples:80}):probe;
  const B=probe.impactEnergyJ,C=probe.gravityWorkJ-probe.deltaSpringEnergyJ,A=motorProbe.torqueCeilingNm,Q=(p.tc-p.te)*Math.PI/180;
  if(![B,C,A,Q].every(Number.isFinite)||!(B>0&&A>0&&Q>0))return {rows:[],reason:probe.reason??'Invalid geometry or touchdown state.'};
  // Necessary work bound: B*h+C <= (A/sqrt(h))*Q. Strictly increasing gap.
  let hi=1;
  if(fixed){
   // At fixed GR the cap is constant; touchdown rpm scales with sqrt(h).
   const speedProbe=motorProbe.speedSafetyFactor>0?motorProbe:VSLFall.solve({...common,fallPowerCeiling:1e12},1,{samples:80});
   hi=speedProbe.speedSafetyFactor**2;
   // The speed bound is valid even when an earlier stop beats the full-stroke
   // work budget. Torque, power and contact are enforced by each trajectory.
   if(!(Number.isFinite(hi)&&hi>0))return {rows:[],reason:'No positive motor-speed height bound could be resolved.'};
  }else{
   while(B*hi+C-A*Q/Math.sqrt(hi)<0&&hi<1e8)hi*=2;
   let lo=0;for(let i=0;i<70;i++){const mid=(lo+hi)/2;if(B*mid+C-A*Q/Math.sqrt(mid)>0)hi=mid;else lo=mid;}
  }
  const upper=hi,points=new Set([upper]);
  for(let i=0;i<=56;i++){points.add(upper*(i+1)/57);points.add(upper*Math.pow(1e-7,1-i/56));}
  const hs=[...points].sort((x,y)=>x-y),all=[[],[],[]];let count=0;
  function check(h,power,samples=120){const r=VSLFall.solve({...common,fallPowerCeiling:power},h,{samples});
   const speedOK=r.valid&&r.peaks.omega2*r.gearRatio<=free(p)*(1+2e-5);
   return {h,r,ok:Boolean(r.valid&&speedOK),reason:r.valid&&!speedOK?'Motor free speed exceeded during recovery.':r.reason};}
  const accepts=(x,mode)=>x.ok&&(mode!==2||x.r.catchTimeS<=thermal);
  for(const h of hs){const unrestricted=check(h,1e12),power=check(h,P);all[0].push(unrestricted);all[1].push(power);all[2].push(power);if(++count%8===0)progress(count/hs.length*.8);}
  const rows=[];
  for(let mode=0;mode<3;mode++){
   const trials=all[mode],idx=trials.findLastIndex(x=>accepts(x,mode));
   if(idx<0){rows.push({valid:false,reason:mode===2?'No feasible catch meets both power and recovery-time limits in the sampled domain.':trials.find(x=>x.reason)?.reason??'No feasible catch found.'});continue;}
   let best=trials[idx],right=trials[idx+1]?.h??upper;
   for(let i=0;i<22&&right-best.h>Math.max(1e-7,best.h*1e-5);i++){
    const mid=check((best.h+right)/2,mode===0?1e12:P,400);
    if(accepts(mid,mode))best=mid;else right=mid.h;
   }
   // Independent denser force/time evaluation before displaying a boundary.
   let final=check(best.h,mode===0?1e12:P,1000);
   for(let i=0;i<20&&!accepts(final,mode);i++)final=check(final.h*.999,mode===0?1e12:P,1000);
   if(!accepts(final,mode)){rows.push({valid:false,reason:'Boundary did not pass the denser verification.'});continue;}
   rows.push({valid:true,heightM:final.h,gearRatio:final.r.gearRatio,speedSafetyFactor:final.r.speedSafetyFactor,initialOmega2Rpm:final.r.rows[0].qdot*60/(2*Math.PI),torqueCeilingNm:final.r.torqueCeilingNm,omega2Rpm:final.r.peaks.omega2,powerW:final.r.peaks.hipPower,timeS:final.r.catchTimeS,stopTheta:final.r.stopTheta,energyResidualJ:final.r.energyResidualJ,boundWidthM:right-best.h});
   progress(.8+(mode+1)/3*.2);
  }
  return {rows,workUpperBoundM:upper,powerLimitW:P,thermalLimitS:thermal,samples:hs.length,method:'Maximum allowed resistance, first rest at/before theta2c; '+(fixed?'fixed GR':'SF=1')+'; speed/contact/travel checked. Sampled feasible islands, refined upper boundaries.'};
 }
 function sweep(p,motors,supplies,progress=()=>{}){
  const results=[],cache=new Map();let reused=0;
  for(let i=0;i<supplies.length;i++){
   const s=supplies[i];
   for(let j=0;j<motors.length;j++){
    const m=motors[j],q={...p,motorKV:m.kv,motorKvLNOverride:m.kvLNOverride??null,motorKtOverride:m.ktOverride??null,motorFreeSpeedOverride:null,supplyVmaxLN:s.vmax,supplyIpeak:s.peak,supplyIcont:s.continuous,supplyOverheatS:s.overheat,fallPowerCeiling:s.power},start=(i*motors.length+j)/(supplies.length*motors.length);
    // SF=1: cap depends on Kt*free, while GR scales with free.
    const signature=i+':'+(kt(q)*free(q)).toPrecision(12);
    let data=cache.get(signature);
    if(!data){
     const h=heights(q,f=>progress(start+f/(supplies.length*motors.length)));
     data={...h,free:free(q)};data.rows=data.rows.map(r=>r.valid?{...r,payload:payload(q,r.gearRatio)}:r);cache.set(signature,data);
    }else reused++;
    const rows=data.rows.map(r=>r.valid?{...r,gearRatio:r.gearRatio*free(q)/data.free,payload:{...r.payload,gearRatio:r.gearRatio*free(q)/data.free}}:r);
    results.push({motor:{id:m.id,kv:m.kv,comment:m.comment},supply:s,rows,reason:data.reason});
   }
  }
  progress(1);return {results,solves:cache.size,reused};
 }
 function fixedSweep(p,gearRatio,supplies,progress=()=>{}){
  if(!(Number.isFinite(gearRatio)&&gearRatio>0))throw Error('A positive resolved GR is required.');
  const results=[];
  for(let i=0;i<supplies.length;i++){
   const s=supplies[i],q={...p,motorFreeSpeedOverride:null,supplyVmaxLN:s.vmax,supplyIpeak:s.peak,supplyIcont:s.continuous,supplyOverheatS:s.overheat,fallPowerCeiling:s.power};
   const h=heights(q,f=>progress((i+f)/supplies.length),{gearRatio}),capacity=payload(q,gearRatio);
   results.push({motor:{id:p.motorConfigId??String(p.motorKV),kv:p.motorKV,comment:'Selected motor'},supply:s,rows:h.rows.map(r=>r.valid?{...r,payload:capacity}:r),payload:capacity,reason:h.reason});
  }
  progress(1);return {results,gearRatio,motorKV:p.motorKV};
 }
 return {phase,kt,free,payload,heights,sweep,fixedSweep};
}
const VSLMotorLimits=VSLMotorLimitsModel();
if(typeof module!=='undefined')module.exports={VSLMotorLimitsModel,VSLMotorLimits};
