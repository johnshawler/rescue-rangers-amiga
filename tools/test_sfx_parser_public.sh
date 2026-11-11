#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
python "$ROOT/port/tests/recovery_test_sfx_tick_entry.py"
python "$ROOT/port/tests/recovery_test_sfx_command_mask.py"
