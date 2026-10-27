/** Independent tilted-mount endpoint-work checks. Run node verify-energy-alpha.cjs.
 * Temporary mm/deg/kg/N fixtures cover rotated link geometry, gravity work,
 * local spring invariance, gearing and signed budgets. No contact trajectory,
 * retained rolling/rotor energy, impact peak or hardware claim is tested.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({});for(const name of ['reference-v4.js','model.js','variables.js','project-store.js','energy-analysis.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+name,'utf8'),ctx,{filename:name});
const P=ctx.KinefoldProjects,A=ctx.KinefoldEnergyAnalysis,V=ctx.KinefoldV4,R=Math.PI/180;
const clone=p=>{ctx.raw=JSON.stringify(p);return vm.runInContext('JSON.parse(raw)',ctx);};
let checks=0,fixtures=0;const ok=(v,s)=>{assert.ok(v,s);checks++;},near=(a,b,t=1e-7)=>ok(Math.abs(a-b)<t,`${a} != ${b}`);
const base=P.baseline();
// Derive each world point directly from the two link vectors, not VSL.state,
// the production guide axis or the phi0=0 cos(alpha) simplification.
function world(p,q){const b=p.phi0+(180-q)*(p.ra/p.rb-1),u=-p.L2*Math.cos(q*R)-p.L3*Math.cos(b*R),v=-p.L2*Math.sin(q*R)-p.L3*Math.sin(b*R);return {u,v,x:-Math.cos(p.alpha*R)*u-Math.sin(p.alpha*R)*v,z:-Math.sin(p.alpha*R)*u+Math.cos(p.alpha*R)*v,h:p.rw+Math.sin(p.alpha*R)*u-Math.cos(p.alpha*R)*v};}
for(const alpha of [0,10,20,30,45])for(const phi0 of [0,20])for(const law of ['v4','constant'])for(const enabled of [false,true])for(const limit of [50,450])for(const H of [0,100,2000])for(const kind of ['jump','landing']){
  const p=clone(base);Object.assign(p.params,{alpha,phi0,springLaw:law,springEnabled:enabled,m6:1.5,...phi0?{te:110}:{}});
  p.motorConfig={...P.motorDefaults,enabled:true,gearRatio:7,coggingAmplitudeNm:.7,coggingPeriodsPerRev:3,coggingPhaseDeg:27};
  p.energyConfig={...P.energyDefaults,dropHeightMm:H,targetClearanceMm:limit};p.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:H};
  const before=JSON.stringify(p),z=A.workspace(p,kind,{samples:41}),m=p.params,start=world(m,z.qStartDeg),end=world(m,z.qEndDeg),ref=ctx.Kinefold.reference(m);
  const d0=V.VSLSpring.geometry(ref,90).payout,Us=q=>{const d=V.VSLSpring.geometry(ref,q).payout-d0;return enabled?(m.p0*d+.5*(law==='constant'?0:m.springK)*d*d)/1000:0;},Uc=q=>.7/3*Math.cos((3*7*q+27)*R);
  const Ug=p.params.m1*m.g*(end.h-start.h)/1000,Ds=Us(z.qEndDeg)-Us(z.qStartDeg),Dc=Uc(z.qEndDeg)-Uc(z.qStartDeg);
  const work=kind==='jump'?Ug+(m.m1+m.m6)*m.g*H/1000+Ds+Dc:m.m1*m.g*H/1000-Ug-Ds-Dc;
  near(z.alphaDeg,alpha);near(z.guideTiltFromDownDeg,alpha-phi0/2);near(z.startHipHeightMm,start.h);near(z.endHipHeightMm,end.h);near(z.startWheelCxMm,start.x);near(z.endWheelCxMm,end.x);near(z.horizontalWheelTravelMm,end.x-start.x);
  near(z.workJ,work);near(z.requiredJointNm,Math.max(0,work/z.angularTravelRad));near(z.requiredShaftNm,z.requiredJointNm/7);
  near(z.stroke.at(-1).gravityDeltaJ,Ug);near(z.stroke.at(-1).springDeltaJ,Ds);near(z.stroke.at(-1).coggingDeltaJ,Dc);
  near(z.endpointKineticBudgetJ,(kind==='jump'?0:m.m1*m.g*H/1000)+(kind==='jump'?1:-1)*z.requiredJointNm*z.angularTravelRad-Ug-Ds-Dc);
  for(const r of z.stroke){const w=world(m,r.hipAngleDeg);near(r.alphaDeg,alpha);near(r.sourcePuMm,w.u);near(r.sourcePvMm,w.v);near(r.wheelCxMm,w.x);near(r.wheelCzMm,w.z);near(r.hipHeightMm,w.h);near(r.horizontalWheelDisplacementMm,w.x-start.x);near(r.underbodyClearanceMm,w.h-50);near(r.kineticBudgetJ,z.initialKineticBudgetJ+r.motorWorkJ-r.gravityDeltaJ-r.springDeltaJ-r.coggingDeltaJ);}
  ok(z.curve.every(r=>r.alphaDeg===alpha),'all CSV curve rows carry mounting pitch');
  if(kind==='landing'){if(limit===450){near(z.endClearanceMm,450);ok(z.limiter==='Target ground clearance','tilted clearance root');}else ok(z.limiter==='Mechanical stop reserve','tilted compression stop');near(A.landingEstimate(p,H,limit).requiredJointNm,z.requiredJointNm);}
  else near(A.jumpEstimate(p,H).jointNm,z.requiredJointNm);
  ok(JSON.stringify(p)===before,'tilted estimator/workspace pure');fixtures++;
}
// For phi0=0, only vertical gravity projection scales with cos(alpha); local
// spring work and the angular work distance must not receive that factor.
for(const law of ['v4','constant'])for(const kind of ['jump','landing']){
 const zero=clone(base);zero.params.springLaw=law;zero.energyConfig={...P.energyDefaults,dropHeightMm:2000};const z0=A.workspace(zero,kind);
 for(const alpha of [10,20,30,45]){const p=clone(zero);p.params.alpha=alpha;const z=A.workspace(p,kind);near(z.angularTravelRad,z0.angularTravelRad);near(kind==='jump'?z.stanceGravityJ:z.gravityCompressionJ,(kind==='jump'?z0.stanceGravityJ:z0.gravityCompressionJ)*Math.cos(alpha*R));near(kind==='jump'?z.springReleaseJ:z.springReleasedJ,kind==='jump'?z0.springReleaseJ:z0.springReleasedJ);}
}
// Independent finite derivative work integration in world coordinates for an
// asymmetric phase and tilted mount, including total conservative potential.
const d=clone(base);Object.assign(d.params,{alpha:30,phi0:20,te:110});d.energyConfig={...P.energyDefaults,dropHeightMm:2000};const z=A.workspace(d,'landing'),ref=ctx.Kinefold.reference(d.params),pot=q=>d.params.m1*d.params.g*world(d.params,q).h/1000+V.VSLSpring.state(ref,q).energy;
let integral=0;const n=2000,dq=(z.qEndDeg-z.qStartDeg)/n,eps=1e-4;for(let i=0;i<=n;i++){const q=z.qStartDeg+i*dq,derivative=(pot(q+eps)-pot(q-eps))/(2*eps*R);integral+=(i===0||i===n?.5:1)*derivative*dq*R;}near(integral,z.stroke.at(-1).gravityDeltaJ+z.stroke.at(-1).springDeltaJ,1e-5);
for(const kind of ['jump','landing'])for(const patch of [{alpha:46},{phi0:20,te:90,tc:95,theta2:92},{phi0:20,te:100}]){const p=clone(base);Object.assign(p.params,patch);assert.throws(()=>A.workspace(p,kind));checks++;}
const low=clone(base);low.params.alpha=45;low.energyConfig={...P.energyDefaults,dropHeightMm:0};const landing=A.workspace(low,'landing');ok(landing.workJ<0&&landing.requiredJointNm===0&&landing.endpointKineticBudgetJ<0&&landing.sampledNegativeInteriorCount>0,'zero brake retains negative unreachable endpoint, not false exact arrest');
low.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:0};const jump=A.workspace(low,'jump');ok(jump.workJ<0&&jump.requiredJointNm===0&&jump.endpointKineticBudgetJ>0,'zero drive retains positive jump surplus');
const baseline=clone(base);baseline.energyConfig={...P.energyDefaults,dropHeightMm:2000};near(A.calculate(baseline).requiredJointNm,232.345151886620,1e-10);
console.log(`PASS ${checks} tilted-energy assertions across ${fixtures} independent endpoint fixtures`);
