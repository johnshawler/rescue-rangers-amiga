#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT=$(mktemp -d "${TMPDIR:-/tmp}/recovery-play-target-public.XXXXXX")
python - "$ROOT" "$OUT" <<'PY'
import sys,hashlib,json,shutil
from pathlib import Path
root,out=map(Path,sys.argv[1:]);name='port/analysis/recovery_play_target_manifest.json'
m=json.loads((root/name).read_text());files={**m['public_allowlist'],**m['dependencies']}
files[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
for n,h in files.items():
 p=Path(n);assert not p.is_absolute() and '..' not in p.parts
 assert all(x not in n for x in ('original-disassembly','.nes','.adf','.bin','.pcm'))
 assert hashlib.sha256((root/n).read_bytes()).hexdigest()==h,n
 q=out/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/n,q)
print('Verified flat source-only closure:',len(files),'files',out,flush=True)
PY
cd "$OUT"
bash port/tools/recovery_play_target_public.sh
printf 'Restored tree retained: %s\n' "$OUT"
