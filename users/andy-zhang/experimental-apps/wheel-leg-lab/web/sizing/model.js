/** Suspension sizing screen. Import in browser or run node --test tests/sizing.test.js.
 * Inputs: explicit SI geometry, kg, N, rad, s; sheet-derived motor and gearbox catalog.
 * Outputs: ideal generalized loads and conditional current/power/speed envelopes.
 * Limits: fixed 2:1 guide, no contact/thermal/IR-drop/rotor-inertia/strength validation.
 */
export const G = 9.80665;
export const DEFAULTS = Object.freeze({upper:.24,lower:.24,chassis:20,payload:7.5,supports:4,
  upperMass:.35,lowerMass:.35,wheelMass:.9,springForce:65,anchor:.15,attachment:.5,
  minAngle:20,maxAngle:70,speed:.10,acceleration:1,actuator:1,voltage:36,current:20,
  reserve:.85,safety:1.25,mode:'nominal',mapMinMass:5,mapMaxMass:65,mapMinLink:.12,mapMaxLink:.45});
export function validate(p) {
  for(const [k,v] of Object.entries(DEFAULTS)) if(typeof v==='number' && !Number.isFinite(p[k])) throw Error(`${k} must be a finite number.`);
  for(const k of ['upper','lower','anchor','voltage','current','safety','mapMinLink','mapMaxLink']) if(p[k]<=0) throw Error(`${k} must be positive.`);
  for(const k of ['chassis','payload','upperMass','lowerMass','wheelMass','springForce','speed','acceleration','mapMinMass']) if(p[k]<0) throw Error(`${k} cannot be negative.`);
  if(!Number.isInteger(p.supports)||p.supports<1||p.supports>4)throw Error('Supporting corners must be 1–4.');
  if(![1,2].includes(p.actuator))throw Error('Choose hip or relative-knee actuator.');
  if(p.minAngle<1||p.maxAngle>85||p.minAngle>=p.maxAngle)throw Error('Use an increasing working window between 1° and 85°; vertical is singular.');
  if(p.attachment<=0||p.attachment>1||p.reserve<=0||p.reserve>1||p.safety<1)throw Error('Check attachment, voltage reserve and margin bounds.');
  if(p.mapMinMass>=p.mapMaxMass||p.mapMinLink>=p.mapMaxLink)throw Error('Map minimums must be below maximums.');
  if(!['nominal','momentary'].includes(p.mode))throw Error('Unknown gearbox envelope mode.');
  return p;
}
export function support(p) {
  const a=p.upper,b=p.lower,S=a+b,M=(p.chassis+p.payload)/p.supports;
  return G*(M*S+p.upperMass*(a/2+b)+p.lowerMass*b/2)/S;
}
export function spring(p) {
  const R=p.upper*p.attachment,H=p.anchor,k=p.springForce*(p.upper+p.lower)/(H*R);
  return {R,H,k};
}
export function pose(p,theta,velocity=p.speed,acceleration=0) {
  const a=p.upper,b=p.lower,S=a+b,s=Math.sin(theta),c=Math.cos(theta),J=S*c;
  if(Math.abs(J)<1e-7)throw Error('Vertical Jacobian is singular.');
  const M=(p.chassis+p.payload)/p.supports,mu=p.upperMass,ml=p.lowerMass,mw=p.wheelMass;
  const A=mu*a*a/4+ml*(a-b/2)**2+mw*(a-b)**2;
  const B=M*S*S+mu*(a/2+b)**2+ml*b*b/4;
  const inertia=A*s*s+B*c*c+(mu*a*a+ml*b*b)/12;
  const derivative=2*(A-B)*s*c;
  const qdot=velocity/J,qddot=(acceleration+S*s*qdot*qdot)/J;
  const gravity=support(p)*J,assist=p.springForce*J;
  const dynamic=inertia*qddot+.5*derivative*qdot*qdot;
  const torque=(gravity-assist+dynamic)/p.actuator,omega=qdot*p.actuator;
  const {H,R,k}=spring(p),span=Math.sqrt(H*H+R*R-2*H*R*s);
  return {theta,angle:theta*180/Math.PI,height:S*s,x:(a-b)*c,J,qdot,qddot,
    gravity:gravity/p.actuator,assist:assist/p.actuator,dynamic:dynamic/p.actuator,
    torque,rpm:omega*60/(2*Math.PI),power:torque*omega,span,tension:k*span,inertia};
}
export function sweep(p,count=101) {
  validate(p);const rows=[];
  for(let i=0;i<count;i++) {
    const theta=(p.minAngle+(p.maxAngle-p.minAngle)*i/(count-1))*Math.PI/180;
    // Pointwise rectangular bounds, not a time trajectory: either travel direction,
    // acceleration sign and rest. Avoid pretending these extremes occur in one cycle.
    const variants=[pose(p,theta,0,0)];
    for(const v of [-p.speed,p.speed])for(const ac of [-p.acceleration,0,p.acceleration])variants.push(pose(p,theta,v,ac));
    rows.push({...pose(p,theta),variants,requiredTorque:Math.max(...variants.map(r=>Math.abs(r.torque)))*p.safety});
  }
  return rows;
}
export function capacity(motor,gear,p,rpm) {
  const inputRpm=Math.abs(rpm)*gear.ratio;
  const speedLimit=Math.min(motor.kv*p.voltage*p.reserve,p.mode==='nominal'?gear.ratedRpm:gear.maxRpm);
  if(inputRpm>speedLimit+1e-9)return 0;
  const phaseCurrent=Math.min(p.current,motor.maxCurrent);
  const motorTorque=Math.min(motor.kt*phaseCurrent,motor.peakTorque,inputRpm>0?motor.maxPower/(inputRpm*2*Math.PI/60):Infinity);
  return Math.min(motorTorque*gear.ratio*gear.efficiency,p.mode==='nominal'?gear.nominalTorque:gear.momentaryTorque);
}
export function maxRpm(motor,gear,p) {
  return Math.min(motor.kv*p.voltage*p.reserve,p.mode==='nominal'?gear.ratedRpm:gear.maxRpm)/gear.ratio;
}
export function utilization(rows,motor,gear,p) {
  let torqueRatio=0,speedRatio=0;
  for(const row of rows) for(const r of row.variants) {
    const rpm=Math.abs(r.rpm),speed=rpm/maxRpm(motor,gear,p);
    const available=capacity(motor,gear,p,Math.min(rpm,maxRpm(motor,gear,p)));
    torqueRatio=Math.max(torqueRatio,available>0?Math.abs(r.torque)*p.safety/available:Infinity);
    speedRatio=Math.max(speedRatio,speed);
  }
  return {torqueRatio,speedRatio,ratio:Math.max(torqueRatio,speedRatio),fits:torqueRatio<=1&&speedRatio<=1};
}
export function designMap(p,motor,gear,size=27) {
  const masses=Array.from({length:size},(_,i)=>p.mapMinMass+(p.mapMaxMass-p.mapMinMass)*i/(size-1));
  const lengths=Array.from({length:size},(_,i)=>p.mapMinLink+(p.mapMaxLink-p.mapMinLink)*i/(size-1));
  const ratio=p.lower/p.upper,{k,H}=spring(p);
  // Same physical spring stiffness/anchor, attachment stays at its link fraction.
  const z=masses.map(chassis=>lengths.map(upper=>{
    const lower=upper*ratio,force=k*H*upper*p.attachment/(upper+lower);
    const trial={...p,chassis,upper,lower,springForce:force};
    return utilization(sweep(trial,41),motor,gear,trial).ratio;
  }));
  return {masses,lengths,z};
}
export function parseCSV(text) {
  const rows=[];let row=[],value='',quoted=false;
  for(let i=0;i<text.length;i++) {const c=text[i];
    if(c==='"'){if(quoted&&text[i+1]==='"'){value+='"';i++;}else quoted=!quoted;}
    else if(c===','&&!quoted){row.push(value);value='';}
    else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(value);if(row.some(x=>x!==''))rows.push(row);row=[];value='';}
    else value+=c;
  }
  if(quoted)throw Error('CSV has an unclosed quote.');
  row.push(value);if(row.some(x=>x!==''))rows.push(row);if(rows[0])rows[0][0]=rows[0][0].replace(/^\uFEFF/,'');return rows;
}
export function catalogCSV(text,kind) {
  const rows=parseCSV(text),headers=rows.shift()||[];
  const required=kind==='motors'?['Model','Kv (rpm/V)','Converted Kt','Peak/stall τ (N·m)','Rated/max P (W)','Peak/stall I (A)']:
    ['Model','Ratio','Nominal output torque (N m)','Momentary output torque (N m)','Efficiency','Rated input (rpm)','Max input (rpm)'];
  required.forEach(h=>{if(!headers.includes(h))throw Error(`Missing sheet column: ${h}`);});
  const get=(r,h)=>r[headers.indexOf(h)]??'';
  const number=(r,h)=>{const s=get(r,h).replace(/,/g,'').trim();if(!s)throw Error(`${get(r,'Model')}: missing ${h}`);const n=Number(s.replace('%',''));if(!Number.isFinite(n)||n<=0)throw Error(`Invalid ${h}`);return n;};
  const out=rows.filter(r=>kind==='motors'?get(r,'Model').startsWith('Flipsky'):get(r,'Model').trim()).map(r=>{
    const base={model:get(r,'Model'),source:'',notes:'Imported from user-selected Sheet CSV. Source links remain in the workbook.'};
    if(kind==='motors')return {...base,kv:number(r,required[1]),kt:number(r,required[2]),peakTorque:number(r,required[3]),maxPower:number(r,required[4]),maxCurrent:number(r,required[5]),mass:null};
    let efficiency=number(r,'Efficiency');if(get(r,'Efficiency').includes('%'))efficiency/=100;
    if(efficiency>1)throw Error('Efficiency must be 0–1 or include %.');
    const ratio=number(r,'Ratio'),ratedRpm=number(r,'Rated input (rpm)'),maxRpm=number(r,'Max input (rpm)');
    const nominalTorque=number(r,required[2]),momentaryTorque=number(r,required[3]);
    if(maxRpm<ratedRpm||momentaryTorque<nominalTorque)throw Error('Gearbox maximum must not be below nominal.');
    return {...base,ratio,efficiency,ratedRpm,maxRpm,nominalTorque,momentaryTorque,mass:null,condition:get(r,'Condition')};
  });
  if(!out.length)throw Error('No usable catalog rows found.');
  if(new Set(out.map(r=>r.model)).size!==out.length)throw Error('Duplicate model IDs.');
  return out;
}
