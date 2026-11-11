#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned puae_libretro.so}"
: "${HEADLESS:?Set HEADLESS to the pinned headless frontend}"
ROM="$ROOT/input/rescue-rangers-europe.nes"
mkdir -p "$ROOT/logs"
python "$ROOT/port/tests/recovery_test_sfx_channel_reconfigure.py" --rom | tee "$ROOT/logs/state-sfx-channel-rom.log"
for choice in 0 16 1 2; do
 CHARACTER_INPUT="$choice" python "$ROOT/port/tests/recovery_test_resident_sfx_channel_reconfigure.py" | tee "$ROOT/logs/state-sfx-channel-input$choice.log"
done
# These original-code runners require --rom followed by a path, not a Boolean.
python "$ROOT/port/tests/recovery_test_state_dispatch_scheduler_rom.py" --rom "$ROM" | tee "$ROOT/logs/state-scheduler-rom.log"
python "$ROOT/port/tests/recovery_state_dispatch_startup_rom.py" --rom "$ROM" | tee "$ROOT/logs/state-startup-rom.log"
python "$ROOT/port/tools/build_recovery_state_startup_display.py" | tee "$ROOT/logs/state-display-build.json"
python "$ROOT/port/tests/test_recovery_state_startup_display_build.py" | tee "$ROOT/logs/state-display-build-test.json"
out="$ROOT/port/build/recovery_state_startup_display"
# Held diagnostic: neutral input and externally scripted logical NMIs, not live controls.
for prefix in '' repeat-; do
 env -u RAM_LOAD -u RAM_LOAD_FRAME -u RAM_MAP_PREFIX -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
  RAM_OUT="$out/${prefix}chip.bin" timeout 180 "$HEADLESS" "$PUAE_CORE" \
  "$out/recovery_state_startup_display.adf" "$ROOT/artifacts/a1200-system" \
  1800 "$out/${prefix}screen.ppm" > "$out/${prefix}amiga.log" 2>&1
done
python "$ROOT/port/tests/verify_recovery_state_startup_display.py" | tee "$ROOT/logs/state-display-verified.json"
python "$ROOT/port/tests/test_recovery_state_startup_display_rejection.py" | tee "$ROOT/logs/state-display-rejections.json"
python "$ROOT/port/tests/test_recovery_startup_display_device.py" | tee "$ROOT/logs/state-display-device.json"
