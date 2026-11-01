/** Load and hash-check the recorded original V4 oracle for developer checks.
 * Invocation: require('./reference-source.cjs').loadReferenceSource().
 * Inputs: reference.json, its exact Git revision, current upstream HTML (LF).
 * Outputs: verified historical source/analytical blocks and provenance hashes.
 * Requires local Git history; missing refs or numerical drift fail explicitly.
 * Later upstream UI changes are allowed only when analytical blocks match.
 * No source execution, hash updates, network access or hardware validation.
 */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const normalize=s=>s.replace(/\r\n/g,'\n');
function blocks(source){
  const scripts=[...source.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
  if(scripts.length<3)throw Error('V4 analytical script blocks are missing.');
  return [...scripts.slice(0,2),scripts[2].split('const VSLDomains=')[0]].join('\n');
}
function loadReferenceSource(){
  const provenance=JSON.parse(fs.readFileSync(path.join(__dirname,'reference.json'),'utf8'));
  let source;
  try{source=normalize(cp.execFileSync('git',['show',`${provenance.revision}:${provenance.source}`],{cwd:__dirname,encoding:'utf8',maxBuffer:1024*1024,stdio:['ignore','pipe','pipe']}));}
  catch(error){throw Error(`Cannot load pinned V4 ${provenance.revision}:${provenance.source}; local Git history is required. ${error.message}`);}
  if(hash(source)!==provenance.source_sha256)throw Error('Pinned original V4 source hash differs.');
  const retained=blocks(source);
  if(hash(retained)!==provenance.retained_blocks_sha256)throw Error('Pinned original V4 analytical blocks hash differs.');
  const current=normalize(fs.readFileSync(path.resolve(__dirname,'../../../..',provenance.source),'utf8'));
  if(hash(blocks(current))!==provenance.retained_blocks_sha256)throw Error('Current upstream V4 analytical blocks differ from the pinned reference.');
  return {source,retained,provenance,sourceSha256:hash(source),currentSourceSha256:hash(current),retainedBlocksSha256:hash(retained)};
}
module.exports={loadReferenceSource};
