"""Local VSL V5 UI and explicit XLSX configuration-library bridge (Python 3.10+).

Run: python vsl_server.py [--open] [--port 8768]. Bind:127.0.0.1 only.
Inputs: app-local XLSX or a user-selected local .xlsx path; mm/deg/kg/N/Nm.
Outputs: same-origin browser UI, atomic library saves, one recoverable backup.
Uses Python standard library only. Supports VSL libraries, not arbitrary Excel
models/macros. Never evaluates formulas; refuses a foreign workbook overwrite.
"""
from __future__ import annotations
import argparse,copy,datetime as dt,hashlib,http.server,json,math,os,pathlib,shutil,subprocess,sys,tempfile,threading,urllib.parse,urllib.request,webbrowser,xml.etree.ElementTree as ET,zipfile

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parent
DEFAULT_BOOK=HERE/'v5-configs.xlsx'
SCHEMA='vsl-config-library/v1'
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
X=lambda name:f'{{{NS}}}{name}'
COLORS={'none':'FFFFFF','butter':'FFF5CC','peach':'FFE7D2','rose':'FCE2E9','lavender':'ECE5FC','blue':'DFF0FC','mint':'DDF3E5','sand':'F0EADE'}
COLUMNS=json.loads((HERE/'config-library-columns.json').read_text(encoding='utf-8'))
EPOCH=dt.datetime(1899,12,30,tzinfo=dt.timezone.utc)
ET.register_namespace('',NS)
ET.register_namespace('r',REL)

class LibraryError(ValueError):
    def __init__(self,message,status=400):super().__init__(message);self.status=status

def file_path(value):
    value=(value or str(DEFAULT_BOOK)).strip()
    if value.startswith('file:'):
        parsed=urllib.parse.urlparse(value);value=urllib.request.url2pathname(parsed.path)
        if parsed.netloc:value='//'+parsed.netloc+value
    if '://' in value:raise LibraryError('Use a local .xlsx file path. Web links to Excel/SharePoint are not local files.')
    path=pathlib.Path(value).expanduser()
    if not path.is_absolute():raise LibraryError('Enter an absolute local path, or use Browse.')
    path=path.resolve()
    if path.suffix.lower()!='.xlsx':raise LibraryError('Select an .xlsx workbook.')
    return path

def revision(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def get_at(obj,path):
    for key in path.split('.'):
        if not isinstance(obj,dict):return None
        obj=obj.get(key)
    return obj
def put_at(obj,path,value):
    keys=path.split('.')
    for key in keys[:-1]:obj=obj.setdefault(key,{})
    obj[keys[-1]]=value
def close(a,b):return isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and abs(a-b)<=1e-10*max(1,abs(a),abs(b)) or a==b
def weight(p):return sum(p[k] for k in ('m1','m2','m3','m5','m6'))

def validate_document(doc):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA or not isinstance(doc.get('rows'),list) or len(doc['rows'])>2000:raise LibraryError('Not a VSL library, or more than 2000 design points.')
    seen=set()
    for row in doc['rows']:
        dp=row.get('dp')
        if isinstance(dp,bool) or not isinstance(dp,int) or dp<1 or dp in seen:raise LibraryError('DP# must be unique positive whole numbers.')
        seen.add(dp)
        if not isinstance(row.get('name'),str) or len(row['name'])>160:raise LibraryError(f'DP {dp}: name must have at most 160 characters.')
        if row.get('color','none') not in COLORS:raise LibraryError(f'DP {dp}: unknown row color.')
        snapshot=row.get('snapshot')
        if snapshot is not None:
            if snapshot.get('schema') not in ('general-vsl/v4-pulley','general-vsl/v5-fall') or not isinstance(snapshot.get('parameters'),dict):raise LibraryError(f'DP {dp}: invalid solver snapshot.')
            for key,value in snapshot['parameters'].items():
                if isinstance(value,(int,float)) and not math.isfinite(value):raise LibraryError(f'DP {dp}: {key} is not finite.')
            if len(json.dumps(snapshot,ensure_ascii=False))>30000:raise LibraryError(f'DP {dp}: saved design is too large for an Excel cell.')
        if row.get('savedAt') is not None:
            try:dt.datetime.fromisoformat(row['savedAt'].replace('Z','+00:00'))
            except (ValueError,TypeError):raise LibraryError(f'DP {dp}: invalid saved time.')
    if doc.get('loadedDp') not in seen:doc['loadedDp']=None
    return doc

def cell_value(row,column):
    key=column['key'];snapshot=row.get('snapshot');p=snapshot.get('parameters') if snapshot else None
    if key=='springDriven':
        if not snapshot:return None
        defaults=dict(springK=True,hornR=False,Sv=True,rs=True,p0=False,nu=True,Su=False)
        choices={**defaults,**snapshot.get('springDriving',{})};labels=dict(springK='k',hornR='r_h',Sv='S_v',rs='r_s',p0='p0',nu='nu',Su='S_u')
        return ', '.join(labels[k] for k in defaults if not choices[k])
    if column.get('path'):return get_at(snapshot,column['path']) if snapshot else None
    if key in ('save','load'):return 'Use VSL'
    if key=='totalMass':return weight(p) if p else None
    if key in ('qab','qdc','qfe'):
        a,b={'qab':('ra','rb'),'qdc':('rd','rc'),'qfe':('rf','re')}[key]
        return p[a]/p[b] if p else None
    return row.get(key)

def column_name(number):
    out=''
    while number:number,i=divmod(number-1,26);out=chr(65+i)+out
    return out

def xml_bytes(node):return ET.tostring(node,encoding='utf-8',xml_declaration=True)

def read_grid(data,strings):
    root=ET.fromstring(data);out=[]
    for row in root.findall('m:sheetData/m:row',{'m':NS}):
        cells={}
        for cell in row.findall(X('c')):
            key=''.join(c for c in cell.attrib['r'] if c.isalpha());typ=cell.get('t');v=cell.find(X('v'))
            if typ=='inlineStr':value=''.join(cell.itertext())
            elif v is None:value=None
            elif typ=='s':value=strings[int(v.text)]
            elif typ=='b':value=v.text=='1'
            elif typ in ('str','d','e'):value=v.text
            else:
                try:value=float(v.text);value=int(value) if value.is_integer() else value
                except (ValueError,TypeError):value=v.text
            cells[key]=value
        out.append((int(row.attrib['r']),cells))
    return out

def unpack_book(path):
    if path.stat().st_size>25_000_000:raise LibraryError('Workbook exceeds the 25 MB library limit.')
    try:
        with zipfile.ZipFile(path) as archive:
            if sum(i.file_size for i in archive.infolist())>100_000_000:raise LibraryError('Workbook expands beyond the library size limit.')
            files={n:archive.read(n) for n in archive.namelist()}
    except (zipfile.BadZipFile,OSError) as e:raise LibraryError('Could not read this .xlsx workbook: '+str(e))
    strings=[]
    if 'xl/sharedStrings.xml' in files:
        for item in ET.fromstring(files['xl/sharedStrings.xml']).findall(X('si')):strings.append(''.join(item.itertext()))
    rels={node.get('Id'):node.get('Target') for node in ET.fromstring(files['xl/_rels/workbook.xml.rels'])}
    sheets={}
    for sheet in ET.fromstring(files['xl/workbook.xml']).findall(X('sheets')+'/'+X('sheet')):
        target=rels[sheet.get('{'+REL+'}id')];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        sheets[sheet.get('name')]=str(pathlib.PurePosixPath(target))
    if 'Designs' not in sheets or 'VSL state' not in sheets:raise LibraryError('This workbook is not a VSL config library. Choose v5-configs.xlsx, or save to a new .xlsx filename.')
    return files,sheets,strings

def load_library(path):
    if not path.exists():raise LibraryError('Workbook does not exist. Use Save Excel to create a new VSL library at this path.',404)
    files,sheets,strings=unpack_book(path)
    state_grid=read_grid(files[sheets['VSL state']],strings);meta={cells.get('A'):cells.get('B') for _,cells in state_grid if cells.get('A')}
    if meta.get('schema')!=SCHEMA:raise LibraryError('Unsupported VSL library schema.')
    grid=read_grid(files[sheets['Designs']],strings)
    if not grid:raise LibraryError('Designs sheet has no header.')
    headers=grid[0][1];positions={value:key for key,value in headers.items()};required=['DP#','Name']
    if any(k not in positions for k in required):raise LibraryError('Keep the DP# and Name column headers in the Designs sheet.')
    doc={'schema':SCHEMA,'rows':[],'loadedDp':int(meta['loadedDp']) if meta.get('loadedDp') not in (None,'') else None}
    default=json.loads((HERE/'v5-default-library.json').read_text(encoding='utf-8'))['rows'][0]['snapshot']
    for index,cells in grid[1:]:
        dp=cells.get(positions['DP#'])
        if dp is None:continue
        if isinstance(dp,bool) or not isinstance(dp,(int,float)) or int(dp)!=dp:raise LibraryError(f'Excel row {index}: DP# must be a positive whole number.')
        dp=int(dp)
        try:original=json.loads(meta.get('DP:'+str(dp),'null'))
        except (ValueError,TypeError):raise LibraryError(f'DP {dp}: invalid app state JSON.')
        row=copy.deepcopy(original) if original else {'dp':dp,'name':'Design '+str(dp),'savedAt':None,'color':'none','snapshot':None}
        row['dp']=dp;row['name']=str(cells.get(positions['Name']) or 'Design '+str(dp))
        parameter_present=any((c.get('path') or '').startswith('parameters.') and cells.get(positions.get(c['label'])) is not None for c in COLUMNS)
        if row['snapshot'] is None and parameter_present:row['snapshot']=copy.deepcopy(default)
        original_values={c['key']:cell_value(row,c) for c in COLUMNS};changes={}
        for c in COLUMNS:
            if c['label'] not in positions:continue
            value=cells.get(positions[c['label']]);key=c['key']
            if value is None:continue
            if c['type']=='boolean':
                if isinstance(value,str):
                    if value.lower() not in ('true','false','yes','no','1','0'):raise LibraryError(f'DP {dp}: {c["label"]} needs TRUE or FALSE.')
                    value=value.lower() in ('true','yes','1')
                else:value=bool(value)
            elif c['type']=='number':
                if not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value):raise LibraryError(f'DP {dp}: {c["label"]} needs a finite number.')
            elif c['type']=='date':
                if isinstance(value,(int,float)):value=(EPOCH+dt.timedelta(days=value)).isoformat().replace('+00:00','Z')
            if key in ('name','dp','save','load'):continue
            if key in ('savedAt','color'):row[key]=value;continue
            if row['snapshot'] is not None and not close(value,original_values[key]):changes[key]=value
            if c.get('path') and row['snapshot'] is not None:put_at(row['snapshot'],c['path'],value)
        if row['snapshot']:
            p=row['snapshot']['parameters']
            if 'totalMass' in changes:
                p['m1']=changes['totalMass']-sum(p[k] for k in ('m2','m3','m5','m6'))
                if p['m1']<0:raise LibraryError(f'DP {dp}: total mass is less than the entered moving masses.')
            for key,a,b in [('qab','ra','rb'),('qdc','rd','rc'),('qfe','rf','re')]:
                if key in changes:
                    if changes[key]<=0:raise LibraryError(f'DP {dp}: {key} must be positive.')
                    if a in changes or b in changes:
                        if not close(p[a]/p[b],changes[key]):raise LibraryError(f'DP {dp}: edited {key} disagrees with the edited pulley radii.')
                    else:p[a]=changes[key]*p[b]
            if original and original.get('snapshot'):
                old=original['snapshot']['parameters'];before=weight(old)*old['g'];after=weight(p)*p['g']
                if before>0 and before!=after and old['loadMode']==p['loadMode']:
                    for key in (('Fy','Fz') if p['loadMode']=='yz' else ('Fn','Ft')):
                        if key not in changes:p[key]=old[key]*after/before
            if any(key not in ('color','savedAt') for key in changes):row['outputsStale']=True
        doc['rows'].append(row)
    return validate_document(doc)

def styles_xml():
    root=ET.Element(X('styleSheet'))
    formats=ET.SubElement(root,X('numFmts'),count='2')
    ET.SubElement(formats,X('numFmt'),numFmtId='164',formatCode='0.000')
    ET.SubElement(formats,X('numFmt'),numFmtId='165',formatCode='yyyy-mm-dd hh:mm:ss')
    fonts=ET.SubElement(root,X('fonts'),count='2')
    for header in (False,True):
        font=ET.SubElement(fonts,X('font'));ET.SubElement(font,X('sz'),val='10');ET.SubElement(font,X('name'),val='Arial');ET.SubElement(font,X('color'),rgb='FFFFFFFF' if header else 'FF182F3D')
        if header:ET.SubElement(font,X('b'))
    fills=ET.SubElement(root,X('fills'),count=str(3+len(COLORS)))
    for pattern in ('none','gray125'):ET.SubElement(ET.SubElement(fills,X('fill')),X('patternFill'),patternType=pattern)
    for color in ['344F60',*COLORS.values()]:
        fill=ET.SubElement(ET.SubElement(fills,X('fill')),X('patternFill'),patternType='solid');ET.SubElement(fill,X('fgColor'),rgb='FF'+color);ET.SubElement(fill,X('bgColor'),indexed='64')
    borders=ET.SubElement(root,X('borders'),count='1');border=ET.SubElement(borders,X('border'))
    for edge in ('left','right','top','bottom','diagonal'):ET.SubElement(border,X(edge))
    base=ET.SubElement(root,X('cellStyleXfs'),count='1');ET.SubElement(base,X('xf'),numFmtId='0',fontId='0',fillId='0',borderId='0')
    xfs=ET.SubElement(root,X('cellXfs'),count=str(2+3*len(COLORS)))
    ET.SubElement(xfs,X('xf'),numFmtId='0',fontId='0',fillId='0',borderId='0',xfId='0')
    xf=ET.SubElement(xfs,X('xf'),numFmtId='0',fontId='1',fillId='2',borderId='0',xfId='0',applyAlignment='1');ET.SubElement(xf,X('alignment'),vertical='center',wrapText='1')
    for index in range(len(COLORS)):
        for fmt in ('0','164','165'):
            xf=ET.SubElement(xfs,X('xf'),numFmtId=fmt,fontId='0',fillId=str(3+index),borderId='0',xfId='0',applyNumberFormat='1',applyAlignment='1');ET.SubElement(xf,X('alignment'),vertical='center',horizontal='left' if fmt=='0' else 'right')
    cell_styles=ET.SubElement(root,X('cellStyles'),count='1');ET.SubElement(cell_styles,X('cellStyle'),name='Normal',xfId='0',builtinId='0')
    return xml_bytes(root)

def make_sheet(matrix,date_columns=(),row_colors=None,widths=None,freeze=False,table_rel=False,state=False):
    root=ET.Element(X('worksheet'));ET.SubElement(root,X('dimension'),ref=f'A1:{column_name(max(map(len,matrix)))}{len(matrix)}')
    views=ET.SubElement(root,X('sheetViews'));view=ET.SubElement(views,X('sheetView'),workbookViewId='0',showGridLines='0')
    if freeze:ET.SubElement(view,X('pane'),xSplit='5',ySplit='1',topLeftCell='F2',activePane='bottomRight',state='frozen')
    ET.SubElement(root,X('sheetFormatPr'),defaultRowHeight='22');cols=ET.SubElement(root,X('cols'))
    for i in range(max(map(len,matrix))):ET.SubElement(cols,X('col'),min=str(i+1),max=str(i+1),width=str((widths or {}).get(i,16)),customWidth='1')
    data=ET.SubElement(root,X('sheetData'))
    for i,values in enumerate(matrix):
        row=ET.SubElement(data,X('row'),r=str(i+1),ht=str(32 if i==0 else 24),customHeight='1')
        color=(row_colors or {}).get(i,'none');base=2+3*list(COLORS).index(color)
        for j,value in enumerate(values):
            if value is None:continue
            typ='number' if isinstance(value,(int,float)) and not isinstance(value,bool) else 'string'
            style=1 if i==0 else base+(2 if j in date_columns else 1 if typ=='number' else 0)
            c=ET.SubElement(row,X('c'),r=f'{column_name(j+1)}{i+1}',s=str(style))
            if j in date_columns and i>0 and isinstance(value,str):value=(dt.datetime.fromisoformat(value.replace('Z','+00:00'))-EPOCH).total_seconds()/86400;typ='number'
            if isinstance(value,bool):c.set('t','b');ET.SubElement(c,X('v')).text='1' if value else '0'
            elif typ=='number':ET.SubElement(c,X('v')).text=repr(value)
            else:
                c.set('t','inlineStr');text=ET.SubElement(ET.SubElement(c,X('is')),X('t'));text.text=str(value);text.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    if freeze:ET.SubElement(root,X('autoFilter'),ref=f'A1:{column_name(len(matrix[0]))}{len(matrix)}')
    if table_rel:
        parts=ET.SubElement(root,X('tableParts'),count='1');ET.SubElement(parts,X('tablePart'),{'{'+REL+'}id':'rId1'})
    return xml_bytes(root)

LIBRARY_LOCK=threading.RLock()

def write_library(path,doc,expected_revision):
    with LIBRARY_LOCK:return _write_library(path,doc,expected_revision)

def _write_library(path,doc,expected_revision):
    validate_document(doc);current=revision(path)
    if current!=expected_revision:raise LibraryError('The workbook changed since it was loaded, or this path has not been loaded. Load Excel first, then save again.',409)
    template=path if path.exists() else DEFAULT_BOOK
    files,sheets,_=unpack_book(template)
    # Refuse other spreadsheets even when a guessed revision is supplied.
    if path.exists():load_library(path)
    main=[[c['label'] for c in COLUMNS]]+[[cell_value(row,c) for c in COLUMNS] for row in doc['rows']]
    meta=[['Key','Value'],['schema',SCHEMA],['loadedDp',doc.get('loadedDp')]]+[['DP:'+str(row['dp']),json.dumps(row,ensure_ascii=False,separators=(',',':'))] for row in doc['rows']]
    files[sheets['Designs']]=make_sheet(main,date_columns=[4],row_colors={i+1:row.get('color','none') for i,row in enumerate(doc['rows'])},widths={0:8,1:28,2:10,3:10,4:23},freeze=True)
    files[sheets['VSL state']]=make_sheet(meta,widths={0:22,1:110},state=True)
    files['xl/styles.xml']=styles_xml()
    # Retire only this app's generated table relationship; the flat sheet has its own filter.
    for sheet_name in sheets.values():
        relpath=str(pathlib.PurePosixPath(sheet_name).parent/'_rels'/(pathlib.PurePosixPath(sheet_name).name+'.rels'))
        if relpath in files:
            relationships=ET.fromstring(files[relpath]);kept=[x for x in relationships if not x.get('Type','').endswith('/table')]
            if len(kept)!=len(relationships):
                for node in list(relationships):
                    if node not in kept:relationships.remove(node)
                files[relpath]=ET.tostring(relationships,encoding='utf-8',xml_declaration=True)
    if not path.parent.is_dir():raise LibraryError('The workbook folder does not exist.')
    temporary=None
    try:
        fd,temporary=tempfile.mkstemp(prefix='.vsl-',suffix='.xlsx',dir=path.parent);os.close(fd)
        with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,data in files.items():archive.writestr(name,data)
        if path.exists():shutil.copy2(path,path.with_name(path.stem+'.vsl-backup.xlsx'))
        os.replace(temporary,path);temporary=None
    except PermissionError:raise LibraryError('Excel has locked the workbook. Close it in Excel, then press Save Excel again. Your library edits are still in the browser.',423)
    finally:
        if temporary and pathlib.Path(temporary).exists():pathlib.Path(temporary).unlink()
    return revision(path)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,format,*args):pass
    def reply(self,data,status=200):
        raw=json.dumps(data,ensure_ascii=False,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def trusted(self):
        origin=self.headers.get('Origin');allowed={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}
        if self.headers.get('X-VSL-Client')!='config-library' or origin and origin not in allowed:raise LibraryError('This local operation must originate in the VSL calculator.',403)
    def do_GET(self):
        url=urllib.parse.urlparse(self.path)
        if url.path=='/api/health':return self.reply({'app':'vsl-solver-v5','root':str(ROOT)})
        if url.path=='/api/bootstrap':
            try:self.trusted();return self.reply({'defaultPath':str(DEFAULT_BOOK)})
            except LibraryError as e:return self.reply({'error':str(e)},e.status)
        if url.path.startswith('/api/'):return self.reply({'error':'Unknown operation.'},404)
        return super().do_GET()
    def do_POST(self):
        try:
            self.trusted();length=int(self.headers.get('Content-Length','0'))
            if length<=0 or length>20_000_000:raise LibraryError('Library request is too large or empty.')
            body=json.loads(self.rfile.read(length));path=file_path(body.get('path'))
            if self.path=='/api/library/load':return self.reply({'document':load_library(path),'path':str(path),'revision':revision(path)})
            if self.path=='/api/library/save':return self.reply({'path':str(path),'revision':write_library(path,body.get('document'),body.get('expectedRevision'))})
            if self.path=='/api/library/browse':
                proc=subprocess.run([sys.executable,str(HERE/'vsl_server.py'),'--pick-workbook',str(path)],capture_output=True,text=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                if proc.returncode:raise LibraryError('The file picker is unavailable. Paste the full local .xlsx path instead.')
                return self.reply({'path':proc.stdout.strip() or None})
            raise LibraryError('Unknown operation.',404)
        except LibraryError as e:self.reply({'error':str(e)},e.status)
        except (ValueError,TypeError,KeyError,ET.ParseError,zipfile.BadZipFile) as e:self.reply({'error':'Invalid workbook or library: '+str(e)},400)
        except Exception as e:self.reply({'error':'Could not complete the Excel operation: '+str(e)},500)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8768);parser.add_argument('--open',action='store_true');parser.add_argument('--pick-workbook');args=parser.parse_args()
    if args.pick_workbook:
        import tkinter as tk
        from tkinter import filedialog
        root=tk.Tk();root.withdraw();selected=filedialog.askopenfilename(title='Choose a VSL configuration workbook',initialdir=str(pathlib.Path(args.pick_workbook).parent),filetypes=[('Excel workbook','*.xlsx')]);root.destroy();print(selected);return
    url=f'http://127.0.0.1:{args.port}/v5/v5-fall.html'
    # On Windows SO_REUSEADDR can permit a second live listener. Check first,
    # then bind exclusively; repeated launcher clicks reuse the same app.
    try:
        health=json.load(urllib.request.urlopen(f'http://127.0.0.1:{args.port}/api/health',timeout=1))
        if health.get('app')=='vsl-solver-v5' and pathlib.Path(health.get('root','')).resolve()==ROOT:
            if args.open and not os.environ.get('VSL_NO_BROWSER'):webbrowser.open(url)
            print('VSL is already running: '+url);return
    except Exception:pass
    class LocalServer(http.server.ThreadingHTTPServer):allow_reuse_address=False
    try:server=LocalServer(('127.0.0.1',args.port),Handler)
    except OSError:
        try:
            health=json.load(urllib.request.urlopen(f'http://127.0.0.1:{args.port}/api/health',timeout=2))
            if health.get('app')=='vsl-solver-v5' and pathlib.Path(health.get('root','')).resolve()==ROOT:
                if args.open and not os.environ.get('VSL_NO_BROWSER'):webbrowser.open(url)
                print('VSL is already running: '+url);return
        except Exception:pass
        raise SystemExit(f'Port {args.port} is occupied by another app. Close it or use --port with a free port.')
    print('VSL Solver: '+url,flush=True);print('Default Excel library: '+str(DEFAULT_BOOK),flush=True);print('Close this window or press Ctrl+C to stop.',flush=True)
    if args.open and not os.environ.get('VSL_NO_BROWSER'):threading.Timer(.3,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
