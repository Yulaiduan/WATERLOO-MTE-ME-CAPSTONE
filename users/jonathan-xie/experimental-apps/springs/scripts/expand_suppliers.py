"""Normalize additional supplier springs for the VSL catalogue expansion.

Run from springs: python scripts/expand_suppliers.py .work/supplier-expansion-20261111/sources
Inputs: saved STEINEL/Berger HTML, MISUMI SWM PDF and Swift public table text.
Units: supplier metric or inches/lbf, normalized mm/N/N per mm/J. Outputs:
data/additional-springs.json and persistent additional-id-registry.json.
Limits: nominal linear compression models; >=60 J and free length <=254 mm;
not a VSL fit, procurement confirmation or hardware/fatigue qualification.
Requires lxml and pdfplumber from the authoring runtime. Never edits source Excel.
"""
import argparse,json,math,pathlib,re,logging,hashlib
from lxml import html
import pdfplumber
logging.getLogger('pdfminer').setLevel(logging.ERROR)
ROOT=pathlib.Path(__file__).resolve().parents[1]; N=4.4482216152605; INCH=25.4

def num(v):
    m=re.search(r'[-+]?\d+(?:[.,]\d+)?',str(v));return float(m[0].replace(',','.')) if m else None

def cells(row):
    for e in row.xpath('.//span[@class="mobile-label"]'):e.drop_tree()
    return [' '.join(c.text_content().split()) for c in row.xpath('./td|./th')]

def base(source,supplier,part,url,k,travel,force,free,**kw):
    return dict(source=source,supplier=supplier,part_number=part,part_url=url,spring_type='Compression',k_N_per_mm=k,travel_mm=travel,f_max_N=force,l_min_mm=free-travel,l_max_mm=free,free_length_mm=free,initial_tension_N=0,od_mm=None,id_mm=None,retrieved_date='2026-11-11',**kw)

def steinel(src):
    out=[]
    for code,percent in [('SZ8005',35),('SZ8010',30),('SZ8020',25),('SZ8030',20),('SZ8040',17),('SZ8045',10)]:
        tree=html.fromstring((src/f'steinel-{code}.html').read_bytes().decode('utf8'));table=tree.xpath('//table')[0]
        url='https://www.steinel.com/en/produkte-dienstleistungen/federn/systemfedern/online-katalog/system-springs/'+code
        for row in table.xpath('.//tr')[1:]:
            v=cells(row)
            if len(v)<10 or not v[9].startswith(code):continue
            hole,pin,wire,free,k,xlong,flong,xmax,fmax=map(lambda x:num(x),v[:9])
            if free>254:continue
            wx=re.findall(r'[\d.]+',v[2]);r=base('ST','STEINEL',v[9],url,k,xmax,fmax,free,family=code,material='Profiled valve spring steel wire 52SiCrNi5',end_type='Set, closed and ground',specs_met='ISO 10243' if code in ['SZ8010','SZ8020','SZ8030','SZ8040'] else None,wind_direction=None,rate_tolerance_pct=10,installation_hole_mm=hole,guide_rod_mm=pin,wire_width_mm=float(wx[0]),wire_thickness_mm=float(wx[1]),long_life_travel_mm=xlong,long_life_force_N=flong,rating_basis='Supplier max stroke s2 / force F2; separate long-life s1/F1 retained',length_basis='l_min = free length minus supplier max stroke; not solid height',diameter_basis='Hole and pin are installation dimensions, not measured coil OD/ID',source_attributes=dict(zip(['Hole diameter','Pin diameter','Wire','Free length','Rate','Long-life stroke','Long-life force','Maximum stroke','Maximum force','Part'],v[:10])),notes='Confirm actual loaded OD/ID before nested use. Long-life capacity can be below E_T.')
            r['drawing_url']=next(iter(row.xpath('.//a[contains(@href,"partcommunity")]/@href')),None);out.append(r)
    return out

def berger(src):
    tree=html.fromstring((src/'berger-blue-table.html').read_bytes());out=[]
    for row in tree.xpath('//tr'):
        v=cells(row)
        if len(v)<15 or not re.fullmatch(r'B\d+-\d+',v[0]):continue
        part,hole,free,pin,k,x1,f1,x2,f2,x3,f3,xmax,fmax,od,wire=v[:15];free=num(free)
        if free>254:continue
        url='https://www.berger-tools.co.uk/Die_Springs/B_Blue_Die_Spring_Iso10243_Medium_Load/PartPage/'+part+'/'
        wx=re.findall(r'[\d.]+',wire)
        r=base('BT','Berger Tools / Special Springs',part,url,num(k),num(xmax),num(fmax),free,family='B blue ISO medium load',material='High grade Cr-Si alloy spring steel (UNI 3545 / DIN 17221 / DIN 17223)',end_type='Closed and ground square',specs_met='ISO 10243; RoHS compliant',rate_tolerance_pct=10,installation_hole_mm=num(hole),guide_rod_mm=num(pin),wire_width_mm=float(wx[0]),wire_thickness_mm=float(wx[1]),long_life_travel_mm=num(x1),long_life_force_N=num(f1),medium_life_travel_mm=num(x2),medium_life_force_N=num(f2),temperature_min_C=-30,temperature_max_C=120,rating_basis='Supplier maximum operating deflection 37.5% / stated force; long-life 25% also retained',length_basis='l_min = free length minus rated operating deflection; not solid height',diameter_basis='OD is supplier approximate outside diameter; rod diameter is not actual spring ID',source_attributes={'raw_table_row':v},notes='Supplier identifies brand Special Springs. Shot peened and set. Confirm actual ID and loaded dimensional tolerances for nesting.')
        r['od_mm']=num(od);out.append(r)
    return out

def misumi(src):
    out=[];url='https://my.misumi-ec.com/pdf/press/18e_pr1419.pdf'
    with pdfplumber.open(src/'misumi-swm.pdf') as doc:
        table=doc.pages[0].extract_tables()[5];D=d=fmax=flong=None
        for row in table[3:]:
            if row[0] and re.fullmatch(r'\d+',row[0]):D=float(row[0]);d=float(row[1]);flong=num(row[5]);fmax=num(row[9])
            if D is None or not row[2] or not row[3]:continue
            ls=row[2].splitlines();ks=row[3].splitlines();xs=(row[8] or '').splitlines();xl=(row[4] or '').splitlines()
            if len(ls)!=len(ks) or len(ls)!=len(xs):raise ValueError('Misumi grouped rows ambiguous: '+repr(row))
            for L,K,X,XL in zip(ls,ks,xs,xl):
                free=num(L);k=num(K);travel=num(X)
                if not free or free>254 or D>70:continue
                part=f'SWM{int(D)}-{int(free)}';r=base('MI','MISUMI',part,'https://my.misumi-ec.com/vona2/detail/110100185760/?HissuCode='+part,k,travel,fmax,free,family='SWM medium load',material=None,end_type=None,wind_direction='Right',rate_tolerance_pct=None,long_life_travel_mm=num(XL),long_life_force_N=flong,rated_cycle_basis='300,000 uses at 32%; 1,000,000 uses at 25.6%, manufacturer guide',rating_basis='Supplier 32% travel / maximum table force; long-life 25.6% separately retained',length_basis='l_min = free length minus rated operating stroke; not solid height',diameter_basis='Nominal spring D/d from dimensional drawing; OD tolerance -0.7 mm; ID +0.1 to +0.7 mm; confirm drawing',source_catalogue_url=url,source_attributes={'D_mm':D,'d_mm':d,'L_mm':free,'spring_rate_source':K,'F_32pct_N':fmax,'stroke_32pct_mm':travel,'stroke_25_6pct_mm':num(XL),'F_25_6pct_N':flong},notes='PDF p1419/1420, rightmost table. Supplier cycle figures are catalogue conditions, not robot qualification. Confirm availability and current drawing.')
                r['od_mm']=D;r['id_mm']=d;out.append(r)
    return out

def swift(src):
    out=[];url='https://www.swiftsprings.com/pages/standard-coilover-springs-1-88id'
    for line in (src/'swift-standard-250.txt').read_text(encoding='utf8').splitlines():
        line=re.sub(r'^L\d+:\s*','',line);v=[x.strip() for x in line.split('|')]
        if len(v)!=7 or not re.fullmatch(r'\d{3}-\d{3}-\d{3,4}(?: [A-Z0-9]+)?',v[0]):continue
        if not all(re.fullmatch(r'[0-9,.]+',v[j]) for j in [2,3,4,5]):continue
        part=v[0];prefix=part.split('-');free_in=int(prefix[0])/10;id_in=int(prefix[1])/100
        if free_in>10 or id_in>2.5:continue
        rate=float(v[2].replace(',',''));usable=float(v[3]);maxstroke=float(v[4]);load=float(v[5].replace(',',''));price=num(v[6]) if v[6].startswith('$') else None
        r=base('SW','Swift Springs USA',part,url,rate*N/INCH,usable*INCH,load*N,free_in*INCH,family='Standard coilover '+('barrel' if re.search(r' B\d*$',part) else 'tight helix' if part.endswith(' TH') else 'straight'),material='Swift proprietary HS5.TW spring material',end_type=None,package_qty=1,price=price,currency='USD',max_physical_stroke_mm=maxstroke*INCH,rating_basis='Published usable stroke intersects published max load; source max stroke is not substituted for usable stroke',length_basis='l_min = free length minus usable stroke, not coil-bind length',diameter_basis='ID is nominal seating ID; OD unknown unless explicitly B3 outside diameter 3 inches',source_attributes={'part':part,'free_length_in':free_in,'id_in':id_in,'k_lbf_per_in':rate,'usable_stroke_in':usable,'max_stroke_in':maxstroke,'max_load_lbf':load,'price_USD':price},notes='Max load corresponds to supplier maximum-stroke envelope. Use usable stroke for linear design. OD and winding hand need confirmation; no nested-fit approval.')
        r['id_mm']=id_in*INCH
        if part.endswith(' B3'):r['od_mm']=3*INCH
        out.append(r)
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('sources',type=pathlib.Path);a=ap.parse_args()
    groups=[steinel(a.sources),berger(a.sources),misumi(a.sources),swift(a.sources)];rows=[];seen=set();counts={}
    registry_file=ROOT/'data/additional-id-registry.json';registry=json.loads(registry_file.read_text()) if registry_file.exists() else {}
    for group in groups:
        for r in group:
            key=r['source']+':'+r['part_number']
            if key in seen:continue
            seen.add(key);k=r['k_N_per_mm'];x=min(r['travel_mm'],r['f_max_N']/k);E=k*x*x/2000
            if E<60-1e-9:continue
            assert 0<r['l_min_mm']<r['l_max_mm'] and r['f_max_N']>0
            r['energy_J']=E;r['usable_deflection_mm']=x;r['force_at_usable_N']=k*x;r['stroke_to_60J_mm']=math.sqrt(120000/k)
            if r.get('long_life_travel_mm') is not None:r['long_life_energy_J']=k*min(r['long_life_travel_mm'],r['long_life_force_N']/k)**2/2000
            r['selection_status']='Nominal operating-envelope screening; VSL fit not evaluated'
            if key not in registry:
                last=max([int(v[2:]) for v in registry.values() if v.startswith(r['source'])] or [0]);registry[key]=r['source']+str(last+1).zfill(4)
            r['catalogue_id']=registry[key];rows.append(r);counts[r['source']]=counts.get(r['source'],0)+1
    rows.sort(key=lambda r:(r['source'],r['free_length_mm'],r['od_mm'] or r.get('installation_hole_mm') or r['id_mm'] or 999,r['energy_J'],r['part_number']))
    payload={'date':'2026-11-11','scope':'Selected operating-rated compression springs with nominal E_T >=60 J and free length <=254 mm. STEINEL installation holes <=63 mm, MISUMI SWM D40-70, Berger blue family holes <=63 mm, Swift standard seating IDs <=2.5 inches. Not exhaustive supplier catalogues.','counts':counts,'rows':rows,'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in a.sources.iterdir() if p.is_file()}}
    (ROOT/'data/additional-springs.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8');registry_file.write_text(json.dumps(registry,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'counts':counts,'total':len(rows),'examples':[{'id':r['catalogue_id'],'part':r['part_number'],'E_J':round(r['energy_J'],2),'k':r['k_N_per_mm'],'L':r['free_length_mm'],'OD':r['od_mm'],'ID':r['id_mm'],'travel':r['travel_mm']} for r in rows if r['free_length_mm']<=130][:18]},indent=2))
if __name__=='__main__':main()
