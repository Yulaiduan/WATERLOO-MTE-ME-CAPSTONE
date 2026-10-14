/* Export GIF frames from the actual Motion Lab mechanism renderer.
 * Run: node scripts/export_design_examples.cjs while Motion Lab runs on 4186.
 * Inputs: selected mm/degree evidence, deterministic 48-pose sinusoidal cycle.
 * Outputs: ignored PNGs, ten curated web/design-examples/gifs/*.gif via Pillow.
 * Node22/locked Playwright and optional requirements-animation.txt required.
 * Limits: prescribed kinematic illustrations; no dynamics/contact certification.
 */
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
(async()=>{
 let browser;for(const channel of ['msedge','chrome',undefined])try{browser=await chromium.launch({headless:true,...(channel?{channel}:{})});break;}catch{}
 if(!browser)throw Error('No browser for export');
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1000}});
  await page.goto('http://127.0.0.1:4186/design-examples/');await page.waitForFunction(()=>window.DesignExamples);
  if(await page.locator('#play').textContent()==='Pause')await page.locator('#play').click();
  const designs=await page.evaluate(()=>window.DesignExamples.data.designs.map(d=>({slug:d.slug,id:d.id})));
  const frameRoot=path.join(ROOT,'artifacts/design-gif-frames');fs.mkdirSync(frameRoot,{recursive:true});
  for(const d of designs)for(const mode of ['working','inversion']){
   const folder=path.join(frameRoot,`${d.slug}-${mode}`);fs.mkdirSync(folder,{recursive:true});
   for(let i=0;i<48;i++){
    const fraction=(1-Math.cos(2*Math.PI*i/48))/2;
    const result=await page.evaluate(({slug,mode,fraction})=>window.DesignExamples.drawFrame(slug,mode,fraction),{slug:d.slug,mode,fraction});
    fs.writeFileSync(path.join(folder,`${String(i).padStart(3,'0')}.png`),Buffer.from(result.png.split(',')[1],'base64'));
   }
   console.log(`Rendered ${d.slug} · ${mode}`);
  }
  const python=process.env.MOTION_ANIMATION_PYTHON||path.join(ROOT,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
  const encode=spawnSync(python,['scripts/encode_design_gifs.py','--frames','artifacts/design-gif-frames','--output','web/design-examples/gifs'],{cwd:ROOT,encoding:'utf8'});
  if(encode.status!==0)throw Error(encode.stderr||encode.stdout||'GIF encoder failed');
  console.log(encode.stdout);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
