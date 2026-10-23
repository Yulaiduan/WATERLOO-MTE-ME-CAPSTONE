/** Physical preview geometry and material markers; load after model.js.
 * Inputs: resolved V4 parameters in mm/deg and a pose in degrees.
 * Outputs: exact tangent-loop samples, belt material positions, body index axes
 * and captured-frame finite-idler spring routes in Kinefold x/y/z mm. The remote
 * housing/dial is a schematic payout witness; no drum inertia or spring dynamics.
 */
globalThis.KinefoldDrawing = (() => {
  const {VSL} = KinefoldV4;
  const world = (p, v) => Kinefold.point(VSL.global(p, v));
  function belts(p, theta) {
    const s=VSL.state(p,theta), e=VSL.state(p,p.te), dt=(theta-p.te)*VSL.rad;
    const stages=[
      {id:'ab',O:[0,0],C:s.B,r1:p.ra,r2:p.rb,travel:p.ra*dt},
      {id:'cd',O:[0,0],C:s.B,r1:p.rc,r2:p.rd,travel:p.rc*dt},
      // Material motion is relative to the tibia carrier, not the world.
      {id:'ef',O:s.B,C:s.P,r1:p.re,r2:p.rf,
        travel:-p.re*(s.t5-(s.t3-e.t3))*VSL.rad}
    ];
    return stages.map(stage => {
      const dx=stage.C[0]-stage.O[0],dy=stage.C[1]-stage.O[1],length=Math.hypot(dx,dy);
      const loop=VSL.belt(length,stage.r1,stage.r2);
      if(!loop) return {...stage,valid:false};
      const at=distance=>{const v=loop.at(distance);return world(p,[
        stage.O[0]+(dx*v[0]-dy*v[1])/length,
        stage.O[1]+(dy*v[0]+dx*v[1])/length]);};
      const count=Math.max(8,Math.min(24,Math.ceil(loop.total/80)));
      return {...stage,valid:true,loop,at,
        // An offset identifies the same material point across different poses.
        material:offset=>at(offset+stage.travel),
        outline:Array.from({length:161},(_,i)=>at(loop.total*i/160)),
        markers:Array.from({length:count},(_,i)=>at(loop.total*i/count+stage.travel))};
    });
  }
  function indices(p,theta) {
    const s=VSL.state(p,theta),A=[0,0];
    return [
      ['a',A,p.ra,0],['c',A,p.rc,0],['b',s.B,p.rb,s.t3],
      ['d',s.B,p.rd,s.t5],['e',s.B,p.re,s.t5],
      ['f',s.P,p.rf,s.t6],['wheel',s.P,p.rw,s.t6]
    ].map(([id,center,radius,angle])=>{
      const t=angle*VSL.rad;
      return {id,angle,center:world(p,center),radius,
        primary:world(p,[center[0]+radius*Math.cos(t),center[1]+radius*Math.sin(t)]),
        secondary:world(p,[center[0]-.72*radius*Math.sin(t),center[1]+.72*radius*Math.cos(t)])};
    });
  }
  function spring(params,frame) {
    if(!params.springEnabled)return {enabled:false,law:'Spring disabled'};
    const p=Kinefold.reference(params),z=KinefoldV4.VSLSpring.state(p,frame.theta2);
    if(!z.valid)return {enabled:true,valid:false,reason:z.reason};
    const A=frame.actualA||frame.A,at=v=>world(p,v).map((n,i)=>n+A[i]);
    const arc=params.rs>0?Array.from({length:65},(_,i)=>at([
      p.Su+p.rs*Math.cos(z.psi-z.wrap*i/64),p.Sv+p.rs*Math.sin(z.psi-z.wrap*i/64)])):[];
    return {enabled:true,valid:true,law:params.springLaw==='constant'?'Ideal constant cable force':'V4 linear coil',
      A,D:at(z.D),Q:at(z.Q),S:at(z.S),out:at(z.out),remote:at(z.remote(125)),arc,
      forceN:z.force,torqueNm:z.tauS,payoutMm:z.payout,deltaMm:z.delta,
      // The dial is a payout witness, not an assumed physical drum radius.
      witnessAngle:z.delta/20};
  }
  function springSvg(z,P,scale) {
    const number=n=>Number(n).toFixed(2);
    if(!z.enabled)return '<text x="22" y="52" fill="var(--muted)" font-size="11">Spring disabled · no spring force</text>';
    if(!z.valid)return '<text x="22" y="52" fill="var(--red)" font-size="11">Spring route unavailable</text>';
    const path=(points,width)=>`<path d="${points.map((v,i)=>(i?'L':'M')+P(v).join(',')).join(' ')}" fill="none" stroke="var(--amber)" stroke-width="${width}"/>`;
    const [sx,sy]=P(z.S),[rx,ry]=P(z.remote),r=12;
    return `<g data-spring-law="${z.law}" data-spring-payout-mm="${z.payoutMm}" data-spring-delta-mm="${z.deltaMm}" data-spring-force-n="${z.forceN}">`
      +path([z.A,z.D],3)+path([z.D,z.Q],2)+path(z.arc,2.5)+path([z.out,z.remote],2)
      +`<circle cx="${sx}" cy="${sy}" r="${Math.max(2,scale*Math.hypot(...z.S.map((n,i)=>n-z.Q[i])))}" fill="none" stroke="var(--amber)" stroke-width="1.2"/>`
      +`<rect x="${rx-r-5}" y="${ry-r-5}" width="${2*r+10}" height="${2*r+10}" rx="4" fill="var(--paper)" stroke="var(--amber)" stroke-width="1.5"/><circle cx="${rx}" cy="${ry}" r="${r}" fill="none" stroke="var(--amber)"/><path d="M${rx} ${ry}L${rx+r*Math.cos(z.witnessAngle)} ${ry+r*Math.sin(z.witnessAngle)}" stroke="var(--red)" stroke-width="2"/>`
      +`<text x="${rx+r+11}" y="${ry+4}" fill="var(--amber)" font-size="10">Spring · schematic</text>`
      +`<rect x="12" y="40" width="670" height="39" fill="var(--paper)" opacity=".94"/><text x="22" y="54" fill="var(--amber)" font-size="11">${z.law} · Fₛ ${number(z.forceN)} N · τₛ ${number(z.torqueNm)} N·m</text><text x="22" y="71" fill="var(--muted)" font-size="10">Cable payout ΔL₉₀ ${number(z.deltaMm)} mm · dial follows payout, housing schematic</text></g>`;
  }
  return {belts,indices,spring,springSvg};
})();
