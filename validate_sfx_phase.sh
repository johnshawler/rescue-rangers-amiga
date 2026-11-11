#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
mkdir -p "$ROOT/logs"
python "$ROOT/port/tests/recovery_test_sfx_phase_dispatch.py" --rom | tee "$ROOT/logs/sfx-phase-rom.log"
for choice in 0 16 1 2; do
 CHARACTER_INPUT="$choice" python "$ROOT/port/tests/recovery_test_resident_sfx_phase_dispatch.py" | tee "$ROOT/logs/sfx-phase-input$choice.log"
done
