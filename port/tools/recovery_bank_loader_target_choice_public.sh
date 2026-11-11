#!/usr/bin/env bash
set -euo pipefail
: "${VASM:?Set VASM to the approved vasmm68k_mot executable}"
export PYTHONDONTWRITEBYTECODE=1
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT=$(mktemp -d "${TMPDIR:-/tmp}/recovery-target-choice-public.XXXXXX")
cd "$ROOT"
python - "$OUT" <<'PY'
import sys,json,hashlib,shutil
from pathlib import Path
out=Path(sys.argv[1]);seen=set()
def restore(p,want=None):
 q=Path(p);digest=hashlib.sha256(q.read_bytes()).hexdigest()
 assert want is None or digest==want,(p,digest,want)
 if p in seen:return
 seen.add(p);target=out/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,target)
 if q.suffix=='.json':
  data=json.loads(q.read_text())
  for field in ('public_allowlist','dependencies','files','additional_source_dependencies'):
   for path,sha in data.get(field,{}).items():restore(path,sha)
restore('port/analysis/recovery_bank_loader_target_choice_manifest.json')
print('Verified isolated source restore:',len(seen),'files',flush=True)
PY
cd "$OUT"
PYTHONPATH="$OUT/port/tests:${PYTHONPATH:-}" python - <<'PY'
import sys,importlib,json,hashlib
from pathlib import Path
def audit(event,args):
 if event=='import':
  name=str(args[0]);assert 'oracle' not in name and not name.startswith('py65'),('private oracle import',name)
 if event=='open':
  name=str(args[0]);assert '/input/' not in name and not name.endswith('.nes'),('cartridge access',name)
sys.addaudithook(audit)
from recovery_bank_loader_target_choice_harness import assemble
manifest=json.loads(Path('port/analysis/recovery_bank_loader_target_choice_manifest.json').read_text());code=assemble()
assert len(code)==manifest['composite_bytes'] and hashlib.sha256(code).hexdigest()==manifest['composite_sha256']
print('Exact native composition:',len(code),hashlib.sha256(code).hexdigest(),flush=True)
for name in ('recovery_bank_loader_target_choice_test','recovery_bank_loader_target_choice_wrapper_test'):
 sys.argv=[name,'--quick'] if name=='recovery_stage_scroll_test' else [name]
 importlib.import_module(name).main()
print('PASS isolated F328 source-only public/negative suite; no cartridge/oracle imports',flush=True)
PY
printf 'Isolated source restore retained at %s\n' "$OUT"
