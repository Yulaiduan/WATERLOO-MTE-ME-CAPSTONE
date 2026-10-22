/** Verify actual embedded v2 statics using FBDs, whole-system balance and virtual work.
 * Run: node verify-quasi-static.cjs. Inputs: deterministic mm/deg/kg/N fixtures.
 * Outputs: assertion count. Uses Node standard libraries only; no dynamics/hardware claim.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'v2-quasi-static.html'),'utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);scripts.forEach(x=>new vm.Script(x));
const {VSL:k,VSLStatic:m}=vm.runInNewContext(scripts[0]+scripts[1]+';({VSL,VSLStatic});');
let checks=0,maxF=0,maxM=0,maxVW=0;
const near=(a,b,tol=2e-8)=>{assert.ok(Math.abs(a-b)<=tol,`${a} != ${b}; tol ${tol}`);checks++;};
const vnear=(a,b,tol=2e-8)=>a.forEach((x,i)=>near(x,b[i],tol));
const plus=(...v)=>v.reduce((a,b)=>[a[0]+b[0],a[1]+b[1]],[0,0]),times=(a,c)=>a.map(x=>x*c),minus=(a,b)=>plus(a,times(b,-1));
const cross=(a,b)=>a[0]*b[1]-a[1]*b[0],dot=(a,b)=>a[0]*b[0]+a[1]*b[1];
const R=Math.PI/180,p={...m.defaults,Fn:100};
let s=m.solve(p,120);near(s.tau2,-30);near(s.tau4,0);near(s.ab.U,600);near(s.ab.L,0);near(s.Mw,0);
s=m.solve({...p,Fn:0,Ft:100,rc:50,rd:25},120);near(s.tau2,10);near(s.tau4,-20);assert.equal(s.cd.active,'L');assert.equal(s.ef.active,'U');checks+=2;
for(const t of [90,100,140,180]){const a=m.solve({...p,Fn:0,Ft:0,m1:40},t);near(a.tau2,0);near(a.tau4,0);vnear(k.global(p,a.Fground),[0,40*9.81]);}
for(let i=0;i<240;i++){
 const a={...p,L2:300+(i%7)*13,L3:260+(i%9)*9,ra:20*(.5+(i%8)*.4),rb:20,rc:15*(.6+(i%6)*.5),rd:15,re:12*(.7+(i%5)*.6),rf:12,rw:80+i%11,alpha:(i*7)%46,beta:(i*11)%91,phi0:(i*3)%31,m1:i%13,m2:(i%5)*.2,m3:(i%7)*.15,m5:(i%3)*.1,m6:(i%6)*.3,Fn:(i*19)%401,Ft:((i*23)%301)-150,Tab0:i%31,Tcd0:i%29,Tef0:i%17,te:97,tc:170};
 const t=90+(i*17)%91,b=m.solve(a,t);assert.ok(b.valid);checks++;
 maxF=Math.max(maxF,b.maxForce);maxM=Math.max(maxM,b.maxMoment);maxVW=Math.max(maxVW,b.virtualWorkError);
 // Re-sum every applied force/couple at its actual contact point.
 for(const body of Object.values(b.bodies)){vnear(plus(...body.forces.map(f=>f.vec)),[0,0]);const moment=body.forces.reduce((sum,f)=>sum+cross(minus(f.pos,body.origin),f.vec)/1000,0)+body.couples.reduce((sum,c)=>sum+c.value,0);near(moment,0);}
 for(const loop of [b.ab,b.cd,b.ef]){near(loop.U-loop.L,loop.delta);near(Math.min(loop.U,loop.L),a[loop.name==='ab'?'Tab0':loop.name==='cd'?'Tcd0':'Tef0']);vnear(plus(loop.Fleft,loop.Fright),[0,0]);near(loop.spans.reduce((sum,sp)=>sum+cross(minus(sp.left.pos,loop.O),sp.left.vec)/1000,0),loop.Mleft);near(loop.spans.reduce((sum,sp)=>sum+cross(minus(sp.right.pos,loop.C),sp.right.vec)/1000,0),loop.Mright);}
 vnear(plus(b.F32,b.bodies[3].forces[0].vec),[0,0]);vnear(plus(b.F25,b.bodies[2].forces[2].vec),[0,0]);vnear(plus(b.Fw,b.F36),[0,0]);
 near(Math.hypot(...minus(b.P,b.C)),a.rw);const pg=k.global(a,minus(b.P,b.C));vnear(pg,[-a.rw*Math.sin(a.beta*R),-a.rw*Math.cos(a.beta*R)]);
 near(cross(minus(b.P,b.C),b.Fcontact)/1000,a.Ft*a.rw/1000);near(dot(b.Fcontact,b.Fcontact),a.Fn*a.Fn+a.Ft*a.Ft,2e-7);
 // Entire assembly, including grounded lump m1, closes in force and moment.
 vnear(plus(b.Fground,b.Fcontact,b.W1,b.W2,b.W3,b.W5,b.W6),[0,0]);
 near(b.Mground+cross(b.P,b.Fcontact)/1000+cross(b.C2,b.W2)/1000+cross(b.C3,b.W3)/1000+cross(b.B,b.W5)/1000+cross(b.C,b.W6)/1000,0);
 // Independent numerical virtual displacement; no solver Jacobian is used.
 const h=1e-5,up=k.raw(a,t+h/R),dn=k.raw(a,t-h/R),dB=times(minus(up.B,dn.B),1/(2*h*1000)),dC=times(minus(up.P,dn.P),1/(2*h*1000)),dC2=times(dB,.5),dC3=times(plus(dB,dC),.5),Q=dot(b.Fcontact,dC)+dot(b.W2,dC2)+dot(b.W3,dC3)+dot(b.W5,dB)+dot(b.W6,dC)+b.Mw*k.coefficient(a);
 near(b.tau2,-Q,2e-6);near(b.tau4,-a.rw*a.Ft/1000*(a.rc/a.rd)*(a.re/a.rf));
 // Common preload changes pin forces, but does not alter ideal actuator torque.
 const load=m.solve({...a,Tab0:a.Tab0+100,Tcd0:a.Tcd0+80,Tef0:a.Tef0+60},t);near(load.tau2,b.tau2);near(load.tau4,b.tau4);
 const noMain=m.solve({...a,m1:a.m1+100},t);near(noMain.tau2,b.tau2);near(noMain.tau4,b.tau4);
 const fast=m.solve(a,t,false);near(fast.tau2,b.tau2);near(fast.tau4,b.tau4);
}
for(const [x,y,want] of [[1,1,45],[-1,1,-45],[1,-1,135],[-1,-1,-135],[0,-1,180],[1,0,90]])near(k.inclination(x,y),want);
assert.equal(k.inclination(0,0),null);checks++;
for(const t of [p.te,p.tc]){const a=k.state(p,t),v2=k.state(m.defaults,t);vnear(a.P,v2.P);near(a.t3,v2.t3);}
assert.equal(m.solve({...p,L2:50},120).valid,false);checks++;
assert.ok(m.validate({...p,m2:-1}).length);assert.ok(m.validate({...p,Fn:NaN}).length);assert.ok(m.validate({...p,beta:91}).length);checks+=3;
near(m.solve({...p,m2:2,m3:3,m5:4,m6:5,r5I:40},120).inertia.I5,4*.04**2);
// Driving-convention conversion is orthogonal and preserves the complete statics.
for(let i=0;i<91;i++){
 const nt=m.resolveLoads({...p,beta:i,Fn:100-i*2,Ft:i-45,alpha:i%46,m2:.3,m3:.2,m5:.1,m6:.4});
 const yz=m.resolveLoads({...nt,loadMode:'yz'});near(yz.Fn,nt.Fn);near(yz.Ft,nt.Ft);near(yz.Fy,nt.Fy);near(yz.Fz,nt.Fz);near(nt.Fy**2+nt.Fz**2,nt.Fn**2+nt.Ft**2,1e-7);
 const a=m.solve(nt,111.3),b=m.solve(yz,111.3);for(const k of ['tau2','tau4'])near(a[k],b[k]);for(const k of ['F12','F14','F25','F32','Fw'])vnear(a[k],b[k]);for(const k of ['ab','cd','ef']){near(a[k].U,b[k].U);near(a[k].L,b[k].L);}near(b.maxForce,0);near(b.maxMoment,0);near(b.virtualWorkError,0);
 const sweep=m.solve({...yz,beta:90-i},120,false);near(sweep.Fy,nt.Fy);near(sweep.Fz,nt.Fz);
}
const nonmonotone={...p,L2:300,L3:300,ra:40,rb:20,phi0:30,te:90,tc:180,alpha:0};
const domain=m.dzDomain(nonmonotone,90,180);assert.ok(domain.min<-15&&domain.max>400);checks++;
const roots=m.posesAtDz(nonmonotone,0,90,180);assert.equal(roots.length,2);checks++;near(roots[0],90);near(roots[1],120);
for(const tt of [90,99.2,120,180]){const z=k.state(nonmonotone,tt).dz;assert.ok(m.posesAtDz(nonmonotone,z,90,180).some(a=>Math.abs(a-tt)<1e-5));checks++;}
const exact=m.thetaSamples({...p,te:103.14,tc:167.89},90,180,20);assert.ok(exact.includes(103.14)&&exact.includes(167.89));checks++;
const flat=m.dzDomain({...p,te:120,tc:120},120,120);near(flat.min,-.5);near(flat.max,.5);
assert.equal(m.validate({...p,Fn:-1}).length,0);assert.ok(m.validate({...p,loadMode:'oops'}).length);checks+=2;
console.log(`PASS: ${checks} quasi-static assertions; max F residual ${maxF.toExponential(3)} N, max M residual ${maxM.toExponential(3)} Nm, max virtual-work error ${maxVW.toExponential(3)} Nm. All embedded scripts parse.`);
