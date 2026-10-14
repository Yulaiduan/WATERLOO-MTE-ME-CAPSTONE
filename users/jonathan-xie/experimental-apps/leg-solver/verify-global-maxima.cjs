/** Verify actual embedded global-headline search against FBD statics and closed forms.
 * Run: node verify-global-maxima.cjs. Inputs: deterministic mm/deg/kg/N cases.
 * Outputs assertions and default timing; numerical consistency, no hardware claim.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'v2-quasi-static.html'),'utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);scripts.forEach(s=>new vm.Script(s));
const {VSL:k,VSLStatic:s,VSLPeaks:g}=vm.runInNewContext(scripts.slice(0,3).join('\n')+';({VSL,VSLStatic,VSLPeaks});');
let checks=0;const near=(a,b,t=1e-7)=>{assert.ok(Math.abs(a-b)<=t,`${a} != ${b}`);checks++;};
const ranges={alpha:{min:0,max:30},beta:{min:0,max:90}},p={...s.defaults,Fn:100};
const start=performance.now(),demo=g.calculate(p,ranges),elapsed=performance.now()-start;
near(demo.tau2.value,-60*Math.sin(75*Math.PI/180),.001);near(demo.tau4.value,0);near(demo.ab.value,1200,.001);near(demo.dz.value,435.5932247458122,.001);
let seed=1234567;const random=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
for(let i=0;i<24;i++){
 const a={...p,L2:250+random()*150,L3:240+random()*140,ra:20+random()*80,rb:20,rc:25+random()*30,rd:25,re:20+random()*20,rf:20,rw:80+random()*50,phi0:random()*30,m2:random(),m3:random(),m5:random(),m6:random(),g:i%5?9.81:0,Tab0:random()*50,Tef0:random()*50,Fn:random()*300-100,Ft:random()*200-100,Fy:random()*300-150,Fz:random()*300-100,loadMode:i%2?'yz':'nt',te:90+random()*25,tc:140+random()*40};
 const r={alpha:{min:random()*10,max:20+random()*25},beta:{min:random()*15,max:60+random()*30}},peaks=g.calculate(a,r);
 assert.ok(peaks.valid);checks++;
 // Independent actual FBD solver verifies the analytic objective at arbitrary angles.
 for(let j=0;j<120;j++){
  const theta=a.te+(a.tc-a.te)*random(),alpha=r.alpha.min+(r.alpha.max-r.alpha.min)*random(),beta=r.beta.min+(r.beta.max-r.beta.min)*random(),b=s.solve({...a,alpha,beta},theta,false),c=g.coefficients(a,theta);
  for(const key of ['tau2','tau4','ab','dz']){
   const actual=key==='ab'?b.ab.delta:b[key],formula=g.value(c[key],alpha*k.rad,beta*k.rad);near(formula,actual,2e-7);
   const magnitude=key==='ab'?Math.max(b.ab.U,b.ab.L):Math.abs(actual);assert.ok(magnitude<=Math.abs(peaks[key].value)+peaks[key].error+2e-7,`${key} domain sample exceeded certified upper value`);checks++;
  }
 }
 for(const key of ['tau2','tau4','ab','dz']){const b=peaks[key],actual=s.solve({...a,alpha:b.alpha,beta:b.beta},b.theta2,false),value=key==='ab'?Math.max(actual.ab.U,actual.ab.L):key==='dz'?Math.abs(actual.dz):actual[key];near(value,b.value,2e-7);assert.ok(b.converged&&b.error<=.001);checks++;assert.ok(b.theta2>=a.te&&b.theta2<=a.tc&&b.alpha>=r.alpha.min-1e-9&&b.alpha<=r.alpha.max+1e-9&&b.beta>=r.beta.min-1e-9&&b.beta<=r.beta.max+1e-9);checks++;}
}
// Collapsed boxes, zero forces, interior beta optimum, preload and negative travel.
const fixed={alpha:{min:17,max:17},beta:{min:34,max:34}},z=g.calculate({...p,te:123,tc:123},fixed);for(const key of ['tau2','tau4','ab','dz'])near(z[key].error,0);
const negative=g.calculate({...p,phi0:30,te:90,tc:110},{alpha:{min:0,max:0},beta:{min:0,max:0}});assert.ok(negative.dz.signedValue<0&&negative.dz.value>19);checks++;
const yz=g.calculate({...p,loadMode:'yz',Fy:100,Fz:-100},ranges);near(Math.abs(yz.tau4.value),Math.sqrt(200),.001);near(yz.tau4.beta,45,1e-7);
const preload=g.calculate({...p,Tab0:37},ranges);near(preload.ab.value-demo.ab.value,37);near(preload.tau2.value,demo.tau2.value);
const limited=g.calculate(p,ranges,{maxIterations:0});assert.ok(!limited.tau2.converged&&limited.tau2.error>0);checks++;
assert.equal(g.calculate({...p,L2:50},ranges).valid,false);checks++;
// User-facing search holds alpha at its current value, ignoring its slider window.
for(const alpha of [0,12,30,45])for(const loadMode of ['nt','yz']){
 const a={...p,alpha,loadMode,Fn:100,Ft:20,Fy:-40,Fz:120,m2:.7,m3:.9,m6:.4},z=g.fixedAlpha(a,ranges),other=g.fixedAlpha(a,{...ranges,alpha:{min:0,max:0}});
 for(const key of ['tau2','tau4','ab','dz']){near(z[key].alpha,alpha);near(z[key].value,other[key].value);assert.ok(z[key].converged);checks++;}
 for(let j=0;j<200;j++){const theta=a.te+(a.tc-a.te)*random(),beta=90*random(),b=s.solve({...a,beta},theta,false);for(const key of ['tau2','tau4','ab','dz']){const value=key==='ab'?Math.max(b.ab.U,b.ab.L):Math.abs(b[key]);assert.ok(value<=Math.abs(z[key].value)+z[key].error+1e-7);checks++;}}
}
console.log(`PASS: ${checks} global-maximum assertions; analytic objective/FBD parity, full-domain bounds, attained poses and degeneracies. Default ${demo.evaluations} evaluations in ${elapsed.toFixed(1)} ms.`);
