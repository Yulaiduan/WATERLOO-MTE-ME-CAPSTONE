/** Verify the replacement upper-link/chassis spring and 2:1 wheel-leg guide and lever-to-suspension bridge.
 * Run: node scripts/verify_suspension_architecture_ui.cjs with Motion Lab on port 4186.
 * Inputs: live factory SI profile, live math/Pymunk APIs and browser interactions.
 * Outputs: ignored artifacts/suspension-architecture-ui JSON/PNG and assertions.
 * Native launch/status endpoints are mocked; no desktop windows are opened.
 * This checks routing, measured channels and profile preservation, not hardware validity.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const origin='http://127.0.0.1:4186';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1000},acceptDownloads:true}),errors=[],launches=[],wheelCalls=[];
  page.on('pageerror',cause=>errors.push(cause.message));
  page.on('request',request=>{if(request.method()==='POST'&&/\/api\/(pymunk\/simulate|math\/simulate|simulate)$/.test(request.url()))wheelCalls.push({url:request.url(),config:request.postDataJSON()});});
  await page.route(origin+'/api/native-gui**',route=>{
   const request=route.request(),parts=request.url().split('/');
   if(request.method()==='POST'&&!request.url().endsWith('/show')){launches.push(request.postDataJSON());return route.fulfill({status:202,contentType:'application/json',body:JSON.stringify({id:'suspension-test-'+launches.length,pid:7654321,status:'starting'})});}
   return route.fulfill({contentType:'application/json',body:JSON.stringify({id:parts.at(-1)==='show'?parts.at(-2):parts.at(-1),pid:7654321,status:'running',solver_steps:120,loops:0,window_shown:true})});
  });
  const factoryResponse=await page.request.get(origin+'/api/suspension-architecture/defaults');assert.ok(factoryResponse.ok(),'Architecture factory API must be running');
  const factoryValue=await factoryResponse.json(),factory=factoryValue.config||factoryValue;
  function architecture(config){assert.equal(config.spring_topology,'gravity_balance');assert.equal(config.spring_force_law,'zero_effective');assert.equal(config.aux_spring_enabled,false);assert.equal(config.damping,100);assert.equal(config.fixture,'floating');assert.equal(config.target,'position');assert.equal(config.radius,.2);assert.equal(config.chassis_shape_enabled,true);assert.equal(config.guide_pulleys_visible,true);assert.equal(config.guide_hip_radius,.028);}
  function nativePacket(packet,baseline=60){assert.equal(packet.model,'wheel_leg');architecture(packet.config);assert.equal(packet.guide_visualization.pretension_N,baseline);assert.equal(packet.guide_visualization.show_force_vectors,true);assert.equal(packet.config.guide_visualization,undefined);assert.equal(packet.config.T0_N,undefined);}
  architecture(factory);
  const out=path.join(__dirname,'../artifacts/suspension-architecture-ui');fs.mkdirSync(out,{recursive:true});
  await page.goto(origin+'/?tab=physics&architecture=constant-lift');
  const physics=page.frameLocator('iframe[data-key="physics"]');
  await physics.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  assert.equal(wheelCalls.length,1,'Cold architecture entry must not run generic defaults first');architecture(wheelCalls[0].config);
  assert.match(await page.locator('iframe[data-key="physics"]').getAttribute('src'),/loadOnly=1/);
  assert.equal(await physics.locator('[data-key="aux_spring_enabled"]').isChecked(),false);
  assert.equal(await physics.locator('[data-key="aux_rest_length"]').isDisabled(),true);
  assert.equal(await physics.locator('.js-plotly-plot').count(),12);
  assert.equal(await physics.locator('.auxiliary-spring-overlay').count(),0);assert.equal(await physics.locator('.chassis-body').count(),1);
  await physics.locator('.guide-belt-dot').first().waitFor();assert.equal(await physics.locator('.guide-belt-dot').count(),24);assert.equal(await physics.locator('.engine-guide-pulley').count(),2);
  await physics.locator('#equation-checks > summary').click();await physics.locator('#T0-newtons').fill('37');await physics.locator('#T0-newtons').dispatchEvent('input');
  await physics.locator('#guide-pretension-N').fill('60');await physics.locator('#guide-pretension-N').dispatchEvent('input');assert.equal(await physics.locator('#T0-newtons').inputValue(),'37');
  const download=page.waitForEvent('download');await physics.locator('#save-data').click();const file=await download;await file.saveAs(path.join(out,'physics-run.json'));
  const physical=JSON.parse(fs.readFileSync(path.join(out,'physics-run.json'),'utf8'));architecture(physical.config);assert.equal(physical.backend,'pymunk');
  const channels=['spring_elastic_tension','spring_damper_tension','spring_tension','spring_energy_J','spring_elastic_equivalent_lift_N','guide_tension_difference_N','guide_belt_speed_relative'];
  function verifyRun(run){
   assert.ok(run.rows.length>100);for(const key of channels)assert.ok(run.rows.every(row=>Number.isFinite(row[key])),key+' must remain finite');
   assert.ok(run.rows.every(row=>row.aux_spring_tension===0&&row.spring_lower_fx===0&&row.spring_lower_fy===0),'Replacement spring never loads the lower link directly');
   assert.ok(run.rows.some(row=>Math.abs(row.spring_damper_tension)>1e-3),'Damping belongs to the replacement unit');
   assert.ok(Math.max(...run.rows.map(row=>row.spring_elastic_equivalent_lift_N))-Math.min(...run.rows.map(row=>row.spring_elastic_equivalent_lift_N))<(run.backend==='math'?1e-7:.02),'Elastic gravity support is constant within the declared solver tolerance');
   for(const frame of run.frames){assert.equal(frame.auxiliary_spring_geometry,undefined);assert.equal(frame.spring_geometry.anchors.a.body,'hip');assert.equal(frame.spring_geometry.anchors.b.body,'upper');assert.deepEqual([...new Set(frame.spring_geometry.force_sites.map(site=>site.body))].sort(),['hip','upper']);assert.equal(frame.guide_pulleys.hip.radius,2*frame.guide_pulleys.knee.radius);}
   assert.equal(run.reference_inputs.T0_N,37);assert.equal(run.reference_inputs.guide_visualization.pretension_N,60);assert.equal(run.reference_inputs.guide_visualization.applied_to_solver,false);
  }
  verifyRun(physical);assert.equal(physical.frames[0].debug_draw.filter(shape=>['circle','segment','capsule','polygon'].includes(shape.kind||shape.type)).length,6,'Actual engine model includes chassis and two guide drums');
  await page.locator('#show-gui').click();await page.waitForFunction(()=>document.querySelector('#native-status').dataset.state==='running');nativePacket(launches.at(-1));
  const nativeCount=launches.length,show=page.waitForResponse(response=>response.url().endsWith('/show'));await page.locator('#show-gui').click();assert.ok((await show).ok());assert.equal(launches.length,nativeCount,'Same profile restores its owned desktop window');
  // A changed guide assumption gets a separate native cache key while the solver config stays fixed.
  await physics.locator('#guide-pretension-N').fill('70');await physics.locator('#guide-pretension-N').dispatchEvent('input');
  const changedLaunch=page.waitForResponse(response=>response.url().endsWith('/api/native-gui')&&response.request().method()==='POST');await page.locator('#show-gui').click();assert.equal((await changedLaunch).status(),202);nativePacket(launches.at(-1),70);
  // The saved record restores its independent viewer assumptions, including browser playback.
  await page.waitForFunction(()=>document.querySelectorAll('.data-record').length>=2);
  await page.locator('[data-tab="data"]').click();await page.locator('.data-record').filter({hasText:'pymunk'}).first().click();
  const savedLaunch=page.waitForResponse(response=>response.url().endsWith('/api/native-gui')&&response.request().method()==='POST');await page.locator('#data-panel').getByRole('button',{name:'Show Pymunk desktop GUI',exact:true}).click();assert.equal((await savedLaunch).status(),202);nativePacket(launches.at(-1));
  await page.locator('#data-panel').getByRole('button',{name:'Recorded browser playback',exact:true}).click();const viewer=page.frameLocator('iframe[data-key="gui"]');await viewer.locator('.guide-belt-dot').first().waitFor({timeout:30000});assert.match(await viewer.locator('.guide-force-label').textContent(),/60/);await page.locator('#close-gui').click();
  await page.getByRole('button',{name:'Load 2D physics profile',exact:true}).click();
  assert.equal(await physics.locator('#guide-pretension-N').inputValue(),'60');assert.equal(await physics.locator('#T0-newtons').inputValue(),'37');
  assert.equal(await physics.locator('[data-key="aux_spring_enabled"]').isChecked(),false);
  await page.locator('[data-tab="math"]').click();
  const math=page.frameLocator('iframe[data-key="math"]');await math.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  await math.locator('#profile-import').setInputFiles(path.join(out,'physics-run.json'));await math.locator('#status').filter({hasText:'Profile loaded'}).waitFor();assert.equal(await math.locator('[data-key="aux_spring_enabled"]').isChecked(),false);
  await math.locator('#run').click();await math.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  const mathDownload=page.waitForEvent('download');await math.locator('#save-data').click();const mathFile=await mathDownload;await mathFile.saveAs(path.join(out,'math-run.json'));
  const mathematical=JSON.parse(fs.readFileSync(path.join(out,'math-run.json'),'utf8'));architecture(mathematical.config);verifyRun(mathematical);assert.equal(mathematical.backend,'math');
  await page.locator('#show-gui').click();await page.waitForFunction(()=>document.querySelector('#native-status').dataset.state==='running');nativePacket(launches.at(-1));
  await page.locator('[data-math-model="counterbalance"]').click();const lever=page.frameLocator('iframe[data-key="counterbalance"]');await lever.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  const beforeBridge=wheelCalls.length,bridgeResponse=page.waitForResponse(response=>response.request().method()==='POST'&&response.url().endsWith('/api/simulate'));await lever.locator('#architecture').click();assert.ok((await bridgeResponse).ok());await physics.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  await page.waitForFunction(()=>document.querySelector('[data-tab="physics"]').getAttribute('aria-current')==='page');assert.equal(wheelCalls.length,beforeBridge+1);architecture(wheelCalls.at(-1).config);
  await page.locator('#theme-toggle').click();await page.setViewportSize({width:390,height:1000});await page.waitForTimeout(150);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:path.join(out,'suspension-dark-mobile.png'),fullPage:true});assert.deepEqual(errors,[]);
  // A standalone lever uses the same durable root route instead of wheel API calls itself.
  await page.goto(origin+'/counterbalance/?loadOnly=1');await page.locator('#architecture').waitFor();await page.locator('#architecture').click();await page.waitForURL(/architecture=constant-lift/);await page.frameLocator('iframe[data-key="physics"]').locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});architecture(wheelCalls.at(-1).config);
  console.log('PASS: cold factory route without generic run, one replacement upper/chassis coil with damping, six actual shapes and 2:1 belt marks, neutral constant support, independent guide/T0 JSON/library/playback preservation, model-specific native view envelope and owned-window restore, embedded/standalone lever bridge, Plotly and mobile theme.');
 }finally{await browser.close();}
})().catch(cause=>{console.error(cause);process.exitCode=1;});
