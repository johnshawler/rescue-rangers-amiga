#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# Synthetic source-only contracts. No ROM, firmware, fixtures or private disks.
for test in \
 recovery_test_title_engine_tables \
 recovery_test_title_engine_wait \
 recovery_test_title_menu_loop \
 recovery_test_active_command0e_contract \
 recovery_test_active_command01_contract \
 recovery_test_active_command12_contract \
 recovery_test_active_command13_contract \
 recovery_test_character_menu_setup \
 recovery_test_queued_video_nmi \
 recovery_test_character_selection_dispatch \
 test_recovery_startup_display_device \
 test_startup_render_unrolled_experiment; do
 python "$ROOT/port/tests/$test.py"
done
