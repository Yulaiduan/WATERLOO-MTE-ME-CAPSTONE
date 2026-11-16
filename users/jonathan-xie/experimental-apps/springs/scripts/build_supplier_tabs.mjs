/** Author supplier additions with artifact-tool, preserving the base in a later package merge.
 * Run: node build_supplier_tabs.mjs ROOT WORKDIR (runtime package junction in WORKDIR).
 * Inputs: data/additional-springs.json, original catalogue snapshot; mm,N,N/mm,J.
 * Outputs: supplier-tabs.xlsx, previews, validation JSON. Does not overwrite catalogue.
 * Limits: nominal supplier ratings; no solver fit or native Excel UI validation.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const [root,work]=process.argv.slice(2),data=JSON.parse(await fs.readFile(path.join(root,'data/additional-springs.json'),'utf8'));
const col=i=>{let s='';for(let n=i+1;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
if(!(await fs.stat(path.join(work,'original-preview.png')).catch(()=>null))){
const original=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(work,'original.xlsx')));
console.log((await original.inspect({kind:'region',sheetId:'MC',range:'A1:L4',maxChars:1800,tableMaxRows:4,tableMaxCols:12})).ndjson);
const oldImage=await original.render({sheetName:'MC',range:'A1:I5',scale:1.2,format:'png'});await fs.writeFile(path.join(work,'original-preview.png'),new Uint8Array(await oldImage.arrayBuffer()));
}
const wb=Workbook.create();
const spec=[['catalogue_id','Catalogue ID'],['part_number','Supplier part number'],['part_url','Supplier part / catalogue link'],['energy_J','E_T (J)'],['k_N_per_mm','k (N/mm)'],['travel_mm','Δl usable / rated (mm)'],['f_max_N','F_max rated (N)'],['l_min_mm','l_min rated (mm)'],['l_max_mm','l_max rated (mm)'],['free_length_mm','Free length (mm)'],['initial_tension_N','Initial tension / F_min (N)'],['od_mm','OD nominal (mm)'],['id_mm','ID nominal (mm)'],['spring_type','Spring type'],['supplier','Supplier / manufacturer'],['family','Family'],['long_life_travel_mm','Long-life travel (mm)'],['long_life_force_N','Long-life force (N)'],['long_life_energy_J','Long-life energy (J)'],['force_at_usable_N','Nominal force at usable limit (N)'],['usable_deflection_mm','Conservative usable deflection (mm)'],['stroke_to_60J_mm','Deflection to store 60 J (mm)'],['installation_hole_mm','Installation hole diameter (mm)'],['guide_rod_mm','Guide rod diameter (mm)'],['wire_width_mm','Wire width (mm)'],['wire_thickness_mm','Wire thickness (mm)'],['max_physical_stroke_mm','Supplier max stroke (mm)'],['price','Supplier price'],['currency','Price currency'],['package_qty','Package quantity'],['unit_price','Unit price'],['wind_direction','Wind direction'],['material','Material'],['end_type','End type'],['specs_met','Specs met'],['rate_tolerance_pct','Rate tolerance ± (%)'],['temperature_min_C','Temperature min (°C)'],['temperature_max_C','Temperature max (°C)'],['rated_cycle_basis','Supplier cycle basis'],['rating_basis','Force / travel rating basis'],['length_basis','Length basis'],['diameter_basis','Diameter basis'],['selection_status','Screening status'],['notes','Rating / design notes'],['source_catalogue_url','Technical catalogue URL'],['drawing_url','Drawing URL'],['retrieved_date','Retrieved date'],['source_attributes','Original supplier values']].map(([key,label])=>({key,label}));
const imp=[['k_N_per_mm','k (lbf/in)',25.4/4.4482216152605],['travel_mm','Δl usable / rated (in)',1/25.4],['f_max_N','F_max rated (lbf)',1/4.4482216152605],['l_min_mm','l_min rated (in)',1/25.4],['l_max_mm','l_max rated (in)',1/25.4],['free_length_mm','Free length (in)',1/25.4],['initial_tension_N','Initial tension / F_min (lbf)',1/4.4482216152605],['od_mm','OD nominal (in)',1/25.4],['id_mm','ID nominal (in)',1/25.4],['long_life_travel_mm','Long-life travel (in)',1/25.4],['long_life_force_N','Long-life force (lbf)',1/4.4482216152605],['installation_hole_mm','Installation hole diameter (in)',1/25.4],['guide_rod_mm','Guide rod diameter (in)',1/25.4],['wire_width_mm','Wire width (in)',1/25.4],['wire_thickness_mm','Wire thickness (in)',1/25.4],['max_physical_stroke_mm','Supplier max stroke (in)',1/25.4]].map(([source,label,factor])=>({key:'imp_'+source,label,source,factor}));
const columns=[...spec,...imp],index=Object.fromEntries(columns.map((d,i)=>[d.key,i]));
const checks={date:'2026-11-11',rows:{},energyComparisons:0,recalculation:{},sourceWorkbookDataPreservation:'Verified in package-merge step'};
for(const type of ['ST','BT','MI','SW']){
 const rows=data.rows.filter(r=>r.source===type),s=wb.worksheets.add(type),n=rows.length+1;
 const matrix=[columns.map(d=>d.label),...rows.map(r=>columns.map(d=>d.key.startsWith('imp_')?null:d.key==='part_url'?(type==='BT'?'Open supplier part':'Open supplier catalogue'):d.key==='source_attributes'?JSON.stringify(r.source_attributes):r[d.key]??null))];
 s.getRangeByIndexes(0,0,n,columns.length).values=matrix;
 for(let i=0;i<rows.length;i++){
  const rr=i+2,r=rows[i];
  s.getRange(`D${rr}`).formulas=[[`=E${rr}*MIN(F${rr},G${rr}/E${rr})^2/2000`]];
  s.getRange(`T${rr}:V${rr}`).formulas=[[`=E${rr}*MIN(F${rr},G${rr}/E${rr})`,`=MIN(F${rr},G${rr}/E${rr})`,`=SQRT(120000/E${rr})`]];
  if(r.long_life_travel_mm!=null)s.getRange(`S${rr}`).formulas=[[`=E${rr}*MIN(Q${rr},R${rr}/E${rr})^2/2000`]];
  if(r.price!=null&&r.package_qty)s.getRange(`AE${rr}`).formulas=[[`=AB${rr}/AD${rr}`]];
  for(const d of imp)if(r[d.source]!=null)s.getRange(`${col(index[d.key])}${rr}`).formulas=[[`=${col(index[d.source])}${rr}*${d.factor}`]];
 }
 const all=s.getRangeByIndexes(0,0,n,columns.length);all.format.font={name:'Arial',size:10,color:'#223044'};all.format.rowHeight=22;all.format.columnWidth=20;all.format.verticalAlignment='center';
 s.getRangeByIndexes(0,0,1,columns.length).format={fill:'#18374E',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:54,horizontalAlignment:'center'};
 for(const c of ['A','B','C'])s.getRange(`${c}:${c}`).format.columnWidth=c==='A'?16:c==='B'?25:38;
 s.getRange(`C2:C${n}`).format.font={color:'#1766A4'};
 s.getRange(`D2:M${n}`).setNumberFormat('0.0000');s.getRange(`Q2:AA${n}`).setNumberFormat('0.0000');s.getRange(`AJ2:AL${n}`).setNumberFormat('0.00');s.getRange(`AB2:AB${n}`).setNumberFormat('0.00');s.getRange(`AE2:AE${n}`).setNumberFormat('0.00');s.getRange(`AD2:AD${n}`).setNumberFormat('0');s.getRangeByIndexes(1,spec.length,rows.length,imp.length).setNumberFormat('0.0000');
 for(const key of ['supplier','family','material','end_type','specs_met','rated_cycle_basis','rating_basis','length_basis','diameter_basis','selection_status','notes','source_catalogue_url','drawing_url','source_attributes']){
  const c=col(index[key]);s.getRange(`${c}:${c}`).format.columnWidth=['notes','rating_basis','length_basis','diameter_basis'].includes(key)?88:key==='source_attributes'?120:55;
 }
 s.getRange(`A1:${col(columns.length-1)}${n}`).format.verticalAlignment='center';
 const tab=s.tables.add(`A1:${col(columns.length-1)}${n}`,true,type+'AdditionalSprings');tab.showFilterButton=true;
 s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(3);s.showGridLines=false;s.tabColor={ST:'#2F6684',BT:'#6B608B',MI:'#52734D',SW:'#A56A33'}[type];
 for(let i=0;i<rows.length;i++){const got=s.getRange(`D${i+2}`).values[0][0];if(Math.abs(got-rows[i].energy_J)>1e-7*Math.max(1,got))throw Error(type+' energy mismatch '+i);checks.energyComparisons++;}
 const force=s.getRange('G2'),saved=force.values[0][0],before=s.getRange('D2').values[0][0];force.values=[[saved/2]];const actual=s.getRange('D2').values[0][0],expected=rows[0].k_N_per_mm*Math.min(rows[0].travel_mm,(saved/2)/rows[0].k_N_per_mm)**2/2000;if(Math.abs(actual-expected)>1e-7)throw Error(type+' recalculation failed');force.values=[[saved]];checks.recalculation[type]={before,changedForceEnergy:actual,expected,restored:s.getRange('D2').values[0][0]};checks.rows[type]=rows.length;
}
wb.recalculate();
for(const type of ['ST','BT','MI','SW']){const pic=await wb.render({sheetName:type,range:'A1:M7',scale:1.25,format:'png'});await fs.writeFile(path.join(work,type+'-preview.png'),new Uint8Array(await pic.arrayBuffer()));}
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:2000});checks.errorScan=errors.ndjson;
await fs.writeFile(path.join(work,'columns.json'),JSON.stringify(columns,null,2));await fs.writeFile(path.join(work,'authoring-validation.json'),JSON.stringify(checks,null,2));
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(work,'supplier-tabs.xlsx'));console.log(JSON.stringify(checks));
