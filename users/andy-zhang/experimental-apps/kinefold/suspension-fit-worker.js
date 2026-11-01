/** Cancellable browser worker for the retained Kinefold/V4 spring fit.
 * Spawn from suspension-fit.js; input {params,locks} in mm/deg/kg/N.
 * Outputs progress, then an immutable proposed fit report or explicit error.
 * No storage/network API writes; terminating this worker cancels computation.
 * Bounded sampled quasi-static optimization, not dynamics or hardware proof.
 */
'use strict';
importScripts('reference-v4.js','model.js','suspension-fit.js');
self.onmessage=event=>{
 try{const result=KinefoldSuspensionFit.solve(event.data.params,event.data.locks,{progress:data=>self.postMessage({type:'progress',...data})});self.postMessage({type:'result',result});}
 catch(error){self.postMessage({type:'error',message:error.message});}
};
