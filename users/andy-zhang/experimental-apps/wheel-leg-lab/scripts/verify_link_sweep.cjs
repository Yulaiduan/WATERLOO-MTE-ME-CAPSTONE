// Verify the sizing study through real browser controls, plots and exports.
// Run: node scripts/verify_link_sweep.cjs with Motion Lab at 127.0.0.1:4186.
// Inputs: mm, degrees, N; outputs assertions and ignored screenshots/configs.
// Limits: analytical sizing / UI / memory only; no robot dynamics or hardware.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
(async()=>{
  const root=path.resolve(__dirname,'..'),out=path.join(root,'artifacts/link-sweep');fs.mkdirSync(out,{recursive:true});
  const model=await import(pathToFileURL(path.join(root,'web/force-plots/link-sweep-model.js')));
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  try {
    const page=await browser.newPage({viewport:{width:1280,height:1000}}),errors=[],external=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.route('**/*',route=>{if(route.request().url().startsWith('http://127.0.0.1:4186/'))return route.continue();external.push(route.request().url());return route.abort();});
    const set=async(id,value)=>{await page.locator('#ls-'+id).fill(String(value));await page.locator('#ls-'+id).dispatchEvent('change');};
    const run=async()=>{await page.locator('#ls-run').click();assert.equal(await page.locator('#ls-error').isVisible(),false);};
    await page.goto('http://127.0.0.1:4186/force-plots/');await page.locator('#ls-rows tr').first().waitFor();
    assert.equal(await page.locator('#ls-diameter').inputValue(),'400');assert.equal(await page.locator('#ls-rom').inputValue(),'200');
    assert.ok((await page.locator('#ls-selected').textContent()).includes('L = 120.0 mm'));
    const expected=model.sweep(model.defaultSweep()).best;
    const first=await page.locator('#ls-rows tr').first().innerText();assert.ok(first.includes(expected.peak.toFixed(2)));
    for(const id of ['start','rom','end']){
      if(id==='rom')await page.locator('#ls-nominal').uncheck();
      const before=Number(await page.locator('#ls-'+id).inputValue());
      await page.locator('#ls-'+id+'-unit').selectOption('deg');
      const degrees=Number(await page.locator('#ls-'+id).inputValue());assert.ok(degrees>0);
      await page.locator('#ls-'+id+'-unit').selectOption('mm');
      assert.ok(Math.abs(Number(await page.locator('#ls-'+id).inputValue())-before)<1e-6);
    }
    await page.locator('#ls-nominal').check();await set('diameter',200);await run();
    assert.equal(await page.locator('#ls-radius').inputValue(),'100');assert.equal(await page.locator('#ls-rom').inputValue(),'100');
    await set('radius',200);await run();assert.equal(await page.locator('#ls-diameter').inputValue(),'400');
    await page.locator('#ls-nominal').uncheck();
    await page.locator('#ls-start-unit').selectOption('deg');await set('start',10);
    await page.locator('#ls-rom-unit').selectOption('deg');await set('rom',35);
    await page.locator('#ls-end-unit').selectOption('deg');await set('end',5);await run();
    assert.ok((await page.locator('#ls-selected').textContent()).includes('(35.00°)'));
    await page.locator('#ls-start-unit').selectOption('mm');await set('start',20);
    await page.locator('#ls-end-unit').selectOption('mm');await set('end',20);
    await page.locator('#ls-nominal').check();await run();
    await page.locator('#ls-weighting').selectOption('angle');await run();
    assert.ok((await page.locator('#ls-status').textContent()).includes('angle weighting'));
    await page.locator('#ls-shaft').selectOption('knee');await run();
    const knee=await page.locator('#ls-rows tr').first().innerText();
    const kc={...model.defaultSweep(),weighting:'angle',shaft:'knee'};
    assert.ok(knee.includes(model.sweep(kc).best.peak.toFixed(2)));
    await page.locator('#ls-objective').selectOption('flat');await run();
    assert.ok((await page.locator('#ls-selected').textContent()).includes('L = 600.0 mm'));assert.equal(await page.locator('#ls-boundary').isVisible(),true);
    await page.locator('#ls-winners button').first().click();assert.ok((await page.locator('#ls-selected').textContent()).includes('L = 120.0 mm'));
    await set('previewLink',240);await page.locator('#ls-inspect').click();
    assert.ok((await page.locator('#ls-selected').textContent()).includes('L = 240.0 mm'));
    await set('chassisDepth',400);await set('airGap',80);await run();
    const gaps=await page.locator('#ls-rows tr').evaluateAll(xs=>xs.map(tr=>parseFloat(tr.cells[7].textContent)));assert.ok(gaps.every(x=>x>=80));
    await set('maxLink',100);await run();assert.equal(await page.locator('#ls-results').isVisible(),false);
    assert.ok((await page.locator('#ls-status').textContent()).includes('No feasible'));
    const emptyDownload=page.waitForEvent('download');await page.locator('#ls-save').click();
    const empty=await emptyDownload;await empty.saveAs(path.join(out,'infeasible-config.json'));
    assert.equal(JSON.parse(fs.readFileSync(path.join(out,'infeasible-config.json'),'utf8')).selected,null);
    await set('maxLink',600);await set('chassisDepth',200);await set('airGap',20);
    await page.locator('#ls-shaft').selectOption('hip');await page.locator('#ls-weighting').selectOption('travel');await page.locator('#ls-objective').selectOption('peak');await run();
    const csvDownload=page.waitForEvent('download');await page.locator('#ls-export').click();
    const csv=await csvDownload;await csv.saveAs(path.join(out,'candidates.csv'));
    const text=fs.readFileSync(path.join(out,'candidates.csv'),'utf8');assert.ok(text.startsWith('link_mm,q_start_deg'));
    assert.equal(text.trim().split('\n').length,model.sweep(model.defaultSweep()).rows.length+1);
    const jsonDownload=page.waitForEvent('download');await page.locator('#ls-save').click();
    const json=await jsonDownload;const jsonPath=path.join(out,'config.json');await json.saveAs(jsonPath);
    await set('diameter',300);await page.locator('#ls-import').setInputFiles(jsonPath);
    await page.waitForFunction(()=>document.getElementById('ls-diameter').value==='400');
    assert.equal(await page.locator('#ls-export').isDisabled(),false);
    await page.reload();await page.locator('#ls-rows tr').first().waitFor();assert.equal(await page.locator('#ls-diameter').inputValue(),'400');
    await page.locator('#ls-length-plot').evaluate(async node=>Plotly.relayout(node,{'xaxis.range':[100,300]}));
    assert.deepEqual(await page.locator('#ls-length-plot').evaluate(node=>node.layout.xaxis.range),[100,300]);
    await page.evaluate(()=>window.postMessage({type:'motion-lab-theme',theme:'dark'},location.origin));
    await page.waitForFunction(()=>document.documentElement.dataset.theme==='dark');
    assert.equal(await page.locator('#ls-curve').evaluate(n=>n.layout.paper_bgcolor),'transparent');
    await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
    await page.setViewportSize({width:360,height:900});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    assert.equal(await page.locator('#ls-diagram').evaluate(n=>/NaN|Infinity/.test(n.innerHTML)),false);
    await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
    await page.setViewportSize({width:1280,height:1000});
    // Verify actual Motion Lab navigation and change-unit memory survives a study switch.
    await page.goto('http://127.0.0.1:4186/?tab=studies&study=ratio');
    const frame=page.frameLocator('#studies-host iframe');await frame.locator('#ls-rows tr').first().waitFor();
    await frame.locator('#ls-start-unit').selectOption('deg');
    const savedStart=await frame.locator('#ls-start').inputValue();
    await frame.locator('#ls-run').click();
    await page.locator('#study-select').selectOption('linear');
    await page.locator('#study-select').selectOption('ratio');
    await frame.locator('#ls-start-unit').waitFor();
    assert.equal(await frame.locator('#ls-start-unit').inputValue(),'deg');
    assert.ok(Math.abs(Number(await frame.locator('#ls-start').inputValue())-Number(savedStart))<1e-7);
    assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    console.log('PASS: sizing controls/conversions, diameter/radius/ROM, both coordinates/averages, objectives/selection/clearance, infeasibility, JSON/CSV, refresh/study memory, Plotly zoom/dark, 360px layout, offline assets and no browser errors.');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
