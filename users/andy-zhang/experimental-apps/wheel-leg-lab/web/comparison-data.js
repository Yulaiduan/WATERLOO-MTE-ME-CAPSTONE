/** Pure comparison model. Import in the browser or run tests/comparison.test.js with Node.
 * Inputs: library records with source-unit numeric rows; outputs: time series, signed deltas,
 * sample RMS/max/final statistics and portable split layouts. No solver or storage writes.
 * Limits: linear interpolation over recorded overlap only, no interpolation through missing
 * values; deltas require matching known units, channel names and mechanism families.
 */
import {extractTables, numericRow, normalizeImport} from './library.js';

export const COMPARISON_SCHEMA = 'motion-lab-comparison/v1';
export const MAX_PANELS = 8;
export const MAX_TRACES = 32;
const finite = value => typeof value === 'number' && Number.isFinite(value);
const METRES = ['height','chassis_displacement','position_actual','position_command','position_error','spring_length','spring_coil_length','pin_error','tip_x','tip_y','span_m','coil_length_m','spring_extension_m'];
const FORCES = ['driver_force','driver_check','j1_fx','j1_fy','j1_force','j2_fx','j2_fy','j2_force','j3_fx','j3_fy','j3_force','spring_tension','spring_elastic_tension','spring_damper_tension','spring_coil_load','hip_mount_fx','hip_mount_fy','joint_fx','joint_fy','reaction_check','equivalent_vertical_support','aux_spring_tension'];
const MOMENTS = ['actuator_torque','actuator_command','guide_link_torque','spring_knee_moment','wheel_external_moment','wheel_drive_reaction','wheel_drive_check','guide_hip_reaction','stop_knee_torque','angular_check'];
const RATES = ['knee_speed','upper_speed','lower_speed','wheel_speed'];
const ACCELS = ['knee_accel','upper_accel','lower_accel','wheel_accel'];

export function modelFamily(record) {
  const backend = record.backend || record.result?.backend || '';
  if (backend.startsWith('counterbalance_') || record.config?.anchor_height !== undefined) return 'constant-lift lever';
  if (['math','pymunk','matlab-ode45'].includes(backend) || record.config?.radius !== undefined) return 'wheel leg';
  if (backend === 'linkage') return 'archived linkage';
  return `source dataset: ${record.result?.model || record.result?.study_settings?.id || 'unclassified'}`;
}

export function channelUnit(record, key) {
  const explicit = record.result?.units?.[key];
  if (typeof explicit === 'string' && explicit.trim()) return {unit:explicit,known:true};
  if (key === 't' || key === 'time') return {unit:'s',known:true};
  const family = modelFamily(record);
  if (!['wheel leg','constant-lift lever'].includes(family)) return {unit:'source units',known:false};
  let unit;
  if (/_mm$/.test(key)) unit='mm';
  else if (/_deg$/.test(key)) unit='deg';
  else if (key==='phase_error') unit='rad';
  else if (/_kgf$/.test(key)) unit='kgf';
  else if (/_rad_s2$/.test(key)) unit='rad/s²';
  else if (/_rad_s$/.test(key)) unit='rad/s';
  else if (/_Nm$/.test(key) || MOMENTS.includes(key)) unit='N·m';
  else if (/_N$/.test(key) || FORCES.includes(key)) unit='N';
  else if (/_J$/.test(key)) unit='J';
  else if (/_W$/.test(key)) unit='W';
  else if (/_m$/.test(key) || METRES.includes(key)) unit='m';
  else if (/^(hub|chassis|com)_v[xy]$/.test(key) || key==='tip_velocity_y' || key==='guide_belt_speed_relative') unit='m/s';
  else if (/^(hub|chassis|com)_a[xy]$/.test(key) || key==='tip_acceleration_y') unit='m/s²';
  else if (RATES.includes(key)) unit='rad/s';
  else if (ACCELS.includes(key)) unit='rad/s²';
  else if (/(_engaged|_slack)$/.test(key)) unit='0/1';
  else if (key==='input') unit=record.config?.target==='position'?'m':record.config?.target==='knee'?'N·m':record.config?.target==='force'?'N':undefined;
  return {unit:unit||'source units',known:!!unit};
}

/** Sources include all tables; the original record is held unchanged for export/provenance. */
export function recordSources(record, recordId) {
  if (!record.result) return [];
  return extractTables(record.result).map((table,index) => {
    const keys = [...new Set(table.rows.flatMap(row => Object.keys(numericRow(row))))].filter(key=>!['t','time'].includes(key)).sort();
    const timeKey = table.rows.some(row=>'t' in row)?'t':table.rows.some(row=>'time' in row)?'time':null;
    return {id:`${recordId}:${index}`,recordId,record,name:record.name,table:table.name,rows:table.rows,timeKey,model:modelFamily(record),channels:keys.map(key=>({key,...channelUnit(record,key)}))};
  });
}

function valueAt(row, key) {
  if (Object.hasOwn(row, key)) return row[key];
  return key.split('.').reduce((value, part)=>value?.[part],row);
}

export function seriesFor(source, key) {
  const descriptor=source.channels.find(channel=>channel.key===key);
  if (!descriptor) throw new Error(`Channel ${key} is not recorded in ${source.name}.`);
  const x=source.rows.map((row,index)=>source.timeKey?row[source.timeKey]:index);
  if (x.some(value=>!finite(value))) throw new Error(`${source.name}: sample times must be finite numbers.`);
  if (x.some((value,index)=>index&&value<=x[index-1])) throw new Error(`${source.name}: sample times must be strictly increasing; no duplicates or sorting are assumed.`);
  const y=source.rows.map(row=>{const value=valueAt(row,key);return finite(value)?value:null;});
  return {...descriptor,sourceId:source.id,model:source.model,name:source.name,table:source.table,x,y,timeBased:!!source.timeKey};
}

/** Binary-search interpolation uses adjacent recorded points, never bridging a missing value. */
export function interpolate(series, time) {
  const {x,y}=series;
  if (!x.length || time<x[0] || time>x.at(-1)) return null;
  let lo=0,hi=x.length-1;
  while(lo<=hi){const mid=(lo+hi)>>1;if(x[mid]===time)return finite(y[mid])?y[mid]:null;if(x[mid]<time)lo=mid+1;else hi=mid-1;}
  if(hi<0||lo>=x.length||!finite(y[hi])||!finite(y[lo]))return null;
  return y[hi]+(y[lo]-y[hi])*(time-x[hi])/(x[lo]-x[hi]);
}

export function compareSeries(candidate, reference) {
  if (!candidate.timeBased || !reference.timeBased) throw new Error('Delta needs recorded t/time in seconds; sample indices are not interchangeable with time.');
  if (candidate.model!==reference.model) throw new Error('Delta requires the same mechanism family; wheel-leg and lever channels describe different models.');
  if (candidate.key!==reference.key) throw new Error('Delta requires the same channel name.');
  if (!candidate.known || !reference.known || candidate.unit!==reference.unit) throw new Error('Delta requires matching documented units. Unknown source units cannot establish physical equivalence.');
  const start=Math.max(candidate.x[0],reference.x[0]),end=Math.min(candidate.x.at(-1),reference.x.at(-1));
  if (!finite(start)||!finite(end)||start>end) throw new Error('These recordings have no time overlap.');
  const x=[...new Set([...candidate.x,...reference.x].filter(t=>t>=start&&t<=end))].sort((a,b)=>a-b);
  const y=x.map(t=>{const a=interpolate(candidate,t),b=interpolate(reference,t);return a===null||b===null?null:a-b;});
  const pairs=y.flatMap((value,index)=>finite(value)?[{value,t:x[index]}]:[]);
  if (!pairs.length) throw new Error('No valid matching samples remain in the overlapping interval. Missing values are not bridged.');
  return {x,y,unit:candidate.unit,stats:{maxAbs:pairs.reduce((maximum,p)=>Math.max(maximum,Math.abs(p.value)),0),rms:Math.sqrt(pairs.reduce((sum,p)=>sum+p.value*p.value,0)/pairs.length),final:pairs.at(-1).value,finalTime:pairs.at(-1).t,count:pairs.length,start,end},convention:'candidate minus reference',sampling:'union of recorded timestamps over overlap; linear interpolation; sample RMS'};
}

export function leaves(layout) {return layout.kind==='panel'?[layout]:[...leaves(layout.first),...leaves(layout.second)];}
export function splitPanel(layout,id,direction,newId) {
  if (!['horizontal','vertical'].includes(direction)) throw new Error('Split direction must be horizontal or vertical.');
  if (leaves(layout).length>=MAX_PANELS) throw new Error(`At most ${MAX_PANELS} plots can be displayed.`);
  if (leaves(layout).some(panel=>panel.id===newId)) throw new Error('Plot IDs must be unique.');
  if (!leaves(layout).some(panel=>panel.id===id)) throw new Error('Select a plot to split.');
  const replace=node=>node.kind==='panel'?(node.id===id?{kind:'split',direction,first:node,second:{kind:'panel',id:newId}}:node):{...node,first:replace(node.first),second:replace(node.second)};
  return replace(layout);
}
export function removePanel(layout,id) {
  if (layout.kind==='panel') return layout.id===id?null:layout;
  const first=removePanel(layout.first,id),second=removePanel(layout.second,id);
  return !first?second:!second?first:{...layout,first,second};
}

/** Validate portable workspaces before restoring layout; records still use normal import checks. */
export function normalizeWorkspace(input) {
  if(input?.schema!==COMPARISON_SCHEMA)throw new Error('Unsupported comparison workspace schema.');
  if(!Array.isArray(input.records)||input.records.length>64)throw new Error('Workspace needs at most 64 source records.');
  const recordIds=new Set();
  const records=input.records.map(item=>{
    if(typeof item.id!=='string'||!item.id||recordIds.has(item.id))throw new Error('Source record IDs must be unique strings.');
    recordIds.add(item.id);const checked=normalizeImport(item.record,item.record?.name);return {id:item.id,record:JSON.parse(JSON.stringify({...item.record,...checked}))};
  });
  let count=0;const panelIds=new Set();
  function layout(node,depth=0){
    if(depth>MAX_PANELS||!node||typeof node!=='object')throw new Error('Invalid plot layout.');
    if(node.kind==='panel'){
      if(typeof node.id!=='string'||!node.id||panelIds.has(node.id)||++count>MAX_PANELS)throw new Error('Plot IDs must be unique; at most eight plots.');
      panelIds.add(node.id);return {kind:'panel',id:node.id};
    }
    if(node.kind!=='split'||!['horizontal','vertical'].includes(node.direction))throw new Error('Invalid split layout.');
    return {kind:'split',direction:node.direction,first:layout(node.first,depth+1),second:layout(node.second,depth+1)};
  }
  const checkedLayout=layout(input.layout);
  const allSources=records.flatMap(item=>recordSources(item.record,item.id));
  const sourceIds=new Set(allSources.map(source=>source.id));
  const panels={};
  for(const id of panelIds){
    const panel=input.panels?.[id];
    if(!panel||!['overlay','delta'].includes(panel.mode)||typeof panel.legend!=='boolean'||!Array.isArray(panel.traces)||panel.traces.length>MAX_TRACES)throw new Error('Invalid plot settings.');
    if(panel.reference!==null&&!sourceIds.has(panel.reference))throw new Error('Reference source is missing.');
    const seen=new Set();
    const traces=panel.traces.map(trace=>{
      if(!sourceIds.has(trace.sourceId)||typeof trace.key!=='string'||typeof trace.visible!=='boolean')throw new Error('Plot channel source is missing or invalid.');
      const token=`${trace.sourceId}|${trace.key}`;if(seen.has(token))throw new Error('Duplicate plot channel.');seen.add(token);
      const source=allSources.find(s=>s.id===trace.sourceId);
      if(!source.channels.some(channel=>channel.key===trace.key))throw new Error('Plot channel is not recorded.');
      return {sourceId:trace.sourceId,key:trace.key,visible:trace.visible};
    });
    panels[id]={mode:panel.mode,legend:panel.legend,reference:panel.reference,traces};
  }
  return {schema:COMPARISON_SCHEMA,records,layout:checkedLayout,panels,active:panelIds.has(input.active)?input.active:[...panelIds][0]};
}
