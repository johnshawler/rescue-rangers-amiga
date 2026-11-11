#!/usr/bin/env python3
"""No oracle imports/inputs, poisoned reference independence, deterministic rebuilds."""
import hashlib,importlib.abc,json,subprocess,sys
from pathlib import Path
PORT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PORT/'tools'))
from build_recovery_state_menu_display import OUT,source

def main():
 files=['recovery_state_menu_display.s','recovery_state_menu_display.bin','boot.s','boot.bin','recovery_state_menu_display.adf','private-prg.bin','startup-display-private-chr.bin','build.json']
 hashes=lambda:{f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in files}
 before=hashes()
 # The builder has zero expected-state arguments. Deny all original-oracle and
 # py65 imports in a fresh process, then perform the complete private build.
 program='''import importlib.abc,runpy,sys
class Deny(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if 'oracle' in fullname or fullname.startswith('py65'):raise RuntimeError('Forbidden oracle dependency: '+fullname)
sys.meta_path.insert(0,Deny())
runpy.run_path(sys.argv[1],run_name='__main__')
'''
 for _ in range(2):
  subprocess.run([sys.executable,'-c',program,str(PORT/'tools/build_recovery_state_menu_display.py')],check=True,stdout=subprocess.DEVNULL)
  assert hashes()==before
 # Poison reference result production in this process; production source cannot
 # observe any original RAM, context, journal, diagnostics, or helper sequence.
 sys.path.insert(0,str(PORT/'tests'))
 import recovery_state_menu_display_oracle as reference
 original=reference.oracle
 reference.oracle=lambda *_:[bytes([0x69])*32770]*4096
 try:assert source().encode()==(OUT/'recovery_state_menu_display.s').read_bytes()
 finally:reference.oracle=original
 result=dict(status='PASS',rebuilds_equal=2,complete_build_with_oracle_imports_denied=True,poisoned_reference_source_unchanged=True,artifacts=before)
 (OUT/'build-test.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
