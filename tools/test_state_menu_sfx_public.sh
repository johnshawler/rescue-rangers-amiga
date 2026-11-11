#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
for test in audit contract edges tail_contract; do
 python "$ROOT/port/tests/recovery_state_menu_sfx_$test.py"
done
for suite in menu music long; do
 python "$ROOT/port/tests/recovery_state_menu_sfx_regression.py" "$suite"
done
# This is the unchanged predecessor, not its rejection contract on the new entry.
python "$ROOT/port/tests/recovery_state_dispatch_startup_contract.py"
