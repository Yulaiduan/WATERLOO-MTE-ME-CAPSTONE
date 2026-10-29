"""Add native part hyperlinks missing from the spreadsheet authoring API.

Run: python finalize_workbook.py WORKBOOK PAYLOAD
Inputs: artifact-tool XLSX and normalized catalogue JSON (mm/N/deg units).
Output: the same XLSX with native external hyperlinks in column C; link counts
and combined row/column freeze panes verified. No values or formulas changed.
Limit: only supplier hyperlink relationships are added; no Excel UI automation.
"""
import json,sys,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

MAIN='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
ET.register_namespace('',MAIN);ET.register_namespace('r',REL)
book=Path(sys.argv[1]);payload=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
with zipfile.ZipFile(book) as z:entries={name:z.read(name) for name in z.namelist()}
counts={}
for i,kind in enumerate(['MC','ME','MT'],1):
    name=f'xl/worksheets/sheet{i}.xml';root=ET.fromstring(entries[name]);rows=[r for r in payload['rows'] if r['type']==kind]
    rname=f'xl/worksheets/_rels/sheet{i}.xml.rels'
    rels=ET.fromstring(entries[rname]) if rname in entries else ET.Element('{'+PKG+'}Relationships')
    existing={r.attrib.get('Id') for r in rels};links=ET.Element('{'+MAIN+'}hyperlinks')
    for row,r in enumerate(rows,2):
        rid=f'mmcPart{row}'
        assert rid not in existing
        ET.SubElement(rels,'{'+PKG+'}Relationship',Id=rid,Type=REL+'/hyperlink',Target=r['part_url'],TargetMode='External')
        ET.SubElement(links,'{'+MAIN+'}hyperlink',{'ref':f'C{row}','{'+REL+'}id':rid,'display':'Open McMaster part'})
    # hyperlinks follows conditionalFormatting / dataValidations and precedes print elements.
    after_tags={'sheetPr','dimension','sheetViews','sheetFormatPr','cols','sheetData','sheetCalcPr','sheetProtection','protectedRanges','scenarios','autoFilter','sortState','dataConsolidate','customSheetViews','mergeCells','phoneticPr','conditionalFormatting','dataValidations'}
    insert=0
    for j,e in enumerate(root):
        if e.tag.rsplit('}',1)[-1] in after_tags:insert=j+1
    root.insert(insert,links)
    pane=root.find('.//{'+MAIN+'}pane')
    assert pane is not None and pane.attrib.get('xSplit')=='3' and pane.attrib.get('ySplit')=='1',(kind,None if pane is None else pane.attrib)
    entries[name]=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    entries[rname]=ET.tostring(rels,encoding='utf-8',xml_declaration=True)
    counts[kind]=len(links)
temporary=book.with_suffix('.hyperlinks.tmp')
with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for name,blob in entries.items():z.writestr(name,blob)
temporary.replace(book)
print(json.dumps({'native_hyperlinks':counts,'frozen_identifiers_and_header':True}))
