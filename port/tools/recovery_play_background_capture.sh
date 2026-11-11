#!/usr/bin/env bash
# Fresh stock capture; expected frozen PCM rejection remains a failure, never hidden.
set -euo pipefail
cd "$(dirname "$0")/../.."
B=$(realpath "${1:?New built output directory}")
python - "$B" <<'PY'
import json,sys
from pathlib import Path
m=json.loads((Path(sys.argv[1])/'build.json').read_text())
assert m['background_optimized'] and m['profiling'] is False and m['play']
assert m['background_source_sha256']=='d916fffbc90f750b96568fc85f4f069a1b6b4e8bff706cec7756b5c628c23f3e'
PY
bash port/tools/recovery_play_target_run.sh "$B" 11500 '80:90:13,160:170:13,360:390:13'
