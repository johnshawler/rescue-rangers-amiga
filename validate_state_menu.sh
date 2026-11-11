#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
ROM="$ROOT/input/rescue-rangers-europe.nes"
mkdir -p "$ROOT/logs"
# Original-first host comparisons, not target rendering or live controls.
python "$ROOT/port/tests/recovery_state_dispatch_menu_rom.py" --rom "$ROM" | tee "$ROOT/logs/state-menu-rom.json"
python "$ROOT/port/tests/recovery_state_dispatch_menu_long_rom.py" --rom "$ROM" | tee "$ROOT/logs/state-menu-long-rom.json"

# Actual stock-target first-character-menu display, with scripted input only.
: "${PUAE_CORE:?Set PUAE_CORE to the pinned puae_libretro.so}"
: "${HEADLESS:?Set HEADLESS to the pinned headless frontend}"
python "$ROOT/port/tools/build_recovery_state_menu_display.py" | tee "$ROOT/logs/state-menu-display-build.json"
python "$ROOT/port/tests/test_recovery_state_menu_display_build.py" | tee "$ROOT/logs/state-menu-display-build-test.json"
out="$ROOT/port/build/recovery_state_menu_display"
for prefix in '' repeat-; do
 env -u RAM_LOAD -u RAM_LOAD_FRAME -u RAM_MAP_PREFIX -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
  RAM_OUT="$out/${prefix}chip.bin" timeout 240 "$HEADLESS" "$PUAE_CORE" \
  "$out/recovery_state_menu_display.adf" "$ROOT/artifacts/a1200-system" \
  6000 "$out/${prefix}screen.ppm" > "$out/${prefix}amiga.log" 2>&1
done
python "$ROOT/port/tests/verify_recovery_state_menu_display.py" | tee "$ROOT/logs/state-menu-display-verified.json"
python "$ROOT/port/tests/test_recovery_state_menu_display_rejection.py" | tee "$ROOT/logs/state-menu-display-rejections.json"
