/** Verify optional finite-link endpoint energy using independent COM geometry.
 * Run node verify-energy-link-masses.cjs from Kinefold. Inputs temporary project
 * fixtures (mm/deg/kg/N); outputs assertion count, no saved profile writes.
 * Checks energy accounting and purity, not contact/takeoff or hardware fidelity.
 */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({});
for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','energy-analysis.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx,{filename:f});
const P=ctx.KinefoldProjects,A=ctx.KinefoldEnergyAnalysis,R=Math.PI/180;
let checks=0;const near=(a,b,t=1e-8)=>{assert.ok(Math.abs(a-b)<=t,`${a} != ${b}`);checks++;};
const clone=x=>{ctx.raw=JSON.stringify(x);return vm.runInContext('JSON.parse(raw)',ctx);};
// Independent trig coordinates, with each uniform rod's COM at its midpoint.
function gravity(p,q){
 const a=q*R,b=(p.phi0+180-q)*R,alpha=p.alpha*R;
 const B=[-p.L2*Math.cos(a),-p.L2*Math.sin(a)],C=[B[0]-p.L3*Math.cos(b),B[1]-p.L3*Math.sin(b)];
 const z=v=>-Math.sin(alpha)*v[0]+Math.cos(alpha)*v[1],h=p.rw-z(C);
 return p.g*(p.m1*h+p.m2*(h+z(B)/2)+p.m3*(h+(z(B)+z(C))/2)+p.m5*(h+z(B))+p.m6*p.rw)/1000;
}
for(const alpha of [0,20,40])for(const phi0 of [0,6])for(const springEnabled of [false,true])for(const kind of ['landing','jump']){
 const p=clone(P.baseline());Object.assign(p.params,{m2:1,m3:.7,m5:.2,m6:.5,alpha,phi0,springEnabled});
 p.motorConfig={...P.motorDefaults,enabled:true,gearRatio:12,hipBeltRatio:2,coggingAmplitudeNm:.03,coggingPeriodsPerRev:7,coggingPhaseDeg:13};
 p.energyConfig={...P.energyDefaults,dropHeightMm:2000};p.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:2000};
 const before=JSON.stringify(p),z=A.workspace(p,kind,{includeLegMasses:true,samples:31});
 const start=gravity(p.params,z.qStartDeg),delta=gravity(p.params,z.qEndDeg)-start;
 const dropMass=p.params.m1+1+.7+.2,flightMass=dropMass+.5;
 const ref=ctx.Kinefold.reference(p.params),spring=q=>springEnabled?ctx.KinefoldV4.VSLSpring.state(ref,q).energy:0;
 const cog=q=>.03/7*Math.cos(7*24*q*R+13*R);
 const passiveDelta=spring(z.qEndDeg)-spring(z.qStartDeg)+cog(z.qEndDeg)-cog(z.qStartDeg);
 const expected=kind==='jump'?delta+flightMass*9.81*2+passiveDelta:dropMass*9.81*2-delta-passiveDelta;
 near(z.workJ,expected);near(z.requiredJointNm,expected/z.angularTravelRad);
 near(z.flightMassKg,flightMass);near(z.stroke.at(-1).gravityDeltaJ,delta);
 for(const row of z.stroke){
  near(row.gravityDeltaJ,gravity(p.params,row.hipAngleDeg)-start);
  near(row.gravityDeltaJ,row.chassisGravityDeltaJ+row.upperLinkGravityDeltaJ+row.lowerLinkGravityDeltaJ+row.compoundGravityDeltaJ);
  near(row.kineticBudgetJ,z.initialKineticBudgetJ+row.motorWorkJ-row.gravityDeltaJ-row.springDeltaJ-row.coggingDeltaJ);
 }
 near(z.endpointKineticBudgetJ,kind==='jump'?flightMass*9.81*2:0);
 if(alpha===0&&phi0===0){
  const effective=p.params.m1+.75*p.params.m2+.25*p.params.m3+.5*p.params.m5;
  near(delta,effective*9.81*(z.endHipHeightMm-z.startHipHeightMm)/1000);
 }
 const curveA=z.curve[10],curveB=z.curve[40],slope=(curveB.netMotorWorkJ-curveA.netMotorWorkJ)/(curveB.heightMm-curveA.heightMm);
 near(slope,(kind==='jump'?flightMass:dropMass)*9.81/1000);
 const off=A.workspace(p,kind,{includeLegMasses:false}),massless=clone(p);massless.params.m2=massless.params.m3=massless.params.m5=0;
 near(off.requiredJointNm,A.workspace(massless,kind).requiredJointNm);
 assert.equal(off.usedLinkMassesKg.upperLink,0);assert.equal(z.usedLinkMassesKg.upperLink,1);assert.equal(JSON.stringify(p),before);checks+=3;
}
// Wheel impact energy is deliberately outside landing's retained energy model;
// wheel flight energy must still raise the jump torque and curve slope.
for(const kind of ['landing','jump']){
 const p=clone(P.baseline());Object.assign(p.params,{m2:1,m3:1,m6:.5});
 const light=A.workspace(p,kind,{includeLegMasses:true});p.params.m6=2.5;
 const heavy=A.workspace(p,kind,{includeLegMasses:true});
 near(heavy.workJ-light.workJ,kind==='landing'?0:2*p.params.g*heavy.selectedHeightMm/1000);
 near(heavy.requiredJointNm-light.requiredJointNm,(kind==='landing'?0:2*p.params.g*heavy.selectedHeightMm/1000)/heavy.angularTravelRad);
}
for(const kind of ['landing','jump']){
 const p=clone(P.baseline()),on=A.workspace(p,kind,{includeLegMasses:true}),off=A.workspace(p,kind,{includeLegMasses:false});
 near(on.requiredJointNm,off.requiredJointNm);near(on.workJ,off.workJ);
 const invalid=clone(p);invalid.params.m2=-1;assert.throws(()=>A.workspace(invalid,kind,{includeLegMasses:false}));checks++;
 assert.throws(()=>A.workspace(p,kind,{includeLegMasses:'yes'}));checks++;
}
console.log('PASS '+checks+' finite/massless Energy assertions; independent tilted COM geometry, ledgers, curve slopes, zero-mass limit and unchanged projects.');
