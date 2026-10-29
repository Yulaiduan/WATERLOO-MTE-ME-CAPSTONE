/** Reconstruct V5 massless-link forces under the fall trajectory's wheel load.
 * Browser/Node; inputs geometry mm/deg, h m, mass kg; outputs VSL statics fields
 * in N/Nm with the dynamic Fz, Fy=beta=0 and all entered mass lumped at the chassis.
 * create() caches sampled feasibility by geometry/alpha/height, never mutates inputs.
 * Numerical fall assumptions apply; moving-link inertia and motor ratings excluded.
 */
const VSLFallAnalysis=(()=>{
 const key=(p,h)=>JSON.stringify([['L2','L3','ra','rb','phi0','te','tc','alpha','g','m1','m2','m3','m5','m6','springEnabled','springK','hornR','Sv','rs','p0','nu','Su'].map(k=>p[k]),h]);
 function create(){
  const cache=new Map();
  function trajectory(p,h){const k=key(p,h);if(cache.has(k))return cache.get(k);const r=VSLFall.solve(p,h,{samples:80});if(cache.size>512)cache.clear();cache.set(k,r);return r;}
  function seed(p,h,r){cache.set(key(p,h),r);}
  function solve(p,h,theta,detail=true){
   const r=trajectory(p,h),point=VSLFall.sample(p,h,theta,r);
   if(!point.valid)return {...VSL.state(p,theta),valid:false,reason:point.reason,spring:VSLSpring.state(p,theta),analysisMode:'fall'};
   const total=VSLSpring.totalMass(p),dynamic={...p,m1:total,m2:0,m3:0,m5:0,m6:0,loadMode:'yz',Fy:0,Fz:point.Fz,beta:0},s=VSLStatic.solve(dynamic,theta,detail);
   return {...s,fall:point,analysisMode:'fall'};
  }
  function globalPeaks(p,h){
   const r=trajectory(p,h);if(!r.valid)return {valid:false,reason:r.reason};
   const result={valid:true},pick={};
   for(let i=0;i<=320;i++){
    const theta=p.te+(p.tc-p.te)*i/320,s=solve(p,h,theta,false);if(!s.valid)continue;
    const values={tau2:s.tau2,tau4:s.tau4,ab:Math.max(s.ab.U,s.ab.L),dz:s.dz};
    for(const k in values)if(!pick[k]||Math.abs(values[k])>Math.abs(pick[k].value))pick[k]={value:values[k],signedValue:values[k],theta2:theta,alpha:p.alpha,beta:0,error:0,converged:k==='tau2'||k==='tau4',sampled:true,active:k==='ab'?s.ab.active:undefined};
   }
   for(const k of ['tau2','tau4','ab','dz']){if(!pick[k])return {valid:false,reason:'No valid fall poses.'};result[k]=pick[k];}
   result.Fs=VSLSpring.maximum(p,p.te,p.tc);return result;
  }
  return {trajectory,seed,solve,globalPeaks,clear:()=>cache.clear()};
 }
 return {create,key};
})();
if(typeof module!=='undefined')module.exports=VSLFallAnalysis;
