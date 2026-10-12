/** Verify sizing physics against existing Jacobian and independent integration.
 * Run npm test. Inputs mm/deg/N; outputs node assertions. Analytical checks
 * establish static model consistency, not spring, robot or hardware validation.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {defaultSweep,rad,deg,height,limits,convert,metrics,sweep} from '../web/force-plots/link-sweep-model.js';
import {defaultConfig,pose} from '../src/linkage/model.js';
const near=(a,b,tol=1e-8)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
test('Torque matches existing linkage Jacobian and work over angle',()=>{
  const c=defaultSweep(),L=240,a=rad(18),b=rad(64),m=metrics(c,L,a,b),model=defaultConfig();
  model.geometry.upperLength=L/1000;model.geometry.lowerLength=L/1000;
  for(const q of [a,(a+b)/2,b]){
    const torque=2*c.load*L/1000*Math.sin(q);
    near(torque,c.load*pose(model,q).verticalJacobian);
    const eps=1e-6,finite=(height(L,q-eps)-height(L,q+eps))/(2*eps)/1000;
    near(torque,c.load*finite,1e-7);
  }
  const angle=metrics({...c,weighting:'angle'},L,a,b);
  near(angle.mean*(b-a),c.load*m.travel/1000);
  const knee=metrics({...c,shaft:'knee'},L,a,b);
  for(const key of ['mean','peak','rms','min'])near(knee[key],m[key]/2);
  near(knee.cv,m.cv);
});
test('Both weighting modes agree with independent midpoint quadrature',()=>{
  for(const weighting of ['angle','travel']){
    const c={...defaultSweep(),weighting},L=310,a=rad(12),b=rad(72),m=metrics(c,L,a,b);
    let mean=0,second=0;const n=20000;
    for(let i=0;i<n;i++){
      const u=(i+.5)/n;
      const q=weighting==='angle'?a+(b-a)*u:Math.acos((height(L,a)-m.travel*u)/(2*L));
      const torque=c.load*2*L/1000*Math.sin(q);mean+=torque/n;second+=torque**2/n;
    }
    near(m.mean,mean,2e-7);near(m.rms,Math.sqrt(second),2e-7);
    near(m.cv,Math.sqrt(second-mean**2)/mean,1e-8);
    assert.ok(m.min<=m.mean&&m.mean<=m.rms&&m.rms<=m.peak);
  }
});
test('Unit conversions preserve sequential geometry at the reference link',()=>{
  const c=defaultSweep(),L=240;
  for(const key of ['start','rom','end']){
    const degrees=convert(c,L,key,'deg');
    near(convert({...c,nominal:false,[key]:{value:degrees,unit:'deg'}},L,key,'mm'),c[key].value);
  }
  const d={...c,nominal:false,start:{value:15,unit:'deg'},rom:{value:30,unit:'deg'},end:{value:8,unit:'deg'}};
  near(convert(d,L,'rom','mm'),height(L,rad(15))-height(L,rad(45)));
  assert.throws(()=>convert({...c,start:{value:1000,unit:'mm'}},L,'start','deg'));
});
test('Sweep enforces usable radius lift, reserves and chassis clearance',()=>{
  const c=defaultSweep(),s=sweep(c);assert.ok(s.rows.length>1000);
  for(const r of s.rows){
    near(r.travel,c.diameter/2,1e-7);
    assert.ok(r.startMM>=c.start.value-1e-7);
    assert.ok(r.endMM>=c.end.value-1e-7);
    assert.ok(r.groundGap>=c.airGap-1e-7);
    assert.ok(r.startDeg>=0&&r.endDeg<=90);
  }
  const highChassis={...c,chassisDepth:400,airGap:80},t=sweep(highChassis);
  assert.ok(t.rows.length>0);assert.ok(t.rows.every(r=>r.groundGap>=80-1e-7));
  const low=sweep({...c,minLink:100,maxLink:100});assert.equal(low.best,null);
});
test('Exact feasibility endpoints and deg ROM are included',()=>{
  const c={...defaultSweep(),nominal:false,start:{value:20,unit:'mm'},rom:{value:200,unit:'mm'},end:{value:20,unit:'mm'},chassisDepth:0,airGap:0,minLink:120,maxLink:120};
  const s=sweep(c);assert.equal(s.rows.length,1);near(s.best.startMM,20);near(s.best.endMM,20);
  const d={...c,start:{value:10,unit:'deg'},rom:{value:35,unit:'deg'},end:{value:5,unit:'deg'},minLink:200,maxLink:201,linkStep:3};
  const t=sweep(d);assert.ok(t.rows.some(r=>r.link===201));
  assert.ok(t.rows.some(r=>Math.abs(r.endDeg-85)<1e-8));
  t.rows.forEach(r=>near(r.endDeg-r.startDeg,35));
  assert.ok(limits(d,200));
});
test('Ranking finds requested sampled minima and exposes tradeoff',()=>{
  const c=defaultSweep();
  for(const objective of ['peak','mean','flat']){
    const s=sweep({...c,objective}),key=objective==='flat'?'cv':objective;
    near(s.best[key],Math.min(...s.rows.map(r=>r[key])));
  }
  const peak=sweep(c).best,flat=sweep({...c,objective:'flat'}).best;
  assert.ok(flat.cv<peak.cv);assert.ok(flat.peak>peak.peak);
});
test('Impossible / malformed sweeps fail clearly without nonfinite results',()=>{
  assert.equal(sweep({...defaultSweep(),diameter:5000}).best,null);
  for(const patch of [{load:NaN},{minLink:0},{airGap:-1},{angleStep:.000001},{shaft:'unknown'},
    {start:{value:90,unit:'deg'}},{nominal:false,rom:{value:0,unit:'mm'}}])assert.throws(()=>sweep({...defaultSweep(),...patch}));
  near(deg(rad(45)),45);
});
