/** Verify Jonathan source preservation and library compatibility; run npm test.
 * Inputs: built/source HTML and parameter JSON, mm/deg/kg/N/Nm.
 * Outputs: Node assertions. Limits: not browser, dynamic or hardware validation.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {normalizeImport} from '../web/library.js';
import {modelFamily,recordSources,seriesFor,compareSeries} from '../web/comparison-data.js';

const source=fs.readFileSync(new URL('../../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html',import.meta.url),'utf8');
const built=fs.readFileSync(new URL('../web/jon-linkage/index.html',import.meta.url),'utf8');
const scripts=html=>Object.fromEntries([...html.matchAll(/<script id="([^"]+)">([\s\S]*?)<\/script>/g)].map(m=>[m[1],m[2]]));
const context=vm.createContext({});for(const code of Object.values(scripts(source)))vm.runInContext(code,context);
const defaults=JSON.parse(vm.runInContext('JSON.stringify(VSLStatic.defaults)',context));
const config={schema:'general-vsl/v2-quasi-static',parameters:{...defaults,L2:250,L3:310,alpha:15,beta:30,Fn:120,Ft:-20,m2:.5,m3:.3,m5:.1,m6:1,Tab0:10,Tcd0:20,Tef0:30},theta2:126,driven:{q23:'q23',qab:'rb',qcd:'rd',qef:'rf'},ranges:{beta:{min:20,max:60}},absoluteTorques:true,view:{showTau4:false}};

test('all three original model scripts are byte-identical and provenance matches',()=>{
 const original=scripts(source),output=scripts(built),manifest=JSON.parse(fs.readFileSync(new URL('../web/jon-linkage/source.json',import.meta.url),'utf8'));
 for(const id of ['solver-model','statics-model','global-maxima-model']){
  assert.equal(output[id],original[id]);assert.equal(manifest.models[id],crypto.createHash('sha256').update(original[id]).digest('hex'));
 }
 assert.equal(manifest.source_sha256,crypto.createHash('sha256').update(source).digest('hex'));
 assert.match(built,/window\.JonLinkage=/);
});
test('original v1/v2 JSON and full linkage library profiles retain source units/state',()=>{
 const profile=normalizeImport(config,'Jonathan loading');assert.equal(profile.backend,'jon_v2');assert.deepEqual(profile.config,config);
 const v1={...config,schema:'general-vsl/v1-kinematics'};assert.deepEqual(normalizeImport(v1).config,v1);
 const envelope=normalizeImport({kind:'profile',backend:'jon_v2',config});assert.deepEqual(envelope.config,config);
 assert.equal(envelope.config.parameters.L3,310);assert.equal(envelope.config.parameters.Tab0,10);
});
test('malformed linkage loads/geometry are rejected without reinterpreting as SI wheel config',()=>{
 for(const [key,value] of [['L2',0],['m2',-1],['Ft','20'],['r5I',0],['loadMode','typo'],['beta',91],['alpha',46]])
  assert.throws(()=>normalizeImport({...config,parameters:{...config.parameters,[key]:value}}));
 assert.throws(()=>normalizeImport({...config,parameters:{...config.parameters,te:170,tc:100}}));
 assert.throws(()=>normalizeImport({...config,theta2:'126'}));
});
test('four sweep tables and undefined travel angles remain explicit non-time datasets',()=>{
 const result={config,rows:['t2','dz','beta','alpha'].map(mode=>({mode,x:1,x_unit:mode==='dz'?'mm':'deg',tau2_Nm:-2,gamma_uv_deg:null})),units:{tau2_Nm:'Nm'},scope:'Analytical sweeps; no timestamps.'};
 const record=normalizeImport({backend:'jon_v2',kind:'run',config,result});
 assert.equal(record.kind,'run');assert.equal(record.result.rows[1].x_unit,'mm');assert.equal(record.result.rows[0].gamma_uv_deg,null);
 assert.equal('t' in record.result.rows[0],false);
 assert.equal(modelFamily(record),'Jonathan v2 quasi-static linkage');
 const series=seriesFor(recordSources(record,'jon')[0],'tau2_Nm');assert.equal(series.unit,'Nm');assert.equal(series.timeBased,false);
 assert.throws(()=>compareSeries(series,series),/recorded t\/time/);
});
