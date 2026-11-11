#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
mkdir -p "$ROOT/logs"
python "$ROOT/port/tests/recovery_test_sfx_event_action.py" --rom | tee "$ROOT/logs/sfx-event-rom.log"
for choice in 0 16 1 2; do
 CHARACTER_INPUT="$choice" python "$ROOT/port/tests/recovery_test_resident_sfx_event_action.py" | tee "$ROOT/logs/sfx-event-input$choice.log"
done
for choice in 1 2; do
 CHARACTER_INPUT="$choice" NEXT_TICK_BOUNDARY=1 python "$ROOT/port/tests/recovery_test_resident_sfx_event_action.py" | tee "$ROOT/logs/sfx-event-next-tick$choice.log"
done
