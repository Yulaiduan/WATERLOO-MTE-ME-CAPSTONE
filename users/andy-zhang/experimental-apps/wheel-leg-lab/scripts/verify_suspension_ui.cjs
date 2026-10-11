// Verify real preset controls/solver drawings/JSON. Run: node scripts/verify_suspension_ui.cjs.
// Inputs: loopback 4186 and SI demo dimensions. Output: ignored browser screenshots.
// Uses Playwright/Edge and real backends; native launch is covered separately.
const {chromium}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true}),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  const presetData=await (await page.request.get('http://127.0.0.1:4186/api/spring-presets')).json(),presets=Object.keys(presetData.catalog);
  for(const route of ['physics','mathematical']){
   await page.goto(`http://127.0.0.1:4186/${route}/?loadOnly=1`);
   await page.locator('[data-key="spring_topology"]').waitFor();
   for(const name of presets){
    await page.locator('[data-key="spring_topology"]').selectOption(name);
    const expected={...presetData.defaults,...presetData.catalog[name].defaults};
    for(const [key,scale] of [['spring_pulley_radius',1000],['spring_bellcrank_radius',1000],['stiffness',1],['damping',1]])assert.ok(Math.abs(Number(await page.locator(`[data-key="${key}"]`).inputValue())-expected[key]*scale)<1e-9,`${name}: catalog ${key} must reset`);
    const set=async(key,value)=>{await page.locator(`[data-key="${key}"]`).evaluate(n=>n.closest('details').open=true);await page.locator(`[data-key="${key}"]`).fill(String(value));await page.locator(`[data-key="${key}"]`).dispatchEvent('change');};
    await set('duration',1.2);await set('start',.3);await set('position_amplitude',8);
    const responsePromise=page.waitForResponse(r=>r.url().includes('/simulate'));
    await page.locator('#run').click();const response=await responsePromise;const result=await response.json();
    assert.equal(response.status(),200,JSON.stringify(result));assert.equal(result.config.spring_topology,name);
    await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('Recorded'));
    assert.equal(result.config.spring_integration,'point_force');
    assert.equal(await page.locator('#passive-stability').getAttribute('data-classification'),result.passive_stability.classification);
    assert.ok((await page.locator('#stability-balance').textContent()).includes('kgf'));
    assert.equal(await page.locator('.js-plotly-plot').count(),name==='gravity_balance'?12:11);
    if(name==='gravity_balance'){
     assert.equal(result.config.spring_force_law,'zero_effective');
     assert.ok(Math.abs(result.config.stiffness-2260.043672222222)<1e-6);
     assert.equal(await page.locator('[data-key="stiffness"]').isDisabled(),true);
     assert.ok(result.rows.every(r=>Math.abs(r.spring_elastic_equivalent_lift_N-84.7516377083333)<.01));
    }
    assert.equal(result.config.radius,.2);assert.ok(result.rows.every(r=>Number.isFinite(r.spring_coil_load)));
    if(name!=='legacy_tip')assert.ok(await page.locator('.spring-mechanism-overlay').count()>0);
    if(name==='knee_capture'){
     assert.equal(await page.locator('[data-key="spring_mode"]').inputValue(),'compression');
     assert.equal(await page.locator('[data-key="spring_transmission"]').inputValue(),'pullrod');
     assert.ok(result.frames[0].spring_geometry.force_sites.length===2);
     await page.locator('#time').evaluate(n=>{n.value=.8;n.dispatchEvent(new Event('input',{bubbles:true}));});
     const downloadPromise=page.waitForEvent('download');await page.locator('#profile').click();
     const download=await downloadPromise,out=path.join(__dirname,'../artifacts/preset-profile-'+route+'.json');
     fs.mkdirSync(path.dirname(out),{recursive:true});await download.saveAs(out);
     assert.equal(JSON.parse(fs.readFileSync(out)).config.spring_transmission,'pullrod');
     await page.screenshot({path:path.join(__dirname,'../artifacts/suspension-'+route+'.png'),fullPage:true});
    }
   }
   await page.setViewportSize({width:390,height:1000});
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.setViewportSize({width:1440,height:1100});
  }
  assert.deepEqual(errors,[]);console.log('PASS: all9 presets on both actual backends, calibrated constant lift, editable demo resets, Plotly charts, geometry, coil outputs, JSON profiles and mobile.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
