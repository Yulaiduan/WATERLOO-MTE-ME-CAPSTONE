// Unified motion-lab integration. Run: node scripts/verify_motion_lab.cjs.
// Inputs: local SciPy/Pymunk APIs, saved SI profiles; output: ignored QA files.
// Requires Playwright/Edge. Native launch/status endpoints are mocked to avoid opening windows;
// the actual live desktop API is verified separately with owned-PID cleanup.
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true}),errors=[],external=[],nativeLaunches=[];
  let nativeSteps=0,nativeFailure=false;
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',r=>{if(r.request().url().startsWith('http://127.0.0.1:4186/'))return r.continue();external.push(r.request().url());return r.abort();});
  await page.route('http://127.0.0.1:4186/api/native-gui**',r=>{
   if(r.request().method()==='POST'&&!r.request().url().endsWith('/show')){
    nativeLaunches.push(r.request().postDataJSON());
    return r.fulfill({status:202,contentType:'application/json',body:JSON.stringify({id:'browser-test-'+nativeLaunches.length,pid:7654321,status:'starting',mode:'native-live'})});
   }
   nativeSteps+=120;
   const parts=r.request().url().split('/'),id=parts.at(-1)==='show'?parts.at(-2):parts.at(-1);
   return r.fulfill({contentType:'application/json',body:JSON.stringify({id,pid:7654321,status:nativeFailure?'failed':'running',solver_steps:nativeSteps,loops:0,paused:false,window_shown:true,...(nativeFailure?{error:'Fixture native startup failure'}:{})})});
  });
  await page.goto('http://127.0.0.1:4186/');await page.locator('#motion-lab').waitFor();
  assert.equal(await page.locator('[data-open]').count(),4);
  await page.locator('#show-gui').click();
  await page.waitForFunction(()=>document.querySelector('#native-status').dataset.state==='running');
  assert.equal(nativeLaunches.length,1);assert.equal(nativeLaunches[0].target,'position');
  assert.equal(await page.locator('#gui-dialog').evaluate(n=>n.open),false);
  assert.match(await page.locator('#native-status').innerText(),/simulation host.*live solver steps/);
  const showResponse=page.waitForResponse(r=>r.url().endsWith('/show'));
  await page.locator('#show-gui').click();assert.equal((await showResponse).status(),200);
  assert.equal(nativeLaunches.length,1);
  await page.locator('#show-playback').click();
  const viewer=page.frameLocator('iframe[data-key="gui"]');await viewer.locator('.engine-shape').first().waitFor({timeout:30000});
  assert.equal(await viewer.locator('.engine-shape').count(),3);
  assert.equal(await viewer.locator('.js-plotly-plot').count(),0);
  await viewer.locator('#time').evaluate(n=>{n.value=.8;n.dispatchEvent(new Event('input',{bubbles:true}));});
  assert.equal(await viewer.locator('.disturbance-arrow').getAttribute('data-kind'),'position');
  await page.locator('#close-gui').click();
  await page.locator('[data-tab="math"]').click();
  const math=page.frameLocator('iframe[data-key="math"]');await math.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  assert.ok(await math.locator('.js-plotly-plot').count()>=8);
  assert.equal(await math.locator('.engine-shape').count(),0);
  await math.locator('[data-key="length"]').fill('250');await math.locator('[data-key="length"]').dispatchEvent('change');
  await page.locator('#profile-name').fill('Integration profile');
  const downloadPromise=page.waitForEvent('download');await page.locator('#save-profile').click();const downloaded=await downloadPromise;
  const out=path.join(__dirname,'../artifacts/motion-lab');fs.mkdirSync(out,{recursive:true});await downloaded.saveAs(path.join(out,'profile.json'));
  const profile=JSON.parse(fs.readFileSync(path.join(out,'profile.json'),'utf8'));assert.equal(profile.backend,'math');assert.equal(profile.config.length,.25);
  await page.waitForFunction(()=>document.querySelector('#lab-status').textContent.includes('Saved profile'));
  await page.locator('#compare-models').click();await page.waitForFunction(()=>document.querySelector('#lab-status').textContent.includes('Both runs saved'),null,{timeout:45000});
  assert.equal(await page.locator('#comparison-plot').evaluate(n=>n.data.length),3);
  assert.equal(await math.locator('#status').evaluate(n=>/NaN|undefined/.test(n.textContent)),false);
  await math.locator('.chart').first().evaluate(n=>window.Plotly.relayout(n,{'xaxis.range':[.8,1.4]}));
  await page.locator('#theme-toggle').click();await page.waitForTimeout(250);
  assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
  assert.deepEqual(await math.locator('.chart').first().evaluate(n=>n._fullLayout.xaxis.range),[.8,1.4]);
  await page.locator('#show-playback').click();await viewer.locator('.engine-shape').first().waitFor();assert.equal(await viewer.locator('.engine-shape').count(),3);await page.locator('#close-gui').click();
  await page.locator('[data-math-model="linkage"]').click();
  const linkage=page.frameLocator('iframe[data-key="linkage"]');await linkage.locator('.js-plotly-plot').first().waitFor();assert.equal(await linkage.locator('.js-plotly-plot').count(),4);
  await page.locator('[data-math-model="scipy"]').click();
  await page.locator('[data-tab="data"]').click();await page.locator('.data-record').first().waitFor();
  const savedCount=await page.locator('.data-record').count();assert.ok(savedCount>=4);
  await page.locator('.data-record').filter({hasText:'Integration profile'}).first().click();
  await page.locator('.data-chart.js-plotly-plot').waitFor();
  const runDownload=page.waitForEvent('download');await page.getByRole('button',{name:'Download JSON',exact:true}).click();const runFile=await runDownload;await runFile.saveAs(path.join(out,'run.json'));
  const run=JSON.parse(fs.readFileSync(path.join(out,'run.json'),'utf8'));assert.equal(run.kind,'run');assert.ok(run.result.rows.length>1000);
  await page.locator('#data-panel').getByRole('button',{name:'Show Pymunk desktop GUI',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('#native-status').dataset.session==='browser-test-2');
  assert.equal(nativeLaunches.length,2);assert.equal(nativeLaunches[1].length,.25);
  nativeFailure=true;await page.locator('#lab-error').waitFor({state:'visible'});assert.match(await page.locator('#lab-error').innerText(),/Fixture native startup failure/);nativeFailure=false;
  await page.getByRole('button',{name:/Load .* profile/}).click();
  assert.equal(await page.locator('[data-panel="math"]').isVisible(),false);assert.equal(await page.locator('[data-panel="physics"]').isVisible(),true);
  const physics=page.frameLocator('iframe[data-key="physics"]');await physics.locator('[data-key="length"]').waitFor();
  await physics.locator('[data-key="length"][value="250"]').waitFor();assert.equal(await physics.locator('[data-key="length"]').inputValue(),'250');
  await page.locator('[data-tab="data"]').click();
  await page.getByLabel('Import profile or recorded run JSON').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from('{"config":{"length":-1,"radius":0.2,"target":"position"}}')});
  await page.locator('#data-panel [role="alert"]').waitFor({state:'visible'});
  await page.locator('[data-tab="studies"]').click();await page.locator('#study-select').selectOption('paths');
  const study=page.frameLocator('iframe[data-key="studies"]');await study.locator('.family-chart.js-plotly-plot').first().waitFor();
  assert.equal(await study.locator('.js-plotly-plot').count(),6);
  const studyDownload=page.waitForEvent('download');await page.locator('#save-study-data').click();const studyFile=await studyDownload;await studyFile.saveAs(path.join(out,'study-data.json'));
  const studyData=JSON.parse(fs.readFileSync(path.join(out,'study-data.json'),'utf8'));assert.equal(studyData.schema,'motion-lab-study/v1');assert.equal(studyData.study_settings.id,'paths');assert.ok(studyData.rows.length>100);
  await page.locator('[data-tab="data"]').click();await page.locator('.data-record').filter({hasText:'Mathematical path family'}).first().click();
  await page.getByRole('button',{name:'Restore motion study settings'}).click();await study.locator('.js-plotly-plot').first().waitFor();
  await page.setViewportSize({width:390,height:1000});await page.waitForTimeout(150);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('[data-tab="home"]').click();await page.screenshot({path:path.join(out,'menu-dark-mobile.png'),fullPage:true});
  await page.reload();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
  await page.locator('[data-tab="data"]').click();await page.locator('.data-record').first().waitFor();assert.ok(await page.locator('.data-record').count()>=savedCount);
  assert.match(await page.locator('a[download]').innerText(),/legacy-tip/);
  const matlab=await page.request.get('http://127.0.0.1:4186/math/wheel_leg_ode45.m');assert.equal(matlab.status(),200);assert.ok((await matlab.text()).includes('ode45'));
  await page.evaluate(config=>sessionStorage.setItem('motion-lab-gui-profile',JSON.stringify(config)),run.config);
  const launchesBeforeQuery=nativeLaunches.length;await page.goto('http://127.0.0.1:4186/?gui=1');
  await page.waitForFunction(()=>document.querySelector('#native-status').dataset.state==='running');
  assert.equal(nativeLaunches.length,launchesBeforeQuery+1);assert.equal(nativeLaunches.at(-1).length,.25);
  assert.equal(await page.locator('#gui-dialog').evaluate(n=>n.open),false);
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log('PASS: unified menu, live solver APIs, independent comparison, recorded browser playback, mocked native launch/profile/status/failure, Plotly zoom/dark mode, JSON/library/import/load/reload, misc plots and mobile.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
