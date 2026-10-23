/** Check motor UI command conversion and saved-profile identity without a browser.
 * Run node verify-motor-ui.cjs; inputs deg/Nm/SI motor fixtures. Outputs assertions.
 * Pure equations/validation only; browser controls and physical integration are separate.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({KinefoldStudio:{}});for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','motor-ui.js','dynamic-analysis.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx);
const P=ctx.KinefoldProjects,U=ctx.KinefoldMotorUI,A=ctx.KinefoldDynamicAnalysis;
let checks=0;const ok=(value,label)=>{assert.ok(value,label);checks++;};
const base=P.baseline();base.params.theta2=132.5;const required=-.027168833380;
ok(U.balanceCommand(base,required)===required,'legacy torque unchanged');
for(const basis of ['joint','motor']){
 const c={...P.motorDefaults,enabled:true,gearRatio:10,coggingAmplitudeNm:.03,coggingPeriodsPerRev:3,coggingPhaseDeg:25,commandBasis:basis};const p={...base,motorConfig:c};
 const command=U.balanceCommand(p,required),joint=basis==='motor'?command*c.gearRatio:command;
 const cog=c.gearRatio*c.coggingAmplitudeNm*Math.sin((c.coggingPeriodsPerRev*c.gearRatio*p.params.theta2+c.coggingPhaseDeg)*Math.PI/180);
 ok(Math.abs(joint+cog-required)<1e-12,'converted electromagnetic command cancels fixed-phase cogging');
 ok(A.snapshotKey(p)!==A.snapshotKey(base),'motor model makes results stale');
}
ok(U.balanceCommand({...base,motorConfig:{...P.motorDefaults,coggingAmplitudeNm:10,gearRatio:50,commandBasis:'motor'}},required)===required,'disabled retained values have no conversion effect');
console.log('PASS '+checks+' motor UI conversion assertions');
