/** Verify rendered-geometry inputs and belt material motion. Run: node verify-drawing.cjs.
 * Inputs: mm/degree V4 mechanisms. Outputs: numerical geometric/no-slip assertions.
 * Independent finite differences check material velocities on each pulley wrap.
 * This validates the ideal preview, not manufactured clearance or belt elasticity.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const read=f=>fs.readFileSync(path.join(__dirname,f),'utf8'),ctx=vm.createContext({});
vm.runInContext(['reference-v4.js','model.js','preview-geometry.js'].map(read).join('\n'),ctx);
const {Kinefold:M,KinefoldV4:R,KinefoldDrawing:D}=ctx;
let count=0,maxVelocityError=0;
const near=(a,b,t=1e-7)=>{assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} vs ${b}, tolerance ${t}`);count++;};
const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
const cases=[{}, {ra:57,rb:24,rd:45,rc:30,re:22,rf:38}, {L2:360,L3:270,alpha:20,phi0:14}, {ra:45,rb:30,rd:22,rc:35,re:35,rf:25,alpha:35}];
for(const change of cases)for(const theta of [103,120,145,162]){
 const p=M.reference({...M.defaults,...change,theta2:theta}),indices=D.indices(p,theta),bands=D.belts(p,theta);
 const pose=R.VSL.state(p,theta),eps=1e-6,hd=eps/R.VSL.rad;
 for(const index of indices){
  near(distance(index.center,index.primary),index.radius);near(distance(index.center,index.secondary),.72*index.radius);
  const a=index.primary.map((v,i)=>v-index.center[i]),b=index.secondary.map((v,i)=>v-index.center[i]);near(a.reduce((sum,v,i)=>sum+v*b[i],0),0,1e-7);
  near(index.primary[1],0);near(index.secondary[1],0);
 }
 near(indices.find(x=>x.id==='b').angle,pose.t3);near(indices.find(x=>x.id==='d').angle,pose.t5);near(indices.find(x=>x.id==='e').angle,pose.t5);near(indices.find(x=>x.id==='wheel').angle,pose.t6);near(indices.find(x=>x.id==='f').angle,pose.t6);
 const plusIndices=D.indices(p,theta+hd),minusIndices=D.indices(p,theta-hd),plus=D.belts(p,theta+hd),minus=D.belts(p,theta-hd);
 for(const band of bands){
  assert.ok(band.valid);count++;near(distance(band.at(0),band.at(band.loop.total)),0);
  for(const [side,indexId,s] of [['left',band.id[0],2*band.loop.straight+band.loop.right+band.loop.left/2],['right',band.id[1],band.loop.straight+band.loop.right/2]]){
   const offset=s-band.travel,point=band.material(offset),body=indices.find(x=>x.id===indexId),bp=plusIndices.find(x=>x.id===indexId),bm=minusIndices.find(x=>x.id===indexId);
   near(distance(point,body.center),body.radius);
   const v=plus.find(x=>x.id===band.id).material(offset).map((value,i)=>(value-minus.find(x=>x.id===band.id).material(offset)[i])/(2*eps));
   const centerV=bp.center.map((value,i)=>(value-bm.center[i])/(2*eps)),rate=(bp.angle-bm.angle)*R.VSL.rad/(2*eps),r=point.map((value,i)=>value-body.center[i]);
   const expected=[centerV[0]+rate*r[2],0,centerV[2]-rate*r[0]];
   for(let i=0;i<3;i++){maxVelocityError=Math.max(maxVelocityError,Math.abs(v[i]-expected[i]));near(v[i],expected[i],2e-5);}
  }
 }
}
const p=M.reference(M.defaults);for(const t of [100,125,165])near(D.indices(p,t).find(x=>x.id==='wheel').angle,0);
console.log(JSON.stringify({status:'PASS',assertions:count,maxPulleySurfaceVelocityError_mm_per_rad:maxVelocityError,scope:'Exact index radii/orthogonality and finite-difference no-slip material velocities on both wraps of all three belts; baseline wheel spin cancellation.'},null,2));
