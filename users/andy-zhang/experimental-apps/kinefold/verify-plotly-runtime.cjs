/** Verify Plotly ownership, cursor/theme state and delayed graph retirement.
 * Run node verify-plotly-runtime.cjs; inputs are stub DOM and deferred Plotly
 * operations (unitless). Outputs lifecycle assertions, including replacement
 * during in-flight rendering. Actual pointer/layout behavior needs browser QA.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const listeners={},frames=[],calls=[],errors=[];let ink='#111',mutation,delayNext=false,release;
let active=0,maxActive=0;
const document={documentElement:{},body:{},addEventListener:(n,f)=>listeners[n]=f,querySelectorAll:()=>[]};
const Plotly={
 react:async(n,t,l,c)=>{active++;maxActive=Math.max(maxActive,active);n._fullLayout={};calls.push(['react',t,l,c,n]);if(delayNext){delayNext=false;await new Promise(r=>release=r);}assert.ok(n._fullLayout,'layout survives pending react');n.layout=l;active--;return n;},
 relayout:async(n,l)=>{active++;maxActive=Math.max(maxActive,active);assert.ok(n._fullLayout);Object.assign(n.layout,l);calls.push(['relayout',l,n]);active--;},
 Plots:{resize:async n=>{active++;maxActive=Math.max(maxActive,active);assert.ok(n._fullLayout);calls.push(['resize',n]);active--; }},
 purge:n=>{calls.push(['purge',n]);delete n._fullLayout;}
};
const context={document,Plotly,window:{addEventListener:(n,f)=>listeners[n]=f},ResizeObserver:class{observe(){}unobserve(){}},MutationObserver:class{constructor(f){mutation=f;}observe(){}},getComputedStyle:()=>({getPropertyValue:k=>k==='--ink'?ink:'#abc'}),requestAnimationFrame:f=>(frames.push(f),frames.length),console:{error:(...a)=>errors.push(a)}};
vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/plotly-runtime.js','utf8'),context);
function host(id){return {id,dataset:{},classList:{add(){}},isConnected:true,clientWidth:700,getClientRects(){return this.visible?[{}]:[];},visible:true,matches:()=>true,querySelectorAll:()=>[]};}
const node=host('first'),P=context.KinefoldPlotly;let count=0;const ok=(v,m)=>{assert.ok(v,m);count++;};
const flush=()=>{while(frames.length)frames.shift()();};
const settle=async()=>{for(let i=0;i<8;i++){await new Promise(setImmediate);flush();}};
(async()=>{
 await P.react(node,[{line:{color:'var(--ink)'}}],{shapes:[{name:'bound'}]},{key:'stable'});await settle();
 ok(calls[0][1][0].line.color==='#111','computed colors');ok(calls[0][3].modeBarButtonsToRemove.includes('toImage'),'no download camera');ok(node.layout.uirevision==='stable','zoom identity');
 const before=calls.filter(c=>c[0]==='react').length;P.cursor(node,2.48);await settle();ok(calls.filter(c=>c[0]==='react').length===before,'cursor relayout only');ok(node.layout.shapes.some(s=>s.name==='bound'),'physical bounds retained');
 node.visible=false;const n=calls.length;P.cursor(node,3);await settle();ok(calls.length===n&&node.dataset.cursorTime==='3','hidden cursor cached');
 node.visible=true;P.resize(node);await settle();ok(node.layout.shapes.find(s=>s.name==='kinefold-cursor').x0===3,'reopen applies cursor');
 ink='#eee';listeners['kinefold-theme-change']();await settle();ok(node.layout.shapes.find(s=>s.name==='kinefold-cursor').x0===3,'theme sought time');ok(node.layout.font.color==='#eee','theme repaints');
 const prior=calls.length;mutation([{removedNodes:[{...node,nodeType:1}]}]);await settle();ok(calls.length===prior,'connected reinsert not purged');
 // Same physical node retired/reinserted while an old render is still in flight.
 delayNext=true;const old=P.react(node,[],{title:'old'});await new Promise(setImmediate);
 const purges=calls.filter(c=>c[0]==='purge').length;P.purge(node);P.cursor(node,4);
 const latest=P.react(node,[],{title:'latest'});release();await Promise.all([old,latest]);await settle();
 ok(node.layout.title==='latest','new generation wins');ok(calls.filter(c=>c[0]==='purge').length===purges,'retirement cannot destroy reactivated host');
 // Detached replacement: purge must wait until its in-flight promise is done.
 const detached=host('detached');delayNext=true;const pending=P.react(detached,[],{});await new Promise(setImmediate);
 P.cursor(detached,1);P.purge(detached);detached.isConnected=false;
 ok(!calls.some(c=>c[0]==='purge'&&c[1]===detached),'purge deferred during render');release();await pending;await settle();
 ok(calls.filter(c=>c[0]==='purge'&&c[1]===detached).length===1,'retired host purged once after settle');
 ok(maxActive===1,'react resize relayout serialized');ok(errors.length===0,'cancelled obsolete work produces no errors');
 const originalReact=Plotly.react;Plotly.react=async()=>{throw Error('current render failure');};await assert.rejects(P.react(node,[],{}),/current render failure/);ok(true,'current failures are reported to caller');Plotly.react=originalReact;await P.react(node,[],{});await settle();ok(node._fullLayout,'queue recovers after a current failure');
 P.purge(node);await settle();ok(calls.at(-1)[0]==='purge','final purge');
 console.log('PASS '+count+' Plotly lifecycle assertions');
})().catch(e=>{console.error(e);process.exitCode=1;});
