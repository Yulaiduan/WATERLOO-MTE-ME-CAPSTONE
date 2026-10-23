/** Shared offline Plotly lifecycle, theme and responsive sizing for Kinefold.
 * Load after the pinned local Plotly basic runtime. Inputs: chart traces/layouts
 * in the caller's declared engineering units. Outputs: actual Plotly graphs;
 * geometry/FBD SVGs remain separate illustrations. Image downloads are removed;
 * contextual data exports remain in the app-folder storage service.
 */
globalThis.KinefoldPlotly = (() => {
  'use strict';
  const registry = new Map(), pendingCursors = new Map();
  const sizes = new ResizeObserver(entries => { for(const entry of entries)resize(entry.target); });
  let cursorFrame = 0;
  const plain = value => value && typeof value === 'object' && !Array.isArray(value);
  const merge = (base, extra) => {
    const out = {...base};
    for (const [key, value] of Object.entries(extra || {})) out[key] = plain(value) && plain(base?.[key]) ? merge(base[key], value) : value;
    return out;
  };
  function color(value) {
    if (typeof value !== 'string' || !value.includes('var(')) return value;
    return value.replace(/var\((--[\w-]+)(?:,\s*([^)]*))?\)/g, (_, key, fallback) => getComputedStyle(document.documentElement).getPropertyValue(key).trim() || fallback || '#52665a');
  }
  function resolved(value) {
    if (typeof value === 'string') return color(value);
    if (Array.isArray(value)) return value.map(resolved);
    if (plain(value)) return Object.fromEntries(Object.entries(value).map(([key, child]) => [key, resolved(child)]));
    return value;
  }
  function themedLayout(extra, key) {
    const axis = {gridcolor:color('var(--line)'), zerolinecolor:color('var(--muted)'), tickfont:{size:13}, automargin:true};
    const base = {autosize:true, height:360, margin:{l:78,r:30,t:40,b:64},
      paper_bgcolor:color('var(--paper)'), plot_bgcolor:color('var(--paper)'),
      font:{family:'Segoe UI, system-ui, sans-serif',size:13,color:color('var(--ink)')},
      hoverlabel:{bgcolor:color('var(--paper)'),font:{color:color('var(--ink)'),size:12}},
      xaxis:axis, yaxis:axis, dragmode:'zoom', hovermode:'closest',
      legend:{orientation:'h',y:-.22,x:0,font:{size:12}}, uirevision:key};
    return resolved(merge(base, extra));
  }
  async function react(node, traces, layout = {}, options = {}) {
    if (!globalThis.Plotly) {
      node.textContent = 'The offline Plotly runtime could not be loaded. Restart Kinefold and reload.';
      throw Error('Offline Plotly runtime unavailable.');
    }
    node.dataset.kinefoldPlot = options.key || node.id || 'chart';
    node.classList.add('kinefold-plot');
    if(!registry.has(node))sizes.observe(node);
    registry.set(node, {traces, layout, options});
    const result = await Plotly.react(node, resolved(traces), themedLayout(layout, options.key || node.id),
      {responsive:true, displaylogo:false, scrollZoom:false, displayModeBar:'hover',
       modeBarButtonsToRemove:['toImage','sendDataToCloud'], showTips:true});
    if (node.isConnected) {
      resize(node);
      if(Number.isFinite(Number(node.dataset.cursorTime)))cursor(node,Number(node.dataset.cursorTime));
      if(options.onScrub&&node.on){
        node.removeAllListeners('plotly_click');
        node.on('plotly_click',event=>{if(event.points?.length)options.onScrub(event.points[0]);});
      }
    }
    return result;
  }
  function resize(node) {
    if (!node?.isConnected || !node._fullLayout || !node.getClientRects().length || node.clientWidth < 20) return;
    Plotly.Plots.resize(node).then(()=>{if(node.dataset.cursorTime!==undefined)cursor(node,Number(node.dataset.cursorTime));}).catch(() => {});
  }
  function resizeAll(root = document) {
    for (const node of root.querySelectorAll('[data-kinefold-plot]')) resize(node);
  }
  function purge(root) {
    const nodes = [...(root?.matches?.('[data-kinefold-plot]') ? [root] : []), ...(root?.querySelectorAll?.('[data-kinefold-plot]') || [])];
    for (const node of nodes) {
      registry.delete(node); pendingCursors.delete(node);sizes.unobserve(node);
      if (globalThis.Plotly && node._fullLayout) Plotly.purge(node);
    }
  }
  function cursor(node, x) {
    if (!node?._fullLayout || !Number.isFinite(x)) return;
    node.dataset.cursorTime = String(x); pendingCursors.set(node, x);
    if (cursorFrame) return;
    cursorFrame = requestAnimationFrame(() => {
      cursorFrame = 0;
      for (const [host, time] of pendingCursors) {
        if (!host.isConnected || !host._fullLayout || !host.getClientRects().length || host.clientWidth<20) continue;
        const shapes = (host.layout.shapes || []).filter(shape => shape.name !== 'kinefold-cursor');
        shapes.push({name:'kinefold-cursor',type:'line',xref:'x',yref:'paper',x0:time,x1:time,y0:0,y1:1,
          line:{color:color('var(--ink)'),width:1.3},layer:'above'});
        Plotly.relayout(host, {shapes}).catch(() => {});
      }
      pendingCursors.clear();
    });
  }
  document.addEventListener('toggle', event => {
    if (event.target.open) requestAnimationFrame(() => resizeAll(event.target));
  }, true);
  window.addEventListener('kinefold-solver-tab', () => requestAnimationFrame(() => resizeAll()));
  window.addEventListener('kinefold-theme-change', () => {
    for (const [node, state] of registry) if (node.isConnected) react(node, state.traces, state.layout, state.options).catch(() => {});
  });
  new MutationObserver(records => {
    for (const record of records) for (const node of record.removedNodes) if (node.nodeType === 1 && !node.isConnected) purge(node);
  }).observe(document.body, {childList:true,subtree:true});
  return {react,color,resize,resizeAll,purge,cursor,themedLayout};
})();
