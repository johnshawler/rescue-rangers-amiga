#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
python - "$ROOT" <<'PY'
import hashlib, importlib.abc, os, runpy, sys, tempfile
from pathlib import Path
root = Path(sys.argv[1]); port = root / 'port'
class DenyOracle(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if 'oracle' in fullname or fullname.startswith('py65'):
            raise ImportError('Private oracle imports are forbidden in this public check')
sys.meta_path.insert(0, DenyOracle())
def guard(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        path = str(args[0]).lower()
        if path.endswith('.nes') or '/input/' in path or 'kick40068' in path:
            raise PermissionError('Private cartridge and firmware inputs are forbidden')
sys.addaudithook(guard)
sys.path[:0] = [str(port / 'tools'), str(port / 'tests')]
def run(path, *args):
    sys.argv = [str(path), *map(str, args)]
    runpy.run_path(str(path), run_name='__main__')
run(port / 'tests/recovery_profile_public_test.py')
run(port / 'tests/recovery_zx_keyboard_test.py')
run(port / 'tests/recovery_zx_poll_test.py')
with tempfile.TemporaryDirectory(prefix='recovery-input-public-') as directory:
    output = Path(directory) / 'fresh'
    run(port / 'tools/recovery_zx_build.py', '--output', output)
    disk = output / 'input-probe.adf'
    digest = hashlib.sha256(disk.read_bytes()).hexdigest()
    assert digest == 'c94ac0f963ec9c56b84be1a79076145bc4af2cde046d615984939a34c2ea089b'
    try:
        run(port / 'tools/recovery_zx_build.py', '--output', output)
    except FileExistsError:
        pass
    else:
        raise AssertionError('Builder accepted an existing evidence directory')
    assert hashlib.sha256(disk.read_bytes()).hexdigest() == digest
print('PASS source-only profiler/input extension, exact input probe build and overwrite refusal; no target playback or speed claim. Python private-input/import hooks are regression checks, not an OS sandbox.')
PY
