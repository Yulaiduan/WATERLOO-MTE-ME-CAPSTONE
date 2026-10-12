/** Exercise invertible design geometry, torque-driven ground flips and library.
 * Run node scripts/verify_inversion_ui.cjs with Motion Lab at4186.
 * SI profiles, real solver APIs; ignored PNG/JSON evidence. Native API mocked
 * here; actual desktop renderer is tested separately. No hardware/3D claim.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1450,height:1100},acceptDownloads:true}),errors=[],origin='http://127.0.0.1:4186',out=path.join(__dirname,'../artifacts/inversion-ui');fs.mkdirSync(out,{recursive:true});page.on('pageerror',e=>errors.push(e.message));
  const launches=[];await page.route(origin+'/api/native-gui**',route=>{if(route.request().method()==='POST'){launches.push(route.request().postDataJSON());return route.fulfill({status:202,contentType:'application/json',body:JSON.stringify({id:'inversion-test',pid:12345,status:'starting',message:'Native launched'})});}return route.fulfill({contentType:'application/json',body:JSON.stringify({id:'inversion-test',pid:12345,status:'running',solver_steps:100})});});
  await page.goto(origin+'/inversion/?backend=pymunk');await page.locator('#mechanism[data-mode="setup"]').waitFor();
  const defaults=await(await page.request.get(origin+'/api/inversion/defaults')).json();
  await page.addInitScript(c=>{if(sessionStorage.getItem('inversion-migration-seeded'))return;sessionStorage.setItem('inversion-migration-seeded','1');delete c.rope_neutral_pose;c.preload=.01;c.rod_length=.12;c.upper_mass=.7;sessionStorage.setItem('motion-lab-inversion/v1:inversion_pymunk',JSON.stringify({config:c}));},defaults.default);
  await page.reload();await page.locator('#mechanism[data-mode="setup"]').waitFor();assert.equal(await page.locator('[data-key="upper_mass"]').inputValue(),'0.7');assert.equal(await page.locator('[data-key="rod_length"]').inputValue(),'130');
  assert.equal(await page.locator('.routing-pulley-red').count(),1);assert.equal(await page.locator('.routing-pulley-blue').count(),1);assert.equal(await page.locator('.knee-spring-pulley').count(),1);assert.equal(await page.locator('.parallel-feed').count(),2);
  assert.equal(await page.locator('[data-key="attachment_offset_deg"]').inputValue(),'5');assert.equal(await page.locator('#readouts').textContent(),'');assert.equal(await page.locator('[data-key="roller_gap"]').inputValue(),'0.2');assert.equal(await page.locator('[data-key="initial_angle_deg"]').inputValue(),'45');assert.equal(await page.locator('#mechanism .angle-limits').count(),1);
  assert.equal(await page.locator('#mechanism').getAttribute('data-rope-routing'),'central_wrap');
  assert.equal(await page.locator('#cap-detail').getAttribute('data-rope-routing'),'central_wrap');
  assert.equal(await page.locator('#cap-detail .detail-roller-red').count(),1);assert.equal(await page.locator('#cap-detail .detail-roller-blue').count(),1);
  const feeds=await page.locator('#mechanism .central-feed').evaluateAll(nodes=>nodes.map(n=>Number(n.dataset.eyeOffsetM)));assert.deepEqual(feeds,[.00002,-.00002]);
  const arcs=await page.locator('#mechanism .roller-arc').evaluateAll(nodes=>nodes.map(n=>[Number(n.dataset.centerX),Number(n.dataset.centerY)]));assert.ok(arcs.every(([x,y])=>x!==0||y!==0));
  assert.equal(await page.locator('[data-key="rope_neutral_pose"]').inputValue(),'folded');assert.equal(await page.locator('[data-key="preload"]').inputValue(),'0');
  await page.locator('[data-key="fixture"]').selectOption('hip_fixed');
  await page.locator('[data-key="initial_angle_deg"]').fill('0');
  const neutralResponse=page.waitForResponse(r=>r.url().endsWith('/api/inversion/preview')&&r.request().postDataJSON().initial_angle_deg===0);
  await page.locator('[data-key="initial_angle_deg"]').dispatchEvent('change');
  const neutral=await(await neutralResponse).json();assert.equal(neutral.frame.spring.compression,0);assert.equal(neutral.frame.spring.cap_force,0);assert.equal(neutral.frame.spring.red_tension,0);assert.equal(neutral.frame.spring.blue_tension,0);
  assert.ok(Object.values(neutral.frame.spring.geometry.routes).every(r=>r.anchor[0]<0));
  await page.waitForFunction(()=>document.querySelector('#snapshot').textContent.includes('θ 0.0°'));
  assert.ok((await page.locator('#cap-detail').textContent()).includes('0.0 mm · unloaded'));
  const drumX=Number(await page.locator('.detail-knee-pulley').getAttribute('cx'));for(const colour of ['red','blue'])assert.ok(Number(await page.locator('.detail-anchor-'+colour).getAttribute('cx'))<drumX);
  await page.locator('.mechanism-panel').screenshot({path:path.join(out,'dual-rope-contracted.png')});fs.writeFileSync(path.join(out,'contracted-preview.json'),JSON.stringify(neutral));
  await page.locator('#load-demo').click();await page.waitForFunction(()=>document.querySelector('#snapshot').textContent.includes('θ -45.0°'));
  const response=page.waitForResponse(r=>r.url().endsWith('/api/inversion/pymunk'));await page.locator('#run').click();const result=await(await response).json();assert.ok(result.diagnostics.flip_time_s>0);assert.ok(result.rows.some(r=>r.active_red)&&result.rows.some(r=>r.active_blue));
  await page.locator('#mechanism[data-mode="recorded"]').waitFor();assert.equal(await page.locator('.js-plotly-plot').count(),10);
  assert.equal(result.config.rope_routing,'central_wrap');assert.equal(result.config.rope_neutral_pose,'folded');assert.equal(result.config.preload,0);assert.equal(result.config.angle_limit_enabled,true);assert.ok(result.frames.every(f=>f.knee[0]>f.hip[0]));assert.ok(result.rows.every(r=>r.theta_deg>=-80.5&&r.theta_deg<=80.5));assert.ok(Math.max(...result.rows.map(r=>Math.max(r.red_lead_angle_deg,r.blue_lead_angle_deg)))<1.1);assert.ok(result.frames.some(f=>Object.values(f.spring.geometry.routes).some(r=>r.pieces.some(p=>p.kind==='arc'&&p.center[0]===0&&p.center[1]===0))));
  await page.locator('#time').evaluate((n,t)=>{n.value=t;n.dispatchEvent(new Event('input',{bubbles:true}));},result.diagnostics.flip_time_s+.01);assert.ok((await page.locator('#readouts').textContent()).includes('N /'));assert.equal(await page.locator('.shared-cap').count(),1);
  await page.locator('.mechanism-panel').screenshot({path:path.join(out,'dual-rope-flip.png')});
  const download=page.waitForEvent('download');await page.locator('#save-run').click();const file=await download;await file.saveAs(path.join(out,'dual-run.json'));const saved=JSON.parse(fs.readFileSync(path.join(out,'dual-run.json'),'utf8'));assert.equal(saved.backend,'inversion_pymunk');assert.equal(saved.config.start_inverted,true);
  await page.locator('[data-key="preset"]').selectOption('knee_bellcrank');await page.locator('#load-demo').click();await page.locator('.bellcrank-femur-anchor').waitFor();assert.equal(await page.locator('[data-key="femur_anchor_distance"]').inputValue(),'50');
  const bell=page.waitForResponse(r=>r.url().endsWith('/api/inversion/pymunk'));await page.locator('#run').click();const b=await(await bell).json();assert.ok(b.diagnostics.flip_time_s>0);await page.locator('#mechanism[data-mode="recorded"]').waitFor();await page.locator('.mechanism-panel').screenshot({path:path.join(out,'bellcrank-flip.png')});
  await page.locator('#gui').click();assert.equal(launches.at(-1).model,'inversion');assert.equal(launches.at(-1).config.preset,'knee_bellcrank');
  await page.goto(origin+'/?tab=physics');const wheel=page.frameLocator('iframe[data-key="physics"]');await wheel.locator('[data-key="spring_topology"]').waitFor();await wheel.locator('[data-key="spring_topology"]').selectOption('invertible_dual_rope');
  const inversion=page.frameLocator('iframe[data-key="inversion-physics"]');await inversion.locator('.routing-pulley-red').waitFor();assert.equal(await page.locator('iframe[data-key="physics"]').isVisible(),false);
  await inversion.locator('[data-key="attachment_offset_deg"]').fill('7');await inversion.locator('[data-key="attachment_offset_deg"]').dispatchEvent('change');
  await page.locator('[data-tab="math"]').click();await page.locator('[data-tab="physics"]').click();assert.equal(await inversion.locator('[data-key="attachment_offset_deg"]').inputValue(),'7');
  await page.locator('#show-gui').click();await page.waitForFunction(()=>document.querySelector('#native-status').dataset.state==='running');assert.equal(launches.at(-1).model,'inversion');assert.equal(launches.at(-1).config.attachment_offset_deg,7);
  await page.locator('[data-tab="math"]').click();await page.locator('[data-inversion-open="math"]').click();const math=page.frameLocator('iframe[data-key="inversion-math"]');await math.locator('#mechanism[data-mode="setup"]').waitFor();assert.equal(await math.locator('[data-key="fixture"]').inputValue(),'hip_fixed');
  await math.locator('[data-key="duration"]').evaluate(n=>n.closest('details').open=true);await math.locator('[data-key="duration"]').fill('.2');await math.locator('[data-key="duration"]').dispatchEvent('change');const mathDone=page.waitForResponse(r=>r.url().endsWith('/api/inversion/math')&&r.status()!==409);await math.locator('#run').click();const mathResponse=await mathDone;assert.equal(mathResponse.status(),200,JSON.stringify(await mathResponse.json()));await math.locator('#status').filter({hasText:'SciPy'}).waitFor({timeout:30000});
  await page.locator('#compare-models').click();await page.waitForFunction(()=>document.querySelector('#lab-status').textContent.includes('Matched fixed-J1 inversion'),null,{timeout:30000});assert.equal(await page.locator('.comparison-chart').count(),3);
  await page.locator('[data-tab="data"]').click();await page.locator('.data-record').filter({hasText:'inversion_pymunk'}).first().click();await page.getByRole('button',{name:'Load invertible suspension profile',exact:true}).click();await inversion.locator('#mechanism[data-mode="setup"]').waitFor();
  await page.setViewportSize({width:390,height:1100});await page.waitForTimeout(150);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
  console.log('PASS: actual inverted setup, three pulleys/two offset attachments/shared cap, torque-driven flips for both designs,50mm bellcrank mount, Plotly/JSON/library, tab memory, matching native envelope and fixed-J1 math/Pymunk comparison.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
