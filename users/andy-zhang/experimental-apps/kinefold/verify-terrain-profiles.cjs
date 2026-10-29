/** Verify periodic terrain UI, captured identities and input presets in memory.
 * Run node verify-terrain-profiles.cjs. Inputs sheet catalog and temporary V4
 * projects; outputs assertion counts and BASIC Plotly mounts. No server, live
 * libraries or dynamics requests; this DOM fixture does not certify CSS/pointers.
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

Element.prototype.matches=function(selector){if(selector.includes(','))return selector.split(',').some(s=>this.matches(s.trim()));if(selector.startsWith('#'))return this.id===selector.slice(1);if(selector.startsWith('.'))return(this.attrs.class||'').split(' ').includes(selector.slice(1));const m=selector.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);if(m)return m[2]===undefined?m[1]in this.attrs:this.attrs[m[1]]===m[2];return this.tagName.toLowerCase()===selector;};
Element.prototype.before=function(child){const p=this.parentNode;child.parentNode=p;p.children.splice(p.children.indexOf(this),0,child);};
const document=new Element('body');document.innerHTML='<section id="analytical"><div class="quarter-scope"></div></section><section id="pymunk"><div class="quarter-scope"></div></section>';document.getElementById=id=>document.querySelector('#'+id);document.createElement=tag=>new Element(tag);
const charts=[],saves=[],toasts=[];let writes=0,current,ctx;const realm=v=>{ctx.raw=JSON.stringify(v);return vm.runInContext('JSON.parse(raw)',ctx);};
ctx=vm.createContext({console,document,structuredClone:v=>realm(v),window:{dispatchEvent(){}},CustomEvent:class{},fetch(){throw Error('No network or dynamics allowed in UI fixture.');}});
for(const f of ['reference-v4.js','model.js','variables.js','terrain-profiles.js','project-store.js','preset-store.js','dynamic-analysis.js'])vm.runInContext(read(f),ctx,{filename:f});
ctx.KinefoldTerrainProfiles.init(realm(JSON.parse(read('terrain-catalog.json'))));const T=ctx.KinefoldTerrainProfiles,P=ctx.KinefoldProjects,Presets=ctx.KinefoldPresets;
current=P.baseline();current.params.m6=1.5;current.contactConfig=realm({...P.contactDefaults});current.caseConfig=realm({...P.caseDefaults,kind:'landing'});
ctx.KinefoldStudio={getSnapshot:()=>realm(current),exportProject:()=>realm(current),toast:s=>toasts.push(s),async applySnapshot(next){current=P.validate(realm(next));writes++;ctx.KinefoldTerrainUI.update(realm(current));return current;},setTerrainConfig(next){if(next===null)delete current.terrainConfig;else current.terrainConfig=T.validate(realm(next));writes++;ctx.KinefoldTerrainUI.update(realm(current));}};
ctx.KinefoldPresetWorkbench={async saveInputPreset(project,name){saves.push(Presets.make('input',name,Presets.captureInput(realm(project))));}};
ctx.KinefoldPlotly={purge(){},react:async(node,traces,layout)=>{assert.ok(node);assert.ok(traces.every(t=>t.type==='scatter'&&t.x.length===t.y.length));charts.push({traces,layout});}};
vm.runInContext(read('terrain-ui.js'),ctx,{filename:'terrain-ui.js'});
const UI=ctx.KinefoldTerrainUI,$=(id,s)=>document.getElementById(id).querySelector(s),change=(id,s,v)=>{const e=$(id,s);e.value=v;e.onchange({target:e});},click=async(id,s)=>{const e=$(id,s);await e.onclick({target:e});};let checks=0;const ok=(v,s)=>{assert.ok(v,s);checks++;};
(async()=>{
 const before=JSON.stringify(current);for(const id of ['analytical','pymunk'])UI.mount(id,document.getElementById(id));await new Promise(setImmediate);UI.update(realm(current));
 ok(JSON.stringify(current)===before&&writes===0,'mount/update do not edit saved design');ok($('analytical','[data-terrain-source]').querySelectorAll('option').length===16,'all source terrains available');
 ok(!$('analytical','[data-terrain-source]').disabled,'local preview remains editable in landing');ok($('analytical','[data-terrain-apply="short"]').disabled,'landing cannot apply a terrain');
 change('analytical','[data-terrain-source]','gravel-service-fire-road');change('analytical','[data-terrain-severity]','difficult');ok(writes===0&&JSON.stringify(current)===before,'preview selection is local');ok($('analytical','[data-terrain-period]').value==='5000','source difficult spacing uses m to mm conversion');
 current.caseConfig.kind='terrain-stability';UI.update(realm(current));ok(!$('analytical','[data-terrain-apply="short"]').disabled,'terrain contact enables Apply');
 const physical=JSON.stringify([current.params,current.contactConfig,current.motorConfig]);await click('analytical','[data-terrain-apply="short"]');ok(writes===1,'one deliberate Apply');ok(JSON.stringify([current.params,current.contactConfig,current.motorConfig])===physical,'mechanism and friction preserved');ok(current.solverConfig.duration===6.5&&current.solverConfig.inputSpeedMmS===5000/6,'explicit short test settings');
 ok($('pymunk','[data-terrain-source]').value==='gravel-service-fire-road','both tabs synchronize saved config');ok($('pymunk','[data-terrain-severity]').value==='difficult','same severity');
 const round=P.decode(realm(JSON.parse(JSON.stringify(current)))).project;ok(JSON.stringify(round.terrainConfig)===JSON.stringify(current.terrainConfig),'project roundtrip retains profile');
 const input=Presets.make('input','Captured terrain',Presets.captureInput(realm(current))),suspension=Presets.make('suspension','Geometry',Presets.captureSuspension(realm(current))),actuator=Presets.make('actuator','Ideal motor',Presets.captureActuator(realm(current)));
 const composed=Presets.compose(P.baseline(),suspension,actuator,input);ok(JSON.stringify(composed.terrainConfig)===JSON.stringify(current.terrainConfig),'input composition freezes periodic profile');await click('analytical','[data-terrain-save]');ok(saves.length===1&&saves[0].values.terrainConfig.profileId===current.terrainConfig.profileId,'Save input uses existing preset flow');
 const key=ctx.KinefoldDynamicAnalysis.snapshotKey(current);ok(key!==ctx.KinefoldDynamicAnalysis.snapshotKey({...current,terrainConfig:{...current.terrainConfig,periodMm:1000}}),'period change marks results stale');
 current.solverConfig.inputSpeedMmS=123;current.solverConfig.duration=3;UI.update(realm(current));change('analytical','[data-terrain-period]','2000');await click('analytical','[data-terrain-apply="entered"]');ok(current.solverConfig.inputSpeedMmS===123&&current.solverConfig.duration===3,'entered speed/duration retained');
 change('analytical','[data-terrain-source]','snow-covered-terrain');ok($('analytical','[data-terrain-period]').value==='','snow spacing not inferred');ok($('analytical','[data-terrain-apply="entered"]').disabled,'missing period blocks Apply');change('analytical','[data-terrain-period]','3000');ok(!$('analytical','[data-terrain-apply="entered"]').disabled,'explicit entered snow period enables obstacle proxy');change('analytical','[data-terrain-representation]','roughness');ok($('analytical','[data-terrain-apply="entered"]').disabled,'ambiguous snow RMS remains blocked');
 await click('pymunk','[data-terrain-square]');ok(!current.terrainConfig,'Use square removes only optional surface');ok(current.solverConfig.inputSpeedMmS===123&&current.solverConfig.duration===3,'square retains run settings');ok(JSON.stringify([current.params,current.contactConfig,current.motorConfig])===physical,'all UI interactions preserve physical mechanism/material');
 current.terrainConfig=T.config('gravel-service-fire-road','difficult');for(const id of ['saved-a','saved-b']){const root=new Element('section',{id});root.innerHTML='<div class="quarter-scope"></div>';document.append(root);UI.mount(id,root);}await new Promise(setImmediate);for(const id of ['saved-a','saved-b'])ok($(id,'[data-terrain-source]').value==='gravel-service-fire-road','saved terrain survives asynchronous two-panel option fill');
 ok(charts.length>10,'Plotly previews mount for selections');ok(read('terrain-ui.js').includes('full cycle need not pass the wheel'),'lead-in limitation visible');
 for(const bad of [null,{...T.config('talus-boulder-field'),periodMm:NaN},{...T.config('talus-boulder-field'),profileId:'unknown'},{...T.config('talus-boulder-field'),unexpected:1}]){assert.throws(()=>T.validate(bad));checks++;}
 ok(read('contact-ui.js').includes('value.terrainConfig = project.terrainConfig'),'actual payload carries surface');ok(read('viewer_service.py').includes("'terrainConfig'"),'desktop request carries surface');
 console.log(`PASS ${checks} periodic terrain DOM/project/preset assertions; ${charts.length} BASIC Plotly mounts; no live disk writes or dynamics calls.`);
})().catch(e=>{console.error(e);process.exitCode=1;});
