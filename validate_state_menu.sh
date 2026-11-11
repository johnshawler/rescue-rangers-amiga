#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
ROM="$ROOT/input/rescue-rangers-europe.nes"
mkdir -p "$ROOT/logs"
# Original-first host comparisons, not target rendering or live controls.
python "$ROOT/port/tests/recovery_state_dispatch_menu_rom.py" --rom "$ROM" | tee "$ROOT/logs/state-menu-rom.json"
python "$ROOT/port/tests/recovery_state_dispatch_menu_long_rom.py" --rom "$ROM" | tee "$ROOT/logs/state-menu-long-rom.json"
