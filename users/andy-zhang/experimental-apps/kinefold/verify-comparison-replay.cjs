/** Verify shared replay clocks, capture guards and actual contact SVG playback.
 * Run node verify-comparison-replay.cjs [--bundle captured-api-response.json ...].
 * Inputs synthetic SI-second/world-mm/degree trajectories and optional actual
 * saved engine bundles. Outputs assertion counts; DOM/clock fixtures never run
 * physics, open a browser/server or edit live profiles. No live UI/hardware claim.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
let count=0;const ok=(v,n)=>{assert.ok(v,n);count++;},same=(a,b,n)=>{assert.equal(a,b,n);count++;},clone=v=>JSON.parse(JSON.stringify(v));
const context=vm.createContext({console});
for(const name of ['reference-v4.js','model.js','preview-geometry.js','contact-render.js','comparison-replay.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,name),'utf8'),context,{filename:name});
const Replay=context.KinefoldComparisonReplay,Drawing=context.KinefoldContactDrawing;
const project=JSON.parse(fs.readFileSync(path.join(__dirname,'saved-configurations/vsl-v45-nominal-alpha0.json'),'utf8'));
function fixture(kind='landing',nativeTimes=[0,.75,1.5,2]){
  const params=clone(project.params),motorConfig={enabled:true,gearRatio:10,rotorInertiaKgM2:.0005},actuatorConfig={ratio:10,peakShaftNm:20,forwardEfficiency:.9,reverseEfficiency:.9,minClearanceMm:50};
  const base={params,runConfig:{...project.solverConfig,inputRiseMm:0,duration:2},contactConfig:{mode:'terrain-contact',drive:'free',friction:.8,restitution:0},caseConfig:{kind:kind==='terrain'?'terrain-stability':kind,undersideOffsetMm:50},motorConfig,actuatorConfig};
  const runs={};
  for(const engine of ['analytical','pymunk']){
    const times=engine==='analytical'?[0,1,1,2]:nativeTimes;
    const frames=times.map((t,index)=>{
      const theta2=135+Math.min(30,15*t)+(engine==='analytical'&&index===1?-1:0),h=1000-200*t+(engine==='pymunk'?5:0);
      const model=context.Kinefold.evaluate({...params,theta2}),at=v=>v.map((x,i)=>x+(i===2?h:0)),wheelAngle=t*45;
      return {t,A:[0,0,h],actualA:[0,0,h],B:at(model.B),C:at(model.C),theta2,theta4:t*10,theta5:t*20,theta6:wheelAngle,wheelAngle,indexAnglesDeg:{a:0,b:theta2-100,c:t*10,d:t*10,e:t*20,f:wheelAngle},terrainOffsetMm:kind==='terrain'?[-100*t,0,0]:[0,0,0]};
    });
    const rows=frames.map(f=>({t:f.t,theta2:f.theta2,chassisZMm:f.A[2],wheelZMm:f.C[2],chassisClearanceMm:f.A[2]-50,motorTorqueNm:-100,Fs:80,wheelAngle:f.wheelAngle}));
    const payload={engine,...clone(base)},result={schema:'kinefold/contact-v2',engine,...clone(base),snapshot:{params:clone(params),solverConfig:clone(base.runConfig),contactConfig:clone(base.contactConfig),caseConfig:clone(base.caseConfig),motorConfig:clone(motorConfig),actuatorConfig:clone(actuatorConfig)},designHash:'same-captured-design',rows,frames,events:[{type:'first-contact',t:.75},{type:'compression-stop',t:1}],terrain:{polygonsMm:kind==='terrain'?[[[-200,0,0],[0,0,0],[0,0,150],[-200,0,150]]]:[],baseSegmentMm:[[-2000,0,0],[2000,0,0]]},diagnostics:{termination:'duration',finiteLinkDynamics:true}};
    runs[engine]={payload,result,assessment:{status:'fail',metrics:{}},candidateId:'motor-a__gear-b',engine,kind};
  }
  return {schema:'kinefold/comparison-replay-v1',originalJobId:'a'.repeat(32),candidateId:'motor-a__gear-b',candidate:{id:'motor-a__gear-b',motorId:'motor-a',motorName:'Saved motor',gearboxId:'gear-b',gearboxName:'Saved SO gearbox',hardware:{actuatorConfig:clone(actuatorConfig),rotorInertiaKgM2:.0005}},project:clone(project),kind,settingsHash:'b'.repeat(64),runs,warnings:[]};
}
function clock(){
  let wall=0,id=0;const tasks=new Map(),old=[];
  return {now:()=>wall,requestFrame:fn=>{tasks.set(++id,fn);old.push(fn);return id;},cancelFrame:id=>tasks.delete(id),step(ms){wall+=ms;const callbacks=[...tasks.values()];tasks.clear();callbacks.forEach(f=>f(wall));},jump(ms){wall+=ms;},pending:()=>tasks.size,oldCallbacks:old};
}
function reject(mutator,label){const b=fixture();mutator(b);assert.throws(()=>Replay.create(b),label);count++;}
class Element{
  constructor(tag='div',attrs={}){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.children=[];this.parentNode=null;this.hidden='hidden'in attrs;this.dataset={};this.listeners={};this._text='';this._value=attrs.value;for(const[k,v]of Object.entries(attrs))if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v;this.classList={add:(...x)=>{this.attrs.class=[...(this.attrs.class||'').split(' '),...x].join(' ');}};}
  set innerHTML(html){this.children=[];this._text='';this._html=String(html);const stack=[this];for(const token of this._html.match(/<[^>]*>|[^<]+/g)||[]){if(token.startsWith('</')){if(stack.length>1)stack.pop();continue;}if(token.startsWith('<')){const tag=token.match(/^<([\w-]+)/)?.[1];if(!tag)continue;const attrs={};for(const m of token.slice(tag.length+1,-1).matchAll(/([\w-]+)(?:="([^"]*)"|='([^']*)'|=([^\s>]+))?/g))attrs[m[1]]=m[2]??m[3]??m[4]??'';const child=new Element(tag,attrs);stack.at(-1).append(child);if(!['input','br','hr','img'].includes(tag)&&!token.endsWith('/>'))stack.push(child);}else stack.at(-1)._text+=token;}}
  get innerHTML(){return this._html||'';}
  get textContent(){return this._text+this.children.map(c=>c.textContent).join('');}set textContent(v){this._text=String(v);this.children=[];}
  get value(){if(this.tagName==='SELECT')return this._value??this.querySelectorAll('option').find(x=>'selected'in x.attrs)?.value??'';return this._value??this.attrs.value??'';}set value(v){this._value=String(v);}
  append(child){child.parentNode=this;this.children.push(child);}
  matches(selector){if(selector.startsWith('.'))return(this.attrs.class||'').split(' ').includes(selector.slice(1));const m=selector.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);return m?(m[2]===undefined?m[1]in this.attrs:this.attrs[m[1]]===m[2]):this.tagName.toLowerCase()===selector;}
  closest(selector){for(let n=this;n;n=n.parentNode)if(n.matches(selector))return n;return null;}
  querySelectorAll(selector){const out=[],walk=n=>{for(const c of n.children){if(c.matches(selector))out.push(c);walk(c);}};walk(this);return out;}querySelector(s){return this.querySelectorAll(s)[0]||null;}
  setAttribute(k,v){this.attrs[k]=String(v);}addEventListener(k,f){(this.listeners[k]??=[]).push(f);}removeEventListener(k,f){this.listeners[k]=(this.listeners[k]||[]).filter(x=>x!==f);}
}
// One saved capture is immutable and both independent sample grids use one clock.
const original=fixture(),before=JSON.stringify(original),timer=clock();let renderCalls=0;
const instrumented={bounds:Drawing.bounds,render(s){renderCalls++;return Drawing.render(s);}};
const controller=Replay.create(original,{...timer,drawing:instrumented});
same(controller.getState().time,0);same(controller.getState().playing,false);same(timer.pending(),0,'No autoplay');
ok(Object.isFrozen(controller.getBundle().runs.analytical.result.rows[0]),'Saved rows frozen');
original.runs.analytical.payload.params.m1=99;same(controller.getBundle().runs.analytical.payload.params.m1,8.75,'Caller mutation cannot alter capture');
const union=controller.getCamera();for(const engine of ['analytical','pymunk']){const b=Drawing.bounds(controller.getBundle().runs[engine].result,project.params);ok(union.minX<=b.minX&&union.maxX>=b.maxX&&union.minZ<=b.minZ&&union.maxZ>=b.maxZ,'Union camera contains '+engine);}
const host=new Element(),nativeHost=new Element(),analyticalHost=new Element();
const pair=Replay.mount(host,controller),native=Replay.mount(nativeHost,controller,{engines:['pymunk']}),analytical=Replay.mount(analyticalHost,controller,{engines:['analytical']});
same(renderCalls,2,'Pair and mirrors share two cached renderings');
same(host.querySelectorAll('svg').length,2);same(nativeHost.querySelectorAll('svg').length,1);same(analyticalHost.querySelectorAll('svg').length,1);
const click=(h,name)=>{const node=h.querySelector('[data-replay-action="'+name+'"]');for(const fn of h.listeners.click||[])fn({target:node});};
const input=(h,selector,value,type='input')=>{const node=h.querySelector(selector);node.value=value;for(const fn of h.listeners[type]||[])fn({target:node});};
click(host,'play');same(timer.pending(),1,'Only one RAF for all mounts');timer.step(500);
same(controller.getState().time,.5);same(host.querySelector('[data-replay-svg="analytical"]').dataset.time,'0','No between-sample interpolation');same(nativeHost.querySelector('[data-replay-svg="pymunk"]').dataset.time,'0');
timer.step(500);const state=controller.getState();same(state.timeS,1);same(state.engines.analytical.index,2,'Last duplicate timestamp preserves post-event state');same(state.engines.pymunk.index,1,'Different native sample grid preserved');
same(host.querySelector('[data-replay-svg="analytical"]').dataset.time,'1');same(analyticalHost.querySelector('[data-replay-svg="analytical"]').dataset.time,'1');same(nativeHost.querySelector('[data-replay-svg="pymunk"]').dataset.time,'0.75');
same(renderCalls,4,'Only changed exact indices are redrawn once across mirrors');
ok(host.textContent.includes('compression-stop @ 1.000'),'Actual events retained');
click(nativeHost,'play');same(controller.getState().playing,false,'Single native mirror pauses shared pair');same(timer.pending(),0);
input(analyticalHost,'[data-replay-seek]','0.999999999');same(controller.getState().engines.analytical.index,0,'Clock before an impulse never selects a future duplicate');
input(host,'[data-replay-seek]','1');same(controller.getState().engines.analytical.index,2);same(nativeHost.querySelector('[data-replay-time]').textContent,'1.000 / 2.000 s');
input(nativeHost,'[data-replay-speed]','2','change');same(controller.getState().speed,2);click(nativeHost,'play');timer.step(250);same(controller.getState().time,1.5);same(controller.getState().engines.pymunk.t,1.5);
timer.step(500);same(controller.getState().time,2);same(controller.getState().playing,false);same(timer.pending(),0);
click(host,'restart');same(controller.getState().time,0);same(controller.getState().playing,true);controller.pause();
const stale=timer.oldCallbacks.at(-1),timeAtPause=controller.getState().time;stale(99999);same(controller.getState().time,timeAtPause,'Cancelled RAF cannot advance paused state');
const n=renderCalls;controller.seek(.1);controller.seek(.2);same(renderCalls,n,'Repeated frame samples reuse SVG');
nativeHost.hidden=true;controller.seek(1.5);const hiddenTime=nativeHost.querySelector('[data-replay-svg="pymunk"]').dataset.time;nativeHost.hidden=false;native.refresh();same(nativeHost.querySelector('[data-replay-svg="pymunk"]').dataset.time,'1.5');ok(hiddenTime!=='1.5','Hidden mirror refreshes when shown');
assert.throws(()=>controller.setSpeed(NaN));count++;assert.throws(()=>controller.setSpeed(0));count++;assert.throws(()=>controller.seek(NaN));count++;
controller.seek(-10);same(controller.getState().time,0);controller.seek(999);same(controller.getState().time,2);
pair.destroy();same(host.listeners.click.length,0);same(host.innerHTML,'');controller.seek(1);same(nativeHost.querySelector('[data-replay-time]').textContent,'1.000 / 2.000 s','Destroying pair mount leaves mirrors working');
controller.play();const pending=timer.oldCallbacks.at(-1);controller.destroy();same(timer.pending(),0);pending(999999);same(controller.getState().destroyed,true);same(controller.getState().playing,false);assert.throws(()=>controller.render('analytical'));count++;ok(nativeHost.textContent.includes('replaced or closed'),'Old mirrors mark controller destroyed');native.destroy();analytical.destroy();
same(JSON.stringify({...original,runs:{...original.runs,analytical:{...original.runs.analytical,payload:{...original.runs.analytical.payload,params:{...original.runs.analytical.payload.params,m1:8.75}}}}}),before,'Replay never writes source profiles/captures');
// Unequal observation endings are shown honestly, using the final actual frame.
const shortTimer=clock(),short=Replay.create(fixture('landing',[0,.5,1]),{...shortTimer});short.seek(1.6);same(short.getState().engines.pymunk.t,1);same(short.getState().engines.pymunk.held,true);same(short.getState().engines.pymunk.ended,true);same(short.getState().engines.analytical.t,1);const shortHost=new Element(),shortMount=Replay.mount(shortHost,short);ok(shortHost.textContent.includes('ended; holding last frame'),'Early termination shown');shortMount.destroy();short.destroy();
// Source identity and mismatched settings cannot silently combine unrelated runs.
reject(b=>{b.candidateId='other';},/candidate/);reject(b=>{b.runs.pymunk.candidateId='other';},/candidate/);reject(b=>{b.runs.pymunk.kind='jump';},/case/);reject(b=>{b.runs.pymunk.payload.engine='analytical';},/engine/);
reject(b=>{b.runs.pymunk.result.designHash='other';},/design/);reject(b=>{b.runs.pymunk.result.schema='kinefold/dynamics-v1';},/contact/);reject(b=>{b.runs.pymunk.payload.params.alpha=20;},/params/);
reject(b=>{b.runs.pymunk.payload.motorConfig.gearRatio=20;b.runs.pymunk.result.motorConfig.gearRatio=20;b.runs.pymunk.result.snapshot.motorConfig.gearRatio=20;},/settings/);
reject(b=>{b.runs.pymunk.result.snapshot.solverConfig.dt+=.000123;},/snapshot/);reject(b=>{b.settingsHash='bad';},/hash/);reject(b=>{b.originalJobId='../elsewhere';},/identity/);
reject(b=>{delete b.runs.pymunk;},/Both/);reject(b=>{b.runs.pymunk.result.frames.pop();},/misaligned/);reject(b=>{b.runs.pymunk.result.frames[1].t=.9;},/timestamps/);
reject(b=>{b.runs.pymunk.result.rows[2].t=.5;b.runs.pymunk.result.frames[2].t=.5;},/timestamps/);reject(b=>{b.runs.pymunk.result.frames[0].A[0]=NaN;},/nonfinite/);
reject(b=>{b.runs.pymunk.result.frames[0].theta2+=1;},/angle/);reject(b=>{delete b.runs.pymunk.result.frames[0].indexAnglesDeg.b;},/indices/);reject(b=>{b.runs.pymunk.result.terrain.baseSegmentMm=[];},/terrain/);
reject(b=>{b.runs.pymunk.result.terrain.polygonsMm=[[1]];},/polygon/);
reject(b=>{b.runs.pymunk.result.rows[0].chassisZMm+=1;},/frame/);
reject(b=>{b.runs.pymunk.payload.params.m1='<script>';b.runs.pymunk.result.params.m1='<script>';b.runs.pymunk.result.snapshot.params.m1='<script>';},/geometry/);
// Replacement or seeking from a subscriber cannot publish stale state or add clocks.
const replaceClock=clock(),replaced=Replay.create(fixture(),{...replaceClock}),seen=[];
replaced.subscribe(s=>{if(s.playing)replaced.destroy();});replaced.subscribe(s=>seen.push(s.destroyed));replaced.play();same(seen.join(','),'false,true','Destroy invalidates in-flight publications');same(replaceClock.pending(),0);assert.throws(()=>Replay.mount(new Element(),replaced),/closed/);count++;
const seekClock=clock(),seeking=Replay.create(fixture(),{...seekClock}),seekStates=[];
seeking.subscribe(s=>{if(s.playing&&s.time===0)seeking.seek(1);});seeking.subscribe(s=>seekStates.push(s.time));seeking.play();same(seekClock.pending(),1,'Reentrant seek retains one shared RAF');same(seekStates.join(','),'0,1','Seek invalidates stale clock publication');seeking.destroy();
// Actual app renderer moves physical spring, wheel indices and translating floor.
for(const kind of ['landing','jump','terrain']){
 const b=fixture(kind),c=Replay.create(b),a=Replay.renderFrame(c,'analytical',0),later=Replay.renderFrame(c,'analytical',1),p=Replay.renderFrame(c,'pymunk',1);
 ok(a.html!==later.html,kind+' saved mechanism moves');ok(a.html.includes('data-compression-spring="illustrative"'),'Actual compression assembly retained');ok(later.html.includes('+x')&&later.html.includes('+z'),'Coordinate directions retained');same(later.frame.wheelAngle,45,'Saved wheel angle replayed');same(later.camera,p.camera,'Independent engines share exact same camera object');
 const payout=html=>Number(html.match(/data-spring-payout-mm="([^"]+)"/)[1]);ok(payout(a.html)!==payout(later.html),'Spring payout actually changes');
 same(later.frame.terrainOffsetMm[0],kind==='terrain'?-100:0,'Terrain translation matches saved case');
 const svg=Replay.renderSVG(c,'analytical',1);ok(svg.startsWith('<svg xmlns='));ok(!svg.includes('var(--'),'Standalone SVG resolves app colors');ok(!/NaN|Infinity/.test(svg),'Standalone preview contains finite drawing coordinates');c.destroy();
}
// Optional parent-provided real API bundles exercise all captured data/render paths.
for(let i=2;i<process.argv.length;i++){
 if(process.argv[i]!=='--bundle'||!process.argv[i+1])throw Error('Use --bundle captured-api-response.json');
 const file=process.argv[++i],raw=JSON.parse(fs.readFileSync(file,'utf8')),bundle=raw.bundle||raw,c=Replay.create(bundle),st=c.getState();
 for(const engine of ['analytical','pymunk'])for(const t of [0,Math.min(.65,st.duration),st.duration/2,st.duration]){
  c.seek(t);const frame=c.render(engine);ok(frame.sampleTimeS<=t,'Real saved sample never comes from the future');ok(!/NaN|Infinity/.test(frame.html),'Real '+engine+' finite SVG');ok(frame.html.includes('data-compression-spring'),'Real spring animation data present');same(frame.row.t,frame.frame.t,'Real saved row/frame aligned');
 }
 c.destroy();console.log('Validated actual replay bundle '+path.basename(file));
}
console.log('PASS '+count+' saved comparison replay clock/DOM/capture/SVG assertions; no live browser, physics execution or profile writes.');
