#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
mkdir -p "$ROOT/logs"
# Host-only extension. The verified private cartridge is the only private input.
for test in recovery_test_sfx_stream_entry recovery_test_sfx_duration_math; do
 python "$ROOT/port/tests/$test.py" --rom | tee "$ROOT/logs/runtime-$test-rom.log"
done
for test in recovery_test_resident_sfx_stream_entry recovery_test_resident_sfx_duration_math; do
 for choice in 0 16 1 2; do
  CHARACTER_INPUT="$choice" python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/runtime-$test-input$choice.log"
 done
done
for test in recovery_test_state_dispatch_prefix recovery_test_state_dispatch_prefix_independent recovery_test_state_dispatch_palette_rom recovery_test_state_dispatch_active_rom; do
 python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/runtime-$test.log"
done
