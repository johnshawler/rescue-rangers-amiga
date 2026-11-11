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
