/** Recorded-length adapter checks. Run npm test; SI inputs, no solver integration. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {transmissionState} from '../web/spring-transmission.js';
import {drawCylinder} from '../web/spring-transmission.js';
function svgNode(){return {children:[],attrs:{},attr(k,v){if(arguments.length===1)return this.attrs[k];this.attrs[k]=v;return this;},append(tag){const n=svgNode();n.tag=tag;this.children.push(n);return n;},text(t){this.label=t;return this;}};}
test('inline has no housing; rope attaches to a moving rigid rod eye outside the cylinder',()=>{
 const state={coil:.18,free:.2,travel:.02,strain:-.02};
 for(const transmission of ['direct','pullrod','ideal_rope']){
  const g=svgNode(),a=drawCylinder(g,{...state,transmission});
  assert.equal(g.children.filter(n=>n.attrs.class==='cylinder-housing').length,transmission==='direct'?0:1);
  assert.equal(g.children.filter(n=>n.attrs.class==='pull-cable').length,transmission==='ideal_rope'?1:0);
  if(transmission==='ideal_rope'){
   const cable=g.children.find(n=>n.attrs.class==='pull-cable'),rod=g.children.find(n=>n.attrs.class==='piston-rod');
   assert.equal(cable.attrs['data-attachment-x'],rod.attrs.x2);assert.equal(cable.attrs['data-attachment-y'],rod.attrs.y2);assert.ok(a.eye>a.seat);
  }
 }
});
test('pulling moves cap and rod end equally, preserving rigid rod length and shortening the coil',()=>{
 const a=drawCylinder(svgNode(),{transmission:'pullrod',coil:.2,free:.2,travel:0}),b=drawCylinder(svgNode(),{transmission:'pullrod',coil:.18,free:.2,travel:.02});
 assert.ok(b.cap>a.cap);assert.equal(a.eye-a.cap,b.eye-b.cap);assert.ok(Math.abs(b.cap-a.cap-.02*a.px)<1e-10);
});
test('uses actual recorded coil geometry and signed payout rather than inferred angle',()=>{
 const c={spring_transmission:'pullrod',rest_length:.23,spring_mode:'compression'};
 const s=transmissionState(c,{spring_geometry:{input_length:.24},spring_coil_length:.16},{spring_coil_length:.15},{spring_geometry:{input_length:.2}});
 assert.equal(s.coil,.16);assert.ok(Math.abs(s.travel-.04)<1e-12);assert.ok(Math.abs(s.strain+.07)<1e-12);
});
test('preserves disengaged finite coil and compensation identity',()=>{
 const s=transmissionState({spring_transmission:'ideal_rope',rest_length:.25,spring_force_law:'zero_effective'},
  {spring_geometry:{input_length:.1},spring_coil_length:.25,spring_slack:true});
 assert.equal(s.slack,true);assert.equal(s.strain,0);assert.equal(s.compensated,true);assert.equal(s.transmission,'ideal_rope');
});
