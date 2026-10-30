/** Independent analytical/DOM checks for the actuator information calculator.
 * Run: node verify-actuator-calculator.cjs from this app (Node built-ins only).
 * Inputs: synthetic SI hardware and copied V4 geometry, never live libraries.
 * Outputs: assertion count, limiting-case residuals and UI purity checks.
 * Does not run browser/computer automation, contact engines or certify hardware.
 */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
require('./reference-v4.js');require('./model.js');const A=require('./actuator-calculator.js');
let checks=0;const ok=(v,n)=>{assert.ok(v,n);checks++;},near=(a,b,e=1e-9,n='')=>ok(Math.abs(a-b)<=e,n+': '+a+' versus '+b),throws=(fn,re)=>{assert.throws(fn,re);checks++;};
const p={...globalThis.Kinefold.defaults,m2:1,m3:1,m6:.5,theta2:135},original=JSON.stringify(p);
const h=A.hardware({motorPeakNm:8,motorNoLoadRpm:6000,ratio:10,efficiency:.9,rotorInertiaKgM2:.0001,gearboxInputInertiaKgM2:.00001,gearboxOutputInertiaKgM2:0,gearboxPeakNm:100,gearboxInputMaxRpm:6000,gearboxOutputMaxRpm:1000});
const belt=A.hardware({...h,hipBeltRatio:2});near(belt.totalRatio,20);near(belt.motorReflectedKgM2,4*h.motorReflectedKgM2);near(belt.gearboxReflectedKgM2,4*h.gearboxReflectedKgM2);near(belt.unlimitedJointPeakNm,2*h.unlimitedJointPeakNm);near(A.torque(A.hardware({...h,hipBeltRatio:2,gearboxPeakNm:20}),0),40);near(A.hardware({...h,hipBeltRatio:2,motorNoLoadRpm:1e6,gearboxInputMaxRpm:null,gearboxOutputMaxRpm:100}).jointSpeedCapRadS,100*2*Math.PI/60/2);throws(()=>A.hardware({...h,hipBeltRatio:3.01}),/belt ratio/);
// Independent closed form for equal 300mm uniform links and a free 500g wheel.
// Fixed hip: .06+.36cos²q. Grounded wheel: .06+3.33cos²q (8.75kg chassis).
for(let q=100;q<=165;q+=.5){const c=Math.cos(q*A.RAD),z=A.inertia(p,q*A.RAD,h),g=A.inertia(p,q*A.RAD,h,'grounded-wheel');
  near(z.legKgM2,.06+.36*c*c,2e-14,'Independent fixed-hip inertia');near(g.legKgM2,.06+3.33*c*c,2e-13,'Independent grounded inertia');
  near(z.derivativeKgM2Rad,-.72*Math.cos(q*A.RAD)*Math.sin(q*A.RAD),2e-14,'Independent dJ/dq');
  near(z.motorKgM2,.01);near(z.gearboxKgM2,.001);
  for(const alpha of [0,20,30])near(A.inertia({...p,alpha},q*A.RAD,h).legKgM2,z.legKgM2,1e-13,'Rigid rotation preserves fixed-hip inertia');
}
for(const q of [100,120,135,165])for(const fixture of ['fixed-hip','grounded-wheel']){
  const t=q*A.RAD,z=A.geometry({...p,alpha:20},t,fixture),eps=1e-5,lo=A.geometry({...p,alpha:20},t-eps,fixture),hi=A.geometry({...p,alpha:20},t+eps,fixture);
  for(const key of Object.keys(z.sites))for(let k=0;k<2;k++){near((hi.sites[key].site[0][k]-lo.sites[key].site[0][k])/(2*eps),z.sites[key].site[1][k],2e-10,'Position Jacobian');near((hi.sites[key].site[1][k]-lo.sites[key].site[1][k])/(2*eps),z.sites[key].site[2][k],2e-10,'Position curvature');}
}
const doubled={...p,m1:2*p.m1,m2:2,m3:2,m6:1};near(A.inertia(doubled,135*A.RAD,h).legKgM2,2*A.inertia(p,135*A.RAD,h).legKgM2);
const h20=A.hardware({...h,ratio:20});near(h20.motorReflectedKgM2,4*h.motorReflectedKgM2);near(h20.gearboxReflectedKgM2,4*h.gearboxReflectedKgM2);near(h20.unlimitedJointPeakNm,2*h.unlimitedJointPeakNm);
near(A.torque(h,0),72);near(A.torque(h,h.motorNoLoadRpm*2*Math.PI/60/h.ratio),0);near(A.torque(A.hardware({...h,gearboxPeakNm:20}),0),20);
throws(()=>A.hardware({...h,rotorInertiaKgM2:null}),/rotorInertia/);throws(()=>A.hardware({...h,motorNoLoadRpm:null}),/motorNoLoad/);throws(()=>A.hardware({...h,efficiency:1.1}),/exceed/);
ok(!A.hardware({...h,gearboxPeakNm:null}).gearboxTorqueAssessed,'Unknown rating stays unassessed');
const zero={name:'Zero',coulombNm:0,viscousNms:0};
const rod={...p,m1:0,m2:1,m3:0,m5:0,m6:0,springEnabled:false,g:0},constant=A.hardware({...h,ratio:1,efficiency:1,rotorInertiaKgM2:0,gearboxInputInertiaKgM2:0,motorPeakNm:2,motorNoLoadRpm:1e6,gearboxInputMaxRpm:null,gearboxOutputMaxRpm:null,gearboxPeakNm:null,torqueModel:'constant'});
const length=(rod.tc-rod.te)*A.RAD,J=rod.m2*(rod.L2/1000)**2/3,T=constant.motorPeakNm;
const exact=A.integrateStroke(rod,constant,zero,{steps:3000});
ok(exact.complete,'Constant-inertia stroke completes');near(exact.end.kineticJ,T*length,1e-12);near(exact.end.speedRadS,Math.sqrt(2*T*length/J),1e-11);near(exact.strokeTimeS,Math.sqrt(2*J*length/T),1e-10,'Constant acceleration stroke time');
// Independent viscous + linear torque-speed closed form at constant inertia.
const visc={name:'Viscous',coulombNm:.05,viscousNms:.03},linear=A.hardware({...constant,motorNoLoadRpm:600,torqueModel:'linear'}),curve=A.integrateStroke(rod,linear,visc,{steps:5000});
const drive=T-visc.coulombNm,B=T/(600*2*Math.PI/60)+visc.viscousNms,lambda=B/J;
const position=t=>drive/B*(t-(1-Math.exp(-lambda*t))/lambda);let lo=0,hi=10;for(let i=0;i<90;i++){const m=(lo+hi)/2;if(position(m)<length)lo=m;else hi=m;}const exactTime=(lo+hi)/2;
near(curve.strokeTimeS,exactTime,2e-7,'Independent viscous ramp time');near(curve.end.speedRadS,drive/B*(1-Math.exp(-lambda*exactTime)),2e-7,'Independent viscous end speed');
const variable=A.integrateStroke(p,{...constant,motorPeakNm:40},zero,{steps:1200});
ok(variable.complete,'Variable-inertia stroke completes');for(const row of variable.rows){near(row.kineticJ,40*row.sRad,2e-11,'Variable-J work identity');near(.5*row.totalInertiaKgM2*row.speedRadS**2,row.kineticJ,2e-11);near(row.lowerAbsoluteVelocityRadS,-row.hipVelocityRadS,1e-10);near(row.relativeKneeVelocityRadS,-2*row.hipVelocityRadS,1e-10);}
const stalled=A.integrateStroke(rod,{...constant,motorPeakNm:0},zero);ok(stalled.status==='stalled-at-start'&&stalled.rows.length===1,'Zero drive remains at rest');
const cut=A.integrateStroke(rod,{...constant,gearboxOutputMaxRpm:10},zero);ok(cut.status==='speed-limit'&&!cut.complete,'Speed limit terminates without extrapolation');near(cut.end.speedRadS,10*2*Math.PI/60,1e-10);
const gravityP={...p,springEnabled:false},jumpHardware={...constant,motorPeakNm:200,rotorInertiaKgM2:.001,ratio:4};
const jump=A.estimateJump(gravityP,jumpHardware,zero,{steps:1200});ok(jump.complete&&jump.estimatedJumpHeightM>0,'Jump screen yields conditional apex');
const dzChassis=.6*(Math.sin(p.te*A.RAD)-Math.sin(p.tc*A.RAD));
const expectedGravity=9.81*(8.75*dzChassis+1*.75*dzChassis+1*.25*dzChassis);
near(jump.end.gravityDeltaJ,expectedGravity,1e-11,'Independent all-body grounded gravity');near(jump.end.kineticJ,200*4*length-expectedGravity,2e-10,'Jump work ledger');
near(jump.estimatedJumpHeightM,jump.takeoffComSpeedMS**2/(2*p.g),1e-12);ok(jump.excludedInternalOrHorizontalKineticJ>=-1e-9,'Rotor/internal energy not allocated to vertical COM');
ok(A.estimateJump(gravityP,{...jumpHardware,rotorInertiaKgM2:.02},zero,{steps:1200}).estimatedJumpHeightM<jump.estimatedJumpHeightM,'More reflected rotor inertia lowers COM apex at same work');
throws(()=>A.estimateJump({...p,L3:301},h,zero),/equal links/);throws(()=>A.estimateJump({...p,te:90},h,zero),/singular/);
const pitch=A.estimateJump({...gravityP,alpha:20},jumpHardware,zero,{steps:1200});
// Rod COM offsets rotate as well as chassis travel. Both 1kg link COMs add
// 0.5 L Δcos(q) sin(alpha); a chassis-only cos(alpha) shortcut misses this.
const rotatedRodOffset=9.81*.3*(Math.cos(p.te*A.RAD)-Math.cos(p.tc*A.RAD))*Math.sin(20*A.RAD);
near(pitch.end.gravityDeltaJ,expectedGravity*Math.cos(20*A.RAD)+rotatedRodOffset,2e-11,'Full-body world gravity includes mounting alpha');
const calculated=A.calculate({id:'test',name:'V4.5',params:p},h,{steps:200});ok(calculated.cases.length===3&&A.plotSpecs(calculated).length===9,'Three loss cases and nine categorized Plotly charts');
ok(A.plotSpecs(calculated).find(x=>x.id==='actuator-jump-height').traces.some(t=>t.name==='Target COM height'),'Target height plot marker present');
ok(JSON.stringify(p)===original,'All source geometry/masses unchanged');
for(const spec of A.plotSpecs(calculated))for(const trace of spec.traces){ok(trace.type==='scatter','Offline BASIC-compatible scatter');ok(trace.x.length===trace.y.length,'Trace dimensions');ok(trace.y.every(v=>v===null||Number.isFinite(v)),'Finite or missing trace values');}

// Minimal dependency-free DOM exercises the real UI handlers; not browser QA.
const decode=s=>String(s).replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
class Element{
  constructor(tag='div',attrs={}){this.tagName=tag.toUpperCase();this.attrs={...attrs};this.children=[];this.parentNode=null;this.hidden='hidden'in attrs;this.checked='checked'in attrs;this.dataset={};this._value=attrs.value;this._text='';this.listeners={};for(const[k,v]of Object.entries(attrs))if(k.startsWith('data-'))this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v;this.classList={add:(...c)=>{this.attrs.class=[...(this.attrs.class||'').split(' '),...c].join(' ');}};}
  set innerHTML(html){this.children=[];this._text='';const stack=[this];for(const token of String(html).match(/<[^>]*>|[^<]+/g)||[]){if(token.startsWith('</')){if(stack.length>1)stack.pop();continue;}if(token.startsWith('<')){const tag=token.match(/^<([\w-]+)/)?.[1];if(!tag)continue;const attrs={};for(const m of token.slice(tag.length+1,-1).matchAll(/([\w-]+)(?:="([^"]*)"|='([^']*)'|=([^\s>]+))?/g))attrs[m[1]]=decode(m[2]??m[3]??m[4]??'');const child=new Element(tag,attrs);stack.at(-1).append(child);if(!['input','br','hr','img'].includes(tag)&&!token.endsWith('/>'))stack.push(child);}else stack.at(-1)._text+=decode(token);}}
  get textContent(){return this._text+this.children.map(x=>x.textContent).join('');}set textContent(v){this._text=String(v);this.children=[];}
  get value(){if(this.tagName==='SELECT')return this._value??this.querySelector('option')?.value??'';return this._value??(this.tagName==='OPTION'?this.attrs.value??this.textContent:'');}set value(v){this._value=String(v);}
  append(x){x.parentNode=this;this.children.push(x);}insertAdjacentHTML(_,html){const temp=new Element();temp.innerHTML=html;for(const child of temp.children)this.append(child);}
  matches(s){if(s.startsWith('#'))return this.attrs.id===s.slice(1);if(s.startsWith('.'))return(this.attrs.class||'').split(' ').includes(s.slice(1));const m=s.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);return m?(m[2]===undefined?m[1]in this.attrs:this.attrs[m[1]]===m[2]):this.tagName.toLowerCase()===s;}
  querySelectorAll(selector){const ss=selector.split(',').map(s=>s.trim()),out=[];const walk=n=>{for(const c of n.children){if(ss.some(s=>c.matches(s)))out.push(c);walk(c);}};walk(this);return out;}querySelector(s){return this.querySelectorAll(s)[0]||null;}
  closest(s){for(let n=this;n;n=n.parentNode)if(n.matches(s))return n;return null;}
  setAttribute(k,v){this.attrs[k]=String(v);}addEventListener(k,f){(this.listeners[k]??=[]).push(f);}removeEventListener(k,f){this.listeners[k]=(this.listeners[k]||[]).filter(x=>x!==f);}
}
const document={getElementById:()=>null,createElement:tag=>new Element(tag)},host=new Element('section'),timers=new Map(),events={},charts=[],artifacts=[];let timerId=0,sub,selectCallback,compareCallback,writes=0,current={id:'design-test',name:'V4.5 mock',params:p};
const sourceCombo={motorId:'m',gearboxId:'g',name:'Source combo',gearRatio:10,efficiency:null,peakMotorTorqueNm:8,rotorInertiaKgM2:.0001,gearboxInputInertiaKgM2:.00001,gearPeakOutputNm:100,gearMaxInputRpm:6000,gearMaxOutputRpm:null,motorNoLoadRpm:null};
const studio={getSnapshot:()=>JSON.parse(JSON.stringify(current)),subscribe:fn=>{sub=fn;return()=>{sub=null;}},saveArtifact:async(name,value)=>artifacts.push({name,value}),setMotorConfig(){writes++;},setSolverConfig(){writes++;},applySnapshot(){writes++;}};
const catalog={mount(node,callbacks){selectCallback=callbacks.onSelect;compareCallback=callbacks.onCompare;return {ready:Promise.resolve(),destroy(){},getSelection:()=>sourceCombo,getComparisons:()=>[]};}};
const context=vm.createContext({console,document,KinefoldActuatorCalculator:A,setTimeout:fn=>{timers.set(++timerId,fn);return timerId;},clearTimeout:id=>timers.delete(id),addEventListener:(k,fn)=>(events[k]??=[]).push(fn),removeEventListener(){},KinefoldPlotly:{purge(){},react:async(node,traces,layout)=>{charts.push({node,traces,layout});}}});
vm.runInContext(fs.readFileSync(path.join(__dirname,'actuator-calculator-ui.js'),'utf8'),context);
const ui=context.KinefoldActuatorCalculatorUI.mount(host,studio,catalog),flush=()=>{const jobs=[...timers.values()];timers.clear();jobs.forEach(fn=>fn());},$=s=>host.querySelector(s),dispatch=(kind,node)=>{for(const fn of host.listeners[kind]||[])fn({target:node});};
selectCallback(sourceCombo);flush();ok(ui.getResult()!==null,'Catalog selection immediately calculates');ok(charts.length===9,'All initial UI charts mounted');ok($('[data-actuator-profile]').textContent.includes('8.75'),'Chassis mass appears in profile identity block');ok($('[data-actuator-profile]').textContent.includes('11.25'),'All profile masses shown');
ok($('[data-hardware="ratio"]').readOnly,'Source SKU ratio is read-only');ok(host.textContent.includes('6000 rpm'),'Unsourced speed assumption disclosed');ok(host.textContent.includes('not measured'),'Preliminary drag assumptions disclosed');ok(host.textContent.includes('Relative knee')||host.textContent.includes('relative-knee'),'Hip/knee rates distinguished');
const previous=ui.getResult().cases[1].free.strokeTimeS;const damping=$('[data-loss="1"]');damping.value=20;dispatch('input',damping);flush();ok(ui.getResult().cases[1].free.strokeTimeS>previous,'Loss input recomputes without Run');
const before=JSON.stringify(current);current={...current,params:{...current.params,alpha:20}};sub(current);flush();near(ui.getResult().profile.params.alpha,20);ok(JSON.stringify(current)===JSON.stringify({...JSON.parse(before),params:{...p,alpha:20}}),'Subscription reads profile without mutation');
compareCallback([sourceCombo,{...sourceCombo,name:'Second exact SKU',gearRatio:20}]);flush();ok(ui.getResult().compare.length===2,'Pinned source combinations calculate');ok(charts.at(-1).traces[0].x.length===2,'Exact combination comparison scatter');
const beltInput=$('[data-hardware="hipBeltRatio"]');ok(beltInput!==null,'editable belt input exists');beltInput.value='2';dispatch('input',beltInput);flush();near(ui.getState().hardware.totalRatio,20);ok(ui.getResult().compare.every(c=>c.hardware.hipBeltRatio===2),'pinned candidates use same editable belt');beltInput.value='1';dispatch('input',beltInput);flush();
const blank=$('[data-hardware="motorNoLoadRpm"]');blank.value='';dispatch('input',blank);flush();ok(ui.getResult()===null,'Missing motor speed blocks rather than zero-fills');ok($('[data-actuator-error]').textContent.includes('motorNoLoadRpm'),'Missing input message visible');blank.value='6000';dispatch('input',blank);flush();ok(ui.getResult()!==null,'Valid input recovers');
(async()=>{await host.listeners.click[0]({target:$('[data-action="export"]')});ok(artifacts.length===1&&artifacts[0].value.schema==='kinefold/actuator-calculator-v1','Explicit export uses app-folder artifact service');ok(artifacts[0].value.profile.params.m2===1,'Export captures finite link masses');ok(writes===0,'No physical profile/config/library writes');ui.destroy();ok(sub===null,'Subscription cleaned up');console.log('PASS '+checks+' actuator analytical/DOM assertions; '+charts.length+' scatter chart mounts; no live browser or hardware validation.');})().catch(e=>{console.error(e);process.exitCode=1;});
