/** Labelled Motion Lab example playback and deterministic GIF frame API.
 * Inputs: retained mm/degree configs and local view/playback controls.
 * Outputs: common-scale canvas examples, GIF links and kinematic pose snapshots.
 * No physics API calls or saved solver-profile changes; playback is illustrative.
 * Open /design-examples/ on the local Motion Lab server.
 */
import {data} from './data.js';
import {drawExample,WIDTH,HEIGHT} from './renderer.js';
const $=id=>document.getElementById(id),canvases=new Map();
let playing=!matchMedia('(prefers-reduced-motion: reduce)').matches,clock=0,last=performance.now();
for(const d of data.designs){
 const option=document.createElement('option');option.value=d.slug;option.textContent=`${d.number} · ${d.label}`;$('design-filter').append(option);
 const card=document.createElement('article');card.className='example';card.dataset.example=d.slug;
 const canvas=document.createElement('canvas');canvas.width=WIDTH*2;canvas.height=HEIGHT*2;canvas.setAttribute('aria-label',d.label);canvas.role='img';
 const description=document.createElement('p');description.className='scope';description.style='padding:0 18px;margin:12px 0;font-size:12px';description.textContent=d.note;
 const links=document.createElement('div');links.className='gif-links';
 for(const [mode,label] of [['working','Working-stroke GIF'],['inversion','Full-inversion GIF']]){
  const a=document.createElement('a');a.href=`gifs/${d.slug}-${mode}.gif`;a.download=`${d.slug}-${mode}.gif`;a.textContent=label;links.append(a);
 }
 card.append(canvas,description,links);$('examples').append(card);canvases.set(d.slug,canvas);
}
function render(){
 const mode=$('view-mode').value,fraction=Number($('scrub').value),dark=document.documentElement.dataset.theme==='dark';
 $('examples').dataset.single=String($('design-filter').value!=='all');
 $('view-description').textContent=mode==='working'?'The reported windows include two 20 mm reserves. Chord angles describe endpoints; local tangent angles vary. All panels share one metric scale.':'The full range continues from below to above the hip. The path stays visible through projected overlap; red outlines flag unresolved wheel/chassis clearance. All panels share one metric scale.';
 for(const d of data.designs){
  const canvas=canvases.get(d.slug);canvas.parentElement.hidden=$('design-filter').value!=='all'&&$('design-filter').value!==d.slug;
  canvas.dataset.pose=JSON.stringify(drawExample(canvas,d,fraction,mode,{dark,clearance:$('show-clearance').checked,guide:$('show-guide').checked}));
 }
 $('play').textContent=playing?'Pause':'Play';
}
function tick(time){const dt=Math.min(time-last,100);last=time;if(playing&&!document.hidden){clock+=dt;const v=(1-Math.cos(2*Math.PI*clock/4800))/2;$('scrub').value=String(v);render();}requestAnimationFrame(tick);}
$('play').onclick=()=>{playing=!playing;render();};
$('restart').onclick=()=>{clock=0;$('scrub').value='0';render();};
$('scrub').oninput=()=>{playing=false;clock=Math.acos(1-2*Number($('scrub').value))*4800/(2*Math.PI);render();};
for(const id of ['view-mode','design-filter','show-clearance','show-guide'])$(id).onchange=()=>{if(id==='view-mode'){clock=0;$('scrub').value='0';}render();};
document.addEventListener('motion-lab-theme',render);
window.addEventListener('message',event=>{if(event.origin===location.origin&&event.data?.type==='motion-lab-deactivate'){playing=false;render();}});
window.DesignExamples={data,render,drawFrame(slug,mode,fraction){
 const design=data.designs.find(d=>d.slug===slug);if(!design)throw Error('Unknown design');
 const canvas=document.createElement('canvas');canvas.width=WIDTH;canvas.height=HEIGHT;
 const pose=drawExample(canvas,design,fraction,mode,{dark:false,clearance:true,guide:true});return {png:canvas.toDataURL('image/png'),pose};
}};
render();requestAnimationFrame(tick);
