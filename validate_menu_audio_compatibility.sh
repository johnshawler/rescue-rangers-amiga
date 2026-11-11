#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# Deliberately separate from the assembler-only aggregate: needs m68k GCC/binutils.
# Every run keeps its private event/plan evidence in a distinct ignored directory.
mkdir -p "$ROOT/port/build" "$ROOT/logs"
container=$(mktemp -d "$ROOT/port/build/menu-audio-audit.XXXXXXXX")
out="$container/evidence"
python "$ROOT/port/tests/recovery_menu_audio_events.py" --rom "$ROOT/input/rescue-rangers-europe.nes" --output "$out" | tee "$container/collector.log"
python "$ROOT/port/tests/recovery_menu_audio_compatibility.py" --profiles "$out" | tee "$container/planner.log"
printf 'Private audit output: %s\n' "$out"
