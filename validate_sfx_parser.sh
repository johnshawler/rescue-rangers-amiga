#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
mkdir -p "$ROOT/logs"
python "$ROOT/port/tests/recovery_test_sfx_tick_entry.py" --rom | tee "$ROOT/logs/sfx-tick-rom.log"
python "$ROOT/port/tests/recovery_test_sfx_command_mask.py" --rom | tee "$ROOT/logs/sfx-mask-rom.log"
for choice in 0 16 1 2; do
 CHARACTER_INPUT="$choice" python "$ROOT/port/tests/recovery_test_resident_sfx_command_mask.py" | tee "$ROOT/logs/sfx-mask-input$choice.log"
done
