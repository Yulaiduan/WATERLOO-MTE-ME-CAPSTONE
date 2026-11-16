"""Add MD/RF supplier snapshots. Run with bundled Python from springs root.
Inputs: public McMaster DOM rows and FOX HTML in .work/md-rf-20261113.
Outputs: normalized JSON, artifact-tool build/merge work files; mm,N,N/mm,J.
Nominal >=60 J filter; FOX forces are derived, not independent rated loads.
"""
import pathlib,json,re,math,shutil
from fractions import Fraction
from lxml import html
R=pathlib.Path(__file__).resolve().parents[1];W=R/'.work/md-rf-20261113';N=4.4482216152605
rows=[];errors=[]
registry_path=R/'data/md-rf-id-registry.json'
registry=json.loads(registry_path.read_text()) if registry_path.exists() else {}

def val(s):
 s=s.replace('"','').replace(',','').replace('$','').strip();return sum(float(Fraction(x)) for x in s.split())
def add(prefix,part,url,k,x,f,L,**kw):
 E=k*min(x,f/k)**2/2000
 if E<60:return
 key=prefix+':'+part
 if key not in registry:registry[key]=prefix+str(1+max([int(v[2:]) for v in registry.values() if v.startswith(prefix)] or [0])).zfill(4)
 rows.append(dict(source=prefix,catalogue_id=registry[key],supplier='McMaster-Carr' if prefix=='MD' else 'FOX',part_number=part,part_url=url,k_N_per_mm=k,travel_mm=x,f_max_N=f,l_min_mm=L-x,l_max_mm=L,free_length_mm=L,initial_tension_N=0,energy_J=E,usable_deflection_mm=min(x,f/k),force_at_usable_N=k*min(x,f/k),stroke_to_60J_mm=math.sqrt(120000/k),spring_type='Compression',retrieved_date='2026-11-13',od_mm=None,id_mm=None,**kw))
md=json.loads((W/'md.json').read_text(encoding='utf8'))
for r in md:
 c=r['cells'];imp='"' in c[2];unit=25.4 if imp else 1;shift=1 if len(c)==18 else 0;L=val(c[2])*unit;low=val(c[5])*unit;k=val(c[8])*N/(25.4 if imp else 1);f=val(c[7])*N
 for j,lnk in enumerate(r['links']):
  pi=11+shift if j==0 else 14+shift;qty=1 if j==0 else val(c[13+shift]);price=val(c[12+shift] if j==0 else c[15+shift])
  add('MD',lnk['text'],lnk['url'],k,L-low,f,L,installation_hole_mm=val(c[0])*unit,guide_rod_mm=val(c[1])*unit,wire_thickness_mm=val(c[3])*unit,wire_width_mm=val(c[4])*unit,material=c[9],end_type=c[10],specs_met=c[11] if shift else None,price=price,currency='USD',package_qty=qty,family='Color-coded die springs',rating_basis='Published maximum load, rate and compressed length; conservative intersection',length_basis='Supplier compressed length at maximum load, not solid height',diameter_basis='Hole/shaft are installation dimensions, not actual OD/ID',selection_status='Nominal screening; VSL fit not evaluated',notes='Below-60 J options omitted. Each/package part numbers retained separately.',source_attributes=r)
tree=html.fromstring((W/'fox.html').read_bytes());seen=set()
for tr in tree.xpath('//tr'):
 c=[' '.join(x.text_content().split()) for x in tr.xpath('./td')]
 if not any('Spring:' in x for x in c):continue
 desc=next(x for x in c if 'Spring:' in x);pn=next((x for x in c if re.fullmatch(r'803-\d+-\d+',x)),None)
 if not pn or pn in seen:continue
 seen.add(pn)
 try:
  def find(p):return float(re.search(p,desc,re.I)[1])
  diameter=find(r'([\d.]+)\s*(?:in)?\s*ID')*25.4;k=find(r'([\d.]+)\s*lbs?/in')*N/25.4;L=find(r'([\d.]+)\s*(?:in)?\s*TLG')*25.4;x=find(r'([\d.]+)\s*(?:in)?(?:/[\d.]+mm)?\s*Travel')*25.4
  mm=re.search(r'/([\d.]+)mm\s*Travel',desc,re.I)
  if mm:x=min(x,float(mm[1]))
  add('RF',pn,'https://tech.ridefox.com/bike/general-info/918/2020+-sls-and-standard-steel-rear-shock-spring-information',k,x,k*x,L,family='SLS' if 'SLS' in desc else 'Standard steel',material='Steel',rating_basis='Force DERIVED as k times marked spring travel; no independent force rating supplied',length_basis='TLG free length; l_min is theoretical marked-travel ceiling, not recommended working minimum',diameter_basis='Published coil ID; OD not supplied',selection_status='Review: derived force / open travel boundary; not validated for VSL',notes='FOX requires shock travel LESS THAN marked spring travel. Reserve preload and working-stroke margin; energy is a nominal ceiling, not guaranteed operating capacity.',source_attributes={'supplier_row':c,'description':desc,'internal_part':c[1]})
  if rows and rows[-1]['part_number']==pn:rows[-1]['id_mm']=diameter
 except Exception as e:errors.append((pn,desc,str(e)))
assert not errors,errors
payload={'counts':{p:sum(r['source']==p for r in rows) for p in ['MD','RF']},'rows':rows,'screened_MD_parts':len({a['text'] for r in md for a in r['links']}),'screened_RF_parts':len(seen),'filter':'Nominal E_T >=60 J; no length filter'}
(W/'payload.json').write_bytes(json.dumps(payload,indent=2,ensure_ascii=False).encode('utf8'));(R/'data/md-rf-springs.json').write_bytes((W/'payload.json').read_bytes())
b=(R/'scripts/build_supplier_tabs.mjs').read_text(encoding='utf-8-sig').replace("path.join(root,'data/additional-springs.json')","path.join(work,'payload.json')").replace("['ST','BT','MI','SW']","['MD','RF']").replace("s.tabColor={ST:'#2F6684',BT:'#6B608B',MI:'#52734D',SW:'#A56A33'}[type]","s.tabColor=type==='MD'?'#2F6684':'#A56A33'").replace("F_max rated (N)","F_max rated / derived (N)").replace("date:'2026-11-11'","date:'2026-11-13'")
(W/'build.mjs').write_bytes(b.encode('utf8'))
m=(R/'scripts/merge_supplier_tabs.py').read_text(encoding='utf-8-sig').replace("ROOT/'data/additional-springs.json'","work/'payload.json'").replace("{'ST','BT','MI','SW'}","{'MD','RF'}").replace("['ST','BT','MI','SW']","['MD','RF']")
(W/'merge.py').write_bytes(m.encode('utf8'));shutil.copy2(R/'outputs/2026-11-11-suppliers/spring-catalogue-expanded.xlsx',W/'original.xlsx')
registry_path.write_bytes((json.dumps(registry,indent=2)+'\n').encode('utf8'))
print({k:v for k,v in payload.items() if k!='rows'})
