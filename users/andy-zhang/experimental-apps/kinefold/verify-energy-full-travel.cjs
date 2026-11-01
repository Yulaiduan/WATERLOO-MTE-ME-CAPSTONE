/** Check exact 90-degree Energy endpoints and the pure working-design proposal.
 * Run node verify-energy-full-travel.cjs. Inputs temporary mm/deg/kg/N project
 * fixtures; outputs assertions for geometry, independent signed work and guards.
 * No services/profiles modified. Singular endpoints are energy screens only;
 * these checks do not establish contact, finite-speed takeoff or hardware travel.
 */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),c=vm.createContext({});
for(const f of ['reference-v4.js','model.js','variables.js','project-store.js','energy-analysis.js'])vm.runInContext(fs.readFileSync(__dirname+'/'+f,'utf8'),c,{filename:f});
const P=c.KinefoldProjects,A=c.KinefoldEnergyAnalysis,V=c.KinefoldV4,M=c.Kinefold,R=Math.PI/180;
const copy=x=>{c.raw=JSON.stringify(x);return vm.runInContext('JSON.parse(raw)',c);};let count=0;
const ok=(v,msg)=>{assert.ok(v,msg);count++;},near=(a,b,t=1e-7)=>ok(Math.abs(a-b)<t,`${a} != ${b}`);
for(const alpha of [0,20])for(const phi0 of [0,10])for(const kind of ['landing','jump']){
 const p=copy(P.v45());p.params.alpha=alpha;p.params.phi0=phi0;p.energyConfig=copy({...P.energyDefaults,dropHeightMm:2000});p.torqueTargetConfig=copy({...P.torqueTargetDefaults,jumpHeightMm:2000});
 const other=kind==='landing'?'jump':'landing',otherBand=A.travelRange(p,other);p.energyConfig.travelRanges=copy({[other]:{minClearanceMm:otherBand.minClearanceMm,maxClearanceMm:otherBand.maxClearanceMm}});
 const initial=JSON.stringify(p),full=A.fullTravelProject(p,kind),z=A.workspace(full,kind,{includeLegMasses:true}),band=A.travelRange(full,kind),ref=M.reference(full.params),te=(180+phi0)/2;
 ok(JSON.stringify(p)===initial,'full travel proposal is pure');near(full.params.te,te);near(full.params.tc,te+90);near(z.angularTravelDeg,90,1e-12);near(z.angularTravelRad,Math.PI/2,1e-12);
 assert.equal(band.qEndDeg,full.params.te);count++;assert.equal(band.qStartDeg,full.params.tc);count++;
 ok(JSON.stringify(full.energyConfig.travelRanges[other])===JSON.stringify(p.energyConfig.travelRanges[other]),'other case override preserved');
 ok(JSON.stringify(full.solverConfig)===JSON.stringify(p.solverConfig)&&JSON.stringify(full.motorConfig)===JSON.stringify(p.motorConfig)&&JSON.stringify(full.caseConfig)===JSON.stringify(p.caseConfig),'physical controller/settings retained');
 for(const key of ['springK','p0','hornR','Su','Sv','alpha','phi0','m1','m2','m3','m6'])near(full.params[key],p.params[key]);
 ok(z.fullTravelBoundaryWarning.includes('zero vertical Jacobian'),'finite endpoint does not claim dynamic takeoff');
 const body=q=>{const s=V.VSL.state(ref,q),h=full.params.rw-s.Pg[1],p=full.params;return p.g/1000*(p.m1*h+p.m2*(h+s.Bg[1]/2)+p.m3*(h+(s.Bg[1]+s.Pg[1])/2)+p.m5*(h+s.Bg[1])+p.m6*p.rw);};
 const gravity=body(z.qEndDeg)-body(z.qStartDeg),spring=V.VSLSpring.state(ref,z.qEndDeg).energy-V.VSLSpring.state(ref,z.qStartDeg).energy,m=full.params;
 const energy=kind==='jump'?gravity+spring+(m.m1+m.m2+m.m3+m.m5+m.m6)*m.g*2:(m.m1+m.m2+m.m3+m.m5)*m.g*2-gravity-spring;
 near(z.workJ,energy);near(z.requiredJointNm,Math.max(0,energy/(Math.PI/2)));
 const edited=A.travelRangeFromAngles(full,kind,full.params.tc-5,full.params.te+10);const next=copy(full);next.energyConfig.travelRanges[kind]=copy(edited);near(A.workspace(next,kind,{includeLegMasses:true}).angularTravelDeg,75);
 ok(JSON.stringify(P.decode(copy(full)).project.energyConfig.travelRanges)===JSON.stringify(full.energyConfig.travelRanges),'full endpoints portable');
 for(const q of [full.params.te,full.params.tc]){const drawing=M.evaluate({...full.params,theta2:q});ok(drawing.valid&&drawing.C.every(Number.isFinite)&&Number.isFinite(drawing.spring.force),'spring/preview valid at exact boundary');}
}
const legacy=copy(P.v45()),before=JSON.stringify(legacy);near(A.workspace(legacy,'jump',{includeLegMasses:true}).angularTravelDeg,65);near(A.workspace(legacy,'landing',{includeLegMasses:true}).angularTravelDeg,42+1/3);ok(JSON.stringify(legacy)===before,'legacy65 values not rewritten');
const reversing=copy(legacy);reversing.params.te=85;reversing.params.tc=100;assert.throws(()=>A.mechanicalTravel(reversing),/crosses/);count++;
const excessive=copy(legacy);excessive.params.te=90;excessive.params.tc=181;assert.throws(()=>A.mechanicalTravel(excessive),/90/);count++;
const floor=copy(legacy);floor.caseConfig=copy({...P.caseDefaults,undersideOffsetMm:300});assert.throws(()=>A.fullTravelProject(floor,'landing'),/below the floor/);count++;
const badSpring=copy(legacy);badSpring.params.Su=0;badSpring.params.Sv=0;assert.throws(()=>A.fullTravelProject(badSpring,'landing'));count++;
console.log('PASS '+count+' exact90 Energy geometry, work, proposal purity, metadata and boundary guards.');
