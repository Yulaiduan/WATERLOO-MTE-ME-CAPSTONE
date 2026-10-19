/** Verify analytical sizing against independent virtual work / point kinetic energy.
 * Run: node --test tests/sizing.test.js. Inputs SI cases and sheet snapshot.
 * Outputs assertion results; no canonical robot, thermal or hardware verification.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {G,DEFAULTS,support,spring,pose,sweep,capacity,maxRpm,utilization,designMap,catalogCSV,parseCSV,validate} from '../web/sizing/model.js';
const catalog=JSON.parse(readFileSync(new URL('../web/sizing/catalog.json',import.meta.url)));
const close=(a,b,tol=1e-7)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
test('gravity equals potential derivative for unequal rods and changing corner load',()=>{
 for(const a of [.18,.24,.35])for(const b of [.17,.24,.40])for(const mass of [0,20,60])for(const q of [.2,.6,1.3]){
  const p={...DEFAULTS,upper:a,lower:b,chassis:mass};
  const V=t=>G*((mass+p.payload)/p.supports*(a+b)*Math.sin(t)+p.upperMass*(a/2+b)*Math.sin(t)+p.lowerMass*b/2*Math.sin(t));
  const h=1e-5;close(pose(p,q,0,0).gravity,(V(q+h)-V(q-h))/(2*h),1e-6);
 }
});
test('constant lift, zero assistance and exact balance identities',()=>{
 const p={...DEFAULTS,upper:.20,lower:.25};p.springForce=support(p);
 for(const q of [.1,.5,1,1.4]){const r=pose(p,q,0,0),sp=spring(p);close(r.torque,0);close(sp.k*sp.H*sp.R/(p.upper+p.lower),p.springForce);close(r.tension,sp.k*r.span);}
 close(pose({...p,springForce:0},.6,0,0).torque,pose({...p,springForce:0},.6,0,0).gravity);
 assert.ok(pose({...p,chassis:0},.6,0,0).torque<0,'fixed spring over-assists lighter chassis');
});
test('dynamic inertia matches independent finite-difference COM velocities',()=>{
 const p={...DEFAULTS,upper:.19,lower:.25};
 for(const q of [.3,.8,1.2]){
  const a=p.upper,b=p.lower,h=1e-6;
  const coords=t=>[[0,(a+b)*Math.sin(t)],[a/2*Math.cos(t),(a/2+b)*Math.sin(t)],[(a-b/2)*Math.cos(t),b/2*Math.sin(t)],[(a-b)*Math.cos(t),0]];
  const plus=coords(q+h),minus=coords(q-h),masses=[(p.chassis+p.payload)/p.supports,p.upperMass,p.lowerMass,p.wheelMass];
  const kinetic=masses.reduce((sum,m,i)=>sum+m*((plus[i][0]-minus[i][0])**2+(plus[i][1]-minus[i][1])**2)/(4*h*h),0)+(p.upperMass*a*a+p.lowerMass*b*b)/12;
  close(pose(p,q).inertia,kinetic,1e-8);
 }
});
test('hip/knee power invariance and prescribed vertical kinematics',()=>{
 for(const q of [.3,.8,1.3]){const hip=pose(DEFAULTS,q,.2,1),knee=pose({...DEFAULTS,actuator:2},q,.2,1);
  close(hip.torque,2*knee.torque);close(knee.rpm,2*hip.rpm);close(knee.power,hip.power);
  close(hip.J*hip.qdot,.2);close(hip.J*hip.qddot-(DEFAULTS.upper+DEFAULTS.lower)*Math.sin(q)*hip.qdot**2,1);
 }
});
test('sheet gear limits preserve nonmonotonic torque and speed mapping',()=>{
 assert.equal(catalog.motors.length,9);assert.equal(catalog.gearboxes.length,6);
 assert.deepEqual(catalog.gearboxes.slice(0,4).map(g=>g.nominalTorque),[28,10,30,25]);
 const m=catalog.motors[4],p={...DEFAULTS,current:100};
 for(const g of catalog.gearboxes){close(maxRpm(m,g,p),3000/g.ratio);assert.ok(capacity(m,g,p,0)<=g.nominalTorque);assert.equal(capacity(m,g,p,maxRpm(m,g,p)+.1),0);}
});
test('power/current caps, map center and speed failure are explicit',()=>{
 const m={kv:100,kt:.1,peakTorque:10,maxCurrent:100,maxPower:50},g={ratio:5,efficiency:.9,ratedRpm:3000,maxRpm:6000,nominalTorque:30,momentaryTorque:60};
 close(capacity(m,g,DEFAULTS,0),9);
 close(capacity(m,g,DEFAULTS,500),.9*50/(500*2*Math.PI/60));
 const p={...DEFAULTS,mapMinMass:10,mapMaxMass:30,mapMinLink:.12,mapMaxLink:.36};
 const map=designMap(p,m,g,3);close(map.z[1][1],utilization(sweep(p,41),m,g,p).ratio);
 assert.ok(!utilization(sweep({...p,speed:20}),m,g,p).fits);
});
test('CSV refresh handles quoted cells and rejects absent/invalid data',()=>{
 assert.deepEqual(parseCSV('a,b\r\n"x,y","say ""hi"""'),[['a','b'],['x,y','say "hi"']]);
 assert.throws(()=>catalogCSV('Model,Ratio\nX,20','gears'),/Missing/);
 const header='Model,Ratio,Nominal output torque (N m),Momentary output torque (N m),Efficiency,Rated input (rpm),Max input (rpm)';
 const row=catalogCSV(header+'\nX,20,30,60,94%,3000,6000','gears')[0];close(row.efficiency,.94);
 assert.throws(()=>catalogCSV(header+'\nX,20,,60,94%,3000,6000','gears'),/missing/);
 assert.throws(()=>catalogCSV(header+'\nX,20,30,60,94,3000,6000','gears'),/Efficiency/);
});
test('invalid inputs and near-vertical windows are rejected',()=>{
 for(const p of [{supports:0},{supports:1.5},{maxAngle:90},{minAngle:80,maxAngle:70},{current:NaN},{springForce:-1},{reserve:1.1}])assert.throws(()=>validate({...DEFAULTS,...p}));
 assert.throws(()=>pose(DEFAULTS,Math.PI/2));
});
