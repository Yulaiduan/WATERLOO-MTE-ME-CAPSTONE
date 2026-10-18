/** Verify the actual V3 embedded model. Run: node verify-spring.cjs.
 * Deterministic geometry mm/deg, loads N/kg, spring N/mm; reports numerical
 * force, moment, energy and peak checks. No hardware or dynamic validation.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'v3-spring.html'),'utf8'),scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
scripts.forEach(x=>new vm.Script(x));
const {VSL:k,VSLStatic:s,VSLUnassisted:base,VSLSpring:sp,VSLPeaks:peak}=vm.runInNewContext(scripts.slice(0,3).join('\n')+';({VSL,VSLStatic,VSLUnassisted,VSLSpring,VSLPeaks});');
let n=0;const near=(a,b,t=1e-7)=>{assert.ok(Math.abs(a-b)<=t,`${a} != ${b}`);n++;};
const p={...s.defaults},ranges={alpha:{min:0,max:30},beta:{min:0,max:90}};
let seed=4823;const rand=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/2**32;};
let forceError=0,momentError=0,energyError=0;
for(let i=0;i<450;i++){
 const pp={...p,alpha:45*rand(),ra:25+70*rand(),L2:250+100*rand(),L3:250+100*rand(),m2:rand(),m3:rand(),m5:rand(),m6:rand(),Fn:200*rand()-50,Ft:100*rand()-50,Fy:200*rand()-50,Fz:200*rand()-50,beta:90*rand(),loadMode:i%2?'yz':'nt',springPreload:30*rand(),springL0:i%3?55:160,tc:270},t=90+180*rand(),z=s.solve(pp,t),b=base.solve(pp,t),sh=z.spring,h=1e-5;
 near(z.tau2,z.tauG-z.tauS);near(z.tauG,-b.tau2);near(z.tau2Applied,-z.tau2);near(z.tau4,b.tau4);near(z.ab.delta,b.ab.delta);near(z.cd.delta,b.cd.delta);near(z.ef.delta,b.ef.delta);
 near(z.F12[0],b.F12[0]-z.Fspring[0]);near(z.F12[1],b.F12[1]-z.Fspring[1]);near(base.cross(sh.Dg,sh.Fg)/1000,-z.tauS);
 near((sp.state(pp,t+h/k.rad).energy-sp.state(pp,t-h/k.rad).energy)/(2*h),z.tauS,2e-5);
 energyError=Math.max(energyError,Math.abs((sp.state(pp,t+h/k.rad).energy-sp.state(pp,t-h/k.rad).energy)/(2*h)-z.tauS));
 near((sp.span(pp,t+h/k.rad).length-sp.span(pp,t-h/k.rad).length)/(2*h),sh.derivative,1e-6);
 for(const key of ['tau2','tauG','tauS','tau4'])near(s.solve(pp,t,false)[key],z[key]);
 near(z.maxForce,0,5e-10);near(z.maxMoment,0,5e-10);near(z.virtualWorkError,0,5e-10);forceError=Math.max(forceError,z.maxForce);momentError=Math.max(momentError,z.maxMoment);
 // Chassis spring mounting force/couple restore unchanged whole-system reactions.
 near(z.F12[0]+z.Fspring[0],b.F12[0]);near(z.F12[1]+z.Fspring[1],b.F12[1]);near(z.tau2Applied+base.cross([pp.Sy,pp.Sz],sh.Fg)/1000,b.tau2);
 const off=s.solve({...pp,springEnabled:false},t);near(off.tau2,-b.tau2);near(off.F12[0],b.F12[0]);near(off.spring.force,0);
 const f=peak.coefficients(pp,t);near(peak.value(f.tau2,pp.alpha*k.rad,pp.beta*k.rad),z.tau2);
}
const curve=[];for(let i=0;i<=18000;i++){const t=90+i*.01,z=s.solve(p,t,false);curve.push({theta2:t,length:z.spring.length,force:z.spring.force,tauG:z.tauG,tauS:z.tauS,tau2:z.tau2,supportRatio:z.spring.supportRatio});}
const work=curve.filter(z=>z.theta2>=100&&z.theta2<=165),rr=work.map(z=>z.supportRatio);near(Math.min(...rr),.9779681604664655,1e-9);near(sp.state(p,100).supportRatio,1.0220306343897747,1e-7);near(sp.state(p,100).force,185.92260674300582);near(sp.state(p,135).extension,51.606454104602746);assert.equal(sp.state(p,90).supportRatio,null);assert.equal(sp.state(p,270).supportRatio,null);
const start=performance.now();let peakEvaluations=0;
for(let i=0;i<14;i++){
 const pp={...p,te:i%3?100:90,tc:i%3?165:270,alpha:45*rand(),loadMode:i%2?'yz':'nt',Fn:100+100*rand(),Ft:40*rand()-20,Fy:100*rand()-50,Fz:150*rand(),springL0:i%4?55:130,springPreload:i%4?0:20,m2:rand(),m3:rand()},g=peak.fixedAlpha(pp,ranges);
 assert.ok(g.valid);peakEvaluations+=g.evaluations;
 for(const key of ['tau2','tau4','ab','dz']){
  const b=g[key],z=s.solve({...pp,beta:b.beta},b.theta2,false),actual=key==='ab'?Math.max(z.ab.U,z.ab.L):key==='dz'?Math.abs(z.dz):z[key];near(actual,b.value);assert.ok(b.error<=.001&&b.converged);n++;
  for(let j=0;j<300;j++){const z=s.solve({...pp,beta:90*rand()},pp.te+(pp.tc-pp.te)*rand(),false),actual=key==='ab'?Math.max(z.ab.U,z.ab.L):Math.abs(z[key]);assert.ok(actual<=Math.abs(b.value)+b.error+1e-7,`${key}: invalid bound`);n++;}
 }
}
assert.ok(s.validate({...p,tc:270}).length===0);assert.ok(s.validate({...p,tc:271}).length>0);assert.ok(s.validate({...p,springK:-1}).length>0);assert.ok(s.validate({...p,Sy:p.hornR,Sz:0,hornEta:-180}).length>0);
const samples=[90,91,95,100,120,135,150,165,180,210,240,246.9,250,260,269,270].map(t=>({theta2:t,...sp.state(p,t),tauG:s.solve(p,t,false).tauG,tau2:s.solve(p,t,false).tau2}));
const summary={assertions:n,forceError_N:forceError,momentError_Nm:momentError,energyDerivativeError_Nm:energyError,peakCases:14,peakEvaluations,peakTime_ms:performance.now()-start,workingRatio:[Math.min(...rr),Math.max(...rr)],maximumWorkingResidual_Nm:Math.max(...work.map(z=>Math.abs(z.tau2))),samples};
if(process.argv.includes('--output')){fs.writeFileSync(path.join(__dirname,'v3-verification.json'),JSON.stringify(summary,null,2)+'\n');fs.writeFileSync(path.join(__dirname,'v3-full-range.csv'),Object.keys(curve[0]).join(',')+'\n'+curve.map(o=>Object.values(o).map(v=>v===null?'':v).join(',')).join('\n')+'\n');}
console.log(JSON.stringify({...summary,samples:samples.map(z=>({theta2:z.theta2,force:z.force,ratio:z.supportRatio,tauG:z.tauG,tauS:z.tauS,tau2:z.tau2}))},null,2));

