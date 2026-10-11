/** Pure guide-belt geometry/phase/load checks.
 * Run: node --test tests/guide-belt.test.js. SI inputs; assertion-only outputs.
 * Verifies ideal visualization identities, not physical belt compliance or hardware.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {openBeltGeometry,sampleBelt,beltMaterialPhase,beltMaterialDots,guideSpanLoads} from '../web/guide-belt.js';
const near=(a,b,tol=1e-11)=>assert.ok(Math.abs(a-b)<tol,String(a)+' ≠ '+b);
const pointNear=(a,b)=>a.forEach((value,index)=>near(value,b[index]));
const cross=(a,b)=>a[0]*b[1]-a[1]*b[0],sub=(a,b)=>[a[0]-b[0],a[1]-b[1]];
const rotate=(p,angle,offset=[0,0])=>[offset[0]+p[0]*Math.cos(angle)-p[1]*Math.sin(angle),offset[1]+p[0]*Math.sin(angle)+p[1]*Math.cos(angle)];
const base=()=>openBeltGeometry([0,0],[.3,0],.028,.014);
test('External tangent spans are perpendicular to both actual pulley radii',()=>{
 const g=base();
 for(const side of ['Plus','Minus']){
  const a=g.tangencies['hip'+side],b=g.tangencies['knee'+side],span=sub(b,a);
  for(const [contact,center,radius] of [[a,g.hip,g.hipRadius],[b,g.knee,g.kneeRadius]]){
   const radial=sub(contact,center);near(Math.hypot(...radial),radius);
   near(radial[0]*span[0]+radial[1]*span[1],0);
  }
 }
 near(g.hipRadius/g.kneeRadius,2);
});
test('Clockwise line/arc loop closes with continuous tangent direction',()=>{
 const g=base();let s=0;
 for(const segment of g.segments){
  const before=sampleBelt(g,s+segment.length-1e-10),after=sampleBelt(g,s+segment.length+1e-10);
  assert.ok(Math.hypot(...sub(before.point,after.point))<3e-10);
  assert.ok(Math.hypot(...sub(before.tangent,after.tangent))<2e-8);
  s+=segment.length;
 }
 pointNear(sampleBelt(g,0).point,sampleBelt(g,g.length).point);
 pointNear(sampleBelt(g,-.01).point,sampleBelt(g,g.length-.01).point);
});
test('Belt perimeter matches exact unequal-pulley external-wrap expression',()=>{
 const g=base(),alpha=Math.asin((.028-.014)/.3);
 near(g.length,2*Math.sqrt(.3**2-(.028-.014)**2)+Math.PI*(.028+.014)+2*(.028-.014)*alpha);
 assert.ok(Math.abs(g.segments[3].sweep)>Math.PI);assert.ok(Math.abs(g.segments[1].sweep)<Math.PI);
});
test('Tangent geometry rotates and translates without changing material length',()=>{
 const g=base(),angle=.73,shift=[.17,-.28],r=openBeltGeometry(rotate(g.hip,angle,shift),rotate(g.knee,angle,shift),.028,.014);
 near(r.length,g.length);for(const key of Object.keys(g.tangencies))pointNear(r.tangencies[key],rotate(g.tangencies[key],angle,shift));
});
test('Material phase fixes the hip mark and rotates the knee opposite its carrier',()=>{
 const g=base(),change=.08,r=openBeltGeometry([0,0],rotate([.3,0],change),.028,.014);
 const phase=beltMaterialPhase(.028,change,0,0);
 const hipS=g.segments.slice(0,3).reduce((sum,s)=>sum+s.length,0)+g.segments[3].length/2,kneeS=g.segments[0].length+g.segments[1].length/2;
 const hip0=sampleBelt(g,hipS),hip1=sampleBelt(r,hipS+phase),knee0=sampleBelt(g,kneeS),knee1=sampleBelt(r,kneeS+phase);
 near(hip1.angle,hip0.angle);near(knee1.angle-knee0.angle,-change);
 near((knee1.angle-knee0.angle)-change,-2*change);
});
test('Moving chassis phase gives exact world-angle rotation for both attached pulleys',()=>{
 const g=base(),carrier=.06,hip=.02,r=openBeltGeometry([0,0],rotate([.3,0],carrier),.028,.014),phase=beltMaterialPhase(.028,carrier,hip,0);
 const hipS=g.segments.slice(0,3).reduce((sum,s)=>sum+s.length,0)+g.segments[3].length/2,kneeS=g.segments[0].length+g.segments[1].length/2;
 near(sampleBelt(r,hipS+phase).angle-sampleBelt(g,hipS).angle,hip);
 near(sampleBelt(r,kneeS+phase).angle-sampleBelt(g,kneeS).angle,2*hip-carrier);
});
test('Material dots are reproducible pose samples with closed-loop wrapping',()=>{
 const g=base(),phase=beltMaterialPhase(.028,-.9,0,-.9);
 near(phase,0);beltMaterialDots(g,phase).forEach((a,i)=>pointNear(a.point,beltMaterialDots(g,phase+g.length)[i].point));
 assert.equal(beltMaterialDots(g,phase,24).length,24);
 for(const dot of beltMaterialDots(g,phase))pointNear(dot.point,sampleBelt(g,dot.distance).point);
});
test('Unspecified pretension provides only a difference component, never absolute bearing loads',()=>{
 const g=base(),loads=guideSpanLoads(g,80);
 assert.equal(loads.span_tensions_N,null);assert.equal(loads.bearing_resultants_N,null);assert.equal(loads.assumed,false);
 assert.ok(loads.forces.every(f=>f.role==='difference'));near(loads.torques_Nm.knee,80*.014);near(loads.torques_Nm.hip,-2*loads.torques_Nm.knee);
});
test('Assumed baseline forces preserve opposite span directions and signed 2:1 torque',()=>{
 const g=openBeltGeometry([.1,.2],[.3,.4],.028,.014);
 for(const difference of [-90,90]){
  const loads=guideSpanLoads(g,difference,120);
  near(loads.span_tensions_N.plus-loads.span_tensions_N.minus,difference);
  near(Math.min(...Object.values(loads.span_tensions_N)),120);
  for(const span of ['plus','minus']){const pair=loads.forces.filter(f=>f.span===span);pointNear(pair[0].vector,pair[1].vector.map(x=>-x));}
  const hipTorque=loads.forces.filter(f=>f.body==='hip').reduce((sum,f)=>sum+cross(sub(f.point,g.hip),f.vector),0);
  const kneeTorque=loads.forces.filter(f=>f.body==='lower').reduce((sum,f)=>sum+cross(sub(f.point,g.knee),f.vector),0);
  near(kneeTorque,g.kneeRadius*difference);near(hipTorque,-2*kneeTorque);
 }
});
test('Invalid sizes, baseline forces and phase inputs fail explicitly',()=>{
 assert.throws(()=>openBeltGeometry([0,0],[.01,0],.028,.014),RangeError);
 assert.throws(()=>openBeltGeometry([0,0],[.3,0],-.028,.014),RangeError);
 assert.throws(()=>openBeltGeometry([0,0],[.04,0],.028,.014),RangeError);
 assert.throws(()=>openBeltGeometry([0,0],[.3,0],.028,.016),RangeError);
 assert.throws(()=>guideSpanLoads(base(),Infinity),RangeError);
 assert.throws(()=>guideSpanLoads(base(),2,-1),RangeError);
 assert.throws(()=>beltMaterialPhase(.028,NaN,0,0),RangeError);
 assert.throws(()=>beltMaterialDots(base(),0,0),RangeError);
});

