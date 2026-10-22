/** Emit exact source-reference fixtures for merged math tests; run with JSON stdin.
 * Inputs: array of {parameters,theta2} in Jonathan mm/deg/kg/N/Nm units.
 * Outputs: compact original-model states as JSON stdout; no files/network/GUI.
 * Limits: geometry/statics reference only, not dynamics or hardware validation.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.resolve(__dirname,'../../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html'),'utf8'),ctx=vm.createContext({});
for(const m of html.matchAll(/<script id="[^"]+">([\s\S]*?)<\/script>/g))vm.runInContext(m[1],ctx);
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const result=input.map(x=>{ctx.p=x.parameters;ctx.t=x.theta2;return JSON.parse(vm.runInContext('JSON.stringify((()=>{const s=VSLStatic.solve(p,t);return {valid:s.valid,B:s.Bg,C:s.Cg,t3:s.t3,t5:s.t5,t6:s.t6,Fn:s.Fn,Ft:s.Ft,Fy:s.Fy,Fz:s.Fz,tau2:s.tau2,tau4:s.tau4,inertia:s.inertia,forceResidual:s.maxForce,momentResidual:s.maxMoment,virtualWorkError:s.virtualWorkError};})())',ctx));});
process.stdout.write(JSON.stringify(result));
