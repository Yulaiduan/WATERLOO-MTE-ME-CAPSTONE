/** Offline linked coupling plots. Open index.html or run server.py.
 * Inputs: ratio controls (positive, dimensionless), pointer orbit/zoom events.
 * Outputs: canvas surface and SVG torque/cross-section plots. No network/storage.
 * Surface uses an orthographic painter projection; this is an analytical explorer.
 */
'use strict';
const $=id=>document.getElementById(id);
const model=CouplingModel;
const initial=()=>({dc:{min:1,max:3,current:2},fe:{min:1,max:3,current:2}});
let state=initial();
const view={yaw:-0.65,pitch:0.55,zoom:1};
let projected=[],drag=null,queued=false;
const format=(value,digits=4)=>Math.abs(value)<1e-10?'0':Number(value.toPrecision(digits)).toString();
const linspace=(a,b,n)=>Array.from({length:n+1},(_,i)=>a+(b-a)*i/n);
function syncControls(editingId=null){
  for(const key of ['dc','fe']){
    const value=state[key];
    for(const field of ['min','max','current']){
      const id=`${key}-${field}`;
      if(id!==editingId)$(id).value=value[field];
    }
    const slider=$(`${key}-slider`);
    slider.min=value.min;slider.max=value.max;slider.step=(value.max-value.min)/2000;slider.value=value.current;
  }
}
function changeControl(key,field,editing=false){
  const input=$(`${key}-${field}`),value=Number(input.value);
  const candidate={...state[key],[field]:value};
  if(input.value.trim()===''||!Number.isFinite(value)||value<=0||candidate.min>=candidate.max){
    $(`${key}-error`).textContent='Use positive numbers with minimum < maximum.';
    input.setAttribute('aria-invalid','true');return;
  }
  input.removeAttribute('aria-invalid');$(`${key}-error`).textContent='';
  if(field==='current'){
    candidate.min=Math.min(candidate.min,value);candidate.max=Math.max(candidate.max,value);
  }
  candidate.current=Math.max(candidate.min,Math.min(candidate.max,candidate.current));
  state[key]=candidate;syncControls(editing?`${key}-${field}`:null);render();
}
for(const key of ['dc','fe']){
  for(const field of ['min','max','current']){
    $(`${key}-${field}`).addEventListener('input',()=>changeControl(key,field,true));
    $(`${key}-${field}`).addEventListener('change',()=>changeControl(key,field));
  }
  $(`${key}-slider`).addEventListener('input',event=>{
    state[key].current=Number(event.target.value);$(`${key}-current`).value=state[key].current;render();
  });
}
function resetView(){view.yaw=-0.65;view.pitch=0.55;view.zoom=1;drawSurface();}
$('home').addEventListener('click',resetView);
$('reset').addEventListener('click',()=>{
  state=initial();document.querySelectorAll('.error').forEach(e=>e.textContent='');
  document.querySelectorAll('[aria-invalid]').forEach(e=>e.removeAttribute('aria-invalid'));
  syncControls();resetView();render();
});
function axisFrame(width,height,xmin,xmax,ymin,ymax,xlabel,ylabel){
  const pad={l:76,r:30,t:25,b:58};
  const x=value=>pad.l+(value-xmin)/(xmax-xmin)*(width-pad.l-pad.r);
  const y=value=>height-pad.b-(value-ymin)/(ymax-ymin)*(height-pad.t-pad.b);
  let markup='';
  for(const tick of linspace(xmin,xmax,4))markup+=`<line class="grid" x1="${x(tick)}" x2="${x(tick)}" y1="${pad.t}" y2="${height-pad.b}"/><text x="${x(tick)}" y="${height-pad.b+23}" text-anchor="middle">${format(tick,3)}</text>`;
  for(const tick of linspace(ymin,ymax,4))markup+=`<line class="grid" x1="${pad.l}" x2="${width-pad.r}" y1="${y(tick)}" y2="${y(tick)}"/><text x="${pad.l-12}" y="${y(tick)+4}" text-anchor="end">${format(tick,3)}</text>`;
  markup+=`<rect class="border" x="${pad.l}" y="${pad.t}" width="${width-pad.l-pad.r}" height="${height-pad.t-pad.b}"/>`;
  markup+=`<text class="axis-title" x="${(pad.l+width-pad.r)/2}" y="${height-10}" text-anchor="middle">${xlabel}</text><text class="axis-title" transform="translate(20 ${(pad.t+height-pad.b)/2}) rotate(-90)" text-anchor="middle">${ylabel}</text>`;
  return {x,y,markup,pad};
}
function renderEnvelope(){
  const dc=state.dc.current,fe=state.fe.current,{c2,k}=model.coefficients(dc,fe);
  const xmax=23.6/c2*1.3,ymax=(130+Math.abs(k)*23.6)*1.18;
  const tauW='τ<tspan baseline-shift="sub" font-size="10">W</tspan>';
  const tauH='τ<tspan baseline-shift="sub" font-size="10">H</tspan>';
  const {x,y,markup,pad}=axisFrame(620,430,-xmax,xmax,-ymax,ymax,`${tauW} = τ₄ / c₂ (Nm)`,`${tauH} (Nm)`);
  const vertices=model.envelope(dc,fe);
  let content=markup+`<polygon points="${vertices.map(p=>`${x(p.x)},${y(p.y)}`).join(' ')}" fill="#e0eff2" stroke="#197e89" stroke-width="2.5"/>`;
  content+=`<line class="zero" x1="${x(0)}" x2="${x(0)}" y1="${pad.t}" y2="372"/><line class="zero" x1="76" x2="590" y1="${y(0)}" y2="${y(0)}"/>`;
  content+=`<line x1="${x(-23.6/c2)}" y1="${y(-k*23.6)}" x2="${x(23.6/c2)}" y2="${y(k*23.6)}" stroke="#197e89" stroke-width="2" stroke-dasharray="3 5"/>`;
  for(const p of vertices)content+=`<circle cx="${x(p.x)}" cy="${y(p.y)}" r="4" fill="#197e89"><title>τW ${format(p.x,6)} Nm; τH ${format(p.y,6)} Nm</title></circle>`;
  const sign=k<0?'−':'+';
  content+=`<g id="envelope-equations"><rect x="198" y="164" width="270" height="70" rx="8" fill="white" fill-opacity=".94" stroke="#bdd4d9"/><text x="333" y="191" text-anchor="middle" class="equation">${tauW} = ${format(1/c2,5)} τ₄</text><text x="333" y="217" text-anchor="middle" class="equation">${tauH} = τ₂ ${sign} ${format(Math.abs(k),5)} τ₄</text></g>`;
  $('envelope').innerHTML=content;
}
function renderSection(key){
  const other=key==='dc'?'fe':'dc',range=state[key];
  const value=q=>model.coefficients(key==='dc'?q:state.dc.current,key==='fe'?q:state.fe.current).k;
  const ends=[value(range.min),value(range.max),0];
  const spread=Math.max(...ends)-Math.min(...ends),padding=Math.max(spread*.15,.25);
  const ymin=Math.min(...ends)-padding,ymax=Math.max(...ends)+padding;
  const {x,y,markup}=axisFrame(620,350,range.min,range.max,ymin,ymax,key==='dc'?'qdc':'qfe','k = −c₁ / c₂');
  const color=key==='dc'?'#117e88':'#d77d36';
  let content=markup+`<line class="zero" x1="76" x2="590" y1="${y(0)}" y2="${y(0)}"/><path d="M${x(range.min)} ${y(value(range.min))} L${x(range.max)} ${y(value(range.max))}" fill="none" stroke="${color}" stroke-width="3"/>`;
  const q=range.current,k=value(q);
  content+=`<line class="zero" x1="${x(q)}" x2="${x(q)}" y1="25" y2="292"/><circle class="point" cx="${x(q)}" cy="${y(k)}" r="6"><title>q${key} ${format(q,6)}; k ${format(k,6)}</title></circle>`;
  $(`section-${key}`).innerHTML=content;
  $(`fixed-${other}`).textContent=`q${other} = ${format(state[other].current)}`;
}
function render(){
  const {c1,c2,k}=model.coefficients(state.dc.current,state.fe.current);
  $('gain').textContent=format(k,6);
  $('coefficient-c1').textContent=format(c1,6);
  $('coefficient-c2').textContent=format(c2,6);
  $('sign-note').textContent=k>1e-9?'Positive coupling':k< -1e-9?'Negative coupling · reaction reverses':'Zero coupling';
  renderEnvelope();renderSection('dc');renderSection('fe');
  if(!queued){queued=true;requestAnimationFrame(()=>{queued=false;drawSurface();});}
}
const canvas=$('surface'),context=canvas.getContext('2d');
function color(value,limit){
  const t=Math.min(1,Math.abs(value)/limit),from=[247,249,250],to=value<0?[69,117,180]:[215,125,54];
  return `rgb(${from.map((v,i)=>Math.round(v+(to[i]-v)*t)).join(',')})`;
}
function drawSurface(){
  const width=canvas.clientWidth,height=canvas.clientHeight,dpr=window.devicePixelRatio||1;
  if(!width||!height)return;
  canvas.width=width*dpr;canvas.height=height*dpr;context.setTransform(dpr,0,0,dpr,0,0);context.clearRect(0,0,width,height);
  const corners=[state.dc.min,state.dc.max].flatMap(dc=>[state.fe.min,state.fe.max].map(fe=>model.coefficients(dc,fe).k));
  const zmin=Math.min(0,...corners),zmax=Math.max(0,...corners),span=Math.max(zmax-zmin,.01),limit=Math.max(Math.abs(zmin),Math.abs(zmax),.01);
  $('color-low').textContent=format(-limit,3);$('color-high').textContent=format(limit,3);
  const scale=Math.min(width*.24,height*.29)*view.zoom;
  function project(dc,fe,k){
    const xx=2*(dc-state.dc.min)/(state.dc.max-state.dc.min)-1;
    const yy=2*(fe-state.fe.min)/(state.fe.max-state.fe.min)-1;
    const zz=1.65*(k-zmin)/span-.8;
    const horizontal=Math.cos(view.yaw)*xx-Math.sin(view.yaw)*yy;
    const depth=Math.sin(view.yaw)*xx+Math.cos(view.yaw)*yy;
    const vertical=-Math.sin(view.pitch)*depth+Math.cos(view.pitch)*zz;
    return {x:width*.49+scale*horizontal,y:height*.51-scale*vertical,depth:Math.cos(view.pitch)*depth+Math.sin(view.pitch)*zz,dc,fe,k};
  }
  function line(points,stroke,lw=1,dash=[]){
    context.beginPath();points.forEach((p,i)=>i?context.lineTo(p.x,p.y):context.moveTo(p.x,p.y));context.strokeStyle=stroke;context.lineWidth=lw;context.setLineDash(dash);context.stroke();context.setLineDash([]);
  }
  const xs=linspace(state.dc.min,state.dc.max,32),ys=linspace(state.fe.min,state.fe.max,32);
  for(const dc of linspace(state.dc.min,state.dc.max,4))line([project(dc,state.fe.min,zmin),project(dc,state.fe.max,zmin)],'#e0e8ec');
  for(const fe of linspace(state.fe.min,state.fe.max,4))line([project(state.dc.min,fe,zmin),project(state.dc.max,fe,zmin)],'#e0e8ec');
  const grid=xs.map(dc=>ys.map(fe=>project(dc,fe,model.coefficients(dc,fe).k)));
  const cells=[];
  for(let i=0;i<32;i++)for(let j=0;j<32;j++){
    const points=[grid[i][j],grid[i+1][j],grid[i+1][j+1],grid[i][j+1]];
    cells.push({points,depth:points.reduce((sum,p)=>sum+p.depth,0)/4,k:points.reduce((sum,p)=>sum+p.k,0)/4});
  }
  cells.sort((a,b)=>a.depth-b.depth);
  for(const cell of cells){
    context.beginPath();cell.points.forEach((p,i)=>i?context.lineTo(p.x,p.y):context.moveTo(p.x,p.y));context.closePath();
    context.fillStyle=color(cell.k,limit);context.fill();context.strokeStyle='rgba(255,255,255,.23)';context.lineWidth=.35;context.stroke();
  }
  line(xs.map(dc=>project(dc,state.fe.current,model.coefficients(dc,state.fe.current).k)),'#117e88',3);
  line(ys.map(fe=>project(state.dc.current,fe,model.coefficients(state.dc.current,fe).k)),'#d77d36',3);
  const current=project(state.dc.current,state.fe.current,model.coefficients(state.dc.current,state.fe.current).k);
  line([project(state.dc.current,state.fe.current,zmin),current],'#334f61',1,[3,4]);
  context.beginPath();context.arc(current.x,current.y,6,0,2*Math.PI);context.fillStyle='#243f4d';context.fill();context.strokeStyle='white';context.lineWidth=2;context.stroke();
  const origin=project(state.dc.min,state.fe.min,zmin);
  const axes=[{points:[origin,project(state.dc.max,state.fe.min,zmin)],label:'qdc'}, {points:[origin,project(state.dc.min,state.fe.max,zmin)],label:'qfe'}, {points:[origin,project(state.dc.min,state.fe.min,zmax)],label:'−c₁ / c₂'}];
  context.font='12px Segoe UI, Arial';context.fillStyle='#4e6975';
  for(const axis of axes){line(axis.points,'#8da4ae',1.3);const p=axis.points[1];context.fillText(axis.label,p.x+7,p.y-8);}
  for(const q of [state.dc.min,state.dc.max]){const p=project(q,state.fe.min,zmin);context.fillText(format(q,3),p.x-10,p.y+18);}
  for(const q of [state.fe.min,state.fe.max]){const p=project(state.dc.min,q,zmin);context.fillText(format(q,3),p.x-28,p.y+15);}
  for(const k of linspace(zmin,zmax,3)){const p=project(state.dc.min,state.fe.min,k);context.fillText(format(k,3),p.x-33,p.y+4);}
  projected=grid.flat();projected.push(current);
}
canvas.addEventListener('pointerdown',event=>{drag={x:event.clientX,y:event.clientY};canvas.setPointerCapture(event.pointerId);$('surface-tooltip').hidden=true;});
canvas.addEventListener('pointermove',event=>{
  if(drag){view.yaw+=(event.clientX-drag.x)*.008;view.pitch=Math.max(.08,Math.min(1.4,view.pitch+(event.clientY-drag.y)*.008));drag={x:event.clientX,y:event.clientY};drawSurface();return;}
  const rect=canvas.getBoundingClientRect(),x=event.clientX-rect.left,y=event.clientY-rect.top;
  let nearest=null,distance=18;
  for(const p of projected){const delta=Math.hypot(p.x-x,p.y-y);if(delta<distance){nearest=p;distance=delta;}}
  const tooltip=$('surface-tooltip');tooltip.hidden=!nearest;
  if(nearest){tooltip.innerHTML=`q<sub>dc</sub> ${format(nearest.dc)} · q<sub>fe</sub> ${format(nearest.fe)}<br>−c<sub>1</sub>/c<sub>2</sub> = <b>${format(nearest.k,6)}</b>`;tooltip.style.left=`${Math.max(4,Math.min(x+14,rect.width-210))}px`;tooltip.style.top=`${Math.max(4,y-60)}px`;}
});
for(const name of ['pointerup','pointercancel'])canvas.addEventListener(name,()=>{drag=null;});
canvas.addEventListener('pointerleave',()=>{$('surface-tooltip').hidden=true;});
canvas.addEventListener('wheel',event=>{event.preventDefault();view.zoom=Math.max(.55,Math.min(1.8,view.zoom*Math.exp(-event.deltaY*.001)));drawSurface();},{passive:false});
new ResizeObserver(drawSurface).observe(canvas);
syncControls();render();
