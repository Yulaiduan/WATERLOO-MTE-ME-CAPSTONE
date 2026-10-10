// Browser/geometry validation for the portable toolkit. Run: npm run test:browser.
// Inputs are app-local studies and SI fixtures; outputs are diagnostics and ignored screenshots.
// This checks rendering, kinematics and interactions, not a terrain-contact robot.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const BASE=process.env.WHEEL_LEG_URL||'http://127.0.0.1:4186';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{channel:'msedge'}:{})});
 try{
  const page=await browser.newPage({viewport:{width:900,height:950},reducedMotion:'reduce'}),errors=[],external=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',r=>{if(r.request().url().startsWith(BASE))return r.continue();external.push(r.request().url());return r.abort();});
  for(const slug of ['linear-leg','coaxial-wheel-leg','tilted-invertible-leg','left-tilted-leg','two-position-left-leg','fixed-ratio-left-leg','leg-path-family']){
   await page.goto(`${BASE}/animations/${slug}/`);await page.locator('svg').first().waitFor();
   await page.waitForTimeout(60);assert.equal(await page.locator('path').evaluateAll(ps=>ps.some(p=>/NaN|Infinity/.test(p.getAttribute('d')||''))),false);
  }
  await page.goto(`${BASE}/animations/linear-leg/`);await page.locator('[data-play]').click();
  for(const value of [12,43,75]){
   await page.locator('#leg-angle').evaluate((n,v)=>{n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));},value);
   const dx=await page.locator('#linear-leg-motion').evaluate(r=>Number(r.querySelector('[data-foot]').getAttribute('cx'))-Number(r.querySelector('[data-base]').getAttribute('cx')));assert.equal(dx,0);
  }
  await page.goto(`${BASE}/animations/leg-path-family/`);await page.locator('path.wheel-path').first().waitFor({state:'attached'});
  await page.locator('#leg-path-family').evaluate(r=>r.dispatchEvent(new CustomEvent('family:settings',{detail:{lambda:1,ratio:2,theta:55}})));
  const family=await page.locator('svg.family-chart').evaluateAll(xs=>xs.map(s=>({R:+s.dataset.ratio,L:+s.dataset.lengthRatio,x:+s.dataset.currentX,y:+s.dataset.currentY})));
  assert.equal(family.length,6);for(const p of family){const q=55*Math.PI/180;assert.ok(Math.abs(p.x-250*(Math.sin(q)-p.L*Math.sin((p.R-1)*q)))<1e-8);}
  await page.goto(`${BASE}/animations/fixed-ratio-left-leg/`);let worst=0;
  for(const mode of ['lower','upper'])for(let i=0;i<=40;i++){
   const center=mode==='lower'?26.395687229702627:180-26.395687229702627;
   await page.locator('#fixed-ratio-left-leg').evaluate((r,d)=>r.dispatchEvent(new CustomEvent('leg:pose',{detail:d})),{mode,theta:center-2+i/10});
   const pose=await page.locator('#fixed-ratio-left-leg').evaluate(r=>{const p=n=>{const e=r.querySelector('[data-'+n+']');return[+e.getAttribute('cx'),+e.getAttribute('cy')];};const A=p('hip'),B=p('small'),C=p('wheel'),s=Math.hypot(B[0]-A[0],B[1]-A[1])/250;return{x:(C[0]-A[0])/s,y:(C[1]-A[1])/s};});
   const error=Math.abs(pose.x+Math.tan(12*Math.PI/180)*Math.abs(pose.y))/Math.sqrt(1+Math.tan(12*Math.PI/180)**2);worst=Math.max(worst,error);assert.ok(error<.768);
  }
  await page.goto(`${BASE}/force-plots/`);await page.locator('#wl-summary tr').nth(2).waitFor();assert.ok((await page.locator('#wl-summary tr').nth(1).textContent()).includes('273 mm'));
  await page.goto(`${BASE}/linkage/`);await page.locator('#app').waitFor();assert.ok((await page.locator('body').textContent()).includes('Linkage simulator'));
  await page.goto(`${BASE}/recorded/`);await page.locator('#pm-state').waitFor();assert.ok((await page.locator('#pm-state').textContent()).includes('kgf'));
  await page.locator('#pm-time').evaluate(n=>{n.value=.6;n.dispatchEvent(new Event('input',{bubbles:true}));});assert.equal(await page.locator('.pm-disturbance-arrow').count(),1);
  for(const width of [900,360]){await page.setViewportSize({width,height:1100});await page.waitForTimeout(80);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));}
  const out=path.join(__dirname,'../artifacts');fs.mkdirSync(out,{recursive:true});await page.screenshot({path:path.join(out,'portable-recorded-preview.png'),fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log(`PASS: seven offline motion studies, straight-line and path-family coordinates, fixed 4:1 error ${worst.toFixed(3)} mm, force calculator, detailed bench, recorded disturbance and mobile layout.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
