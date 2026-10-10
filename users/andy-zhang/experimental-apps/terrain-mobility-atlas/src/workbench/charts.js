const COLORS = ['#b96a00', '#246b8e', '#697840', '#9a4570', '#6d5d92'];
let chartSequence = 0;

export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
}

export function formatNumber(value, digits = 2) {
  if (!Number.isFinite(value)) return '—';
  if (value === 0) return '0';
  if (Math.abs(value) < .001 || Math.abs(value) > 1e6) return value.toExponential(2);
  return value.toLocaleString('en-US', {maximumFractionDigits: digits});
}

// Retain local minima and maxima, rather than choosing every nth sample.
export function preserveExtrema(points, budget = 1200) {
  const clean = points.filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));
  if (clean.length <= budget) return clean;
  const buckets = Math.max(1, Math.floor((budget - 2) / 2));
  const size = (clean.length - 2) / buckets;
  const reduced = [clean[0]];
  for (let b = 0; b < buckets; b++) {
    const start = 1 + Math.floor(b * size);
    const end = Math.min(clean.length - 1, 1 + Math.floor((b + 1) * size));
    let min = start, max = start;
    for (let i = start + 1; i < end; i++) {
      if (clean[i].y < clean[min].y) min = i;
      if (clean[i].y > clean[max].y) max = i;
    }
    if (min === max) reduced.push(clean[min]);
    else if (min < max) reduced.push(clean[min], clean[max]);
    else reduced.push(clean[max], clean[min]);
  }
  reduced.push(clean.at(-1));
  return reduced;
}

function expandedExtent(values, fixed) {
  if (fixed) return fixed;
  let min = Infinity, max = -Infinity;
  for (const v of values) if (Number.isFinite(v)) {min = Math.min(min, v); max = Math.max(max, v);}
  if (min === Infinity) return [0, 1];
  if (min === max) {const delta = Math.max(Math.abs(min) * .1, .1); return [min - delta, max + delta];}
  const padding = (max - min) * .09;
  return [min - padding, max + padding];
}

function preserveScatter(points, budget = 500) {
  const clean = points.filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));
  if (clean.length <= budget) return clean;
  const buckets = Math.max(1,Math.floor(budget/4));
  const selected = new Set([0,clean.length-1]);
  for(let b=0;b<buckets;b++) {
    const start=Math.floor(b*clean.length/buckets),end=Math.floor((b+1)*clean.length/buckets);
    let xmin=start,xmax=start,ymin=start,ymax=start;
    for(let i=start+1;i<end;i++) {
      if(clean[i].x<clean[xmin].x)xmin=i;if(clean[i].x>clean[xmax].x)xmax=i;
      if(clean[i].y<clean[ymin].y)ymin=i;if(clean[i].y>clean[ymax].y)ymax=i;
    }
    [xmin,xmax,ymin,ymax].forEach(i=>selected.add(i));
  }
  return [...selected].sort((a,b)=>a-b).map(i=>clean[i]);
}

export function chartMarkup(options) {
  const {title, subtitle = '', xLabel, yLabel, series, xDomain, yDomain, scatter = false, referenceLines = [], height = 265, chartWidth = 800} = options;
  const id = `plot-${++chartSequence}`;
  const width = Math.max(250,chartWidth), left = width < 450 ? 62 : 76, right = 18, top = 20, bottom = 52;
  const plotW = width - left - right, plotH = height - top - bottom;
  const [xmin, xmax] = expandedExtent(series.flatMap(s => s.points.map(p => p.x)), xDomain);
  const [ymin, ymax] = expandedExtent([...series.flatMap(s => s.points.map(p => p.y)), ...referenceLines.map(l => l.value)], yDomain);
  const sx = x => left + (x - xmin) / (xmax - xmin || 1) * plotW;
  const sy = y => top + (ymax - y) / (ymax - ymin || 1) * plotH;
  let grids = '';
  const xTicks = width < 450 ? 2 : 4;
  for (let i = 0; i <= xTicks; i++) {
    const x = xmin + (xmax - xmin) * i / xTicks;
    grids += `<line class="gridline" x1="${sx(x)}" x2="${sx(x)}" y1="${top}" y2="${top + plotH}"/><text class="tick" x="${sx(x)}" y="${height - 28}" text-anchor="${i===0?'start':i===xTicks?'end':'middle'}">${formatNumber(x, 2)}</text>`;
  }
  for(let i=0;i<=4;i++) {
    const y = ymin + (ymax - ymin) * i / 4;
    grids += `<line class="gridline" x1="${left}" x2="${width - right}" y1="${sy(y)}" y2="${sy(y)}"/><text class="tick" x="${left - 10}" y="${sy(y) + 4}" text-anchor="end">${formatNumber(y, 2)}</text>`;
  }
  const refs = referenceLines.map(l => `<line class="reference-line" x1="${left}" x2="${width-right}" y1="${sy(l.value)}" y2="${sy(l.value)}"/><text class="reference-label" x="${width-right-4}" y="${sy(l.value)-5}" text-anchor="end">${escapeHtml(l.label)}</text>`).join('');
  const paths = series.map((s, index) => {
    const color = s.color || COLORS[index % COLORS.length];
    const points = scatter && !s.line ? preserveScatter(s.points) : preserveExtrema(s.points,1000);
    if (scatter && !s.line) return points.map(p => `<circle cx="${sx(p.x).toFixed(2)}" cy="${sy(p.y).toFixed(2)}" r="2.5" fill="${color}" opacity=".6"><title>${escapeHtml(s.label)}: ${formatNumber(p.x,3)} ${escapeHtml(xLabel)}, ${formatNumber(p.y,3)} ${escapeHtml(yLabel)}</title></circle>`).join('');
    const d = points.map((p,i) => `${i ? 'L' : 'M'}${sx(p.x).toFixed(2)},${sy(p.y).toFixed(2)}`).join(' ');
    return `<path d="${d}" fill="none" stroke="${color}" stroke-width="${s.width || 1.8}" ${s.dashed ? 'stroke-dasharray="6 4"' : ''} vector-effect="non-scaling-stroke"/>`;
  }).join('');
  const data = series.map((s,i) => ({label:s.label,color:s.color || COLORS[i%COLORS.length],points:scatter&&!s.line?preserveScatter(s.points):preserveExtrema(s.points,1600),line:s.line}));
  chartStore.set(id, {series:data,xmin,xmax,ymin,ymax,left,right,top,bottom,width,height,xLabel,yLabel,scatter,options});
  return `<figure class="plot-card" data-chart="${id}"><figcaption><h3>${escapeHtml(title)}</h3>${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ''}</figcaption><div class="plot-legend">${series.map((s,i) => `<span><i style="background:${s.color || COLORS[i%COLORS.length]}"></i>${escapeHtml(s.label)}</span>`).join('')}</div><div class="plot-wrap"><svg class="plot" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="${id}-title ${id}-desc" tabindex="0"><title id="${id}-title">${escapeHtml(title)}</title><desc id="${id}-desc">${escapeHtml(`${xLabel}; ${yLabel}. ${subtitle} ${series.map(s=>s.label).join(', ')}. Use left and right arrow keys to inspect values.`)}</desc><defs><clipPath id="${id}-clip"><rect x="${left}" y="${top}" width="${plotW}" height="${plotH}"/></clipPath></defs>${grids}<g clip-path="url(#${id}-clip)">${refs}${paths}</g><line class="axis" x1="${left}" x2="${width-right}" y1="${top+plotH}" y2="${top+plotH}"/><text class="axis-label" x="${left+plotW/2}" y="${height-5}" text-anchor="middle">${escapeHtml(xLabel)}</text><text class="axis-label" transform="translate(18 ${top+plotH/2}) rotate(-90)" text-anchor="middle">${escapeHtml(yLabel)}</text><line class="plot-cursor" x1="${left}" x2="${left}" y1="${top}" y2="${top+plotH}" visibility="hidden"/></svg><output class="plot-tooltip" aria-live="polite"></output></div></figure>`;
}

const chartStore = new Map();
const observers = new Set();
export function resetCharts() {for(const observer of observers)observer.disconnect();observers.clear();chartStore.clear();}

export function attachCharts(root) {
  root.querySelectorAll('[data-chart]').forEach(figure => {
    let spec = chartStore.get(figure.dataset.chart);
    if (!spec) return;
    let svg,tooltip,cursor;
    let fraction = .5;
    const inspect = f => {
      fraction = Math.min(1, Math.max(0, f));
      const target = spec.xmin + fraction * (spec.xmax - spec.xmin);
      const picked = spec.series.map(s => {
        let lo = 0, hi = s.points.length - 1;
        while (lo < hi) {const mid = Math.floor((lo+hi)/2); if(s.points[mid].x < target) lo=mid+1; else hi=mid;}
        const a = s.points[lo], b = s.points[Math.max(0,lo-1)];
        const p = a && b ? (Math.abs(a.x-target)<Math.abs(b.x-target) ? a : b) : a || b;
        return p ? `${s.label}: ${formatNumber(p.y,3)}` : `${s.label}: —`;
      });
      const pos = spec.left + fraction * (spec.width-spec.left-spec.right);
      cursor.setAttribute('x1',pos);cursor.setAttribute('x2',pos);cursor.setAttribute('visibility','visible');
      tooltip.textContent = `${spec.xLabel}: ${formatNumber(target,3)} · ${spec.yLabel} · ${picked.join(' / ')}`;
    };
    const inspectScatter = (px,py) => {
      let nearest=null,dist=Infinity;
      for(const series of spec.series.filter(s=>!s.line))for(const p of series.points){
        const x=spec.left+(p.x-spec.xmin)/(spec.xmax-spec.xmin)*(spec.width-spec.left-spec.right);
        const y=spec.top+(spec.ymax-p.y)/(spec.ymax-spec.ymin)*(spec.height-spec.top-spec.bottom);
        const d=(x-px)**2+(y-py)**2;if(d<dist){dist=d;nearest={p,series,x};}
      }
      if(!nearest)return;
      cursor.setAttribute('x1',nearest.x);cursor.setAttribute('x2',nearest.x);cursor.setAttribute('visibility','visible');
      tooltip.textContent=`${nearest.series.label} · ${spec.xLabel}: ${formatNumber(nearest.p.x,3)} · ${spec.yLabel}: ${formatNumber(nearest.p.y,3)}${nearest.p.meta?' · '+nearest.p.meta:''}`;
    };
    const bind = () => {
      svg=figure.querySelector('svg');tooltip=figure.querySelector('output');cursor=figure.querySelector('.plot-cursor');
      svg.addEventListener('pointermove',event => {
      const box = svg.getBoundingClientRect();
      const x = (event.clientX-box.left)/box.width*spec.width;
      const y = (event.clientY-box.top)/box.height*spec.height;
      if(spec.scatter)inspectScatter(x,y);else inspect((x-spec.left)/(spec.width-spec.left-spec.right));
      });
      svg.addEventListener('pointerleave',()=> {if(document.activeElement!==svg){cursor.setAttribute('visibility','hidden');tooltip.textContent='';}});
      svg.addEventListener('focus',()=>{if(spec.scatter)inspectScatter(spec.width*.5,spec.height*.5);else inspect(fraction);});
      let scatterIndex=0;
      svg.addEventListener('keydown',event=>{
        if(event.key!=='ArrowRight'&&event.key!=='ArrowLeft')return;
        event.preventDefault();
        if(spec.scatter){
          const series=spec.series.find(s=>!s.line), points=series?.points||[];if(!points.length)return;
          scatterIndex=(scatterIndex+(event.key==='ArrowRight'?1:-1)+points.length)%points.length;
          const p=points[scatterIndex];
          inspectScatter(spec.left+(p.x-spec.xmin)/(spec.xmax-spec.xmin)*(spec.width-spec.left-spec.right),spec.top+(spec.ymax-p.y)/(spec.ymax-spec.ymin)*(spec.height-spec.top-spec.bottom));
        }else inspect(fraction+(event.key==='ArrowRight'?.02:-.02));
      });
    };
    bind();
    const resize = () => {
      const actualWidth=Math.floor(figure.querySelector('.plot-wrap').getBoundingClientRect().width);
      if(actualWidth<250||Math.abs(actualWidth-spec.width)<2)return;
      const oldId=figure.dataset.chart;
      const template=document.createElement('template');template.innerHTML=chartMarkup({...spec.options,chartWidth:actualWidth});
      const fresh=template.content.firstElementChild;
      figure.innerHTML=fresh.innerHTML;figure.dataset.chart=fresh.dataset.chart;
      spec=chartStore.get(fresh.dataset.chart);chartStore.delete(oldId);bind();
    };
    resize();
    if(typeof ResizeObserver!=='undefined'){const observer=new ResizeObserver(resize);observer.observe(figure);observers.add(observer);}
  });
}

export function nodeGraphMarkup(nodes, selectedId) {
  const positions = {terrain:[28,65],scenario:[28,190],geometry:[28,315],dynamics:[300,190],joint:[565,190],actuator:[565,350],report:[830,190],validation:[300,475]};
  const edges = [['terrain','dynamics'],['scenario','dynamics'],['geometry','dynamics'],['dynamics','joint'],['joint','actuator'],['actuator','report'],['joint','report']];
  const lines = edges.map(([a,b]) => {
    const [ax,ay]=positions[a], [bx,by]=positions[b];
    if(a==='joint'&&b==='actuator') return `<path d="M ${ax+104} ${ay+82} L ${bx+104} ${by}"/>`;
    if(a==='actuator') return `<path d="M ${ax+208} ${ay+40} L ${bx-20} ${ay+40} L ${bx-20} ${by+50} L ${bx} ${by+50}"/>`;
    return `<path d="M ${ax+208} ${ay+40} C ${ax+236} ${ay+40}, ${bx-30} ${by+40}, ${bx} ${by+40}"/>`;
  }).join('');
  return `<div class="graph-scroll"><div class="node-canvas"><svg class="graph-edges" viewBox="0 0 1070 585" aria-hidden="true"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M 0 0 L 8 4 L 0 8 z" fill="#777b6b"/></marker></defs><g fill="none" stroke="#9a9e8e" stroke-width="1.6" marker-end="url(#arrow)">${lines}<path d="M 565 390 L 440 390 L 440 272" stroke-dasharray="6 4"/><path d="M 300 515 L 16 515 L 16 105 L 28 105" stroke-dasharray="6 4"/></g><text x="380" y="422">candidate limits → response</text><text x="64" y="543">measured validation → revised inputs</text></svg>${nodes.map(node=>{const [x,y]=positions[node.id];return `<button class="graph-node ${node.id===selectedId?'selected':''}" data-node="${node.id}" style="left:${x}px;top:${y}px" aria-pressed="${node.id===selectedId}"><small>${escapeHtml(node.stage)}</small><strong>${escapeHtml(node.label)}</strong><span>${escapeHtml(node.short)}</span></button>`;}).join('')}</div></div>`;
}
