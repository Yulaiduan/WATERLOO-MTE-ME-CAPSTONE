/* Independently verify RMS comparisons against original Jonathan V2 and Andy2D.
 * Run from app: node scripts/verify_rms_links.cjs [--math-only]
 * Inputs mm/deg/N/Nm retained cases and original models; Node22, existing local
 * Playwright for optional offline HTML QA. Outputs compact check JSON and
 * ignored browser images/print PDF. No loaded dynamics/contact validation.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const d=JSON.parse(fs.readFileSync(path.join(root,'docs/rms-link-results.json'),'utf8'));
 const src=path.resolve(root,'../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html');
 const source=fs.readFileSync(src,'utf8'),ctx=vm.createContext({Math});
 for(const id of ['solver-model','statics-model'])vm.runInContext(source.match(new RegExp(`<script id="${id}">([\\s\\S]*?)<\\/script>`))[1],ctx);
 vm.runInContext('globalThis.ref={VSL,VSLStatic}',ctx);
 await import(pathToFileURL(path.join(root,'model.js')).href);const M=globalThis.DesignStudyModel;
 let comparisons=0,maxError=0,maxRmsError=0,maxTimeError=0;
 const eq=(a,b,tol=1e-8)=>{let e=Math.abs(a-b);assert.ok(e<tol,`${a} vs ${b}; error${e}`);comparisons++;maxError=Math.max(maxError,e);return e;};
 const simpson=(ys,h)=>{let s=ys[0]+ys.at(-1);for(let i=1;i<ys.length-1;i++)s+=(i%2?4:2)*ys[i];return s*h/3;};
 for(const c of d.selected){
  assert.ok(c.length_ratio<=1.25+1e-10&&c.assumed_guide10_pass&&c.full_ideal_inverse);
  const p={...M.DEFAULT_CONFIG,...c.config,rc:35,rd:35,re:35,rf:35,beta:0,Fy:0,Fz:d.force_N,loadMode:'yz',m1:10,m2:0,m3:0,m5:0,m6:0};
  const state=q=>ctx.ref.VSL.state(p,q),torque=q=>-ctx.ref.VSLStatic.solve(p,q,true).tau2;
  for(const side of ['normal','useful','full'])for(const row of c[side].samples){const s=state(row.q_deg);eq(s.Pg[0],row.x_mm);eq(s.Pg[1],row.z_mm);}
  for(const row of c.force.samples)for(const s of [ctx.ref.VSLStatic.solve(p,row.q_deg,true),M.statics(p,row.q_deg)]){
   eq(s.Cg[0],row.x_mm);eq(s.Cg[1],row.z_mm);eq(s.tau2,-row.torque_45kg_Nm);
  }
  for(const row of c.timed.samples)eq(torque(row.q_deg),row.torque_45kg_Nm);
  const [lo,hi]=c.force.usable_angle_bounds_deg,n=800,ys=[];
  for(let i=0;i<=n;i++)ys.push(torque(lo+(hi-lo)*i/n)**3);
  const rms=Math.sqrt(simpson(ys,(hi-lo)*Math.PI/180/n)/(d.force_N*.285));
  maxRmsError=Math.max(maxRmsError,eq(rms,c.rms_quad_hip_Nm));
  eq(c.rms_quad_relative_knee_Nm,rms/c.config.qab);
  const z0=state(lo).Pg[1],ts=[];
  for(let i=0;i<=1000;i++){
   const t=i/1000,z=z0+285*(10*t**3-15*t**4+6*t**5);let l=lo,h=hi;
   for(let j=0;j<40;j++){let m=(l+h)/2;if(state(m).Pg[1]<z)l=m;else h=m;}
   ts.push(torque((l+h)/2)**2);
  }
  maxTimeError=Math.max(maxTimeError,eq(Math.sqrt(simpson(ts,.001)),c.timed.quintic_static_rms_hip_Nm));
 }
 const control=d.groups.fixed450_r2.map(id=>d.selected.find(c=>c.id===id));
 for(const c of control){eq(c.rms_quad_hip_Nm,control[0].rms_quad_hip_Nm);eq(c.force.hip_ROM_deg,control[0].force.hip_ROM_deg);}
 assert.equal(d.search.counts.enumerated,582471);assert.equal(d.groups.grid.length,36);
 for(const [p,h] of Object.entries(d.provenance.sources))assert.equal(hash(path.join(root,p)),h);
 const checks={passed:true,cases:d.selected.length,scalar_comparisons:comparisons,max_error_mm_Nm:maxError,max_height_RMS_error_Nm:maxRmsError,max_quintic_RMS_error_Nm:maxTimeError,
  scope:'Original V2/Andy geometry/statics plus independent dense height and quintic-time static RMS; no inertia/clearance/thermal claim',
  sources:{'docs/rms-link-results.json':hash(path.join(root,'docs/rms-link-results.json')),'scripts/verify_rms_links.cjs':hash(__filename),'model.js':hash(path.join(root,'model.js'))},original_V2_sha256:hash(src)};
 const engine=JSON.parse(fs.readFileSync(path.join(root,'docs/rms-link-engine-checks.json'),'utf8'));
 assert.ok(engine.all_passed);assert.equal(engine.cases.length,3);
 for(const [p,h] of Object.entries(engine.sources))assert.equal(hash(path.join(root,p)),h);
 checks.unloaded_engine_cases=3;
 fs.writeFileSync(path.join(root,'docs/rms-link-checks.json'),JSON.stringify(checks)+'\n');
 if(process.argv.includes('--math-only')){console.log(JSON.stringify(checks,null,2));return;}
 const {chromium}=require(path.resolve(root,'../wheel-leg-lab/node_modules/playwright'));let browser;
 for(const opt of [{channel:'msedge'},{channel:'chrome'},{}])try{browser=await chromium.launch({headless:true,...opt});break;}catch{}
 assert.ok(browser);const out=path.join(root,'artifacts/rms-links');fs.mkdirSync(out,{recursive:true});
 try{
  const c=await browser.newContext({javaScriptEnabled:false,viewport:{width:1440,height:1100}}),p=await c.newPage(),requests=[],errors=[];
  p.on('request',r=>requests.push(r.url()));p.on('pageerror',e=>errors.push(e.message));const url=pathToFileURL(path.join(root,'rms-link-comparison.html')).href;await p.goto(url);
  assert.equal(await p.locator('section').count(),4);assert.equal(await p.locator('svg').count(),3);
  assert.deepEqual(JSON.parse(await p.locator('#report-evidence').textContent()),d);
  assert.ok(!/NaN|undefined|Infinity/.test(await p.locator('body').innerText()));
  for(const id of ['matched','compact','meaning','limits'])await p.locator('#'+id).screenshot({path:path.join(out,id+'.png')});
  await p.setViewportSize({width:390,height:844});await p.evaluate(()=>scrollTo(0,0));assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await p.screenshot({path:path.join(out,'mobile.png')});
  assert.equal(requests.length,1);assert.deepEqual(errors,[]);assert.ok(requests.every(u=>u.startsWith('file:')));
  assert.equal(await p.locator('#pdf-link').getAttribute('href'),'docs/rms-link-report.pdf');assert.equal(fs.readFileSync(path.join(root,'docs/rms-link-report.pdf')).subarray(0,5).toString(),'%PDF-');await c.close();
  const ct=await browser.newContext(),pp=await ct.newPage();await pp.goto(url);await pp.evaluate(()=>{window.__prints=0;window.print=()=>window.__prints++;});
  await pp.locator('#print-report').click();assert.equal(await pp.evaluate(()=>window.__prints),1);await pp.emulateMedia({media:'print'});assert.equal(await pp.locator('header').isVisible(),false);
  await pp.pdf({path:path.join(out,'browser-print.pdf'),format:'A4',printBackground:true});await ct.close();
  console.log(JSON.stringify({...checks,offline_js_disabled:true,external_requests:0,sections:4,svg:3},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
