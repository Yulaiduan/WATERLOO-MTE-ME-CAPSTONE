/** Verify the analytical General VSL model embedded in the standalone HTML.
 * Run: node verify-kinematics.cjs (from any directory). Inputs: embedded demo mm/deg.
 * Outputs: assertion counts on stdout; requires only Node standard libraries.
 * Limitations: ideal mathematical identities and belt material velocities, not hardware tests.
 */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, 'v1-kinematics.html'), 'utf8');
const source = html.match(/<script id="solver-model">([\s\S]*?)<\/script>/)[1];
const m = vm.runInNewContext(source + '\nVSL;');
for (const [,script] of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)) new vm.Script(script);
let checks=0;
const near=(a,b,tol=1e-8)=>{assert.ok(Math.abs(a-b)<=tol,`${a} != ${b}`);checks++;};
const p={...m.defaults};
// Closed-form scissor geometry is independent of the belt-constraint implementation.
for(let t=90;t<=180;t+=.25){const s=m.state(p,t);near(s.P[0],0);near(s.P[1],-600*Math.sin(t*Math.PI/180));near(s.t3,180-t);near(s.t6,0);}
// Three carrier-frame nonslip constraints for unequal links, ratios and phase offsets.
for(const qab of [.5,1,1.7,2,3.4])for(const qcd of [.6,1,1.5,2.3])for(const qef of [.4,1,2.7]){
  const a={...p,ra:25*qab,rc:20*qcd,rd:20,re:15*qef,rf:15,L2:320,L3:275,alpha:17,phi0:13,te:104,tc:169},e=m.state(a,a.te);
  for(const t of [90,104,128,169,180]){const s=m.state(a,t),dt=t-a.te,dt3=s.t3-e.t3;
    near(a.ra*(0-dt),a.rb*(dt3-dt));
    near(a.rc*(s.t4-dt),a.rd*(s.t5-dt));
    near(a.re*(s.t5-dt3),a.rf*(s.t6-dt3));
    near(Math.hypot(...s.B),a.L2);near(Math.hypot(s.P[0]-s.B[0],s.P[1]-s.B[1]),a.L3);
    near(Math.hypot(s.du,s.dv),Math.hypot(s.dy,s.dz));
  }
  for(const k of ['du','dv','dy','dz','t5','t6'])near(e[k],0);
  const s=m.state(a,140),eps=1e-4,up=m.state(a,140+eps),down=m.state(a,140-eps);
  near((up.t6-down.t6)/(2*eps),m.coefficient(a));
  // Independent differentiation of the link position, not reusing model derivatives.
  const d3=1-qab,R=Math.PI/180;
  near((up.du-down.du)/(2*eps),R*(a.L2*Math.sin(140*R)+a.L3*Math.sin(s.t3*R)*d3),2e-7);
  near((up.dv-down.dv)/(2*eps),-R*(a.L2*Math.cos(140*R)+a.L3*Math.cos(s.t3*R)*d3),2e-7);
}
near(m.coefficient({...p,rc:45,rd:30,re:40,rf:20}),0);
near(m.state({...p,rc:50,rd:25},165).t6,-65);
near(m.coefficient({...p,ra:25,rb:25,rc:30,rd:30,re:39,rf:13}),0);
near(m.coefficient({...p,rc:50,rd:25,re:90,rf:15}),-1);
// Belt total length compared with exact open-belt length; junction continuity and material velocities.
for(const [D,R,r] of [[300,50,25],[300,25,50],[300,35,35],[100,31,12]]){
  const b=m.belt(D,R,r),beta=Math.asin((R-r)/D),expected=2*Math.sqrt(D*D-(R-r)**2)+Math.PI*(R+r)+2*(R-r)*beta;
  near(b.total,expected);
  for(const j of [0,b.straight,b.straight+b.right,2*b.straight+b.right,b.total]){const a=b.at(j-1e-7),c=b.at(j+1e-7);near(Math.hypot(a[0]-c[0],a[1]-c[1]),0,3e-7);}
  // Fixed material on each wrap must have the rigid pulley surface velocity in world frame.
  const wc=.8,wdriver=-.3,wout=wc+(R/r)*(wdriver-wc),speed=-R*(wdriver-wc),eps=1e-7;
  for(const [distance,center,omega] of [[b.straight+b.right*.5,[D,0],wout],[2*b.straight+b.right+b.left*.5,[0,0],wdriver]]){
    function position(dt){const a=b.at(distance+speed*dt),c=Math.cos(wc*dt),s=Math.sin(wc*dt);return [c*a[0]-s*a[1],s*a[0]+c*a[1]];}
    const a=position(0),up=position(eps),dn=position(-eps),vc=[-wc*center[1],wc*center[0]];
    near((up[0]-dn[0])/(2*eps),vc[0]-omega*(a[1]-center[1]),2e-5);
    near((up[1]-dn[1])/(2*eps),vc[1]+omega*(a[0]-center[0]),2e-5);
  }
}
assert.equal(m.belt(75,50,25),null);checks++;
assert.ok(m.validate({...p,rb:0}).length);checks++;
assert.ok(m.validate({...p,te:170,tc:100}).length);checks++;
assert.ok(m.validate({...p,alpha:NaN}).length);checks++;
assert.equal(m.validate({...p,te:120,tc:120}).length,0);checks++;
assert.ok(m.warnings({...p,L2:50}).length);checks++;
const env=m.envelope(p);near(env.values.du.min,0);near(env.values.du.max,0);near(env.values.dv.max,600*(Math.sin(p.te*Math.PI/180)-Math.sin(p.tc*Math.PI/180)));
const nonmono=m.envelope({...p,phi0:30,te:90,tc:180});assert.ok(nonmono.values.dv.min < -1);checks++;
for(const [u,v,angle] of [[1,1,45],[-1,1,-45],[1,-1,135],[-1,-1,-135],[1,0,90],[0,-1,180]])near(m.inclination(u,v),angle);
assert.equal(m.inclination(0,0),null);checks++;
const ref=m.state(p,p.te);assert.equal(ref.gammaUV,null);assert.equal(ref.gammaYZ,null);checks+=2;
for(const alpha of [0,15,30]){const z=m.state({...p,alpha},p.tc);near(z.gammaUV,0);near(z.gammaYZ,alpha);}
console.log(`PASS: ${checks} mathematical assertions; both embedded scripts parse.`);
