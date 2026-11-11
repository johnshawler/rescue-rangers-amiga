#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
: "${VASM:?Set VASM to pinned assembler}"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/port/src" "$TMP/port/tests"
cp "$ROOT/port/src/recovery_player_collision_region.s" "$TMP/port/src/"
for f in recovery_player_collision_test.py recovery_stage_map_test.py recovery_bank_loader_dialogue_harness.py; do cp "$ROOT/port/tests/$f" "$TMP/port/tests/"; done
python - "$TMP" "$@" <<'PY'
import importlib.abc,runpy,sys
from pathlib import Path
root=Path(sys.argv[1]);args=sys.argv[2:]
class DenyOracle(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.startswith('py65') or 'oracle' in fullname:raise ImportError('Private reference import forbidden')
sys.meta_path.insert(0,DenyOracle())
def guard(event,args):
 if event=='open' and isinstance(args[0],(str,bytes)):
  p=str(args[0]).lower()
  if p.endswith('.nes') or '/input/' in p:raise PermissionError('Private cartridge read forbidden')
sys.addaudithook(guard)
sys.path.insert(0,str(root/'port/tests'));test=root/'port/tests/recovery_player_collision_test.py';sys.argv=[str(test)]+args
runpy.run_path(str(test),run_name='__main__')
print('PASS source-only restored player collision helper; import/read guards are regression tests, not OS sandbox')
PY
