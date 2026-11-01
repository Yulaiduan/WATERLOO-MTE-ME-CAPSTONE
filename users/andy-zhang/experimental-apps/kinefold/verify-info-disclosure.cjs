/** Check native info controls in an isolated Chromium DOM, without an app server.
 * Run node verify-info-disclosure.cjs --playwright PATH_TO_PLAYWRIGHT_CORE
 *   --browser PATH_TO_CHROMIUM. Uses existing developer-installed runtimes.
 * Inputs inline explanation/status/control fixtures; no physical units.
 * Outputs assertions for preservation, native keyboard behavior, observer updates
 * and guard promotion. No profile/network writes, model or full-app visual proof.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const option=name=>{const i=process.argv.indexOf(name);if(i<0||!process.argv[i+1])throw Error('Required '+name+' PATH');return process.argv[i+1];};
const {chromium}=require(path.resolve(option('--playwright')));let browser,checks=0;
const ok=(value,message)=>{assert.ok(value,message);checks++;};
(async()=>{try{
 browser=await chromium.launch({headless:true,executablePath:path.resolve(option('--browser'))});
 const page=await browser.newPage({viewport:{width:390,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.setContent(`<main><section id="builder"><h2>Builder</h2><div id="adjacent"><p id="first" class="hint">Spring explanation <a href="#fixture" id="old-link">Read more</a>.</p><p id="second" class="hint">Another explanation.</p></div><p id="critical" class="hint notice error">Invalid geometry: fix radius.</p><p id="status" class="hint" role="status">Running 3 of 6</p><p id="controls" class="hint">Keep this action <button id="action">Apply</button></p><label id="label">Length · mm<input value="300"></label><div id="late"><p id="late-note" class="hint"></p></div><section class="energy-input-card"><p data-energy-handoff>Physical torque 42 N·m</p><p id="definition">Drop height is measured from the wheel.</p></section><section data-energy-equations><h3>Equations below</h3><p class="hint" id="bottom">Full derivation remains here.</p><table id="numbers"><tr><td>42</td></tr></table></section><details class="solver-settings" open><summary>Setup</summary><details open><summary>Input</summary><p id="input-help">Transition defines smooth edges.</p></details></details><div class="js-plotly-plot"><p class="hint" id="plot-internal">Plot module text</p></div></section><section id="conventions"><p class="hint" id="reference">Full variable definitions.</p></section></main>`);
 await page.evaluate(()=>{window.original=document.querySelector('#first');window.linkClicks=0;document.querySelector('#old-link').addEventListener('click',()=>window.linkClicks++);});
 await page.addStyleTag({content:fs.readFileSync(path.join(__dirname,'info-disclosure.css'),'utf8')});
 await page.addScriptTag({content:fs.readFileSync(path.join(__dirname,'info-disclosure.js'),'utf8')});
 await page.waitForSelector('.info-disclosure');
 ok(await page.locator('#adjacent>.info-disclosure').count()===1,'Adjacent help grouped under one icon');
 ok(await page.locator('#adjacent .info-body>#first').count()===1&&await page.locator('#adjacent .info-body>#second').count()===1,'Original paragraphs retained');
 ok(await page.evaluate(()=>window.original===document.querySelector('#first')),'Original node identity retained');
 ok(!await page.locator('#first').isVisible(),'Explanatory prose initially hidden');
 for(const id of ['critical','status','controls','label','reference','bottom','numbers','plot-internal'])ok(await page.locator('#'+id).isVisible(),id+' remains visible');
 ok(!await page.locator('[data-energy-handoff]').evaluate(n=>n.closest('.info-disclosure')),'Current physical handoff numbers untouched');
 ok(await page.locator('#definition').evaluate(n=>!!n.closest('.info-disclosure')),'Known card definition collapses');
 ok(await page.locator('#input-help').evaluate(n=>!!n.closest('.info-disclosure')),'Open settings explanation collapses');
 const summary=page.locator('#adjacent>.info-disclosure>.info-summary');await summary.focus();await page.keyboard.press('Enter');await page.waitForFunction(()=>document.querySelector('#adjacent>.info-disclosure').open);
 ok(await page.locator('#first').isVisible(),'Enter opens native details');await page.waitForFunction(()=>document.querySelector('#adjacent .info-summary').getAttribute('aria-expanded')==='true');checks++;
 await page.locator('#old-link').click();ok(await page.evaluate(()=>window.linkClicks===1),'Existing descendant listener retained');
 await page.locator('#old-link').focus();await page.keyboard.press('Escape');ok(!await page.locator('#first').isVisible(),'Escape closes help');ok(await summary.evaluate(n=>document.activeElement===n),'Escape restores info focus');
 await page.keyboard.press('Space');await page.waitForFunction(()=>document.querySelector('#adjacent>.info-disclosure').open);checks++;
 await page.evaluate(()=>document.querySelector('#late-note').textContent='A newly rendered explanation.');await page.waitForFunction(()=>!!document.querySelector('#late-note').closest('.info-disclosure'));
 ok(!await page.locator('#late-note').isVisible(),'Observer handles previously empty help');
 await page.evaluate(()=>document.querySelector('#late-note').textContent='Updated explanation, same element.');
 ok(await page.locator('#late .info-disclosure').count()===1,'Updates do not nest wrappers');
 await page.evaluate(()=>{const n=document.querySelector('#late-note');n.textContent='Invalid radius';n.classList.add('notice','error');});await page.waitForFunction(()=>!document.querySelector('#late-note').closest('.info-disclosure'));
 ok(await page.locator('#late-note').isVisible(),'Help promoted to visible when it becomes an error');
 await page.evaluate(()=>{const n=document.createElement('p');n.id='gains-action';n.className='hint';n.textContent='Initially help';document.querySelector('#late').append(n);});await page.waitForFunction(()=>!!document.querySelector('#gains-action').closest('.info-disclosure'));
 await page.evaluate(()=>{const button=document.createElement('button');button.id='new-action';button.textContent='Retry';document.querySelector('#gains-action').append(button);});await page.waitForFunction(()=>!document.querySelector('#gains-action').closest('.info-disclosure'));
 ok(await page.locator('#new-action').isVisible(),'New actions are never trapped in collapsed help');
 const count=await page.locator('.info-disclosure').count();await page.evaluate(()=>{KinefoldInfoDisclosure.enhance(document);KinefoldInfoDisclosure.enhance(document);});ok(await page.locator('.info-disclosure').count()===count,'Repeated enhancement is idempotent');
 ok(await page.locator('.info-disclosure .info-disclosure').count()===0,'No nested info disclosures');
 ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Phone width has no overflow');
 ok(errors.length===0,'No browser errors');
 console.log('PASS '+checks+' native info-disclosure browser assertions; no app server or profile writes.');
}finally{await browser?.close();}})().catch(error=>{console.error(error.stack);process.exitCode=1;});
