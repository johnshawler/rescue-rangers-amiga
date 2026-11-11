#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
python - "$ROOT" <<'PY'
import hashlib,importlib.abc,json,os,subprocess,sys,tempfile
from pathlib import Path
root=Path(sys.argv[1]);port=root/'port'
class DenyOracle(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if 'oracle' in fullname or fullname.startswith('py65'):
   raise ImportError('Original-code oracle imports are forbidden in this public check')
sys.meta_path.insert(0,DenyOracle())
def guard(event,args):
 if event=='open' and isinstance(args[0],(str,bytes)):
  path=str(args[0]).lower()
  if path.endswith('.nes') or '/input/' in path:
   raise PermissionError('Private cartridge inputs are forbidden in this public check')
sys.addaudithook(guard)
sys.path.insert(0,str(port/'tools'))
import build_recovery_menu_timing as build
for item in json.loads((port/'analysis/recovery_menu_timing_dependencies.json').read_text())['frozen_dependencies']:
 assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256']
# Assemble the same runner/helper/device source against synthetic resources only.
# This checks public reproducibility and assembly, not game behavior or timing.
with tempfile.TemporaryDirectory() as d:
 d=Path(d);resource=bytes(range(256))*512
 for name in ('private-prg.bin','startup-display-private-chr.bin'):(d/name).write_bytes(resource)
 (d/'timing.s').write_text(build.source())
 subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(port/'src'),'-I'+str(d),'-o',str(d/'timing.bin'),str(d/'timing.s')],check=True)
 blob=(d/'timing.bin').read_bytes()
 assert len(blob)==510966
 assert blob.count(b'CDRTIM01')==1 and blob.count(b'CDRDIS01')==1
 assert blob[370:370+31628] and hashlib.sha256(blob[370:370+31628]).hexdigest()=='ac4b5d9cdca6da92badce8ca6ffffb1a1bc0077c0d10f77fb98c47a678f6e135'
 for name in ('private-prg.bin','startup-display-private-chr.bin'):assert (d/name).read_bytes()==resource
 for path in port.glob('**/*menu_timing*.py'):compile(path.read_bytes(),str(path),'exec')
 print('PASS synthetic timing-target assembly, frozen helpers, private-input denial and Python syntax; no runtime/timing claim')
PY
