// Read only the embedded analytical library; do not execute browser UI code.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const folder=path.join(__dirname,'inputs');
const html=fs.readFileSync(path.join(folder,'v4-pulley.html'),'utf8');
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const sp=vm.runInNewContext(scripts.slice(0,3).join('\n')+';VSLSpring;');
const p=JSON.parse(fs.readFileSync(path.join(folder,'v4-textbook-10mm.json'),'utf8')).parameters;
const rows=[];
for(let i=0;i<=650;i++) { const q=100+i/10,z=sp.state(p,q); if(!z.valid)throw Error(z.reason);rows.push({q_deg:q,force:z.force,tauS:z.tauS,energy:z.energy,delta:z.delta}); }
const output=path.join(__dirname,'results/source-reference');fs.mkdirSync(output,{recursive:true});
fs.writeFileSync(path.join(output,'spring-reference.json'),JSON.stringify(rows));
console.log('Exported',rows.length,'pinned embedded-spring reference poses.');
