/** Independent actuator/inertia and optimistic jump screening, not a simulator.
 * Browser: load after reference-v4.js/model.js; Node: require this module.
 * Inputs: builder mm/deg/kg, hardware SI kg m²/Nm/rpm and explicit assumptions.
 * Outputs: generalized inertias, rad/s², stroke times, sampled work and COM apex.
 * Uniform rods; free wheel spin is independent of folding; rigid ideal reduction.
 * Source ratings and assumed torque-speed/loss models do not certify hardware,
 * contact, liftoff, traction, thermal duration, stopping or a complete robot.
 */
(function(root,factory){const api=factory(root);if(typeof module==='object'&&module.exports)module.exports=api;root.KinefoldActuatorCalculator=api;})(globalThis,function(root){
  'use strict';
  const RAD=Math.PI/180,TAU=2*Math.PI,clone=v=>JSON.parse(JSON.stringify(v));
  const finite=(v,label,lo=0,hi=Infinity)=>{if(!Number.isFinite(v)||v<lo||v>hi)throw Error(label+' must be finite in ['+lo+', '+hi+'].');return v;};
  const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],scale=(a,n)=>[a[0]*n,a[1]*n],dot=(a,b)=>a[0]*b[0]+a[1]*b[1];
  function validateParams(input){
    const p=clone(input);
    for(const k of ['L2','L3','ra','rb','rc','rd','re','rf','rw'])finite(p[k],k,1e-9,1e6);
    for(const k of ['m1','m2','m3','m5','m6','g'])finite(p[k],k,0,1e6);
    for(const k of ['alpha','phi0','te','tc','theta2'])finite(p[k],k,-360,360);
    if(!(p.tc>p.te&&p.theta2>=p.te&&p.theta2<=p.tc))throw Error('Require a nonzero working range and an in-range saved pose.');
    if(p.m1+p.m2+p.m3+p.m5+p.m6<=0)throw Error('At least one design mass is required.');
    return p;
  }
  function hardware(input){
    const h=clone(input||{});h.hipBeltRatio=h.hipBeltRatio??1;finite(h.hipBeltRatio,'Hip belt ratio',1,3);h.totalRatio=h.ratio*h.hipBeltRatio;
    for(const k of ['motorPeakNm','motorNoLoadRpm','ratio','efficiency','rotorInertiaKgM2','gearboxInputInertiaKgM2','gearboxOutputInertiaKgM2'])finite(h[k],k,['motorNoLoadRpm','ratio','efficiency'].includes(k)?1e-12:0);
    if(h.efficiency>1)throw Error('Torque transfer efficiency cannot exceed 1.');
    if(h.ratio>1e4||h.motorNoLoadRpm>1e7)throw Error('Reduction or speed exceeds this screening range.');
    for(const k of ['gearboxPeakNm','gearboxInputMaxRpm','gearboxOutputMaxRpm'])if(h[k]!==null&&h[k]!==undefined)finite(h[k],k,0);
    h.torqueModel=h.torqueModel||'linear';if(!['linear','constant'].includes(h.torqueModel))throw Error('Unknown illustrative torque-speed model.');
    const caps=[h.motorNoLoadRpm*TAU/60/h.totalRatio];
    if(Number.isFinite(h.gearboxInputMaxRpm))caps.push(h.gearboxInputMaxRpm*TAU/60/h.totalRatio);
    if(Number.isFinite(h.gearboxOutputMaxRpm))caps.push(h.gearboxOutputMaxRpm*TAU/60/h.hipBeltRatio);
    h.jointSpeedCapRadS=Math.min(...caps);
    h.motorReflectedKgM2=h.totalRatio*h.totalRatio*h.rotorInertiaKgM2;
    h.gearboxReflectedKgM2=h.totalRatio*h.totalRatio*h.gearboxInputInertiaKgM2+h.gearboxOutputInertiaKgM2;
    h.unlimitedJointPeakNm=h.efficiency*h.totalRatio*h.motorPeakNm;
    h.jointPeakNm=Number.isFinite(h.gearboxPeakNm)?Math.min(h.unlimitedJointPeakNm,h.gearboxPeakNm*h.hipBeltRatio):h.unlimitedJointPeakNm;
    h.gearboxTorqueAssessed=Number.isFinite(h.gearboxPeakNm);
    return h;
  }
  function fromCombination(c,overrides={}){
    if(!c)throw Error('Choose a motor and gearbox combination.');
    return {...overrides,motorPeakNm:c.peakMotorTorqueNm,motorNoLoadRpm:c.motorNoLoadRpm,ratio:c.gearRatio,hipBeltRatio:1,efficiency:c.efficiency,
      rotorInertiaKgM2:c.rotorInertiaKgM2,gearboxInputInertiaKgM2:c.gearboxInputInertiaKgM2,
      // Input-equivalent gearbox inertia already includes its rotating train.
      // Zero here means no additional independently specified output inertia.
      gearboxOutputInertiaKgM2:0,gearboxPeakNm:c.gearPeakOutputNm,gearboxInputMaxRpm:c.gearMaxInputRpm,gearboxOutputMaxRpm:c.gearMaxOutputRpm,
      motorId:c.motorId,gearboxId:c.gearboxId,name:c.name,source:clone(c.provenance||{}),...overrides};
  }
  /** Exact q-derivatives, where q is the saved hip angle in radians. */
  function geometry(p,q,fixture='fixed-hip'){
    if(!['fixed-hip','grounded-wheel'].includes(fixture))throw Error('Unknown calculator fixture.');
    const L=p.L2/1000,l=p.L3/1000,k=1-p.ra/p.rb,b=p.phi0*RAD+(Math.PI-q)*(p.ra/p.rb-1),a=p.alpha*RAD;
    const B=[-L*Math.cos(q),-L*Math.sin(q)],Bq=[L*Math.sin(q),-L*Math.cos(q)],Bqq=[L*Math.cos(q),L*Math.sin(q)];
    const C=add(B,[-l*Math.cos(b),-l*Math.sin(b)]),Cq=add(Bq,[l*k*Math.sin(b),-l*k*Math.cos(b)]),Cqq=add(Bqq,[l*k*k*Math.cos(b),l*k*k*Math.sin(b)]);
    const world=v=>[-Math.cos(a)*v[0]-Math.sin(a)*v[1],-Math.sin(a)*v[0]+Math.cos(a)*v[1]];
    const c=[C,Cq,Cqq].map(world),origin=fixture==='grounded-wheel'?[[0,p.rw/1000-c[0][1]],[0,-c[1][1]],[0,-c[2][1]]]:[[0,0],[0,0],[0,0]];
    const pair=(r,v,w)=>[r,v,w].map((x,i)=>add(world(x),origin[i]));
    const sites={
      chassis:{mass:p.m1,rate:0,bodyInertia:0,site:origin},
      upper:{mass:p.m2,rate:1,bodyInertia:p.m2*L*L/12,site:pair(scale(B,.5),scale(Bq,.5),scale(Bqq,.5))},
      lower:{mass:p.m3,rate:k,bodyInertia:p.m3*l*l/12,site:pair(scale(add(B,C),.5),scale(add(Bq,Cq),.5),scale(add(Bqq,Cqq),.5))},
      compound:{mass:p.m5,rate:1-p.rc/p.rd,bodyInertia:.5*p.m5*(Math.max(p.rd,p.re)/1000)**2,site:pair(B,Bq,Bqq)},
      wheel:{mass:p.m6,rate:0,bodyInertia:.5*p.m6*(p.rw/1000)**2,site:pair(C,Cq,Cqq)}
    };
    const totalMass=Object.values(sites).reduce((s,x)=>s+x.mass,0);
    const com=[0,1,2].map(i=>Object.values(sites).reduce((s,x)=>add(s,scale(x.site[i],x.mass/totalMass)),[0,0]));
    return {qRad:q,qDeg:q/RAD,fixture,sites,relativeWheel:c,hip:origin,com,totalMass,lowerRate:k,freeWheelSpin:true};
  }
  function inertia(p,q,h,fixture='fixed-hip'){
    const z=geometry(p,q,fixture),parts={},derivative={};
    for(const [key,x]of Object.entries(z.sites)){parts[key]=x.mass*dot(x.site[1],x.site[1])+x.bodyInertia*x.rate*x.rate;derivative[key]=2*x.mass*dot(x.site[1],x.site[2]);}
    const leg=Object.values(parts).reduce((a,b)=>a+b,0),dJ=Object.values(derivative).reduce((a,b)=>a+b,0);
    const motor=h.totalRatio*h.totalRatio*h.rotorInertiaKgM2,gear=h.totalRatio*h.totalRatio*h.gearboxInputInertiaKgM2+h.gearboxOutputInertiaKgM2;
    return {...z,parts,legKgM2:leg,motorKgM2:motor,gearboxKgM2:gear,totalKgM2:leg+motor+gear,derivativeKgM2Rad:dJ,
      reflectedFraction:(motor+gear)/(leg+motor+gear),reflectedToLegRatio:leg>0?(motor+gear)/leg:null};
  }
  function torque(h,speed){
    const rpm=Math.abs(speed)*h.totalRatio*60/TAU;
    const fraction=h.torqueModel==='constant'?1:Math.max(0,1-rpm/h.motorNoLoadRpm);
    const uncapped=h.efficiency*h.totalRatio*h.motorPeakNm*fraction;
    return Math.min(uncapped,Number.isFinite(h.gearboxPeakNm)?h.gearboxPeakNm*h.hipBeltRatio:Infinity);
  }
  function defaultLosses(h){return [1,3,8].map((percent,i)=>({id:['low','medium','high'][i],name:['Low','Medium','High'][i],
    coulombNm:h.jointPeakNm*percent/100,viscousNms:h.jointPeakNm*percent/100/10,referenceSpeedRadS:10,percent,
    meaning:'Assumed output-side envelope: '+percent+'% peak Coulomb plus '+percent+'% peak viscous drag at 10 rad/s; not measured.'}));}
  function validateLoss(loss){finite(loss.coulombNm,'Output Coulomb torque',0,1e9);finite(loss.viscousNms,'Output viscous coefficient',0,1e9);return {...loss};}
  function lossTorque(loss,speed){return loss.coulombNm+loss.viscousNms*Math.abs(speed);}
  function potential(p,q,fixture,balance='profile'){
    const z=geometry(p,q,fixture);let gravity=0,gravityQ=0,spring=0,springQ=0;
    for(const x of Object.values(z.sites)){gravity+=x.mass*p.g*x.site[0][1];gravityQ+=x.mass*p.g*x.site[1][1];}
    if(balance==='profile'&&p.springEnabled){
      if(!root.KinefoldV4?.VSLSpring)throw Error('The V4 spring reference must be loaded for profile suspension.');
      const r=root.Kinefold?.reference?root.Kinefold.reference(p):{...p,springK:p.springLaw==='constant'?0:p.springK};
      const s=root.KinefoldV4.VSLSpring.state(r,q/RAD);
      if(!s.valid||!Number.isFinite(s.energy)||!Number.isFinite(s.tauS))throw Error(s.reason||'Invalid spring route.');
      if(s.slack)throw Error('Saved spring route is slack; recovery is outside this screening calculation.');
      spring=s.energy;springQ=-s.tauS;
    }
    if(!['profile','gravity-only','ideal-balance'].includes(balance))throw Error('Unknown gravity/suspension calculation mode.');
    return {gravityJ:gravity,springJ:spring,totalJ:gravity+spring,derivativeNm:gravityQ+springQ,
      appliedDerivativeNm:balance==='ideal-balance'?0:gravityQ+springQ,balanced:balance==='ideal-balance'};
  }
  function straightBranch(p){
    if(Math.abs(p.L2-p.L3)>1e-8||Math.abs(p.ra/p.rb-2)>1e-10)throw Error('Jump screen requires equal links and r_a/r_b = 2.');
    const mean=(180+p.phi0)/2;
    for(let n=-3;n<4;n++)if(mean+n*180>=p.te-1e-9&&mean+n*180<=p.tc+1e-9)throw Error('Jump range crosses a reversing/singular straight-path branch.');
    for(const q of [p.te,(p.te+p.tc)/2,p.tc])if(geometry(p,q*RAD,'grounded-wheel').hip[1][1]>=-1e-8)throw Error('Extension must raise chassis height throughout the jump stroke.');
    if(!(p.g>0))throw Error('Jump height requires positive gravity.');
    return true;
  }
  /** Energy-domain integration includes variable generalized inertia exactly in
   * E=J(q)ω²/2. Time uses two-point Gauss quadrature in sqrt(progress), which
   * removes the start-from-rest 1/sqrt(progress) time singularity. Peak sampled.
   */
  function integrateStroke(params,hw,loss,options={}){
    const p=validateParams(params),h=hardware(hw),f=validateLoss(loss),fixture=options.fixture||'fixed-hip',balance=options.balance||(fixture==='fixed-hip'?'ideal-balance':'profile');
    if(fixture==='grounded-wheel')straightBranch(p);
    const q0=(options.startDeg??p.tc)*RAD,q1=(options.endDeg??p.te)*RAD,dir=Math.sign(q1-q0),length=Math.abs(q1-q0),steps=options.steps??1000;
    if(!dir||!Number.isInteger(steps)||steps<20||steps>10000)throw Error('Stroke needs distinct endpoints and 20–10000 integration intervals.');
    if(q0<p.te*RAD-1e-10||q0>p.tc*RAD+1e-10||q1<p.te*RAD-1e-10||q1>p.tc*RAD+1e-10)throw Error('Calculator stroke endpoints must lie within saved physical stops.');
    const at=s=>inertia(p,q0+dir*s,h,fixture),U=s=>potential(p,q0+dir*s,fixture,balance),u0=U(0);
    if(!(at(0).totalKgM2>1e-12))throw Error('Generalized inertia is zero at stroke start.');
    const deriv=(s,state)=>{const z=at(s),speed=Math.sqrt(2*Math.max(0,state[0])/z.totalKgM2),drive=torque(h,speed),drag=lossTorque(f,speed),u=U(s),comp=balance==='ideal-balance'?dir*u.derivativeNm:0;
      return [drive-drag-dir*u.appliedDerivativeNm,drive,drag,comp];};
    const rk=(s,y,ds)=>{const a=deriv(s,y),b=deriv(s+ds/2,y.map((v,i)=>v+ds*a[i]/2)),c=deriv(s+ds/2,y.map((v,i)=>v+ds*b[i]/2)),d=deriv(s+ds,y.map((v,i)=>v+ds*c[i]));return y.map((v,i)=>v+ds*(a[i]+2*b[i]+2*c[i]+d[i])/6);};
    let state=[0,0,0,0],s=0,time=0,status='complete',rows=[];
    const row=()=>{const z=at(s),u=U(s),omega=Math.sqrt(2*Math.max(0,state[0])/z.totalKgM2),drive=torque(h,omega),drag=lossTorque(f,omega),jprime=dir*z.derivativeKgM2Rad;
      const acceleration=(drive-drag-dir*u.appliedDerivativeNm-.5*jprime*omega*omega)/z.totalKgM2;
      const wheel=z.sites.wheel.site,com=z.com;
      return {sRad:s,qDeg:(q0+dir*s)/RAD,timeS:time,speedRadS:omega,speedDegS:omega/RAD,motorRpm:omega*h.totalRatio*60/TAU,
        accelerationRadS2:acceleration,hipAccelerationRadS2:dir*acceleration,driveNm:drive,lossNm:drag,potentialResistingNm:dir*u.appliedDerivativeNm,
        hipVelocityRadS:dir*omega,lowerAbsoluteVelocityRadS:z.lowerRate*dir*omega,relativeKneeVelocityRadS:(z.lowerRate-1)*dir*omega,
        lowerAbsoluteAccelerationRadS2:z.lowerRate*dir*acceleration,relativeKneeAccelerationRadS2:(z.lowerRate-1)*dir*acceleration,
        totalInertiaKgM2:z.totalKgM2,legInertiaKgM2:z.legKgM2,motorInertiaKgM2:z.motorKgM2,gearboxInertiaKgM2:z.gearboxKgM2,
        wheelVelocityXMS:dir*wheel[1][0]*omega,wheelVelocityZMS:dir*wheel[1][1]*omega,
        wheelAccelerationXMS2:dir*wheel[1][0]*acceleration+wheel[2][0]*omega*omega,wheelAccelerationZMS2:dir*wheel[1][1]*acceleration+wheel[2][1]*omega*omega,
        comHeightM:com[0][1],comVerticalVelocityMS:dir*com[1][1]*omega,hipHeightM:z.hip[0][1],hipVerticalVelocityMS:dir*z.hip[1][1]*omega,
        kineticJ:Math.max(0,state[0]),motorWorkJ:state[1],lossWorkJ:state[2],compensationWorkJ:state[3],gravityDeltaJ:u.gravityJ-u0.gravityJ,springDeltaJ:u.springJ-u0.springJ,
        ledgerResidualJ:state[0]-(state[1]-state[2]-(u.totalJ-u0.totalJ)+state[3])};};
    rows.push(row());
    if(deriv(0,state)[0]<=1e-12)status='stalled-at-start';
    else if(!(h.jointSpeedCapRadS>0))status='speed-limit';
    else for(let i=0;i<steps;i++){
      // Uniform sqrt(progress) resolves the non-smooth motor/viscous derivative
      // at rest without hiding it behind an arbitrary initial kinetic energy.
      let ds=length*(2*i+1)/(steps*steps),next=rk(s,state,ds),w0=rows.at(-1).speedRadS;
      const limitEnergy=x=>.5*at(s+x).totalKgM2*h.jointSpeedCapRadS*h.jointSpeedCapRadS;
      let endReason=null;
      if(next[0]<0){let lo=0,hi=ds;for(let j=0;j<45;j++){const mid=(lo+hi)/2;if(rk(s,state,mid)[0]>0)lo=mid;else hi=mid;}ds=(lo+hi)/2;next=rk(s,state,ds);next[0]=0;endReason='stalled-in-stroke';}
      else if(next[0]>limitEnergy(ds)*(1+1e-10)){let lo=0,hi=ds;for(let j=0;j<45;j++){const mid=(lo+hi)/2;if(rk(s,state,mid)[0]<limitEnergy(mid))lo=mid;else hi=mid;}ds=(lo+hi)/2;next=rk(s,state,ds);endReason='speed-limit';}
      const w1=Math.sqrt(2*Math.max(0,next[0])/at(s+ds).totalKgM2);
      let dt;
      if(endReason==='stalled-in-stroke')dt=2*ds/(w0+w1);
      else{
        const u0=Math.sqrt(s),u1=Math.sqrt(s+ds),um=(u0+u1)/2,half=(u1-u0)/2;
        dt=0;for(const node of [-1/Math.sqrt(3),1/Math.sqrt(3)]){const u=um+half*node,progress=u*u,partial=rk(s,state,progress-s),omega=Math.sqrt(2*Math.max(0,partial[0])/at(progress).totalKgM2);dt+=half*2*u/omega;}
      }
      if(!Number.isFinite(dt)||dt<0){status='unresolved-time';break;}
      time+=dt;s+=ds;state=next;rows.push(row());
      if(time>(options.maxTimeS??30)){status='time-limit';break;}
      if(endReason){status=endReason;break;}
    }
    const first=rows[0],last=rows.at(-1),peak=rows.reduce((a,b)=>b.accelerationRadS2>a.accelerationRadS2?b:a,first);
    return {fixture,balance,loss:f,hardware:h,status,complete:status==='complete',rows,start:first,end:last,strokeTimeS:time,
      angularTravelRad:s,requestedTravelRad:length,initialAccelerationRadS2:first.accelerationRadS2,sampledPeakAccelerationRadS2:peak.accelerationRadS2,
      sampledPeakPoseDeg:peak.qDeg,sampledPeakSpeedRadS:Math.max(...rows.map(r=>r.speedRadS)),
      maxAbsLedgerResidualJ:Math.max(...rows.map(r=>Math.abs(r.ledgerResidualJ))),method:'RK4 energy-domain; finite stroke/peak sampling; no contact/liftoff detection'};
  }
  function estimateJump(p,h,loss,options={}){
    const r=integrateStroke(p,h,loss,{...options,fixture:'grounded-wheel',balance:options.balance||'profile'}),end=r.end;
    const totalMass=p.m1+p.m2+p.m3+p.m5+p.m6,v=end.comVerticalVelocityMS;
    const height=r.complete&&v>0?v*v/(2*p.g):null,ballisticEnergy=r.complete&&v>0?.5*totalMass*v*v:null;
    return {...r,estimatedJumpHeightM:height,takeoffComSpeedMS:r.complete?v:null,ballisticComEnergyJ:ballisticEnergy,
      excludedInternalOrHorizontalKineticJ:ballisticEnergy===null?null:end.kineticJ-ballisticEnergy,
      totalMassKg:totalMass,comStanceRiseM:end.comHeightM-r.start.comHeightM,
      meaning:'Optimistic vertical COM apex above takeoff COM, if the full stroke can release into flight. Grounded wheel height, sliding x, fixed chassis x/pitch. No liftoff/reaction/traction/stop/impact test; rotor and internal/horizontal kinetic energy are not converted into vertical COM flight.'};
  }
  function accelerationCurve(p,h,loss,qDeg=p.theta2,options={}){
    const z=inertia(p,qDeg*RAD,h,'fixed-hip'),u=potential(p,qDeg*RAD,'fixed-hip',options.balance||'ideal-balance'),dir=-1;
    return Array.from({length:121},(_,i)=>{const speed=h.jointSpeedCapRadS*i/120,drive=torque(h,speed),drag=lossTorque(loss,speed);
      return {speedRadS:speed,motorRpm:speed*h.totalRatio*60/TAU,driveNm:drive,lossNm:drag,accelerationRadS2:(drive-drag-dir*u.appliedDerivativeNm-.5*dir*z.derivativeKgM2Rad*speed*speed)/z.totalKgM2};});
  }
  function idealRatioSweep(p,h,qDeg=p.theta2){
    const z=inertia(p,qDeg*RAD,h),J=z.legKgM2+h.gearboxOutputInertiaKgM2,j=h.rotorInertiaKgM2+h.gearboxInputInertiaKgM2;
    const optimum=j>0&&J>0?Math.sqrt(J/j):null,maximum=Math.min(500,Math.max(100,optimum?2*optimum:100));
    const rows=Array.from({length:201},(_,i)=>{const N=1+(maximum-1)*i/200,total=J+N*N*j;return {ratio:N,reflectedInertiaKgM2:N*N*j,totalInertiaKgM2:total,zeroSpeedAccelerationRadS2:total>0?h.efficiency*N*h.motorPeakNm/total:null};});
    return {optimumRatio:optimum,rows,meaning:'Hypothetical zero-speed reduction sweep: same selected input-equivalent inertias and efficiency at every N, no gearbox torque cap, losses or speed constraints. These are not catalog SKUs or a hardware optimum.'};
  }
  function calculate(project,inputHardware,options={}){
    const p=validateParams(project.params||project),h=hardware(inputHardware),losses=(options.losses||defaultLosses(h)).map(validateLoss);
    if(losses.length<1||losses.length>6)throw Error('Choose one to six loss assumptions.');
    const fixedBalance=options.fixedBalance||'ideal-balance',jumpBalance=options.jumpBalance||'profile';
    const current=inertia(p,p.theta2*RAD,h),poses=Array.from({length:181},(_,i)=>{const q=p.te+(p.tc-p.te)*i/180,z=inertia(p,q*RAD,h);return {qDeg:q,legKgM2:z.legKgM2,motorKgM2:z.motorKgM2,gearboxKgM2:z.gearboxKgM2,totalKgM2:z.totalKgM2,
      zeroSpeedAccelerationRadS2:h.jointPeakNm/z.totalKgM2};});
    const cases=losses.map(loss=>{
      const free=integrateStroke(p,h,loss,{balance:fixedBalance,steps:options.steps||1000});let jump,jumpError=null;
      try{jump=estimateJump(p,h,loss,{balance:jumpBalance,steps:options.steps||1000});}catch(e){jumpError=e.message;jump=null;}
      const zeroSpeedPoses=poses.map(z=>{const u=potential(p,z.qDeg*RAD,'fixed-hip',fixedBalance);return {qDeg:z.qDeg,accelerationRadS2:(h.jointPeakNm-loss.coulombNm+u.appliedDerivativeNm)/z.totalKgM2};});
      return {loss,free,jump,jumpError,zeroSpeedPoses,accelerationCurve:accelerationCurve(p,h,loss,p.theta2,{balance:fixedBalance})};});
    const targetJumpHeightM=options.targetJumpHeightM??2;finite(targetJumpHeightM,'Target jump height',0,100);
    const compare=[];
    for(const candidate of (options.candidates||[]).slice(0,16)){
      try{const ch=hardware(candidate.hardware||candidate),loss=losses[Math.min(1,losses.length-1)],z=inertia(p,p.theta2*RAD,ch);
        const free=integrateStroke(p,ch,loss,{balance:fixedBalance,steps:240});let jump=null;try{jump=estimateJump(p,ch,loss,{balance:jumpBalance,steps:240});}catch{}
        compare.push({name:candidate.name||ch.name||'Candidate',ratio:ch.totalRatio,peakJointNm:ch.jointPeakNm,totalInertiaKgM2:z.totalKgM2,motorInertiaKgM2:z.motorKgM2,gearboxInertiaKgM2:z.gearboxKgM2,initialAccelerationRadS2:free.initialAccelerationRadS2,strokeTimeS:free.complete?free.strokeTimeS:null,terminalSpeedRadS:free.end.speedRadS,jumpHeightM:jump?.estimatedJumpHeightM??null,status:free.status,hardware:ch});
      }catch(e){compare.push({name:candidate.name||'Candidate',error:e.message});}
    }
    return {schema:'kinefold/actuator-calculator-v1',profile:{id:project.id||null,name:project.name||'Mechanism snapshot',params:p},hardware:h,
      options:{fixedBalance,jumpBalance,targetJumpHeightM,steps:options.steps||1000},current,poses,cases,compare,idealRatioSweep:idealRatioSweep(p,h),
      assumptions:clone(options.assumptions||[]),warning:'Independent preliminary calculator. Peak ratings plus illustrative torque-speed/loss assumptions do not establish a safe continuous actuator envelope or simulated jump.'};
  }
  function plotSpecs(result){
    const colors=['#198475','#c68b24','#a84a49','#5875a0','#875891','#4b5e36'];
    const trace=(x,y,name,color,extra={})=>({type:'scatter',mode:'lines',x,y,name,line:{color,width:2},...extra});
    const specs=[
      {id:'actuator-inertia',title:'Where joint inertia comes from',xLabel:'Hip angle θ₂ · deg',yLabel:'Generalized inertia · kg m²',traces:[['legKgM2','Link + wheel motion','#198475'],['motorKgM2','Reflected motor','#5875a0'],['gearboxKgM2','Reflected gearbox','#c68b24'],['totalKgM2','Total','#263c33']].map(([k,n,c])=>trace(result.poses.map(r=>r.qDeg),result.poses.map(r=>r[k]),n,c))},
      {id:'actuator-ideal-ratio',title:'Why more reduction eventually slows acceleration · ideal sweep',xLabel:'Hypothetical total reduction N · not catalog SKUs',yLabel:'Zero-speed ideal acceleration · rad/s²',traces:[trace(result.idealRatioSweep.rows.map(r=>r.ratio),result.idealRatioSweep.rows.map(r=>r.zeroSpeedAccelerationRadS2),'No torque cap or drag','#5875a0')]},
      {id:'actuator-acceleration',title:'Acceleration vs speed at saved pose',xLabel:'Extension speed |q̇| · rad/s',yLabel:'Extension acceleration · rad/s²',traces:result.cases.map((c,i)=>trace(c.accelerationCurve.map(r=>r.speedRadS),c.accelerationCurve.map(r=>r.accelerationRadS2),c.loss.name,colors[i]))},
      {id:'actuator-zero-speed',title:'Zero-speed extension acceleration across poses',xLabel:'Hip angle θ₂ · deg',yLabel:'Initial extension acceleration · rad/s²',traces:result.cases.map((c,i)=>trace(c.zeroSpeedPoses.map(r=>r.qDeg),c.zeroSpeedPoses.map(r=>r.accelerationRadS2),c.loss.name,colors[i]))},
      {id:'actuator-speed',title:'Finite extension stroke · speed and time',xLabel:'Time · s',yLabel:'Extension speed |q̇| · rad/s',traces:result.cases.map((c,i)=>trace(c.free.rows.map(r=>r.timeS),c.free.rows.map(r=>r.speedRadS),c.loss.name+' · '+c.free.status,colors[i]))},
      {id:'actuator-stroke-acceleration',title:'Sampled acceleration through the extension',xLabel:'Hip angle θ₂ · deg',yLabel:'Extension acceleration · rad/s²',traces:result.cases.map((c,i)=>trace(c.free.rows.map(r=>r.qDeg),c.free.rows.map(r=>r.accelerationRadS2),c.loss.name,colors[i]))},
      {id:'actuator-jump-height',title:'Conditional COM jump estimate',xLabel:'Extension progress · rad',yLabel:'Ballistic COM height v_COM,z²/(2g) · m',traces:result.cases.filter(c=>c.jump).map((c,i)=>trace(c.jump.rows.map(r=>r.sRad),c.jump.rows.map(r=>Math.max(0,r.comVerticalVelocityMS)**2/(2*result.profile.params.g)),c.loss.name+' · '+c.jump.status,colors[i]))},
      {id:'actuator-jump-work',title:'Jump work and kinetic energy · medium losses',xLabel:'Extension progress · rad',yLabel:'Energy · J',traces:[]}
    ];
    const middle=result.cases[Math.min(1,result.cases.length-1)].jump;
    if(middle)specs.at(-1).traces=[['motorWorkJ','Motor delivered','#5875a0'],['lossWorkJ','Coulomb + viscous loss','#a84a49'],['gravityDeltaJ','Gravity increase','#c68b24'],['springDeltaJ','Spring change','#198475'],['kineticJ','Total kinetic','#263c33']].map(([k,n,c])=>trace(middle.rows.map(r=>r.sRad),middle.rows.map(r=>r[k]),n,c));
    const free=result.cases[Math.min(1,result.cases.length-1)].free;
    specs.push({id:'actuator-link-rates',title:'Hip, lower-link absolute and relative-knee speeds · medium losses',xLabel:'Time · s',yLabel:'Signed angular velocity · rad/s',traces:[['hipVelocityRadS','Hip θ₂','#5875a0'],['lowerAbsoluteVelocityRadS','Lower absolute θ₃','#198475'],['relativeKneeVelocityRadS','Relative knee θ₃−θ₂','#c68b24']].map(([k,n,c])=>trace(free.rows.map(r=>r.timeS),free.rows.map(r=>r[k]),n,c))});
    const jumpSpec=specs.find(s=>s.id==='actuator-jump-height'),maxS=Math.max(0,...result.cases.filter(c=>c.jump).map(c=>c.jump.angularTravelRad));
    if(maxS>0)jumpSpec.traces.push(trace([0,maxS],[result.options.targetJumpHeightM,result.options.targetJumpHeightM],'Target COM height','#a84a49',{line:{color:'#a84a49',width:1.3,dash:'dash'}}));
    if(result.compare.length){const rows=result.compare.filter(c=>!c.error);specs.push({id:'actuator-comparison',title:'Exact catalog combinations · inertia and acceleration',xLabel:'Total reduction N',yLabel:'Initial extension acceleration · rad/s²',traces:[{type:'scatter',mode:'markers',x:rows.map(r=>r.ratio),y:rows.map(r=>r.initialAccelerationRadS2),text:rows.map(r=>r.name),name:'Selected catalog combinations',marker:{color:'#5875a0',size:10},hovertemplate:'%{text}<br>N=%{x}<br>%{y:.3f} rad/s²<extra></extra>'}]});}
    return specs;
  }
  return {RAD,hardware,fromCombination,validateParams,geometry,inertia,torque,defaultLosses,lossTorque,potential,straightBranch,integrateStroke,estimateJump,accelerationCurve,idealRatioSweep,calculate,plotSpecs};
});
