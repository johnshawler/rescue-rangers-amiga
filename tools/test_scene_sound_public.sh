#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# Pure synthetic contracts; no cartridge, firmware or captured fixtures.
for test in \
 recovery_test_active_command0f_contract \
 recovery_test_post_confirmation_entry \
 recovery_test_scene_palette_entry \
 recovery_test_scene_sprite_hide \
 recovery_test_character_cursor_sound_request \
 recovery_test_pending_sfx27_dispatch \
 recovery_test_sfx_header_initialize \
 recovery_test_sfx_initialized_tail; do
 python "$ROOT/port/tests/$test.py"
done
