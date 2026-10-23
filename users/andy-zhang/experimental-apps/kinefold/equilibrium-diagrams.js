/** Native equilibrium free-body and finite-idler route diagrams.
 * Invocation: load after reference-v4.js and model.js; call renderBodies(params,
 * detailedRaw) or renderSpring(params, Kinefold.evaluate(params)). Inputs use
 * mm/deg/kg/N; output is HTML/SVG and pure world-frame drawing data. All forces
 * and positions transform once from source mechanism-local u/v into x/z.
 * Body geometry shares one scale per figure; force arrows are schematic. This
 * depicts the experimental static model, not measured reactions or packaging.
 */
globalThis.KinefoldEquilibriumDiagrams = (() => {
  'use strict';
  const {VSL, VSLStatic, VSLSpring} = KinefoldV4;
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = (n, digits=3) => Number.isFinite(n) ? (Math.abs(n)<.5*10**-digits?0:n).toLocaleString('en-CA',{maximumFractionDigits:digits}) : '—';
  const world = (p,v) => Kinefold.point(VSL.global(p,v));
  const momentY = (r,f) => (r[2]*f[0]-r[0]*f[2])/1000;
  const sub = (a,b) => a.map((v,i)=>v-b[i]);
  const sum = vs => vs.reduce((a,b)=>a.map((v,i)=>v+b[i]),[0,0,0]);
  const names = {2:'Femur + horn',3:'Tibia + pulley b',4:'Drive rotor c',5:'Compound pulleys d / e',6:'Wheel + pulley f'};
  const colors = {2:'var(--sage)',3:'var(--blue)',4:'var(--purple)',5:'var(--purple)',6:'var(--ink)'};
  function color(name) {
    return name.startsWith('T_ab')?'var(--sage)':name.startsWith('T_cd')?'var(--purple)':name.startsWith('T_ef')?'var(--amber)':name.startsWith('W')?'var(--muted)':name==='F_s'?'var(--amber)':name==='F_n'?'var(--red)':'var(--blue)';
  }
  function bodyData(params, detailedRaw) {
    const p=Kinefold.reference(params),raw=detailedRaw||VSLStatic.solve(p,params.theta2,true);
    if(!raw?.valid||!raw.bodies)return {valid:false,reason:raw?.reason||'Detailed equilibrium is unavailable.'};
    const bodies=[2,3,4,5,6].map(id=>{
      const b=raw.bodies[id],origin=world(p,b.origin);
      const forces=b.forces.map((f,i)=>({index:i+1,name:f.name,point:world(p,f.pos),vector:world(p,f.vec),magnitude:Math.hypot(...f.vec),color:color(f.name)}));
      const couples=b.couples.map(c=>({name:c.name,point:world(p,c.pos),value:c.value}));
      const residualF=sum(forces.map(f=>f.vector));
      const residualM=forces.reduce((v,f)=>v+momentY(sub(f.point,origin),f.vector),0)+couples.reduce((v,c)=>v+c.value,0);
      return {id,name:names[id],origin,ends:b.ends.map(v=>world(p,v)),radius:b.radius||0,angle:b.angle,
        axis:world(p,[b.origin[0]+(b.radius||p.rb)*Math.cos(b.angle*VSL.rad),b.origin[1]+(b.radius||p.rb)*Math.sin(b.angle*VSL.rad)]),
        horn:id===2?world(p,raw.D||VSLSpring.position(p,params.theta2).D):null,
        contact:id===6?world(p,raw.P):null,forces,couples,residualF,residualM,
        radii:id===3?[p.rb]:id===5?[p.rd,p.re]:id===6?[p.rw,p.rf]:id===4?[p.rc]:[]};
    });
    return {valid:true,bodies};
  }
  function springData(params,evaluated) {
    const p=Kinefold.reference(params);
    if(!params.springEnabled)return {valid:false,disabled:true,reason:'Spring assistance is disabled. Cable force and spring torque are zero.'};
    if(evaluated?.valid===false)return {valid:false,reason:evaluated.errors?.join(' ')||'Correct the mechanism geometry before viewing the cable route.'};
    const sp=evaluated?.spring||VSLSpring.state(p,params.theta2);
    if(!sp?.valid)return {valid:false,reason:sp?.reason||evaluated?.errors?.join(' ')||'The cable route is unavailable.'};
    const arc=params.rs>0?Array.from({length:97},(_,i)=>world(p,[p.Su+p.rs*Math.cos(sp.psi-sp.wrap*i/96),p.Sv+p.rs*Math.sin(sp.psi-sp.wrap*i/96)])):[];
    const remoteLength=Math.max(100,Math.min(180,params.hornR*2));
    return {valid:true,A:world(p,[0,0]),D:world(p,sp.D),S:world(p,sp.S),Q:world(p,sp.Q),out:world(p,sp.out),
      Su:world(p,[p.Su,0]),remote:world(p,sp.remote(remoteLength)),arc,radius:params.rs,hornRadius:params.hornR,
      force:world(p,sp.Flocal),forceMagnitude:sp.force,tauS:sp.tauS,tangentLength:sp.tangentLength,
      wrap:sp.wrap,wrapDegrees:sp.wrap/VSL.rad,payout:sp.payout,delta:sp.delta,referencePayout:sp.referencePayout,
      exitDegrees:sp.zetaApplied,energy:sp.energy,slack:sp.slack,localOffset:[p.Su,p.Sv],worldIdler:world(p,[p.Su,p.Sv])};
  }
  const text=(p,label,color='var(--muted)',size=15,attrs='')=>`<text x="${p[0]}" y="${p[1]}" fill="${color}" font-size="${size}" ${attrs}>${esc(label)}</text>`;
  const line=(a,b,color,width=1,attrs='')=>`<path d="M${a.join(',')}L${b.join(',')}" fill="none" stroke="${color}" stroke-width="${width}" ${attrs}/>`;
  const circle=(c,r,color,fill='none',width=1)=>`<circle cx="${c[0]}" cy="${c[1]}" r="${r}" stroke="${color}" stroke-width="${width}" fill="${fill}"/>`;
  function mapper(points,rings=[],width=600,height=440) {
    const pts=points.filter(v=>v&&v.every(Number.isFinite));
    for(const [c,r] of rings)pts.push([c[0]-r,0,c[2]-r],[c[0]+r,0,c[2]+r]);
    const xs=pts.map(v=>-v[0]),ys=pts.map(v=>-v[2]),loX=Math.min(...xs),hiX=Math.max(...xs),loY=Math.min(...ys),hiY=Math.max(...ys);
    const scale=Math.min((width-190)/Math.max(70,hiX-loX),(height-185)/Math.max(70,hiY-loY));
    return {scale,map:v=>[width/2+(-v[0]-(loX+hiX)/2)*scale,200+(-v[2]-(loY+hiY)/2)*scale]};
  }
  function arrow(origin,vector,color,length=60) {
    const mag=Math.hypot(...vector);if(mag<1e-10)return {html:'',end:origin};
    const u=[-vector[0]/mag,-vector[2]/mag],end=origin.map((v,i)=>v+u[i]*length),n=[-u[1],u[0]],back=end.map((v,i)=>v-u[i]*8);
    return {end,html:line(origin,end,color,2)+`<polygon points="${end.join(',')} ${back.map((v,i)=>v+4*n[i]).join(',')} ${back.map((v,i)=>v-4*n[i]).join(',')}" fill="${color}"/>`};
  }
  function couple(center,value,radius=35) {
    if(Math.abs(value)<1e-10)return '';
    const sign=Math.sign(value),points=Array.from({length:41},(_,i)=>{const a=-.4+sign*i/40*4.4;return [center[0]+radius*Math.cos(a),center[1]-radius*Math.sin(a)];});
    const last=points.at(-1),prior=points.at(-2),dx=last[0]-prior[0],dy=last[1]-prior[1],length=Math.hypot(dx,dy),u=[dx/length,dy/length],n=[-u[1],u[0]];
    return `<polyline points="${points.map(p=>p.join(',')).join(' ')}" fill="none" stroke="var(--red)" stroke-width="2"/><polygon points="${last.join(',')} ${last.map((v,i)=>v-8*u[i]+4*n[i]).join(',')} ${last.map((v,i)=>v-8*u[i]-4*n[i]).join(',')}" fill="var(--red)"/>`;
  }
  function axes() {
    return '<g aria-label="Global axes: positive x left, positive z up; positive y out of screen">'+arrow([78,404],[1,0,0],'var(--red)',37).html+arrow([78,404],[0,0,1],'var(--blue)',37).html+text([23,408],'+x','var(--red)',14)+text([88,372],'+z','var(--blue)',14)+text([100,407],'⊙ +y · positive torque ↺','var(--muted)',14)+'</g>';
  }
  function bodySvg(b) {
    const {map,scale}=mapper([...b.ends,...b.forces.map(f=>f.point),b.horn,b.contact],b.radii.map(r=>[b.origin,r]));
    let out='<rect width="600" height="440" fill="var(--paper)"/>';
    if(b.ends.length===2)out+=line(map(b.ends[0]),map(b.ends[1]),colors[b.id],10,'stroke-linecap="round" opacity=".55"');
    for(const r of b.radii)out+=circle(map(b.origin),r*scale,colors[b.id],'none',1.5);
    if(b.radii.length)out+=line(map(b.origin),map(b.axis),'var(--red)',1.4);
    if(b.horn)out+=line(map(b.origin),map(b.horn),'var(--amber)',5,'stroke-linecap="round"')+circle(map(b.horn),3,'var(--amber)','var(--paper)',1.5)+text([map(b.horn)[0]+8,map(b.horn)[1]-8],'D','var(--amber)',15);
    // Only label numbered force keys; force names/components remain in the table.
    // Greedy badge placement keeps coincident pin and opposing belt loads legible.
    const occupied=[];
    for(const f of b.forces){
      if(f.magnitude<1e-10)continue;
      const a=arrow(map(f.point),f.vector,f.color,40+27*(1-Math.exp(-f.magnitude/140)));out+=a.html;
      let badge=[Math.max(18,Math.min(582,a.end[0]+11)),Math.max(35,Math.min(345,a.end[1]-9))];
      for(let attempt=0;attempt<14&&occupied.some(v=>Math.hypot(v[0]-badge[0],v[1]-badge[1])<22);attempt++)badge=[Math.max(18,Math.min(582,a.end[0]+(attempt%2?-1:1)*(15+attempt*3))),Math.max(27,Math.min(345,a.end[1]-15-Math.floor(attempt/2)*20))];
      occupied.push(badge);out+=line(a.end,badge,f.color,.7,'opacity=".6"')+circle(badge,9,f.color,'var(--paper)',1)+text([badge[0],badge[1]+3.5],f.index,f.color,14,'text-anchor="middle" font-weight="700"');
    }
    for(const c of b.couples)out+=couple(map(c.point),c.value)+text([Math.max(20,map(c.point)[0]-58),Math.max(20,map(c.point)[1]-44)],`${c.name}: ${fmt(c.value)} N·m`,'var(--red)',14);
    for(let i=0;i<b.ends.length;i++){const at=map(b.ends[i]),label=b.id===2?['A','B'][i]:b.id===3?['B','C'][i]:b.id===4?'A':b.id===5?'B':'C';out+=circle(at,3,'var(--ink)','var(--paper)',1.5)+text([at[0]+8,at[1]+18],label,'var(--ink)',15);}
    if(b.contact)out+=circle(map(b.contact),3,'var(--red)','var(--paper)')+text([map(b.contact)[0]+8,map(b.contact)[1]+16],'P','var(--red)',15);
    out+=text([18,22],'WORLD x / z · uniformly scaled body','var(--muted)',14)+axes();
    return `<svg class="eqd-svg" viewBox="0 0 600 440" role="img" aria-label="Body ${b.id}: ${esc(b.name)} free-body diagram, global x left and z up">${out}</svg>`;
  }
  function renderBodies(params,detailedRaw) {
    const data=bodyData(params,detailedRaw);if(!data.valid)return `<div class="notice error">${esc(data.reason)}</div>`;
    return '<p class="eqd-caption">Application points and body outlines share a uniform geometric scale in each figure. Force-arrow lengths and torque arcs are schematic; numbered keys refer to the exact values below. Zero forces remain in the table. Positive torque is +y, counterclockwise.</p><div class="eqd-body-grid">'+data.bodies.map(b=>`<article class="eqd-card" data-eqd-body="${b.id}"><h4>Body ${b.id} · ${b.name}</h4>${bodySvg(b)}<div class="eqd-table-wrap"><table><caption>Global force components · N</caption><thead><tr><th>Key / force</th><th>Fx</th><th>Fz</th><th>|F|</th></tr></thead><tbody>${b.forces.map(f=>`<tr><td><span style="color:${f.color}">${f.index}</span> · ${esc(f.name)}</td><td>${fmt(f.vector[0])}</td><td>${fmt(f.vector[2])}</td><td>${fmt(f.magnitude)}</td></tr>`).join('')}</tbody></table></div>${b.couples.map(c=>`<p class="eqd-couple">${esc(c.name)} = ${fmt(c.value,6)} N·m · ${Math.abs(c.value)<1e-10?'zero':c.value>0?'↺ +y':'↻ −y'}</p>`).join('')}<p class="eqd-residual">Recomputed from displayed world forces: |ΣF| ${Math.hypot(...b.residualF).toExponential(2)} N · ΣMᵧ ${b.residualM.toExponential(2)} N·m about ${b.id===2||b.id===4?'A':b.id===6?'C':'B'}.</p></article>`).join('')+'</div>';
  }
  function springSvg(d) {
    const {map,scale}=mapper([d.A,d.D,d.S,d.Q,d.out,d.Su,d.remote,...d.arc],[[d.S,d.radius]],720,460);
    const path=vs=>vs.map((v,i)=>(i?'L':'M')+map(v).join(',')).join(' ');
    let out='<rect width="720" height="460" fill="var(--paper)"/>';
    out+=line(map(d.A),map(d.D),'var(--amber)',5,'stroke-linecap="round"')+line(map(d.D),map(d.Q),'var(--sage)',2.5)+circle(map(d.S),d.radius*scale,'var(--amber)','none',1.5);
    if(d.arc.length)out+=`<path d="${path(d.arc)}" stroke="var(--sage)" stroke-width="3" fill="none"/>`;
    out+=line(map(d.out),map(d.remote),'var(--sage)',2.5);
    out+=line(map(d.A),map(d.Su),'var(--muted)',1,'stroke-dasharray="4 4"')+line(map(d.Su),map(d.S),'var(--muted)',1,'stroke-dasharray="4 4"');
    const mid=(a,b)=>map(a).map((v,i)=>(v+map(b)[i])/2);
    out+=text(mid(d.A,d.Su).map((v,i)=>v+(i?19:0)),`Su ${fmt(d.localOffset[0])} mm`,'var(--muted)',14,'text-anchor="middle"')+text(mid(d.Su,d.S).map((v,i)=>v+(i?0:12)),`Sv ${fmt(d.localOffset[1])} mm`,'var(--muted)',14)+text(mid(d.A,d.D).map((v,i)=>v+(i?-12:0)),`rₕ ${fmt(d.hornRadius)} mm`,'var(--amber)',11,'text-anchor="middle"');
    for(const [point,label,dx,dy] of [[d.A,'A',8,18],[d.D,'D',8,18],[d.S,'S',8,18],[d.Q,'Q in',-10,-12],[d.out,'Q out',8,-13]])out+=circle(map(point),3,'var(--ink)','var(--paper)',1)+text([map(point)[0]+dx,map(point)[1]+dy],label,'var(--ink)',11);
    const remote=map(d.remote);out+=circle(remote,4,'var(--sage)','var(--paper)',1.5)+text([remote[0],remote[1]-18],'Remote spring / fixed exit','var(--sage)',11,'text-anchor="middle"');
    const f=arrow(map(d.D),d.force,'var(--red)',58);out+=f.html;if(d.forceMagnitude>1e-10)out+=text([f.end[0]+8,f.end[1]-7],`Fs ${fmt(d.forceMagnitude)} N`,'var(--red)',14);
    out+=text([18,22],'EXACT HORN / IDLER / TANGENT / WRAP GEOMETRY','var(--muted)',14)+axes();
    return `<svg class="eqd-svg eqd-spring-svg" viewBox="0 0 720 460" role="img" aria-label="Finite-idler spring route in global x-left, z-up coordinates">${out}</svg>`;
  }
  function renderSpring(params,evaluated) {
    const d=springData(params,evaluated);if(!d.valid)return `<div class="notice${d.disabled?'':' error'}">${esc(d.reason)}</div>`;
    const values=[['Cable condition',d.slack?'Zero tension / slack':'Taut'],['Cable tension Fs',`${fmt(d.forceMagnitude)} N`],['Spring torque τS',`${fmt(d.tauS,6)} N·m`],['Incoming tangent D–Q',`${fmt(d.tangentLength)} mm`],['Clockwise idler wrap',`${fmt(d.wrapDegrees)}°`],['Payout · tangent + wrap arc',`${fmt(d.payout)} mm`],['90° reference payout',`${fmt(d.referencePayout)} mm`],['Payout change Δℓ',`${fmt(d.delta)} mm`],['Fixed exit redirection',`${fmt(d.exitDegrees)}°`],['Idler radius rs',`${fmt(d.radius)} mm`],['World idler x / z',`${fmt(d.S[0])} / ${fmt(d.S[2])} mm`],['Stored spring energy',`${fmt(d.energy,6)} J`]];
    return `<div class="eqd-spring-layout"><div>${springSvg(d)}<p class="eqd-caption">Su / Sv are mounting-frame dimensions, rotated by α into the world axes. Idler circle, tangent, clockwise wrap and horn share one scale. The remote spring endpoint is schematic; no housing dimensions are implied. The force arrow is schematic.</p></div><dl class="eqd-readouts">${values.map(([a,b])=>`<div><dt>${esc(a)}</dt><dd>${esc(b)}</dd></div>`).join('')}</dl></div>`;
  }
  return {world,momentY,bodyData,springData,renderBodies,renderSpring};
})();
