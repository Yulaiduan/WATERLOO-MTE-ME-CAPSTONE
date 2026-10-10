// Standalone persistence adapter for exported conversation visuals. No host API needed.
(() => {
  if(window.openai)return;
  const key='wheel-leg-lab:'+location.pathname;let saved=null;
  try{saved=JSON.parse(localStorage.getItem(key));}catch{}
  window.openai={widgetState:saved,setWidgetState:async value=>{window.openai.widgetState=value;try{localStorage.setItem(key,JSON.stringify(value));}catch{}}};
})();
