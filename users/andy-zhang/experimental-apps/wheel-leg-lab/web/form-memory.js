/** Remember form values only while each input's identity and contract match.
 * Inputs: DOM forms with IDs/data-key, optional browser session storage.
 * Outputs: checked values and disclosure state; files/playback/live commands excluded.
 * Explicit profile loads own their values; this is UI memory, not run provenance.
 */
const eligible=n=>n.matches('input,select')&&(n.id||n.dataset.key)&&!['file','button','submit'].includes(n.type)&&!['time','live-force-N','live-force-kgf'].includes(n.id);
function identity(n){return n.dataset.key?'key:'+n.dataset.key:'id:'+n.id;}
function contract(n){return JSON.stringify([n.tagName,n.type,n.dataset.scale||'',n.closest('label')?.querySelector('em')?.textContent||'',n.min,n.max,n.step,
 n.tagName==='SELECT'?[...n.options].map(o=>o.value):null]);}
export function captureForm(root){
 return {fields:[...root.querySelectorAll('input,select')].filter(eligible).map(n=>({id:identity(n),contract:contract(n),value:n.type==='checkbox'?n.checked:n.value})),
 details:[...root.querySelectorAll('details')].map(n=>({name:n.querySelector('summary')?.textContent,open:n.open}))};
}
export function restoreForm(root,saved,{dispatch=false,fields=true}={}){
 if(!saved)return;
 const prior=new Map((saved.fields||[]).map(v=>[v.id,v]));
 if(fields)for(const n of [...root.querySelectorAll('input,select')].filter(eligible)){
  const v=prior.get(identity(n));if(!v||v.contract!==contract(n))continue;
  if(n.type==='checkbox')n.checked=v.value===true;else n.value=String(v.value);
  if(dispatch){n.dispatchEvent(new Event('input',{bubbles:true}));n.dispatchEvent(new Event('change',{bubbles:true}));}
 }
 for(const n of root.querySelectorAll('details')){const v=saved.details?.find(d=>d.name===n.querySelector('summary')?.textContent);if(v)n.open=v.open;}
}
