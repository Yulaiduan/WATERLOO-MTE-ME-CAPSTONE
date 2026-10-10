/** Verify the standalone lever and unified profiles/native routing in Edge.
 * Run: node scripts/verify_counterbalance_ui.cjs with Motion Lab ready on port 4186.
 * Inputs: illustrative SI lever profiles and live math/Pymunk APIs. Output: ignored QA JSON/PNG.
 * Native launch/status is mocked: no desktop windows are opened; actual GUI is tested separately.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1000},acceptDownloads:true}),errors=[],launches=[],wheelCalls=[];
  page.on('pageerror',cause=>errors.push(cause.message));
  page.on('request',request=>{if(request.method()==='POST'&&/\/api\/(pymunk\/simulate|math\/simulate|simulate)$/.test(request.url()))wheelCalls.push(request.url());});
  await page.route('http://127.0.0.1:4186/api/native-gui**',route=>{
   const request=route.request(),parts=request.url().split('/');
   if(request.method()==='POST'&&!request.url().endsWith('/show')){launches.push(request.postDataJSON());return route.fulfill({status:202,contentType:'application/json',body:JSON.stringify({id:'lever-test-'+launches.length,pid:7654321,status:'starting'})});}
   const id=parts.at(-1)==='show'?parts.at(-2):parts.at(-1);
   return route.fulfill({contentType:'application/json',body:JSON.stringify({id,pid:7654321,status:'running',solver_steps:120,loops:0,window_shown:true})});
  });
  const out=path.join(__dirname,'../artifacts/counterbalance-ui');fs.mkdirSync(out,{recursive:true});
  await page.goto('http://127.0.0.1:4186/?tab=math&model=counterbalance');
  const tool=page.frameLocator('iframe[data-key="counterbalance"]');
  await tool.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  assert.ok(await tool.locator('.js-plotly-plot').count()>=11);
  const staticValues=await tool.locator('#lift-angle .lever-chart').evaluate(node=>node.data.map(trace=>trace.y.filter(Number.isFinite)));
  assert.ok(Math.max(...staticValues[0])-Math.min(...staticValues[0])<1e-10);
  assert.ok(Math.max(...staticValues[1])-Math.min(...staticValues[1])>1);
  const tension=await tool.locator('#tension-angle .lever-chart').evaluate(node=>node.data[0].y);assert.ok(Math.max(...tension)-Math.min(...tension)>10);
  await tool.locator('#c-physical_free_length').fill('250');await tool.locator('#c-physical_free_length').dispatchEvent('change');
  await tool.locator('#run').click();await tool.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  const jsonDownload=page.waitForEvent('download');await tool.locator('#save-run').click();const downloaded=await jsonDownload;await downloaded.saveAs(path.join(out,'math-run.json'));
  const math=JSON.parse(fs.readFileSync(path.join(out,'math-run.json'),'utf8'));assert.equal(math.backend,'counterbalance_math');assert.equal(math.config.physical_free_length,.25);
  assert.ok(math.result.rows.every(row=>Math.abs(row.coil_length_m-row.span_m-.25)<1e-12));
  assert.ok(Math.max(...math.result.rows.map(row=>row.equivalent_support_N))-Math.min(...math.result.rows.map(row=>row.equivalent_support_N))<1e-9);
  await tool.locator('#c-law').selectOption('ordinary');await tool.locator('#compare').click();await tool.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  assert.equal(await tool.locator('#comparison-time .lever-chart').evaluate(node=>node.data.length),2);
  await tool.locator('#backend').selectOption('counterbalance_pymunk');
  const physicalDownload=page.waitForEvent('download');await tool.locator('#save-run').click();const physicalFile=await physicalDownload;await physicalFile.saveAs(path.join(out,'pymunk-run.json'));
  const physical=JSON.parse(fs.readFileSync(path.join(out,'pymunk-run.json'),'utf8'));assert.equal(physical.backend,'counterbalance_pymunk');assert.ok(physical.result.frames[0].debug_draw.length);
  assert.ok(physical.result.rows.every(row=>Number.isFinite(row.joint_force_N)&&Number.isFinite(row.driver_torque_Nm)));
  await tool.locator('#native').click();await page.waitForFunction(()=>document.querySelector('#native-status').dataset.state==='running');
  assert.equal(launches.length,1);assert.equal(launches[0].model,'counterbalance');assert.equal(launches[0].config.law,'ordinary');assert.equal(launches[0].config.length,.4);
  await page.locator('#show-playback').click();assert.equal(await page.locator('#gui-dialog').evaluate(node=>node.open),false);
  await tool.locator('#c-law').selectOption('zero_effective');await tool.locator('#c-mode').selectOption('free');await tool.locator('#backend').selectOption('counterbalance_math');
  // Selecting an existing recording intentionally restores its saved inputs; apply the free setup afterwards.
  await tool.locator('#c-law').selectOption('zero_effective');await tool.locator('#c-mode').selectOption('free');
  await tool.locator('#run').click();await tool.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  const freeDownload=page.waitForEvent('download');await tool.locator('#save-run').click();const freeFile=await freeDownload;await freeFile.saveAs(path.join(out,'free-run.json'));
  const free=JSON.parse(fs.readFileSync(path.join(out,'free-run.json'),'utf8'));assert.equal(free.config.mode,'free');assert.ok(free.result.rows.every(row=>Math.abs(row.driver_torque_Nm)<1e-12));assert.ok(free.result.rows.every(row=>Math.abs(row.theta_deg-30)<1e-6));
  await page.locator('[data-tab="data"]').click();await page.locator('.data-record').filter({hasText:'counterbalance_pymunk'}).first().click();
  await page.getByRole('button',{name:'View lever recording in tool',exact:true}).click();
  await tool.locator('#backend').filter({hasText:'2D Pymunk'}).waitFor();assert.equal(await tool.locator('#backend').inputValue(),'counterbalance_pymunk');
  await page.locator('[data-tab="data"]').click();await page.getByRole('button',{name:'Load counterbalance lever profile',exact:true}).click();
  await tool.locator('#status').filter({hasText:'Lever profile loaded'}).waitFor();assert.equal(await tool.locator('#play').isEnabled(),false);
  await page.locator('#theme-toggle').click();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
  await page.setViewportSize({width:390,height:1000});await page.waitForTimeout(200);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await tool.locator('#lift-angle .lever-chart').evaluate(node=>window.Plotly.relayout(node,{'xaxis.range':[10,55]}));
  assert.deepEqual(await tool.locator('#lift-angle .lever-chart').evaluate(node=>node._fullLayout.xaxis.range),[10,55]);
  await page.screenshot({path:path.join(out,'lever-dark-mobile.png'),fullPage:true});
  assert.deepEqual(wheelCalls,[]);assert.deepEqual(errors,[]);
  console.log('PASS: flat equivalent lift vs changing spring tension, ordinary comparison, physical coil free length, live math/Pymunk, free balance, JSON/library/load, lever playback/native envelope, Plotly zoom/theme and mobile.');
 }finally{await browser.close();}
})().catch(cause=>{console.error(cause);process.exitCode=1;});
