/** Mount saved-run comparison: mountComparison(root,{theme,onRunProfile}).
 * Inputs: full library records and optional callback that explicitly runs a profile.
 * Outputs: Plotly overlays/deltas, independent trace visibility, split plots and portable JSON.
 * Limits: browser-local library, documented source units, recorded overlap/interpolation only.
 */
import {listRecords,getRecord,normalizeImport,saveRecord,downloadJSON,MAX_IMPORT_BYTES} from './library.js';
import {COMPARISON_SCHEMA,MAX_PANELS,MAX_TRACES,recordSources,seriesFor,compareSeries,leaves,splitPanel,removePanel,normalizeWorkspace} from './comparison-data.js';

function el(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function button(text,action){const node=el('button',text);node.type='button';node.addEventListener('click',action);return node;}
function option(value,text){const node=el('option',text);node.value=value;return node;}
function labeled(text,control){const label=el('label',text);label.append(control);return label;}
const freshPanel=()=>({mode:'overlay',legend:true,reference:null,traces:[]});
const identity=()=>globalThis.crypto?.randomUUID?.()||`compare-${Date.now()}-${Math.random().toString(16).slice(2)}`;
const number=value=>Number.isFinite(value)?value===0?'0':Math.abs(value)<.001||Math.abs(value)>=10000?value.toExponential(4):value.toPrecision(6):'—';

export function mountComparison(root,{theme='light',onRunProfile}={}){
  let currentTheme=theme,records=[],sources=[],summaries=[],active='plot-1',layout={kind:'panel',id:active},panels={[active]:freshPanel()},revision=0;
  const selectedLibrary=new Set(),plotNodes=new Map(),seriesCache=new Map(),openOptions=new Set();
  let channelsOpen=true,focusPlots=false;
  root.replaceChildren();root.classList.add('comparison-workspace');
  const top=el('div',undefined,'comparison-topbar');
  const sourceTools=el('details',undefined,'comparison-source-tools');
  sourceTools.append(el('summary','Sources & help'));
  sourceTools.append(el('p','Load recordings or run saved profiles. Select a plot and click channels on the right. Plot controls contain splits, reference selection, channel visibility and legend settings.','muted'));
  sourceTools.append(el('p','Signed delta is candidate minus reference over shared timestamps, with linear interpolation and sample RMS. Wheel-model pin forces compare Pymunk step averages with instantaneous mathematical loads; startup constraint initialization can dominate maxima.','muted'));
  const error=el('div','','error');error.hidden=true;error.setAttribute('role','alert');
  const status=el('p','','comparison-status');status.setAttribute('role','status');
  const toggleChannels=button('Hide channels',()=>{channelsOpen=!channelsOpen;view();});
  const toggleFocus=button('Focus plots',()=>{focusPlots=!focusPlots;view();});
  top.append(el('h2','Comparison'),status,toggleChannels,toggleFocus);
  const toolbar=el('div',undefined,'comparison-toolbar');
  const importer=el('input');importer.type='file';importer.accept='.json,application/json';importer.multiple=true;importer.setAttribute('aria-label','Import comparison, profile or recorded data JSON');
  toolbar.append(button('Load profiles / recordings',()=>{library.hidden=!library.hidden;if(!library.hidden)safe(refresh);}),labeled('Import JSON',importer),button('Export comparison JSON',()=>safe(exportWorkspace)));
  const library=el('section',undefined,'comparison-library');library.hidden=true;
  const librarySearch=el('input');librarySearch.type='search';librarySearch.placeholder='Search saved profiles and runs';librarySearch.setAttribute('aria-label','Search saved profiles and runs');
  const listing=el('div',undefined,'comparison-library-list'),loadButton=button('Load selected (run profiles)',()=>safe(loadSelected));
  library.append(el('p','A profile contains settings only. Loading a profile explicitly runs its solver and appends a new run to your library.'),librarySearch,button('Refresh library',()=>safe(refresh)),listing,loadButton);
  const body=el('div',undefined,'comparison-body'),plots=el('div',undefined,'comparison-plots'),side=el('aside',undefined,'comparison-sidebar');
  const channelSearch=el('input');channelSearch.type='search';channelSearch.placeholder='Search channels';channelSearch.setAttribute('aria-label','Search comparison channels');
  const activeLabel=el('p','','comparison-active-label'),sourceList=el('div',undefined,'comparison-source-list'),channels=el('div',undefined,'comparison-channel-list');
  const provenance=el('details',undefined,'comparison-provenance');provenance.append(el('summary','Source details'),sourceList);
  side.append(activeLabel,channelSearch,channels,provenance);
  sourceTools.append(toolbar,library);body.append(plots,side);root.append(top,sourceTools,error,body);

  function resize(){for(const node of plotNodes.values())if(node.chart.offsetWidth)globalThis.Plotly?.Plots.resize(node.chart);}
  function view(){
    root.classList.toggle('comparison-focus',focusPlots);root.classList.toggle('comparison-no-sidebar',!channelsOpen||focusPlots);
    side.hidden=!channelsOpen||focusPlots;toggleChannels.textContent=channelsOpen?'Hide channels':'Show channels';toggleChannels.setAttribute('aria-pressed',String(channelsOpen));toggleChannels.hidden=focusPlots;
    toggleFocus.textContent=focusPlots?'Exit focus':'Focus plots';toggleFocus.setAttribute('aria-pressed',String(focusPlots));
    if(focusPlots)sourceTools.open=false;
    for(const {id}of leaves(layout))safe(()=>draw(id));requestAnimationFrame(resize);
  }
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&focusPlots&&!root.hidden&&!document.querySelector('dialog[open]')){focusPlots=false;view();}});

  function report(cause){error.textContent=cause instanceof Error?cause.message:String(cause);error.hidden=false;}
  async function safe(action){error.hidden=true;try{return await action();}catch(cause){report(cause);}}
  function rebuildSources(){sources=records.flatMap(item=>recordSources(item.record,item.id));seriesCache.clear();}
  function series(sourceId,key){const token=`${sourceId}|${key}`;if(!seriesCache.has(token)){const source=sources.find(s=>s.id===sourceId);if(!source)throw new Error('Source recording is missing.');seriesCache.set(token,seriesFor(source,key));}return seriesCache.get(token);}
  function sourceName(source){return `${source.name} · ${source.record.backend||'dataset'}${source.table==='Recorded samples'?'':` · ${source.table}`}`;}
  function setActive(id){active=id;for(const [key,node]of plotNodes)node.container.classList.toggle('is-active',key===active);renderChannels();}
  function ensureTrace(panel,source,key){if(panel.traces.some(trace=>trace.sourceId===source.id&&trace.key===key))return;if(panel.traces.length>=MAX_TRACES)throw new Error(`At most ${MAX_TRACES} channels per plot. Remove a channel before adding more.`);panel.traces.push({sourceId:source.id,key,visible:true});}
  function defaultKey(list){for(const key of ['chassis_displacement_mm','tip_height_m','tip_y','theta_deg'])if(list.some(source=>source.channels.some(channel=>channel.key===key)))return key;return list[0]?.channels[0]?.key;}

  /** Ordinary loads overlay default displacement/angle. paired creates overlay plus two delta panels. */
  async function addRecords(input,{paired=false}={}){
    if(!Array.isArray(input))throw new Error('Pass full source records as an array.');
    const prepared=input.map(original=>{
      const checked=normalizeImport(original,original.name||'Comparison source');
      if(!checked.result)throw new Error(`“${checked.name}” is a profile with no data. Use Load profiles to run it first.`);
      // Retain full provenance (IDs, creation timestamps, configs and original result) after validation.
      return {id:original.id||identity(),record:JSON.parse(JSON.stringify({...original,...checked}))};
    });
    if(records.length+prepared.filter(item=>!records.some(existing=>existing.id===item.id)).length>64)throw new Error('At most 64 source recordings per comparison.');
    const added=[];
    for(const item of prepared){if(!records.some(existing=>existing.id===item.id)){records.push(item);added.push(item.id);}}
    rebuildSources();const incoming=sources.filter(source=>prepared.some(item=>item.id===source.recordId));
    if(paired&&incoming.length>=2){
      // Comparison is a deliberate fresh layout; source datasets remain retained for later channels.
      active='plot-1';layout={kind:'split',direction:'vertical',first:{kind:'panel',id:active},second:{kind:'split',direction:'horizontal',first:{kind:'panel',id:'plot-2'},second:{kind:'panel',id:'plot-3'}}};
      panels={'plot-1':freshPanel(),'plot-2':{...freshPanel(),mode:'delta'},'plot-3':{...freshPanel(),mode:'delta'}};
      const reference=incoming.find(source=>['math','counterbalance_math'].includes(source.record.backend))||incoming[0];
      const key=defaultKey(incoming),theta=incoming.some(source=>source.channels.some(channel=>channel.key==='theta_deg'))?'theta_deg':key;
      for(const [id,selectedKey]of [['plot-1',key],['plot-2',key],['plot-3',theta]]){
        panels[id].reference=reference.id;
        for(const source of incoming)if(source.channels.some(channel=>channel.key===selectedKey))ensureTrace(panels[id],source,selectedKey);
      }
    }else if(sources.length){
      const panel=panels[active],key=panel.traces[0]?.key||defaultKey(incoming);
      for(const source of incoming)if(source.channels.some(channel=>channel.key===key))ensureTrace(panel,source,key);
      panel.reference ||= incoming[0]?.id;
      // Multi-select loads may arrive one at a time; keep already established default plots comparable.
      for(const [id,other]of Object.entries(panels))if(id!==active&&other.traces.length){
        const otherKey=other.traces[0].key;
        for(const source of incoming)if(source.channels.some(channel=>channel.key===otherKey))ensureTrace(other,source,otherKey);
      }
      if(leaves(layout).length===1&&incoming.some(source=>source.channels.some(channel=>channel.key==='theta_deg'))&&key!=='theta_deg'){
        const id=identity();layout=splitPanel(layout,active,'vertical',id);panels[id]=freshPanel();panels[id].reference=panel.reference;
        for(const source of incoming)if(source.channels.some(channel=>channel.key==='theta_deg'))ensureTrace(panels[id],source,'theta_deg');
      }
    }
    renderAll();status.textContent=`${records.length} recordings · ${sources.length} tables`;
    return added;
  }

  function renderChannels(){
    activeLabel.textContent=`Channels → ${plotTitle(active)}`;channels.replaceChildren();
    const groups=new Map();
    for(const source of sources)for(const channel of source.channels){const token=`${source.model}|${channel.key}|${channel.unit}`;if(!groups.has(token))groups.set(token,{...channel,model:source.model,sources:[]});groups.get(token).sources.push(source);}
    const query=channelSearch.value.toLowerCase();
    for(const group of [...groups.values()].filter(group=>`${group.key} ${group.unit} ${group.model}`.toLowerCase().includes(query)).sort((a,b)=>a.key.localeCompare(b.key))){
      const add=button('',()=>safe(()=>{
        const panel=panels[active],missing=group.sources.filter(source=>!panel.traces.some(trace=>trace.sourceId===source.id&&trace.key===group.key));
        if(panel.traces.length+missing.length>MAX_TRACES)throw new Error(`This would exceed ${MAX_TRACES} traces in the active plot.`);
        for(const source of group.sources)ensureTrace(panel,source,group.key);
        panel.reference ||= group.sources[0]?.id;renderPanelContents(active);
      }));
      add.className='comparison-channel';add.title=`${group.model} · add ${group.sources.length} sources to ${plotTitle(active)}`;add.append(el('strong',group.key),el('span',`${group.unit} · ${group.sources.length}`));channels.append(add);
    }
    if(!channels.childElementCount)channels.append(el('p',sources.length?'No matching channels.':'Load recordings to choose channels.','muted'));
    sourceList.replaceChildren();
    for(const item of records){const source=el('details'),summary=el('summary',`${item.record.name} · ${item.record.backend||'dataset'}`),meta=el('pre',JSON.stringify({id:item.record.id,created_at:item.record.created_at,source_created_at:item.record.source_created_at,config:item.record.config,engine:item.record.result?.engine,units:item.record.result?.units,scope:item.record.result?.scope},null,2));source.append(summary,meta,button('Download original JSON',()=>downloadJSON(item.record,`${item.record.name}.json`)));sourceList.append(source);}
  }
  function plotTitle(id){return `Plot ${leaves(layout).findIndex(panel=>panel.id===id)+1}`;}
  function clearPlots(){for(const node of plotNodes.values()){node.observer?.disconnect();globalThis.Plotly?.purge(node.chart);}plotNodes.clear();plots.replaceChildren();}
  function renderAll(){
    revision++;clearPlots();
    function build(node){
      if(node.kind==='split'){const box=el('div',undefined,`comparison-split comparison-split-${node.direction}`);box.append(build(node.first),build(node.second));return box;}
      const container=el('section',undefined,'comparison-plot-panel');container.dataset.plotId=node.id;container.classList.toggle('is-active',node.id===active);
      const heading=el('div',undefined,'comparison-plot-header'),select=button(plotTitle(node.id),()=>setActive(node.id)),label=el('span','','comparison-plot-label');select.className='comparison-select-plot';heading.append(select,label);
      const options=el('div',undefined,'comparison-options'),actions=el('div',undefined,'comparison-plot-actions');options.hidden=!openOptions.has(node.id);
      const more=button('Controls',()=>{if(openOptions.has(node.id))openOptions.delete(node.id);else openOptions.add(node.id);options.hidden=!openOptions.has(node.id);more.setAttribute('aria-expanded',String(!options.hidden));requestAnimationFrame(resize);});
      more.className='comparison-options-toggle';more.setAttribute('aria-label',`${plotTitle(node.id)} controls`);more.setAttribute('aria-expanded',String(!options.hidden));heading.append(more);
      for(const direction of ['horizontal','vertical']){const split=button(direction==='horizontal'?'Split side by side':'Split stacked',()=>safe(()=>{const id=identity();layout=splitPanel(layout,node.id,direction,id);panels[id]=freshPanel();panels[id].reference=panels[node.id].reference;active=id;renderAll();}));split.disabled=leaves(layout).length>=MAX_PANELS;actions.append(split);}
      const remove=button('Remove plot',()=>safe(()=>{const next=removePanel(layout,node.id);if(!next)throw new Error('Keep at least one plot.');layout=next;delete panels[node.id];openOptions.delete(node.id);if(active===node.id)active=leaves(layout)[0].id;renderAll();}));remove.disabled=leaves(layout).length===1;actions.append(remove);
      const controls=el('div',undefined,'comparison-plot-controls'),traceList=el('div',undefined,'comparison-traces'),chart=el('div',undefined,'comparison-chart'),messages=el('div',undefined,'comparison-plot-messages'),stats=el('div',undefined,'comparison-delta-stats');
      chart.setAttribute('aria-label',`${plotTitle(node.id)} comparison chart`);options.append(actions,controls,traceList);container.append(heading,options,chart,messages,stats);
      const observer=new ResizeObserver(()=>{if(chart.offsetWidth&&chart._fullLayout)globalThis.Plotly?.Plots.resize(chart);});observer.observe(chart);
      container.addEventListener('pointerdown',()=>setActive(node.id));plotNodes.set(node.id,{container,controls,traceList,chart,messages,stats,label,observer});return container;
    }
    plots.append(build(layout));renderChannels();for(const {id}of leaves(layout))renderPanelContents(id);
  }
  function renderPanelContents(id){
    const nodes=plotNodes.get(id),panel=panels[id];if(!nodes)return;
    const description=[...new Set(panel.traces.map(trace=>trace.key))].join(' · ');nodes.label.textContent=(panel.mode==='delta'?'Δ ':'')+(description||'Choose channels');nodes.label.title=nodes.label.textContent;
    nodes.controls.replaceChildren();
    const mode=el('select');mode.setAttribute('aria-label',`${plotTitle(id)} display mode`);mode.append(option('overlay','Overlay source values'),option('delta','Signed delta: candidate − reference'));mode.value=panel.mode;mode.addEventListener('change',()=>{panel.mode=mode.value;renderPanelContents(id);});
    const reference=el('select');reference.setAttribute('aria-label',`${plotTitle(id)} reference recording`);reference.append(option('','Choose reference recording'));for(const source of sources)reference.append(option(source.id,sourceName(source)));reference.value=panel.reference||'';reference.addEventListener('change',()=>{panel.reference=reference.value||null;renderPanelContents(id);});
    const legend=el('input');legend.type='checkbox';legend.checked=panel.legend;legend.setAttribute('aria-label',`${plotTitle(id)} show legend`);legend.addEventListener('change',()=>{panel.legend=legend.checked;safe(()=>draw(id));});
    nodes.controls.append(labeled('Display',mode),labeled('Reference',reference),labeled('Show legend',legend));
    nodes.traceList.replaceChildren();
    panel.traces.forEach((trace,index)=>{
      const source=sources.find(source=>source.id===trace.sourceId),row=el('div',undefined,'comparison-trace-row'),check=el('input');check.type='checkbox';check.checked=trace.visible;check.setAttribute('aria-label',`Show ${source?.name} ${trace.key} in ${plotTitle(id)}`);check.addEventListener('change',()=>{trace.visible=check.checked;safe(()=>draw(id));});
      const label=el('label');label.append(check,el('span',`${source?sourceName(source):'Missing source'} · ${trace.key}`));row.append(label,button('Remove',()=>{panel.traces.splice(index,1);renderPanelContents(id);}));nodes.traceList.append(row);
    });
    safe(()=>draw(id));
  }
  async function draw(id){
    const panel=panels[id],nodes=plotNodes.get(id);if(!nodes)return;
    const drawRevision=(nodes.drawRevision||0)+1;nodes.drawRevision=drawRevision;
    nodes.messages.replaceChildren();nodes.stats.replaceChildren();const traces=[],traceRefs=[],warnings=[],axisUnits=[],timeKinds=new Set();
    for(const trace of panel.traces){
      try{
        let values=series(trace.sourceId,trace.key),name=`${values.name} · ${trace.key}`,delta;
        if(panel.mode==='delta'){
          if(!panel.reference)throw new Error('Choose a reference recording for signed deltas.');
          if(trace.sourceId===panel.reference)continue;
          delta=compareSeries(values,series(panel.reference,trace.key));values={...values,x:delta.x,y:delta.y};name=`${values.name} − ${sources.find(source=>source.id===panel.reference)?.name} · ${trace.key}`;
          if(trace.visible){const stat=el('div',undefined,'comparison-stat');stat.title=name;stat.append(el('span',`max |Δ| ${number(delta.stats.maxAbs)} ${delta.unit} · RMS ${number(delta.stats.rms)} · final Δ ${number(delta.stats.final)} ${delta.unit}`));stat.append(el('small',`t=${number(delta.stats.finalTime)} s · n=${delta.stats.count.toLocaleString()}`));nodes.stats.append(stat);}
        }
        timeKinds.add(values.timeBased?'time':'index');
        // Unknown units each get their own channel axis; two unlabelled physical signals never share one.
        const unitToken=values.known?values.unit:`source units: ${values.model} ${values.key}`;
        if(!axisUnits.includes(unitToken))axisUnits.push(unitToken);
        const axis=axisUnits.indexOf(unitToken);
        traces.push({x:values.x,y:values.y,name,type:'scatter',mode:'lines',connectgaps:false,visible:trace.visible?true:'legendonly',yaxis:axis?'y'+(axis+1):'y',hovertemplate:`%{x:.5g} ${values.timeBased?'s':'sample'}<br>%{y:.6g} ${values.unit}<extra>%{fullData.name}</extra>`});traceRefs.push(trace);
      }catch(cause){warnings.push(`${trace.key}: ${cause.message}`);}
    }
    if(timeKinds.size>1){warnings.push('Time-based recordings and sample-index datasets cannot share an x axis. Use separate plots.');traces.length=0;traceRefs.length=0;}
    if(axisUnits.length>4){warnings.push('Use a split plot for additional units; at most four separate unit axes per plot.');traces.length=0;traceRefs.length=0;}
    for(const warning of [...new Set(warnings)])nodes.messages.append(el('p',warning,'comparison-warning'));
    if(!panel.traces.length)nodes.messages.append(el('p','Select this plot, then click a channel on the right.','muted'));
    if(!globalThis.Plotly){nodes.messages.append(el('p','Plotly is loading.','comparison-warning'));return;}
    const dark=currentTheme==='dark',background=dark?'#202824':'#fffdf5',foreground=dark?'#e6ecdf':'#343e2f',grid=dark?'#3c493f':'#d7d8c6';
    const plotLayout={paper_bgcolor:background,plot_bgcolor:background,font:{color:foreground,size:11},showlegend:panel.legend&&!focusPlots,legend:{orientation:'h',font:{size:10}},margin:{l:55,r:axisUnits.length>1?85:15,t:10,b:45},xaxis:{title:{text:timeKinds.has('index')?'Recorded sample index':'Time (s)'},gridcolor:grid,automargin:true},uirevision:id,hovermode:'x',autosize:true};
    axisUnits.forEach((unit,index)=>{plotLayout[index?'yaxis'+(index+1):'yaxis']={title:{text:`${panel.mode==='delta'?'Δ ':''}${unit}`},gridcolor:grid,automargin:true,...(index?{overlaying:'y',side:'right',anchor:'free',autoshift:true,showgrid:false}:{})};});
    if(!axisUnits.length)plotLayout.yaxis={title:{text:'Select channels'},gridcolor:grid};
    const generation=revision;
    await globalThis.Plotly.react(nodes.chart,traces,plotLayout,{responsive:true,scrollZoom:true,displaylogo:false});
    if(generation!==revision||plotNodes.get(id)!==nodes||nodes.drawRevision!==drawRevision)return;
    nodes.chart.removeAllListeners?.('plotly_legendclick');nodes.chart.removeAllListeners?.('plotly_legenddoubleclick');
    nodes.chart.on?.('plotly_legendclick',event=>{const trace=traceRefs[event.curveNumber];if(trace){trace.visible=!trace.visible;renderPanelContents(id);}return false;});
    nodes.chart.on?.('plotly_legenddoubleclick',()=>false);
  }

  function renderLibrary(){
    listing.replaceChildren();const query=librarySearch.value.toLowerCase();
    for(const summary of summaries.filter(item=>`${item.name} ${item.backend} ${item.kind}`.toLowerCase().includes(query))){
      const label=el('label',undefined,'comparison-library-record'),check=el('input');check.type='checkbox';check.checked=selectedLibrary.has(summary.id);check.addEventListener('change',()=>check.checked?selectedLibrary.add(summary.id):selectedLibrary.delete(summary.id));
      label.append(check,el('span',`${summary.name} · ${summary.backend||'dataset'} · ${summary.kind}${summary.kind==='profile'?' → runs solver':` · ${summary.sample_count||0} samples`}`));listing.append(label);
    }
    if(!listing.childElementCount)listing.append(el('p','No saved studies match. Save a simulation or import JSON.','muted'));
  }
  async function refresh(){summaries=await listRecords();renderLibrary();return summaries;}
  async function loadSelected(){
    if(!selectedLibrary.size)throw new Error('Select one or more saved profiles or recordings.');
    loadButton.disabled=true;
    try{
      // Load individually so a failed solver does not discard already successful sources.
      const failures=[];
      for(const id of [...selectedLibrary]){
        try{let record=await getRecord(id);if(!record)throw new Error('Saved study is unavailable.');
          if(!record.result){if(typeof onRunProfile!=='function')throw new Error('Running profiles is unavailable in this view.');status.textContent=`Running profile: ${record.name}…`;record=await onRunProfile(record);if(!record?.result)throw new Error('Profile solver did not return a saved run.');}
          await addRecords([record]);selectedLibrary.delete(id);
        }catch(cause){failures.push(cause.message);}
      }
      await refresh();if(failures.length)throw new Error(failures.join('\n'));
    }finally{loadButton.disabled=false;}
  }
  function exportWorkspace(){
    const packet={schema:COMPARISON_SCHEMA,created_at:new Date().toISOString(),records,layout,panels,active};
    if(new Blob([JSON.stringify(packet)]).size>MAX_IMPORT_BYTES)throw new Error('Comparison exceeds the portable 80 MiB JSON limit. Export a smaller group of source recordings.');
    downloadJSON(packet,'motion-lab-comparison.json',{compact:true});
  }
  async function importFiles(){
    for(const file of importer.files){
      if(file.size>MAX_IMPORT_BYTES)throw new Error('JSON exceeds the 80 MiB import limit.');
      const value=JSON.parse(await file.text());
      if(value.schema===COMPARISON_SCHEMA){
        const checked=normalizeWorkspace(value),restored=[];
        // Append restored records to library, never overwrite IDs. Workspace IDs remain internal.
        for(const item of checked.records){const saved=await saveRecord(item.record);restored.push({...item,record:{...item.record,id:saved.id,created_at:saved.created_at}});}
        records=restored;layout=checked.layout;panels=checked.panels;active=checked.active;rebuildSources();renderAll();status.textContent=`Restored ${records.length} source recordings and ${leaves(layout).length} plots; copies appended to library.`;
      }else{
        let record=await saveRecord(normalizeImport(value,file.name));
        if(!record.result){if(typeof onRunProfile!=='function')throw new Error(`Imported profile “${record.name}” is saved. Run it through Load profiles.`);status.textContent=`Running imported profile: ${record.name}…`;record=await onRunProfile(record);if(!record?.result)throw new Error('Profile solver did not return a saved run.');}
        await addRecords([record]);
      }
    }
    importer.value='';await refresh();
  }
  importer.addEventListener('change',()=>safe(importFiles));librarySearch.addEventListener('input',renderLibrary);channelSearch.addEventListener('input',renderChannels);
  renderAll();safe(refresh);
  return {refresh:()=>safe(refresh),setTheme(next){currentTheme=next;for(const {id}of leaves(layout))safe(()=>draw(id));},addRecords,resize};
}
