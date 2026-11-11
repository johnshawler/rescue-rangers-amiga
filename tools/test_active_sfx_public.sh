#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# The isolated runner executes the complete default suite with private reads denied.
python "$ROOT/port/tests/recovery_test_sfx_active_control_isolated.py"
