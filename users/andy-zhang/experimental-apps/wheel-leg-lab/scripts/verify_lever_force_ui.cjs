/** Verify real single-link end-force interaction and replay in the browser.
 * Run: node scripts/verify_lever_force_ui.cjs with Motion Lab ready on port4186.
 * Inputs: local SciPy/Pymunk APIs, press/hold pointer events, SI JSON profiles.
 * Outputs: ignored run/screenshot evidence; confirms neutral release, explicit
 * rest placement, opposite force, tab-deactivation safety, units and equations.
 * Desktop native launches and hardware suspension behavior are outside scope.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1000},acceptDownloads:true}),errors=[];
  page.on('pageerror',cause=>errors.push(cause.message));
  const out=path.join(__dirname,'../artifacts/lever-force-ui');fs.mkdirSync(out,{recursive:true});
  await page.goto('http://127.0.0.1:4186/counterbalance/?loadOnly');
  await page.locator('#c-mode').waitFor();
  assert.equal(await page.locator('#c-mode').inputValue(),'free');assert.equal(await page.locator('#c-damping').inputValue(),'0');
  assert.match(await page.locator('.formula').textContent(),/θ̈/);
  assert.match(await page.locator('.formula').textContent(),/F.*L cos θ/);
  await page.locator('#c-initial_angle_deg').fill('45');await page.locator('#c-initial_angle_deg').dispatchEvent('change');
  await page.locator('#place-rest').click();assert.match(await page.locator('#live-status').textContent(),/Placed at θ 45/);
  await page.locator('#live-force-kgf').fill('0.20394324');await page.locator('#live-force-kgf').dispatchEvent('change');
  assert.ok(Math.abs(Number(await page.locator('#live-force-N').inputValue())-2)<1e-4);
  async function hold(id){await page.locator('#'+id).scrollIntoViewIfNeeded();const box=await page.locator('#'+id).boundingBox();await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();}
  async function waitForce(sign){await page.waitForFunction(sign=>{const json=document.querySelector('#diagnostics').textContent;if(!json)return false;const p=JSON.parse(json);return (p.config.force_history||[]).some(v=>Math.sign(v.force_N)===sign)&&p.config.duration>.3;},sign,{timeout:15000});}
  await hold('force-up');await waitForce(1);await page.mouse.up();
  await page.waitForFunction(()=>{const json=document.querySelector('#diagnostics').textContent;if(!json)return false;const p=JSON.parse(json);return p.config.duration>.7&&p.config.force_history.at(-1).force_N===0;},{timeout:15000});
  await page.locator('#live-toggle').click();assert.match(await page.locator('#live-status').textContent(),/velocity.*retained/);
  const downloadPromise=page.waitForEvent('download');await page.locator('#save-run').click();const download=await downloadPromise;await download.saveAs(path.join(out,'live-up-release.json'));
  const packet=JSON.parse(fs.readFileSync(path.join(out,'live-up-release.json'),'utf8')),run=packet.result;
  assert.equal(packet.backend,'counterbalance_math');assert.equal(run.config.mode,'force');assert.equal(run.config.damping,0);
  assert.ok(run.config.force_history.some(v=>v.force_N>0));assert.equal(run.config.force_history.at(-1).force_N,0);
  assert.ok(run.rows.every(row=>row.driver_torque_Nm===0&&row.dissipation_W===0));
  const lastPositive=run.rows.findLast(row=>row.end_force_N>0),released=run.rows.filter(row=>row.t>lastPositive.t+.002);
  assert.ok(released.length>100);assert.ok(released[0].angular_velocity_rad_s>.1);
  assert.ok(Math.max(...released.map(row=>row.angular_velocity_rad_s))-Math.min(...released.map(row=>row.angular_velocity_rad_s))<1e-8);
  assert.ok(released.at(-1).theta_deg>released[0].theta_deg+.1);
  const replayResponse=await page.request.post('http://127.0.0.1:4186/api/counterbalance/math',{data:run.config});assert.equal(replayResponse.status(),200);const replay=await replayResponse.json();
  assert.ok(Math.abs(replay.rows.at(-1).theta_deg-run.rows.at(-1).theta_deg)<2e-5);
  assert.ok(Math.abs(replay.rows.at(-1).angular_velocity_rad_s-run.rows.at(-1).angular_velocity_rad_s)<1e-6);
  // Leaving the tab pauses the solver without changing its saved velocity.
  await page.locator('#live-toggle').click();await page.waitForTimeout(160);await page.evaluate(()=>window.postMessage({type:'motion-lab-deactivate'},location.origin));
  await page.locator('#live-status').filter({hasText:'inactive'}).waitFor();
  const beforePause=JSON.parse(await page.locator('#diagnostics').textContent()).config.duration;
  await page.waitForTimeout(220);assert.equal(JSON.parse(await page.locator('#diagnostics').textContent()).config.duration,beforePause);
  await page.locator('#place-rest').click();await page.locator('#c-initial_angle_deg').fill('40');await page.locator('#c-initial_angle_deg').dispatchEvent('change');await page.locator('#place-rest').click();
  await hold('force-down');await waitForce(-1);await page.mouse.up();await page.waitForTimeout(250);await page.locator('#live-toggle').click();
  const downDownload=page.waitForEvent('download');await page.locator('#save-run').click();const downFile=await downDownload;await downFile.saveAs(path.join(out,'live-down-release.json'));
  const down=JSON.parse(fs.readFileSync(path.join(out,'live-down-release.json'),'utf8')).result;assert.ok(down.rows.some(row=>row.end_force_N<0));assert.ok(down.rows.at(-1).theta_deg<40);assert.ok(down.rows.at(-1).angular_velocity_rad_s<0);
  // Blur releases a held pointer load without adding a brake/controller.
  await page.locator('#place-rest').click();await hold('force-up');await waitForce(1);await page.evaluate(()=>window.dispatchEvent(new Event('blur')));await page.mouse.up();
  await page.waitForFunction(()=>{const p=JSON.parse(document.querySelector('#diagnostics').textContent);return p.config.force_history.at(-1).force_N===0;});await page.locator('#live-toggle').click();
  // Recorded force pulse works with the actual rigid-body backend as well.
  await page.locator('#place-rest').click();await page.locator('#c-mode').selectOption('force');await page.locator('#c-wave').selectOption('pulse');
  await page.locator('#controls summary').filter({hasText:'Integration'}).click();
  for(const [id,value] of [['c-start','0.1'],['c-rise','50'],['c-fall','50'],['c-pulse_width','300'],['c-duration','1']]){await page.locator('#'+id).fill(value);await page.locator('#'+id).dispatchEvent('change');}
  await page.locator('#backend').selectOption('counterbalance_pymunk');
  // Backend selection restores an existing saved run; explicitly set the desired scheduled input afterwards.
  await page.locator('#c-mode').selectOption('force');await page.locator('#c-wave').selectOption('pulse');await page.locator('#clear-force-history').click();
  await page.locator('#run').click();await page.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  const diagnostic=JSON.parse(await page.locator('#diagnostics').textContent());assert.equal(diagnostic.model.constraints.length,1);assert.equal(diagnostic.model.constraints[0].class,'PivotJoint');assert.equal(diagnostic.config.damping,0);
  assert.ok(await page.locator('.js-plotly-plot').count()>=14);assert.equal(await page.locator('#end-force-time .lever-chart').evaluate(node=>node.data[0].name),'Applied force at C · upward positive');
  await page.locator('#theme').click();await page.setViewportSize({width:390,height:1000});await page.waitForTimeout(200);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:path.join(out,'force-pulse-dark-mobile.png'),fullPage:true});assert.deepEqual(errors,[]);
  // The single Misc iframe pauses live solving when its host navigation hides it.
  await page.setViewportSize({width:1400,height:1000});await page.goto('http://127.0.0.1:4186/?tab=studies&study=counterbalance');
  const tool=page.frameLocator('iframe[data-key="counterbalance"]');await tool.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  assert.equal(await tool.locator('#c-mode').inputValue(),'free');await tool.locator('#live-toggle').click();
  await tool.locator('#status').filter({hasText:'Live 0.30'}).waitFor({timeout:15000});
  await page.locator('[data-tab="data"]').click();await page.waitForTimeout(180);
  const savedTime=await tool.locator('#diagnostics').textContent();await page.waitForTimeout(220);assert.equal(await tool.locator('#diagnostics').textContent(),savedTime);
  await page.locator('[data-tab="studies"]').click();assert.match(await tool.locator('#live-status').textContent(),/inactive/);
  assert.match(await tool.locator('#live-toggle').textContent(),/Resume/);
  assert.equal(await page.locator('iframe[data-key="counterbalance"]').count(),1);assert.deepEqual(errors,[]);
  console.log('PASS: default neutral free link, N/kgf, real up/down force, coast after release, portable history replay, inactive/blur release, explicit rest reset, equations, Plotly and actual Pymunk point load.');
 }finally{await browser.close();}
})().catch(cause=>{console.error(cause);process.exitCode=1;});
