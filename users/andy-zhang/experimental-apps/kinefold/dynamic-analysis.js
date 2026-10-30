/** Pure native dynamic chart/comparison and prescribed spatial-floor data.
 * Load after model.js; Node VM tests may call the exported helpers. Inputs use
 * captured builder mm/deg/kg/N and backend seconds/SI energy rows. Outputs are
 * derived chart rows, exact-time/event-side comparisons and world-mm profiles.
 * No interpolated jump peaks, dynamic pin-force solve or collision model.
 */
globalThis.KinefoldDynamicAnalysis = (() => {
  'use strict';
  const palette = ['var(--sage)', 'var(--blue)', 'var(--amber)', 'var(--purple)'];
  const series = (...items) => items.map(([key, label], i) => [key, label, palette[i % palette.length]]);
  const manifest = [
    ['motion', 'input', 'Requested & applied wheel input', 'mm', series(['requestedInputMm', 'Requested square'], ['appliedInputMm', 'Applied input'])],
    ['motion', 'heave', 'Chassis displacement from initial', 'mm', series(['chassisDisplacementMm', 'Chassis heave'])],
    ['motion', 'height', 'World-frame heights', 'mm', series(['chassisZMm', 'Hip A'], ['wheelZMm', 'Wheel centre C'])],
    ['motion', 'speed', 'Chassis vertical speed', 'mm/s', series(['chassisVelocityMmS', 'Chassis speed'])],
    ['motion', 'acceleration', 'Chassis vertical acceleration', 'mm/s²', series(['chassisAccelerationMmS2', 'Chassis acceleration'])],
    ['kinematics', 'angles', 'Physical angles · jumps retained', '°', series(['theta2', 'Hip θ₂'], ['theta3', 'Tibia θ₃'], ['theta5', 'Compound θ₅'], ['theta6', 'Wheel θ₆'])],
    ['kinematics', 'rates', 'Angular rates · between input edges', '°/s', series(['velocityDegS', 'Hip'], ['rate3', 'Tibia'], ['rate5', 'Compound'], ['rate6', 'Wheel'])],
    ['kinematics', 'angular-acceleration', 'Angular acceleration · between input edges', '°/s²', series(['accelerationDegS2', 'Hip'], ['accel3', 'Tibia'], ['accel5', 'Compound'], ['accel6', 'Wheel'])],
    ['kinematics', 'wheel-x', 'Wheel-centre horizontal displacement', 'mm', series(['wheelDisplacementXMm', 'C_x − initial C_x'])],
    ['forces', 'spring', 'Spring cable tension', 'N', series(['Fs', 'Cable tension'])],
    ['forces', 'reaction', 'Signed vertical wheel-input reaction', 'N', series(['inputReactionN', 'Input actuator reaction'])],
    ['forces', 'torques', 'Applied & balance-reference torques', 'N·m', series(['motorTorqueNm', 'Motor command'], ['dampingTorqueNm', 'Damping'], ['tauApplied', 'Command + friction/damping'], ['tauStatic', 'Instantaneous balance reference'])],
    ['energy', 'energy', 'Energy accounting', 'J', series(['kineticJ', 'Kinetic'], ['potentialJ', 'Effective potential'], ['energyJ', 'Total'])],
    ['energy', 'work', 'Cumulative supplied work', 'J', series(['actuatorDampingWorkJ', 'Actuation + damping'], ['inputWorkJ', 'Wheel input'])],
    ['energy', 'residual', 'Work–energy residual', 'J', series(['workEnergyResidualJ', 'E − E₀ − W_act − W_input'])],
    ['energy', 'constraint-position', 'Sampled horizontal chassis constraint error', 'mm', series(['constraintPositionErrorMm', '|x_A|'])],
    ['energy', 'constraint-angle', 'Sampled chassis pitch constraint error', '°', series(['constraintAngleErrorDeg', '|pitch|'])],
  ].map(([group, id, title, unit, keys]) => ({group, id, title, unit, series: keys}));
  const contactManifest = [
    ['motion','contact-heave','Chassis displacement from initial','mm',series(['chassisDisplacementMm','Chassis heave'])],
    ['motion','contact-heights','Actual chassis & wheel heights','mm',series(['chassisZMm','Actual A'],['wheelZMm','Actual C'])],
    ['motion','contact-speed','Actual vertical chassis speed','mm/s',series(['chassisVelocityMmS','Chassis speed'])],
    ['motion','contact-wheel-velocity','Actual wheel-centre velocity','mm/s',series(['wheelVelocityXMmS','+x velocity'],['wheelVelocityZMmS','+z velocity'])],
    ['kinematics','contact-angles','Backdriven physical indices','°',series(['theta2','Hip θ₂'],['theta4','Free drive θ₄'],['theta5','Compound θ₅'],['theta6','Wheel θ₆'])],
    ['kinematics','contact-spin','Actual wheel & backdrive angular rates','°/s',series(['wheelAngularVelocityDegS','Actual wheel spin'],['rate4','Backdriven shaft'],['rate5','Compound'])],
    ['kinematics','contact-guide','Actual guide residual','mm',series(['guideResidualMm','Constraint residual'])],
    ['forces','contact-spring','Spring cable tension','N',series(['Fs','Cable tension'])],
    ['forces','contact-forces','Contact force magnitudes · interval means','N',series(['contactNormalForceN','Normal magnitude'],['contactTangentialForceN','Tangential magnitude'])],
    ['forces','contact-world-forces','Signed contact force on wheel','N',series(['contactForceXN','+x component'],['contactForceZN','+z component'])],
    ['forces','contact-slip','Actual tangential slip · gaps when airborne','mm/s',series(['slipMmS','Contact slip'])],
    ['forces','contact-separation','Terrain separation & penetration','mm',series(['gapMm','Signed gap'],['penetrationMm','Penetration'])],
    ['forces','contact-guide-force','Equivalent guide actuation force','N',series(['guideForceN','Guide force'])],
    ['energy','contact-energy','Mechanical energy','J',series(['kineticJ','Kinetic'],['potentialJ','Potential'],['energyJ','Total'])],
    ['energy','contact-actuator-work','Cumulative hip actuation & damping work','J',series(['actuatorDampingWorkJ','Hip/damping work'])],
    ['motion','case-clearance','Chassis underside clearance · when assessed','mm',series(['chassisClearanceMm','Underside clearance'])],
    ['kinematics','case-motor','Motor / hold / braking torques','N·m',series(['motorTorqueNm','Actual motor command'],['holdTorqueNm','Hold compensation'],['brakeTorqueNm','Braking command'],['demandTorqueNm','Stopping demand estimate'])],
    ['kinematics','case-travel','Working travel & compression','°',series(['theta2','Hip angle'])],
    ['energy','case-kinetic','Body kinetic energy','J',series(['chassisKineticJ','½ m₁ v_A²'],['wheelKineticJ','Wheel translation + rotation'],['linkKineticJ','Two rod links'])],
    ['energy','case-potential','Spring and gravity potential','J',series(['springEnergyJ','Spring energy'],['gravityEnergyJ','Gravity potential'])],
    ['energy','case-work','Motor work and inelastic stop loss','J',series(['motorWorkJ','∫ τ_motor dθ₂'],['stopDissipationJ','Travel-stop loss'])],
    ['energy','case-ledger','Engine energy-ledger residual · refine dt','J',series(['energyBalanceResidualJ','Unresolved ledger residual'],['positionStabilizationJ','Analytical position-projection energy'])],
    ['energy','case-contact-loss','Contact / stop impulse losses','J',series(['contactDissipationJ','Contact impulse loss'],['stopDissipationJ','Travel-stop loss'])],
  ].map(([group,id,title,unit,keys])=>({group,id,title,unit,series:keys}));
  // Conservative differences and per-step accumulators share one engine catalog.
  // Filled output paths illustrate area, never replace the authoritative work.
  const integralManifest = [
    {group:'integrals',id:'integral-event-speed',title:'First wheel contact ≠ chassis arrest',unit:'mm/s',series:series(['chassisVelocityMmS','Chassis +z speed'],['wheelVelocityZMmS','Wheel centre +z speed']),note:'Contact and arrest markers retain actual integration-step states; vertical chassis speed is never clamped to zero on wheel contact. Mechanical bottom-out before arrest remains a failed landing.'},
    {group:'integrals',id:'integral-storage',title:'Signed energy stored / removed since first contact',unit:'J',series:series(['contactSpringStoredJ','Spring stored · recoverable'],['contactMotorRemovedJ','Motor net work removed'],['contactCoggingStoredJ','Cogging stored · recoverable'])},
    {group:'integrals',id:'integral-kinetic',title:'Actual kinetic energy and contact reference',unit:'J',series:series(['kineticJ','Total kinetic'],['chassisKineticJ','Chassis ½m₁v²'],['wheelKineticJ','Wheel kinetic'],['contactInitialKineticJ','Total kinetic at first contact'])},
    {group:'integrals',id:'integral-sources',title:'Signed energy supplied after first contact',unit:'J',series:series(['contactGravityReleasedJ','Gravity released'],['contactTerrainSuppliedJ','Terrain work'],['contactExternalSuppliedJ','Additional load work'])},
    {group:'integrals',id:'integral-losses',title:'Loss accounts and numerical terms · kept separate',unit:'J',series:series(['contactDampingRemovedJ','Joint damping removed'],['contactMotorLossJ','Motor friction loss'],['contactContactLossJ','Contact impulse accounting'],['contactStopLossJ','Stop impulse accounting'],['contactCoupledNumericalLossJ','Coupled native constraint · signed numerical'],['contactProjectionEnergyJ','Position projection · signed numerical'],['contactLedgerResidualJ','Unresolved numerical residual'])},
    {group:'integrals',id:'integral-spring-area',title:'Cable force × payout · sampled area',unit:'N',xKey:'contactCableTravelM',xLabel:'Payout − first-contact payout · m',fill:true,series:series(['contactSpringForceN','Cable force']),note:'ΔUₛ = ∫F dℓ = −∫τₛ dθ₂. Running storage above uses exact potential differences. Filled output-sample paths can overlap on reversal; their union is not signed work.'},
    {group:'integrals',id:'integral-torque-area',title:'Resisting torque × signed hip travel · sampled area',unit:'N·m',xKey:'contactHipTravelRad',xLabel:'θ₂ − first-contact θ₂ · rad',fill:true,series:series(['contactSpringResistingNm','−τ_spring'],['contactMotorResistingNm','−τ_motor']),note:'Positive area during positive compression means stored/removed energy; reversals change the work sign. Cumulative motor work is integrated every engine step; a native rotor uses its actual motor coordinate, whose small constraint residual is reported separately.'},
    {group:'integrals',id:'integral-momentum-area',title:'Chassis kinetic integral · sampled area',unit:'kg·m/s',xKey:'chassisSpeedMagnitudeMS',xLabel:'Chassis speed magnitude |v_A| · m/s',fill:true,series:series(['chassisMomentumMagnitudeKgMS','m₁ |v_A|']),note:'K_chassis = ∫₀^|v| m₁u du = ½m₁v². Wheel contact constrains wheel normal velocity; chassis downward speed continues while the leg compresses. Arrest is a separate event.'},
  ];
  const motorManifest=[
    ['motor','motor-speed','Motor shaft speed','rad/s',series(['motorVelocityRadS','Shaft angular speed'])],
    ['motor','motor-command','Motor and joint electromagnetic torque','N·m',series(['shaftCommandNm','Motor shaft command'],['jointElectromagneticNm','Joint electromagnetic command'])],
    ['motor','motor-passive','Joint-side cogging and friction','N·m',series(['jointCoggingNm','Conservative cogging'],['jointFrictionNm','Motor friction'],['jointPassiveNm','Total motor passive torque'])],
    ['motor','motor-energy','Rotor kinetic and detent potential energy','J',series(['rotorKineticJ','Motor rotor kinetic'],['legacyJointRotorKineticJ','Additional joint inertia kinetic'],['coggingPotentialJ','Cogging potential'])],
    ['motor','motor-loss','Motor dissipated energy','J',series(['motorDissipatedJ','Motor losses'])],
    ['motor','motor-constraint','Rotor kinematic constraint residual','rad/s',series(['rotorConstraintVelocityErrorRadS','Rotor speed residual'])]
    ,['motor','motor-position-residual','Rotor joint-angle constraint residual','rad',series(['rotorConstraintPositionResidualRad','Native rotor − ideal q'])]
    ,['motor','motor-numerical-work','Native rotor constraint work · numerical','J',series(['rotorConstraintImpulseWorkJ','Signed native constraint impulse work'],['coupledConstraintKineticLossJ','Signed coupled free-to-solved KE change'])]
  ].map(([group,id,title,unit,keys])=>({group,id,title,unit,series:keys}));
  const comparisonFields = [
    ['chassisDisplacementMm', 'Chassis displacement', 'mm'],
    ['chassisVelocityMmS', 'Chassis speed', 'mm/s'],
    ['theta2', 'Hip angle', '°'],
    ['Fs', 'Spring tension', 'N'],
    ['inputReactionN', 'Wheel-input reaction', 'N'],
    ['workEnergyResidualJ', 'Work–energy residual', 'J'],
    ['rotorKineticJ','Motor rotor energy','J'],['shaftCommandNm','Motor shaft command','N·m'],
  ];
  const contactComparisonFields = [
    ['chassisDisplacementMm','Chassis displacement','mm'],['chassisVelocityMmS','Chassis speed','mm/s'],
    ['theta2','Hip angle','°'],['wheelAngularVelocityDegS','Wheel spin','°/s'],['Fs','Spring tension','N'],
    ['contactNormalForceN','Contact normal · interval mean','N'],['motorTorqueNm','Motor torque','N·m'],
    ['rotorKineticJ','Motor rotor energy','J'],['shaftCommandNm','Motor shaft command','N·m'],['motorDissipatedJ','Motor dissipated energy','J'],
    ['chassisKineticJ','Chassis kinetic energy','J'],['springStoredJ','Spring stored from run start','J'],['motorRemovedJ','Motor removed from run start','J'],['gravityReleasedJ','Gravity released from run start','J'],['externalWorkJ','Additional load work','J'],['contactSpringStoredJ','Spring stored since each engine contact','J'],['contactMotorRemovedJ','Motor removed since each engine contact','J'],['motorWorkJ','Motor work','J'],['energyBalanceResidualJ','Energy-ledger residual','J'],
  ];
  function stable(value) {
    if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
    if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + stable(value[k])).join(',') + '}';
    return JSON.stringify(value);
  }
  function snapshotKey(snapshot) { return stable({params: snapshot.params, config: snapshot.solverConfig,contact:snapshot.contactConfig||null,case:snapshot.caseConfig||null,motor:snapshot.motorConfig||null,terrain:snapshot.terrainConfig||null}); }
  function integralRow(result,row) {
    const since=row.sinceContact, impact=result.events?.find(e=>e.type==='first-contact')?.state;
    const fields={};
    for(const [key,value] of Object.entries(since||{})) fields['contact'+key[0].toUpperCase()+key.slice(1)]=value;
    const hasContact=!!since&&!!impact;
    return {...row,...fields,contactInitialKineticJ:hasContact?impact.kineticJ:null,
      contactCableTravelM:hasContact?(row.springCablePayoutMm-impact.springCablePayoutMm)/1000:null,
      contactHipTravelRad:hasContact?row.hipAngleRad-impact.hipAngleRad:null,
      contactSpringForceN:hasContact?row.Fs:null,contactSpringResistingNm:hasContact?-row.springTorqueNm:null,
      contactMotorResistingNm:hasContact?-row.motorTorqueNm:null,
      chassisSpeedMagnitudeMS:Math.abs(row.chassisVelocityMmS)/1000,
      chassisMomentumMagnitudeKgMS:result.params.m1*Math.abs(row.chassisVelocityMmS)/1000};
  }
  function integralRows(result,rows,throughArrest=true) {
    const impact=result.events?.find(e=>e.type==='first-contact'), arrest=result.events?.find(e=>e.type==='chassis-arrest');
    const stop=result.events?.find(e=>e.type==='compression-stop');
    const end=throughArrest?Math.min(arrest?.t??Infinity,stop?.t??Infinity):Infinity;
    const start=throughArrest?(impact?.t??0):0;
    const out=rows.filter(r=>r.t>=start-1e-12&&r.t<=end+1e-12).map(r=>({...r}));
    for(const event of result.events||[]) if(event.state&&event.t>=start-1e-12&&event.t<=end+1e-12){
      const state=integralRow(result,{...event.state,sinceContact:event.sinceContact,eventSide:event.type});
      const index=out.findIndex(r=>Math.abs(r.t-event.t)<1e-12);
      if(index>=0)out.splice(index,1);
      out.push(state);
    }
    return out.sort((a,b)=>a.t-b.t);
  }
  function velocityRows(result,rows) {
    const impact=result.events?.find(e=>e.type==='first-contact');
    if(!impact?.state||!rows.length||impact.t<rows[0].t-1e-12||impact.t>rows.at(-1).t+1e-12)return rows;
    const before={...impact.state,eventSide:'before wheel impulse',
      chassisVelocityMmS:impact.preImpulseChassisVelocityMmS,wheelVelocityZMmS:impact.preImpulseWheelVelocityZMmS};
    const index=rows.findIndex(r=>r.t>=impact.t-1e-12);
    const out=[...rows];out.splice(index<0?out.length:index,0,before);return out;
  }
  function enrich(result) {
    const p = result.params, config = result.runConfig, ref = Kinefold.reference(p);
    const ratios = KinefoldV4.VSL.ratios(ref), k3 = 1 - ratios.qab, k5 = 1 - 1 / ratios.qdc;
    const k6 = KinefoldV4.VSL.coefficient(ref), first = result.rows[0];
    return result.rows.map((row, i) => {
      const pose = KinefoldV4.VSL.state(ref, row.theta2), frame = result.frames[i], contact=result.scope?.mode==='terrain-contact';
      const driveRate=contact?ratios.qdc*ratios.qfe*(row.wheelAngularVelocityDegS-k6*row.velocityDegS):0;
      const structuralRotor=!contact||result.engine==='analytical'||!(config.hipRotorInertiaKgM2+(result.motorConfig?.enabled?result.motorConfig.gearRatio**2*result.motorConfig.rotorInertiaKgM2:0));
      const integralFields=contact?integralRow(result,row):{};
      return {...row,...integralFields, chassisDisplacementMm: row.chassisZMm - first.chassisZMm,
        wheelDisplacementXMm: row.CxMm - first.CxMm,
        theta3: pose.t3, theta4:contact?row.theta4:0,theta5: contact?row.theta5:pose.t5, theta6: contact?row.theta6:pose.t6,
        rate3: k3 * row.velocityDegS,rate4:driveRate, rate5: k5 * row.velocityDegS+driveRate/ratios.qdc, rate6: contact?row.wheelAngularVelocityDegS:k6 * row.velocityDegS,
        accel3:Number.isFinite(row.accelerationDegS2)?k3*row.accelerationDegS2:null, accel5:Number.isFinite(row.accelerationDegS2)?k5*row.accelerationDegS2:null, accel6:Number.isFinite(row.accelerationDegS2)?k6*row.accelerationDegS2:null,
        rotorConstraintVelocityErrorRadS:Number.isFinite(row.rotorConstraintVelocityResidualRadS)?row.rotorConstraintVelocityResidualRadS:structuralRotor?0:null,
        rotorConstraintPositionResidualRad:Number.isFinite(row.rotorConstraintPositionResidualRad)?row.rotorConstraintPositionResidualRad:structuralRotor?0:null,
        motorDissipatedJ:Number.isFinite(row.motorDissipatedJ)?row.motorDissipatedJ:Number.isFinite(row.motorFrictionLossJ)?row.motorFrictionLossJ:null,
        motorTorqueNm: Number.isFinite(row.motorTorqueNm)?row.motorTorqueNm:config.hipTorqueNm, dampingTorqueNm: -config.dampingNms * row.velocityDegS * Math.PI / 180,
        workEnergyResidualJ: [row.energyJ,first.energyJ,row.actuatorDampingWorkJ,row.inputWorkJ].every(Number.isFinite)?row.energyJ-first.energyJ-row.actuatorDampingWorkJ-row.inputWorkJ+(Number.isFinite(row.motorFrictionLossJ)?row.motorFrictionLossJ:Number.isFinite(row.motorDissipatedJ)?row.motorDissipatedJ:0):null,
        constraintPositionErrorMm: frame.constraintPositionErrorMm ?? (result.engine === 'analytical' ? 0 : null),
        constraintAngleErrorDeg: frame.constraintAngleErrorDeg ?? (result.engine === 'analytical' ? 0 : null)};
    });
  }
  function comparison(a, b) {

    if (a && b && (a.engine !== 'analytical' || b.engine !== 'pymunk')) return {valid:false,reason:'Choose one analytical run and one Pymunk run.'};
    if (!a || !b) return {valid: false, reason: 'Run both engines on the same captured mechanism and input profile.'};
    if(stable(a.terrainConfig||null)!==stable(b.terrainConfig||null))return {valid:false,reason:'Periodic terrain profiles differ. Run both from the same captured design.'};
    if(stable(a.motorConfig||null)!==stable(b.motorConfig||null))return {valid:false,reason:'Motor/gear profiles differ. Run both from the same captured design.'};
    if (a.scope?.mode !== b.scope?.mode || stable(a.contactConfig||null)!==stable(b.contactConfig||null) || stable(a.caseConfig||null)!==stable(b.caseConfig||null)) return {valid:false,reason:'Interaction, material or case profiles differ. Run both on the same captured snapshot.'};
    const fields=a.scope?.mode==='terrain-contact'?contactComparisonFields:comparisonFields;
    if (!a.designHash || a.designHash !== b.designHash || stable(a.params) !== stable(b.params))
      return {valid: false, reason: 'Mechanism snapshots differ. Run both again from one captured design.'};
    if (stable(a.runConfig) !== stable(b.runConfig)) return {valid: false, reason: 'Input or numerical profiles differ. Run both again with the same profile.'};
    const aa = enrich(a), bb = enrich(b), key = r => r.t.toFixed(8) + '|' + (r.eventSide || 'sample');
    const byTime = new Map(bb.map(row => [key(row), row])), rows = [];
    for (const ar of aa) {
      const br = byTime.get(key(ar));
      if (!br || Math.abs(ar.t - br.t) > 1e-8) continue;
      const row = {t: ar.t, eventSide: ar.eventSide || ''};
      for (const [field] of fields) {
        row[field + 'A'] = ar[field]; row[field + 'P'] = br[field];
        row[field + 'Error'] = Number.isFinite(br[field]) && Number.isFinite(ar[field]) ? br[field] - ar[field] : null;
      }
      rows.push(row);
    }
    if (!rows.length) return {valid: false, reason: 'No matching time/event-side samples; no interpolation or extrapolation is performed.'};
    const stats = fields.map(([field, label, unit]) => {
      const values = rows.map(row => row[field + 'Error']).filter(Number.isFinite);
      return {field, label, unit, count: values.length, maxAbs: values.length ? Math.max(...values.map(Math.abs)) : null,
        rms: values.length ? Math.sqrt(values.reduce((v, x) => v + x * x, 0) / values.length) : null};
    });
    return {valid: true, fields, rows, stats, outcomeA:a.caseMetrics?.outcome||null,outcomeP:b.caseMetrics?.outcome||null, matched: rows.length, analyticalSamples: aa.length, pymunkSamples: bb.length,
      start: rows[0].t, end: rows.at(-1).t, complete: rows.length === aa.length && rows.length === bb.length,
      terminationA: a.diagnostics.termination, terminationP: b.diagnostics.termination};
  }
  function inputAtDistance(config, distance, side = 'right') {
    const height = config.inputHeightMm, high = config.inputPlateauMm, period = high + config.inputGapMm;
    const tolerance = config.inputSpeedMmS * 1e-10, startTolerance = config.inputSpeedMmS * 1e-12;
    if (distance < -startTolerance || (Math.abs(distance) < startTolerance && side === 'left')) return {requested: 0, applied: 0};
    let phase = Math.max(0, distance) % period;
    if (phase < tolerance || period - phase < tolerance) phase = side === 'left' && distance > 0 ? period : 0;
    if (Math.abs(phase - high) < tolerance) phase = side === 'left' ? high - config.inputSpeedMmS * 1e-11 : high;
    const requested = phase < high ? height : 0, rise = config.inputRiseMm;
    if (!requested || !rise) return {requested, applied: requested};
    const u = phase < rise ? phase / rise : phase > high - rise ? (high - phase) / rise : 1;
    return {requested, applied: height * u ** 3 * (10 + u * (-15 + 6 * u))};
  }
  function floor(config, row, wheelX, minX, maxX) {
    const distance = config.inputSpeedMmS * (row.t - config.inputDelayS);
    const period = config.inputPlateauMm + config.inputGapMm, positions = [minX, maxX, wheelX];
    const start = Math.max(0, Math.floor((distance + minX - wheelX) / period) - 1);
    const end = Math.max(start, Math.ceil((distance + maxX - wheelX) / period) + 1);
    for (let n = start; n <= end && n - start < 2000; n++) {
      const origin = wheelX - distance + n * period;
      for (const offset of [0, config.inputRiseMm, config.inputPlateauMm - config.inputRiseMm, config.inputPlateauMm]) {
        const x = origin + offset;
        if (x >= minX && x <= maxX) positions.push(x);
      }
    }
    for (let i = 0; i <= 300; i++) positions.push(minX + (maxX - minX) * i / 300);
    const xs = [...new Set(positions)].filter(x => x >= minX && x <= maxX).sort((a, b) => a - b), requested = [], applied = [];
    for (const x of xs) {
      const d = distance + x - wheelX;
      for (const side of ['left', 'right']) {
        const value = inputAtDistance(config, d, side);
        requested.push([x, value.requested]); applied.push([x, value.applied]);
      }
    }
    return {requested, applied, atWheel: inputAtDistance(config, distance, row.eventSide === 'before' ? 'left' : 'right'), distance, dense: end - start >= 2000};
  }
  return {manifest,contactManifest,integralManifest,motorManifest, comparisonFields, stable, snapshotKey, enrich, integralRow, integralRows, velocityRows, comparison, inputAtDistance, floor};
})();
