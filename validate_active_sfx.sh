#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
mkdir -p "$ROOT/logs"
python "$ROOT/port/tests/recovery_test_sfx_active_control.py" --rom | tee "$ROOT/logs/active-sfx-rom.log"
# This resident runner requires explicit --rom, unlike earlier resident runners.
for choice in 0 16 1 2; do
 CHARACTER_INPUT="$choice" python "$ROOT/port/tests/recovery_test_resident_sfx_active_control.py" --rom | tee "$ROOT/logs/active-sfx-input$choice.log"
done
