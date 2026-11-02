/** V5 linear plot bounds/ticks. Browser or Node: VSLPlot.bounds(values, includeZero).
 * Inputs/outputs share each signal's units. Keeps zero at a one-sided boundary;
 * references() adds exact, labelled zero/1g ticks without near-duplicate labels.
 */
const VSLPlot=(()=>{
 function bounds(values,includeZero=false,references=[]){
  const finite=values.filter(Number.isFinite);let min=finite.length?Math.min(...finite):0,max=finite.length?Math.max(...finite):1;
  for(const ref of references.filter(Number.isFinite)){min=Math.min(min,ref);max=Math.max(max,ref);}
  if(includeZero){min=Math.min(0,min);max=Math.max(0,max);}
  const scale=Math.max(Math.abs(min),Math.abs(max),1e-6),pad=max>min?(max-min)*.08:scale*.01;
  if(min===max&&min===0)return {min:0,max:1};
  return {min:min>=0?Math.max(0,min-pad):min-pad,max:max<=0?Math.min(0,max+pad):max+pad};
 }
 function ticks(min,max,refs=[0]){
  const span=max-min,important=[...new Set(refs)].filter(v=>v>=min-1e-12&&v<=max+1e-12);
  const regular=Array.from({length:5},(_,i)=>min+span*i/4).filter(v=>!important.some(r=>Math.abs(v-r)<span*.045));
  return [...regular,...important].sort((a,b)=>a-b);
 }
 return {bounds,ticks};
})();
if(typeof module!=='undefined')module.exports=VSLPlot;
