#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned puae_libretro.so}"
: "${HEADLESS:?Set HEADLESS to the pinned headless frontend}"
mkdir -p "$ROOT/logs"
# This extension uses only the private cartridge and firmware, not legacy fixtures.
for test in recovery_test_post_confirmation_entry recovery_test_scene_palette_entry recovery_test_scene_sprite_hide recovery_test_character_cursor_sound_request recovery_test_pending_sfx27_dispatch recovery_test_sfx_header_initialize recovery_test_sfx_initialized_tail; do
 python "$ROOT/port/tests/$test.py" --rom | tee "$ROOT/logs/scene-$test-rom.log"
done
for test in recovery_test_active_command0f_rom recovery_test_active_command0f_adversarial recovery_test_active_command0f_slots recovery_test_resident_command0f_loop; do
 python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/scene-$test.log"
done
for test in recovery_test_resident_post_confirmation recovery_test_resident_scene_palette recovery_test_resident_scene_sprite recovery_test_resident_character_cursor_sound recovery_test_resident_pending_sfx27 recovery_test_resident_sfx_header; do
 for choice in 0 1 2 16; do
  CHARACTER_INPUT="$choice" python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/scene-$test-input$choice.log"
 done
done
# Target execution is a fixed diagnostic schedule with scripted controller bytes.
# It does not implement live Amiga controls or real-time logical NMI timing.
python "$ROOT/port/tools/build_recovery_character_confirmation_probe.py" | tee "$ROOT/logs/scene-character-target-build.json"
args=()
if [[ -n "${DELIVERED_ADF:-}" ]]; then args+=(--delivered-adf "$DELIVERED_ADF"); fi
python "$ROOT/port/tests/test_recovery_character_confirmation_build.py" "${args[@]}" | tee "$ROOT/logs/scene-character-target-build-test.json"
out="$ROOT/port/build/character-confirmation-stock"
for window in 0 1 2 3 4; do
 env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM -u RAM_MAP_PREFIX PUAE_MODEL=A1200OG \
  RAM_OUT="$out/recovery-character-confirmation-w$window-chip.bin" timeout 180 "$HEADLESS" "$PUAE_CORE" \
  "$out/recovery-character-confirmation-w$window.adf" "$ROOT/artifacts/a1200-system" 1800 \
  > "$out/w$window-amiga.log" 2>&1
done
python "$ROOT/port/tests/verify_recovery_character_confirmation_probe.py" "$out" | tee "$ROOT/logs/scene-character-target-verified.json"
env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM -u RAM_MAP_PREFIX PUAE_MODEL=A1200OG \
 RAM_OUT="$out/repeat-w0-chip.bin" timeout 180 "$HEADLESS" "$PUAE_CORE" \
 "$out/recovery-character-confirmation-w0.adf" "$ROOT/artifacts/a1200-system" 1800 \
 > "$out/repeat-w0-amiga.log" 2>&1
python - "$ROOT" "$out" <<'PY'
import json,sys
from pathlib import Path
root,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(root/'port/tests'))
from verify_recovery_character_confirmation_probe import verify,verify_amiga_log
dump=(out/'repeat-w0-chip.bin').read_bytes()
assert dump==(out/'recovery-character-confirmation-w0-chip.bin').read_bytes()
result=verify(dump,(root/'input/rescue-rangers-europe.nes').read_bytes(),0)
result['actual_target']=verify_amiga_log((out/'repeat-w0-amiga.log').read_text())
result['entire_Chip_dump_identical']=True
print(json.dumps(result,indent=2))
PY
python "$ROOT/port/tests/test_recovery_character_confirmation_probe_rejection.py" "$out" | tee "$ROOT/logs/scene-character-target-rejection.json"
