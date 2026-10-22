/** Verify flexible spring minimax fit, held inputs and physical torque signs.
 * Run node verify-fit.cjs [--output]. Deterministic mm/deg/N/Nm/kg fixtures;
 * output compact analytical consistency evidence, not global/hardware acceptance.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'v4-pulley.html'),'utf8'),scripts=[...source.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);scripts.forEach(s=>new vm.Script(s));
const {VSLStatic:s,VSLSpring:sp,VSLFit:f,VSLUnassisted:base}=vm.runInNewContext(scripts.slice(0,3).join('\n')+';({VSLStatic,VSLSpring,VSLFit,VSLUnassisted});');
let checks=0;const near=(a,b,eps=1e-6)=>{assert.ok(Math.abs(a-b)<eps,`${a} != ${b}`);checks++;},p={...s.defaults},hold=()=>Object.fromEntries(f.keys.map(k=>[k,true]));
const point={...p,rs:0,Su:0,nu:0,hornR:sp.target(p)/(p.springK*p.Sv),p0:0};
let driving={...hold(),p0:false},single=f.fit(point,{driving});assert.ok(single.valid);near(single.parameters.p0,point.springK*Math.abs(point.Sv-point.hornR));assert.ok(single.maxTorque<1e-7);checks++;
driving={...hold(),springK:false,p0:false};let linear=f.fit({...p,rs:0,Su:0,hornR:80,p0:0},{driving});assert.ok(linear.valid);near(linear.parameters.springK,sp.target(p)/(80*p.Sv));assert.ok(linear.maxTorque<1e-6);checks++;
const start=performance.now(),normal=f.fit({...p,hornR:75,Su:0,p0:200}),empty=f.fit(p,{driving:hold()}),all=f.fit(p,{driving:Object.fromEntries(f.keys.map(k=>[k,false]))});
assert.ok(normal.valid);assert.ok(normal.maxTorque<.08);assert.ok(empty.valid&&empty.free.length===0&&empty.warnings.length);assert.ok(all.valid&&all.free.length===7);assert.ok(all.maxTorque<normal.maxTorque);checks+=5;
for(const result of [single,linear,normal,empty,all]){for(const key of f.keys)if(result.driving[key])near(result.parameters[key],(result===single?point:result===linear?{...p,rs:0,Su:0,hornR:80,p0:0}:result===normal?{...p,hornR:75,Su:0,p0:200}:p)[key],1e-12);}
// Every possible number of driven variables, including seven; randomized masks.
const masks=[];for(let count=0;count<=7;count++)for(let offset=0;offset<2;offset++){const d=hold();for(let i=0;i<count;i++)d[f.keys[(i+offset)%7]]=false;masks.push(d);}
for(const d of masks){const r=f.fit(p,{driving:d,samples:11,iterations:8,starts:1,verification:101});assert.ok(r.valid,JSON.stringify(d));checks++;for(const key of f.keys)if(d[key])near(r.parameters[key],p[key],1e-12);for(let i=0;i<=100;i++){const z=s.solve(r.parameters,100+65*i/100,false);assert.ok(z.valid);assert.ok(Math.abs(z.tau2)<=r.maxTorque+1e-6);checks+=2;}}
for(let theta=100;theta<=270;theta+=2){const z=s.solve(p,theta),un=base.solve(p,theta);if(!z.valid)continue;near(z.tauG,-un.tau2);near(z.tau2+z.tauG+z.tauS,0);near(z.tau2,un.tau2-z.tauS);near(z.maxMoment,0);}
const reverse=s.solve({...p,Fz:-p.Fz},135);assert.ok(reverse.tauG<0);checks++;
const report={checks,defaultDriving:f.defaults,normalFit:{free:normal.free,maxTorque_Nm:normal.maxTorque,theta2:normal.peakTheta,parameters:normal.parameters},allFreeFit:{maxTorque_Nm:all.maxTorque,rs_mm:all.parameters.rs,warnings:all.warnings},linearFit:{k:linear.parameters.springK,p0:linear.parameters.p0,maxTorque_Nm:linear.maxTorque},milliseconds:performance.now()-start};
if(process.argv.includes('--output'))fs.writeFileSync(path.join(__dirname,'v4-flex-fit-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
