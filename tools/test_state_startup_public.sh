#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# ROM-free contracts for new sound-channel and live-state startup adapters.
python "$ROOT/port/tests/recovery_test_sfx_channel_reconfigure.py"
python "$ROOT/port/tests/recovery_test_state_dispatch_scheduler_contract.py"
python "$ROOT/port/tests/recovery_state_dispatch_startup_contract.py"
