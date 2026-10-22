/** Physical preview geometry and material markers; load after model.js.
 * Inputs: resolved V4 parameters in mm/deg and a pose in degrees.
 * Outputs: exact tangent-loop samples, belt material positions and body index axes
 * in Kinefold x/y/z mm. No invented wheel width, belt elasticity or dynamics.
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
  return {belts,indices};
})();
