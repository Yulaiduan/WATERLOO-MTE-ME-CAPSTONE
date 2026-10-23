/** Exercise actual equilibrium Plotly trace generation without a browser.
 * Run: node verify-equilibrium-plotly.cjs. Inputs: synthetic signed, singular,
 * wrapped and reversed mm/deg/N/Nm rows; outputs assertion count. DOM and Plotly
 * are stubs; actual rendering and pointer interactions require browser QA.
 */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'equilibrium.js'),'utf8');
const plot=source.slice(source.indexOf('function plot('),source.indexOf('\nasync function exportData'));
const nodes=new Map(),captures=[];
function node(id){if(!nodes.has(id))nodes.set(id,{id,dataset:{},querySelectorAll:()=>[],isConnected:false});return nodes.get(id);}
const context={charts:new Map(),retained:new Map(),$:node,selected:(_id,keys)=>new Set(keys),colors:{},labels:{},fmt:String,data:{params:{te:100}},opts:{absolute:false},KinefoldPlotly:{color:v=>v,react:(host,traces,layout)=>{captures.push({traces,layout});return Promise.resolve();}}};
vm.createContext(context);vm.runInContext(plot+';globalThis.run=plot;',context);
let checks=0;function ok(value,message){assert.ok(value,message);checks++;}
function run(rows,extra={}){context.run('test',{rows,x:'x',keys:['tau2'],unit:'N·m',domain:{min:0,max:4},current:1,bounds:[0,4],...extra});return captures.at(-1);}
let out=run([{x:0,tau2:-2},{x:1,tau2:2}],{kind:'torque',absolute:true});
ok(out.traces.length===2,'sign crossing splits magnitude trace');ok(out.traces[0].line.dash==='dash'&&out.traces[1].line.dash==='solid','signed dash survives magnitude');ok(out.traces.every(t=>t.y.every(v=>v>=0)),'magnitude never negative');ok(out.traces[0].y.at(-1)===0&&out.traces[1].y[0]===0,'interpolated zero crossing');
out=run([{x:0,tau2:2},{x:1,tau2:null},{x:2,tau2:3}]);ok(out.traces.length===2,'null gap is not connected');
out=run([{x:0,ab:4,abActive:'U'},{x:1,ab:3,abActive:'L'}],{keys:['ab'],kind:'tension'});ok(out.traces[0].line.dash==='solid'&&out.traces[1].line.dash==='dash','active belt span style');
out=run([{x:0,gammaUV:179,theta2:110},{x:1,gammaUV:-179,theta2:111}],{keys:['gammaUV'],angle:true});ok(out.traces.length===2,'inclination wrap gap');
out=run([{x:0,supportPercent:10,Jz:1},{x:1,supportPercent:-10,Jz:-1}],{keys:['supportPercent'],support:true,leftFactor:.2,includeZero:false});ok(out.traces.length===3,'Jacobian sign gap plus right axis');ok(out.traces[0].y[0]===2&&out.traces[1].y[0]===-2,'kg conversion stays signed');ok(out.layout.yaxis2.range[0]===out.layout.yaxis.range[0]/.2,'dual axis scale');
out=run([{x:0,tau2:1},{x:3,tau2:2},{x:1,tau2:3}],{axis:'dz'});ok(out.traces[0].x.join(',')==='0,3,1','travel parameter order retained');
ok(!source.includes('<svg id="eq-chart-'),'all analytical chart hosts are divs');ok(source.includes("config.axis==='alpha'||config.axis==='beta'"),'diagnostic axis click guard');
out=run([{x:0,supportPercent:null,Jz:0}],{keys:['supportPercent'],support:true,leftFactor:0});ok(out.layout.yaxis2.range.every(Number.isFinite),'zero total mass has finite display range');
console.log(JSON.stringify({status:'PASS',assertions:checks,limitations:'Pure trace tests; browser rendering is separate.'}));
