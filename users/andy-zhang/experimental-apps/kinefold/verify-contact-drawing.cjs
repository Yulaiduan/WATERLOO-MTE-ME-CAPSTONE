/** Verify actual-contact backdrive indices/material motion without a browser.
 * Run node verify-contact-drawing.cjs. Inputs: mm/deg mechanisms with independent
 * q/drive motion, tilted mount and nonunit drive ratios. Outputs finite-difference
 * no-slip/index assertions; no manufactured belt/contact validation.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({});vm.runInContext(['reference-v4.js','model.js','contact-render.js'].map(f=>fs.readFileSync(path.join(__dirname,f),'utf8')).join('\n'),ctx);
const {Kinefold:M,KinefoldV4:V,KinefoldContactDrawing:D}=ctx;let checks=0,maxError=0;
const near=(a,b,tol=1e-6)=>{assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<tol,`${a} vs ${b}`);checks++;};
function frame(p,q,drive){const r=M.reference(p),s=V.VSL.state(r,q),dc=p.rd/p.rc,fe=p.rf/p.re,dt=q-p.te;
 const theta5=(1-1/dc)*dt+drive/dc,theta6=V.VSL.coefficient(r)*dt+drive/(dc*fe);
 return {theta2:q,theta4:drive,theta5,theta6,A:[0,0,700],B:M.point(s.Bg).map((v,i)=>v+(i===2?700:0)),C:M.point(s.Pg).map((v,i)=>v+(i===2?700:0)),indexAnglesDeg:{a:0,b:s.t3,c:drive,d:theta5,e:theta5,f:theta6}};
}
for(const variant of [{},{alpha:15,phi0:10,rc:30,rd:45,re:20,rf:35}])for(const q of [112,132.5,155])for(const drive of [-80,0,125]){
 const p={...M.defaults,...variant},f=frame(p,q,drive),base=D.transmission(p,f),eps=1e-6,hd=eps*180/Math.PI,driveRate=1.7;
 const plus=D.transmission(p,frame(p,q+hd,drive+hd*driveRate)),minus=D.transmission(p,frame(p,q-hd,drive-hd*driveRate));
 near(base.indices.find(i=>i.id==='a').angle,0);near(base.indices.find(i=>i.id==='c').angle,drive);
 for(const index of base.indices){near(Math.hypot(...index.primary.map((v,i)=>v-index.centre[i])),index.radius);const a=index.primary.map((v,i)=>v-index.centre[i]),b=index.secondary.map((v,i)=>v-index.centre[i]);near(a.reduce((v,x,i)=>v+x*b[i],0),0,1e-7);}
 for(const belt of base.stages){assert.ok(belt.valid);checks++;
  for(const [id,s]of [[belt.id[0],2*belt.loop.straight+belt.loop.right+belt.loop.left/2],[belt.id[1],belt.loop.straight+belt.loop.right/2]]){
   const offset=s-belt.travel,point=belt.material(offset),body=base.indices.find(i=>i.id===id),bp=plus.indices.find(i=>i.id===id),bm=minus.indices.find(i=>i.id===id);
   const velocity=plus.stages.find(b=>b.id===belt.id).material(offset).map((v,i)=>(v-minus.stages.find(b=>b.id===belt.id).material(offset)[i])/(2*eps));
   const cv=bp.centre.map((v,i)=>(v-bm.centre[i])/(2*eps)),rate=(bp.angle-bm.angle)*Math.PI/180/(2*eps),r=point.map((v,i)=>v-body.centre[i]);
   const expected=[cv[0]+rate*r[2],0,cv[2]-rate*r[0]];
   velocity.forEach((v,i)=>{maxError=Math.max(maxError,Math.abs(v-expected[i]));near(v,expected[i],3e-5);});
  }
 }
}
console.log(JSON.stringify({status:'PASS',assertions:checks,maxNoSlipVelocityErrorMmPerRad:maxError}));
