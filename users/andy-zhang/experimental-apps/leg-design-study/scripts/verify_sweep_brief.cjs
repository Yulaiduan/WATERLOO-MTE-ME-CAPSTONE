/* Verify original models and the offline equal/unequal design brief.
 * Run from app: node scripts/verify_sweep_brief.cjs [--math-only]
 * Inputs: retained mm/deg/N/Nm comparisons, original V2, Andy model, local HTML,
 * Node22 and sibling locked Playwright. Outputs compact math evidence and
 * ignored screenshots/print PDF. Limits: no new loaded/contact/impact check.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {pathToFileURL}=require('node:url'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const d=JSON.parse(fs.readFileSync(path.join(root,'docs/equal-link-comparison.json'),'utf8'));
 const sourcePath=path.resolve(root,'../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html');
 const source=fs.readFileSync(sourcePath,'utf8'),context=vm.createContext({Math});
 for(const id of ['solver-model','statics-model'])vm.runInContext(source.match(new RegExp(`<script id="${id}">([\\s\\S]*?)<\\/script>`))[1],context);
 vm.runInContext('globalThis.ref={VSL,VSLStatic}',context);
 await import(pathToFileURL(path.join(root,'model.js')).href);const M=globalThis.DesignStudyModel;
 let comparisons=0,maxError=0;
 const eq=(a,b)=>{const e=Math.abs(a-b);assert.ok(e<1e-8,`${a} vs ${b}`);comparisons++;maxError=Math.max(maxError,e);};
 for(const c of d.selected){
  assert.ok(Math.max(c.config.L2,c.config.L3)/Math.min(c.config.L2,c.config.L3)<=1.25+1e-9);
  const p={...M.DEFAULT_CONFIG,...c.config,rc:35,rd:35,re:35,rf:35,
   beta:0,Fy:0,Fz:110.3625,loadMode:'yz',m1:10,m2:0,m3:0,m5:0,m6:0};
  for(const side of ['normal','useful','full'])for(const row of c[side].samples){
   const s=context.ref.VSL.state(p,row.q_deg);eq(s.Pg[0],row.x_mm);eq(s.Pg[1],row.z_mm);
  }
  for(const row of c.force.samples)for(const s of [context.ref.VSLStatic.solve(p,row.q_deg,true),M.statics(p,row.q_deg)]){
   eq(s.Cg[0],row.x_mm);eq(s.Cg[1],row.z_mm);eq(s.tau2,-row.torque_45kg_Nm);
  }
 }
 const e=d.selected.find(c=>c.id==='r2_equal'),u=d.selected.find(c=>c.id==='r2_upper');
 eq(e.force.peak_45kg_hip_Nm,u.force.peak_45kg_hip_Nm);eq(e.force.hip_ROM_deg,u.force.hip_ROM_deg);
 assert.ok(e.comparison_10mm_guide_pass&&u.comparison_10mm_guide_pass);
 assert.equal(d.controls.find(c=>c.id==='control100').feasible_325,false);
 assert.equal(d.selected.find(c=>c.id==='control25').comparison_10mm_guide_pass,false);
 for(const [p,h] of Object.entries(d.provenance.sources))assert.equal(hash(path.join(root,p)),h);
 const checks={passed:true,cases:d.selected.length,scalar_comparisons:comparisons,max_error_mm_Nm:maxError,
  scope:'Original V2/Andy geometry and static equivalent-load torque; exact equal-S,r2 identities. No loaded simulation claim.',
  sources:{'docs/equal-link-comparison.json':hash(path.join(root,'docs/equal-link-comparison.json')),
   'scripts/verify_sweep_brief.cjs':hash(__filename),'model.js':hash(path.join(root,'model.js'))},original_V2_sha256:hash(sourcePath)};
 fs.writeFileSync(path.join(root,'docs/equal-link-comparison-checks.json'),JSON.stringify(checks)+'\n');
 if(process.argv.includes('--math-only')){console.log(JSON.stringify(checks,null,2));return;}
 const {chromium}=require(path.resolve(root,'../wheel-leg-lab/node_modules/playwright'));
 let browser;for(const opt of [{channel:'msedge'},{channel:'chrome'},{}])try{browser=await chromium.launch({headless:true,...opt});break;}catch{}
 assert.ok(browser,'No installed browser');const out=path.join(root,'artifacts/sweep-brief');fs.mkdirSync(out,{recursive:true});
 try{
  const c=await browser.newContext({javaScriptEnabled:false,viewport:{width:1440,height:1100}}),page=await c.newPage();
  const requests=[],errors=[];page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>errors.push(e.message));
  const url=pathToFileURL(path.join(root,'design-sweep-brief.html')).href;await page.goto(url);
  assert.equal(await page.locator('section').count(),4);assert.equal(await page.locator('svg').count(),2);
  assert.deepEqual(JSON.parse(await page.locator('#report-evidence').textContent()),d);
  assert.equal(await page.locator('#comparison-table tbody tr').count(),4);
  assert.ok(!/NaN|undefined|Infinity/.test(await page.locator('body').innerText()));
  assert.equal(await page.locator('svg').evaluateAll(ns=>ns.every(n=>!/(NaN|Infinity|undefined)/.test(n.outerHTML))),true);
  for(const id of ['comparison','geometry','requirements','next-sweep'])await page.locator('#'+id).screenshot({path:path.join(out,id+'.png')});
  await page.screenshot({path:path.join(out,'desktop.png')});
  await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:path.join(out,'mobile.png')});
  assert.equal(requests.length,1);assert.ok(requests.every(u=>u.startsWith('file:')));assert.deepEqual(errors,[]);
  assert.equal(await page.locator('#pdf-link').getAttribute('href'),'docs/design-sweep-brief.pdf');
  assert.equal(fs.readFileSync(path.join(root,'docs/design-sweep-brief.pdf')).subarray(0,5).toString(),'%PDF-');await c.close();
  const ctx=await browser.newContext(),p=await ctx.newPage();await p.goto(url);
  await p.evaluate(()=>{window.__prints=0;window.print=()=>window.__prints++;});await p.locator('#print-report').click();assert.equal(await p.evaluate(()=>window.__prints),1);
  await p.emulateMedia({media:'print'});assert.equal(await p.locator('header').isVisible(),false);
  await p.pdf({path:path.join(out,'browser-print.pdf'),format:'A4',printBackground:true});await ctx.close();
  console.log(JSON.stringify({...checks,sections:4,svg:2,offline_js_disabled:true,external_requests:0},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
