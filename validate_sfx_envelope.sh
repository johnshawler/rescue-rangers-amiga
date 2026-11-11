#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
mkdir -p "$ROOT/logs"
python "$ROOT/port/tests/recovery_test_sfx_envelope.py" --rom | tee "$ROOT/logs/sfx-envelope-rom.log"
python "$ROOT/port/tests/recovery_test_sfx_envelope_edges.py" --rom | tee "$ROOT/logs/sfx-envelope-edges-rom.log"
python "$ROOT/port/tests/recovery_test_sfx_envelope_audit.py" --rom | tee "$ROOT/logs/sfx-envelope-audit-rom.log"
for choice in 0 16 1 2; do
 CHARACTER_INPUT="$choice" python "$ROOT/port/tests/recovery_test_resident_sfx_envelope.py" --rom | tee "$ROOT/logs/sfx-envelope-input$choice.log"
done
for choice in 1 2; do
 CHARACTER_INPUT="$choice" AUDIO_RETURN_CAP=118 python "$ROOT/port/tests/recovery_test_resident_sfx_envelope.py" --rom | tee "$ROOT/logs/sfx-envelope-long-input$choice.log"
done
