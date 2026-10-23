/** Actual world-mesh contact playback and backdriven ideal belt drawing.
 * Load after model/drawing. Inputs: contact-v1 frames in mm/deg and captured
 * builder geometry. Outputs: native SVG plus pure belt/index geometry. Chassis
 * and wheel transforms/terrain are actual engine outputs; B/transmission is the
 * explicit ideal massless linkage, with its solver residual shown separately.
 */
globalThis.KinefoldContactDrawing = (() => {
  'use strict';
  const R = Math.PI / 180;
  function transmission(params, frame) {
    const q = KinefoldV4.VSL.state(Kinefold.reference(params), frame.theta2);
    const extension = KinefoldV4.VSL.state(Kinefold.reference(params), params.te);
    const dt = (frame.theta2 - params.te) * R, drive = frame.theta4 * R;
    const stages = [
      {id:'ab',start:frame.A,end:frame.B,r1:params.ra,r2:params.rb,travel:params.ra*dt},
      {id:'cd',start:frame.A,end:frame.B,r1:params.rc,r2:params.rd,travel:params.rc*(dt-drive)},
      {id:'ef',start:frame.B,end:frame.C,r1:params.re,r2:params.rf,travel:-params.re*(frame.theta5-(q.t3-extension.t3))*R},
    ].map(stage => {
      const dx = -(stage.end[0]-stage.start[0]), dz = stage.end[2]-stage.start[2], length = Math.hypot(dx,dz);
      const loop = KinefoldV4.VSL.belt(length,stage.r1,stage.r2);
      if (!loop) return {...stage,valid:false};
      const at = distance => {
        const [u,v] = loop.at(distance);
        return [stage.start[0]-(dx*u-dz*v)/length,0,stage.start[2]+(dz*u+dx*v)/length];
      };
      const count = Math.max(8,Math.min(24,Math.ceil(loop.total/80)));
      return {...stage,valid:true,loop,material:offset=>at(offset+stage.travel),
        outline:Array.from({length:161},(_,i)=>at(loop.total*i/160)),
        markers:Array.from({length:count},(_,i)=>at(loop.total*i/count+stage.travel))};
    });
    const centres = {a:frame.A,c:frame.A,b:frame.B,d:frame.B,e:frame.B,f:frame.C,wheel:frame.C};
    const radii = {a:params.ra,b:params.rb,c:params.rc,d:params.rd,e:params.re,f:params.rf,wheel:params.rw};
    const angles = {...frame.indexAnglesDeg,wheel:frame.theta6};
    const indices = Object.keys(centres).map(id => {
      const centre=centres[id],radius=radii[id],angle=(angles[id]-params.alpha)*R;
      return {id,centre,radius,angle:angles[id],primary:[centre[0]-radius*Math.cos(angle),0,centre[2]+radius*Math.sin(angle)],
        secondary:[centre[0]+radius*.72*Math.sin(angle),0,centre[2]+radius*.72*Math.cos(angle)]};
    });
    return {stages,indices};
  }
  function bounds(result,p) {
    let minX=Infinity,maxX=-Infinity,minZ=0,maxZ=-Infinity;
    for (const f of result.frames) {
      const spring=KinefoldDrawing.spring(p,f);
      for (const point of [f.A,f.B,f.C,...(spring.valid?[spring.D,spring.S,spring.remote]:[])]) {
        minX=Math.min(minX,point[0]-p.rw);maxX=Math.max(maxX,point[0]+p.rw);
        minZ=Math.min(minZ,point[2]-p.rw);maxZ=Math.max(maxZ,point[2]+200);
      }
    }
    return {minX:minX-180,maxX:maxX+180,minZ:minZ-60,maxZ};
  }
  function render(state) {
    const result=state.result,p=state.snapshot.params,frame=result.frames[state.index],row=result.rows[state.index];
    state.contactBounds ||= bounds(result,p);
    const b=state.contactBounds,W=740,H=450,scale=Math.min((W-100)/(b.maxX-b.minX),(H-70)/(b.maxZ-b.minZ));
    const P=v=>[W/2-(v[0]-(b.minX+b.maxX)/2)*scale,H/2-(v[2]-(b.minZ+b.maxZ)/2)*scale];
    const line=(points,color,width=1,extra='')=>`<path d="${points.map((v,i)=>(i?'L':'M')+P(v).join(',')).join(' ')}" fill="none" stroke="${color}" stroke-width="${width}" ${extra}/>`;
    const circle=(point,radius,color,width=1)=>`<circle cx="${P(point)[0]}" cy="${P(point)[1]}" r="${radius*scale}" fill="none" stroke="${color}" stroke-width="${width}"/>`;
    let html='<rect width="740" height="450" fill="var(--paper)"/>';
    for(let x=Math.ceil(b.minX/100)*100;x<=b.maxX;x+=100)html+=line([[x,0,b.minZ],[x,0,b.maxZ]],'var(--line)');
    for(let z=Math.ceil(b.minZ/100)*100;z<=b.maxZ;z+=100)html+=line([[b.minX,0,z],[b.maxX,0,z]],'var(--line)');
    const polygons=frame.terrainPolygonsMm || result.terrain.polygonsMm.map(poly=>poly.map(v=>v.map((n,i)=>n+(frame.terrainOffsetMm?.[i]||0))));
    for(const polygon of polygons)html+=`<polygon points="${polygon.map(v=>P(v).join(',')).join(' ')}" fill="var(--sage-soft)" stroke="var(--sage)" stroke-width="2"/>`;
    const base=result.terrain.baseSegmentMm.map(v=>v.map((n,i)=>n+(frame.terrainOffsetMm?.[i]||0)));
    html+=line(base,'var(--sage)',2)+line([frame.A,frame.B],'var(--sage)',11)+line([frame.B,frame.C],'var(--blue)',9)+circle(frame.C,p.rw,'var(--ink)',2);
    const drawing=transmission(p,frame);
    for(const belt of drawing.stages)if(belt.valid){
      html+=line(belt.outline,'var(--muted)',1);
      for(const point of belt.markers)html+=`<circle cx="${P(point)[0]}" cy="${P(point)[1]}" r="1.7" fill="var(--sage)"/>`;
    }
    for(const index of drawing.indices)html+=circle(index.centre,index.radius,'var(--amber)',1.1)+line([index.centre,index.primary],'var(--red)',1.5)+line([index.centre,index.secondary],'var(--red)',.8,'stroke-dasharray="3 3"');
    html+=KinefoldDrawing.springSvg(KinefoldDrawing.spring(p,frame),P,scale);
    const [ax,az]=P(frame.A);
    html+=`<rect x="${ax-48}" y="${az-28}" width="96" height="26" rx="4" fill="var(--soft)" stroke="var(--sage)"/><text x="${ax}" y="${az-10}" text-anchor="middle" fill="var(--ink)" font-size="11">m₁ ${p.m1} kg</text>`;
    const offset=result.caseConfig?.undersideOffsetMm;
    if(Number.isFinite(offset)) {
      const point=[frame.A[0],0,frame.A[2]-offset],pixel=P(point);
      html+=line([frame.A,point],'var(--red)',1,'stroke-dasharray="3 3"')+circle(point,5/scale,'var(--red)',1.5)+`<text x="${pixel[0]+10}" y="${pixel[1]+5}" fill="var(--red)" font-size="11">Underside point · ${offset} mm below A</text>`;
    }
    for(const [key,point]of [['A',frame.A],['B',frame.B],['C',frame.C]])html+=`<text x="${P(point)[0]+(key==='A'?-18:9)}" y="${P(point)[1]+(key==='A'?14:-9)}" fill="var(--ink)" font-size="12">${key}</text>`;
    html+='<rect x="12" y="12" width="490" height="27" fill="var(--paper)" opacity=".94"/><text x="22" y="30" fill="var(--muted)" font-size="11">ACTUAL CONTACT · WORLD GRID 100 mm · IDEAL MASSLESS LINKS</text><rect x="12" y="385" width="206" height="52" fill="var(--paper)" opacity=".94"/><path d="M90 422H34m8-4-8 4 8 4M90 422V392m-4 8 4-8 4 8" fill="none" stroke="var(--ink)"/><text x="14" y="426" fill="var(--red)" font-size="11">+x</text><text x="101" y="396" fill="var(--blue)" font-size="11">+z</text><text x="106" y="425" fill="var(--sage)" font-size="10">⊙ +y</text>'+(result.caseConfig?.kind&&result.caseConfig.kind!=='terrain-stability'?'':'<path d="M540 424H620m-8-5 8 5-8 5" stroke="var(--sage)" fill="none"/>')+'<text x="526" y="406" fill="var(--sage)" font-size="11">'+(result.caseConfig?.kind&&result.caseConfig.kind!=='terrain-stability'?'Stationary flat floor':'Actual terrain moves −x →')+'</text>';
    return {html,row,frame};
  }
  return {transmission,bounds,render};
})();
