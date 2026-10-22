"""Test VSL XLSX save/load, edits, revision conflicts and immutable snapshots.

Run: python verify_excel.py. Inputs app workbook, mm/deg/kg/N/Nm. Outputs
unittest results. All mutations use temporary workbooks; no Excel install needed.
Does not certify the native Browse dialog or Excel desktop interoperability.
"""
import copy,pathlib,tempfile,unittest,zipfile,xml.etree.ElementTree as ET
import vsl_server as v

class ExcelTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.temp.name)/'test.xlsx';self.doc=v.load_library(v.DEFAULT_BOOK)
    def tearDown(self):self.temp.cleanup()
    def write(self):return v.write_library(self.path,self.doc,None)
    def edit(self,key,value):
        files,sheets,_=v.unpack_book(self.path);root=ET.fromstring(files[sheets['Designs']]);c=next(c for c in v.COLUMNS if c['key']==key);col=v.column_name(v.COLUMNS.index(c)+1);node=root.find(f'.//{v.X("c")}[@r="{col}2"]');node.attrib.pop('t',None)
        for child in list(node):node.remove(child)
        ET.SubElement(node,v.X('v')).text=str(value);files[sheets['Designs']]=v.xml_bytes(root)
        with zipfile.ZipFile(self.path,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,data in files.items():archive.writestr(name,data)
    def test_roundtrip(self):
        self.doc['rows'][0]['color']='rose';self.doc['loadedDp']=1;original=copy.deepcopy(self.doc);rev=self.write();result=v.load_library(self.path)
        self.assertEqual(result['rows'][0]['snapshot'],original['rows'][0]['snapshot']);self.assertFalse(result['rows'][0].get('outputsStale',False));self.assertEqual(result['loadedDp'],1);self.assertEqual(result['rows'][0]['color'],'rose')
        v.write_library(self.path,result,rev);self.assertTrue(self.path.with_name('test.vsl-backup.xlsx').exists())
    def test_order_and_unsaved(self):
        a=copy.deepcopy(self.doc['rows'][0]);a['dp']=7;self.doc['rows'].insert(0,a);self.doc['rows'].append(dict(dp=8,name='Unsaved',color='none',savedAt=None,snapshot=None));self.write();b=v.load_library(self.path);self.assertEqual([r['dp'] for r in b['rows']],[7,1,8]);self.assertIsNone(b['rows'][-1]['snapshot'])
    def test_conflict(self):
        rev=self.write();self.path.write_bytes(self.path.read_bytes()+b' ')
        with self.assertRaises(v.LibraryError) as ctx:v.write_library(self.path,self.doc,rev)
        self.assertEqual(ctx.exception.status,409)
    def test_excel_mass_edit(self):
        self.write();self.edit('totalMass',10);b=v.load_library(self.path);self.assertEqual(b['rows'][0]['snapshot']['parameters']['m1'],10);self.assertTrue(b['rows'][0]['outputsStale'])
    def test_excel_ratio_edit(self):
        self.write();self.edit('qdc',2);b=v.load_library(self.path)['rows'][0]['snapshot']['parameters'];self.assertEqual(b['rd'],2*b['rc'])
    def test_conflicting_radii(self):
        self.write();self.edit('qdc',2);self.edit('rd',80)
        with self.assertRaises(v.LibraryError):v.load_library(self.path)
    def test_duplicate_and_foreign(self):
        self.doc['rows'].append(copy.deepcopy(self.doc['rows'][0]))
        with self.assertRaises(v.LibraryError):self.write()
        self.path.write_text('unrelated workbook',encoding='utf-8')
        with self.assertRaises(v.LibraryError):v.write_library(self.path,v.load_library(v.DEFAULT_BOOK),v.revision(self.path))
    def test_paths(self):
        self.assertEqual(v.file_path(v.DEFAULT_BOOK.as_uri()),v.DEFAULT_BOOK)
        with self.assertRaises(v.LibraryError):v.file_path('https://example.com/book.xlsx')
        with self.assertRaises(v.LibraryError):v.file_path('relative.xlsx')
    def test_flexible_driving_and_signed_output(self):
        snap=self.doc['rows'][0]['snapshot'];snap['torqueConvention']='physical-link2-ccw/v2';snap['outputs']['tauG']=abs(snap['outputs']['tauG']);snap['springDriving']=dict(springK=True,hornR=False,Sv=True,rs=False,p0=True,nu=True,Su=False)
        expected=copy.deepcopy(snap);self.write();actual=v.load_library(self.path)['rows'][0];self.assertEqual(actual['snapshot'],expected);self.assertFalse(actual.get('outputsStale',False))

if __name__=='__main__':unittest.main()
