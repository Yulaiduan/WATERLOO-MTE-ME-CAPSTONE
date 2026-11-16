"""Append artifact-authored supplier sheets without round-tripping original tabs.

Run: python scripts/merge_supplier_tabs.py WORKDIR
Inputs: original.xlsx, supplier-tabs.xlsx, columns.json, normalized supplier JSON.
Output: expanded.xlsx and preservation-validation.json in WORKDIR. Uses stdlib;
all original sheet XML, cached values, formulas and native links stay byte-identical.
Only global package registries and appended styles are extended. New supplier
links and combined frozen panes are native XLSX features. No source is overwritten.
"""
import copy,hashlib,io,json,pathlib,re,sys,xml.etree.ElementTree as E,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1];M='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';P='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types'
E.register_namespace('',M);E.register_namespace('r',R)
def q(t):return '{'+M+'}'+t
NAMESPACES={}
def xml(t):
 E.register_namespace('',t.tag.split('}')[0][1:]);E.register_namespace('r',R)
 text=E.tostring(t,encoding='utf-8',xml_declaration=True).decode('utf8')
 start=text.index('<',text.index('?>')+2);end=text.index('>',start)
 for prefix,uri in NAMESPACES.items():
  if prefix and ('xmlns:'+prefix+'=') not in text[start:end]:
   text=text[:end]+' xmlns:'+prefix+'="'+uri+'"'+text[end:];end=text.index('>',start)
 return text.encode('utf8')
def readzip(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def col(i):
 s=''
 while i:i,j=divmod(i-1,26);s=chr(65+j)+s
 return s

def main():
 work=pathlib.Path(sys.argv[1]);old=readzip(work/'original.xlsx');new=readzip(work/'supplier-tabs.xlsx');out=dict(old)
 for payload in list(old.values())+list(new.values()):
  if not payload.lstrip().startswith(b'<'):continue
  try:
   for _,(prefix,uri) in E.iterparse(io.BytesIO(payload),events=['start-ns']):
    if prefix and not re.fullmatch(r'ns\d+',prefix):NAMESPACES[prefix]=uri;E.register_namespace(prefix,uri)
  except E.ParseError:pass
 data=json.loads((ROOT/'data/additional-springs.json').read_text(encoding='utf8'));columns=json.loads((work/'columns.json').read_text());base_styles=E.fromstring(old['xl/styles.xml']);new_styles=E.fromstring(new['xl/styles.xml']);maps={}
 for tag in ['fonts','fills','borders']:
  a=base_styles.find(q(tag));b=new_styles.find(q(tag));offset=len(a);maps[tag]={i:i+offset for i in range(len(b))}
  for node in b:a.append(copy.deepcopy(node))
  a.set('count',str(len(a)))
 oldnum=base_styles.find(q('numFmts'));newnum=new_styles.find(q('numFmts'));num_map={};highest=max([163]+[int(n.get('numFmtId')) for n in oldnum] if oldnum is not None else [163])
 if newnum is not None:
  if oldnum is None:oldnum=E.Element(q('numFmts'));base_styles.insert(0,oldnum)
  for node in newnum:
   highest+=1;x=copy.deepcopy(node);num_map[int(x.get('numFmtId'))]=highest;x.set('numFmtId',str(highest));oldnum.append(x)
  oldnum.set('count',str(len(oldnum)))
 ax=base_styles.find(q('cellXfs'));offset=len(ax)
 for node in new_styles.find(q('cellXfs')):
  x=copy.deepcopy(node)
  for attr,group in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:
   if attr in x.attrib:x.set(attr,str(maps[group][int(x.get(attr))]))
  if int(x.get('numFmtId','0')) in num_map:x.set('numFmtId',str(num_map[int(x.get('numFmtId'))]))
  if 'xfId' in x.attrib:x.set('xfId','0')
  ax.append(x)
 ax.set('count',str(len(ax)));out['xl/styles.xml']=xml(base_styles)
 wb=E.fromstring(old['xl/workbook.xml']);rels=E.fromstring(old['xl/_rels/workbook.xml.rels']);cts=E.fromstring(old['[Content_Types].xml']);sheets=wb.find(q('sheets'));
 assert not {'ST','BT','MI','SW'} & {s.get('name') for s in sheets},'Use a pre-expansion original.xlsx; supplier tabs already exist.'
 next_sheet=max(int(s.get('sheetId')) for s in sheets)+1;next_rel=max([int(re.sub(r'\D','',n.get('Id'))) for n in rels if re.sub(r'\D','',n.get('Id'))]or[0])+1
 table_id=max([int(re.search(r'table(\d+)\.xml',n)[1]) for n in old if re.fullmatch(r'xl/tables/table\d+\.xml',n)]or[0])+1
 ss=[]
 if 'xl/sharedStrings.xml' in new:ss=list(E.fromstring(new['xl/sharedStrings.xml']))
 newwb=E.fromstring(new['xl/workbook.xml']);nr={x.get('Id'):x.get('Target') for x in E.fromstring(new['xl/_rels/workbook.xml.rels'])};link_count=0
 for index,sh in enumerate(newwb.find(q('sheets'))):
  name=sh.get('name');target=nr[sh.get('{'+R+'}id')];source=target.lstrip('/') if target.startswith('/') else 'xl/'+target
  sheet=E.fromstring(new[source]);number=next_sheet+index;dest=f'xl/worksheets/sheet{number}.xml'
  for c in sheet.findall('.//'+q('c')):
   if 's' in c.attrib:c.set('s',str(int(c.get('s'))+offset))
   if c.get('t')=='s':
    v=c.find(q('v'));si=copy.deepcopy(ss[int(v.text)]);si.tag=q('is');c.remove(v);c.append(si);c.set('t','inlineStr')
  for view in sheet.findall(q('sheetViews')+'/'+q('sheetView')):
   for pane in view.findall(q('pane')):view.remove(pane)
   for selection in view.findall(q('selection')):view.remove(selection)
   view.insert(0,E.Element(q('pane'),{'xSplit':'3','ySplit':'1','topLeftCell':'D2','activePane':'bottomRight','state':'frozen'}));view.append(E.Element(q('selection'),{'pane':'bottomRight','activeCell':'D2','sqref':'D2'}))
  destrels=E.Element('{'+P+'}Relationships');source_rels=str(pathlib.PurePosixPath(source).parent/'_rels'/(pathlib.PurePosixPath(source).name+'.rels'))
  if source_rels in new:
   for rel in E.fromstring(new[source_rels]):
    if rel.get('Type').endswith('/table'):
     oldpath='xl/tables/'+pathlib.PurePosixPath(rel.get('Target')).name;table=E.fromstring(new[oldpath]);table.set('id',str(table_id));newpath=f'xl/tables/table{table_id}.xml';out[newpath]=xml(table);rel.set('Target',f'../tables/table{table_id}.xml');cts.append(E.Element('{'+CT+'}Override',{'PartName':'/'+newpath,'ContentType':'application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml'}));table_id+=1
    else:raise ValueError('Unexpected new sheet relationship '+str(rel.attrib))
    destrels.append(copy.deepcopy(rel))
  links=E.Element(q('hyperlinks'));used_ids={r.get('Id') for r in destrels};ri=1
  rows=[r for r in data['rows'] if r['source']==name]
  for i,row in enumerate(rows,2):
   for key in ['part_url','source_catalogue_url','drawing_url']:
    url=row.get(key)
    if not url:continue
    while 'rId'+str(ri) in used_ids:ri+=1
    rid='rId'+str(ri);used_ids.add(rid);ri+=1;ci=next(j+1 for j,d in enumerate(columns) if d['key']==key)
    links.append(E.Element(q('hyperlink'),{'ref':col(ci)+str(i),'{'+R+'}id':rid}));destrels.append(E.Element('{'+P+'}Relationship',{'Id':rid,'Type':R+'/hyperlink','Target':url,'TargetMode':'External'}));link_count+=1
  first=next((i for i,n in enumerate(sheet) if n.tag in [q(x) for x in ['printOptions','pageMargins','pageSetup','headerFooter','drawing','tableParts','extLst']]),len(sheet));sheet.insert(first,links)
  out[dest]=xml(sheet);out[f'xl/worksheets/_rels/sheet{number}.xml.rels']=xml(destrels)
  rid='rId'+str(next_rel+index);sheets.append(E.Element(q('sheet'),{'name':name,'sheetId':str(number),'{'+R+'}id':rid}));rels.append(E.Element('{'+P+'}Relationship',{'Id':rid,'Type':R+'/worksheet','Target':'worksheets/sheet'+str(number)+'.xml'}));cts.append(E.Element('{'+CT+'}Override',{'PartName':'/'+dest,'ContentType':'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml'}))
 out['xl/workbook.xml']=xml(wb);out['xl/_rels/workbook.xml.rels']=xml(rels);out['[Content_Types].xml']=xml(cts)
 # The source package has no chart or drawing additions. Original parts remain untouched.
 allowed={'xl/styles.xml','xl/workbook.xml','xl/_rels/workbook.xml.rels','[Content_Types].xml'}
 changed=[n for n in old if old[n]!=out[n]];assert set(changed)<=allowed
 for n,b in out.items():
  if n.endswith('.xml') or n.endswith('.rels'):E.fromstring(b)
 errors=[];energies={}
 for name in ['ST','BT','MI','SW']:
  idx=next(int(s.get('sheetId')) for s in sheets if s.get('name')==name);sheet=E.fromstring(out[f'xl/worksheets/sheet{idx}.xml']);rs=sheet.findall(q('sheetData')+'/'+q('row'));energies[name]=len(rs)-1
  assert len(rs)-1==data['counts'][name]
  records=[r for r in data['rows'] if r['source']==name]
  for row,record in zip(rs[1:],records):
   for c in row:
    if c.get('t')=='e':errors.append((name,c.get('r')))
    if c.get('r')=='D'+row.get('r'):
     value=float(c.find(q('v')).text);assert abs(value-record['energy_J'])<1e-7*max(1,value) and value>=60-1e-9
 assert not errors
 with zipfile.ZipFile(work/'expanded.xlsx','w',zipfile.ZIP_DEFLATED) as z:
  for n,b in out.items():z.writestr(n,b)
 result={'original_sha256':hashlib.sha256((work/'original.xlsx').read_bytes()).hexdigest(),'expanded_sha256':hashlib.sha256((work/'expanded.xlsx').read_bytes()).hexdigest(),'new_rows':energies,'new_native_links':link_count,'original_package_parts_preserved_byte_identical':len(old)-len(changed),'original_package_parts_extended':changed,'original_sheet_XML_and_native_links':'byte-identical','formula_errors':errors,'energy_rows_checked':sum(energies.values())}
 (work/'preservation-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
