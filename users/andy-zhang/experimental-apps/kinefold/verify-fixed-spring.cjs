/** Verify fixed-chassis spring geometry, locks and conservative work.
 * Run node verify-fixed-spring.cjs from any cwd. Inputs mm/deg/kg/N presets.
 * Outputs independent world-point, derivative, legacy/render and bounded-fit
 * assertions. Python/real-engine parity is in verify_fixed_spring.py.
 * Experimental quasi-static/numerical checks, not hardware validation.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const c=vm.createContext({console,structuredClone});for(const f of ['reference-v4.js','model.js','preview-geometry.js','suspension-fit.js','dynamic-analysis.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,f),'utf8'),c);
const M=c.Kinefold,D=c.KinefoldDrawing,R=c.KinefoldV4,A=c.KinefoldSuspensionFit,clone=x=>JSON.parse(JSON.stringify(x));let count=0;
const ok=(x,m)=>{assert.ok(x,m);count++;},near=(a,b,t=1e-8)=>ok(Math.abs(a-b)<t,`${a} != ${b}`);
const p={...clone(M.defaults),m2:1,m3:1,m6:.5};let maxEnergyError=0,maxForceError=0;
for(const alpha of [0,20,45]){const z={...p,alpha};ok(!M.validate(z).length,M.validate(z).join(' '));const r=M.reference(z),v=M.springReference(z);
 for(let i=0;i<=100;i++){const theta=z.te+(z.tc-z.te)*i/100,s=R.VSLSpring.state(r,theta),w=R.VSLSpring.state(v,theta),draw=D.spring(z,{A:[11,0,700],theta2:theta,springConvention:M.springConvention});
  near(draw.S[0],11-z.Su);near(draw.S[2],700+z.Sv);near(draw.fixedSeat[2],draw.out[2]);near(draw.movingSeat[2],draw.out[2]);
  const a=(theta+z.nu-alpha)*Math.PI/180;near(draw.D[0],11-z.hornR*Math.cos(a));near(draw.D[2],700+z.hornR*Math.sin(a));
  near(s.force,w.force);near(s.tauS,w.tauS);near(s.delta,w.delta);maxForceError=Math.max(maxForceError,Math.abs(s.force-w.force));
  const eps=1e-4,up=R.VSLSpring.state(r,theta+eps).energy,down=R.VSLSpring.state(r,theta-eps).energy;
  const error=Math.abs((up-down)/(2*eps*Math.PI/180)+s.tauS);maxEnergyError=Math.max(maxEnergyError,error);ok(error<1e-6,'spring work derivative');
  if(alpha===0){const old=R.VSLSpring.state(M.reference(z,M.legacySpringConvention),theta);near(old.force,s.force);near(old.tauS,s.tauS);}
 }
 const legacy=D.spring(z,{A:[0,0,700],theta2:z.theta2,t:0});ok(legacy.springConvention===M.legacySpringConvention,'missing capture token is legacy');
 const oldS=M.point(R.VSL.global(M.reference(z,M.legacySpringConvention),[z.Su,z.Sv]));near(legacy.S[0],oldS[0]);near(legacy.S[2],700+oldS[2]);
}
const tilted={...p,alpha:20},before=JSON.stringify(tilted),fit=A.solve(tilted,clone(A.defaults),{iterations:150,starts:2});
ok(fit.valid,fit.reason);ok(JSON.stringify(tilted)===before,'No input mutation');for(const k of ['springK','Sv','rs','nu'])near(fit.params[k],tilted[k],1e-12);
ok(fit.after.maxTorqueNm<fit.before.maxTorqueNm,'Tilted chassis fit improves sampled peak');
ok(fit.method.includes('chassis-variable'),'World idler locks use chassis-variable search');
const hornOnly=A.solve(tilted,Object.fromEntries(A.keys.map(k=>[k,k!=='hornR'])),{iterations:100,starts:2});
ok(hornOnly.valid&&hornOnly.method.includes('chassis-variable'),'Tilted horn-only search enforces fixed horizontal outlet');near(hornOnly.params.Su,tilted.Su,1e-12);near(hornOnly.params.Sv,tilted.Sv,1e-12);
const mismatch=c.KinefoldDynamicAnalysis.comparison({engine:'analytical',scope:{springConvention:M.springConvention}},{engine:'pymunk',scope:{}});ok(!mismatch.valid&&mismatch.reason.includes('conventions'),'Mixed-convention comparison rejected before numerical comparison');
if(process.argv[2])for(const row of JSON.parse(fs.readFileSync(process.argv[2],'utf8'))){const s=R.VSLSpring.state(M.reference(row.params),row.theta),drawing=D.spring(row.params,{A:[11,0,700],theta2:row.theta,springConvention:M.springConvention});near(s.force,row.force);near(s.tauS,row.torque);near(s.energy,row.energy);near(s.delta,row.delta);for(const key of ['S','D'])for(let i=0;i<3;i++)near(drawing[key][i],row[key][i]);}
console.log(JSON.stringify({status:'PASS',checks:count,maxEnergyErrorNm:maxEnergyError,maxForceErrorN:maxForceError,tiltedFit:{before:fit.before.maxTorqueNm,after:fit.after.maxTorqueNm,params:fit.params}}));
