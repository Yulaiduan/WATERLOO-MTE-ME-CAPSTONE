/** Check cylinder motion, three routes and form memory with the actual APIs.
 * Run node scripts/verify_transmission_memory_ui.cjs with Motion Lab at4186.
 * Inputs: editable SI fixture profiles; outputs: ignored SVG/browser evidence.
 * Housing/idler packaging is schematic; no hardware/contact assertion.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1500,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const origin='http://127.0.0.1:4186',out=path.join(__dirname,'../artifacts/transmission-memory');fs.mkdirSync(out,{recursive:true});
  await page.goto(origin+'/physics/?loadOnly=1');await page.locator('#mechanism[data-mode="setup-preview"]').waitFor();
  await page.locator('[data-key="spring_topology"]').selectOption('knee_capture');await page.locator('#transmission-detail .ideal_rope').waitFor();
  await page.locator('[data-key="spring_mode"]').selectOption('captured');
  const capsule=()=>page.locator('#transmission-detail .spring-transmission').evaluate(n=>({coil:Number(n.dataset.coilLengthM),cap:Number(n.dataset.capX),seat:Number(n.dataset.seatX),scale:Number(n.dataset.scalePxM),method:n.dataset.transmission}));
  // Non-pulley: inline or rigid reversing piston. Pulley: rope+piston only.
  await page.locator('[data-key="spring_topology"]').selectOption('legacy_tip');
  for(const method of ['direct','pullrod']){
   await page.locator('[data-key="spring_transmission"]').selectOption(method);await page.locator('#transmission-detail .'+method).waitFor();
   assert.equal(await page.locator('#transmission-detail .cylinder-housing').count(),method==='direct'?0:1);
   assert.equal(await page.locator('#mechanism .direct-cylinder-housing').count(),0);
   assert.equal(await page.locator('#transmission-detail .routing-idler').count(),0);
   assert.equal(await page.locator('#transmission-comparison svg').count(),3);
  }
  for(const topology of ['hip_pulley','knee_pulley','knee_capture']){
   await page.locator('[data-key="spring_topology"]').selectOption(topology);await page.locator('#transmission-detail .ideal_rope').waitFor();
   assert.equal(await page.locator('[data-key="spring_transmission"]').isDisabled(),true);assert.equal(await page.locator('[data-key="spring_transmission"] option').count(),1);
   assert.equal(await page.locator('#mechanism .cylinder-housing').count(),1);assert.equal(await page.locator('#mechanism .pull-cable').count(),1);
   assert.equal(await page.locator('#transmission-detail .piston-rod-eye').count(),1);
  }
  // Full recording: both main and detail consume the captured coil length, cap
  // motion has opposite sign under pull-through, and no per-frame plot rebuild.
  await page.locator('[data-key="duration"]').evaluate(n=>n.closest('details').open=true);
  await page.locator('[data-key="duration"]').fill('2');await page.locator('[data-key="duration"]').dispatchEvent('change');
  const response=page.waitForResponse(r=>r.url().endsWith('/api/simulate')&&r.request().method()==='POST');await page.locator('#run').click();const run=await(await response).json();
  await page.locator('#mechanism[data-mode="recorded"]').waitFor();
  const poses=[];for(const t of [0,.65,1.2,1.8]){await page.locator('#time').evaluate((n,t)=>{n.value=t;n.dispatchEvent(new Event('input',{bubbles:true}));},t);const current=await capsule();
   const nearest=run.frames.reduce((a,b)=>Math.abs(b.t-t)<Math.abs(a.t-t)?b:a);
   assert.ok(Math.abs(current.coil-nearest.spring_coil_length)<1e-12);assert.ok(Math.abs(current.seat-current.cap-current.coil*current.scale)<1e-8);poses.push(current);
  }
  assert.ok(Math.max(...poses.map(p=>p.cap))-Math.min(...poses.map(p=>p.cap))>.1,'Recorded end cap actually moves');
  await page.locator('.transmission-panel summary').click();await page.locator('.mechanism-panel').screenshot({path:path.join(out,'rope-and-three-transmissions.png')});
  await page.locator('#model-view').selectOption('annotated');await page.locator('#force-view').selectOption('fy');await page.locator('#probe').selectOption('j2');await page.locator('#forces').check();
  await page.locator('[data-key="length"]').fill('281');await page.locator('[data-key="length"]').dispatchEvent('change');
  await page.reload();await page.locator('#mechanism[data-mode="setup-preview"]').waitFor();
  assert.equal(await page.locator('[data-key="length"]').inputValue(),'281');assert.equal(await page.locator('[data-key="spring_transmission"]').inputValue(),'ideal_rope');assert.equal(await page.locator('#model-view').inputValue(),'annotated');assert.equal(await page.locator('#forces').isChecked(),true);assert.equal(await page.locator('#probe').inputValue(),'j2');
  // Loaded profile is explicit authority, not overwritten by remembered values.
  await page.locator('#profile-import').setInputFiles({name:'profile.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({config:{...run.config,length:.3}}))});
  await page.locator('#status').filter({hasText:'Profile loaded'}).waitFor();assert.equal(await page.locator('[data-key="length"]').inputValue(),'300');
  await page.goto(origin+'/?tab=physics&architecture=constant-lift');const bench=page.frameLocator('iframe[data-key="physics"]');await bench.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  assert.equal(await bench.locator('[data-key="damping"]').count(),0);assert.equal(await bench.locator('[data-key="aux_spring_enabled"]').count(),0);assert.equal(await bench.locator('.replacement-damper').count(),0);
  await bench.locator('[data-key="spring_topology"]').selectOption('knee_capture');await bench.locator('#transmission-detail .ideal_rope').waitFor();
  assert.equal(await bench.locator('[data-key="guide_pulleys_visible"]').isChecked(),true,'Unchanged guide checkbox survives a preset rebuild');
  await bench.locator('[data-key="spring_topology"]').selectOption('gravity_balance');await bench.locator('#transmission-detail .direct').waitFor();
  await bench.locator('[data-key="theta"]').fill('48');await bench.locator('[data-key="theta"]').dispatchEvent('change');await bench.locator('#forces').check();
  await page.locator('[data-tab="math"]').click();await page.locator('[data-tab="physics"]').click();assert.equal(await bench.locator('[data-key="theta"]').inputValue(),'48');assert.equal(await bench.locator('#forces').isChecked(),true);
  await page.locator('[data-tab="studies"]').click();await page.locator('#study-select').selectOption('ratio');const study=page.frameLocator('iframe[data-key="studies"]');await study.locator('input[type="number"]').first().waitFor();
  const input=study.locator('input[type="number"]').first();const id=await input.getAttribute('id');assert.ok(id);await input.fill('2.1');await input.dispatchEvent('input');await study.locator('#wl-projection').check();await study.locator('#wl-radius').evaluate(n=>{n.value='220';n.dispatchEvent(new Event('input',{bubbles:true}));});
  await page.locator('#study-select').selectOption('paths');await study.locator('#'+id).waitFor({state:'detached'});
  await page.locator('#study-select').selectOption('ratio');await study.locator('#'+id).waitFor();await page.waitForTimeout(150);
  assert.equal(await study.locator('#'+id).inputValue(),'2.1');assert.equal(await study.locator('#wl-projection').isChecked(),true);assert.equal(await study.locator('#wl-radius').inputValue(),'220');
  // Changed field contract is skipped, unchanged checkboxes/numbers restore.
  const matched=await page.evaluate(async()=>{const {captureForm,restoreForm}=await import('/form-memory.js');const root=document.createElement('div');root.innerHTML='<input id="a" type="number" min="0" max="500" value="42"><input id="b" type="checkbox" checked><select id="s"><option value="a">A</option><option value="b" selected>B</option></select>';const saved=captureForm(root);root.querySelector('#a').max='50';root.querySelector('#a').value='9';root.querySelector('#b').checked=false;root.querySelector('#s').value='a';restoreForm(root,saved);return [root.querySelector('#a').value,root.querySelector('#b').checked,root.querySelector('#s').value];});assert.deepEqual(matched,['9',true,'b']);
  assert.deepEqual(errors,[]);console.log('PASS: actual coil/cap travel, three distinct transmissions, routed cable/idler, undamped replacement, no extra strut controls, tab/refresh/study memory and explicit profile precedence.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
