/** Ideal open guide-belt geometry and derived force visualization.
 * Invocation: import from the browser bench or node --test tests/guide-belt.test.js.
 * Inputs: world coordinates/radii in metres, angles in radians, tensions in N.
 * Outputs: external tangencies, clockwise arc-length samples, material phase and
 * torque-implied force components. No DOM, solver forces, stretch or bearing model.
 */
const TAU=2*Math.PI;
const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],sub=(a,b)=>[a[0]-b[0],a[1]-b[1]];
const mul=(a,s)=>[a[0]*s,a[1]*s];
const finitePoint=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite);
const wrap=(s,length)=>((s%length)+length)%length;
export function openBeltGeometry(hip,knee,hipRadius,kneeRadius){
  if(!finitePoint(hip)||!finitePoint(knee)||!Number.isFinite(hipRadius)||!Number.isFinite(kneeRadius)||hipRadius<=0||kneeRadius<=0)throw new RangeError('Finite centers and positive pulley radii are required.');
  if(Math.abs(hipRadius-2*kneeRadius)>1e-12*hipRadius)throw new RangeError('The guide pulley radii must have an exact 2:1 ratio.');
  const d=Math.hypot(...sub(knee,hip));
  if(d<=hipRadius+kneeRadius)throw new RangeError('Guide pulley circles must be separated without overlap or contact.');
  const e=mul(sub(knee,hip),1/d),perp=[-e[1],e[0]],delta=(hipRadius-kneeRadius)/d,c=Math.sqrt(1-delta*delta);
  const plus=add(mul(e,delta),mul(perp,c)),minus=sub(mul(e,delta),mul(perp,c));
  const hipPlus=add(hip,mul(plus,hipRadius)),kneePlus=add(knee,mul(plus,kneeRadius));
  const hipMinus=add(hip,mul(minus,hipRadius)),kneeMinus=add(knee,mul(minus,kneeRadius));
  const kneeSweep=2*Math.acos(delta),hipSweep=TAU-kneeSweep,span=d*c;
  const segments=[
    {kind:'line',start:hipPlus,end:kneePlus,length:span},
    {kind:'arc',center:knee,radius:kneeRadius,startAngle:Math.atan2(plus[1],plus[0]),sweep:-kneeSweep,length:kneeRadius*kneeSweep},
    {kind:'line',start:kneeMinus,end:hipMinus,length:span},
    {kind:'arc',center:hip,radius:hipRadius,startAngle:Math.atan2(minus[1],minus[0]),sweep:-hipSweep,length:hipRadius*hipSweep},
  ];
  return {hip:[...hip],knee:[...knee],hipRadius,kneeRadius,centerDistance:d,delta,
    normals:{plus,minus},tangencies:{hipPlus,kneePlus,kneeMinus,hipMinus},
    segments,length:segments.reduce((sum,s)=>sum+s.length,0),pulleyOverlap:d<hipRadius+kneeRadius};
}
export function sampleBelt(geometry,distance){
  if(!Number.isFinite(distance))throw new RangeError('Belt arc length must be finite.');
  let remaining=wrap(distance,geometry.length);
  for(let i=0;i<geometry.segments.length;i++){
    const segment=geometry.segments[i];
    if(remaining<=segment.length||i===geometry.segments.length-1){
      const fraction=Math.min(1,remaining/segment.length);
      if(segment.kind==='line'){
        const tangent=mul(sub(segment.end,segment.start),1/segment.length);
        return {point:add(segment.start,mul(tangent,remaining)),tangent,segment:i};
      }
      const angle=segment.startAngle+segment.sweep*fraction;
      return {point:add(segment.center,mul([Math.cos(angle),Math.sin(angle)],segment.radius)),
        tangent:[Math.sin(angle),-Math.cos(angle)],segment:i,angle};
    }
    remaining-=segment.length;
  }
}
export function beltMaterialPhase(hipRadius,carrierAngle,hipAngle,initialCarrierRelative){
  if(![hipRadius,carrierAngle,hipAngle,initialCarrierRelative].every(Number.isFinite)||hipRadius<=0)throw new RangeError('Pulley radius and angles must be finite.');
  return hipRadius*(carrierAngle-hipAngle-initialCarrierRelative);
}
export function beltMaterialDots(geometry,phase,count=24){
  if(!Number.isInteger(count)||count<2||count>1000)throw new RangeError('Material-dot count must be an integer from 2 to 1000.');
  return Array.from({length:count},(_,index)=>({index,distance:wrap(index*geometry.length/count+phase,geometry.length),...sampleBelt(geometry,index*geometry.length/count+phase)}));
}
export function guideSpanLoads(geometry,differenceN,pretensionN=null){
  if(!Number.isFinite(differenceN)||(pretensionN!==null&&(!Number.isFinite(pretensionN)||pretensionN<0)))throw new RangeError('Tension difference must be finite; an assumed baseline must be nonnegative or unspecified.');
  const assumed=pretensionN!==null,components={plus:Math.max(differenceN,0),minus:Math.max(-differenceN,0)};
  const magnitudes={plus:components.plus+(pretensionN??0),minus:components.minus+(pretensionN??0)},forces=[];
  for(const span of ['plus','minus']){
    const start=geometry.tangencies[span==='plus'?'hipPlus':'hipMinus'],end=geometry.tangencies[span==='plus'?'kneePlus':'kneeMinus'];
    const direction=mul(sub(end,start),1/geometry.segments[0].length),magnitude=magnitudes[span];
    forces.push({body:'hip',span,point:start,direction,magnitude,vector:mul(direction,magnitude),role:assumed?'assumed':'difference'});
    forces.push({body:'lower',span,point:end,direction:mul(direction,-1),magnitude,vector:mul(direction,-magnitude),role:assumed?'assumed':'difference'});
  }
  const resultant=body=>forces.filter(f=>f.body===body).reduce((sum,f)=>add(sum,f.vector),[0,0]);
  return {difference_N:differenceN,assumed,pretension_N:pretensionN,span_tensions_N:assumed?magnitudes:null,
    differential_components_N:components,forces,
    bearing_resultants_N:assumed?{hip:resultant('hip'),lower:resultant('lower')}:null,
    torques_Nm:{hip:-geometry.hipRadius*differenceN,knee:geometry.kneeRadius*differenceN}};
}

