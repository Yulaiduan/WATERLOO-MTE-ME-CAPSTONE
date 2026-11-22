"""Add IEM DieMax springs from the supplied PDF to the local catalogue.
Run: bundled-python scripts/add_diemax.py PATH_TO_PDF from springs root.
Inputs: inch/metric supplier tables (lbf per 0.1 in, N/mm); >=60 J screen.
Outputs: normalized JSON/ID registry and artifact authoring/append work files.
Limits: dated PDF, nominal linear ratings; no fatigue or VSL fit validation.
"""
import pathlib,json,re,math,shutil,sys,hashlib
from pypdf import PdfReader
R=pathlib.Path(__file__).resolve().parents[1];W=R/'.work/dm-20261121';W.mkdir(parents=True,exist_ok=True)
source=pathlib.Path(sys.argv[1]);raw=R/'data/raw/2026-11-21-dm';raw.mkdir(parents=True,exist_ok=True);shutil.copy2(source,raw/source.name)
pages=[p.extract_text() for p in PdfReader(source).pages];N=4.4482216152605
pattern=re.compile(r'9-(\d{2})(\d{2})-(\d{2,3})')
records={};count={};errors=[]
# Hole/rod sizes read visually from rendered metric tables. The PDF text layer
# incorrectly encodes several merged diameter cells (e.g. 13/6 vs visible 12.5/7).
metric_dims={'06':(10,5),'08':(12.5,7),'10':(16,8.5),'12':(20,10),'16':(25,12.5),'20':(32,16),'24':(40,20),'32':(50,25),'40':(63,38)}
inch_rods={'06':3/16,'08':9/32,'10':11/32,'12':3/8,'16':1/2,'20':5/8,'24':3/4,'32':1,'40':1.5}
for i in range(7,25):
 unit='metric' if 15<=i<=22 else 'inch';count[str(i+1)]=0
 for line in pages[i].splitlines():
  m=pattern.search(line)
  if not m:continue
  pn=m[0];tail=line[m.end():].split();assert len(tail)==9,(i+1,line)
  values=list(map(float,tail));code,lengthcode,suffix=m.groups()
  L=float(line[:m.start()].split()[-1]) if unit=='metric' else int(lengthcode)/4
  row=dict(pdf_page=i+1,printed_page=i-1,units=unit,part_number=pn,free_length=L,rate=values[0],rate_units='N/mm' if unit=='metric' else 'lbf per 0.1 in',long_life_force=values[1],long_life_travel=values[2],average_life_force=values[3],average_life_travel=values[4],operating_force=values[5],operating_travel=values[6],solid_force=values[7],solid_travel=values[8],source_line=line)
  row['installation_hole'],row['guide_rod']=metric_dims[code] if unit=='metric' else (int(code)/16,inch_rods[code])
  assert unit not in records.setdefault(pn,{}),(pn,unit)
  records[pn][unit]=row;count[str(i+1)]+=1
assert sum(count.values())==sum(len(x) for x in records.values())
registry_path=R/'data/dm-id-registry.json';registry=json.loads(registry_path.read_text()) if registry_path.exists() else {}
rows=[];excluded=[]
for pn,variants in sorted(records.items()):
 s=variants.get('metric',variants.get('inch'));metric=s['units']=='metric';u=1 if metric else 25.4;funit=1 if metric else N
 k=s['rate'] if metric else s['rate']*N/2.54;L=s['free_length']*u;f=s['operating_force']*funit;x=min(s['operating_travel']*u,f/k)
 E=k*x*x/2000
 if E<60:excluded.append(pn);continue
 if pn not in registry:registry[pn]='DM'+str(1+max([int(v[2:]) for v in registry.values()] or [0])).zfill(4)
 suffix=pattern.fullmatch(pn)[3];roundwire=len(suffix)==3;duty={'11':'Light','21':'Medium','26':'Heavy','36':'Extra heavy'}[suffix[:2]];color={'Light':'Green','Medium':'Blue','Heavy':'Red','Extra heavy':'Yellow'}[duty]
 lx=min(s['long_life_travel']*u,s['long_life_force']*funit/k);ax=min(s['average_life_travel']*u,s['average_life_force']*funit/k)
 url='../../data/raw/2026-11-21-dm/'+source.name+'#page='+str(s['pdf_page'])
 variation=None
 if len(variants)==2:
  imp=variants['inch'];variation=100*abs(k-imp['rate']*N/2.54)/k
 assert 0<lx<=ax<=x+0.3 and x<s['solid_travel']*u,(pn,lx,ax,x)
 rows.append(dict(source='DM',catalogue_id=registry[pn],supplier='IEM / DieMax',part_number=pn,part_url=url,source_catalogue_url=url,k_N_per_mm=k,travel_mm=x,f_max_N=f,l_min_mm=L-x,l_max_mm=L,free_length_mm=L,initial_tension_N=0,energy_J=E,usable_deflection_mm=x,force_at_usable_N=k*x,stroke_to_60J_mm=math.sqrt(120000/k),od_mm=None,id_mm=None,spring_type='Compression',family='DieMax XL '+('round wire' if roundwire else 'rectangular wire')+' / '+duty,installation_hole_mm=s['installation_hole']*u,guide_rod_mm=s['guide_rod']*u,material='Chromium alloy steel' if roundwire else 'Chrome silicon alloy spring steel',end_type=None if roundwire else 'Closed and ground',specs_met=None if roundwire else 'ISO 10243 / NAAMS; wire ASTM A1000-99 (catalogue claim)',long_life_travel_mm=s['long_life_travel']*u,long_life_force_N=s['long_life_force']*funit,long_life_energy_J=k*lx*lx/2000,average_life_travel_mm=s['average_life_travel']*u,average_life_force_N=s['average_life_force']*funit,average_life_energy_J=k*ax*ax/2000,max_physical_stroke_mm=s['solid_travel']*u,solid_height_mm=L-s['solid_travel']*u,solid_force_N=s['solid_force']*funit,duty=duty,color=color,pdf_page=s['pdf_page'],metric_imperial_rate_variation_pct=variation,rated_cycle_basis='Long-life / average-life categories; no numerical cycle count supplied',rating_basis='Published maximum OPERATING force/travel intersection; travel to solid is a separate nonoperating endpoint',length_basis='l_min = free length minus conservative operating deflection; separate derived solid height',diameter_basis='Hole/rod installation sizes from visible table; actual coil OD/ID not published',selection_status='Nominal >=60 J screening; VSL fit and fatigue not evaluated',notes='Metric table is primary where the part repeats; inch table originals retained separately in source values. Inch rate is lbf PER 0.1 IN, converted to N/mm. Never operate to solid. No price/package quantity supplied. PDF diameter text-layer errors corrected against visible table.',retrieved_date='2026-11-21',source_attributes={'primary':s['units'],'tables':variants,'source_pdf_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}))
rows.sort(key=lambda r:r['catalogue_id'])
payload={'counts':{'DM':len(rows)},'rows':rows,'screened_unique_parts':len(records),'source_rows_by_pdf_page':count,'excluded_below_60J':len(excluded),'source_pdf':source.name,'filter':'E_T >=60 J at maximum operating limit; no length filter'}
for target in [W/'payload.json',R/'data/dm-springs.json']:target.write_bytes((json.dumps(payload,indent=2,ensure_ascii=False)+'\n').encode('utf8'))
registry_path.write_bytes((json.dumps(registry,indent=2)+'\n').encode())
# Reuse the established artifact-tool authoring and package-preservation append.
b=(R/'scripts/build_supplier_tabs.mjs').read_text(encoding='utf-8-sig').replace("path.join(root,'data/additional-springs.json')","path.join(work,'payload.json')").replace("['ST','BT','MI','SW']","['DM']").replace("s.tabColor={ST:'#2F6684',BT:'#6B608B',MI:'#52734D',SW:'#A56A33'}[type]","s.tabColor='#006447'").replace("date:'2026-11-11'","date:'2026-11-21'").replace("'Supplier max stroke (mm)'","'Travel to solid - NOT operating (mm)'").replace("'Supplier max stroke (in)'","'Travel to solid - NOT operating (in)'")
extra=[['average_life_travel_mm','Average-life travel (mm)'],['average_life_force_N','Average-life force (N)'],['average_life_energy_J','Average-life energy (J)'],['solid_height_mm','Derived solid height (mm)'],['solid_force_N','Published force at solid (N)'],['duty','Load class'],['color','Colour'],['pdf_page','PDF page (1-based)'],['metric_imperial_rate_variation_pct','Metric/inch rate difference (%)']]
b=b.replace("['source_attributes','Original supplier values']]","['source_attributes','Original supplier values'],"+','.join(json.dumps(e) for e in extra)+']')
b=b.replace("const tab=s.tables.add", "for(const key of ['average_life_travel_mm','average_life_force_N','average_life_energy_J','solid_height_mm','solid_force_N','metric_imperial_rate_variation_pct']){const cc=col(index[key]);s.getRange(`${cc}2:${cc}${n}`).setNumberFormat('0.0000');}\n for(let i=0;i<rows.length;i++){const rr=i+2,cc=col(index.average_life_energy_J),xc=col(index.average_life_travel_mm),fc=col(index.average_life_force_N);s.getRange(`${cc}${rr}`).formulas=[[`=E${rr}*MIN(${xc}${rr},${fc}${rr}/E${rr})^2/2000`]];}\n const tab=s.tables.add")
b=b.replace("['max_physical_stroke_mm','Travel to solid - NOT operating (in)',1/25.4]]", "['max_physical_stroke_mm','Travel to solid - NOT operating (in)',1/25.4],['average_life_travel_mm','Average-life travel (in)',1/25.4],['average_life_force_N','Average-life force (lbf)',1/4.4482216152605],['solid_height_mm','Derived solid height (in)',1/25.4],['solid_force_N','Published force at solid (lbf)',1/4.4482216152605]]")
(W/'build.mjs').write_bytes(b.encode('utf8'))
m=(R/'scripts/merge_supplier_tabs.py').read_text(encoding='utf-8-sig').replace("ROOT/'data/additional-springs.json'","work/'payload.json'").replace("{'ST','BT','MI','SW'}","{'DM'}").replace("['ST','BT','MI','SW']","['DM']")
(W/'merge.py').write_bytes(m.encode());shutil.copy2(R/'outputs/2026-11-13-md-rf/spring-catalogue-expanded.xlsx',W/'original.xlsx')
print({k:v for k,v in payload.items() if k!='rows'});print('energy range',min(r['energy_J'] for r in rows),max(r['energy_J'] for r in rows))