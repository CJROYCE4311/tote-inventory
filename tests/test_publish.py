import sys,unittest,copy,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from publish_inventory import compile_data,rows,HEADERS
class Validation(unittest.TestCase):
 def setUp(self):
  self.data={'Boxes':[dict(zip(HEADERS['Boxes'],['JEAN 025','','Cataloged','Arizona','Books','Miki','','','','','Yes']))], 'Items':[dict(zip(HEADERS['Items'],['I25','JEAN 025','Books',3,'Books','Good','','','','']))], 'Photos':[dict(zip(HEADERS['Photos'],['P25','JEAN 025','','abcdefghijklmno12345','','','Yes']))]}
 def test_new_box_and_box_photo(self):
  b,p=compile_data(self.data);self.assertEqual(b[0]['slug'],'jean-025');self.assertEqual(b[0]['photos'],['abcdefghijklmno12345.jpg'])
 def test_duplicate_and_orphan_rejected(self):
  d=copy.deepcopy(self.data);d['Boxes']*=2
  with self.assertRaises(ValueError):compile_data(d)
  d=copy.deepcopy(self.data);d['Items'][0]['Box ID']='JEAN 999'
  with self.assertRaises(ValueError):compile_data(d)
 def test_private_photo_omitted(self):
  self.data['Photos'][0]['Publish']='No';b,p=compile_data(self.data);self.assertEqual(p,[])
 def test_bad_quantity_and_url(self):
  self.data['Items'][0]['Qty']=0
  with self.assertRaises(ValueError):compile_data(self.data)
  self.data['Items'][0]['Qty']=1;self.data['Boxes'][0]['Website URL']='https://example.com/'
  with self.assertRaises(ValueError):compile_data(self.data)
if __name__=='__main__':unittest.main()
