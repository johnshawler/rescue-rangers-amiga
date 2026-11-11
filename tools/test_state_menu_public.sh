#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# Synthetic menu and music-adapter contracts; no cartridge or private imports.
python "$ROOT/port/tests/recovery_state_dispatch_menu_contract.py"
python "$ROOT/port/tests/recovery_state_dispatch_menu_music_contract.py"
python "$ROOT/port/tests/recovery_state_dispatch_menu_long_contract.py"
python "$ROOT/port/tests/test_recovery_state_menu_display_device.py"
