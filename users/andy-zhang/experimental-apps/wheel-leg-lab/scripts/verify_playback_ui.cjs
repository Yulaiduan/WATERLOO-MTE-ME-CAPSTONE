/** Guard smooth recorded playback without changing solver sampling or chart data.
 * Run: node scripts/verify_playback_ui.cjs with Motion Lab on loopback4186.
 * Inputs: actual default/replacement six-second SI runs; outputs: ignored JSON.
 * Checks expensive redraw count, wall-clock playback, cursor coordinates, zoom,
 * export and exact pause/end behavior. Headless timing is not remote-device FPS.
 */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1000}}),errors=[],evidence=[];
  page.on('pageerror',e=>errors.push(e.message));
  for(const [name,route] of [['default','/api/defaults'],['replacement','/api/suspension-architecture/defaults']]){
   const c=await(await page.request.get('http://127.0.0.1:4186'+route)).json();
   const response=await page.request.post('http://127.0.0.1:4186/api/simulate',{data:c});assert.equal(response.status(),200);const run=await response.json();
   await page.goto('http://127.0.0.1:4186/physics/?loadOnly=1');await page.locator('#mechanism[data-mode="setup-preview"]').waitFor();
   await page.evaluate(run=>window.postMessage({type:'motion-lab-load-result',result:run},location.origin),run);
   await page.locator('#status').filter({hasText:'Recorded'}).waitFor();await page.waitForFunction(()=>[...document.querySelectorAll('.chart')].every(n=>n._fullLayout?.shapes?.[0]));
   await page.evaluate(()=>{window.playbackProbe={relayouts:0,intervals:[]};const original=Plotly.relayout;Plotly.relayout=function(...args){window.playbackProbe.relayouts++;return original.apply(this,args);};let last=0;function sample(t){if(window.playbackProbe.stopped)return;if(last)window.playbackProbe.intervals.push(t-last);last=t;requestAnimationFrame(sample);}requestAnimationFrame(sample);});
   await page.locator('#play').click();await page.waitForTimeout(900);await page.locator('#play').click();
   const measured=await page.evaluate(()=>{window.playbackProbe.stopped=true;return {...window.playbackProbe,time:Number(document.querySelector('#time').value)};});
   assert.equal(measured.relayouts,0,'Playback must not repeatedly recalculate all Plotly charts');assert.ok(measured.time>.6&&measured.time<1.3);
   const scrub=async t=>page.locator('#time').evaluate((n,t)=>{n.value=t;n.dispatchEvent(new Event('input',{bubbles:true}));},t);
   await scrub(1.5);
   const checks=await page.locator('.chart').evaluateAll(nodes=>nodes.map(n=>{const f=n._fullLayout,s=f.shapes[0],p=n.querySelector('.shapelayer path[data-index="0"]'),v=p.getAttribute('d').match(/[-+]?\d*\.?\d+(?:e[-+]?\d+)?/gi).map(Number);return {x:s.x0,stored:n.layout.shapes[0].x0,error:Math.abs(v[0]-(f.xaxis._offset+f.xaxis.d2p(s.x0))),yError:Math.abs(v[1]-(f.yaxis._offset+f.yaxis._length))};}));
   assert.ok(checks.every(c=>c.error<1e-7&&c.yError<1e-7&&c.x===c.stored));assert.equal(checks[0].x,1.5);
   assert.ok((await page.locator('#pose-values').textContent()).includes(run.rows.find(r=>Math.abs(r.t-1.5)<1e-9).theta_deg.toFixed(1)));
   await page.locator('.chart').first().evaluate(n=>Plotly.relayout(n,{'xaxis.range':[1,2]}));
   const exported=await page.locator('.chart').first().evaluate(async n=>({url:await Plotly.toImage(n,{format:'svg'}),x:n._fullLayout.shapes[0].x0,path:n.querySelector('.shapelayer path[data-index="0"]').getAttribute('d')}));
   assert.equal(exported.x,1.5);assert.ok(exported.url.startsWith('data:image/svg+xml'));
   await page.locator('html').evaluate(n=>n.dataset.theme='dark');await page.waitForFunction(()=>document.querySelector('.chart')._fullLayout.paper_bgcolor!==undefined);
   await scrub(5.9);await page.locator('#speed').selectOption('2');await page.locator('#play').click();await page.waitForFunction(()=>document.querySelector('#play').textContent==='Play');
   assert.equal(Number(await page.locator('#time').inputValue()),6);assert.ok((await page.locator('#pose-values').textContent()).includes(run.rows.at(-1).theta_deg.toFixed(1)));
   await scrub(.2);await page.locator('#play').click();await page.waitForTimeout(100);await page.evaluate(()=>window.postMessage({type:'motion-lab-deactivate'},location.origin));await page.waitForFunction(()=>document.querySelector('#play').textContent==='Play');
   const stopped=await page.locator('#time').inputValue();await page.waitForTimeout(100);assert.equal(await page.locator('#time').inputValue(),stopped);
   const sorted=measured.intervals.sort((a,b)=>a-b);evidence.push({name,recorded_rows:run.rows.length,recorded_frames:run.frames.length,plots:checks.length,relayouts_during_playback:measured.relayouts,observed_p95_ms:sorted[Math.floor(sorted.length*.95)],cursor_checks:checks});
  }
  assert.deepEqual(errors,[]);const out=path.join(__dirname,'../artifacts/playback-regression');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(evidence,null,2));
  console.log('PASS: default/replacement playback avoids Plotly redraws, tracks wall time, preserves cursor/zoom/export and exact pause/end, and pauses on tab deactivation.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
