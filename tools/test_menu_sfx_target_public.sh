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
sys.path[:0]=[str(port/'tools'),str(port/'tests')]
import build_recovery_menu_sfx_target as build
import recovery_menu_sfx_target_adapter_test as adapter
for item in json.loads((port/'analysis/recovery_menu_sfx_target_dependencies.json').read_text())['frozen_dependencies']:
 assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256']
with tempfile.TemporaryDirectory() as tmp:
 out=Path(tmp);resource=bytes(range(256))*512
 for history in build.HISTORIES:
  d=out/history;d.mkdir()
  for name in ('private-prg.bin','startup-display-private-chr.bin'):(d/name).write_bytes(resource)
  (d/'target.s').write_text(build.source(history))
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(port/'src'),'-I'+str(d),'-o',str(d/'recovery_menu_sfx_target.bin'),str(d/'target.s')],check=True)
  blob=(d/'recovery_menu_sfx_target.bin').read_bytes()
  assert len(blob)==788426 and blob.count(b'CDRSFX01')==1
  assert hashlib.sha256(blob[626:47118]).hexdigest()=='a8a31217696f2f3d30d629adf570b9723c171d965e25f267294a55dc1534496e'
  assert hashlib.sha256(blob[47118:48868]).hexdigest()=='85b142d8ac84d53f4f5bb6f5143b28d1a07183989b71f2aeeeacaa0a3f920bad'
  for name in ('private-prg.bin','startup-display-private-chr.bin'):assert (d/name).read_bytes()==resource
 adapter.OUT=out;adapter.main()
 for path in list(port.glob('**/*menu_sfx_target*.py'))+list(port.glob('tests/recovery_menu_audio_*.py')):compile(path.read_bytes(),str(path),'exec')
 print('PASS three synthetic target assemblies and ten native capture-adapter cases; private input/oracle denial; no game or timing claim')
PY
