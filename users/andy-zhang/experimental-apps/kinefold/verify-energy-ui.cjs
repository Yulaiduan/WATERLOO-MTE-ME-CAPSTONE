/** DOM/VM integration for standalone Energy UI. Run node verify-energy-ui.cjs.
 * Inputs temporary in-memory projects; outputs assertions for instant math,
 * saved metadata, plots, navigation, correct torque-side handoff and artifacts.
 * Minimal DOM is not a browser: CSS, pointer/visual QA remain unverified.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const read=f=>fs.readFileSync(__dirname+'/'+f,'utf8');
const decode=s=>String(s).replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
class Element{
  constructor(tag='div',attrs={}){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.children=[];this.parentNode=null;this.hidden='hidden'in attrs;this.disabled='disabled'in attrs;this.checked='checked'in attrs;this.open='open'in attrs;this.dataset={};this._value=attrs.value;this._text='';this.listeners={};for(const [k,v]of Object.entries(attrs))if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v;this.classList={add:(...c)=>{this.attrs.class=[...(this.attrs.class||'').split(' '),...c].join(' ');},toggle:(c,on)=>{const names=new Set((this.attrs.class||'').split(' '));if(on)names.add(c);else names.delete(c);this.attrs.class=[...names].join(' ');}};}
  get id(){return this.attrs.id;} get type(){return this.attrs.type||'';}
  set innerHTML(html){this.children=[];this._text='';const stack=[this];for(const token of String(html).match(/<[^>]*>|[^<]+/g)||[]){if(token.startsWith('</')){if(stack.length>1)stack.pop();continue;}if(token.startsWith('<')){if(token.startsWith('<!'))continue;const tag=token.match(/^<([\w-]+)/)?.[1];if(!tag)continue;const attrs={};const text=token.slice(tag.length+1,-1);for(const m of text.matchAll(/([\w-]+)(?:="([^"]*)"|='([^']*)'|=([^\s>]+))?/g))attrs[m[1]]=decode(m[2]??m[3]??m[4]??'');const child=new Element(tag,attrs);stack.at(-1).append(child);if(!['input','br','hr','img','meta','link','path','circle'].includes(tag)&&!token.endsWith('/>'))stack.push(child);}else stack.at(-1)._text+=decode(token);}}
  get innerHTML(){return this.children.map(c=>c.outerHTML).join('')+this._text;}
  get outerHTML(){return `<${this.tagName.toLowerCase()}>${this.innerHTML}</${this.tagName.toLowerCase()}>`;}
  get textContent(){return this._text+this.children.map(c=>c.textContent).join('');}
  set textContent(text){this.children=[];this._text=String(text);}
  get value(){if(this.tagName==='SELECT'){const options=this.querySelectorAll('option');return this._value??options.find(o=>'selected'in o.attrs)?.value??options[0]?.value??'';}return this._value??(this.tagName==='OPTION'?this.attrs.value??this.textContent:'');}
  set value(v){this._value=String(v);}
  get selectedOptions(){return this.querySelectorAll('option').filter(o=>o.value===this.value);}
  append(child){child.parentNode=this;this.children.push(child);} appendChild(child){this.append(child);}
  matches(selector){if(selector.includes('>'))return this.matches(selector.split('>').at(-1));if(selector.startsWith('#'))return this.id===selector.slice(1);if(selector.startsWith('.'))return (this.attrs.class||'').split(' ').includes(selector.slice(1));const m=selector.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);if(m)return m[2]===undefined?m[1]in this.attrs:this.attrs[m[1]]===m[2];return this.tagName.toLowerCase()===selector;}
  querySelectorAll(selector){const selectors=selector.split(',').map(s=>s.trim()),out=[];const walk=node=>{for(const child of node.children){if(selectors.some(s=>child.matches(s)))out.push(child);walk(child);}};walk(this);return out;}
  querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
  setAttribute(k,v){this.attrs[k]=String(v);if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=String(v);}
  addEventListener(k,fn){(this.listeners[k]??=[]).push(fn);}
  focus(){this.focused=true;} scrollIntoView(){this.scrolled=true;}
  getBoundingClientRect(){return {left:0,right:200,top:0,bottom:120,width:200,height:120};}
}
Element.prototype.closest=function(selector){let node=this;while(node){if(node.matches(selector))return node;node=node.parentNode;}return null;};
Element.prototype.hasAttribute=function(k){return k in this.attrs;};
Object.defineProperty(Element.prototype,'isConnected',{get(){return !!this.closest('body');}});
const document=new Element('body');document.innerHTML='<section id="energy" role="tabpanel" hidden></section>';
document.getElementById=id=>document.querySelector('#'+id);document.createElement=tag=>new Element(tag);
const events={},charts=[],artifacts=[],toasts=[];let requests=0,tab='builder',current,ctx,checks=0;
const ok=(v,s)=>{assert.ok(v,s);checks++;},near=(a,b,t=1e-8)=>ok(Math.abs(a-b)<t,`${a} != ${b}`);
const realm=v=>{ctx.raw=JSON.stringify(v);return vm.runInContext('JSON.parse(raw)',ctx);};
ctx=vm.createContext({console,document,structuredClone:v=>realm(v),window:{addEventListener:(k,fn)=>(events[k]??=[]).push(fn)},fetch(){requests++;throw Error('Energy UI must not fetch dynamics.');}});
for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','energy-analysis.js','dynamic-analysis.js'])vm.runInContext(read(f),ctx,{filename:f});
const P=ctx.KinefoldProjects,A=ctx.KinefoldEnergyAnalysis;current=P.baseline();const original=JSON.stringify(current);
ctx.KinefoldStudio={getSnapshot:()=>realm(current),exportProject:()=>realm(current),toast:s=>toasts.push(s),showTab:id=>{tab=id;document.getElementById('energy').hidden=id!=='energy';for(const fn of events['kinefold-solver-tab']||[])fn({detail:{id}});},
setEnergyConfig:c=>{if(c===null)delete current.energyConfig;else current.energyConfig=P.validateEnergy(realm(c));ctx.KinefoldEnergyUI.update(realm(current));},setTorqueTargetConfig:c=>{current.torqueTargetConfig=P.validateTorqueTargets(realm(c));ctx.KinefoldEnergyUI.update(realm(current));},setCaseConfig:c=>{current.caseConfig=P.validateCase(realm(c));ctx.KinefoldEnergyUI.update(realm(current));},saveArtifact:async(name,value,mime)=>{artifacts.push({name,value:typeof value==='string'?value:realm(value),mime});}};
ctx.KinefoldPlotly={purge(){},resizeAll(){},react:async(host,traces,layout)=>{ok(!!host,'chart host exists');ok(traces.every(t=>t.type==='scatter'),'BASIC scatter only');for(const t of traces){ok(t.x.length===t.y.length,'matching trace axes');ok(t.y.every(v=>v===null||Number.isFinite(v)),'finite or explicit missing values');}charts.push({host,traces,layout});}};
for(const f of ['contact-ui.js','energy-ui.js'])vm.runInContext(read(f),ctx,{filename:f});
const UI=ctx.KinefoldEnergyUI,$=s=>document.getElementById('energy').querySelector(s),click=async s=>{let el=$(s);ok(!!el,s+' exists');await el.onclick({target:el});},change=(s,value)=>{let el=$(s);el.value=value;el.onchange({target:el});};
(async()=>{
UI.mount('energy',document.getElementById('energy'));UI.update(realm(current));ok(JSON.stringify(current)===original,'initial mount/update no saved writes');ok(charts.length===0,'hidden initial tab defers chart work');
ctx.KinefoldStudio.showTab('energy');ok(charts.length===4,'URL/tab reveal mounts all four plots');ok(!UI.getState().result.sampledNegativeInteriorCount,'baseline landing no negative interior budget');ok($('[data-energy-use="pymunk"]').disabled,'massless/prescribed profile blocks handoff only');ok($('[data-energy-handoff]').textContent.includes('Wheel mass'),'actionable mass limitation');
await click('[data-energy-two-metre]');near(UI.getState().result.requiredJointNm,232.3451518866197);ok(charts.length===8,'height edit recomputes plots without run');ok(!current.caseConfig,'height edit only analysis metadata');
// Saved Studio mounting pitch participates immediately, survives save/reload,
// appears in all chart titles and full projection equations, and remains pure.
current.params.alpha=20;const tiltedBefore=JSON.stringify(current);UI.update(realm(current));const tilted=UI.getState().result;
ok(tilted!==null&&tilted.alphaDeg===20&&tilted.requiredJointNm<232.3451518866197,'saved alpha recomputes projected gravity without Run');
ok(JSON.stringify(current)===tiltedBefore,'mounting pitch read does not edit saved design');ok($('[data-energy-alpha]').textContent.includes('α = 20°'),'prominent saved alpha readout');
ok($('[data-energy-output]').textContent.includes('−sin(α) P_u(q) + cos(α) P_v(q)'),'full rotated vertical projection visible');ok($('[data-energy-output]').textContent.includes('horizontal wheel motion is allowed')||$('[data-energy-output]').textContent.includes('wheel x motion is allowed'),'wheel horizontal freedom visible');
ok(charts.slice(-4).every(c=>c.layout.title.text.includes('α = 20°')),'all chart titles retain saved mounting pitch');
current=P.decode(realm(P.validate(current))).project;UI.update(realm(current));near(UI.getState().result.requiredJointNm,tilted.requiredJointNm);near(UI.getState().result.alphaDeg,20);
await click('[data-energy-alpha-edit]');ok(tab==='builder','alpha edit action opens Studio');ctx.KinefoldStudio.showTab('energy');
const beforeModeCharts=charts.length;await click('[data-energy-mode="jump"]');ok(UI.getState().kind==='jump'&&charts.length===beforeModeCharts+4,'mode switches all plots');ok($('[data-energy-case="landingOpenFraction"]').closest('label').hidden,'jump hides irrelevant opening');ok(!$('[data-energy-target="jumpHeightMm"]').closest('[data-energy-for]').hidden,'jump height visible');near(UI.getState().result.alphaDeg,20);
const lower=UI.getState().result.requiredJointNm;change('[data-energy-target="jumpHeightMm"]',300);ok(UI.getState().result.requiredJointNm>lower,'jump target changes work torque');
change('[data-energy-motor]','flipsky-80100-130');change('[data-energy-gear]','eg20');near(UI.getState().result.gearRatio,20);near(UI.getState().result.availableJointNm,60);ok($('[data-energy-screen="customRatio"]').closest('label').hidden,'custom ratio hidden for catalog');ok(!current.motorConfig,'catalog never creates physical motor');
change('[data-energy-gear]','custom');ok(!$('[data-energy-screen="customRatio"]').closest('label').hidden,'custom fields shown only when selected');ok(UI.getState().result.screening.gearboxPass===null,'unknown gearbox cannot pass');
change('[data-energy-gear]','eg20');const saved=JSON.stringify(current);UI.update(realm(current));ok(JSON.stringify(current)===saved,'repeated update no writes');
change('[data-energy-range="heightMaxMm"]',100);ok($('[data-energy-range-error]').textContent.includes('outside'),'offrange target explicit');ok(charts.at(-4).layout.xaxis.range[1]===100,'height range constrained despite outside marker');
const beforeInvalid=charts.length;change('[data-energy-range="heightMaxMm"]',-1);ok(charts.length===beforeInvalid&&$('[data-energy-range-error]').textContent.includes('range'),'invalid range keeps known calculation and reports input');
await click('[data-energy-export="json"]');ok(artifacts.at(-1).value.projectSnapshot.id===current.id&&artifacts.at(-1).value.calculation.stroke.length===161,'complete JSON snapshot/ledger');near(artifacts.at(-1).value.calculation.alphaDeg,20);near(artifacts.at(-1).value.projectSnapshot.params.alpha,20);
await click('[data-energy-export="curve"]');ok(artifacts.at(-1).value.split('\n').length===82,'all height samples CSV');ok(artifacts.at(-1).value.split('\n')[0].startsWith('alphaDeg,')&&artifacts.at(-1).value.split('\n').slice(1).every(r=>r.startsWith('20,')),'every curve CSV row retains alpha');
await click('[data-energy-export="stroke"]');ok(artifacts.at(-1).value.includes('kineticBudgetJ'),'signed budget CSV');ok(artifacts.at(-1).value.includes('wheelCxMm')&&artifacts.at(-1).value.includes('horizontalWheelDisplacementMm'),'stroke CSV contains signed world horizontal wheel travel');ok(artifacts.at(-1).value.split('\n').slice(1).every(r=>r.startsWith('20,')),'every stroke CSV row retains alpha');
// Real guard/physical-basis contracts, separate catalog N20 and physical N10.
current.params.m6=1.5;current.contactConfig=realm({...P.contactDefaults});current.motorConfig=realm({...P.motorDefaults,enabled:true,gearRatio:10,commandBasis:'motor',coggingAmplitudeNm:.4,coggingPeriodsPerRev:3});UI.update(realm(current));
const cmd=UI.command(realm(current),'jump'),physical=A.jumpEstimate(realm(current),300);near(physical.alphaDeg,20);near(cmd.commandNm,physical.jointNm/10);ok(cmd.reasons.length===0&&!$('[data-energy-use="pymunk"]').disabled,'valid tilted free-wheel contact enables handoff');ok($('[data-energy-handoff]').textContent.includes('independently'),'candidate/physical estimate clearly distinct');
const motorBefore=JSON.stringify(current.motorConfig);await click('[data-energy-use="pymunk"]');ok(tab==='pymunk'&&current.caseConfig.kind==='jump','handoff selects scenario/navigates');near(current.caseConfig.jumpTorqueNm,cmd.commandNm);ok(current.caseConfig.jumpTorqueNm>=0,'controller gets positive magnitude');ok(JSON.stringify(current.motorConfig)===motorBefore,'handoff leaves physical motor unchanged');
ctx.KinefoldStudio.showTab('energy');await click('[data-energy-mode="landing"]');current.motorConfig.commandBasis='joint';UI.update(realm(current));const landing=UI.command(realm(current),'landing');await click('[data-energy-use="analytical"]');near(current.caseConfig.landingBrakeTorqueNm,landing.jointNm);near(current.caseConfig.landingBrakeLimitNm,landing.jointNm);ok(current.caseConfig.landingBrakeTorqueNm>200,'copied high command not silently capped');near(current.caseConfig.landingDropMm,2000);near(current.torqueTargetConfig.landingClearanceMm,50);ok(tab==='analytical','landing handoff navigation');
current.motorConfig.gearRatio=.001;current.motorConfig.commandBasis='motor';UI.update(realm(current));ok(UI.command(realm(current),'landing').reasons.some(s=>s.includes('cannot be copied')),'oversized motor-side command blocked before writes');
current.params.alpha=46;UI.update(realm(current));ok(UI.getState().result===null&&!$('[data-energy-key="dropHeightMm"]').disabled,'unsupported geometry leaves editable controls');ok($('[data-energy-output]').textContent.includes('unavailable'),'old results removed on error');
current.params.alpha=0;current.motorConfig.gearRatio=10;UI.update(realm(current));ok(UI.getState().result!==null,'valid edits recover');
const beforeZero=realm(current);current.params.alpha=45;current.energyConfig={...P.energyDefaults,dropHeightMm:0};UI.update(realm(current));ok(UI.getState().result.requiredJointNm===0&&UI.getState().result.endpointKineticBudgetJ<0,'tilted zero-height landing keeps signed unreachable endpoint');ok($('[data-energy-output]').textContent.includes('earlier arrest/reversal'),'negative landing demand explains earlier arrest');
current.torqueTargetConfig={...P.torqueTargetDefaults,jumpHeightMm:0};await click('[data-energy-mode="jump"]');ok(UI.getState().result.requiredJointNm===0&&UI.getState().result.endpointKineticBudgetJ>0,'tilted zero-height jump keeps surplus');ok($('[data-energy-output]').textContent.includes('positive endpoint kinetic surplus'),'negative jump demand explains apex not established');current=beforeZero;UI.open('landing');
await click('[data-energy-remove]');ok(!current.energyConfig&&current.torqueTargetConfig,'reset removes only calculator metadata');ok(requests===0,'no dynamics/network calls from calculator or handoff');
const html=read('index.html');ok(html.indexOf('data-tab="builder"')<html.indexOf('data-tab="energy"')&&html.indexOf('data-tab="energy"')<html.indexOf('data-tab="analytical"'),'energy before dynamics');ok(read('app.js').includes("['builder','energy','analytical','pymunk','presets','flow','conventions']"),'stable tab IDs / conventions last');ok(!read('solvers.js').includes('KinefoldEnergyUI.mount(id'),'no duplicate energy calculators in dynamics');
ok(document.querySelectorAll('label').every(label=>!label.querySelector('label')),'valid nonnested labels');
console.log('PASS '+checks+' Energy DOM/VM assertions; '+charts.length+' BASIC-compatible chart mounts; no live browser QA.');
})().catch(e=>{console.error(e);process.exitCode=1;});
