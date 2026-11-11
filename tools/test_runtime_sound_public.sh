#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# New state-selected dispatch and SFX contracts use no private inputs.
for test in \
 recovery_test_sfx_stream_entry \
 recovery_test_sfx_duration_math \
 recovery_test_state_dispatch_palette_contract \
 recovery_test_state_dispatch_active_contract; do
 python "$ROOT/port/tests/$test.py"
done
