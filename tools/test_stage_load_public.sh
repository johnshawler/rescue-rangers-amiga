#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
python - "$ROOT" <<'PY'
import importlib.abc, runpy, sys
from pathlib import Path
root = Path(sys.argv[1])
class DenyOracle(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith('py65') or 'oracle' in fullname:
            raise ImportError('Original-cartridge oracle imports are forbidden')
sys.meta_path.insert(0, DenyOracle())
def guard(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        path = str(args[0]).lower()
        if path.endswith('.nes') or '/input/' in path or 'kick40068' in path:
            raise PermissionError('Private cartridge and firmware reads are forbidden')
sys.addaudithook(guard)
sys.path.insert(0, str(root / 'port/tests'))
for name in ('recovery_bank_loader_dialogue_contract.py', 'recovery_bank_loader_dialogue_nmi_test.py', 'recovery_stage_map_test.py', 'recovery_bank_loader_stage_contract.py', 'recovery_stage_object_test.py', 'recovery_bank_loader_finish_contract.py', 'recovery_bank_loader_music_contract.py'):
    test = root / 'port/tests' / name
    sys.argv = [str(test)]
    runpy.run_path(str(test), run_name='__main__')
print('PASS source-only stage loading contracts; no target timing claim. Python private-input/import hooks are regression checks, not an OS sandbox.')
PY
