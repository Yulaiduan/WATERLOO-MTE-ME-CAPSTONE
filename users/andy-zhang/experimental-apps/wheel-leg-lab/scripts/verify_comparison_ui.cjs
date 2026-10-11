/** Exercise the comparison workspace against actual saved wheel solver data.
 * Run: node scripts/verify_comparison_ui.cjs with Motion Lab on port4186.
 * Inputs: same SI wheel profile, library JSON and real solver APIs. Outputs:
 * ignored workspace JSON/screenshots, per-plot visibility/split/delta assertions.
 * Uses Playwright/Edge; verifies browser wiring, not hardware accuracy.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1600,height:1050},acceptDownloads:true}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const out=path.join(__dirname,'../artifacts/comparison-ui');fs.mkdirSync(out,{recursive:true});
  await page.goto('http://127.0.0.1:4186/?tab=math');
  const math=page.frameLocator('iframe[data-key="math"]');await math.locator('#status').filter({hasText:'Recorded'}).waitFor({timeout:30000});
  assert.equal(await page.locator('[data-math-model="counterbalance"],[data-math-model="linkage"]').count(),0);
  const duration=math.locator('[data-key="duration"]');await duration.evaluate(n=>n.closest('details').open=true);await duration.fill('.9');await duration.dispatchEvent('change');
  await page.locator('#profile-name').fill('Comparison QA profile');
  await page.locator('#save-profile').click();await page.waitForFunction(()=>document.querySelector('#lab-status').textContent.includes('Saved profile'));
  await page.locator('#compare-models').click();await page.waitForFunction(()=>document.querySelector('#lab-status').textContent.includes('Both runs saved'),null,{timeout:45000});
  assert.equal(await page.locator('#compare-panel').isVisible(),true);
  await page.locator('.comparison-stat').nth(1).waitFor();assert.equal(await page.locator('.comparison-plot-panel').count(),3);
  assert.equal(await page.locator('.comparison-chart').first().evaluate(n=>n.data.length),2);
  const delta=await page.locator('.comparison-chart').nth(1).evaluate(n=>n.data[0].y);assert.ok(delta.every(Number.isFinite));assert.ok(Math.max(...delta.map(Math.abs))>0);
  assert.match(await page.locator('.comparison-stat').first().textContent(),/max.*RMS.*final/);
  assert.equal(await page.locator('.comparison-warning').count(),0);
  assert.equal(await page.locator('.comparison-options:visible').count(),0);
  assert.ok(await page.locator('.comparison-chart').first().evaluate(n=>n.getBoundingClientRect().top<320),'Compact layout puts the plots near the top');
  const first=page.locator('.comparison-plot-panel').first();await first.getByRole('button',{name:'Plot 1 controls',exact:true}).click();await first.getByRole('button',{name:'Split side by side',exact:true}).click();
  let active=page.locator('.comparison-plot-panel.is-active');const activeId=await active.getAttribute('data-plot-id');
  await page.getByRole('searchbox',{name:'Search comparison channels'}).fill('j2_force');await page.locator('.comparison-channel').filter({hasText:'j2_force'}).click();
  await page.waitForFunction(id=>document.querySelector(`[data-plot-id="${id}"] .comparison-chart`).data?.length===2,activeId);
  assert.equal(await first.locator('.comparison-chart').evaluate(n=>n.data.length),2,'Adding a force channel leaves the displacement plot alone');
  await active.locator('.comparison-options-toggle').click();await active.locator('.comparison-traces input').first().uncheck();
  await page.waitForFunction(id=>document.querySelector(`[data-plot-id="${id}"] .comparison-chart`).data?.[0].visible==='legendonly',activeId);
  await active.locator('.comparison-plot-controls input').uncheck();await page.locator('#theme-toggle').click();
  active=page.locator(`[data-plot-id="${activeId}"]`);assert.equal(await active.locator('.comparison-plot-controls input').isChecked(),false);
  assert.equal(await active.locator('.comparison-traces input').first().isChecked(),false);
  assert.equal(await active.locator('.comparison-chart').evaluate(n=>n._fullLayout.showlegend),false);
  await active.getByRole('button',{name:'Split stacked',exact:true}).click();assert.equal(await page.locator('.comparison-plot-panel').count(),5);
  await page.getByRole('searchbox',{name:'Search comparison channels'}).fill('chassis_vy');await page.locator('.comparison-channel').filter({hasText:'chassis_vy'}).click();
  const newer=page.locator('.comparison-plot-panel.is-active');await newer.locator('.comparison-chart').waitFor();
  await page.locator('.comparison-source-tools > summary').click();
  const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export comparison JSON',exact:true}).click();await (await download).saveAs(path.join(out,'workspace.json'));
  const saved=JSON.parse(fs.readFileSync(path.join(out,'workspace.json'),'utf8'));assert.equal(saved.schema,'motion-lab-comparison/v1');assert.equal(Object.keys(saved.panels).length,5);assert.equal(saved.panels[activeId].legend,false);assert.equal(saved.panels[activeId].traces[0].visible,false);
  await newer.locator('.comparison-options-toggle').click();await newer.getByRole('button',{name:'Remove plot',exact:true}).click();assert.equal(await page.locator('.comparison-plot-panel').count(),4);
  await page.getByLabel('Import comparison, profile or recorded data JSON').setInputFiles(path.join(out,'workspace.json'));
  await page.locator('.comparison-status').filter({hasText:'Restored'}).waitFor();assert.equal(await page.locator('.comparison-plot-panel').count(),5);
  assert.equal(await page.locator(`[data-plot-id="${activeId}"] .comparison-traces input`).first().isChecked(),false);
  await page.getByRole('button',{name:'Load profiles / recordings',exact:true}).click();
  const profile=page.locator('.comparison-library-record').filter({hasText:'Comparison QA profile'}).filter({hasText:'profile → runs solver'}).first();await profile.locator('input').check();
  const response=page.waitForResponse(r=>r.url().endsWith('/api/math/simulate')&&r.request().method()==='POST');await page.getByRole('button',{name:'Load selected (run profiles)',exact:true}).click();assert.equal((await response).status(),200);
  await page.waitForFunction(()=>!document.querySelector('.comparison-library button:last-child').disabled);
  await page.locator('.comparison-channel').first().waitFor();assert.equal(await page.locator('#compare-panel > .error').isVisible(),false);
  await page.getByRole('button',{name:'Load profiles / recordings',exact:true}).click();
  await page.locator('.comparison-source-tools > summary').click();
  await page.getByRole('button',{name:'Hide channels',exact:true}).click();assert.equal(await page.locator('.comparison-sidebar').isVisible(),false);
  await page.getByRole('button',{name:'Show channels',exact:true}).click();assert.equal(await page.locator('.comparison-sidebar').isVisible(),true);
  await page.getByRole('button',{name:'Focus plots',exact:true}).click();assert.equal(await page.locator('.lab-header').isVisible(),false);assert.equal(await page.locator('.comparison-sidebar').isVisible(),false);assert.equal(await page.locator('.comparison-options:visible').count(),0);
  await page.waitForFunction(()=>[...document.querySelectorAll('.comparison-chart')].every(n=>n._fullLayout.showlegend===false));
  await page.getByRole('button',{name:'Exit focus',exact:true}).click();assert.equal(await page.locator('.lab-header').isVisible(),true);assert.equal(await page.locator(`[data-plot-id="${activeId}"] .comparison-traces input`).first().isChecked(),false);
  await page.locator('.comparison-chart').first().evaluate(n=>Plotly.relayout(n,{'xaxis.range':[.3,.6]}));assert.deepEqual(await page.locator('.comparison-chart').first().evaluate(n=>n._fullLayout.xaxis.range),[.3,.6]);
  await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});await page.setViewportSize({width:390,height:950});await page.screenshot({path:path.join(out,'mobile-before.png'),fullPage:true});await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth,null,{timeout:5000}).catch(async error=>{console.log(await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(n=>n.getBoundingClientRect().right>innerWidth+1).slice(0,15).map(n=>[n.tagName,n.className,n.getBoundingClientRect().width])));throw error;});
  await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});assert.deepEqual(errors,[]);
  console.log('PASS: actual paired deltas, compact/collapsible controls and channels, focus/restore, independent visibility, both splits, workspace JSON roundtrip, actual profile rerun, zoom/theme/mobile.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
