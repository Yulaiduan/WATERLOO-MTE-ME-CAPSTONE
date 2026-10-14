/* Verify the frozen offline report through a real installed browser.
 * Invocation: node scripts/verify_offline_report.cjs [--report absolute/index.html].
 * Inputs: static HTML, local companion PDF/JSON, optional PLAYWRIGHT_MODULE_PATH
 * and BROWSER_EXECUTABLE_PATH; Node22 and Playwright from the sibling Wheel Leg Lab.
 * Outputs: assertions and temporary screenshots/print-PDF outside the repository.
 * Limits: file:// rendering, link/data parity and print-layout checks; does not
 * rerun analytical optimization or certify mechanics, hardware or canonical physics.
 */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {pathToFileURL,fileURLToPath}=require('node:url');
const assert=require('node:assert/strict');
const ownRoot=path.resolve(__dirname,'..');
const reportPath=process.argv.includes('--report')?path.resolve(process.argv[process.argv.indexOf('--report')+1]):path.join(ownRoot,'index.html');
const reportRoot=path.dirname(reportPath);
let playwright;
for(const name of [process.env.PLAYWRIGHT_MODULE_PATH,'playwright',path.resolve(reportRoot,'../wheel-leg-lab/node_modules/playwright')].filter(Boolean)){
  try{playwright=require(name);break;}catch{}
}
if(!playwright)throw Error('Playwright not found. Install the sibling Wheel Leg Lab dependencies or set PLAYWRIGHT_MODULE_PATH.');
async function launch(){
  if(process.env.BROWSER_EXECUTABLE_PATH)return playwright.chromium.launch({headless:true,executablePath:process.env.BROWSER_EXECUTABLE_PATH});
  const errors=[];for(const options of [{channel:'msedge'},{channel:'chrome'},{}])try{return await playwright.chromium.launch({headless:true,...options});}catch(e){errors.push(e.message);}
  throw Error('No supported installed browser available. Set BROWSER_EXECUTABLE_PATH. '+errors.join('\n'));
}
(async()=>{
  const html=fs.readFileSync(reportPath,'utf8'),out=fs.mkdtempSync(path.join(os.tmpdir(),'camel-offline-report-'));
  assert.ok(!/<(?:script|link|img|iframe)[^>]+(?:src|href)=/i.test(html),'Report must not load external assets or frames.');
  assert.ok(!/\b(?:fetch\s*\(|new\s+Worker|XMLHttpRequest|importScripts|WebSocket)\b/.test(html),'No runtime/network model controls.');
  const browser=await launch();
  try{
    const errors=[],requests=[];
    const context=await browser.newContext({viewport:{width:1440,height:1000},javaScriptEnabled:false});
    const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
    const url=pathToFileURL(reportPath).href;await page.goto(url);
    assert.equal(await page.locator('section').count(),12);assert.equal(await page.locator('svg').count(),22);
    assert.equal(await page.locator('input,select,textarea,iframe').count(),0);
    assert.equal(await page.locator('button').count(),1);assert.equal(await page.locator('#print-report').textContent(),'Print report');
    const evidence=JSON.parse(await page.locator('#report-evidence').textContent());
    assert.equal(evidence.schema,'camel/generalized-leg-report-evidence/v1');
    assert.ok(evidence.physics.delivery_sha256,'Final relocation metadata must be retained.');
    const central=evidence.analytical.cases.find(c=>c.id==='325_peak');
    assert.equal(central.config.L2,180);assert.equal(central.config.L3,340);assert.equal(central.profile.metrics.totalTravel,325);
    const text=await page.locator('body').innerText();assert.ok(!/\{F\(|undefined|NaN/.test(text),'No unresolved interpolation or invalid numbers.');
    assert.match(text,/46\.260 Nm peak.*41\.089 Nm RMS/);
    assert.match(text,/6\.449 Nm peak.*3\.641 Nm RMS/);
    assert.match(text,/IMPOSSIBLE/);assert.match(text,/52\.642261°.*13\.389732°/);
    assert.equal(await page.locator('#six-cases tbody tr').count(),6);
    assert.equal(await page.locator('#pareto-table tbody tr').count(),16);
    assert.equal(await page.locator('#spring-table tbody tr').count(),9);
    assert.equal(await page.locator('#engine-checks tbody tr').count(),9);
    const checks=await page.locator('#engine-checks tbody tr').allTextContents();assert.ok(checks.every(t=>t.includes('PASS')));
    const displayedCases=await page.locator('#six-cases tbody tr').evaluateAll(rows=>rows.map(row=>[...row.cells].map(c=>c.textContent)));
    evidence.analytical.cases.slice(0,6).forEach((c,i)=>{
      assert.equal(Number(displayedCases[i][5]),Number(c.profile.metrics.peak.toFixed(3)));
      assert.equal(Number(displayedCases[i][6]),Number(c.profile.metrics.rms.toFixed(3)));
    });
    assert.equal(await page.locator('svg').evaluateAll(nodes=>nodes.every(n=>!/(?:NaN|undefined|Infinity)/.test(n.outerHTML))),true);
    await page.screenshot({path:path.join(out,'desktop.png')});
    await page.locator('#profiles').screenshot({path:path.join(out,'individual-profiles.png')});
    await page.locator('#suspensions').screenshot({path:path.join(out,'suspensions.png')});
    await page.locator('.toc a[href="#motion"]').click();assert.equal(new URL(page.url()).hash,'#motion');
    await page.setViewportSize({width:390,height:844});await page.locator('body').evaluate(()=>scrollTo(0,0));
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile page must not overflow its viewport.');
    await page.screenshot({path:path.join(out,'mobile.png')});
    assert.deepEqual(errors,[]);assert.deepEqual(requests,[url],'Reading with JS disabled must load only the local HTML.');
    const pdfURL=await page.locator('#pdf-link').evaluate(a=>a.href);
    assert.equal(new URL(pdfURL).protocol,'file:');const pdfPath=fileURLToPath(pdfURL);assert.equal(path.relative(reportRoot,pdfPath).split(path.sep).join('/'),'docs/generalized-leg-report.pdf');
    const pdfBytes=fs.readFileSync(pdfPath);assert.equal(pdfBytes.subarray(0,5).toString(),'%PDF-');assert.ok(pdfBytes.length>10000);
    const jsonPath=path.join(reportRoot,'docs/generalized-leg-report-data.json');const original=JSON.parse(fs.readFileSync(jsonPath,'utf8'));assert.deepEqual(evidence,original,'Embedded evidence must match the finalized compact JSON.');
    await context.close();
    const enabled=await browser.newContext({viewport:{width:1440,height:1000}}),active=await enabled.newPage(),enabledRequests=[];
    active.on('pageerror',e=>errors.push(e.message));active.on('request',r=>enabledRequests.push(r.url()));await active.goto(url);
    await active.evaluate(()=>{window.__printCalls=0;window.print=()=>window.__printCalls++;});await active.locator('#print-report').click();assert.equal(await active.evaluate(()=>window.__printCalls),1);
    await active.emulateMedia({media:'print'});assert.equal(await active.locator('.toc').isVisible(),false);assert.equal(await active.locator('#print-report').isVisible(),false);assert.equal(await active.locator('#motion').isVisible(),true);
    await active.pdf({path:path.join(out,'print-check.pdf'),preferCSSPageSize:true,printBackground:true});
    assert.deepEqual(errors,[]);assert.deepEqual(enabledRequests,[url]);await enabled.close();
    console.log(JSON.stringify({passed:true,file_protocol:true,js_disabled_read:true,sections:12,embedded_svg:22,external_requests:0,pdf_bytes:pdfBytes.length,artifacts:out},null,2));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
