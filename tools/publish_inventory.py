#!/usr/bin/env python3
"""Read the canonical Sheet and Drive photos; validate, build privately, deploy atomically."""
from pathlib import Path
import argparse,collections,fcntl,hashlib,io,json,os,re,shutil,subprocess,sys,tempfile,time,urllib.request,zipfile
from datetime import datetime,timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from PIL import Image,ImageOps
import qrcode
HOME=Path.home();REPO=Path(__file__).resolve().parents[1];STATE=HOME/'.local/share/jean-inventory-publisher'
SHEET='1fJXY3XIhmydEnoq8Czlc_mQfXPKtWsQ_JK3tsRE4mu4';PHOTOS='1OIN13ZqW200NFUmtsJjjZCh_RKROSwv3';SITE='4c20d8fb-fd1c-4ae6-a324-dc4d0b2b11aa';URL='https://jean-inventory.netlify.app'
HEADERS={'Boxes':['Box ID','Website URL','Status','Current location','Contents summary','Cataloged by','Cataloged date','Last verified','Notes','Legacy QR URL','Publish'],'Items':['Item ID','Box ID','Item / grouped contents','Qty','Category','Condition','Cataloged by','Catalog date','Arizona destination','Original photo reference'],'Photos':['Photo ID','Box ID','Item ID','Drive file ID','Drive URL','Caption','Publish']}
def atomic(p,obj):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(obj,indent=2));os.replace(t,p)
def rows(values,headers):
 if not values or values[0]!=headers:raise ValueError('Sheet headers changed; publisher needs matching schema')
 return [dict(zip(headers,r+['']*(len(headers)-len(r)))) for r in values[1:] if any(str(x).strip() for x in r)]
def identity(row,key,seen):
 v=str(row[key]).strip()
 if not v or v in seen:raise ValueError('Missing or duplicate '+key)
 seen.add(v);return v
def compile_data(tabs):
 boxes={};items={};ids=set()
 for r in tabs['Boxes']:
  bid=identity(r,'Box ID',ids)
  if not re.fullmatch(r'JEAN \d{3,}',bid):raise ValueError('Box ID must use JEAN ###')
  if r['Publish'] not in ('Yes','No'):raise ValueError('Box Publish must be Yes or No')
  slug=bid.lower().replace(' ','-');expected=URL+'/box/'+slug
  if r['Website URL'] and r['Website URL'].rstrip('/')!=expected:raise ValueError('Website URL does not match permanent Box ID')
  boxes[bid]={'id':bid,'slug':slug,'owner':'Jean','label':bid,'status':r['Status'] or 'Awaiting inventory','location':r['Current location'],'category':'Not cataloged','summary':r['Contents summary'],'packedBy':r['Cataloged by'],'updated':str(r['Cataloged date'])[:10],'handling':[],'notes':r['Notes'],'items':[],'photos':[],'publish':r['Publish']=='Yes'}
 for r in tabs['Items']:
  iid=identity(r,'Item ID',set(items));bid=r['Box ID']
  if bid not in boxes or not r['Item / grouped contents']:raise ValueError('Item needs a valid box and description')
  qty=float(r['Qty'])
  if not 0<qty<1000000:raise ValueError('Item quantity must be positive')
  item={'name':r['Item / grouped contents'],'quantity':qty,'category':r['Category'],'condition':r['Condition'],'notes':('Destination: '+r['Arizona destination']) if r['Arizona destination'] else '', 'photo':''}
  items[iid]=(bid,item);boxes[bid]['items'].append(item)
  if 'fragile' in str(r['Condition']).lower():boxes[bid]['handling']=['Fragile']
 photoids=set();photos=[]
 for r in tabs['Photos']:
  identity(r,'Photo ID',photoids);bid=r['Box ID'];iid=r['Item ID']
  if bid not in boxes or (iid and (iid not in items or items[iid][0]!=bid)):raise ValueError('Photo box/item relationship invalid')
  if r['Publish'] not in ('Yes','No'):raise ValueError('Photo Publish must be Yes or No')
  if r['Publish']!='Yes' or not boxes[bid]['publish']:continue
  fid=str(r['Drive file ID']).strip()
  if not fid:
   m=re.search(r'(?:/d/|[?&]id=)([\w-]+)',str(r['Drive URL']));fid=m[1] if m else ''
  if not re.fullmatch(r'[\w-]{15,}',fid):raise ValueError('Photo needs Drive ID or link')
  name=fid+'.jpg';boxes[bid]['photos'].append(name)
  if iid:items[iid][1]['photo']='; '.join(filter(None,[items[iid][1]['photo'],name]))
  photos.append(fid)
 result=[]
 for b in boxes.values():
  if not b.pop('publish'):continue
  b['photos']=list(dict.fromkeys(b['photos']));b['category']=b['items'][0]['category'] if b['items'] else 'Not cataloged';result.append(b)
 if not result:raise ValueError('No published boxes; refusing empty site')
 return result,sorted(set(photos))
def netlify(path,method='GET',data=None,content='application/json'):
 config=json.loads((HOME/'Library/Preferences/netlify/config.json').read_text());user=config['users'][config['userId']];auth=user['auth'];token=auth.get('token') if isinstance(auth,dict) else auth
 req=urllib.request.Request('https://api.netlify.com/api/v1/'+path,data=data,method=method,headers={'Authorization':'Bearer '+token,'Content-Type':content})
 with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--publish',action='store_true');ap.add_argument('--force',action='store_true');a=ap.parse_args()
 STATE.mkdir(parents=True,exist_ok=True,mode=0o700);os.umask(0o077)
 with (STATE/'run.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return
  creds=Credentials.from_authorized_user_file(str(HOME/'.config/caddie-mirror/google-drive/token.json'))
  drive=build('drive','v3',credentials=creds,cache_discovery=False);sheets=build('sheets','v4',credentials=creds,cache_discovery=False)
  meta=sheets.spreadsheets().get(spreadsheetId=SHEET,fields='sheets.properties').execute()
  properties={x['properties']['title']:x['properties'] for x in meta['sheets']}
  ranges=[f"'{n}'!A1:{chr(64+len(headers))}{properties[n]['gridProperties']['rowCount']}" for n,headers in HEADERS.items()]
  data=sheets.spreadsheets().values().batchGet(spreadsheetId=SHEET,ranges=ranges).execute()['valueRanges']
  tabs={n:rows(v.get('values',[]),HEADERS[n]) for n,v in zip(HEADERS,data)};boxes,fids=compile_data(tabs)
  metadata={}
  for fid in fids:
   f=drive.files().get(fileId=fid,fields='id,mimeType,md5Checksum,version,parents,trashed').execute()
   if f.get('trashed') or not f['mimeType'].startswith('image/'):raise ValueError('Photo unavailable or not image')
   # Limit publishing to the designated photo folder, including box subfolders.
   parents=f.get('parents',[]);visited=set();allowed=False
   while parents:
    pid=parents.pop()
    if pid==PHOTOS:allowed=True;break
    if pid in visited:continue
    visited.add(pid);parents.extend(drive.files().get(fileId=pid,fields='parents').execute().get('parents',[]))
   if not allowed:raise ValueError('Photo must live in designated box-photos folder')
   metadata[fid]=f
  revision=hashlib.sha256(json.dumps([tabs,metadata],sort_keys=True).encode()).hexdigest()
  old=json.loads((STATE/'status.json').read_text()) if (STATE/'status.json').exists() else {}
  if old.get('revision')==revision and old.get('status')=='published' and not a.force:
   old['last_checked_at']=datetime.now(timezone.utc).isoformat();atomic(STATE/'status.json',old);(STATE/'last-error.json').unlink(missing_ok=True);print('No inventory changes');return
  with tempfile.TemporaryDirectory(prefix='build-',dir=STATE) as tmp:
   work=Path(tmp)
   for n in ['app','public'] :shutil.copytree(REPO/n,work/n,ignore=shutil.ignore_patterns('box-photos','qr'))
   for n in ['package.json','package-lock.json','tsconfig.json','next-env.d.ts','next.config.ts']:shutil.copy2(REPO/n,work/n)
   (work/'node_modules').symlink_to(REPO/'node_modules',target_is_directory=True)
   (work/'app/inventory-data.json').write_text(json.dumps(boxes))
   photo_dir=work/'public/box-photos';photo_dir.mkdir();qr_dir=work/'public/qr';qr_dir.mkdir()
   cache=STATE/'photo-cache';cache.mkdir(exist_ok=True)
   for fid,f in metadata.items():
    cached=cache/(fid+'-'+str(f['version'])+'.jpg')
    if not cached.exists():
     blob=drive.files().get_media(fileId=fid).execute()
     if f.get('md5Checksum') and hashlib.md5(blob).hexdigest()!=f['md5Checksum']:raise ValueError('Photo checksum mismatch')
     with Image.open(io.BytesIO(blob)) as im:
      im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((1600,1600));im.save(cached,'JPEG',quality=85)
    shutil.copy2(cached,photo_dir/(fid+'.jpg'))
   for b in boxes:qrcode.make(URL+'/box/'+b['slug']).save(qr_dir/(b['slug']+'.png'))
   (work/'public/inventory-version.json').write_text(json.dumps({'revision':revision,'boxes':len(boxes),'items':sum(len(b['items']) for b in boxes),'photos':len(fids),'published_at':datetime.now(timezone.utc).isoformat()}))
   env=dict(os.environ,PATH='/opt/homebrew/bin:/usr/bin:/bin:'+os.environ.get('PATH',''))
   subprocess.run(['/opt/homebrew/bin/npm','run','build'],cwd=work,env=env,check=True,stdout=(STATE/'build.log').open('w'),stderr=subprocess.STDOUT)
   out=work/'out';assert (out/'index.html').exists()
   for b in boxes:assert (out/'box'/b['slug']/'index.html').exists()
   if not a.publish:print('Validated build',len(boxes),'boxes',len(fids),'photos');return
   archive=io.BytesIO()
   with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in out.rglob('*'):
     if p.is_file():z.write(p,str(p.relative_to(out)))
   deployed=netlify('sites/'+SITE+'/deploys','POST',archive.getvalue(),'application/zip')
   for _ in range(60):
    state=netlify('deploys/'+deployed['id'])
    if state['state']=='ready':break
    if state['state']=='error':raise RuntimeError('Netlify deployment failed')
    time.sleep(2)
   else:raise RuntimeError('Netlify deployment still pending')
   with urllib.request.urlopen(URL+'/inventory-version.json?revision='+revision,timeout=60) as r:verify=json.load(r)
   if verify['revision']!=revision:raise RuntimeError('Production readback differs')
   # Preserve source snapshots locally; Google keeps Sheet revision history.
   history=STATE/'history';history.mkdir(exist_ok=True);atomic(history/(revision+'.json'),tabs)
   atomic(STATE/'status.json',dict(verify,status='published',deploy_id=deployed['id']));(STATE/'last-error.json').unlink(missing_ok=True);print('Published and verified',verify)
if __name__=='__main__':
 try:main()
 except Exception as e:
  STATE.mkdir(parents=True,exist_ok=True);atomic(STATE/'last-error.json',{'time':datetime.now(timezone.utc).isoformat(),'error':type(e).__name__+': '+str(e)});raise
