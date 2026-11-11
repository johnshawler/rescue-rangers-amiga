#!/usr/bin/env bash
# One fresh stock capture, current corrected state/pixel/replay/PCM checks.
set -euo pipefail
cd "$(dirname "$0")/../.."
B=$(realpath "${1:?New built output directory}")
python - "$B" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);m=json.loads((p/'build.json').read_text())
assert m['background_optimized'] and m['profiling'] is False and m['display_dma']==1
assert m['background_source_sha256']=='d916fffbc90f750b96568fc85f4f069a1b6b4e8bff706cec7756b5c628c23f3e'
PY
bash port/tools/recovery_stage_target_run.sh "$B" 11000 '80:90:13,160:170:13,360:390:13'
python port/tests/recovery_stage_target_rejection_test.py "$B"
