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
 // Use one constant metres-to-pixels scale for a free and moving coil. Never
 // normalize each frame independently: that would hide actual compression.
 const px=(width-120)/Math.max(free*2,0.15),y=height*.48,seat=pull?width-85:36;
 const rawLength=coil*px,length=Math.max(2,rawLength),cap=seat+(pull?-length:length);
 const fmt=v=>Number.isFinite(v)?(v*1000).toFixed(1):'—';
 group.attr('class',(group.attr('class')||'')+' spring-cylinder '+transmission).attr('data-transmission',transmission)
  .attr('data-coil-length-m',coil).attr('data-input-travel-m',state.travel)
  .attr('data-cap-x',cap).attr('data-scale-px-m',px).attr('data-seat-x',seat);
 const line=(x1,y1,x2,y2,kind,color='var(--muted)',w=2)=>group.append('line').attr('class',kind)
  .attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2).attr('stroke',color).attr('stroke-width',w);
 const text=(x,yy,t,kind='')=>group.append('text').attr('class',kind).attr('x',x).attr('y',yy).text(t);
 const housingStart=pull?seat-free*1.8*px:seat,housingEnd=pull?seat:seat+free*1.8*px;
 group.append('rect').attr('class','cylinder-housing').attr('x',housingStart).attr('y',y-22)
  .attr('width',housingEnd-housingStart).attr('height',44).attr('rx',4)
  .attr('fill','var(--panel)').attr('fill-opacity',.8).attr('stroke','var(--blue)').attr('stroke-width',1.8);
 const freeCap=seat+(pull?-free*px:free*px);
 line(freeCap,y-19,freeCap,y+19,'free-length-cap','var(--muted)',1).attr('stroke-dasharray','3 3');
 line(seat,y-27,seat,y+27,'fixed-seat','var(--text)',4);
 const coilPoints=Array.from({length:27},(_,i)=>{const t=i/26,offset=i<2||i>24?0:(i%2?12:-12);return [seat+(cap-seat)*t,y+offset];});
 group.append('path').attr('class','spring-coil cylinder-coil').attr('d',coilPoints.map((p,i)=>(i?'L':'M')+p.join(',')).join(''))
  .attr('stroke','var(--orange)').attr('stroke-width',2).attr('fill','none');
 line(cap,y-19,cap,y+19,'moving-end-cap','var(--accent)',4);
 const port=rope?width-110:width-26,portY=rope?y+24:y;
 if(rope){
  const idler=width-53,r=12;
  group.append('circle').attr('class','routing-idler').attr('cx',idler).attr('cy',y+12).attr('r',r)
   .attr('fill','var(--panel)').attr('stroke','var(--purple)').attr('stroke-width',2);
  group.append('circle').attr('cx',idler).attr('cy',y+12).attr('r',2).attr('fill','var(--purple)');
  group.append('path').attr('class','pull-cable').attr('d',`M${cap},${y}H${idler}A12,12 0 0 1 ${idler},${y+24}H${port}`)
   .attr('fill','none').attr('stroke','var(--purple)').attr('stroke-width',2.5)
   .attr('stroke-dasharray',state.slack?'4 4':null);
  for(let i=0;i<6;i++){const xx=cap+((i/6+state.travel*px/Math.max(port-cap,1))%1+1)%1*(idler-cap);
   group.append('circle').attr('class','spring-cable-mark').attr('cx',xx).attr('cy',y).attr('r',2).attr('fill','var(--accent)');}
 }else line(cap,y,port,y,pull?'pull-through-rod':'direct-spring-rod',pull?'var(--purple)':'var(--muted)',3);
 line(port,portY-7,port,portY+7,'input-eye','var(--text)',2);
 if(labels){
  text(10,16,rope?'Routed rope · pull-to-compress':pull?'Rigid rod · pull-to-compress':'Direct spring · span drives coil','transmission-title');
  text(10,height-43,`Coil ${fmt(coil)} mm · free ${fmt(free)} mm`,'coil-length-label');
  text(10,height-27,`Input travel ${fmt(state.travel)} mm · ${state.strain<0?'compression':state.strain>0?'extension':'free'} ${fmt(Math.abs(state.strain))} mm`);
  text(10,height-11,state.slack?'Coil disengaged / slack':state.compensated?'Preload/offset emulation · not ordinary direct Hooke':'Green cap moves · dotted cap = free length');
  text(Math.max(5,seat-24),y-32,'Seat');text(Math.max(5,cap-20),y+39,'End cap');
 }
 return {cap,seat,px,port,portY};
}
