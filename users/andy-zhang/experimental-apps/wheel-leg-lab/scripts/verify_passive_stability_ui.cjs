/** Verify passive-stability cards and legacy-profile provenance in both benches.
 * Run: node scripts/verify_passive_stability_ui.cjs with Motion Lab on port 4186.
 * Inputs: live SI solver profiles/results, then explicitly labelled metadata-only
 * render fixtures for restoring/neutral/unstable/N/A badge states.
 * Outputs: assertions and ignored JSON/screenshots under artifacts/stability-ui.
 * Fixtures check rendering; local/global physical stability is not certified here.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const origin='http://127.0.0.1:4186';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1000},acceptDownloads:true}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const defaults=await (await page.request.get(origin+'/api/defaults')).json(),presets=await (await page.request.get(origin+'/api/spring-presets')).json();
  const out=path.join(__dirname,'../artifacts/stability-ui');fs.mkdirSync(out,{recursive:true});
  for(const route of ['physics','mathematical']){
   await page.goto(origin+'/'+route+'/?loadOnly=1');await page.locator('[data-key="spring_topology"]').waitFor();
   const old={...defaults,duration:.9,start:.2,position_amplitude:.005};delete old.spring_integration;
   await page.evaluate(config=>window.postMessage({type:'motion-lab-load-profile',config},location.origin),old);
   assert.equal(await page.locator('#spring-integration-warning').isVisible(),false);
   const responsePromise=page.waitForResponse(r=>r.url().includes('/simulate'));await page.locator('#run').click();const response=await responsePromise,result=await response.json();
   assert.equal(response.status(),200,JSON.stringify(result));assert.equal(result.config.spring_integration,'point_force');
   await page.locator('#status').filter({hasText:'Recorded'}).waitFor();
   assert.equal(await page.locator('#passive-stability').getAttribute('data-classification'),result.passive_stability.classification);
   for(const id of ['stability-mean','stability-left','stability-right'])assert.match(await page.locator('#'+id).textContent(),/N\/m/);
   assert.match(await page.locator('#stability-balance').textContent(),/N \/ .*kgf/);
   assert.match(await page.locator('.stability-scope').textContent(),/Excludes knee feedback, damping and contact/);
   const downloaded=page.waitForEvent('download');await page.locator('#save-data').click();const download=await downloaded;await download.saveAs(path.join(out,route+'-live.json'));
   assert.deepEqual(JSON.parse(fs.readFileSync(path.join(out,route+'-live.json'),'utf8')).passive_stability,result.passive_stability);
   // These metadata packets exercise badges independently of the physical model.
   for(const classification of ['restoring','neutral','unstable','not_applicable']){
    const stability=classification==='not_applicable'?{classification,reason:'Fixed-fixture diagnostic.'}:{...result.passive_stability,classification,net_ride_stiffness_N_m:123,left_ride_stiffness_N_m:120,right_ride_stiffness_N_m:126,initial_force_balance_residual_N:9.80665,notes:['Metadata render fixture.']};
    await page.evaluate(result=>window.postMessage({type:'motion-lab-load-result',result},location.origin),{...result,passive_stability:stability});
    assert.equal(await page.locator('#passive-stability').getAttribute('data-classification'),classification);
    if(classification==='not_applicable')assert.equal(await page.locator('#stability-mean').textContent(),'—');else assert.match(await page.locator('#stability-balance').textContent(),/1.00 kgf/);
   }
   const legacy={...old,spring_topology:'legacy_tip',spring_mode:'captured',spring_transmission:'direct',spring_force_law:'hooke',spring_integration:'native_legacy'};
   await page.evaluate(config=>window.postMessage({type:'motion-lab-load-profile',config},location.origin),legacy);
   assert.equal(await page.locator('#spring-integration-warning').isVisible(),true);assert.match(await page.locator('#spring-integration-warning').textContent(),/native_legacy.*bias ride response/);
   const profileDownload=page.waitForEvent('download');await page.locator('#profile').click();const profile=await profileDownload;await profile.saveAs(path.join(out,route+'-legacy-profile.json'));
   assert.equal(JSON.parse(fs.readFileSync(path.join(out,route+'-legacy-profile.json'),'utf8')).config.spring_integration,'native_legacy');
   await page.locator('[data-key="spring_topology"]').selectOption('hip_pulley');
   assert.equal(await page.locator('#spring-integration-warning').isVisible(),false);
   for(const [key,scale] of [['stiffness',1],['damping',1],['spring_pulley_radius',1000]])assert.equal(Number(await page.locator(`[data-key="${key}"]`).inputValue()),presets.catalog.hip_pulley.defaults[key]*scale);
   await page.evaluate(()=>document.documentElement.dataset.theme='dark');await page.setViewportSize({width:390,height:1000});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.locator('#passive-stability').screenshot({path:path.join(out,route+'-card-dark-mobile.png')});await page.setViewportSize({width:1400,height:1000});
  }
  assert.deepEqual(errors,[]);console.log('PASS: both live stability cards/JSON, explicit metadata badge fixtures, omitted integration defaults, preserved native_legacy warnings and profiles, catalog rate/damping/radius resets, dark/mobile.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
