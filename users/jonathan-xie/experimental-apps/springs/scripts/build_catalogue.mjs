/** Build the McMaster spring catalogue workbook from normalized supplier captures.
 * Invocation: node build_catalogue.mjs INPUT_DIR OUTPUT_DIR
 * Inputs: catalogue-payload.json; engineering units mm, N, N/mm, N mm, deg, N mm/rad.
 * Outputs: mmc-spring-catalogue.xlsx, sheet previews and calculation checks.
 * Requires @oai/artifact-tool from the bundled authoring runtime.
 * Limits: supplier nominal ratings; does not certify installation or fatigue.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const [inputDir,outputDir]=process.argv.slice(2);
const data=JSON.parse(await fs.readFile(path.join(inputDir,'catalogue-payload.json'),'utf8'));
await fs.mkdir(outputDir,{recursive:true});
const wb=Workbook.create();
for(const name of ['MC','ME','MT','ReadMe'])wb.worksheets.add(name);
const col=i=>{let s='';for(let n=i+1;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const C={inch:25.4,lbf:4.4482216152605};
const n=(key,label,imperialKey,factor)=>({key,label,imperialKey,factor});
const linear=[n('k_N_per_mm','k (N/mm)','k_lbf_per_in','rate'),n('travel_mm','Δl rated (mm)','travel_in','inch'),n('f_max_N','F_max rated (N)','f_max_lbf','lbf'),n('l_min_mm','l_min rated (mm)','l_min_in','inch'),n('l_max_mm','l_max rated (mm)','l_max_in','inch'),n('free_length_mm','Free length (mm)','free_length_in','inch'),n('initial_tension_N','Initial tension / F_min (N)','initial_tension_lbf','lbf')];
const torsion=[n('k_torsion_N_mm_per_rad','kθ derived (N mm/rad)','k_torsion_in_lbf_per_deg','torsion'),n('deflection_deg','Rated rotational travel (deg)'),n('torque_max_N_mm','T_max rated (N mm)','torque_max_in_lbf','torque'),{key:'angle_min_deg',label:'Rotation min from free (deg)'},{key:'deflection_deg',label:'Rotation max from free (deg)'}];
const dims=[['od','OD'],['id','ID (catalogued)'],['wire_dia','Wire diameter'],['wire_width','Wire width'],['wire_thickness','Wire thickness'],['shaft_dia','Maximum mounting shaft diameter'],['leg_length','Leg length'],['body_at_max_torque','Body length at max torque']].map(([k,l])=>n(k+'_mm',l+' (mm)',k+'_in','inch'));
const extras=[{key:'nominal_id_mm',label:'ID nominal derived (mm)'},{key:'mean_coil_dia_mm',label:'Mean coil diameter derived (mm)'},{key:'spring_index',label:'Spring index derived (D/d)'},{key:'coils',label:'Number of coils'},{key:'package_qty',label:'Package quantity'},{key:'price_usd',label:'Package / each price (USD)'},{key:'unit_price_usd',label:'Unit price (USD)'},{key:'nominal_force_at_max_N',label:'Nominal force at rated travel (N)'},{key:'force_rating_difference_pct',label:'Nominal vs rated force difference (%)'}];
const textCols=[['family','McMaster family'],['material','Material'],['end_type','End type'],['wind_direction','Wind direction'],['selection_status','Screening status'],['length_basis','Length / mounting datum'],['notes','Rating notes'],['drawing_url','Technical drawing URL'],['source_category_url','Catalogue source URL'],['retrieved_date','Retrieved date'],['detail_fetched','Full specifications captured']].map(([key,label])=>({key,label}));
const imperialLabels={k_lbf_per_in:'k (lbf/in)',travel_in:'Δl rated (in)',f_max_lbf:'F_max rated (lbf)',l_min_in:'l_min rated (in)',l_max_in:'l_max rated (in)',free_length_in:'Free length (in)',initial_tension_lbf:'Initial tension / F_min (lbf)',od_in:'OD (in)',id_in:'ID (catalogued, in)',wire_dia_in:'Wire diameter (in)',wire_width_in:'Wire width (in)',wire_thickness_in:'Wire thickness (in)',shaft_dia_in:'Maximum mounting shaft diameter (in)',leg_length_in:'Leg length (in)',body_at_max_torque_in:'Body length at max torque (in)',torque_max_in_lbf:'T_max rated (in lbf)',k_torsion_in_lbf_per_deg:'kθ derived (in lbf/deg)'};

// Extra dimensional attributes retain source labels and are also converted to metric.
function metricAttribute(label,value){
  if(!value||/^(?:Length|OD|ID|Wire Diameter|Wire Width|Wire Thickness|Width|Thickness|Compressed Length @ Maximum Load|Extended Length @ Maximum Load|Maximum Load|Minimum Load|Spring Rate|Deflection Angle|Leg Length|For Shaft Diameter|Spring Length @ Maximum Torque|Maximum Torque|Number of Coils)$/.test(label))return null;
  let factor,offset=0,unit;
  if(/lbf\/in/.test(value)){factor=C.lbf/C.inch;unit='N/mm';}
  else if(/lbf\/mm/.test(value)){factor=C.lbf;unit='N/mm';}
  else if(/in[· ]?lbf/.test(value)){factor=C.lbf*C.inch;unit='N mm';}
  else if(/\blb\./.test(value)&&/Load|Force/.test(label)){factor=C.lbf;unit='N';}
  else if(/\bmm\b/.test(value)){factor=1;unit='mm';}
  else if(value.includes('"')){factor=C.inch;unit='mm';}
  else if(/Temperature|Temp\./.test(label)&&/F\b/.test(value)){factor=5/9;offset=-32*5/9;unit='°C';}
  else return null;
  // Fractions and decimal ranges are parsed explicitly; text remains available at the end.
  let pieces=value.split(/\s+to\s+/);
  const parse=s=>{let m=s.replaceAll(',','').match(/^\s*([+-]?(?:\d+\s+\d+\/\d+|\d+\/\d+|\d*\.?\d+))/);if(!m)return null;let v=m[1],z;if(v.includes(' ')){let [a,b]=v.split(/\s+/);let [c,d]=b.split('/');z=+a+(+c/+d);}else if(v.includes('/')){let [a,b]=v.split('/');z=+a/+b;}else z=+v;return z*factor+offset;};
  let vals=pieces.map(parse);if(vals.some(x=>x===null||!Number.isFinite(x)))return null;
  return {unit,values:vals};
}

const readme=wb.worksheets.getItem('ReadMe');
const readRows=[
 ['Spring catalogue','McMaster-Carr specifications. Retrieved 2026-10-28.'],
 ['Conversion constant','Value'],['mm per inch',C.inch],['N per lbf',C.lbf],
 ['Scope','The three user-linked categories: 2,120 standard compression, 4,719 extension and 558 torsion part numbers. Other McMaster compression subcategories are outside the supplied compression-family URL.'],
 ['Record grain','One row per McMaster part number, including assortment and cut-to-length products. Prefix MC / ME / MT and four digits identify a record; use the ID registry on future refreshes.'],
 ['Lengths','Compression l_min is compressed length at rated maximum load, not solid height. Extension l_min is free length. Attachment datums follow the supplier drawing.'],
 ['Rated travel','Δl = l_max − l_min. Missing or Not Rated supplier values remain blank; blank is not zero.'],
 ['Torsional rate','Derived kθ = T_max / (rated deflection × π / 180). This is a nominal secant rate; manufacturer does not list a measured spring rate in these torsion tables.'],
 ['Torsion packaging','Use winding direction and maximum mounting shaft diameter. The coil contracts radially and grows axially under load. Body length at max torque is not free body length.'],
 ['Initial tension','Extension F_min is the catalogued minimum load to start extension. It is distinct from installed preload and VSL p₀.'],
 ['VSL v5 mapping','Use springK in N/mm. V5 Fs=max(0,p₀+k[c(θ₂)−c(90°)]), where c is cable payout including wrap. Compare the full c range, not only the sidebar span Δl.'],
 ['Real extension length','For a nominal linear extension spring: L(θ)=L_free+[F_s(θ)−F_initial]/k only on the extended branch. Check force ≥ initial tension and force ≤ rated maximum throughout.'],
 ['Other spring types','Compression needs an installation that maps compression to cable tension. Direct torsion needs a mounting / transmission law; it cannot be inserted into springK as N/mm.'],
 ['Ranking goal','After force, stroke, package and mount feasibility, rank residual hip torque over the requested θ₂ interval. A close k alone does not establish gravity compensation.'],
 ['Force consistency','Nominal force = k×rated travel (+ initial tension for extension). Supplier rounding may differ from rated maximum load. Differences >10% are flagged without altering source ratings.'],
 ['Cut springs','Published cut-to-length k applies to the supplied stock length. Recalculate for cut active length and validate ends, force and travel before selection.'],
 ['Rubber and assortments','Retained for completeness. Rubber may be nonlinear and hysteretic; assortments do not identify one selectable spring.'],
 ['Prices','USD per package or each as displayed in listing. Unit price = package price / quantity. No currency conversion, tax, shipping or live availability assumption.'],
 ['Source fields','All captured supplier specification attributes and original listing values appear in labelled Source / Listing columns at the far right. Additional dimensional attributes also have metric columns.'],
 ['Unknown design limits','No inferred fatigue life, dynamic load rating, stress, tolerances or free torsion body length. Check the drawing and obtain missing design data for shortlisted parts.'],
 ['Source integrity','Public UI tables were scrolled completely and reconciled against category counts. Individual specification pages supply detailed properties. Raw arrays and normalized JSON are retained alongside the workbook.'],
 ['Model status','Catalogue preparation only. The v5 solver and its configuration workbook were not edited. No spring or hardware validation was performed.'],
 ['Refresh','Revisit supplier UI, retain part IDs in id-registry.json, rerun normalization and rebuild. Spreadsheet formulas update units from imperial numeric columns; JSON exports are snapshots.'],
 ['Type','Expected parts','Captured parts','Full specification pages'],
 ...data.coverage.map(c=>[c.type,c.expected,c.captured,c.detail_pages]),
];
for(let i=0;i<readRows.length;i++)readme.getRangeByIndexes(i,0,1,readRows[i].length).values=[readRows[i]];
readme.showGridLines=false;readme.getRange('A1:D29').format.font={name:'Arial',size:10,color:'#223044'};
readme.getRange('A:A').format.columnWidth=27;readme.getRange('B:B').format.columnWidth=105;readme.getRange('C:D').format.columnWidth=22;
readme.getRange('A1:B1').format.font={name:'Arial',size:14,bold:true,color:'#18374E'};
readme.getRange('B5:B24').format.wrapText=true;readme.getRange('A5:B24').format.rowHeight=42;
readme.getRange('A2:B2').format={fill:'#18374E',font:{color:'#FFFFFF',bold:true}};
readme.getRange('A25:D25').format={fill:'#18374E',font:{color:'#FFFFFF',bold:true}};
readme.tabColor='#8A9AA6';

const checks={rows:{},formulaSamples:[],numericComparisons:0};
for(const type of ['MC','ME','MT']){
  const sheet=wb.worksheets.getItem(type),rows=data.rows.filter(r=>r.type===type);
  for(const r of rows){r.retrieved_date=data.retrieved_date;r.angle_min_deg=type==='MT'?0:null;}
  const metric=[...(type==='MT'?torsion:linear),...dims.filter(d=>rows.some(r=>r[d.key]!==null)),...extras.filter(d=>rows.some(r=>r[d.key]!=null))];
  const moreMetric=new Map();
  for(const r of rows)for(const [k,m] of Object.entries(r.metric_attributes??{})){
    m.values.forEach((v,j)=>{const key='metric_extra:'+k+':'+j;moreMetric.set(key,{key,label:k+(m.values.length>1?(j?' max':' min'):'')+' ('+m.unit+')'});r[key]=v;});
  }
  metric.push(...moreMetric.values());
  const imperialKeys=[...new Set(metric.map(d=>d.imperialKey).filter(Boolean))];
  const attrKeys=[...new Set(rows.flatMap(r=>Object.keys(r.attributes)))];
  const listingKeys=[...new Set(rows.flatMap(r=>Object.keys(r.listing)))];
  const spec=[{key:'catalogue_id',label:'Catalogue ID'},{key:'part_number',label:'MMC part number'},{key:'part_url',label:'MMC part link'},...metric,...textCols,...imperialKeys.map(key=>({key,label:imperialLabels[key]})),...attrKeys.map(k=>({key:'attr:'+k,label:'Source: '+k})),...listingKeys.map(k=>({key:'listing:'+k,label:'Listing: '+k}))];
  const indexes=Object.fromEntries(spec.map((d,i)=>[d.key,i]));
  const matrix=[spec.map(d=>d.label),...rows.map(r=>spec.map(d=>d.key.startsWith('attr:')?r.attributes[d.key.slice(5)]??null:d.key.startsWith('listing:')?r.listing[d.key.slice(8)]??null:r[d.key]??null))];
  sheet.getRangeByIndexes(0,0,matrix.length,spec.length).values=matrix;
  // Excel formulas retain transparent, editable conversion relationships.
  for(const d of metric.filter(d=>d.imperialKey)){
    const dst=col(indexes[d.key]),src=col(indexes[d.imperialKey]);
    const f=d.factor==='inch'?"'ReadMe'!$B$3":d.factor==='lbf'?"'ReadMe'!$B$4":d.factor==='rate'?"'ReadMe'!$B$4/'ReadMe'!$B$3":d.factor==='torque'?"'ReadMe'!$B$4*'ReadMe'!$B$3":"'ReadMe'!$B$4*'ReadMe'!$B$3*180/PI()";
    sheet.getRange(`${dst}2:${dst}${rows.length+1}`).formulas=rows.map((r,i)=>[r[d.imperialKey]===null||r[d.imperialKey]===undefined?'=\"\"':`=${src}${i+2}*${f}`]);
  }
  sheet.getRange(`C2:C${rows.length+1}`).values=rows.map(r=>['Open McMaster part']);
  const writeDerived=(key,make)=>{if(indexes[key]===undefined)return;let c=col(indexes[key]);sheet.getRange(`${c}2:${c}${rows.length+1}`).formulas=rows.map((r,i)=>[make(r,i+2)]);};
  const ref=(key,row)=>`${col(indexes[key])}${row}`;
  if(type==='MT'){
    writeDerived('k_torsion_in_lbf_per_deg',(r,row)=>`=${ref('torque_max_in_lbf',row)}/E${row}`);
    sheet.getRange(`H2:H${rows.length+1}`).formulas=rows.map((r,i)=>[`=E${i+2}`]);
  }else{
    writeDerived('travel_in',(r,row)=>r.travel_in===null?'=\"\"':`=${ref('l_max_in',row)}-${ref('l_min_in',row)}`);
    writeDerived('nominal_force_at_max_N',(r,row)=>r.nominal_force_at_max_N==null?'=\"\"':`=D${row}*E${row}${type==='ME'?'+'+ref('initial_tension_N',row):''}`);
    writeDerived('force_rating_difference_pct',(r,row)=>r.force_rating_difference_pct==null?'=\"\"':`=(${ref('nominal_force_at_max_N',row)}/F${row}-1)*100`);
  }
  writeDerived('nominal_id_mm',(r,row)=>r.nominal_id_mm==null?'=\"\"':`=${ref('od_mm',row)}-2*${ref('wire_dia_mm',row)}`);
  writeDerived('mean_coil_dia_mm',(r,row)=>r.mean_coil_dia_mm==null?'=\"\"':`=${ref('od_mm',row)}-${ref('wire_dia_mm',row)}`);
  writeDerived('spring_index',(r,row)=>r.spring_index==null?'=\"\"':`=${ref('mean_coil_dia_mm',row)}/${ref('wire_dia_mm',row)}`);
  if(indexes.unit_price_usd!==undefined){let dst=col(indexes.unit_price_usd),price=col(indexes.price_usd),qty=col(indexes.package_qty);sheet.getRange(`${dst}2:${dst}${rows.length+1}`).formulas=rows.map((r,i)=>[r.price_usd!=null&&r.package_qty?`=${price}${i+2}/${qty}${i+2}`:'=\"\"']);}
  const used=sheet.getRangeByIndexes(0,0,rows.length+1,spec.length);
  used.format.font={name:'Arial',size:10,color:'#223044'};used.format.rowHeight=19;used.format.verticalAlignment='center';used.format.columnWidth=19;
  sheet.getRangeByIndexes(0,0,1,spec.length).format={fill:'#18374E',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',rowHeight:48};
  sheet.getRange(`A1:A${rows.length+1}`).format.columnWidth=16;sheet.getRange(`B1:B${rows.length+1}`).format.columnWidth=19;sheet.getRange(`C1:C${rows.length+1}`).format.columnWidth=24;
  sheet.getRange(`C2:C${rows.length+1}`).format.font={color:'#1766A4'};
  for(const d of [...metric,...imperialKeys.map(key=>({key}))]){let c=col(indexes[d.key]);sheet.getRange(`${c}2:${c}${rows.length+1}`).setNumberFormat('0.0000');}
  for(const key of ['package_qty','coils'])if(indexes[key]!==undefined){let c=col(indexes[key]);sheet.getRange(`${c}2:${c}${rows.length+1}`).setNumberFormat(key==='coils'?'0.00':'0');}
  for(const key of ['price_usd','unit_price_usd'])if(indexes[key]!==undefined){let c=col(indexes[key]);sheet.getRange(`${c}2:${c}${rows.length+1}`).setNumberFormat('$0.00');}
  for(const d of spec)if(['family','material','end_type','wind_direction','selection_status','length_basis','notes','drawing_url','source_category_url'].includes(d.key)||d.key.startsWith('attr:')||d.key.startsWith('listing:'))sheet.getRangeByIndexes(0,indexes[d.key],rows.length+1,1).format.columnWidth=d.key==='notes'||d.key==='length_basis'?100:d.key.includes('url')?80:35;
  for(const d of spec.filter(d=>d.key.startsWith('attr:')||d.key.startsWith('listing:'))){
    const maxLength=Math.max(d.label.length,...matrix.slice(1).map(row=>String(row[indexes[d.key]]??'').length));
    const range=sheet.getRangeByIndexes(0,indexes[d.key],rows.length+1,1);
    range.format.columnWidth=Math.min(150,Math.max(35,maxLength*1.08));
    if(maxLength>150)range.format.wrapText=true;
  }
  for(const key of ['notes','selection_status'])sheet.getRangeByIndexes(1,indexes[key],rows.length,1).format.wrapText=true;
  sheet.getRangeByIndexes(1,0,rows.length,spec.length).format.autofitRows();
  const table=sheet.tables.add(`A1:${col(spec.length-1)}${rows.length+1}`,true,type+'SpringCatalogue');table.showFilterButton=true;
  sheet.showGridLines=false;sheet.freezePanes.freezeRows(1);sheet.freezePanes.freezeColumns(3);sheet.tabColor=type==='MC'?'#18374E':type==='ME'?'#2F6684':'#6B608B';
  checks.rows[type]={rows:rows.length,columns:spec.length,metrics:metric.length};
  const rateKey=type==='MT'?'torque_max_in_lbf':'k_lbf_per_in';
  const rateCell=sheet.getRange(`${col(indexes[rateKey])}2`),original=rateCell.values[0][0],before=sheet.getRange('D2').values[0][0];
  rateCell.values=[[original*2]];
  const after=sheet.getRange('D2').values[0][0];
  if(Math.abs(after-2*before)>1e-8)throw Error(type+' unit conversion failed to recalculate');
  rateCell.values=[[original]];
  checks.rows[type].inputChangeRecalculation=true;
  await fs.writeFile(path.join(outputDir,type+'-columns.json'),JSON.stringify(spec,null,2));
}
wb.recalculate();
for(const type of ['MC','ME','MT']){
  const rows=data.rows.filter(r=>r.type===type),sheet=wb.worksheets.getItem(type);
  for(const i of [0,Math.floor(rows.length/2),rows.length-1]){
    const got=sheet.getRange(`D${i+2}:H${i+2}`).values[0];
    const want=type==='MT'?[rows[i].k_torsion_N_mm_per_rad,rows[i].deflection_deg,rows[i].torque_max_N_mm,0,rows[i].deflection_deg]:[rows[i].k_N_per_mm,rows[i].travel_mm,rows[i].f_max_N,rows[i].l_min_mm,rows[i].l_max_mm];
    got.forEach((v,j)=>{if(want[j]===null){if(v!==''&&v!==null)throw Error(`${type} missing value became ${v}`);}else if(Math.abs(v-want[j])>1e-8*Math.max(1,Math.abs(want[j])))throw Error(`${type} conversion mismatch ${i} ${j}: ${v} vs ${want[j]}`);checks.numericComparisons++;});
    checks.formulaSamples.push({type,row:i+2,values:got});
  }
  const img=await wb.render({sheetName:type,range:'A1:H10',scale:1.4,format:'png'});await fs.writeFile(path.join(outputDir,type+'-preview.png'),new Uint8Array(await img.arrayBuffer()));
}
const rm=await wb.render({sheetName:'ReadMe',range:'A1:B9',scale:1.2,format:'png'});await fs.writeFile(path.join(outputDir,'ReadMe-preview.png'),new Uint8Array(await rm.arrayBuffer()));
const err=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'Final formula error scan'});checks.errorScan=err.ndjson;
await fs.writeFile(path.join(outputDir,'workbook-validation.json'),JSON.stringify(checks,null,2));
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(outputDir,'mmc-spring-catalogue.xlsx'));
console.log(JSON.stringify(checks));
