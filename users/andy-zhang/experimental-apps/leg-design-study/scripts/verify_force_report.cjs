/* Check original V2 force/geometry and offline report rendering.
 * Run: node scripts/verify_force_report.cjs [--math-only] from this app.
 * Inputs: retained mm/deg/N/Nm evidence, original V2, local HTML/PDF, Node22
 * and sibling locked Playwright / installed Edge. Outputs: math checks JSON
 * and ignored browser captures. Limits: no hardware, impact or contact proof.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');const {pathToFileURL}=require('node:url');
const crypto=require('node:crypto');const root=path.resolve(__dirname,'..');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(root,'docs/force-travel-results.json'),'utf8'));
 const sourcePath=path.resolve(root,'../../../jonathan-xie/experimental-apps/vsl-solver/v2/v2-quasi-static.html');
 const source=fs.readFileSync(sourcePath,'utf8'),ctx=vm.createContext({Math});
 for(const id of ['solver-model','statics-model'])vm.runInContext(source.match(new RegExp(`<script id="${id}">([\\s\\S]*?)<\\/script>`))[1],ctx);
 vm.runInContext('globalThis.ref={VSL,VSLStatic};',ctx);
 await import(pathToFileURL(path.join(root,'model.js')).href);const M=globalThis.DesignStudyModel;
 let n=0,max=0;
 const check=(a,b)=>{let e=Math.abs(a-b);assert.ok(e<1e-8,`${a} versus ${b}`);n++;max=Math.max(max,e);};
 for(const c of data.selected){
  const p={...M.DEFAULT_CONFIG,...c.config,rc:35,rd:35,re:35,rf:35,
   beta:0,Fy:0,Fz:110.3625,loadMode:'yz',m1:10,m2:0,m3:0,m5:0,m6:0};
  for(const s of c.force.samples){
   const v=ctx.ref.VSLStatic.solve(p,s.q_deg,true),m=M.statics(p,s.q_deg);
   assert.ok(v.valid);
   for(const r of [v,m]){check(r.Cg[0],s.x_mm);check(r.Cg[1],s.z_mm);check(r.tau2,-s.torque_45kg_Nm);}
   check(v.tau4,0);check(v.virtualWorkError,0);
  }
 }
 for(const [p,h] of Object.entries(data.provenance.sources))assert.equal(hash(path.join(root,p)),h);
 const checks={passed:true,selected_cases:data.selected.length,scalar_comparisons:n,max_error_mm_Nm:max,
  scope:'Original Jonathan V2 and existing Andy 2D statics; pure vertical load, beta0, massless moving links; not actual motor force validation.',
  sources:{'docs/force-travel-results.json':hash(path.join(root,'docs/force-travel-results.json')),
   'scripts/verify_force_report.cjs':hash(__filename),'model.js':hash(path.join(root,'model.js'))},
  original_V2_sha256:hash(sourcePath)};
 fs.writeFileSync(path.join(root,'docs/force-travel-math-checks.json'),JSON.stringify(checks)+'\n');
 if(process.argv.includes('--math-only')){console.log(JSON.stringify(checks,null,2));return;}
 const {chromium}=require(path.resolve(root,'../wheel-leg-lab/node_modules/playwright'));
 let browser;for(const opt of [{channel:'msedge'},{channel:'chrome'},{}])try{browser=await chromium.launch({headless:true,...opt});break;}catch{}
 assert.ok(browser,'No installed supported browser');
 const out=path.join(root,'artifacts/force-travel-report');fs.mkdirSync(out,{recursive:true});
 try{
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:1440,height:1100}}),page=await context.newPage();
  const requests=[],errors=[];page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>errors.push(e.message));
  const url=pathToFileURL(path.join(root,'force-travel.html')).href;await page.goto(url);
  assert.equal(await page.locator('section').count(),9);assert.equal(await page.locator('svg').count(),7);
  assert.equal(await page.locator('input,select,iframe,textarea').count(),0);
  assert.deepEqual(JSON.parse(await page.locator('#report-evidence').textContent()),data);
  assert.equal(await page.locator('#shortlist tbody tr').count(),4);
  assert.ok(!/NaN|undefined|Infinity/.test(await page.locator('body').innerText()));
  assert.equal(await page.locator('svg').evaluateAll(ns=>ns.every(n=>!/(NaN|Infinity|undefined)/.test(n.outerHTML))),true);
  assert.match(await page.locator('body').innerText(),/11,478,060/);
  assert.match(await page.locator('body').innerText(),/IMPOSSIBLE/);
  await page.screenshot({path:path.join(out,'desktop.png')});
  for(const id of ['curves','travel','indexed','inversion'])await page.locator('#'+id).screenshot({path:path.join(out,id+'.png')});
  await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:path.join(out,'mobile.png')});
  assert.deepEqual(requests,[url]);assert.deepEqual(errors,[]);
  assert.equal(await page.locator('#pdf-link').getAttribute('href'),'docs/force-travel-report.pdf');
  assert.equal(fs.readFileSync(path.join(root,'docs/force-travel-report.pdf')).subarray(0,5).toString(),'%PDF-');
  await context.close();
  const c=await browser.newContext(),p=await c.newPage();await p.goto(url);
  await p.evaluate(()=>{window.__print=0;window.print=()=>window.__print++;});await p.locator('#print-report').click();assert.equal(await p.evaluate(()=>window.__print),1);
  await p.emulateMedia({media:'print'});assert.equal(await p.locator('.toc').isVisible(),false);
  await p.pdf({path:path.join(out,'browser-print.pdf'),format:'A4',printBackground:true});await c.close();
  console.log(JSON.stringify({...checks,sections:9,svg:7,offline_js_disabled:true,external_requests:0},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
