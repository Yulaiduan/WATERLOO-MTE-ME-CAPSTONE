/** Verify Motion Lab sizing/V4 integration using the real local app and source solver.
 * Run: node scripts/verify_sizing.cjs after Start Motion Lab.cmd.
 * Inputs: port 4186, sheet snapshot, mm/deg V4 source; outputs ignored screenshots/JSON.
 * Isolated browser storage, no cloud writes or native GUI launch. Not hardware validation.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 const base='http://127.0.0.1:4186',out=path.resolve('.preview/sizing-qa');fs.mkdirSync(out,{recursive:true});
 try{
  const page=await browser.newPage({viewport:{width:1540,height:1100},acceptDownloads:true}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/?tab=sizing');const frame=page.frameLocator('iframe[data-key="sizing"]');
  await frame.locator('body[data-ready="true"]').waitFor();
  const sizing=page.frames().find(f=>f.url().includes('/sizing/'));
  const result=()=>sizing.evaluate(()=>window.sizingResults);
  let a=await result();assert.equal(a.candidates.length,54);assert.equal(await frame.locator('.js-plotly-plot').count(),3);assert.equal(await frame.locator('#error').isVisible(),false);
  await frame.locator('#chassis').fill('40');await sizing.waitForFunction(()=>window.sizingResults.assumptions.chassis===40);
  let b=await result();assert.equal(b.assumptions.springForce,a.assumptions.springForce);assert.ok(b.rows[0].requiredTorque>a.rows[0].requiredTorque);
  await frame.locator('#balance').click();await sizing.waitForFunction(()=>window.sizingResults.assumptions.springForce!==65);
  assert.equal(await frame.locator('#error').isVisible(),false);
  await frame.locator('#reset').click();await sizing.waitForFunction(()=>window.sizingResults.assumptions.chassis===20);
  await frame.locator('#actuator').selectOption('2');await sizing.waitForFunction(()=>window.sizingResults.assumptions.actuator===2);b=await result();
  assert.ok(Math.abs(b.rows[20].rpm-2*a.rows[20].rpm)<1e-9);assert.ok(Math.abs(b.rows[20].requiredTorque-a.rows[20].requiredTorque/2)<1e-9);
  await frame.locator('#minAngle').fill('80');await frame.locator('#error').waitFor({state:'visible'});
  await frame.locator('#reset').click();await frame.locator('#error').waitFor({state:'hidden'});
  await frame.locator('summary').filter({hasText:'Map bounds'}).click();
  await frame.locator('#gears-file').setInputFiles({name:'invalid.csv',mimeType:'text/csv',buffer:Buffer.from('Model,Ratio\nBad,20')});
  await frame.locator('#error').filter({hasText:'Missing sheet column'}).waitFor();assert.equal((await result()).catalog.gearboxes.length,6);
  const gearCsv='Model,Ratio,Nominal output torque (N m),Momentary output torque (N m),Efficiency,Rated input (rpm),Max input (rpm)\nTest sheet gear,20,30,60,94%,3000,6000';
  await frame.locator('#gears-file').setInputFiles({name:'gearboxes.csv',mimeType:'text/csv',buffer:Buffer.from(gearCsv)});
  await sizing.waitForFunction(()=>window.sizingResults.catalog.gearboxes.length===1);assert.equal((await result()).candidates.length,9);
  await frame.locator('#restore-catalog').click();await sizing.waitForFunction(()=>window.sizingResults.catalog.gearboxes.length===6);
  const downloadPromise=page.waitForEvent('download');await frame.locator('#export').click();const download=await downloadPromise;const packet=JSON.parse(fs.readFileSync(await download.path(),'utf8'));assert.equal(packet.schema,'motion-lab-sizing-result/v1');assert.equal(packet.rows.length,101);
  await frame.locator('#save-library').click();await frame.locator('#source-status').filter({hasText:'saved in Profiles'}).waitFor();
  await page.locator('[data-tab="data"]').click();await page.getByText(/Suspension sizing · Flipsky/).first().waitFor();
  await page.locator('[data-tab="sizing"]').click();assert.equal(await frame.locator('#chassis').inputValue(),'20');
  await page.locator('#show-gui').click();assert.match(await page.locator('#lab-status').innerText(),/analytical screen/);
  await page.locator('[data-tab="vsl"]').click();const vf=page.frameLocator('iframe[data-key="vsl"]');await vf.locator('#vsl-to-sizing').waitFor();
  const vpage=page.frames().find(f=>f.url().includes('/vsl-v4/'));
  assert.equal(await vpage.evaluate(()=>VSLApp.playing),false);
  await vf.locator('#min-t2').fill('90');await vf.locator('#min-t2').press('Tab');await vf.locator('#vsl-to-sizing').click();
  await vf.locator('#vsl-lab-status').filter({hasText:'singular'}).waitFor();assert.ok(page.url().includes('tab=vsl'));
  await vf.locator('#reset').click();
  // Exact source-model parity, independent from the served bridge and any saved output.
  const source=fs.readFileSync(path.resolve('../../../jonathan-xie/experimental-apps/leg-solver/v4-pulley.html'),'utf8'),ctx={};vm.createContext(ctx);
  for(const id of ['solver-model','statics-model','spring-model']){const match=source.match(new RegExp('<script id="'+id+'">([\\s\\S]*?)</script>'));if(match)vm.runInContext(match[1],ctx);}
  const modelAvailable=vm.runInContext('typeof VSLStatic',ctx);assert.equal(modelAvailable,'object');
  await vf.locator('#vsl-to-sizing').click();await page.waitForURL(/tab=sizing/);await frame.locator('#v4-overlay').waitFor();
  await sizing.waitForFunction(()=>window.sizingResults.v4?.rows.length===181);b=await result();
  ctx.parameters=b.v4.parameters;
  for(const row of b.v4.rows){ctx.theta=row.theta2;const expected=vm.runInContext('VSLStatic.solve(parameters,theta,false)',ctx);assert.ok(Math.abs(row.hipTorque-expected.tau2)<1e-10);assert.ok(Math.abs(row.outputRpm-Math.abs(100/expected.spring.Jz)*60/(2*Math.PI))<1e-10);}
  assert.ok(Math.max(...b.v4.rows.map(r=>Math.abs(r.hipTorque)))<.038);assert.equal(b.v4.torqueConvention,'applied-ccw-hip');
  await page.screenshot({path:path.join(out,'sizing-desktop.png'),fullPage:false});
  await page.locator('#theme-toggle').click();assert.equal(await sizing.evaluate(()=>document.documentElement.dataset.theme),'dark');
  await page.locator('[data-tab="vsl"]').click();assert.equal(await vpage.evaluate(()=>document.documentElement.dataset.theme),'dark');
  await vf.locator('#vsl-save-study').click();await page.locator('#lab-status').filter({hasText:'Saved V4 parameters'}).waitFor();
  await page.screenshot({path:path.join(out,'v4-desktop.png'),fullPage:false});
  await page.locator('[data-tab="sizing"]').click();await frame.locator('#clear-v4').click();await frame.locator('#v4-overlay').waitFor({state:'hidden'});
  await page.setViewportSize({width:390,height:844});
  await sizing.waitForFunction(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+2,{},{timeout:5000}).catch(async()=>{console.log(await sizing.evaluate(()=>({w:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,nodes:[...document.querySelectorAll('body *')].filter(n=>n.getBoundingClientRect().right>document.documentElement.clientWidth+2).slice(0,12).map(n=>[n.tagName,n.className,n.getBoundingClientRect().width])})));});
  await page.screenshot({path:path.join(out,'sizing-mobile.png'),fullPage:false});
  const overflow=await sizing.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+2);assert.equal(overflow,false,'sizing should not overflow mobile width');
  assert.deepEqual(errors,[]);console.log(JSON.stringify({passed:true,combinations:54,samples:101,v4SourceParitySamples:181,errors,screenshots:out}));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
