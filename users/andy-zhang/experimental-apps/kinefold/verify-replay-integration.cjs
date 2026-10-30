/** Check saved-case handoff, mirror tabs and exact synchronized animations.
 * Run node verify-replay-integration.cjs --bundle FILE --bundle FILE --bundle FILE
 * using replay API responses for landing/jump/terrain (world mm/deg, SI time).
 * Outputs assertions; uses actual captured SVG frames with a deterministic DOM
 * and clock. No GUI/browser, server, physics or active design write is performed.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let count=0;const ok=(v,n)=>{assert.ok(v,n);count++;},eq=(a,b,n)=>{assert.equal(a,b,n);count++;};
const bundles={};for(let i=2;i<process.argv.length;i++)if(process.argv[i]==='--bundle'){const raw=JSON.parse(fs.readFileSync(process.argv[++i],'utf8'));const b=raw.bundle||raw;bundles[b.kind]=b;}
assert.ok(['landing','jump','terrain'].every(k=>bundles[k]),'Supply actual landing, jump and terrain replay API response files.');
const clone=v=>JSON.parse(JSON.stringify(v)),decode=s=>s.replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
class Element{
  constructor(tag='div',attrs={}){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.children=[];this.parentNode=null;this.hidden='hidden'in attrs;this.dataset={};this.listeners={};this._text='';this._value=attrs.value;for(const[k,v]of Object.entries(attrs))if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v;this.classList={add:(...x)=>{this.attrs.class=[this.attrs.class||'',...x].join(' ');}};}
  get firstChild(){return this.children[0]||null;}
  get isConnected(){return !!this.parentNode;}
  set innerHTML(html){for(const c of this.children)c.parentNode=null;this.children=[];this._html=String(html);this._text='';const stack=[this];for(const token of this._html.match(/<[^>]*>|[^<]+/g)||[]){if(token.startsWith('</')){if(stack.length>1)stack.pop();continue;}if(token.startsWith('<')){const tag=token.match(/^<([\w-]+)/)?.[1];if(!tag)continue;const attrs={};for(const m of token.slice(tag.length+1,-1).matchAll(/([\w-]+)(?:="([^"]*)"|='([^']*)'|=([^\s>]+))?/g))attrs[m[1]]=decode(m[2]??m[3]??m[4]??'');const c=new Element(tag,attrs);stack.at(-1).append(c);if(!['input','br','hr','img'].includes(tag)&&!token.endsWith('/>'))stack.push(c);}else stack.at(-1)._text+=decode(token);}}
  get innerHTML(){return this._html||'';}
  get textContent(){return this._text+this.children.map(c=>c.textContent).join('');}set textContent(v){this._text=String(v);this.innerHTML='';this._text=String(v);}
  get value(){if(this.tagName==='SELECT')return this._value??this.querySelectorAll('option').find(x=>'selected'in x.attrs)?.value??this.querySelector('option')?.value??'';return this._value??this.attrs.value??'';}set value(v){this._value=String(v);}
  append(...nodes){for(const c of nodes){if(c.parentNode)c.parentNode.children=c.parentNode.children.filter(x=>x!==c);c.parentNode=this;this.children.push(c);}}
  insertAdjacentHTML(_,html){const t=new Element();t.innerHTML=html;this.append(...t.children);}
  matches(s){if(s.startsWith('.'))return(this.attrs.class||'').split(' ').includes(s.slice(1));if(s==='[hidden]')return this.hidden;const m=s.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);if(m){const key=m[1].startsWith('data-')?m[1].slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase()):null,v=key&&key in this.dataset?this.dataset[key]:this.attrs[m[1]];return m[2]===undefined?v!==undefined:v===m[2];}return this.tagName.toLowerCase()===s;}
  closest(s){for(let n=this;n;n=n.parentNode)if(n.matches(s))return n;return null;}
  querySelectorAll(s){const result=[],walk=n=>{for(const c of n.children){if(c.matches(s))result.push(c);walk(c);}};walk(this);return result;}querySelector(s){return this.querySelectorAll(s)[0]||null;}
  setAttribute(k,v){this.attrs[k]=String(v);}addEventListener(k,f){(this.listeners[k]??=[]).push(f);}removeEventListener(k,f){this.listeners[k]=(this.listeners[k]||[]).filter(x=>x!==f);}
}
let wall=0,seq=0,writes=0,pauseCount=0;const raf=new Map(),timers=new Map(),events=new Map(),plots=[];
const body=new Element(),panels=Object.fromEntries(['actuator','analytical','pymunk'].map(k=>[k,new Element('section',{id:k})]));
for(const [k,p]of Object.entries(panels)){body.append(p);p.hidden=k!=='actuator';if(k!=='actuator')p.innerHTML='<div data-live-sentinel="'+k+'">Original live controls</div>';}
const host=new Element();panels.actuator.append(host);
const studio={showTab(id){for(const [k,p]of Object.entries(panels))p.hidden=k!==id;for(const fn of events.get('kinefold-solver-tab')||[])fn({detail:{id}});},saveArtifact:async()=>{},setMotorConfig(){writes++;},setCaseConfig(){writes++;},setSolverConfig(){writes++;},applySnapshot(){writes++;}};
const context=vm.createContext({console,document:{getElementById:id=>panels[id],createElement:tag=>new Element(tag)},performance:{now:()=>wall},requestAnimationFrame:fn=>{raf.set(++seq,fn);return seq;},cancelAnimationFrame:id=>raf.delete(id),setTimeout:fn=>{timers.set(++seq,fn);return seq;},clearTimeout:id=>timers.delete(id),Event:class{constructor(type){this.type=type;}},addEventListener:(name,fn)=>events.set(name,[...(events.get(name)||[]),fn]),dispatchEvent:event=>{for(const fn of events.get(event.type)||[])fn(event);},KinefoldStudio:studio,KinefoldLiveDynamics:{pauseAll(){pauseCount++;}},KinefoldPlotly:{purge(){},resizeAll(){},react:async(node,traces,layout)=>plots.push({node,traces,layout}),cursor(){}}});
for(const name of ['reference-v4.js','model.js','preview-geometry.js','contact-render.js','comparison-replay.js','automatic-comparison.js','comparison-replay-bridge.js'])vm.runInContext(fs.readFileSync(name,'utf8'),context,{filename:name});
const bridge=context.KinefoldComparisonReplayBridge,requests=[];let missingTerrain=false,jobState='running',deferredLanding=null;
const request=async b=>{requests.push(clone(b));if(b.action==='replay'){if(b.kind==='landing'&&deferredLanding)return deferredLanding.promise;return missingTerrain&&b.kind==='terrain'?{ok:true,ready:false,missing:['analytical','pymunk']}:{ok:true,ready:true,bundle:clone(bundles[b.kind])};}if(b.action==='run-replay')return {ok:true,ready:false,replayJob:{id:'c'.repeat(32),state:'running'}};if(b.action==='replay-status')return {ok:true,replayJob:{id:'c'.repeat(32),state:jobState,message:'Captured input still running'}};if(b.action==='replay-result')return {ok:true,ready:true,replayJob:{id:'c'.repeat(32),state:'complete'},bundle:clone(bundles.terrain)};if(b.action==='replay-cancel')return {ok:true,replayJob:{state:'cancelled'}};throw Error('Unexpected integration API '+b.action);};
const settle=async()=>{for(let i=0;i<14;i++)await Promise.resolve();},step=ms=>{wall+=ms;const tasks=[...raf.values()];raf.clear();tasks.forEach(fn=>fn(wall));};
const before=JSON.stringify(bundles),source=bundles.landing;
(async()=>{
 const ui=bridge.mount(host,{request,studio,jobId:source.originalJobId,candidateId:source.candidateId});await ui.ready;
 ok(ui.getState().ready,'Cached landing opens a complete pair');eq(requests[0].jobId,source.originalJobId,'Original saved job used');eq(requests[0].candidateId,source.candidateId,'Exact selected SKU pair used');eq(raf.size,0,'No autoplay');
 bridge.openInTab('analytical');const a=panels.analytical.querySelector('[data-replay-svg="analytical"]');ok(a&&a.innerHTML.includes('ACTUAL CONTACT'),'Analytical tab renders actual captured mechanism');eq(panels.analytical.querySelector('[data-live-dynamics]').hidden,true,'Live inputs hidden while captured replay shown');
 bridge.openInTab('pymunk');const p=panels.pymunk.querySelector('[data-replay-svg="pymunk"]');ok(p&&p.innerHTML.includes('ACTUAL CONTACT'),'Pymunk tab renders actual native mechanism');
 const c=bridge.getController();c.play();step(720);eq(c.getState().time,.72,'Shared clock advances');const nativeTime=c.getState().engines.pymunk.t;eq(Number(p.dataset.time),nativeTime,'Native mirror uses exact saved sample');bridge.openInTab('analytical');ok(c.getState().playing,'Switching engine tabs preserves the shared playing clock');eq(Number(a.dataset.time),c.getState().engines.analytical.t,'Analytical mirror refreshes when shown');
 c.seek(.74);eq(Number(a.dataset.time),c.getState().engines.analytical.t,'Scrub updates the visible analytical frame');ui.showPair();const pair=host.querySelector('[data-replay-svg="pymunk"]');eq(Number(pair.dataset.time),c.getState().engines.pymunk.t,'Pair view resumes the exact same clock');
 for(const kind of ['jump','terrain']){await ui.selectCase(kind);const cc=bridge.getController();eq(cc.getBundle().kind,kind,'Selected saved case '+kind);eq(cc.getState().time,0,'Case switch resets only playback clock');cc.seek(kind==='terrain'?2:.35);bridge.openInTab('pymunk');const frame=cc.render('pymunk');eq(Number(panels.pymunk.querySelector('[data-replay-svg="pymunk"]').dataset.time),frame.sampleTimeS,'Saved '+kind+' native frame shown');ok(frame.html.includes('Spring')||frame.html.includes('spring'),'Saved spring rendering retained');if(kind==='terrain'){ok(frame.frame.terrainOffsetMm.some(v=>v!==0),'Terrain moves horizontally in actual frames');ok(Math.abs(frame.frame.wheelAngle)>0,'Actual friction-driven wheel rotation retained');}}
 const plotGroup=panels.pymunk.querySelector('[data-captured-plots]');plotGroup.open=true;for(const fn of plotGroup.listeners.toggle||[])fn();ok(plots.length>0,'Captured case plots are available beside replay');ok(plots.every(x=>x.traces.every(t=>t.type==='scatter')),'Captured plots use offline Plotly BASIC');
 bridge.showLive();eq(panels.pymunk.querySelector('[data-live-dynamics]').hidden,false,'Return restores live inputs');ok(panels.pymunk.querySelector('[data-live-sentinel="pymunk"]'),'Original live controls preserved');
 missingTerrain=true;await ui.selectCase('terrain');eq(ui.getState().ready,false,'Missing pair is not animated as a fake result');ok(host.textContent.includes('no complete saved engine pair'),'Missing pair message');await ui.run();ok(ui.isBusy(),'On-demand work remains explicit');eq(requests.find(x=>x.action==='run-replay').kind,'terrain','Only selected case requested');jobState='complete';const tasks=[...timers.values()];timers.clear();tasks.forEach(fn=>fn());await settle();ok(ui.getState().ready,'Completed on-demand pair connects to player');eq(bridge.getController().getBundle().kind,'terrain','On-demand result keeps captured case');
 let resolve;deferredLanding={promise:new Promise(r=>resolve=r)};const slow=ui.selectCase('landing');await ui.selectCase('jump');resolve({ok:true,ready:true,bundle:clone(bundles.landing)});await slow;eq(bridge.getController().getBundle().kind,'jump','Late older response cannot replace selected jump');
 ui.destroy();eq(bridge.getController(),null,'Destroy removes every playback owner');eq(raf.size,0,'No animation callback leak');eq(timers.size,0,'No polling callback leak');eq(writes,0,'Captured replay never changes Studio settings');eq(JSON.stringify(bundles),before,'All original saved settings/results remain byte-identical as objects');ok(pauseCount>0,'Live playback paused when entering captured views');
 let resumeState='running',monitorFailure=false;
 const resumeRequest=async b=>{
  if(b.action==='replay')return {ok:true,ready:false,replayJob:{id:'d'.repeat(32),state:'running'}};
  if(b.action==='replay-status'){if(monitorFailure)throw Error('Temporary monitor interruption');return {ok:true,replayJob:{id:'d'.repeat(32),state:resumeState}};}
  if(b.action==='replay-result')return {ok:true,ready:true,bundle:clone(bundles.landing)};
  if(b.action==='replay-cancel')return {ok:true,replayJob:{state:'cancelled'}};
  throw Error('Refresh must monitor the retained case without starting a second worker');
 };
 const resumed=bridge.mount(host,{request:resumeRequest,studio,jobId:source.originalJobId,candidateId:source.candidateId});await resumed.ready;
 ok(resumed.isBusy(),'Reopening a running captured case resumes its existing worker');eq(resumed.getState().replayId,'d'.repeat(32),'Retained owned replay ID reused');
 resumeState='complete';const pending=[...timers.values()];timers.clear();pending.forEach(fn=>fn());await settle();ok(resumed.getState().ready,'Retained case completion reconnects exact frames');
 monitorFailure=true;await resumed.selectCase('terrain');ok(resumed.isBusy(),'Monitor error does not falsely mark a running worker idle');ok(host.textContent.includes('Monitoring paused'),'Monitor interruption is visible');eq(host.querySelector('[data-case-cancel]').hidden,false,'Cancel remains reachable after monitor error');
 await resumed.cancel();eq(resumed.isBusy(),false,'Explicit cancellation releases the retained job');resumed.destroy();eq(timers.size,0,'Resumed monitor teardown leaves no timer');
 console.log('PASS '+count+' exact saved-case handoff/mirror/clock/API/Plotly assertions with actual frame bundles; DOM fixture, no live browser QA.');
})().catch(error=>{console.error(error);process.exitCode=1;});
