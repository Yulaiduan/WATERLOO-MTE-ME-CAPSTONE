/** Ideal VSL coupling model. Browser: load before app.js; Node: require this file.
 * Inputs: positive dimensionless qdc/qfe, fixed qab=2, motor torques in Nm.
 * Outputs: c1/c2, signed coupling k, requested-coordinate envelope vertices.
 * Limitations: fixed chassis pitch, ideal belts, no contact or dynamic model.
 */
(function(root){
  'use strict';
  function coefficients(qdc,qfe){
    if(!Number.isFinite(qdc)||!Number.isFinite(qfe)||qdc<=0||qfe<=0)throw new RangeError('Ratios must be finite and positive.');
    const c1=-1+(2-1/qdc)/qfe;
    const c2=1/(qdc*qfe);
    const c3=qdc*(qfe-2)+1;
    return {c1,c2,c3,k:c3};
  }
  function envelope(qdc,qfe){
    const {c2,k}=coefficients(qdc,qfe);
    return [[-130,-23.6],[-130,23.6],[130,23.6],[130,-23.6]].map(([hip,drive])=>({x:drive/c2,y:hip+k*drive}));
  }
  const api={coefficients,envelope};
  if(typeof module!=='undefined')module.exports=api;
  root.CouplingModel=api;
})(globalThis);
