/** Verify the integrated Jonathan linkage in installed Edge; node scripts/verify_jon_linkage.cjs.
 * Inputs: running loopback Motion Lab 4186, original models and mm/deg/kg/N/Nm controls.
 * Outputs: assertions and ignored artifacts/jon-linkage screenshots/JSON/CSV.
 * Limits: browser integration/analytical parity only; no dynamics/contact/hardware.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),out=path.join(root,'artifacts/jon-linkage');fs.mkdirSync(out,{recursive:true});
const source=fs.readFileSync(path.resolve(root,'../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html'),'utf8'),ctx=vm.createContext({});
for(const match of source.matchAll(/<script id="[^"]+">([\s\S]*?)<\/script>/g))vm.runInContext(match[1],ctx);
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true}),page=await browser.newPage({viewport:{width:1600,height:1100}}),errors=[],external=[],native=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>{if(r.request().url().startsWith('http://127.0.0.1:4186/')){if(r.request().url().includes('/api/native-gui')&&r.request().method()==='POST')native.push(r.request().url());return r.continue();}external.push(r.request().url());return r.abort();});
 try{
  await page.goto('http://127.0.0.1:4186/?tab=math&model=jon-v2');
  const frame=()=>page.frames().find(f=>f.url().includes('/jon-linkage/'));
  const ui=page.frameLocator('iframe[data-key="jon-v2"]');await ui.locator('#lab-linkage-sweep').waitFor();
  await page.waitForFunction(()=>document.querySelector('iframe[data-key="jon-v2"]').contentWindow.JonLinkageSource);
  assert.equal(await page.locator('#compare-models').isDisabled(),true);
  assert.equal(await page.locator('iframe[data-key="jon-v2"]').count(),1);
  assert.ok(await frame().evaluate(()=>Math.abs(document.querySelector('main').getBoundingClientRect().top-document.querySelector('aside').getBoundingClientRect().top)<1),'Mechanism and parameter column must start together.');
  assert.equal(await ui.locator('.fbd-svg').count(),5);assert.equal(await ui.locator('svg[id^="sweep-"]').count(),12);
  assert.equal(await ui.locator('#torqueCards .torque-card').count(),8);
  const fields=['L2','L3','ra','rb','rc','rd','re','rf','rw','m1','m2','m3','m5','m6','g','r5I','Tab0','Tcd0','Tef0'];
  for(const id of fields)assert.equal(await ui.locator('#'+id).count(),1,id);
  await ui.locator('#L2').fill('250');await ui.locator('#L3').fill('300');
  await ui.locator('#m2').fill('0.5');await ui.locator('#m3').fill('0.3');await ui.locator('#m5').fill('0.1');await ui.locator('#m6').fill('1');
  await ui.locator('#Tab0').fill('10');await ui.locator('#Tcd0').fill('20');await ui.locator('#Tef0').fill('30');
  await ui.locator('#current-alpha').fill('15');await ui.locator('#current-beta').fill('30');await ui.locator('#current-Fn').fill('120');await ui.locator('#current-Ft').fill('-20');await ui.locator('#current-t2').fill('126');
  await ui.locator('#min-beta').fill('20');await ui.locator('#max-beta').fill('60');
  await ui.locator('#absoluteTorques').check();await ui.locator('#showTau4').uncheck();
  const original=await frame().evaluate(()=>JonLinkage.snapshot());assert.equal(original.parameters.L2,250);assert.equal(original.parameters.Ft,-20);assert.equal(original.ranges.beta.min,20);
  const states=await frame().evaluate(config=>Array.from({length:31},(_,i)=>JonLinkage.solve(config,90+i*3)),original);
  ctx.profile=original.parameters;
  for(let i=0;i<states.length;i++){
   ctx.theta=90+i*3;const s=JSON.parse(vm.runInContext('JSON.stringify(VSLStatic.solve(profile,theta))',ctx));
   for(const key of ['tau2','tau4','dz','gammaUV','gammaYZ']){if(s[key]===null)assert.equal(states[i][key],null);else assert.ok(Math.abs(states[i][key]-s[key])<1e-9,key);}
   for(const key of ['ab','cd','ef'])for(const side of ['U','L'])assert.ok(Math.abs(states[i][key][side]-s[key][side])<1e-9);
  }
  const beforeMode=await frame().evaluate(()=>JonLinkage.solve(JonLinkage.snapshot()));await ui.locator('#driving-yz').check();
  const afterMode=await frame().evaluate(()=>JonLinkage.solve(JonLinkage.snapshot()));assert.ok(Math.abs(beforeMode.tau2-afterMode.tau2)<1e-10);assert.equal(await ui.locator('#current-Fn').isDisabled(),true);
  const modeSnapshot=await frame().evaluate(()=>JonLinkage.snapshot());
  await page.locator('[data-tab="physics"]').click();assert.equal(await page.locator('#jon-linkage-panel').isVisible(),true);assert.deepEqual(await frame().evaluate(()=>JonLinkage.snapshot()),modeSnapshot);
  assert.match(await page.locator('[data-panel="physics"] .workspace-bar p').innerText(),/quasi-static/);
  await page.locator('#show-gui').click();await page.locator('#show-playback').click();assert.deepEqual(native,[]);assert.equal(await page.locator('#gui-dialog').evaluate(n=>n.open),false);
  // Playback of every independent master stops when leaving the mounted editor.
  await ui.locator('#play-beta').click();await page.waitForTimeout(170);await page.locator('[data-tab="home"]').click();await page.waitForTimeout(100);
  const stopped=await frame().evaluate(()=>JonLinkage.snapshot());await page.waitForTimeout(220);assert.deepEqual(await frame().evaluate(()=>JonLinkage.snapshot()),stopped);
  await page.locator('[data-tab="math"]').click();
  await frame().evaluate(config=>JonLinkage.restore(config),original);await page.waitForTimeout(180);
  await page.locator('#profile-name').fill('Jonathan merge test');await page.locator('#save-profile').click();await page.waitForFunction(()=>document.querySelector('#lab-status').textContent.includes('Saved profile: Jonathan merge test'));
  await ui.locator('#lab-linkage-sweep').click();await page.waitForFunction(()=>document.querySelector('#lab-status').textContent.includes('samples'));
  await page.locator('[data-tab="data"]').click();await page.locator('.data-record').filter({hasText:'Jonathan merge test'}).filter({hasText:'run'}).first().click();
  const download=page.waitForEvent('download');await page.getByRole('button',{name:'Download JSON',exact:true}).click();await (await download).saveAs(path.join(out,'sweeps.json'));
  const record=JSON.parse(fs.readFileSync(path.join(out,'sweeps.json'),'utf8'));assert.equal(record.backend,'jon_v2');assert.equal(new Set(record.result.rows.map(row=>row.mode)).size,4);assert.ok(record.result.rows.length>=1444);assert.ok(record.result.source.source_sha256);
  for(const row of record.result.rows){assert.equal('t' in row,false);for(const value of Object.values(row))if(typeof value==='number')assert.ok(Number.isFinite(value));}
  await page.getByRole('button',{name:'Load Jonathan v2 linkage profile',exact:true}).click();await ui.locator('#L2').waitFor();assert.deepEqual(await frame().evaluate(()=>JonLinkage.snapshot().parameters),original.parameters);
  const csvDownload=page.waitForEvent('download');await ui.locator('#exportCsv').click();await (await csvDownload).saveAs(path.join(out,'source-sweeps.csv'));
  const csv=fs.readFileSync(path.join(out,'source-sweeps.csv'),'utf8').split('\n').filter(line=>!line.startsWith('#'));assert.equal(csv[0].split(',').length,31);assert.ok(csv.length>=1445);
  // Run a saved profile in Comparison without mutating current editor controls.
  await page.locator('[data-tab="data"]').click();await page.locator('.data-record').filter({hasText:'Jonathan merge test'}).filter({hasText:'profile'}).first().click();
  const live=await frame().evaluate(()=>JonLinkage.snapshot());await page.getByRole('button',{name:'Run profile in Comparison',exact:true}).click();await page.locator('#compare-panel').waitFor({state:'visible'});assert.deepEqual(await frame().evaluate(()=>JonLinkage.snapshot()),live);
  await page.locator('[data-tab="math"]').click();await page.locator('#theme-toggle').click();await page.waitForTimeout(200);assert.equal(await ui.locator('html').getAttribute('data-theme'),'dark');
  await page.screenshot({path:path.join(out,'desktop.png')});await ui.locator('.motion-grid').screenshot({path:path.join(out,'mechanism.png')});
  const saved=await frame().evaluate(()=>JonLinkage.snapshot());await page.reload();await ui.locator('#lab-linkage-sweep').waitFor();await page.waitForFunction(()=>document.querySelector('iframe[data-key="jon-v2"]').contentWindow.JonLinkageSource);assert.deepEqual(await frame().evaluate(()=>JonLinkage.snapshot()),saved);
  const changed={...saved,parameters:{...saved.parameters,m2:1.25,beta:35},theta2:137};
  await page.locator('[data-tab="data"]').click();await page.getByLabel('Import profile or recorded run JSON').setInputFiles({name:'jon-original.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(changed))});await page.locator('.data-record').filter({hasText:'jon-original'}).click();await page.getByRole('button',{name:'Load Jonathan v2 linkage profile',exact:true}).click();
  assert.equal(await ui.locator('#m2').inputValue(),'1.25');assert.equal(await ui.locator('#current-t2').inputValue(),'137');
  // A bad import is atomic; invalid drafts cannot overwrite valid refresh memory.
  const valid=await frame().evaluate(()=>JonLinkage.snapshot());const failure=await frame().evaluate(config=>{try{JonLinkage.restore({...config,ranges:{...config.ranges,beta:{min:90,max:0}}});return false;}catch{return true;}},valid);assert.equal(failure,true);assert.deepEqual(await frame().evaluate(()=>JonLinkage.snapshot()),valid);
  await ui.locator('#L2').fill('-1');await page.locator('#save-profile').click();await page.locator('#lab-error').waitFor({state:'visible'});assert.match(await page.locator('#lab-error').innerText(),/invalid/i);await frame().evaluate(config=>JonLinkage.restore(config),valid);
  await page.locator('[data-tab="math"]').click();await page.setViewportSize({width:390,height:1000});await page.waitForTimeout(250);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.ok(await frame().evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(out,'mobile.png')});await ui.locator('.motion-grid').screenshot({path:path.join(out,'mobile-mechanism.png')});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);assert.deepEqual(native,[]);
  console.log('PASS: original-model parity, all v2 controls, shared Math/Physical state, load conversion, paused background, profiles/JSON/CSV/sweep library/comparison, refresh, invalid state, dark/mobile, no native/external requests.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
