#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
python "$ROOT/port/tests/test_native_background.py"
python "$ROOT/port/tests/test_native_sprites.py"
python "$ROOT/port/tests/test_recovery_input_restore.py"
# Assemble the new reset helper without any cartridge/firmware input.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
"$VASM" -quiet -m68020 -Fbin -o "$TMP/reset.bin" "$ROOT/port/src/recovery_reset_ram.s"
