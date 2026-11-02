"""Atomic local solution workbook persistence; explicit API writes only."""
from __future__ import annotations
import copy,datetime,hashlib,json,os,pathlib,shutil,subprocess,tempfile,threading,xml.etree.ElementTree as ET,zipfile
import spring_lab
HERE=pathlib.Path(__file__).resolve().parent
BOOK=HERE.parent.parent/'springs'/'v6-spring-solutions.xlsx'
LOCK=threading.RLock();CATALOGUE=None;CATALOGUE_VERSION=None

def catalogue():
    global CATALOGUE,CATALOGUE_VERSION
    stat=spring_lab.CATALOGUE.stat();version=(stat.st_mtime_ns,stat.st_size)
    if CATALOGUE is None or CATALOGUE_VERSION!=version:CATALOGUE=spring_lab.read_catalogue();CATALOGUE_VERSION=version
    return CATALOGUE

def empty():return dict(schema='vsl-spring-solutions/v1',nextId=1,solutions=[],catalogueHash=hashlib.sha256(spring_lab.CATALOGUE.read_bytes()).hexdigest(),cataloguePath=str(spring_lab.CATALOGUE))

def read():
    if not BOOK.exists():return empty()
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};main=ns['m'];rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    with zipfile.ZipFile(BOOK) as z:
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        links={x.get('Id'):x.get('Target') for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))};sheets=ET.fromstring(z.read('xl/workbook.xml'))
        sheet=next(x for x in sheets.findall('m:sheets/m:sheet',ns) if x.get('name')=='VSL state');target=links[sheet.get('{'+rel+'}id')];name=target.lstrip('/') if target.startswith('/') else 'xl/'+target;meta={}
        for row in ET.fromstring(z.read(name)).findall('m:sheetData/m:row',ns):
            cells={}
            for c in row:
                v=c.find('m:v',ns);key=''.join(x for x in c.get('r','') if x.isalpha());cells[key]=''.join(c.find('m:is',ns).itertext()) if c.get('t')=='inlineStr' else ss[int(v.text)] if c.get('t')=='s' and v is not None else v.text if v is not None else ''
            if cells.get('A'):meta[cells['A']]=cells.get('B')
    if meta.get('schema')!='vsl-spring-solutions/v1':raise ValueError('Refusing to overwrite a foreign spring solution workbook.')
    return dict(schema=meta['schema'],nextId=int(float(meta['nextId'])),solutions=[json.loads(v) for k,v in meta.items() if k.startswith('S') and k[1:].isdigit()],catalogueHash=meta.get('catalogueHash',''),cataloguePath=str(spring_lab.CATALOGUE))

def writer(doc,path):
    bundled=pathlib.Path.home()/'.cache'/'codex-runtimes'/'codex-primary-runtime'/'dependencies'/'node'/'bin'/'node.exe'
    node=os.environ.get('VSL_NODE') or (str(bundled) if bundled.is_file() else shutil.which('node'))
    if not node:raise ValueError('Node.js with @oai/artifact-tool is required to save spring workbooks.')
    with tempfile.TemporaryDirectory(prefix='vsl-springs-') as folder:
        source=pathlib.Path(folder)/'input.json';source.write_text(json.dumps(doc,allow_nan=False),encoding='utf8')
        output=pathlib.Path(folder)/'output.xlsx'
        proc=subprocess.run([node,str(HERE/'write-spring-workbook.mjs'),str(source),str(output)],capture_output=True,text=True,timeout=90,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if proc.returncode:raise ValueError('Workbook writer failed: '+proc.stderr[-1500:])
        shutil.copyfile(output,path)

def write(doc):
    BOOK.parent.mkdir(parents=True,exist_ok=True);tmp=BOOK.with_name('.v6-spring-solutions.pending.xlsx')
    try:
        writer(doc,tmp)
        if BOOK.exists():shutil.copy2(BOOK,BOOK.with_name('v6-spring-solutions.backup.xlsx'))
        os.replace(tmp,BOOK)
    except PermissionError:raise ValueError('Excel has locked the solutions workbook. Close it in Excel and retry; no solutions were overwritten.')
    finally:
        if tmp.exists():tmp.unlink()

def canonical(record):
    r=copy.deepcopy(record);lookup={x['id']:x for x in catalogue() if x['eligible']};parts=[]
    spring_lab.normalized({'parameters':r['parameters'],'settings':{**r['settings'],**r['geometry'],'bulk':r['bulk'],'payloads':r['payloads']}})
    if not 1<=len(r['springs'])<=12 or not 1<=len(r['payloads'])<=8 or len(r['masks'])!=len(r['payloads']):raise ValueError('Invalid spring slots/cases.')
    if any(len(row)!=len(r['springs']) or any(x not in (0,1) for x in row) or not any(row) for row in r['masks']):raise ValueError('Each case must enable at least one spring.')
    for s in r['springs']:
        part=lookup.get(s['id'])
        if part is None or part['type']!=r['settings']['type']:raise ValueError('Part is not an eligible catalogue spring of the selected type.')
        parts.append({**part,'p0':float(s['p0'])})
    r['springs']=parts;r=spring_lab.evaluate(r);r['catalogueHash']=hashlib.sha256(spring_lab.CATALOGUE.read_bytes()).hexdigest()
    if not r['metrics']['valid']:raise ValueError(' '.join(r['metrics']['violations']))
    return r

def action(body):
    with LOCK:
        doc=read();op=body.get('action','list')
        if op=='add':
            rows=body.get('solutions',[])
            if not 1<=len(rows)<=50:raise ValueError('Save 1–50 valid solutions at a time.')
            added=[]
            for row in rows:
                r=canonical(row);r['id']='S'+str(doc['nextId']).zfill(4);doc['nextId']+=1;r['savedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();doc['solutions'].append(r);added.append(r['id'])
            doc['catalogueHash']=hashlib.sha256(spring_lab.CATALOGUE.read_bytes()).hexdigest();write(doc)
        elif op in ['delete','favorite']:
            r=next((x for x in doc['solutions'] if x['id']==body.get('id')),None)
            if r is None:raise ValueError('Unknown solution ID.')
            if op=='delete':doc['solutions'].remove(r)
            else:r['favorite']=bool(body.get('favorite'))
            write(doc);added=[]
        elif op=='list':added=[]
        else:raise ValueError('Unknown solution operation.')
        return dict(document=doc,added=added,path=str(BOOK))
