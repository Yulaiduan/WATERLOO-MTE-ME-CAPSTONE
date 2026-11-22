/** Verify supply equations, catch boundaries and static payload. Run node verify-supplies.cjs.
 * Uses app defaults (mm/deg/kg/Nm/W/s); no workbook/profile writes. Numerical
 * and analytical agreement only, not measured motor or drop performance.
 */
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path');
const dir=__dirname,live=__dirname;
const html=fs.readFileSync(dir+'/v7-springlab.html','utf8'),scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].filter(m=>!m[1].includes('src=')).slice(0,2).map(m=>m[2]).join('\n'),c=vm.createContext({console});
vm.runInContext(scripts+'\n'+fs.readFileSync(dir+'/fall-model.js','utf8')+'\n'+fs.readFileSync(dir+'/motor-limits.js','utf8'),c);
const p0=JSON.parse(fs.readFileSync(live+'/v7-default-library.json')).rows[0].snapshot.parameters,supplies=JSON.parse(fs.readFileSync(dir+'/power-supply-configs.json'));
let checks=0;function run(p,h){c.p=p;c.h=h;return vm.runInContext('VSLFall.solve(p,h,{samples:240})',c)}
for(const s of supplies)for(const kv of [110,140,170]){const p={...p0,motorKV:kv,motorKvLNOverride:null,motorKtOverride:null,motorIndependent:'sf',speedSF:1,supplyVmaxLN:s.vmax,supplyIpeak:s.peak,supplyIcont:s.continuous,supplyOverheatS:s.overheat,fallPowerCeiling:s.power,fallSolveMode:'maximize'},r=run(p,.25);assert(r.gearRatio>0,r.reason);const rpm=r.valid?r.rows[0].qdot*60/(2*Math.PI):null;assert(Math.abs(r.torqueCeilingNm-r.motorKt*120*r.gearRatio)<1e-8);if(rpm)assert(Math.abs(r.gearRatio*rpm-s.vmax*Math.sqrt(3)*kv)<1e-7);checks+=3;}
const p={...p0,motorKV:110,motorKvLNOverride:null,motorKtOverride:null,motorIndependent:'sf',speedSF:1,supplyVmaxLN:19.11,supplyIpeak:120,supplyIcont:27.9,supplyOverheatS:2.213,fallPowerCeiling:625};c.p=p;
const start=Date.now(),heights=vm.runInContext('VSLMotorLimits.heights(p)',c);console.log('heights',JSON.stringify(heights),'ms',Date.now()-start);
assert(heights.rows[0].valid);assert(heights.rows[1].valid);assert(heights.rows[2].valid);assert(heights.rows[1].heightM<=heights.rows[0].heightM+1e-6);assert(heights.rows[2].heightM<=heights.rows[1].heightM+1e-6);assert(heights.rows[2].timeS<=2.213);assert(heights.rows[1].powerW<=625.001);checks+=7;
const gr=heights.rows[0].gearRatio;c.gr=gr;const capacity=vm.runInContext('VSLMotorLimits.payload(p,gr)',c);console.log('payload',JSON.stringify(capacity));assert(capacity.valid);assert(capacity.perLegKg>0);const test={...p,mp:capacity.totalKg,m1:(p.mc+capacity.totalKg)/4};for(let i=0;i<=400;i++){const t=p.te+(p.tc-p.te)*i/400;c.test=test;c.t=t;const s=vm.runInContext('VSLStatic.solve({...test,beta:0,Fy:0,Fz:VSLSpring.totalMass(test)*test.g,loadMode:"yz"},t,false)',c);assert(Math.abs(s.tau2)<=capacity.capNm+1e-4);checks++;}
console.log({checks});

// Closed-form 1G payload with no spring or moving mass at alpha=0.
c.p={...p,m1:p.mc/4,mp:0,m2:0,m3:0,m5:0,m6:0,springEnabled:false,alpha:0};
const analytic=vm.runInContext('VSLMotorLimits.payload(p,100)',c),expected=(1.5*60/(2*Math.PI)/(Math.sqrt(3)*110)*27.9*100)/(2*9.81*p.L2/1000)-p.mc/4;
assert(analytic.valid);assert(Math.abs(analytic.perLegKg-expected)<1e-8);
// Tight thermal cap must lower the power-only boundary.
c.p={...p,supplyVmaxLN:13.44,supplyIcont:9.7,supplyOverheatS:.1357,fallPowerCeiling:2500};
const thermal=vm.runInContext('VSLMotorLimits.heights(p)',c);assert(thermal.rows[2].valid);assert(thermal.rows[2].timeS<=.1357);assert(thermal.rows[2].heightM<thermal.rows[1].heightM*.98);
console.log('Closed-form payload and active thermal boundary checks passed.');
