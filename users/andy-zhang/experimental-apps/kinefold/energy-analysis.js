/** Pure chassis-only landing energy screen, without integrating a trajectory.
 * Load after model.js/project-store.js. Inputs mm/deg/kg/N and optional saved
 * energyConfig. Outputs J, Nm, geometry and sufficient endpoint drop capacity.
 * Assumes held vertical flat-floor drop, fixed wheel during compression, rest
 * endpoints, massless moving links; not peak torque or post-arrest stability.
 */
globalThis.KinefoldEnergyAnalysis=(()=>{
  'use strict';
  const R=Math.PI/180;
  // Catalog snapshot transcribed 2026-10-23. Marketing maximum/peak, not continuous.
  const motors=[
    ['flipsky-6374-190','Flipsky 6374 · 190 KV',8],['flipsky-6384-170','Flipsky 6384 · 170 KV · Battle Hardened',9],
    ['flipsky-6354-140','Flipsky 6354 · 140 KV · Battle Hardened',7],['flipsky-6384-140','Flipsky 6384 · 140 KV',9],
    ['flipsky-6374-140','Flipsky 6374 · 140 KV · Battle Hardened',8],['flipsky-7070-110','Flipsky 7070 · 110 KV · Battle Hardened',9.5],
    ['flipsky-6368-140','Flipsky 6368 · 140 KV · Battle Hardened',5],['flipsky-63100-140','Flipsky 63100 · 140 KV · Battle Hardened',10],
    ['flipsky-80100-130','Flipsky 80100 · 130 KV',17]
  ].map(([id,name,peakShaftNm])=>Object.freeze({id,name,peakShaftNm,duration:id==='flipsky-63100-140'?'Maximum torque ≤30 s; transient capability still unverified':'Peak duration unspecified'}));
  const gearboxes=[
    ['eg5','EG23-G5-D10',5,28,56,.96],['eg10','EG23-G10-D10',10,10,20,.96],
    ['eg20','EG23-G20-D10',20,30,60,.94],['eg50','EG23-G50-D10',50,25,50,.94]
  ].map(([id,name,ratio,nominalNm,momentaryNm,forwardEfficiency])=>Object.freeze({id,name,ratio,nominalNm,momentaryNm,forwardEfficiency}));
  function resolveScreen(v){
    if(!v)return null;
    const motor=motors.find(m=>m.id===v.motorId),gearbox=gearboxes.find(g=>g.id===v.gearboxId);
    if(v.motorId!=='custom'&&!motor||!['direct','custom'].includes(v.gearboxId)&&!gearbox)throw Error('Unknown energy motor/gearbox selection.');
    const ratio=gearbox?.ratio??(v.gearboxId==='direct'?1:v.customRatio),momentaryNm=gearbox?.momentaryNm??(v.gearboxId==='custom'?v.customMomentaryNm:null);
    const idealJointPeakNm=v.peakShaftNm*ratio,effectiveJointNm=momentaryNm===null?idealJointPeakNm:Math.min(idealJointPeakNm,momentaryNm);
    return {...v,motorName:motor?.name??'Custom motor',catalogPeakShaftNm:motor?.peakShaftNm??null,peakOverridden:!!motor&&motor.peakShaftNm!==v.peakShaftNm,duration:motor?.duration??'Custom peak duration unassessed',gearboxName:gearbox?.name??(v.gearboxId==='direct'?'Direct drive':'Custom reduction'),ratio,nominalNm:gearbox?.nominalNm??null,momentaryNm,idealJointPeakNm,effectiveJointNm,gearboxAssessed:v.gearboxId!=='custom'||momentaryNm!==null,forwardEfficiency:gearbox?.forwardEfficiency??null};
  }
  function calculate(project){
    const p=project.params,P=KinefoldProjects,V=KinefoldV4;
    const e=P.validateEnergy({...P.energyDefaults,dropHeightMm:project.caseConfig?.landingDropMm??P.caseDefaults.landingDropMm,...project.energyConfig});
    const c={...P.caseDefaults,...project.caseConfig},savedMotor={...P.motorDefaults,...project.motorConfig},screening=resolveScreen(e.screening);
    // Candidate reduction changes conservative cogging phase; never mutate dynamics.
    // Disabled saved passives stay zero. No catalog inertia/loss guesses are made.
    const motor=screening?{...savedMotor,enabled:true,gearRatio:screening.ratio,coggingAmplitudeNm:savedMotor.enabled?savedMotor.coggingAmplitudeNm:0}:savedMotor;
    const availableJointNm=screening?screening.effectiveJointNm:e.torqueLimitNm;
    const errors=Kinefold.validate(p);if(errors.length)throw Error(errors.join(' '));
    if(!(p.m1>0&&p.g>0))throw Error('This drop-height energy screen requires positive chassis mass m₁ and gravity g.');
    if(['m2','m3','m5'].some(k=>p[k]!==0))throw Error('Chassis-only energy assumes massless moving links/compound pulley (m₂=m₃=m₅=0).');
    if(p.loadMode==='contact'||p.loadMode==='global'&&(Math.abs(p.Fx)>1e-12||Math.abs(p.Fz)>1e-12))throw Error('Additional prescribed wheel loads are outside this chassis gravity/spring/cogging screen. Use weight reference or zero additional global loads.');
    if(Math.abs(p.L2-p.L3)>1e-9||Math.abs(p.ra/p.rb-2)>1e-10)throw Error('This fixed-wheel screen requires equal links and r_a/r_b=2 for certified straight travel.');
    const mean=(180+p.phi0)/2,ax=-Math.cos((mean-p.alpha)*R),az=-Math.sin((mean-p.alpha)*R);
    if(Math.abs(ax)>1e-9)throw Error('This energy screen requires a vertical wheel path on stationary flat ground; tilted travel needs a full energy/dynamic model.');
    for(let n=-2;n<4;n++)if(mean+n*180>=p.te-1e-9&&mean+n*180<=p.tc+1e-9)throw Error('Working travel crosses a singular or reversing straight-path branch.');
    const q0=p.tc+c.landingOpenFraction*(p.te-p.tc),stop=p.tc-e.compressionReserveDeg;
    const J=q=>-2*p.L2/1000*Math.sin((q-mean)*R);
    if(!(p.tc>q0&&az*J((q0+p.tc)/2)>0))throw Error('The saved landing opening must compress toward θ_c with decreasing chassis height.');
    if(c.undersideOffsetMm===null)throw Error('Set the shared underside offset below hip A before calculating ground clearance.');
    const ref=Kinefold.reference(p),height=q=>p.rw-V.VSL.state(ref,q).Pg[1],clearance=q=>height(q)-c.undersideOffsetMm;
    const initialClearance=clearance(q0);
    if(initialClearance<=e.targetClearanceMm+1e-8)throw Error('Initial underside clearance is at/below the requested residual clearance; no usable braking stroke remains.');
    if(stop<=q0+1e-8)throw Error('The stop reserve consumes the entire available compression angle. Reduce it or open the initial leg further.');
    let end=stop,limiter=e.compressionReserveDeg>0?'Mechanical stop reserve':'Mechanical stop boundary';
    if(clearance(stop)<e.targetClearanceMm){let lo=q0,hi=stop;for(let i=0;i<65;i++){const mid=(lo+hi)/2;if(clearance(mid)>e.targetClearanceMm)lo=mid;else hi=mid;}end=(lo+hi)/2;limiter='Target ground clearance';}
    const travel=(end-q0)*R;if(!(travel>1e-10))throw Error('No usable compression travel remains.');
    if(p.springEnabled){const span=V.VSLSpring.interval(ref,q0,end),z=V.VSLSpring.geometry(ref,90);if(!span.valid||!z.valid)throw Error(span.reason||z.reason);if(ref.p0+ref.springK*(span.min-z.payout)<-1e-8)throw Error('The cable becomes slack during the braking stroke; slack recovery is outside this energy screen.');}
    const spring=q=>{if(!p.springEnabled)return 0;const z=V.VSLSpring.state(ref,q);if(!z.valid||!Number.isFinite(z.energy))throw Error(z.reason||'Invalid spring energy.');return z.energy;};
    const N=motor.enabled?motor.gearRatio:1,cog=q=>motor.enabled?motor.coggingAmplitudeNm/motor.coggingPeriodsPerRev*Math.cos(motor.coggingPeriodsPerRev*N*q*R+motor.coggingPhaseDeg*R):0;
    const gravityCompressionJ=p.m1*p.g*(height(q0)-height(end))/1000;
    const springReleasedJ=spring(q0)-spring(end),coggingReleasedJ=cog(q0)-cog(end);
    const fixedWorkJ=gravityCompressionJ+springReleasedJ+coggingReleasedJ,weight=p.m1*p.g,dropJ=weight*e.dropHeightMm/1000;
    const requiredJointNm=Math.max(0,(dropJ+fixedWorkJ)/travel),capacityRawMm=(availableJointNm*travel-fixedWorkJ)/weight*1000;
    const terms={dropJ,gravityCompressionJ,springReleasedJ,coggingReleasedJ};
    if(screening){screening.motorPass=requiredJointNm/N<=screening.peakShaftNm+1e-10;screening.gearboxPass=!screening.gearboxAssessed?null:screening.momentaryNm===null||requiredJointNm<=screening.momentaryNm+1e-10;screening.savedPassiveMotorEnabled=savedMotor.enabled;}
    return {config:e,openingFraction:c.landingOpenFraction,undersideOffsetMm:c.undersideOffsetMm,qStartDeg:q0,qEndDeg:end,angularTravelRad:travel,angularTravelDeg:end-q0,
      startHipHeightMm:height(q0),endHipHeightMm:height(end),initialClearanceMm:initialClearance,endClearanceMm:clearance(end),chassisCompressionMm:height(q0)-height(end),limiter,
      boundaryOnly:e.compressionReserveDeg===0&&limiter==='Mechanical stop boundary',massKg:p.m1,gravityMS2:p.g,impactSpeedMS:Math.sqrt(2*p.g*e.dropHeightMm/1000),gearRatio:N,
      requiredJointNm,requiredShaftNm:requiredJointNm/N,availableJointNm,availableShaftNm:availableJointNm/N,screening,
      capacityRawMm,capacityMm:capacityRawMm>=0?capacityRawMm:null,passes:requiredJointNm<=availableJointNm+1e-10&&(!screening||screening.gearboxAssessed),
      workJ:dropJ+fixedWorkJ,availableWorkJ:availableJointNm*travel,...terms,
      curve:Array.from({length:81},(_,i)=>{const drop=Math.min(5000,Math.max(500,e.dropHeightMm*1.5))*i/80;return {dropHeightMm:drop,jointTorqueNm:Math.max(0,(weight*drop/1000+fixedWorkJ)/travel)};})};
  }
  function landingEstimate(project,dropHeightMm,targetClearanceMm){
    // Dynamic-case guidance must use its physical motor, never a catalog candidate.
    const energyConfig={...KinefoldProjects.energyDefaults,...project.energyConfig,dropHeightMm,targetClearanceMm};
    delete energyConfig.screening;
    return calculate({...project,energyConfig});
  }
  function jumpEstimate(project,targetHeightMm){
    const p=project.params,motor={...KinefoldProjects.motorDefaults,...project.motorConfig};
    if(!(p.m1>0&&p.m6>=0&&p.g>0)||!Number.isFinite(targetHeightMm)||targetHeightMm<0)throw Error('Jump work estimate needs positive chassis mass/gravity and a nonnegative height.');
    if(['m2','m3','m5'].some(k=>p[k]!==0)||Math.abs(p.L2-p.L3)>1e-9||Math.abs(p.ra/p.rb-2)>1e-10||Math.abs(Math.cos(((180+p.phi0)/2-p.alpha)*R))>1e-9)throw Error('Ideal jump work estimate requires massless equal links and vertical straight travel.');
    if(p.loadMode==='contact'||p.loadMode==='global'&&(Math.abs(p.Fx)>1e-12||Math.abs(p.Fz)>1e-12))throw Error('Extra wheel loads are outside this gravity-only jump work estimate.');
    const mean=(180+p.phi0)/2;
    for(let n=-2;n<4;n++)if(mean+n*180>=p.te-1e-9&&mean+n*180<=p.tc+1e-9)throw Error('Jump travel crosses a singular or reversing straight-path branch.');
    const ref=Kinefold.reference(p),V=KinefoldV4,travel=(p.tc-p.te)*R;
    if(p.springEnabled){const span=V.VSLSpring.interval(ref,p.te,p.tc),z=V.VSLSpring.geometry(ref,90);if(!span.valid||!z.valid)throw Error(span.reason||z.reason);if(ref.p0+ref.springK*(span.min-z.payout)<-1e-8)throw Error('The jump cable becomes slack within the full stroke; slack recovery is outside this energy screen.');}
    const stanceRiseMm=V.VSL.state(ref,p.tc).Pg[1]-V.VSL.state(ref,p.te).Pg[1];
    if(!(travel>0&&stanceRiseMm>0))throw Error('The extension endpoint must raise the chassis on the supported branch.');
    const spring=q=>{if(!p.springEnabled)return 0;const z=V.VSLSpring.state(ref,q);if(!z.valid)throw Error(z.reason);return z.energy;};
    const N=motor.enabled?motor.gearRatio:1,cog=q=>motor.enabled?motor.coggingAmplitudeNm/motor.coggingPeriodsPerRev*Math.cos(motor.coggingPeriodsPerRev*N*q*R+motor.coggingPhaseDeg*R):0;
    const stanceGravityJ=p.m1*p.g*stanceRiseMm/1000,flightEnergyJ=(p.m1+p.m6)*p.g*targetHeightMm/1000;
    const springReleaseJ=spring(p.tc)-spring(p.te),coggingReleaseJ=cog(p.tc)-cog(p.te);
    const jointNm=Math.max(0,(stanceGravityJ+flightEnergyJ-springReleaseJ-coggingReleaseJ)/travel);
    return {jointNm,shaftNm:jointNm/N,stanceRiseMm,stanceGravityJ,flightEnergyJ,springReleaseJ,coggingReleaseJ,angularTravelRad:travel,
      meaning:'Optimistic work screen: full extension at takeoff, locked relative pose during flight, all mass rises together; no stop/contact/friction loss or retained rotor kinetic energy. Not guaranteed takeoff or apex.'};
  }
  return {calculate,landingEstimate,jumpEstimate,motors:Object.freeze(motors),gearboxes:Object.freeze(gearboxes)};
})();
