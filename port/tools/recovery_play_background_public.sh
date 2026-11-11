#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
# Dedicated pinned C-toolchain suite, separate from the assembler-only aggregate.
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
from experimental_direct_paula_build import noise
from recovery_menu_paula_adapter_test import test
for row in json.loads((port/'analysis/recovery_menu_paula_manifest.json').read_text())['files']:
 assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
with tempfile.TemporaryDirectory(prefix='menu-paula-public-') as tmp:
 out=Path(tmp)
 (out/'recovery_menu_paula_waves.h').write_text('static const signed char dp_noise[4][2048] __attribute__((aligned(2)))={'+','.join('{'+','.join(map(str,noise(p,s)))+'}' for p,s in [(148,0),(944,0),(8,1),(188,0)])+'};\n')
 ld=out/'adapter.ld';ld.write_text('SECTIONS { . = 0; .text : { *(.entry) *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }')
 cc=os.environ.get('PAULA_CC','m68k-linux-gnu-gcc')
 subprocess.run([cc,'-I'+str(out),'-m68020','-mpcrel','-O2','-ffreestanding','-fno-builtin','-nostdlib','-fno-pie','-Wl,--build-id=none','-Wl,-T,'+str(ld),*[str(port/'src'/n) for n in ('recovery_menu_paula_entry.s','recovery_stage_target_paula_adapter.c','experimental_direct_paula.c','recovery_stage_target_plan.c')],'-o',str(out/'adapter.elf')],check=True)
 subprocess.run([cc.replace('gcc','objcopy'),'-O','binary',str(out/'adapter.elf'),str(out/'adapter.bin')],check=True)
 syms=subprocess.check_output([cc.replace('gcc','nm'),'-S',str(out/'adapter.elf')],text=True);(out/'adapter.symbols').write_text(syms)
 extent=max(int(x.split()[0],16)+int(x.split()[1],16) for x in syms.splitlines() if len(x.split())==4)
 blob=(out/'adapter.bin').read_bytes();p=next(x.split() for x in syms.splitlines() if x.split()[-1]=='experimental_direct_paula_plan');a,n=int(p[0],16),int(p[1],16)
 assert n==470 and hashlib.sha256(blob[a:a+n]).hexdigest()=='33eaebe81eb97ba518ce3def0ae33bb5db1201745018e4c4c77d5f01a5a64996','Use the pinned recovery GCC14 toolchain'
 (out/'adapter.bin').write_bytes(blob+bytes(extent-len(blob)))
 import runpy
 sys.argv=[str(port/'tests/recovery_stage_target_adapter_test.py'),str(out)]
 runpy.run_path(sys.argv[0],run_name='__main__')
 runpy.run_path(str(port/'tests/recovery_stage_target_public_contract.py'),run_name='__main__')
 sys.argv=[str(port/'tests/recovery_stage_target_plan_test.py'),str(out)]
 runpy.run_path(sys.argv[0],run_name='__main__')
 runpy.run_path(str(port/'tests/recovery_zx_keyboard_test.py'),run_name='__main__')
 runpy.run_path(str(port/'tests/recovery_stage_target_verifier_test.py'),run_name='__main__')
 from recovery_play_target_source import integrated_source
 from recovery_play_background_build import prepare
 from recovery_bank_loader_play_harness import assemble
 native=assemble();assert len(native)==216616 and hashlib.sha256(native).hexdigest()=='5a3ab5ff5204b73dd1223291f42f826f634ff43eaee725c7a503684f80e317f4'
 import re
 (out/'private-prg.bin').write_bytes(bytes(131072))
 (out/'startup-display-private-chr.bin').write_bytes(bytes(131072))
 (out/'synthetic.s').write_text(prepare(integrated_source(),out))
 subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-I'+str(port/'src'),'-I'+str(out),'-L',str(out/'target.list'),'-o',str(out/'target.bin'),str(out/'synthetic.s')],check=True)
 assert (out/'target.bin').read_bytes().count(native)==1
 symbols={n:int(a,16) for a,n in re.findall(r'^([0-9A-Fa-f]{8}) ([A-Za-z_][A-Za-z_0-9]*)$',(out/'target.list').read_text(),re.M)}
 (out/'target.symbols.json').write_text(json.dumps(symbols))
 (out/'build.json').write_text(json.dumps(dict(stage=True)))
 sys.argv=[str(port/'tests/recovery_stage_target_composition_test.py'),str(out)]
 runpy.run_path(sys.argv[0],run_name='__main__')
 sys.argv=[str(port/'tests/recovery_play_target_rejection_test.py'),str(out)]
 runpy.run_path(sys.argv[0],run_name='__main__')
 sys.argv=[str(port/'tests/recovery_play_target_layout_test.py'),str(out)]
 runpy.run_path(sys.argv[0],run_name='__main__')
 print('PASS source-only compiled audio adapter tests; synthetic data only, original oracle/private inputs denied. No target timing or playback claim.')
PY

PYTHONPATH="$ROOT/port/tests:${PYTHONPATH:-}" OPENBLAS_NUM_THREADS=1 python - <<'PYTEST'
import sys
from pathlib import Path
def audit(event,args):
 if event=='import':assert 'oracle' not in str(args[0]) and not str(args[0]).startswith('py65')
 if event=='open':assert '/input/' not in str(args[0]) and not str(args[0]).endswith('.nes')
sys.addaudithook(audit)
import recovery_stage_background_noise_pcm as frozen
import recovery_play_background_noise_audit as diagnostic
assert diagnostic.Classifier is frozen.Classifier and diagnostic.admitted is frozen.admitted
from recovery_stage_background_noise_test import main
main()
print('PASS diagnostic audit uses exact frozen classifier and admission gates; no changed window/threshold classifier')
PYTEST
