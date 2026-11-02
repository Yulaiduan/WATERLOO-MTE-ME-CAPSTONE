/** V6 solution workbook writer. JSON input/output paths, artifact-tool runtime.
 * Pure values with units; VSL state is the authoritative reload representation.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(path.join(process.env.VSL_NODE_MODULES||path.resolve(path.dirname(process.execPath),'..','node_modules'),'__vsl__.cjs'));
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const [input,output,preview]=process.argv.slice(2),doc=JSON.parse(await fs.readFile(input,'utf8')),wb=Workbook.create();
function sheet(name,rows){const sh=wb.worksheets.add(name),cols=Math.max(...rows.map(r=>r.length)),end=rows.length;
 const cells=rows.map(r=>Array.from({length:cols},(_,i)=>typeof r[i]==='number'&&!Number.isFinite(r[i])?null:r[i]??null));
 sh.getRangeByIndexes(0,0,end,cols).values=cells;sh.showGridLines=false;sh.freezePanes.freezeRows(1);
 const all=sh.getRangeByIndexes(0,0,end,cols);all.format.font={name:'Arial',size:10};all.format.columnWidth=18;all.format.rowHeight=23;
 const head=sh.getRangeByIndexes(0,0,1,cols);head.format.fill='#154653';head.format.font={bold:true,color:'#FFFFFF'};head.format.rowHeight=38;head.format.wrapText=true;
 if(end>1){sh.getRangeByIndexes(1,0,end-1,cols).setNumberFormat('0.000');for(let r=1;r<end;r+=2)sh.getRangeByIndexes(r,0,1,cols).format.fill='#F0F6F7';}
 sh.getRangeByIndexes(0,0,end,1).format.columnWidth=14;return sh;
}
if(doc.schema==='vsl-config-library/v1'){
 const cols=JSON.parse(await fs.readFile(new URL('./config-library-columns.json',import.meta.url),'utf8'));
 const get=(o,s)=>s.split('.').reduce((v,k)=>v?.[k],o);
 const cell=(r,c)=>{const s=r.snapshot,p=s?.parameters;if(c.path)return get(s,c.path)??null;if(c.key==='totalMass')return p?4*(p.m1+p.m2+p.m3+p.m5+p.m6):null;if(['qab','qdc','qfe'].includes(c.key)){const [a,b]={qab:['ra','rb'],qdc:['rd','rc'],qfe:['rf','re']}[c.key];return p?p[a]/p[b]:null;}if(['save','load'].includes(c.key))return 'Use VSL';return r[c.key]??null;};
 const designs=sheet('Designs',[cols.map(c=>c.label),...doc.rows.map(r=>cols.map(c=>cell(r,c)))]);
 if(doc.rows.length){designs.getRange('A2:A'+(doc.rows.length+1)).setNumberFormat('0');designs.getRange('E2:E'+(doc.rows.length+1)).setNumberFormat('yyyy-mm-dd hh:mm:ss');}designs.getRange('B:B').format.columnWidth=34;designs.getRange('E:E').format.columnWidth=25;
 sheet('VSL state',[['Key','Value'],['schema',doc.schema],['loadedDp',doc.loadedDp],...doc.rows.map(r=>['DP:'+r.dp,JSON.stringify(r)])]);
}else{
 const summary=sheet('Solutions',[
 ['Solve #','Favorite','Saved UTC','Type','Slots used','Cases','Robot mT (kg)','Payloads (kg)','r_h (mm)','r_s (mm)','nu (deg)','S_v (mm)','S_u (mm)','Bulk preload (mm)','Peak |tau2| (Nm)','Piston stroke (mm)'],
 ...doc.solutions.map(s=>[s.id,s.favorite,s.savedAt,s.settings.type,s.springs.length,s.payloads.length,4*['m1','m2','m3','m5','m6'].reduce((a,k)=>a+s.parameters[k],0),s.payloads.join(', '),s.geometry.hornR,s.geometry.rs,s.geometry.nu,s.geometry.Sv,s.geometry.Su,s.bulk,s.metrics.worstNm,s.metrics.stroke])]);
 if(doc.solutions.length){summary.getRange('C2:C'+(doc.solutions.length+1)).setNumberFormat('yyyy-mm-dd hh:mm:ss');summary.getRange('E2:F'+(doc.solutions.length+1)).setNumberFormat('0');}summary.getRange('C:C').format.columnWidth=25;
 sheet('Springs',[
 ['Solve #','Slot','C/E','Catalogue ID','Part','Website','Max energy (J)','k (N/mm)','Rated travel (mm)','Fmax (N)','Rated Lmin (mm)','Free L (mm)','p0 (N)','Physical l0 (mm)','pe (N)','Physical le (mm)','Individual preload (mm)','Remaining travel (mm)','Enabled cases'],
 ...doc.solutions.flatMap(s=>s.springs.map((p,i)=>[s.id,i+1,p.type,p.id,p.part,p.url,p.energy,p.k,p.travel,p.fmax,p.lmin,p.free,p.p0,p.l0,p.pe,p.le,p.individualMm,p.marginMm,s.masks.map((row,j)=>row[i]?j+1:null).filter(x=>x!==null).join(', ')]))]);
 sheet('Payloads',[
 ['Solve #','Case','Payload (kg)','Per-leg mL (kg)','Enabled slot numbers','Total p0 (N)','Total pe (N)','Largest +tau2 (Nm)','Largest -tau2 (Nm)','Peak |tau2| (Nm)','RMS tau2 (Nm)'],
 ...doc.solutions.flatMap(s=>s.cases.map((c,j)=>[s.id,j+1,c.payload,c.mL,s.masks[j].map((x,i)=>x?i+1:null).filter(x=>x!==null).join(', '),c.p0,c.pe,c.positive,c.negative,c.maxAbs,c.rms]))]);
 sheet('Readme',[['Item','Meaning'],['Mass','mT is full robot mass; mL=(mT+payload)/4.'],['Switching','Only enabled spring subsets change between payload cases.'],['Preload','Bulk is fixed displacement in mm plus fixed individual displacement adjustments.'],['Length','Spring l0/le are physical spring lengths. System l0 is virtual S-H span.'],['Limits','All rated force, travel, length, energy limits are enforced using the conservative intersection.'],['Optimization','Bounded numerical search, not proof of global optimality. Torque extrema are densely sampled.'],['Reload','VSL state stores full records. Edit designs inside Spring lab; summary cells are reports.'],['Reference','p0 and l0 at theta2=90 degrees; pe and le at theta2e.'],['Source',doc.cataloguePath||'User compiled McMaster catalogue'],['Catalogue SHA256',doc.catalogueHash||''],['Next ID',doc.nextId]]);
 sheet('VSL state',[['Key','Value'],['schema','vsl-spring-solutions/v1'],['nextId',doc.nextId],['catalogueHash',doc.catalogueHash||''],...doc.solutions.map(s=>[s.id,JSON.stringify(s)])]);
}
wb.recalculate();
if(preview){console.log(JSON.stringify(await wb.inspect({kind:'table',range:(doc.schema==='vsl-config-library/v1'?'Designs':'Solutions')+'!A1:H6',maxChars:1500,tableMaxRows:6,tableMaxCols:8})));const img=await wb.render({sheetName:doc.schema==='vsl-config-library/v1'?'Designs':'Solutions',range:'A1:H6',scale:1,format:'png'});await fs.writeFile(preview,new Uint8Array(await img.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
