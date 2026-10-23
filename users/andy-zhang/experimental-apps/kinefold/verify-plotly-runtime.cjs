/** Verify the shared offline Plotly lifecycle without a browser.
 * Run: node verify-plotly-runtime.cjs. Inputs are stub DOM/Plotly calls (unitless).
 * Outputs assertions for theme, cursor, hidden charts and camera configuration.
 * Browser layout/zoom/pointer behavior remains a separate manual check.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const listeners={},frames=[],calls=[];let ink='#111',mutation;
const document={documentElement:{},body:{},addEventListener:(n,f)=>listeners[n]=f,querySelectorAll:()=>[]};
const Plotly={react:async(n,t,l,c)=>{n.layout=l;n._fullLayout={};calls.push(['react',t,l,c]);},relayout:async(n,l)=>{Object.assign(n.layout,l);calls.push(['relayout',l]);},Plots:{resize:async()=>{}},purge:n=>calls.push(['purge'])};
const context={document,Plotly,window:{addEventListener:(n,f)=>listeners[n]=f},ResizeObserver:class{observe(){}unobserve(){}},MutationObserver:class{constructor(f){mutation=f;}observe(){}},getComputedStyle:()=>({getPropertyValue:k=>k==='--ink'?ink:'#abc'}),requestAnimationFrame:f=>(frames.push(f),frames.length),console};
vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/plotly-runtime.js','utf8'),context);
const node={id:'test',dataset:{},classList:{add(){}},isConnected:true,clientWidth:700,getClientRects:()=>node.visible?[{}]:[],visible:true,matches:()=>true,querySelectorAll:()=>[]};
const P=context.KinefoldPlotly;let count=0;const ok=(v,m)=>{assert.ok(v,m);count++;};
const flush=()=>{while(frames.length)frames.shift()();};
(async()=>{
 await P.react(node,[{line:{color:'var(--ink)'}}],{shapes:[{name:'bound'}]},{key:'stable'});flush();await Promise.resolve();
 ok(calls[0][1][0].line.color==='#111','computed CSS colors');ok(calls[0][3].modeBarButtonsToRemove.includes('toImage'),'no browser camera download');ok(node.layout.uirevision==='stable','stable zoom identity');
 const before=calls.filter(c=>c[0]==='react').length;P.cursor(node,2.48);flush();ok(calls.filter(c=>c[0]==='react').length===before,'cursor relayout does not redraw traces');ok(node.layout.shapes.some(s=>s.name==='bound'),'cursor keeps physical bounds');
 node.visible=false;const n=calls.length;P.cursor(node,3);flush();ok(calls.length===n&&node.dataset.cursorTime==='3','hidden charts cache cursor without relayout');
 node.visible=true;P.resize(node);await Promise.resolve();await Promise.resolve();flush();ok(node.layout.shapes.find(s=>s.name==='kinefold-cursor').x0===3,'reopen applies cached cursor');
 ink='#eee';listeners['kinefold-theme-change']();await new Promise(setImmediate);flush();ok(node.layout.shapes.find(s=>s.name==='kinefold-cursor').x0===3,'theme retains sought time');ok(node.layout.font.color==='#eee','theme colors refresh');
 const prior=calls.length;mutation([{removedNodes:[{...node,nodeType:1}]}]);ok(calls.length===prior,'reinserted connected charts are not purged');
 P.purge(node);ok(calls.at(-1)[0]==='purge','removed charts purged');console.log('PASS '+count+' Plotly lifecycle assertions');
})().catch(e=>{console.error(e);process.exitCode=1;});
