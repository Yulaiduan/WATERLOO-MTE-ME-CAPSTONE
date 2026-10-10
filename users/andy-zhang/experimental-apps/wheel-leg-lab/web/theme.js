/* Shared standalone/embedded motion-lab theme and iframe sizing.
 * Read local theme, receive same-origin updates; never uploads data.
 */
(() => {
  function setTheme(theme){
    if(!['light','dark'].includes(theme))return;
    document.documentElement.dataset.theme=theme;
    document.documentElement.style.colorScheme=theme;
    document.dispatchEvent(new CustomEvent('motion-lab-theme',{detail:{theme}}));
  }
  let initial='light';try{initial=localStorage.getItem('motion-lab-theme')||'light';}catch{}
  setTheme(initial);
  window.addEventListener('message',event=>{
    if(event.origin===location.origin&&event.data?.type==='motion-lab-theme')setTheme(event.data.theme);
  });
  window.addEventListener('storage',event=>{if(event.key==='motion-lab-theme')setTheme(event.newValue);});
  if(new URLSearchParams(location.search).has('embedded'))document.documentElement.dataset.embedded='true';
  function boot(){
    let scheduled=0,lastHeight=0;
    const height=()=>{
      cancelAnimationFrame(scheduled);scheduled=requestAnimationFrame(()=>{
        const next=Math.ceil(document.body.scrollHeight+10);
        if(Math.abs(next-lastHeight)>3){lastHeight=next;parent.postMessage({type:'motion-lab-height',height:next},location.origin);}
      });
    };
    if(parent!==window){new ResizeObserver(height).observe(document.body);height();}
    document.querySelectorAll('header a[href="/"]').forEach(a=>a.target='_top');
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
