/** Draw labelled selected mechanisms at a common metric scale.
 * Inputs: canvas, retained design config, normalized pose, working/inversion view.
 * Outputs: labelled drawing and returned world pose; GIF export uses this function.
 * Limits: ideal prescribed kinematics. Red overlap is a planar filter, not contact.
 * Loaded by app.js and scripts/export_design_examples.cjs.
 */
import {data} from './data.js';
import {pose,phaseAngle,angleRange,trace} from './model.js';
export const WIDTH=600,HEIGHT=720;
const caches=new Map();
function path(design,mode){const key=design.id+mode;if(!caches.has(key))caches.set(key,trace(design,mode));return caches.get(key);}
function bounds(mode){
 const key='bounds'+mode;if(caches.has(key))return caches.get(key);
 const xs=[],zs=[];
 for(const d of data.designs){
  xs.push(-d.config.ra,d.config.ra);zs.push(-d.config.ra,d.config.ra);
  for(let i=0;i<=100;i++){
   const p=pose(d.config,phaseAngle(d,mode,i/100));
   xs.push(p.B[0]-d.config.rb,p.B[0]+d.config.rb,p.C[0]-d.config.rw,p.C[0]+d.config.rw);
   zs.push(p.B[1]-d.config.rb,p.B[1]+d.config.rb,p.C[1]-d.config.rw,p.C[1]+d.config.rw);
  }
 }
 const b=[Math.min(...xs)-50,Math.max(...xs)+50,Math.min(...zs)-50,Math.max(...zs)+50];caches.set(key,b);return b;
}
export function drawExample(canvas,design,fraction,mode,options={}){
 const dark=options.dark===true,c=canvas.getContext('2d'),p=pose(design.config,phaseAngle(design,mode,fraction));
 c.setTransform(canvas.width/WIDTH,0,0,canvas.height/HEIGHT,0,0);
 const color={bg:dark?'#202824':'#fffdf6',ink:dark?'#e7eddf':'#263c39',muted:dark?'#acbdb1':'#657c72',grid:dark?'#33433b':'#e9eee3',upper:'#25849b',lower:'#d99a49',path:dark?'#64c3a2':'#208365',chord:'#a77cb6',red:dark?'#f3908c':'#b95356',belt:dark?'#84aa92':'#668a76'};
 c.clearRect(0,0,WIDTH,HEIGHT);c.fillStyle=color.bg;c.fillRect(0,0,WIDTH,HEIGHT);
 function text(s,x,y,size=13,col=color.ink,bold=false){c.fillStyle=col;c.font=`${bold?'600':'400'} ${size}px Arial`;c.textAlign='left';c.fillText(s,x,y);}
 text(`EXAMPLE ${design.number} · ${design.role.toUpperCase()}`,22,28,11,color.muted,true);
 text(design.label,22,57,19,color.ink,true);
 const cfg=design.config,met=mode==='inversion'?design.full:design.metrics;
 // Explicit values come from retained evidence, rather than rounded label strings.
 text(`L₂ / L₃ = ${cfg.L2} / ${cfg.L3} mm    rₐ / rᵦ = ${cfg.ra.toFixed(2)} / ${cfg.rb} mm`,22,81);
 text(`Guide ${cfg.qab.toFixed(4)}    α ${cfg.alpha}°    φ₀ ${cfg.phi0}°    Wheel R ${cfg.rw} mm`,22,102,12);
 text(mode==='inversion'?`Full ideal range · ${met.vertical_mm.toFixed(2)} mm vertical`:`Working stroke · ${met.vertical_mm.toFixed(2)} total / ${met.usable_mm.toFixed(2)} usable mm`,22,125,13,color.ink,true);
 text(`Chord ${met.chord_tilt_deg.toFixed(2)}° from vertical · max bow ${met.max_chord_error_mm.toFixed(2)} mm`,22,145,12,color.muted);
 const area={x:22,y:167,w:556,h:407},b=bounds(mode);
 const scale=Math.min(area.w/(b[1]-b[0]),area.h/(b[3]-b[2]));
 const ox=area.x+(area.w-scale*(b[1]-b[0]))/2-b[0]*scale;
 const oz=area.y+(area.h-scale*(b[3]-b[2]))/2+b[3]*scale;
 const xy=v=>[ox+v[0]*scale,oz-v[1]*scale];
 function line(a,b,col,width=1,dash=[]){c.beginPath();c.strokeStyle=col;c.lineWidth=width;c.setLineDash(dash);c.moveTo(...a);c.lineTo(...b);c.stroke();c.setLineDash([]);}
 function circle(v,r,col,width=1,fill=null,dash=[]){c.beginPath();c.strokeStyle=col;c.lineWidth=width;c.setLineDash(dash);c.arc(...xy(v),r*scale,0,2*Math.PI);if(fill){c.fillStyle=fill;c.fill();}c.stroke();c.setLineDash([]);}
 c.save();c.beginPath();c.rect(area.x,area.y,area.w,area.h);c.clip();
 for(let x=Math.ceil(b[0]/100)*100;x<=b[1];x+=100)line(xy([x,b[2]]),xy([x,b[3]]),color.grid);
 for(let z=Math.ceil(b[2]/100)*100;z<=b[3];z+=100)line(xy([b[0],z]),xy([b[1],z]),color.grid);
 line(xy([b[0],0]),xy([b[1],0]),color.muted,1,[4,5]);
 if(options.clearance!==false)circle([0,0],220,color.red,1,null,[4,4]);
 const points=path(design,mode);
 line(xy(points[0]),xy(points.at(-1)),color.chord,1.5,[6,4]);
 c.beginPath();c.moveTo(...xy(points[0]));for(const v of points)c.lineTo(...xy(v));c.strokeStyle=color.path;c.lineWidth=2.6;c.stroke();
 for(const v of [points[0],points.at(-1)])circle(v,6,color.path,1,color.path);
 const overlap=p.hipDistance<cfg.rw+20-1e-7;
 circle(p.C,cfg.rw,overlap?color.red:color.muted,2,overlap?(dark?'#3a282a':'#faf0eb'):null);
 // Wheel spin K=0: no rolling or hidden wheel rotation is imposed.
 line(xy([p.C[0]-cfg.rw,p.C[1]]),xy([p.C[0]+cfg.rw,p.C[1]]),color.grid);
 line(xy([p.C[0],p.C[1]-cfg.rw]),xy([p.C[0],p.C[1]+cfg.rw]),color.grid);
 line(xy(p.A),xy(p.B),color.upper,6);line(xy(p.B),xy(p.C),color.lower,6);
 if(options.guide!==false){
  circle(p.A,cfg.ra,color.belt,1.3);circle(p.B,cfg.rb,color.belt,1.3);
  const dir=Math.atan2(p.B[1],p.B[0]),delta=Math.acos((cfg.ra-cfg.rb)/cfg.L2);
  for(const n of [dir+delta,dir-delta]){
   const v=[Math.cos(n),Math.sin(n)];
   line(xy([v[0]*cfg.ra,v[1]*cfg.ra]),xy([p.B[0]+v[0]*cfg.rb,p.B[1]+v[1]*cfg.rb]),color.belt,1.2);
  }
 }
 const cp=xy(p.C),angle=-p.theta3*Math.PI/180;
 line(cp,xy([p.C[0]+100,p.C[1]]),color.chord,1,[3,3]);
 c.beginPath();c.strokeStyle=color.chord;c.lineWidth=1.3;c.arc(...cp,55*scale,0,angle,angle<0);c.stroke();
 text('θ₃',cp[0]+65*scale,cp[1]+16,11,color.chord);
 const closeHip=p.hipDistance*scale<25;
 for(const [v,label] of [[p.A,closeHip?(p.hipDistance<1e-6?'A=C · fold':'A / C · close'):'A · hip'],[p.B,'B · knee'],[p.C,closeHip?'':'C · wheel']]){
  circle(v,7,color.ink,1,color.bg);const at=xy(v),dy=closeHip?(v===p.B?20:-27):-9;if(label)text(label,Math.min(Math.max(at[0]+9,area.x+4),area.x+area.w-88),Math.min(Math.max(at[1]+dy,area.y+16),area.y+area.h-8),12,color.ink,true);
 }
 const ax=xy(p.A);line([ax[0]-13,ax[1]-7],[ax[0]+13,ax[1]-7],color.ink,2);
 c.restore();
 const bar=100*scale;line([24,570],[24+bar,570],color.muted,2);text('100 mm · shared scale',24,590,10,color.muted);
 const [start,end]=angleRange(design,mode),now=pose(cfg,start),travel=p.C[1]-now.C[1];
 text(`θ₂ ${p.theta2.toFixed(2)}°    θ₃ ${p.theta3.toFixed(2)}°`,22,613,14,color.ink,true);
 text(`Range ${start.toFixed(2)}–${end.toFixed(2)}°  ·  Δz ${travel.toFixed(1)} mm`,22,634,12,color.muted);
 text(`Current rim/hip margin: ${(p.hipDistance-cfg.rw).toFixed(1)} mm`,22,655,12,overlap?color.red:color.muted);
 text(overlap?'Projected clearance FAIL · axial packaging unresolved':'Projected clearance ≥20 mm at this pose',22,675,12,overlap?color.red:color.path,true);
 text('θ₃ from wheel-centre horizontal · prescribed kinematics',22,698,11,color.muted);
 return {...p,mode,fraction,projectedClearancePass:!overlap};
}
