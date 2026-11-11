#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
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
 (out/'recovery_menu_paula_waves.h').write_text('static const signed char dp_noise[3][2048] __attribute__((aligned(2)))={'+','.join('{'+','.join(map(str,noise(p,s)))+'}' for p,s in [(148,0),(944,0),(8,1)])+'};\n')
 ld=out/'adapter.ld';ld.write_text('SECTIONS { . = 0; .text : { *(.entry) *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }')
 cc=os.environ.get('PAULA_CC','m68k-linux-gnu-gcc')
 subprocess.run([cc,'-I'+str(out),'-m68020','-mpcrel','-O2','-ffreestanding','-fno-builtin','-nostdlib','-fno-pie','-Wl,--build-id=none','-Wl,-T,'+str(ld),*[str(port/'src'/n) for n in ('recovery_menu_paula_entry.s','recovery_menu_paula_adapter.c','experimental_direct_paula.c')],'-o',str(out/'adapter.elf')],check=True)
 subprocess.run([cc.replace('gcc','objcopy'),'-O','binary',str(out/'adapter.elf'),str(out/'adapter.bin')],check=True)
 syms=subprocess.check_output([cc.replace('gcc','nm'),'-S',str(out/'adapter.elf')],text=True);(out/'adapter.symbols').write_text(syms)
 extent=max(int(x.split()[0],16)+int(x.split()[1],16) for x in syms.splitlines() if len(x.split())==4)
 blob=(out/'adapter.bin').read_bytes();p=next(x.split() for x in syms.splitlines() if x.split()[-1]=='experimental_direct_paula_plan');a,n=int(p[0],16),int(p[1],16)
 assert n==470 and hashlib.sha256(blob[a:a+n]).hexdigest()=='33eaebe81eb97ba518ce3def0ae33bb5db1201745018e4c4c77d5f01a5a64996','Use the pinned recovery GCC14 toolchain'
 (out/'adapter.bin').write_bytes(blob+bytes(extent-len(blob)))
 test(out)
 for path in list(port.glob('tools/recovery_menu_paula_*.py'))+list(port.glob('tests/recovery_menu_paula_*.py')):compile(path.read_bytes(),str(path),'exec')
 print('PASS source-only compiled audio adapter tests; synthetic data only, original oracle/private inputs denied. No target timing or playback claim.')
PY
