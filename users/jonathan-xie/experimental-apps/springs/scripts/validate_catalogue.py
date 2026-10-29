"""Verify an exported catalogue against its normalized supplier data.

Usage: python validate_catalogue.py WORKBOOK PAYLOAD OUTPUT_JSON
Inputs: saved XLSX and catalogue JSON (metric/imperial keys with explicit units).
Output: compact coverage, numeric cache, identifier, hyperlink and source checks.
Limits: validates file structure and arithmetic; does not simulate Excel's UI,
spring fatigue, supplier availability, or a real VSL mechanism.
"""
from pathlib import Path
import collections, hashlib, json, math, re, sys, zipfile
import xml.etree.ElementTree as ET

book,payload_path,out=map(Path,sys.argv[1:])
data=json.loads(payload_path.read_text(encoding='utf-8'))
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','p':'http://schemas.openxmlformats.org/package/2006/relationships'}
RID='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
stats={'rows':{},'numeric_cells_checked':0,'native_hyperlinks_checked':0,'duplicate_ids':0,'invalid_numeric_values':0}
all_ids=[r['catalogue_id'] for r in data['rows']];assert len(all_ids)==len(set(all_ids))
with zipfile.ZipFile(book) as z:
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    def value(c):
        if c is None:return None
        t=c.attrib.get('t');v=c.find('s:v',NS)
        if t=='inlineStr':return ''.join(c.find('s:is',NS).itertext())
        if v is None:return None
        if t=='s':return strings[int(v.text)]
        if t in ['str','e']:return v.text or ''
        if t=='b':return v.text=='1'
        return float(v.text) if v.text else None
    for i,kind in enumerate(['MC','ME','MT'],1):
        root=ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml'))
        cells={c.attrib['r']:c for c in root.findall('.//s:sheetData/s:row/s:c',NS)}
        rows=[r for r in data['rows'] if r['type']==kind]
        rels={r.attrib['Id']:r.attrib for r in ET.fromstring(z.read(f'xl/worksheets/_rels/sheet{i}.xml.rels'))}
        links={l.attrib['ref']:rels[l.attrib[RID]]['Target'] for l in root.findall('s:hyperlinks/s:hyperlink',NS)}
        assert len(links)==len(rows)
        for j,r in enumerate(rows,2):
            assert re.fullmatch(kind+r'\d{4}',r['catalogue_id'])
            assert value(cells[f'A{j}'])==r['catalogue_id']
            assert value(cells[f'B{j}'])==r['part_number']
            assert links[f'C{j}']==r['part_url'];stats['native_hyperlinks_checked']+=1
            if kind=='MT':
                wanted=[r['torque_max_in_lbf']*4.4482216152605*25.4/math.radians(r['deflection_deg']),r['deflection_deg'],r['torque_max_in_lbf']*4.4482216152605*25.4,0,r['deflection_deg']]
            else:
                k=None if r['k_lbf_per_in'] is None else r['k_lbf_per_in']*4.4482216152605/25.4
                wanted=[k,None if r['travel_in'] is None else r['travel_in']*25.4,None if r['f_max_lbf'] is None else r['f_max_lbf']*4.4482216152605,None if r['l_min_in'] is None else r['l_min_in']*25.4,None if r['l_max_in'] is None else r['l_max_in']*25.4]
            for letter,expected in zip('DEFGH',wanted):
                actual=value(cells.get(f'{letter}{j}'))
                if expected is None:assert actual is None or actual=='',(kind,j,letter,actual)
                else:
                    assert isinstance(actual,(float,int)) and math.isfinite(actual),(kind,j,letter,actual)
                    assert abs(actual-expected)<=1e-8*max(1,abs(expected)),(kind,j,letter,actual,expected)
                    assert actual>=0
                stats['numeric_cells_checked']+=1
            if kind!='MT' and r['travel_mm'] is not None:assert abs(r['travel_mm']-(r['l_max_mm']-r['l_min_mm']))<1e-9
        errors=[ref for ref,c in cells.items() if c.attrib.get('t')=='e' or value(c)=='HYPERLINK is not implemented']
        assert not errors,(kind,errors[:10])
        pane=root.find('.//s:pane',NS);assert pane is not None and pane.attrib.get('xSplit')=='3' and pane.attrib.get('ySplit')=='1'
        table=ET.fromstring(z.read(f'xl/tables/table{i}.xml'));assert table.find('s:autoFilter',NS) is not None
        stats['rows'][kind]={'parts':len(rows),'detail_pages':sum(r['detail_fetched'] for r in rows),'formula_errors':len(errors),'filter':True,'frozen_header_rows':1,'frozen_identifier_columns':3}
stats['catalogue_rows']=len(data['rows'])
stats['source_counts_reconciled']=all(c['expected']==c['captured'] for c in data['coverage'])
stats['missing_detail_parts']=[r['part_number'] for r in data['rows'] if not r['detail_fetched']]
stats['screening_status_counts']=dict(collections.Counter(r['selection_status'] for r in data['rows']))
stats['force_rating_review_rows']=sum(abs(r['force_rating_difference_pct'])>10 for r in data['rows'] if r['force_rating_difference_pct'] is not None)
stats['workbook_sha256']=hashlib.sha256(book.read_bytes()).hexdigest()
stats['native_excel_ui_tested']=False
out.write_text(json.dumps(stats,indent=2),encoding='utf-8');print(json.dumps(stats,indent=2))
