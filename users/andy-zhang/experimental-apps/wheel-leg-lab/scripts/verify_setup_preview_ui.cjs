/** Check architecture selection previews geometry before any simulation request.
 * Run: node scripts/verify_setup_preview_ui.cjs with Motion Lab at loopback4186.
 * Inputs: editable catalog SI profiles; outputs: ignored browser screenshots.
 * Real APIs verify setup-only state, cancellation and recorded-data separation.
 * No hardware, contact or numerical-solver validation is inferred from a preview.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],simulations=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(r.method()==='POST'&&/\/api\/(?:math\/|pymunk\/)?simulate$/.test(r.url()))simulations.push(r.postDataJSON());});
  const out=path.join(__dirname,'../artifacts/setup-preview');fs.mkdirSync(out,{recursive:true});
  for(const route of ['physics','mathematical']){
   await page.goto('http://127.0.0.1:4186/'+route+'/?loadOnly=1');await page.locator('#mechanism[data-mode="setup-preview"]').waitFor();
   assert.equal(await page.locator('#play').isEnabled(),false);assert.equal(await page.locator('#save-data').isEnabled(),false);
   const startCount=simulations.length;
   for(const topology of ['legacy_tip','hip_pulley','knee_pulley','direct_scissor','hip_bellcrank','knee_bellcrank','chassis_direct','knee_capture','gravity_balance']){
    const response=page.waitForResponse(r=>r.url().endsWith('/api/setup-preview')&&r.request().postDataJSON()?.spring_topology===topology);
    await page.locator('[data-key="spring_topology"]').selectOption(topology);const data=await(await response).json();
    assert.equal(data.kind,'setup-preview');assert.equal(data.solver_steps,0);assert.equal(data.rows,undefined);
    await page.locator(`.spring-mechanism-overlay[data-topology="${topology}"]`).waitFor();
    assert.equal(await page.locator('#joint-values').textContent(),'');assert.equal(await page.locator('#torque-values').textContent(),'');
   }
   assert.equal(simulations.length,startCount,'Selecting all architectures does not run a solver');
   const guide=page.waitForResponse(r=>r.url().endsWith('/api/setup-preview')&&r.request().postDataJSON()?.guide_pulleys_visible);
   await page.locator('[data-key="guide_pulleys_visible"]').check();await guide;await page.locator('.guide-belt-dot').first().waitFor();
   assert.equal(await page.locator('.guide-span-force').count(),0,'Preview does not invent solved belt loads');
   await page.locator('#forces').check();assert.equal(await page.locator('#joint-values').textContent(),'');
   const height=await page.locator('#pose-values').textContent();await page.locator('[data-key="theta"]').fill('55');await page.locator('[data-key="theta"]').dispatchEvent('change');
   await page.waitForFunction(old=>document.querySelector('#pose-values').textContent.includes('55.0')&&document.querySelector('#pose-values').textContent!==old,height);
   assert.equal(await page.locator('#mechanism').evaluate(n=>[...n.querySelectorAll('[d]')].some(p=>/NaN|Infinity/.test(p.getAttribute('d')))),false);
   // A quick selection supersedes the debounce for the old setup.
   await page.locator('[data-key="spring_topology"]').selectOption('hip_pulley');await page.locator('[data-key="spring_topology"]').selectOption('direct_scissor');
   await page.locator('.spring-mechanism-overlay[data-topology="direct_scissor"]').waitFor();
   await page.locator('[data-key="duration"]').evaluate(n=>n.closest('details').open=true);await page.locator('[data-key="duration"]').fill('1');await page.locator('[data-key="duration"]').dispatchEvent('change');
   // Run immediately, while the debounce is pending: late preview cannot replace results.
   await page.locator('#run').click();await page.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
   assert.equal(await page.locator('#mechanism').getAttribute('data-mode'),'recorded');assert.equal(await page.locator('#play').isEnabled(),true);
   assert.equal(await page.locator('.setup-preview-note').isVisible(),false);assert.ok((await page.locator('#joint-values').textContent()).includes('J2'));
   await page.locator('[data-key="spring_topology"]').selectOption('knee_capture');await page.locator('.spring-mechanism-overlay[data-topology="knee_capture"]').waitFor();
   await page.getByRole('button',{name:'Show last recording',exact:true}).click();
   assert.equal(await page.locator('#mechanism').getAttribute('data-mode'),'recorded');assert.equal(await page.locator('[data-key="spring_topology"]').inputValue(),'knee_capture','Returning to recording preserves unsimulated edits');
   assert.equal(await page.locator('.spring-mechanism-overlay').getAttribute('data-topology'),'direct_scissor');
   await page.locator('[data-key="theta"]').fill('56');await page.locator('[data-key="theta"]').dispatchEvent('change');await page.locator('#mechanism[data-mode="setup-preview"]').waitFor();
   await page.screenshot({path:path.join(out,route+'.png'),fullPage:true});
  }
  assert.deepEqual(errors,[]);console.log('PASS: all9 architectures preview beforeRun inbothbenches, zero solverrequests/steps/loads, geometry edits, guide preview, superseded requests, immediateRun cancellation and previous-recording separation.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
