/** Verify restored V5 grid data, SVG output and braking/holding endpoint.
 * Run: node verify-ui.cjs [--output] [--svg path]. Reads local code, mm/deg/kg/N/Nm/m/s.
 * Produces assertions and optional JSON/SVG plots; no browser or workbook writes.
 * This checks data/rendering contracts, not actual browser layout or hardware.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),dir=__dirname;
const html=fs.readFileSync(path.join(dir,'v5-fall.html'),'utf8'),scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].filter(m=>!m[1].includes('src=')).map(m=>m[2]);
const files=['plot-utils.js','fall-model.js','fall-analysis.js','fall-ui.js'];for(const file of files)new vm.Script(fs.readFileSync(path.join(dir,file),'utf8'));for(const script of scripts)new vm.Script(script);
const {VSLFall:fall,VSLStatic:stat,VSLSpring:spring,VSLFallUI:ui,VSLPlot:plot}=vm.runInNewContext(scripts.slice(0,2).join('\n')+'\n'+files.map(f=>fs.readFileSync(path.join(dir,f),'utf8')).join('\n')+';({VSLFall,VSLStatic,VSLSpring,VSLFallUI,VSLPlot});');
let checks=0;const ok=(v,msg)=>{assert(v,msg);checks++;},near=(a,b,t=1e-9)=>{ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} != ${b}`);};
const p={...stat.defaults},study=fall.study(p,.25,{min:0,max:30},{samples:160,sweepSamples:80,heightRange:{min:0,max:.8}}),held=ui.holdingRow(study.current),staticHeld=stat.solve({...p,loadMode:'yz',beta:0,Fy:0,Fz:spring.totalMass(p)*p.g},p.tc);
near(held.aG,0);near(held.Fz,spring.totalMass(p)*p.g);near(held.tau2,staticHeld.tau2);near(held.theta,p.tc);near(held.time,study.current.catchTimeS);near(held.vz,0);ok(study.current.rows.at(-1).aG>0);ok(study.current.rows.at(-1).tau2<0);
for(const alpha of [0,15,30])for(const h of [.1,.25,.8]){const pp={...p,alpha},r=fall.solve(pp,h),hold=ui.holdingRow(r),ss=stat.solve({...pp,loadMode:'yz',beta:0,Fy:0,Fz:spring.totalMass(pp)*pp.g},pp.tc);ok(r.valid,r.reason);near(hold.tau2,ss.tau2);near(hold.aG,0);near(hold.Fz,spring.totalMass(pp)*pp.g);near(ss.tau4,0);}
const rendered=[];
for(const includeZero of [false,true])for(const absolute of [false,true])for(const analysisMode of [false,true])for(const row of ui.rows)for(const axis of ui.axes){
 const state={...ui.defaults(),includeZero,absolute,analysisMode},chart=ui.renderPlot(row,axis,study,p,state),data=ui.plotData(row.key,axis,study,absolute),peak=['alpha','height'].includes(axis);
 ok(chart.attributes.signal===row.key);ok(chart.attributes.axis===axis);ok(!/NaN|Infinity|undefined/.test(chart.markup));ok(data.length>0);ok(chart.markup.includes('data-signal="'+row.key+'"'));ok(!chart.markup.includes('Catch duration'));
 const values=data.map(r=>r.y).filter(Number.isFinite);ok(values.every(v=>v>=chart.attributes.yMin-1e-8&&v<=chart.attributes.yMax+1e-8));
 if(includeZero){ok(chart.attributes.yMin<=0&&chart.attributes.yMax>=0);ok(chart.markup.includes('data-reference="zero"'));if(values.every(v=>v>=0))near(chart.attributes.yMin,0);if(values.every(v=>v<=0)&&values.some(v=>v<0))near(chart.attributes.yMax,0);}
 if(absolute||peak)ok(values.every(v=>v>=0));
 if(!peak){near(data.at(-1).x,axis==='theta'?p.tc:study.current.catchTimeS);ok(data.at(-1).holding);if(row.key==='aG'){near(data.at(-1).y,0);ok(chart.markup.includes('data-holding-switch="true"'));ok(chart.markup.includes('hold 0g'));}if(row.key==='tau2')near(data.at(-1).y,absolute?Math.abs(held.tau2):held.tau2);}
 if(row.key==='time'){for(const item of data)if(Number.isFinite(item.y))near(item.y,peak?item.source.catchTimeS:item.source.time);if(axis==='time')for(const item of data)near(item.y,item.x);}
 if(row.key==='dz'&&axis==='height'){ok(data.every(r=>Number.isFinite(r.y)));near(Math.max(...values)-Math.min(...values),0);}
 if(row.key==='vz'&&axis==='alpha')for(const v of values)near(v,study.current.impactSpeed,1e-7);
 // A mode toggle may change the original analyses, never the dedicated fall plot.
 const other=ui.renderPlot(row,axis,study,p,{...state,analysisMode:!analysisMode});ok(other.markup===chart.markup);
 if(!includeZero&&!absolute&&!analysisMode)rendered.push({row:row.key,axis,markup:chart.markup,attributes:chart.attributes});
}
near(plot.bounds([2,3],true).min,0);near(plot.bounds([-3,-2],true).max,0);ok(plot.bounds([2,3],false).min>0);ok(plot.bounds([-3,-2],false).max<0);ok(plot.ticks(-2,3,[0,1]).includes(0));ok(plot.ticks(-2,3,[0,1]).includes(1));
const css=fs.readFileSync(path.join(dir,'v5-ui.css'),'utf8'),source=fs.readFileSync(path.join(dir,'fall-ui.js'),'utf8');ok(css.includes('repeat(4,minmax(230px,1fr))'));ok(css.includes('#masterControls.is-pinned{position:fixed;top:0;'));ok(!css.includes('force-column:not(.driving)'));ok(source.includes("input.type='radio';input.name='vsl-analysis-mode'"));ok(source.includes('Plot absolute magnitudes'));ok(source.includes("const value=$(id).valueAsNumber;try{pause();"));
for(const name of ['plot-utils.js','fall-ui.js','fall-model.js','fall-analysis.js','v5-ui.css'])ok(html.includes(name+'?v=20261028-time'));
const report={checks,charts:rendered.length,grid:{rows:Array.from(ui.rows,r=>r.key),columns:Array.from(ui.axes)},brakingTorqueNm:study.current.rows.at(-1).tau2,holdingTorqueNm:held.tau2,brakingEndAccelerationG:study.current.rows.at(-1).aG,holdingAccelerationG:held.aG,wheelTorqueNm:staticHeld.tau4,scope:'data and SVG contracts; data/SVG checks only; browser layout not checked in this run'};
if(process.argv.includes('--output'))fs.writeFileSync(path.join(dir,'v5-ui-verification.json'),JSON.stringify(report,null,2)+'\n');
if(process.argv.includes('--svg')){let svg='<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1320" viewBox="0 0 1440 1320"><rect width="1440" height="1320" fill="white"/><style>text{font:12px system-ui;fill:#587180}</style>';for(let i=0;i<rendered.length;i++){const c=rendered[i],title=({tau2:'τ₂',aG:'a_z/g',vz:'v_z',dz:'d_z',time:'Elapsed time'})[c.row],axis=({theta:'θ₂',time:'time',alpha:'α (peak)',height:'h (peak)'})[c.axis],x=(i%4)*360,y=Math.floor(i/4)*260;svg+=`<g transform="translate(${x},${y})"><text x="52" y="14" style="font-weight:bold">${title} versus ${axis}</text><g transform="translate(0,20)">${c.markup}</g></g>`;}svg+='</svg>';fs.writeFileSync(path.resolve(process.argv[process.argv.indexOf('--svg')+1]),svg);}
console.log(JSON.stringify(report,null,2));
