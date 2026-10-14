/** Pose adapter for selected Jonathan-convention design examples.
 * Inputs: explicit config lengths in mm, theta2/alpha/phi0 in degrees.
 * Outputs: world +y right/+z up A/B/C positions, mm/rad Jacobian and display ranges.
 * Used by browser and GIF renderer. Ideal kinematics only; not a physics solver.
 * Loaded by app.js; verify with node --test tests/design-examples.test.js.
 */
const R=Math.PI/180;
export function pose(config,qDeg){
 const {L2:a,L3:b,qab:r,phi0,alpha}=config;
 const q=qDeg*R,t=q-Math.PI,k=r-1,phase=phi0*R,angle=phase-k*t;
 const B=[a*Math.cos(t),a*Math.sin(t)];
 const C=[B[0]-b*Math.cos(angle),B[1]-b*Math.sin(angle)];
 const J=[-a*Math.sin(t)-k*b*Math.sin(angle),a*Math.cos(t)+k*b*Math.cos(angle)];
 const u=alpha*R,rotate=v=>[v[0]*Math.cos(u)+v[1]*Math.sin(u),-v[0]*Math.sin(u)+v[1]*Math.cos(u)];
 return {A:[0,0],B:rotate(B),C:rotate(C),J:rotate(J),theta2:qDeg,
   theta3:phi0-(r-1)*(qDeg-180),hipDistance:Math.hypot(...C)};
}
export function angleRange(design,mode){
 return mode==='inversion'?design.full.angle_bounds_deg:[design.config.te,design.config.tc];
}
export function phaseAngle(design,mode,fraction){
 const [a,b]=angleRange(design,mode);return a+(b-a)*fraction;
}
export function trace(design,mode,count=161){
 return Array.from({length:count},(_,i)=>pose(design.config,phaseAngle(design,mode,i/(count-1))).C);
}
