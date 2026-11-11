#!/usr/bin/env python3
"""Source-only fresh-process rebuilds with original-oracle imports prohibited."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
PORT=Path(__file__).resolve().parents[1];ROOT=PORT.parent;OUT=PORT/'build/recovery_menu_sfx_target'
FILES=('recovery_menu_sfx_target.s','recovery_menu_sfx_target.bin','boot.s','boot.bin','recovery_menu_sfx_target.adf','private-prg.bin','startup-display-private-chr.bin','build.json')
HISTORIES=('default','right_hold','move_back')
def hashes(root):return {h+'/'+f:hashlib.sha256((root/h/f).read_bytes()).hexdigest() for h in HISTORIES for f in FILES}
def main():
 before=hashes(OUT)
 program='''import importlib.abc,runpy,sys
class Deny(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if 'oracle' in fullname or fullname.startswith('py65'):raise RuntimeError('Forbidden oracle dependency: '+fullname)
sys.meta_path.insert(0,Deny())
runpy.run_path(sys.argv[1],run_name='__main__')
'''
 with tempfile.TemporaryDirectory(prefix='recovery_menu_sfx_target_') as tmp:
  root=Path(tmp)
  # Copy source files only. No generated output, reference, or captured state.
  for folder in ('src','tests','tools','analysis'):
   shutil.copytree(PORT/folder,root/'port'/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  (root/'input').mkdir();shutil.copyfile(ROOT/'input/rescue-rangers-europe.nes',root/'input/rescue-rangers-europe.nes')
  # Some frozen dependency pins cover root build metadata and scripts.
  for item in json.loads((PORT/'analysis/recovery_menu_timing_dependencies.json').read_text())['frozen_dependencies']:
   dst=root/item['path']
   if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/item['path'],dst)
  for _ in range(2):
   subprocess.run([sys.executable,'-c',program,str(root/'port/tools/build_recovery_menu_sfx_target.py')],check=True,stdout=subprocess.DEVNULL)
   assert hashes(root/'port/build/recovery_menu_sfx_target')==before
 result=dict(status='PASS',fresh_source_only_tree=True,full_builds_equal=2,oracle_and_py65_imports_denied=True,artifacts=before)
 (OUT/'build-test.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
