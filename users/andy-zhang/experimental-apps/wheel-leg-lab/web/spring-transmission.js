/** Cross-section diagrams for the existing ideal spring transmissions.
 * Inputs: recorded/setup SI input and coil lengths, reference and config.
 * Outputs: SVG cylinder seats, end cap, rod/cable and winding marks.
 * Display housing/routing dimensions are schematic, not additional solver bodies,
 * contact, solid-height limits, cable inventory or verified physical packaging.
 */
export function transmissionState(c,frame,row={},initial={}){
 const input=frame.spring_geometry?.input_length??row.spring_length;
 const coil=frame.spring_coil_length??row.spring_coil_length??c.rest_length;
 const reference=initial.spring_geometry?.input_length??input;
 return {transmission:c.spring_transmission||'direct',input,coil,free:c.rest_length,
  travel:input-reference,strain:coil-c.rest_length,slack:Boolean(frame.spring_slack??row.spring_slack),
  compensated:c.spring_force_law==='zero_effective',mode:c.spring_mode};
}
export function drawCylinder(group,state,{width=330,height=170,labels=true}={}){
 const {coil,free,transmission}=state,pull=transmission!=='direct',rope=transmission==='ideal_rope';
 // One fixed scale per profile: piston cap AND the rigid rod-end eye move.
 const px=(width-140)/Math.max(free*2.4,0.15),y=height*.48,seat=pull?width*.55:36;
 const length=Math.max(2,coil*px),cap=seat+(pull?-length:length),rodLength=free*1.5*px;
 const eye=pull?cap+rodLength:cap,port=rope?width-100-state.travel*px:eye,portY=rope?y+20:y;
 const fmt=v=>Number.isFinite(v)?(v*1000).toFixed(1):'—';
 group.attr('class',(group.attr('class')||'')+' spring-transmission '+(pull?'spring-cylinder ':'spring-inline ')+transmission)
  .attr('data-transmission',transmission).attr('data-coil-length-m',coil).attr('data-input-travel-m',state.travel)
  .attr('data-cap-x',cap).attr('data-scale-px-m',px).attr('data-seat-x',seat).attr('data-rod-eye-x',eye);
 const line=(x1,y1,x2,y2,kind,color='var(--muted)',w=2)=>group.append('line').attr('class',kind)
  .attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2).attr('stroke',color).attr('stroke-width',w);
 const text=(x,yy,t,kind='')=>group.append('text').attr('class',kind).attr('x',x).attr('y',yy).text(t);
 const circle=(x,yy,kind)=>group.append('circle').attr('class',kind).attr('cx',x).attr('cy',yy).attr('r',4).attr('fill','var(--panel)').attr('stroke','var(--text)').attr('stroke-width',1.5);
 if(pull){
  group.append('rect').attr('class','cylinder-housing').attr('x',seat-free*1.8*px).attr('y',y-22)
   .attr('width',free*1.8*px).attr('height',44).attr('rx',4).attr('fill','var(--panel)').attr('fill-opacity',.8).attr('stroke','var(--blue)').attr('stroke-width',1.8);
  line(seat,y-27,seat,y+27,'fixed-seat','var(--text)',4);
 }
 const freeCap=seat+(pull?-free*px:free*px);
 line(freeCap,y-19,freeCap,y+19,'free-length-cap','var(--muted)',1).attr('stroke-dasharray','3 3');
 const coilPoints=Array.from({length:27},(_,i)=>{const t=i/26,offset=i<2||i>24?0:(i%2?12:-12);return [seat+(cap-seat)*t,y+offset];});
 group.append('path').attr('class','spring-coil '+(pull?'cylinder-coil':'inline-coil')).attr('d',coilPoints.map((p,i)=>(i?'L':'M')+p.join(',')).join(''))
  .attr('stroke','var(--orange)').attr('stroke-width',2).attr('fill','none');
 if(pull){
  line(cap,y-19,cap,y+19,'moving-end-cap','var(--accent)',4);
  line(cap,y,eye,y,'piston-rod','var(--purple)',3).attr('data-rigid-length-px',rodLength);
  circle(eye,y,'piston-rod-eye');
 }else{circle(seat,y,'inline-fixed-eye');circle(cap,y,'inline-moving-eye');}
 if(rope){
  // The rope is attached OUTSIDE the housing to the rigid piston rod eye.
  // It turns on a separate frictionless idler, never through the coil/cap.
  const idler=width-28,r=10;
  group.append('circle').attr('class','routing-idler').attr('cx',idler).attr('cy',y+10).attr('r',r)
   .attr('fill','var(--panel)').attr('stroke','var(--purple)').attr('stroke-width',2);
  circle(idler,y+10,'idler-pivot');
  group.append('path').attr('class','pull-cable').attr('data-attachment-x',eye).attr('data-attachment-y',y)
   .attr('d',`M${eye},${y}H${idler}A10,10 0 0 1 ${idler},${y+20}H${port}`)
   .attr('fill','none').attr('stroke','var(--purple)').attr('stroke-width',2).attr('stroke-dasharray',state.slack?'4 4':null);
  for(let i=0;i<5;i++){const xx=eye+((i/5+state.travel*px/Math.max(idler-eye,1))%1+1)%1*(idler-eye);
   group.append('circle').attr('class','spring-cable-mark').attr('cx',xx).attr('cy',y).attr('r',2).attr('fill','var(--accent)');}
  circle(port,portY,'cable-input-eye');
 }
 if(labels){
  text(10,16,rope?'3 · Rope → piston rod end → coil':pull?'2 · Reversing cylinder / piston':'1 · Inline spring · normal travel','transmission-title');
  text(10,height-43,`Coil ${fmt(coil)} mm · free ${fmt(free)} mm`,'coil-length-label');
  text(10,height-27,`Input travel ${fmt(state.travel)} mm · ${state.strain<0?'compression':state.strain>0?'extension':'free'} ${fmt(Math.abs(state.strain))} mm`);
  text(10,height-11,state.slack?'Coil disengaged / rope slack':state.compensated?'Ideal preload/offset emulation':pull?'Pull rod outward → coil compresses':'Span grows → coil extends; span shrinks → compresses');
  if(pull){text(seat-20,y-32,'Fixed seat');text(Math.max(5,cap-20),y+38,'Cap');text(Math.min(width-66,eye-8),y-14,'Rod end');}
 }
 return {cap,seat,px,port,portY,eye};
}
