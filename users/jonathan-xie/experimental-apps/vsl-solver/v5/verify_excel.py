"""Verify V5 Excel library compatibility and fall-state persistence.

Run: python verify_excel.py. Inputs local copied workbook and V5 columns;
units kg/m/mm/deg/N/Nm/s. Outputs unittest results. Writes temporary workbooks
only; no installed Excel needed, no native picker or hardware certification.
"""
import copy,pathlib,tempfile,unittest,zipfile,xml.etree.ElementTree as ET
import vsl_server as v

class V5ExcelTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.temp.name)/'test.xlsx';self.doc=v.load_library(v.DEFAULT_BOOK)
    def tearDown(self):self.temp.cleanup()
    def write(self):return v.write_library(self.path,self.doc,None)
    def edit(self,key,value):
        files,sheets,_=v.unpack_book(self.path);root=ET.fromstring(files[sheets['Designs']]);c=next(c for c in v.COLUMNS if c['key']==key);col=v.column_name(v.COLUMNS.index(c)+1);ref=f'{col}2';row=root.find(f'.//{v.X("row")}[@r="2"]');node=row.find(f'{v.X("c")}[@r="{ref}"]')
        if node is None:node=ET.SubElement(row,v.X('c'),r=ref)
        node.attrib.pop('t',None)
        for child in list(node):node.remove(child)
        ET.SubElement(node,v.X('v')).text=str(value);files[sheets['Designs']]=v.xml_bytes(root)
        with zipfile.ZipFile(self.path,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,data in files.items():archive.writestr(name,data)
    def test_copied_legacy_rows(self):
        self.assertGreater(len(self.doc['rows']),0)
        for row in self.doc['rows']:
            if row['snapshot']:self.assertIn(row['snapshot']['schema'],('general-vsl/v4-pulley','general-vsl/v5-fall'))
        original=copy.deepcopy(self.doc);self.write();result=v.load_library(self.path);self.assertEqual(original,result)
    def test_v5_state_roundtrip(self):
        s=self.doc['rows'][0]['snapshot'];s['schema']='general-vsl/v5-fall';s['fallStudy']={'heightM':.7,'massBounds':{'min':1,'max':20},'heightBounds':{'min':0,'max':2}};s['outputs'].update(fallTorque=12.3,fallTime=.45,fallPeakAcceleration=2.1,fallPeakForce=265,fallPeakSpeed=3.7)
        self.write();self.assertEqual(v.load_library(self.path)['rows'][0]['snapshot'],s)
    def test_height_edit_does_not_change_static_parameters(self):
        self.write();before=copy.deepcopy(self.doc['rows'][0]['snapshot']['parameters']);self.edit('fallHeight',.8);result=v.load_library(self.path)['rows'][0];self.assertEqual(result['snapshot']['fallStudy']['heightM'],.8);self.assertEqual(result['snapshot']['parameters'],before);self.assertTrue(result['outputsStale'])
    def test_mass_edit_follows_g(self):
        self.write();before=self.doc['rows'][0]['snapshot']['parameters'];target=v.weight(before)+2;self.edit('totalMass',target);after=v.load_library(self.path)['rows'][0]['snapshot']['parameters'];self.assertAlmostEqual(v.weight(after),target)
        if v.weight(before)>0:
            for key in ('Fy','Fz') if before['loadMode']=='yz' else ('Fn','Ft'):self.assertAlmostEqual(after[key],before[key]*target/v.weight(before))
    def test_revision_and_backup(self):
        rev=self.write();v.write_library(self.path,self.doc,rev);self.assertTrue(self.path.with_name('test.vsl-backup.xlsx').exists())
        with self.assertRaises(v.LibraryError):v.write_library(self.path,self.doc,'stale')
    def test_foreign_book_not_overwritten(self):
        self.path.write_bytes(b'unrelated workbook')
        with self.assertRaises(v.LibraryError):v.write_library(self.path,self.doc,v.revision(self.path))
        self.assertEqual(self.path.read_bytes(),b'unrelated workbook')
    def test_schema_rejected(self):
        self.doc['rows'][0]['snapshot']['schema']='foreign'
        with self.assertRaises(v.LibraryError):self.write()

if __name__=='__main__':unittest.main()
