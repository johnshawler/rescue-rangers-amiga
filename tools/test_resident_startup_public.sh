#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# Synthetic native contracts only. No cartridge, firmware, extracts or target media.
for test in test_recovery_startup_fade_native_contract test_recovery_startup_fade_alu recovery_test_music_duration_prepare_contract recovery_test_music_duration_progress_contract recovery_test_envelope_declarative_contract recovery_test_active_control_contract recovery_test_active_command03_contract recovery_test_empty_queue_entry recovery_test_startup_video_clear; do
 python "$ROOT/port/tests/$test.py"
done
