// Verify relocated atlas/workbench/linkage UI. Run: node scripts/verify_import.cjs.
// Inputs: saved port-4175 build and SI example profiles; writes ignored screenshots.
// Requires Playwright/Edge; software rendering checks do not validate hardware.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:1000}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',r=>r.request().url().startsWith('http://127.0.0.1:4175/')?r.continue():r.abort());
  await page.goto('http://127.0.0.1:4175/');
  await page.locator('#inspector tbody tr').last().waitFor();
  assert.equal(await page.locator('#inspector tbody tr').count(),7);
  const region=page.locator('#region-select');
  const choices=await region.locator('option').evaluateAll(xs=>xs.map(x=>x.value));
  await region.selectOption(choices[1]);
  assert.ok((await page.locator('#inspector').textContent()).includes('illustrative'));
  await page.goto('http://127.0.0.1:4175/workbench/');
  await page.locator('#source-mode').selectOption('measured');
  assert.ok((await page.locator('body').textContent()).includes('USGS'));
  await page.locator('[data-action="run"]').click();
  await page.getByRole('heading',{name:'Run status and constraints'}).waitFor({timeout:60000});
  assert.equal(await page.locator('[role="alert"]').count(),0);
  assert.equal(await page.locator('path').evaluateAll(ps=>ps.some(p=>/NaN|Infinity/.test(p.getAttribute('d')||''))),false);
  await page.setViewportSize({width:390,height:1000});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  const output=path.join(__dirname,'../artifacts/import-review');fs.mkdirSync(output,{recursive:true});
  await page.screenshot({path:path.join(output,'workbench-mobile.png'),fullPage:true});
  await page.goto('http://127.0.0.1:4175/linkage/');
  await page.locator('#app').waitFor();
  assert.ok((await page.locator('body').textContent()).includes('Linkage simulator'));
  assert.deepEqual(errors,[]);
  console.log('PASS: relocated atlas controls, observed-USGS worker run, finite plots, mobile workbench and linkage route; local assets, no page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
