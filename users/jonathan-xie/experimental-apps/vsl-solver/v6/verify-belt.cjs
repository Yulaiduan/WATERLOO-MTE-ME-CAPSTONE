/** Verify V5 AB fall load, Link2-relative velocity/power and CSV handoff.
 * Run: node verify-belt.cjs [--output]. Inputs local mm/deg/kg/N/Nm fall models.
 * Outputs numerical assertion report, optional JSON; never writes workbooks.
 * Compares massless-link dynamics with existing static FBDs; no belt rating.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),dir=__dirname;
const html=fs.readFileSync(path.join(dir,'v6-springlab.html'),'utf8'),scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].filter(m=>!m[1].includes('src=')).map(m=>m[2]);
const {VSLFall:f,VSLStatic:s,VSLSpring:sp,VSLFallUI:ui,VSLFallAnalysis:a}=vm.runInNewContext(scripts.slice(0,2).join('\n')+'\n'+['plot-utils.js','fall-model.js','fall-analysis.js','fall-ui.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n')+';({VSLFall,VSLStatic,VSLSpring,VSLFallUI,VSLFallAnalysis});');
let checks=0;const ok=(v,msg)=>{assert(v,msg);checks++;},near=(a,b,t=1e-8)=>ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<t,`${a} != ${b}`);
const p={...s.defaults};
for(const alpha of [-30,0,15,30])for(const ratio of [1.666,2])for(const Tab0 of [0,100]){
 const pp={...p,alpha,ra:p.rb*ratio,Tab0,m1:7,m2:1,m3:.5,m5:.1,m6:.15},r=f.withBelts(pp,f.solve(pp,.25,{samples:80}));ok(r.valid,r.reason);const dyn={...pp,m1:sp.totalMass(pp),m2:0,m3:0,m5:0,m6:0,loadMode:'yz',Fy:0,beta:0};
 for(const row of r.rows){const st=s.solve({...dyn,Fz:row.Fz},row.theta,false);ok(st.valid,st.reason);near(row.deltaTab,st.ab.delta);near(row.TabU,st.ab.U);near(row.TabL,st.ab.L);near(row.TabU-row.TabL,row.deltaTab);near(row.vab,pp.ra/1000*(-row.vz/row.J));near(row.Pab,row.deltaTab*row.vab);near(row.Pab,st.ab.Mleft*(-row.qdot));near(row.Pab,-st.ab.Mright*(-ratio*row.qdot));}
 near(r.rows.at(-1).vab,0);near(r.rows.at(-1).Pab,0);near(r.peaks.Pab,Math.max(...r.rows.map(x=>Math.abs(x.Pab))));near(r.peaks.deltaTab,Math.max(...r.rows.map(x=>Math.abs(x.deltaTab))));near(r.peaks.vab,Math.max(...r.rows.map(x=>Math.abs(x.vab))));near(r.holdingBelt.Pab,0);near(r.holdingBelt.vab,0);
}
const base=f.withBelts(p,f.solve(p,.25)),pre=f.withBelts({...p,Tab0:123},f.solve(p,.25));for(let i=0;i<base.rows.length;i++){near(base.rows[i].deltaTab,pre.rows[i].deltaTab);near(base.rows[i].Pab,pre.rows[i].Pab);near(pre.rows[i].TabU-base.rows[i].TabU,123);near(pre.rows[i].TabL-base.rows[i].TabL,123);}
ok(base.peaks.Pab<base.peaks.deltaTab*base.peaks.vab,'power peak must be computed pointwise');
const negative=f.withBelts({...p,alpha:-30},f.solve({...p,alpha:-30},.25));ok(negative.rows.some(x=>x.deltaTab<0));ok(negative.rows.some(x=>x.Pab<0));
const bad={...p,L2:70,L3:70,ra:50,rb:25,springEnabled:false},invalid=f.withBelts(bad,f.solve(bad,.25));ok(invalid.valid);ok(invalid.rows.every(x=>x.deltaTab===null&&x.vab===null&&x.Pab===null));ok(invalid.warnings.some(x=>x.includes('AB')));
ok(a.key(p,.25)!==a.key({...p,Tab0:10},.25),'span preload must invalidate cached CSV study');
const lines=ui.csv(base,p).split('\n').filter(x=>!x.startsWith('#')),head=lines[0].split(','),data=lines.slice(1).map(x=>x.split(','));ok(data.length===base.rows.length+1);ok(data.every(x=>x.length===head.length));near(Number(data.at(-1)[head.indexOf('P_ab_link2_W')]),0);ok(data.at(-1)[head.indexOf('phase')]==='holding');
const report={checks,defaultPeaks:base.peaks,peakPoses:base.peakPoses,brakingEndDeltaN:base.rows.at(-1).deltaTab,holdingDeltaN:base.holdingBelt.deltaTab,frame:'Link2 relative; compression-positive belt circulation; TU-TL signed difference',scope:'massless-link vertical point-mass approximation; not a manufacturer belt rating'};if(process.argv.includes('--output'))fs.writeFileSync(path.join(dir,'v6-belt-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
