"""Normalize captured McMaster browser tables for a metric spring catalogue.

Usage: python normalize_catalogue.py --input DIR --output DIR
Inputs: UTF-8 *-captures.json and part-details.json from public catalogue UI.
Units: original McMaster units; outputs mm, N, N/mm, N mm, degrees, N mm/rad.
Outputs: reproducible JSON payload, compressed source snapshots, coverage report.
Limitations: listed ratings, not fatigue or physical testing; no invented ratings.
"""
import argparse, collections, fractions, gzip, hashlib, json, math, re
from pathlib import Path

LBF=4.4482216152605
INCH=25.4
PART=re.compile(r'^\d+[A-Z]\d+$')

def load_json(path):
    if path.exists():return json.loads(path.read_text(encoding='utf-8'))
    with gzip.open(str(path)+'.gz','rt',encoding='utf-8') as fp:return json.load(fp)

def clean(s):
    return re.sub(r'\s+', ' ', str(s)).strip()

def scalar(s):
    s=clean(s).replace(',', '').lstrip('$')
    if not s or s in ('—','–','-') or re.search(r'Not Rated|to|±|<|>',s,re.I): return None
    m=re.match(r'^([+-]?(?:\d+\s+\d+/\d+|\d+/\d+|\d*\.?\d+))',s)
    if not m:return None
    x=m.group(1)
    if ' ' in x:
        a,b=x.split();return float(a)+float(fractions.Fraction(b))
    return float(fractions.Fraction(x))

def inch(s):
    n=scalar(s)
    return None if n is None else n/INCH if re.search(r'\bmm\b',s) else n

def rate(s):
    n=scalar(s)
    if n is None:return None
    if 'lbf/mm' in s:return n*INCH
    if 'N/mm' in s:return n*INCH/LBF
    return n

def times(n,f):return None if n is None else n*f

def convert_attribute(label,value):
    if not value or label in ['Includes','Length','OD','ID','Wire Diameter','Wire Width','Wire Thickness','Compressed Length @ Maximum Load','Extended Length @ Maximum Load','Maximum Load','Minimum Load','Spring Rate','Deflection Angle','Leg Length','For Shaft Diameter','Spring Length @ Maximum Torque','Maximum Torque','Number of Coils']:
        return None
    factor=None;offset=0;unit=None
    if 'lbf/in' in value:factor=LBF/INCH;unit='N/mm'
    elif 'lbf/mm' in value:factor=LBF;unit='N/mm'
    elif re.search(r'in[· ]?lbf',value):factor=LBF*INCH;unit='N mm'
    elif re.search(r'\blb\.',value) and re.search(r'Load|Force|Tension',label):factor=LBF;unit='N'
    elif re.search(r'\bmm\b',value):factor=1;unit='mm'
    elif '"' in value:factor=INCH;unit='mm'
    elif re.search(r'Temperature|Temp\.',label) and re.search(r'F\b',value):factor=5/9;offset=-32*5/9;unit='deg C'
    elif re.search(r'Angle|Deflection',label) and '°' in value:factor=1;unit='deg'
    if factor is None:return None
    parts=re.split(r'\s+to\s+',value)
    vals=[scalar(x) for x in parts]
    if any(v is None for v in vals):return None
    return {'unit':unit,'values':[v*factor+offset for v in vals]}

def headers(t):
    hs=t['headers']; result=[]
    expanded=[]
    for hr in hs:
        line=[]
        for c in hr:line += [clean(c['text'])]*c['span']
        expanded.append(line)
    for i,h in enumerate(expanded[-1]):
        parent=expanded[-2][i] if len(expanded)>1 and i<len(expanded[-2]) else ''
        if parent and parent!=h:h=parent+' '+h
        result.append(h)
    # The leading header is the image/sticky-group column, absent from part rows.
    if result and not result[0]:result=result[1:]
    return result

def listing_records(ds,kind):
    records={};conflicts=[]
    for d in ds:
        for t in d['tables']:
            hs=headers(t); family=t.get('heading','Compression Springs')
            ctx={}
            for row in t['rows']:
                links=[a for a in row['links'] if PART.fullmatch(clean(a['text']))]
                if not links:
                    if any(c['span']>2 for c in row['cells']):
                        label=clean(row['cells'][0]['text'])
                        if not label:continue
                        if 'Deflection' in label:ctx['deflection_deg']=scalar(label)
                        elif 'Hand-Wound' in label:ctx['wind_direction']='Left Hand' if 'Left' in label else 'Right Hand'
                        elif 'End' in label:ctx['end_type']=label
                        elif any(x in label for x in ['Steel','Brass','Bronze','Nickel']):ctx['material']=label
                    continue
                cells=[clean(c['text']) for c in row['cells']]
                assert len(cells)==len(hs),(family,len(cells),len(hs),cells,hs)
                fields={}; seen=collections.Counter()
                for h,v in zip(hs,cells):
                    if not h:continue
                    seen[h]+=1;fields[h+(' #'+str(seen[h]) if seen[h]>1 else '')]=v
                for a in links:
                    part=clean(a['text']); obj={'part_number':part,'part_url':a['href'],'type':kind,'family':family,'listing':fields,'group':dict(ctx),'source_category_url':d['url']}
                    if part in records and records[part]!=obj:
                        # Viewport changes can suppress a text rendering; retain fuller evidence.
                        if records[part]['listing']!=fields:conflicts.append(part)
                    if part not in records or len(json.dumps(obj))>=len(json.dumps(records[part])):records[part]=obj
    return records,sorted(set(conflicts))

def detailed_fields(rows):
    result={};counter=collections.Counter();group=''
    for row in rows:
        if len(row)<2:continue
        label=clean(row[0]);value=clean(' | '.join(row[1:]))
        if not value:
            group=label
            continue
        if group and label in ['Minimum','Maximum','Type','Form','Width','Thickness']:
            label=group+' '+label
        else:group=''
        counter[label]+=1
        result[label+(' #'+str(counter[label]) if counter[label]>1 else '')]=value
    return result

def get(obj,*keys):
    for k in keys:
        if k in obj:return obj[k]
    return ''

def normalize(r,detail):
    f=r['listing'];a=detailed_fields(detail.get('rows',[]));g=r['group'];kind=r['type']
    pick=lambda *keys:get(a,*keys) or get(f,*keys)
    r['attributes']=a;r['detail_fetched']=bool(detail);r['drawing_url']=next((i['url'] for i in detail.get('images',[]) if i['url']),'')
    r['metric_attributes']={k:m for k,v in a.items() if (m:=convert_attribute(k,v)) is not None}
    r['material']=pick('Material') or g.get('material','')
    r['end_type']=pick('End Type') or g.get('end_type','')
    r['wind_direction']=pick('Spring Wind Direction') or g.get('wind_direction','')
    r['deflection_deg']=scalar(pick('Deflection Angle')) or g.get('deflection_deg')
    # Prices and pack quantities come from the full listing, avoiding transient lead times.
    r['package_qty']=scalar(get(f,'Pkg. Qty.'))
    if r['package_qty'] is None and 'Each' in f:r['package_qty']=1
    r['price_usd']=scalar(get(f,'Pkg.','Each'))
    r['unit_price_usd']=r['price_usd']/r['package_qty'] if r['price_usd'] is not None and r['package_qty'] else None
    free=inch(pick('Length','Lg.'))
    loaded=inch(pick('Compressed Length @ Maximum Load','Compressed Lg. @ Max. Load')) if kind=='MC' else inch(pick('Extended Length @ Maximum Load','Extended Lg. @ Max. Load'))
    r['free_length_in']=free
    r['l_min_in']=loaded if kind=='MC' else free if kind=='ME' else None
    r['l_max_in']=free if kind=='MC' else loaded if kind=='ME' else None
    r['travel_in']=r['l_max_in']-r['l_min_in'] if r['l_max_in'] is not None and r['l_min_in'] is not None else None
    r['k_lbf_per_in']=rate(pick('Spring Rate','Spring Rate, lbf/in'))
    r['f_max_lbf']=scalar(pick('Maximum Load','Load Maximum','Max. Load','Load, lb. Max.','Load Max., lb.','Max., lb.'))
    r['initial_tension_lbf']=scalar(pick('Minimum Load','Load Minimum','Min. Load, lb.','Load, lb. Min.','Load Min.'))
    for key,labels in {
        'od_in':['OD'], 'id_in':['ID'], 'wire_dia_in':['Wire Diameter','Wire Dia.','Wire Dia.'],
        'wire_width_in':['Wire Width','Wire Wd.'], 'wire_thickness_in':['Wire Thickness','Wire Thk.'],
        'shaft_dia_in':['For Shaft Diameter','For Shaft Dia.'], 'leg_length_in':['Leg Length','Leg Lg.'],
        'body_at_max_torque_in':['Spring Length @ Maximum Torque','Spring Lg. @ Max. Torque'],
    }.items():r[key]=inch(pick(*labels))
    r['coils']=scalar(pick('Number of Coils','No. of Coils'))
    r['torque_max_in_lbf']=scalar(pick('Maximum Torque','Max. Torque, in·lbf'))
    r['k_torsion_in_lbf_per_deg']=r['torque_max_in_lbf']/r['deflection_deg'] if r['torque_max_in_lbf'] is not None and r['deflection_deg'] else None
    r['k_N_per_mm']=times(r['k_lbf_per_in'],LBF/INCH)
    for key in ['free_length','l_min','l_max','travel','od','id','wire_dia','wire_width','wire_thickness','shaft_dia','leg_length','body_at_max_torque']:
        r[key+'_mm']=times(r.get(key+'_in'),INCH)
    r['f_max_N']=times(r['f_max_lbf'],LBF);r['initial_tension_N']=times(r['initial_tension_lbf'],LBF)
    r['torque_max_N_mm']=times(r['torque_max_in_lbf'],LBF*INCH)
    r['k_torsion_N_mm_per_rad']=times(r['k_torsion_in_lbf_per_deg'],LBF*INCH*180/math.pi)
    r['nominal_id_mm']=r['od_mm']-2*r['wire_dia_mm'] if r['od_mm'] is not None and r['wire_dia_mm'] is not None else None
    r['mean_coil_dia_mm']=r['od_mm']-r['wire_dia_mm'] if r['od_mm'] is not None and r['wire_dia_mm'] is not None else None
    r['spring_index']=r['mean_coil_dia_mm']/r['wire_dia_mm'] if r['mean_coil_dia_mm'] is not None and r['wire_dia_mm'] else None
    notes=[]
    if kind=='MC':r['length_basis']='l_min at F_max; l_max free. Not solid height.'
    elif kind=='ME':r['length_basis']='l_min free; l_max at F_max. Hook datum follows supplier drawing.'
    else:r['length_basis']='Body length at T_max. Shaft diameter is a mounting limit, not coil ID.'
    if kind=='MT':
        notes.append('kθ = T_max / rated deflection (rad); nominal secant rate, not a published measured rate.')
        r['selection_status']='Torsion mounting / linkage model required'
    elif 'Assortment' in r['family']:r['selection_status']='Assortment; no single spring rating'
    elif 'Cut-to-Length' in r['family']:r['selection_status']='Cut geometry and end formation required'
    elif 'Extra-Stretch' in r['family']:r['selection_status']='Rubber force law requires review'
    elif any(r.get(k) is None for k in ['k_N_per_mm','travel_mm','f_max_N','l_min_mm','l_max_mm']):r['selection_status']='Missing a catalogued force / travel / rate limit'
    elif kind=='ME' and r['initial_tension_N'] is None:r['selection_status']='Initial tension not rated; verify force law'
    else:r['selection_status']='Nominal linear screening data available'
    if kind in ['MC','ME'] and r['k_N_per_mm'] is not None and r['travel_mm'] is not None:
        r['nominal_force_at_max_N']=r['k_N_per_mm']*r['travel_mm']+(r['initial_tension_N'] or 0) if kind=='MC' or r['initial_tension_N'] is not None else None
    else:r['nominal_force_at_max_N']=None
    r['force_rating_difference_pct']=(r['nominal_force_at_max_N']/r['f_max_N']-1)*100 if r['nominal_force_at_max_N'] is not None and r['f_max_N'] else None
    if r['force_rating_difference_pct'] is not None and abs(r['force_rating_difference_pct'])>10:
        notes.append('F_max differs from nominal F_initial+kΔl by >10%. Review supplier limits. This flag is not a design acceptance tolerance.')
        if r['selection_status']=='Nominal linear screening data available':r['selection_status']='Review supplier force / rate / travel mismatch'
    if not detail:notes.append('Individual part specification page not yet captured.')
    r['notes']=' '.join(notes);return r

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--registry',type=Path);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    if (args.input/'part-details.json').exists() or (args.input/'part-details.json.gz').exists():details=load_json(args.input/'part-details.json')
    else:
        details={}
        for kind in ['MC','ME','MT']:details.update(load_json(args.input/('part-details-'+kind+'.json')))
    registry_path=args.registry or args.output/'id-registry.json'
    registry=json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {}
    all_rows=[];coverage=[];source={}
    for kind,name,expected in [('MC','compression',2120),('ME','extension',4719),('MT','torsion',558)]:
        ds=load_json(args.input/(name+'-captures.json'))
        records,conflicts=listing_records(ds,kind);assert len(records)==expected,(kind,len(records),expected)
        rows=[normalize(r,details.get(part,{})) for part,r in sorted(records.items(),key=lambda kv:[int(x) if x.isdigit() else x for x in re.split(r'(\d+)',kv[0])])]
        allocated=registry.setdefault(kind,{})
        next_id=max([int(v[2:]) for v in allocated.values()]+[0])+1
        for r in rows:
            if r['part_number'] not in allocated:
                allocated[r['part_number']]=kind+f'{next_id:04d}';next_id+=1
            r['catalogue_id']=allocated[r['part_number']]
        all_rows+=rows;source[kind]=records
        coverage.append({'type':kind,'expected':expected,'captured':len(rows),'detail_pages':sum(r['detail_fetched'] for r in rows),'listing_conflicts':conflicts,'families':dict(collections.Counter(r['family'] for r in rows))})
        with gzip.open(args.output/(kind.lower()+'-catalogue.json.gz'),'wt',encoding='utf-8') as fp:json.dump(rows,fp,ensure_ascii=False,separators=(',',':'))
    payload={'schema_version':'mmc-springs/1','retrieved_date':'2026-10-28','supplier':'McMaster-Carr','currency':'USD','coverage':coverage,'rows':all_rows}
    (args.output/'catalogue-payload.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (args.output/'coverage.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
    registry_path.write_text(json.dumps(registry,indent=2),encoding='utf-8')
    print(json.dumps({'rows':len(all_rows),'coverage':coverage,'status':dict(collections.Counter(r['selection_status'] for r in all_rows))},indent=2))

if __name__=='__main__':main()
