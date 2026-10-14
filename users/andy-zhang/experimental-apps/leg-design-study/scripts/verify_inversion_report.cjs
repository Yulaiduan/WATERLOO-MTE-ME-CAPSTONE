/* Verify the offline alpha-zero report and independent original-model parity.
 * Run: node scripts/verify_inversion_report.cjs from this report folder.
 * Inputs: retained mm/deg/N/Nm evidence, original Jonathan V2 embedded solver,
 * model.js, local HTML/PDF; Node22, sibling locked Playwright, installed browser.
 * Outputs: assertion summary and ignored artifacts/inversion-report screenshots.
 * Limits: numerical/file rendering consistency, no hardware/contact certification.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {pathToFileURL}=require('node:url');const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE_PATH||path.resolve(root,'../wheel-leg-lab/node_modules/playwright'));
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(root,'docs/inversion-path-results.json'),'utf8'));
 await import(pathToFileURL(path.join(root,'model.js')).href);const M=globalThis.DesignStudyModel;
 const source=fs.readFileSync(path.resolve(root,'../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html'),'utf8');
 const context=vm.createContext({Math});
 for(const id of ['solver-model','statics-model'])vm.runInContext(source.match(new RegExp(`<script id="${id}">([\\s\\S]*?)<\\/script>`))[1],context);
 vm.runInContext('globalThis.reference={VSL,VSLStatic};',context);
 let comparisons=0,maxError=0;
 for(const c of [...data.selected,...data.examples,...data.practical]){
  const config={...M.DEFAULT_CONFIG,...c.config};
  for(const row of c.samples){
   for(const model of [M.statics(config,row.q_deg),context.reference.VSLStatic.solve(config,row.q_deg,true)]){
    for(const [a,b] of [[model.Cg[0],row.x_mm],[model.Cg[1],row.z_mm],[model.tau2,row.tau_hip_Nm]]){
     const error=Math.abs(a-b);assert.ok(error<1e-8,`${c.id}: ${a} versus ${b}`);comparisons++;maxError=Math.max(maxError,error);
    }
   }
  }
 }
 let browser;for(const options of [{channel:'msedge'},{channel:'chrome'},{}])try{browser=await chromium.launch({headless:true,...options});break;}catch{}
 assert.ok(browser,'No supported browser available');
 const out=path.join(root,'artifacts/inversion-report');fs.mkdirSync(out,{recursive:true});
 try{
  const ctx=await browser.newContext({viewport:{width:1440,height:1100},javaScriptEnabled:false});
  const page=await ctx.newPage(),requests=[],errors=[];page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>errors.push(e.message));
  const url=pathToFileURL(path.join(root,'inversion-paths.html')).href;await page.goto(url);
  assert.equal(await page.locator('section').count(),12);assert.equal(await page.locator('svg').count(),9);
  assert.equal(await page.locator('input,select,iframe,textarea').count(),0);
  assert.deepEqual(JSON.parse(await page.locator('#report-evidence').textContent()),data);
  assert.equal(await page.locator('#candidate-table tbody tr').count(),data.selected.length);
  const body=await page.locator('body').innerText();assert.ok(!/NaN|undefined|Infinity/.test(body));
  assert.match(body,/26,461,800/);assert.match(body,/12\.02/);assert.match(body,/IMPOSSIBLE/);assert.match(body,/φ₀/);
  assert.equal(await page.locator('svg').evaluateAll(ns=>ns.every(n=>!/(NaN|Infinity|undefined)/.test(n.outerHTML))),true);
  await page.screenshot({path:path.join(out,'desktop.png')});
  for(const id of ['practical','profiles','inversion','phase','validation'])await page.locator('#'+id).screenshot({path:path.join(out,id+'.png')});
  await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:path.join(out,'mobile.png')});
  assert.deepEqual(requests,[url]);assert.deepEqual(errors,[]);
  assert.equal(await page.locator('#pdf-link').getAttribute('href'),'docs/inversion-path-report.pdf');
  assert.equal(fs.readFileSync(path.join(root,'docs/inversion-path-report.pdf')).subarray(0,5).toString(),'%PDF-');
  await ctx.close();
  const enabled=await browser.newContext({viewport:{width:1440,height:1100}}),p=await enabled.newPage();await p.goto(url);
  await p.evaluate(()=>{window.__print=0;window.print=()=>window.__print++;});await p.locator('#print-report').click();assert.equal(await p.evaluate(()=>window.__print),1);
  await p.emulateMedia({media:'print'});assert.equal(await p.locator('.toc').isVisible(),false);assert.equal(await p.locator('#print-report').isVisible(),false);
  await p.pdf({path:path.join(out,'browser-print.pdf'),format:'A4',printBackground:true});await enabled.close();
  console.log(JSON.stringify({passed:true,comparisons,max_error:maxError,sections:12,inline_svg:9,external_requests:0,js_disabled:true,artifacts:'artifacts/inversion-report'},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
