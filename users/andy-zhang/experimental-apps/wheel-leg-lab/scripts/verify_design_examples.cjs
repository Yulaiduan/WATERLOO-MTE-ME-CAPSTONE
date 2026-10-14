/* Check actual Motion Lab labelled examples, exports and menu integration.
 * Run: node scripts/verify_design_examples.cjs on the local 4186 server.
 * Inputs: retained mm/degree designs, live DOM/canvas and ten local GIF assets.
 * Outputs: browser assertion summary and ignored desktop/mobile captures.
 * Limits: geometry/UI/export checks only; no dynamics or hardware certification.
 */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 let browser;for(const channel of ['msedge','chrome',undefined])try{browser=await chromium.launch({headless:true,...(channel?{channel}:{})});break;}catch{}
 assert.ok(browser,'No browser available');
 try{
  const ctx=await browser.newContext({viewport:{width:1440,height:1100}}),page=await ctx.newPage(),errors=[],external=[],nativeLaunches=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4186/'))external.push(r.url());if(r.method()==='POST'&&r.url().includes('/api/native-gui'))nativeLaunches.push(r.url());});
  const folder=path.resolve(__dirname,'../artifacts/design-examples');fs.mkdirSync(folder,{recursive:true});
  await page.goto('http://127.0.0.1:4186/design-examples/');await page.waitForFunction(()=>window.DesignExamples);
  assert.equal(await page.locator('.example').count(),5);assert.equal(await page.locator('.gif-links a').count(),10);
  await page.locator('#play').click();assert.equal(await page.locator('#play').textContent(),'Play');
  for(const mode of ['working','inversion']){
   await page.selectOption('#view-mode',mode);
   for(const fraction of [0,.5,1]){
    await page.locator('#scrub').evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));},String(fraction));
    const poses=await page.locator('canvas').evaluateAll(ns=>ns.map(n=>JSON.parse(n.dataset.pose)));
    assert.ok(poses.every(p=>p.mode===mode&&p.fraction===fraction&&Number.isFinite(p.C[0])&&Number.isFinite(p.C[1])));
    if(mode==='inversion'&&fraction===.5)assert.ok(poses.every(p=>p.hipDistance<30&&!p.projectedClearancePass));
   }
   await page.locator('#scrub').evaluate(el=>{el.value='.5';el.dispatchEvent(new Event('input',{bubbles:true}));});
   await page.screenshot({path:path.join(folder,mode+'.png'),fullPage:true});
  }
  await page.selectOption('#design-filter','simple-guide');assert.equal(await page.locator('.example:visible').count(),1);
  await page.locator('#show-guide').uncheck();await page.locator('#show-clearance').uncheck();
  assert.ok(await page.locator('canvas').first().evaluate(n=>n.toDataURL().length>5000));
  await page.locator('#show-guide').check();await page.locator('#show-clearance').check();
  await page.selectOption('#design-filter','all');
  await page.locator('#play').click();const before=await page.locator('#scrub').inputValue();await page.waitForTimeout(180);assert.notEqual(await page.locator('#scrub').inputValue(),before);await page.locator('#play').click();
  for(const link of await page.locator('.gif-links a').evaluateAll(ns=>ns.map(n=>n.href))){
   const response=await ctx.request.get(link);assert.equal(response.status(),200);assert.match((await response.body()).subarray(0,6).toString(),/^GIF8[79]a$/);
  }
  await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.screenshot({path:path.join(folder,'mobile.png'),fullPage:true});
  await page.setViewportSize({width:1440,height:1100});await page.goto('http://127.0.0.1:4186/?tab=studies&study=design-examples');
  const iframe=page.locator('iframe[data-key="studies"]');await iframe.waitFor();const frame=await iframe.contentFrame();await frame.locator('#view-mode').waitFor();
  assert.equal(await page.locator('#study-select').inputValue(),'design-examples');
  await page.locator('#show-gui').click();assert.match(await page.locator('body').innerText(),/These examples show prescribed kinematics/);assert.deepEqual(nativeLaunches,[]);
  await frame.locator('#view-mode').selectOption('inversion');await frame.locator('#design-filter').selectOption('near-equal-indexed');
  await page.locator('#theme-toggle').click();await frame.locator('html[data-theme="dark"]').waitFor();
  await page.selectOption('#study-select','linear');await page.selectOption('#study-select','design-examples');
  await frame.locator('#design-filter').waitFor();assert.equal(await frame.locator('#view-mode').inputValue(),'inversion');assert.equal(await frame.locator('#design-filter').inputValue(),'near-equal-indexed');
  await page.screenshot({path:path.join(folder,'embedded-dark.png'),fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log(JSON.stringify({passed:true,examples:5,gifs:10,modes:2,controls:true,menu_memory:true,dark_theme:true,mobile:true,external_requests:0,page_errors:0}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
