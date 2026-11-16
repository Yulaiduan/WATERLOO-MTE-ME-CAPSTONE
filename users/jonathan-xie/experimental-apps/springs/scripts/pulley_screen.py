"""Read saved V6 spring geometry and calculate preliminary pulley screening values.

Run: python scripts/pulley_screen.py (from the springs folder).
Inputs: v6-spring-solutions.xlsx; user 3800 N equal-span tension, 90 deg turn,
6 mm rope; dimensions in mm, stress in MPa. Outputs: dated JSON research record.
Uses only Python standard library. Does not modify Excel or execute VSL. Geometry
is reported from saved solutions, not revalidated against the newer mass model.
Bearing ratings are comparisons, not allowable loads or hardware qualification.
"""
import hashlib,json,math,pathlib,xml.etree.ElementTree as ET,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
BOOK=ROOT/'v6-spring-solutions.xlsx'

def solutions():
    with zipfile.ZipFile(BOOK) as z:
        ss=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
        rel={x.get('Id'):x.get('Target') for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheet=next(x for x in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS) if x.get('name')=='VSL state')
        target=rel[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        out=[]
        for row in ET.fromstring(z.read(target)).findall('m:sheetData/m:row',NS):
            cells={}
            for c in row:
                v=c.find('m:v',NS)
                value=''.join(c.find('m:is',NS).itertext()) if c.get('t')=='inlineStr' else ss[int(v.text)] if c.get('t')=='s' and v is not None else v.text if v is not None else ''
                cells[''.join(x for x in c.get('r','') if x.isalpha())]=value
            key=cells.get('A','')
            if key.startswith('S') and key[1:].isdigit():out.append(json.loads(cells['B']))
        return out

def main():
    force=3800.; radial=math.sqrt(2)*force
    rows=solutions(); latest=[r for r in rows if int(r['id'][1:])>=27]
    summary=[]
    for r in latest:
        summary.append({'id':r['id'],'saved_at':r.get('savedAt'),'geometry_mm_deg':r['geometry'],'working_theta2_deg':[r['parameters']['te'],r['parameters']['tc']],'link_length_mm':r['parameters']['L2'],'payloads_kg_total':r['payloads'],'enabled_spring_masks':r['masks'],'saved_peak_residual_Nm':r['metrics']['worstNm'],'springs':[{k:s.get(k) for k in ['part','type','k','initial','od','free','fmax','p0']} for s in r['springs']]})
    out={'date':'2026-11-11','status':'preliminary analytical and supplier-data screening','workbook_sha256':hashlib.sha256(BOOK.read_bytes()).hexdigest(),'saved_solution_count':len(rows),'latest_solutions':summary,'load_checks':{'tension_N':force,'radial_at_90deg_N':radial,'radial_at_180deg_N':2*force,'exact_mass_scale':31/13.5,'scaled_1670N':1670*31/13.5,'SG20_C0_over_P':1700/radial,'SG20_P_over_C0':radial/1700,'ball_bearing_proposed_C0_for_s0_2_N':2*radial,'rope_screen_D_over_d_8_diameter_mm':8*6,'SG20_approx_rope_pitch_radius_mm':24/2-1.75+6/2,'SG20_approx_pitch_D_over_d':(24-2*1.75+6)/6},'shaft_checks':[{'diameter_mm':d,'single_shear_MPa':radial/(math.pi*d*d/4),'double_shear_MPa':radial/(2*math.pi*d*d/4),'illustrative_point_load_bending_MPa_span16mm':8*radial*16/(math.pi*d**3)} for d in [4,5,6,8,10]],'limitations':['3800 N is a supplied screening envelope, not a recomputed V6 dynamic peak.','Saved solutions stop at 165 or 170 deg; no spring or routing validity to 240 deg is established.','Shaft bending uses an illustrative central point load on simply supported 16 mm span, not a modeled joint.','Energy catalogue and solution workbooks are read only.']}
    assert abs(radial-5374.011537017761)<1e-8
    assert abs(out['load_checks']['SG20_approx_rope_pitch_radius_mm']-13.25)<1e-10
    dest=ROOT/'research'/'2026-11-11-pulleys'/'screening-results.json'
    dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'solutions_read':len(rows),'latest_ids':[r['id'] for r in latest],'load_checks':out['load_checks'],'output':str(dest)},indent=2))
if __name__=='__main__':main()
