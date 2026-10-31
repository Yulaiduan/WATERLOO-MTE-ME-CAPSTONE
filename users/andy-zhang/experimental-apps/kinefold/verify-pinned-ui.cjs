/** Check pinned-chassis persistence, transactional controls and Plotly pin data.
 * Run node verify-pinned-ui.cjs. Inputs synthetic mm/kg/deg/s/N project/results;
 * outputs assertions using a deterministic DOM and actual Studio setter methods.
 * No browser, server, physics run, profile write or hardware validation.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let count=0;const ok=(v,n)=>{assert.ok(v,n);count++;};
class Element{
 constructor(tag='div',attrs={}){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.children=[];this.parentNode=null;this.dataset={};this._value=attrs.value;this._text='';for(const[k,v]of Object.entries(attrs))if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v;}
 set innerHTML(html){this.children=[];this._text='';const stack=[this];for(const token of String(html).match(/<[^>]*>|[^<]+/g)||[]){if(token.startsWith('</')){if(stack.length>1)stack.pop();continue;}if(token.startsWith('<')){const tag=token.match(/^<([\w-]+)/)?.[1];if(!tag)continue;const attrs={};for(const m of token.slice(tag.length+1,-1).matchAll(/([\w-]+)(?:="([^"]*)"|='([^']*)'|=([^\s>]+))?/g))attrs[m[1]]=m[2]??m[3]??m[4]??'';const child=new Element(tag,attrs);stack.at(-1).append(child);if(!['input','br','hr'].includes(tag))stack.push(child);}else stack.at(-1)._text+=token;}}
 get textContent(){return this._text+this.children.map(c=>c.textContent).join('');}set textContent(v){this._text=String(v);this.children=[];}
 get value(){return this._value??this.attrs.value??(this.tagName==='SELECT'?this.querySelector('option')?.value:'')??'';}set value(v){this._value=String(v);}
 append(child){if(child.parentNode)child.parentNode.children=child.parentNode.children.filter(c=>c!==child);child.parentNode=this;this.children.push(child);}
 before(child){const parent=this.parentNode;child.parentNode=parent;parent.children.splice(parent.children.indexOf(this),0,child);}
 insertAdjacentHTML(_,html){const temp=new Element();temp.innerHTML=html;for(const child of [...temp.children])this.append(child);}
 matches(s){if(s.startsWith('.'))return(this.attrs.class||'').split(' ').includes(s.slice(1));const m=s.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);if(m){const key=m[1].startsWith('data-')?m[1].slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase()):null,value=key&&key in this.dataset?this.dataset[key]:this.attrs[m[1]];return m[2]===undefined?value!==undefined:value===m[2];}return this.tagName.toLowerCase()===s;}
 querySelectorAll(selector){const parts=selector.split(' '),out=[];function matches(node){if(!node.matches(parts.at(-1)))return false;let parent=node.parentNode;for(let i=parts.length-2;i>=0;i--){while(parent&&!parent.matches(parts[i]))parent=parent.parentNode;if(!parent)return false;parent=parent.parentNode;}return true;}const walk=node=>{for(const child of node.children){if(matches(child))out.push(child);walk(child);}};walk(this);return out;}
 querySelector(s){return this.querySelectorAll(s)[0]||null;}
}
const body=new Element(),panels=Object.fromEntries(['analytical','pymunk'].map(id=>[id,new Element('section')]));
for(const p of Object.values(panels)){p.innerHTML='<div class="solver-heading"><p>Engine</p></div><div class="quarter-scope"></div><button data-hold>Hold</button>';body.append(p);}
const ctx=vm.createContext({console,assert,ok,document:{createElement:tag=>new Element(tag),querySelector:s=>body.querySelector(s),getElementById:id=>panels[id]}});
for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','dynamic-analysis.js','dynamic-results.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),ctx,{filename:f});
vm.runInContext(`
globalThis.P=KinefoldProjects;globalThis.original=P.baseline();globalThis.before=JSON.stringify(original);
ok(JSON.stringify(P.validate(original))===before,'legacy project shape unchanged');
globalThis.project={...P.clone(original),params:{...original.params,m6:.5},contactConfig:{...P.contactDefaults},caseConfig:{...P.caseDefaults}};
globalThis.solverConfig={...project.solverConfig};globalThis.notifications=0;globalThis.saves=0;globalThis.messages=[];
function snapshot(){return P.clone({...project,solverConfig});}function notify(){notifications++;}function save(){saves++;}
function applySnapshot(){}function ask(){}function portable(){return snapshot();}function tab(){}function toast(message){messages.push(message);}
globalThis.store={ready:Promise.resolve()};globalThis.Projects=P;
`,ctx);
const app=fs.readFileSync(__dirname+'/app.js','utf8'),start=app.indexOf('globalThis.KinefoldStudio='),end=app.indexOf('\nfunction fieldHTML',start);
assert.ok(start>=0&&end>start);vm.runInContext(app.slice(start,end),ctx,{filename:'actual Studio setters'});
vm.runInContext(`
globalThis.S=KinefoldStudio;S.setSolverConfig({...solverConfig,fixture:'pinned-chassis'});
ok(solverConfig.fixture==='pinned-chassis','actual setter accepts valid pinned terrain');
globalThis.pinned=P.validate(snapshot());ok(P.decode(P.clone(pinned)).project.solverConfig.fixture==='pinned-chassis','pinned snapshot roundtrip');
globalThis.unchanged=JSON.stringify(snapshot());globalThis.n=notifications;
assert.throws(()=>S.setCaseConfig({...project.caseConfig,kind:'jump'}),/Pinned chassis/);
assert.throws(()=>S.setContactConfig({...project.contactConfig,mode:'prescribed-height'}),/Pinned chassis/);
ok(JSON.stringify(snapshot())===unchanged&&notifications===n,'invalid changes do not mutate or notify');
assert.throws(()=>P.validate({...pinned,contactConfig:undefined}),/contact configuration/);
assert.throws(()=>P.validate({...pinned,caseConfig:{...P.caseDefaults,kind:'landing'}}),/Pinned chassis/);
ok(P.validate({...pinned,solverConfig:{...solverConfig,inputSpeedMmS:0}}).solverConfig.inputSpeedMmS===0,'actual contact accepts stationary floor');
assert.throws(()=>P.validate({...original,solverConfig:{...original.solverConfig,inputSpeedMmS:0}}),/Zero terrain speed/);
ok(JSON.stringify(original)===before,'invalid/valid fixture tests preserve original');
`,ctx);
vm.runInContext(fs.readFileSync(__dirname+'/contact-ui.js','utf8'),ctx,{filename:'contact-ui.js'});
ctx.panels=panels;
vm.runInContext(`
const C=KinefoldContactUI;for(const id of ['analytical','pymunk'])C.mount(id,panels[id]);C.update(snapshot());
for(const id of ['analytical','pymunk']){
 const root=panels[id],field=root.querySelector('[data-contact-fixture]');
 ok(field.value==='pinned-chassis'&&!field.disabled,'both tabs show editable pinned fixture');
 ok(root.querySelector('[data-contact-description]').textContent.includes('wheel is free to rotate, separate'),'wheel not fixed to terrain');
 ok(root.querySelector('[data-contact-description]').textContent.includes('not a direct rise-time test'),'pin diagnostic is not called a response test');
}
const field=panels.analytical.querySelector('[data-contact-fixture]');field.value='floating-chassis';field.onchange({target:field});C.update(snapshot());
ok(solverConfig.fixture==='floating-chassis'&&panels.pymunk.querySelector('[data-contact-fixture]').value==='floating-chassis','fixture change synchronizes tabs');
S.setContactConfig({...project.contactConfig,mode:'prescribed-height'});C.update(snapshot());
field.value='pinned-chassis';field.onchange({target:field});
ok(solverConfig.fixture==='floating-chassis'&&field.value==='floating-chassis','unsupported UI change restores displayed saved fixture');
ok(messages.at(-1).includes('Pinned chassis'),'unsupported UI selection shows an explicit error');
`,ctx);
const A=ctx.KinefoldDynamicAnalysis,D=ctx.KinefoldDynamicResults;
const pin=A.contactManifest.find(x=>x.id==='chassis-pin-force');
ok(pin.group==='forces'&&pin.unit==='N','pin plot categorized and measured in N');
ok(pin.note.includes('first finite interval')&&pin.note.includes('not a chassis response-time'),'baseline and measurement meaning visible');
const rows=[{t:0,pinForceZN:null,pinForceDeltaZN:null},{t:.1,pinForceZN:15,pinForceDeltaZN:0},{t:.2,pinForceZN:-8,pinForceDeltaZN:-23},{t:.3}];
const traces=D.traces({...pin,rows});
assert.deepEqual(JSON.parse(JSON.stringify(traces[0].y)),[null,15,-8,null]);count++;
assert.deepEqual(JSON.parse(JSON.stringify(traces[1].y)),[null,0,-23,null]);count++;
ok(traces.every(t=>t.type==='scatter'&&t.connectgaps===false),'offline Plotly preserves unavailable gaps');
const fake={...rows[0],t:0},legacy=D.traces({...pin,rows:[fake,{t:1}]});
ok(legacy.every(t=>t.y.every(v=>v===null)),'legacy missing pin force is never converted to zero');
ok(A.snapshotKey({...ctx.original,solverConfig:{...ctx.original.solverConfig,fixture:'pinned-chassis'}})!==A.snapshotKey(ctx.original),'fixture changes saved-result identity');
console.log('PASS '+count+' pinned UI/persistence/transaction/Plotly assertions; no physics, browser or profile writes.');
