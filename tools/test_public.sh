#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
python "$ROOT/port/tests/test_native_background.py"
python "$ROOT/port/tests/test_native_sprites.py"
python "$ROOT/port/tests/test_recovery_input_restore.py"
python "$ROOT/port/tests/test_recovery_synthetic_chain.py"
# Assemble the new reset helpers without any cartridge/firmware input.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
"$VASM" -quiet -m68020 -Fbin -o "$TMP/reset.bin" "$ROOT/port/src/recovery_reset_ram.s"
"$VASM" -quiet -m68020 -Fbin -o "$TMP/mapper.bin" "$ROOT/port/src/recovery_reset_mapper.s"
python "$ROOT/port/tools/build_recovery_reset_probe.py"
python "$ROOT/port/tools/build_recovery_reset_probe.py" --first-yield
python "$ROOT/port/tools/build_recovery_reset_probe.py" --nmi-audio-entry
python "$ROOT/port/tools/build_recovery_reset_probe.py" --audio-reset
python "$ROOT/port/tools/build_recovery_reset_probe.py" --nmi-return
python "$ROOT/port/tools/build_recovery_reset_probe.py" --scheduler-resume
python "$ROOT/port/tools/build_recovery_reset_probe.py" --resumed-task-setup
# Existing probe modes must remain byte-identical when an opt-in mode is added.
python - "$ROOT" <<'PY'
import hashlib, sys
from pathlib import Path
build = Path(sys.argv[1])/'port/build'
expected = {
 'recovery-reset-probe': '840e6ff4a1403488f572b5e76e791ad3e97a4acb08f97045e312296d9a3b8225',
 'recovery-first-yield-probe': 'e991d2a5c636a3001d61767ab60daaf307e96d00d290ae4b39d54c50da9d01d3',
 'recovery-nmi-audio-entry-probe': '4d2ab14b1bb174838e7a7a48115bace0d78e4cf281f8edbf1a771048823ee86d',
 'recovery-audio-reset-probe': '70923298254675c33111d6e05e13147cd926d61e9564416d7847a951ef5b5560',
 'recovery-nmi-return-probe': '267303fd0d998937d45052c26063904b96f82c5c44f43b197febd19503a831ba',
 'recovery-scheduler-resume-probe': 'bc3b564980423790d874a5c5c686eb2aa365b6f0c97f3b7e2706f8eb23e660ae',
 'recovery-resumed-task-setup-probe': '052dbe2f97730d822931cbd988793be985aa7f0804bd51d3292284a70312b048',
}
for name, digest in expected.items():
 assert hashlib.sha256((build/(name+'.adf')).read_bytes()).hexdigest() == digest, name
print('PASS seven pinned source-only probe ADF hashes')
PY
