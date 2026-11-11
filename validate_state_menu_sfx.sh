#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
mkdir -p "$ROOT/logs"
for test in tail_contract long_rom rom; do
 python "$ROOT/port/tests/recovery_state_menu_sfx_$test.py" --rom "$ROOT/input/rescue-rangers-europe.nes" | tee "$ROOT/logs/state-menu-sfx-$test.log"
done
