#!/usr/bin/env python3
"""Install only manifest-pinned private inputs. Never replace mismatching data."""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
ROM='051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'
KICK='6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707'
def digest(b):return hashlib.sha256(b).hexdigest()
def prepare(args):
 manifest=json.loads((ROOT/'tools/private-fixture-manifest.json').read_text());pending=[]
 if args.bundle:
  with zipfile.ZipFile(args.bundle) as z:
   for item in manifest:
    rel=Path(item['path']);assert not rel.is_absolute() and '..' not in rel.parts
    data=z.read('title-source/'+rel.as_posix())
    if len(data)!=item['bytes'] or digest(data)!=item['sha256']:raise ValueError('Fixture hash mismatch: '+str(rel))
    pending.append((ROOT/rel,data))
 for value,rel,sha in ((args.rom,'input/rescue-rangers-europe.nes',ROM),(args.kickstart,'artifacts/a1200-system/kick40068.A1200',KICK)):
  if value:
   data=Path(value).read_bytes()
   if digest(data)!=sha:raise ValueError('Wrong original input hash: '+rel)
   pending.append((ROOT/rel,data))
 if not pending:raise ValueError('Provide at least one input')
 # Preflight every destination before any writes, including symlink boundaries.
 for dst,data in pending:
  for parent in [dst,*dst.parents]:
   if parent==ROOT.parent:break
   if parent.is_symlink():raise ValueError('Symlink destination refused: '+str(parent))
  if dst.exists() and (not dst.is_file() or dst.read_bytes()!=data):raise ValueError('Existing different data refused: '+str(dst.relative_to(ROOT)))
 for dst,data in pending:
  if not args.check_only and not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 return [str(dst.relative_to(ROOT)) for dst,_ in pending]
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,help='Private recovered-title-source-and-binaries ZIP');p.add_argument('--rom',type=Path,help='Original European NES cartridge file');p.add_argument('--kickstart',type=Path,help='Existing A1200 Kickstart3.1 file');p.add_argument('--check-only',action='store_true');a=p.parse_args()
 try:print(json.dumps({'status':'CHECKED' if a.check_only else 'INSTALLED_OR_IDENTICAL','files':prepare(a)},indent=2))
 except (OSError,ValueError,KeyError,zipfile.BadZipFile,AssertionError) as e:p.exit(1,str(e)+'\n')
