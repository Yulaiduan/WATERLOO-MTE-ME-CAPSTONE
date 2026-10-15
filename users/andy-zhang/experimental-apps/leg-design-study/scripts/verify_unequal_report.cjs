/* Check original V2/Andy statics and the offline unequal-inversion report.
 * Run from app: node scripts/verify_unequal_report.cjs [--math-only]
 * Inputs: retained mm/degree/N/Nm cases, original embedded V2, local report,
 * Node22, sibling locked Playwright and installed Edge/Chrome. Outputs compact
 * math JSON and ignored QA captures. Limits: no actual stiffness/hardware proof.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {pathToFileURL}=require('node:url'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const d=JSON.parse(fs.readFileSync(path.join(root,'docs/unequal-inversion-results.json'),'utf8'));
 const sourcePath=path.resolve(root,'../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html');
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
 for(const id of d.recommended_ids){const c=d.selected.find(c=>c.id===id);assert.ok(c.config.L2>c.config.L3);assert.equal(c.projection.wheel_upper_segment_min_mm,0);assert.equal(c.projection.physical_full_inversion_validated,false);}
 for(const [p,h] of Object.entries(d.provenance.sources))assert.equal(hash(path.join(root,p)),h);
 const checks={passed:true,selected_cases:d.selected.length,scalar_comparisons:comparisons,max_error_mm_Nm:maxError,
  scope:'Original V2 normal/useful/full geometry and vertical-load statics, Andy2D statics; no compliance/force-engine claim.',
  sources:{'docs/unequal-inversion-results.json':hash(path.join(root,'docs/unequal-inversion-results.json')),
   'scripts/verify_unequal_report.cjs':hash(__filename),'model.js':hash(path.join(root,'model.js'))},original_V2_sha256:hash(sourcePath)};
 fs.writeFileSync(path.join(root,'docs/unequal-inversion-math-checks.json'),JSON.stringify(checks)+'\n');
 if(process.argv.includes('--math-only')){console.log(JSON.stringify(checks,null,2));return;}
 const {chromium}=require(path.resolve(root,'../wheel-leg-lab/node_modules/playwright'));
 let browser;for(const opt of [{channel:'msedge'},{channel:'chrome'},{}])try{browser=await chromium.launch({headless:true,...opt});break;}catch{}
 assert.ok(browser,'No installed browser');const out=path.join(root,'artifacts/unequal-report');fs.mkdirSync(out,{recursive:true});
 try{
  const c=await browser.newContext({javaScriptEnabled:false,viewport:{width:1440,height:1100}}),page=await c.newPage();
  const requests=[],errors=[];page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>errors.push(e.message));
  const url=pathToFileURL(path.join(root,'unequal-inversion.html')).href;await page.goto(url);
  assert.equal(await page.locator('section').count(),6);assert.equal(await page.locator('svg').count(),5);
  assert.equal(await page.locator('input,select,iframe,textarea').count(),0);
  assert.deepEqual(JSON.parse(await page.locator('#report-evidence').textContent()),d);
  assert.equal(await page.locator('#shortlist tbody tr').count(),4);
  assert.ok(!/NaN|undefined|Infinity/.test(await page.locator('body').innerText()));
  assert.equal(await page.locator('svg').evaluateAll(ns=>ns.every(n=>!/(NaN|Infinity|undefined)/.test(n.outerHTML))),true);
  await page.screenshot({path:path.join(out,'desktop.png')});
  for(const id of ['options','inversion','clearance','force','search'])await page.locator('#'+id).screenshot({path:path.join(out,id+'.png')});
  await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:path.join(out,'mobile.png')});
  assert.equal(requests.length,5);assert.ok(requests.every(u=>u.startsWith('file:')));assert.deepEqual(errors,[]);
  assert.equal(await page.locator('img').count(),4);assert.ok(await page.locator('img').evaluateAll(ns=>ns.every(n=>n.complete&&n.naturalWidth===800)));
  const manifest=JSON.parse(fs.readFileSync(path.join(root,'docs/unequal-animations/manifest.json'),'utf8'));
  for(const item of manifest.cases){assert.equal(hash(path.join(root,'docs/unequal-animations',item.file)),item.sha256);assert.equal(item.frames,80);}
  assert.equal(await page.locator('#pdf-link').getAttribute('href'),'docs/unequal-inversion-report.pdf');
  assert.equal(fs.readFileSync(path.join(root,'docs/unequal-inversion-report.pdf')).subarray(0,5).toString(),'%PDF-');await c.close();
  const ctx=await browser.newContext(),p=await ctx.newPage();await p.goto(url);
  await p.evaluate(()=>{window.__prints=0;window.print=()=>window.__prints++;});await p.locator('#print-report').click();assert.equal(await p.evaluate(()=>window.__prints),1);
  await p.emulateMedia({media:'print'});assert.equal(await p.locator('.toc').isVisible(),false);
  await p.pdf({path:path.join(out,'browser-print.pdf'),format:'A4',printBackground:true});await ctx.close();
  console.log(JSON.stringify({...checks,sections:6,svg:5,offline_js_disabled:true,external_requests:0},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
