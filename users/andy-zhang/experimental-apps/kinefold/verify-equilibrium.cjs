/** Compare native equilibrium datasets with independently loaded original V4.
 * Run: node verify-equilibrium.cjs. Inputs: deterministic mm/deg/kg/N designs;
 * outputs assertion/branch counts. Verifies analytical chart meaning, domain
 * isolation and undefined-data handling; no hardware or global-extrema claim.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const read=f=>fs.readFileSync(path.join(__dirname,f),'utf8'),ctx=vm.createContext({});
vm.runInContext(['reference-v4.js','model.js','equilibrium-data.js'].map(read).join('\n'),ctx);
const {Kinefold:M,KinefoldEquilibriumData:D}=ctx,provenance=JSON.parse(read('reference.json'));
const html=fs.readFileSync(path.resolve(__dirname,'../../../..',provenance.source),'utf8').replace(/\r\n/g,'\n');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
assert.equal(hash(html),provenance.source_sha256);
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
const retained=[...scripts.slice(0,2),scripts[2].split('const VSLDomains=')[0]].join('\n');
assert.equal(hash(retained),provenance.retained_blocks_sha256);
const original=vm.createContext({});vm.runInContext(retained+'\nglobalThis.O={VSL,VSLStatic,VSLSpring};',original);
const O=original.O;let assertions=2,cases=0,branches=0;
function ok(v,message){assert.ok(v,message);assertions++;}
function near(a,b,tol=1e-8){ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=tol,`${a} != ${b}`);}
function reference(p){const r={...p,Fy:-p.Fx,loadMode:p.loadMode==='contact'?'nt':'yz',springK:p.springLaw==='constant'?0:p.springK};if(p.loadMode==='weight'){r.Fy=0;r.Fz=(p.m1+p.m2+p.m3+p.m5+p.m6)*p.g;}return O.VSLStatic.resolveLoads(r);}
function compare(p,q,axis='t2',x=q){const r=reference(p),s=O.VSLStatic.solve(r,q,false),k=O.VSL.state(r,q),a=D.row(p,q,axis,x);cases++;ok(a.valid===s.valid);near(a.x,axis==='dz'?k.dz:x);for(const key of ['t3','t5','t6','du','dv','dz'])near(a[key],k[key]);near(a.dx,-k.dy);for(const [key,u,v]of [['gammaUV',k.du,k.dv],['gammaXZ',-k.dy,k.dz]]){if(Math.hypot(u,v)<1e-9)ok(a[key]===null);else near(a[key],Math.atan2(Math.abs(u)<1e-9?0:u,Math.abs(v)<1e-9?0:v)*180/Math.PI);}
for(const key of ['tauG','tauS','tau2','tau4','Fs'])s.valid?near(a[key],s[key]):ok(a[key]===null);
for(const key of ['ab','cd','ef'])if(s.valid){near(a[key+'U'],s[key].U);near(a[key+'L'],s[key].L);near(a[key],Math.max(s[key].U,s[key].L));ok(a[key+'Active']===s[key].active);}else ok(a[key]===null);
for(const key of ['F12','F14','F25','F32','Fw'])s.valid?near(a[key],Math.hypot(...s[key])):ok(a[key]===null);
const mass=p.m1+p.m2+p.m3+p.m5+p.m6,feq=s.spring?.Feq;
if(s.valid&&p.g>0&&mass>0&&Number.isFinite(feq)){near(a.supportKg,feq/p.g-mass);near(a.supportPercent,100*(feq/(mass*p.g)-1));}else{ok(a.supportKg===null);ok(a.supportPercent===null);}}
for(let i=0;i<24;i++){const p={...M.defaults,alpha:i%4*11,beta:i%7*13,m2:i%3*.2,m3:.35,m5:.1,m6:.8,Fx:i-12,Fz:80+i,Fn:70+i,Ft:i-10,loadMode:['weight','global','contact'][i%3],springLaw:i%2?'v4':'constant',Tab0:i,Tcd0:i*.7,Tef0:i*.3};for(const q of [100,117.25,132.5,151,165])compare(p,q);for(const beta of [0,23.75,90])compare({...p,beta},p.theta2,'beta',beta);for(const alpha of [0,17.5,45])compare({...p,alpha},p.theta2,'alpha',alpha);}
const base={...M.defaults},before=JSON.stringify(base),d=D.create(base),t=d.sweep('t2');ok(t===d.sweep('t2'),'cache identity');ok(D.coverage.length===17);ok(new Set(D.coverage.map(x=>x.id)).size===17);ok(D.coverage.filter(x=>x.group==='loads').length===12);ok(JSON.stringify(base)===before,'diagnostic sampling must not mutate builder');
const o=D.options(base,{thetaMin:105,thetaMax:106,expanded:true});near(D.domain(base,o,'t2').min,105);near(D.domain(base,o,'t2').max,106);near(D.domain(base,{...o,clamp:false},'t2').max,270);near(D.domain(base,{...o,clamp:false,expanded:false},'t2').max,180);ok(D.domain(base,{...o,thetaMin:110,thetaMax:110},'t2').min<110);ok(D.row(base,base.te).gammaXZ===null,'zero displacement inclination');
for(const p of [{...base,g:0},{...base,m1:0,m2:0,m3:0,m5:0,m6:0}]){const rows=D.create(p).suspension();ok(rows.every(x=>x.supportKg===null&&x.supportPercent===null));compare(p,p.theta2);}
ok(D.row({...base,alpha:0},90).supportPercent===null,'zero vertical Jacobian is undefined');
const abs=D.create(base,{absolute:true}).sweep('t2');near(abs[200].tau2,t[200].tau2);
// Expanded high-ratio geometry has genuine repeated vertical-travel roots.
const mult={...base,ra:75,rb:25,springEnabled:false},multi=D.create(mult,{clamp:false,expanded:true}),rows=multi.sweep('dz');
ok(rows.every((r,i)=>i===0||r.theta2>=rows[i-1].theta2),'retain parameter order');
ok(rows.some((r,i)=>i>1&&(r.x-rows[i-1].x)*(rows[i-1].x-rows[i-2].x)<0),'travel reverses');
const values=rows.map(x=>x.x),lo=Math.min(...values),hi=Math.max(...values);
for(let i=1;i<20;i++){const z=lo+(hi-lo)*i/20,poses=multi.posesAtDz(z),source=O.VSLStatic.posesAtDz(reference(mult),z,90,270);ok(poses.length===source.length);if(poses.length>1)branches++;for(let j=0;j<poses.length;j++){near(poses[j].theta2,source[j]);near(poses[j].dz,z,1e-6);}}
ok(branches>0,'multiple dz roots exercised');assert.throws(()=>D.create({...base,L2:0}));assertions++;
console.log(JSON.stringify({status:'PASS',assertions,independentSourceCases:cases,multiBranchTravelQueries:branches,sourceCharts:D.coverage.length,limitations:'Finite analytical samples; no hardware or certified global peak validation.'},null,2));
