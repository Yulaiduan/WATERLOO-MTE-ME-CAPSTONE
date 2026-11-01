/** Collapse selected explanatory UI prose behind native, accessible info controls.
 * Load last in index.html. Inputs existing app DOM; no physical units or model
 * changes. Outputs reversible details/summary wrappers retaining original nodes,
 * IDs and listeners. New/rerendered prose is enhanced with MutationObserver.
 * Status, errors, warnings, numeric readouts, controls and detailed reference
 * sections stay visible. No storage, profile, solver or network operations.
 */
globalThis.KinefoldInfoDisclosure=(()=>{
 'use strict';
 const candidates=[
  '.hint','.chart-foot','.preview-note','.eq-scope','.dyn-floor-note',
  '.workspace-heading>div>p','.solver-heading>div>p','.dyn-output-heading>p',
  '.energy-heading>p','.energy-heading>div>p','.energy-rail>p:not([data-energy-mass-note])',
  '.energy-chart-card>p','.energy-plot-heading>div>p','.energy-input-card>p',
  '.solver-settings details>p','.motor-panel>p','.motor-panel .contact-controls>p',
  '.case-settings>p','[data-target-actions]>p:not([data-case-basis]):not([data-target-energy])',
  '.terrain-profile-panel>p:not([data-terrain-active])','.terrain-controls>div>p',
  '.pw-heading>div>p','.pw-editor>.pw-muted','.auto-heading>div>p','.ac-heading>div>p',
  '[data-info-explanation]'
 ].join(',');
 const reserved=[
  '#conventions','dialog','svg','.js-plotly-plot','label','button','summary',
  '[role="status"]','[role="alert"]','[aria-live]','.notice','.error','.warning',
  '.warnings','.solver-warnings','#messages','[data-info-keep]',
  '[data-energy-handoff]','[data-energy-mass-note]','[data-energy-context-values]',
  '[data-energy-alpha]','[data-energy-announcement]','[data-energy-range-error]',
  '[data-motor-conversion]','[data-case-basis]','[data-target-energy]',
  '[data-terrain-active]','[data-auto-setup-summary]','[data-auto-capture]',
  '[data-auto-summary]','[data-fit-status]','.solver-readouts','.readouts',
  '.energy-summary','.energy-signed-readouts','.fit-peaks','.solver-state',
  '.solver-design','.energy-identity','.pw-component-summary','.pw-candidate-list',
  '[data-snapshot-state]',
  '[data-energy-equations]','.solver-details','.fit-bounds','.fit-values',
  '.contact-model-notes','.model-body','.energy-catalog'
 ].join(',');
 const controls='input,select,textarea,button,details,summary,svg,canvas,.js-plotly-plot,[role="status"],[role="alert"],[aria-live]';
 let serial=0,observer=null,pending=false;
 const roots=new Set();
 function protectedNode(node){return !!node.closest(reserved)||!!node.querySelector(controls);}
 function eligible(node){return !!node?.matches?.(candidates)&&!node.closest('.info-disclosure')&&!protectedNode(node)&&!!node.textContent.trim();}
 function context(node){
  const card=node.closest('.suspension-fit,.group,section,article,.solver-heading,.workspace-heading');
  const heading=card?.querySelector('h2,h3,h4,strong');
  return heading?.textContent.trim().slice(0,100)||'this section';
 }
 function wrap(node){
  if(!eligible(node))return null;
  const doc=node.ownerDocument,details=doc.createElement('details'),summary=doc.createElement('summary'),body=doc.createElement('div');
  details.className='info-disclosure';summary.className='info-summary';body.className='info-body';body.id='kinefold-info-'+(++serial);
  summary.setAttribute('aria-label','Information about '+context(node));summary.setAttribute('aria-controls',body.id);summary.setAttribute('aria-expanded','false');summary.title='More information';
  const icon=doc.createElement('span');icon.className='info-symbol';icon.setAttribute('aria-hidden','true');icon.textContent='i';summary.append(icon);
  details.append(summary,body);node.before(details);
  body.append(node);
  // Adjacent explanatory paragraphs share one icon; active data/actions do not.
  while(eligible(details.nextElementSibling))body.append(details.nextElementSibling);
  details.addEventListener('toggle',()=>summary.setAttribute('aria-expanded',String(details.open)));
  details.addEventListener('keydown',event=>{if(event.key==='Escape'&&details.open){details.open=false;summary.setAttribute('aria-expanded','false');summary.focus();event.stopPropagation();}});
  return details;
 }
 function promoteIfNeeded(details){
  if(!details?.isConnected)return;
  const body=details.querySelector(':scope>.info-body');
  if(!body||![...body.children].some(n=>protectedNode(n)))return;
  // If an existing explanation becomes an error/action, expose it immediately.
  while(body.firstChild)details.before(body.firstChild);
  details.remove();
 }
 function enhance(root=document){
  if(root?.nodeType!==1&&root?.nodeType!==9)return 0;
  if(root.closest?.('svg,.js-plotly-plot'))return 0;
  let count=0;
  if(root.matches?.('.info-disclosure'))promoteIfNeeded(root);
  for(const details of root.querySelectorAll('.info-disclosure'))promoteIfNeeded(details);
  const list=[...(root.matches?.(candidates)?[root]:[]),...root.querySelectorAll(candidates)];
  for(const node of list)if(wrap(node))count++;
  return count;
 }
 function schedule(root){
  if(!root?.isConnected||root.closest?.('svg,.js-plotly-plot'))return;
  const disclosure=root.closest?.('.info-disclosure');
  roots.add(disclosure||root);
  if(pending)return;pending=true;
  queueMicrotask(()=>{pending=false;const work=[...roots];roots.clear();for(const item of work)enhance(item);});
 }
 function start(root=document){
  enhance(root);if(observer||typeof MutationObserver==='undefined')return;
  observer=new MutationObserver(records=>{for(const record of records){if(record.type==='attributes'){schedule(record.target);continue;}const target=record.target.nodeType===1?record.target:record.target.parentElement;schedule(target);}});
  observer.observe(root.nodeType===9?root.body:root,{subtree:true,childList:true,attributes:true,attributeFilter:['class','role','aria-live']});
 }
 function stop(){observer?.disconnect();observer=null;roots.clear();}
 if(typeof document!=='undefined'){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>start(),{once:true});else start();}
 return {enhance,eligible,start,stop};
})();
