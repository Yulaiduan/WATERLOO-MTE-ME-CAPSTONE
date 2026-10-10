/** Detailed-linkage Plotly views, mounted by main.js via the /linkage/ route.
 * Inputs: recorded SI-derived series with explicit display units in axis labels.
 * Outputs: responsive zoom/pan/hover/image-export charts and keyboard readouts.
 * Limits: line display uses peak-preserving reduction; saved traces stay complete.
 * Requires the app-local pinned Plotly script loaded before the main module.
 */
const colors=['#a8730b','#286d8a','#657f3b','#8d5583'];
const darkColors=['#ffc663','#70b9db','#b3cd86','#d59dca'];
export const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const fmt=(v,d=2)=>Number.isFinite(v)?(v!==0&&(Math.abs(v)<.0001||Math.abs(v)>1e6)?v.toExponential(2):v.toLocaleString('en-US',{maximumFractionDigits:d})):'—';
let store=[],mounted=[];
const dark=()=>document.documentElement.dataset.theme==='dark';
const palette=()=>dark()?darkColors:colors;
const seriesColor=(s,i)=>s.color?(dark()?({'#a8730b':'#ffc663','#286d8a':'#70b9db','#657f3b':'#b3cd86','#8d5583':'#d59dca','#a3aa97':'#95a48c'}[s.color]||s.color):s.color):palette()[i%colors.length];
export function clearCharts(){
  for(const item of mounted){item.alive=false;item.observer.disconnect();window.Plotly?.purge(item.plot);}
  mounted=[];store=[];
}
export function chart({title,xLabel,yLabel,series,scatter=false,logX=false,subtitle='',zero=false}){
  const id=store.length;store.push({title,xLabel,yLabel,series,scatter,logX,zero});
  return `<section class="card plot-card" data-plot="${id}"><h3>${esc(title)}</h3>${subtitle?`<p>${esc(subtitle)}</p>`:''}<div class="plot" tabindex="0" role="region" aria-label="${esc(title)}. ${esc(xLabel)}; ${esc(yLabel)}. Use the chart toolbar to zoom, pan, reset or save an image. Arrow keys inspect samples."></div><output class="plot-tooltip" aria-live="polite">Hover to inspect values. Drag to zoom; Shift-drag to pan. Double-click to reset. Arrow keys inspect the first series.</output></section>`;
}
function reduce(points,n=900){
  if(points.length<=n)return points;
  const stride=points.length/(n/2),out=[points[0]];
  for(let i=0;i<points.length;i+=stride){
    const bucket=points.slice(Math.floor(i),Math.min(points.length,Math.floor(i+stride)));
    let lo=bucket[0],hi=lo;
    for(const p of bucket){if(p.y<lo.y)lo=p;if(p.y>hi.y)hi=p;}
    out.push(lo,hi);
  }
  out.push(points.at(-1));return out.sort((a,b)=>a.x-b.x);
}
function layout(spec){
  const isDark=dark(),text=isDark?'#e8ede2':'#272b21',muted=isDark?'#b2bba6':'#616957',grid=isDark?'#394333':'#e6eadf',surface=isDark?'#22291e':'#ffffff';
  const axis={color:muted,gridcolor:grid,linecolor:grid,zerolinecolor:isDark?'#a1b086':'#5c6c48',automargin:true,title:{font:{size:12,color:text}},tickfont:{size:11},fixedrange:false};
  return {autosize:true,height:320,paper_bgcolor:surface,plot_bgcolor:surface,font:{family:'Arial, Helvetica, sans-serif',size:12,color:text},margin:{l:62,r:18,t:24,b:57},
    xaxis:{...axis,title:{...axis.title,text:spec.xLabel},type:spec.logX?'log':'linear',zeroline:spec.zero},
    yaxis:{...axis,title:{...axis.title,text:spec.yLabel},zeroline:spec.zero},
    dragmode:'zoom',hovermode:spec.scatter?'closest':'x unified',legend:{orientation:'h',x:0,y:1.08,font:{size:11,color:muted}},
    modebar:{bgcolor:'transparent',color:muted,activecolor:isDark?'#ffc663':'#a8730b'},
    uirevision:`linkage-${spec.title}`,hoverlabel:{font:{size:12}},
    ...(spec.zero?{shapes:[{type:'line',xref:'x',yref:'paper',x0:0,x1:0,y0:0,y1:1,line:{color:isDark?'#b3cd86':'#5c6c48',width:1.5,dash:'dash'}}]}:{})};
}
function traces(spec){
  return spec.series.map((s,i)=>{
    const finite=s.points.filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)&&(!spec.logX||p.x>0));
    const scatter=spec.scatter&&!s.line;
    // Scatter preserves operating-point samples. Lines retain each time bucket's extrema.
    const points=scatter?finite:reduce(finite),color=seriesColor(s,i);
    return {type:'scatter',mode:scatter?'markers':'lines',name:s.label,x:points.map(p=>p.x),y:points.map(p=>p.y),customdata:points.map(p=>p.note||''),
      line:{color,width:1.8,dash:s.dashed?'dash':'solid'},marker:{color,size:(s.radius||2.7)*2,opacity:.75},
      hovertemplate:`${esc(s.label)}<br>${esc(spec.xLabel)}: %{x:.5g}<br>${esc(spec.yLabel)}: %{y:.5g}<br>%{customdata}<extra></extra>`};
  });
}
function draw(item){
  if(!item.alive)return;
  const Plotly=window.Plotly;
  if(!Plotly){item.tip.textContent='Plotly is unavailable. Restart Motion Lab after installing its pinned dependencies.';return;}
  Plotly.react(item.plot,traces(item.spec),layout(item.spec),{responsive:true,displaylogo:false,displayModeBar:true,scrollZoom:true,doubleClick:'reset+autosize',toImageButtonOptions:{format:'png',filename:`linkage-${item.spec.title.toLowerCase().replace(/[^a-z0-9]+/g,'-')}`,scale:2}}).catch(error=>{if(item.alive)item.tip.textContent=`Chart could not render: ${error.message}`;});
}
export function refreshChartThemes(){for(const item of mounted)draw(item);}
export function mountCharts(root){
  root.querySelectorAll('[data-plot]').forEach(el=>{
    const spec=store[Number(el.dataset.plot)],plot=el.querySelector('.plot'),tip=el.querySelector('output');
    if(!spec)return;
    const item={spec,plot,tip,alive:true,index:0};
    item.observer=new ResizeObserver(()=>{if(item.alive&&plot._fullLayout)window.Plotly?.Plots.resize(plot);});
    item.observer.observe(plot);mounted.push(item);draw(item);
    const inspect=()=>{
      const points=spec.series[0]?.points.filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)&&(!spec.logX||p.x>0))||[];
      const p=points[item.index];
      if(p)tip.textContent=`${spec.series[0].label} · ${spec.xLabel}: ${fmt(p.x,4)} · ${spec.yLabel}: ${fmt(p.y,4)}${p.note?` · ${p.note}`:''}`;
    };
    plot.addEventListener('keydown',e=>{
      if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
      e.preventDefault();const count=spec.series[0]?.points.filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)&&(!spec.logX||p.x>0)).length||0;
      item.index=e.key==='Home'?0:e.key==='End'?count-1:Math.max(0,Math.min(count-1,item.index+(e.key==='ArrowRight'?1:-1)));inspect();
    });
  });
}
