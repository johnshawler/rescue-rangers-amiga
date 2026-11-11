#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned puae_libretro.so}"
: "${HEADLESS:?Set HEADLESS to the pinned headless frontend}"
mkdir -p "$ROOT/logs" "$ROOT/port/build"
# This extension needs the private cartridge and firmware, not legacy fixtures.
check_delivered() {
 if [[ -n "${DELIVERED_ADF:-}" ]]; then
  python - "$DELIVERED_ADF" <<'PY'
import hashlib,sys
from pathlib import Path
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() == '6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17', 'Delivered ADF changed'
PY
 fi
}
check_delivered
for test in recovery_test_title_engine_tables recovery_test_title_engine_wait recovery_test_title_menu_loop recovery_test_character_menu_setup recovery_test_queued_video_nmi recovery_test_character_selection_dispatch; do
 python "$ROOT/port/tests/$test.py" --rom | tee "$ROOT/logs/native-$test-rom.log"
done
for test in recovery_test_active_command0e_rom recovery_test_active_command01_rom recovery_test_active_command12_rom recovery_test_active_command12_adversarial recovery_test_active_command13_rom recovery_test_active_command13_adversarial recovery_test_active_command13_slots recovery_test_resident_title_engine_wait recovery_test_resident_title_menu_loop recovery_test_resident_command0e_loop recovery_test_resident_command01_loop recovery_test_resident_command12_loop recovery_test_resident_command13_loop recovery_test_resident_character_menu_setup recovery_test_resident_character_video_queue recovery_test_resident_character_selection; do
 python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/native-$test.log"
done
# Private cartridge-bearing frozen native display; no captured fixture input.
python "$ROOT/port/tools/build_recovery_startup_display.py" | tee "$ROOT/logs/native-startup-display-build.json"
python "$ROOT/port/tests/test_recovery_startup_display_build.py" | tee "$ROOT/logs/native-startup-display-build-test.log"
out="$ROOT/port/build/startup-display-native"
env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
 RAM_OUT="$out/chip.bin" timeout 180 "$HEADLESS" "$PUAE_CORE" \
 "$out/startup-display.adf" "$ROOT/artifacts/a1200-system" 1800 \
 "$out/screen.ppm" > "$out/amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_startup_display.py" | tee "$ROOT/logs/native-startup-display-verified.json"
python "$ROOT/port/tests/test_recovery_startup_display_rejection.py" | tee "$ROOT/logs/native-startup-display-rejection.log"
# Separate instrumented control and renderer experiments, including the slower
# full-unroll result. The accepted compact variant remains an isolated workload.
for variant in baseline optimized paired compact; do
 RR_RENDER_VARIANT="$variant" python "$ROOT/port/tools/build_startup_render_unrolled_experiment.py" | tee "$ROOT/logs/native-render-$variant-build.json"
 out="$ROOT/port/build/startup-render-unrolled-experiment/$variant"
 env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
  RAM_OUT="$out/chip.bin" timeout 180 "$HEADLESS" "$PUAE_CORE" \
  "$out/startup-display.adf" "$ROOT/artifacts/a1200-system" 1800 \
  "$out/screen.ppm" > "$out/amiga.log" 2>&1
 if [[ "$variant" == baseline || "$variant" == compact ]]; then
  env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
   RAM_OUT="$out/repeat-chip.bin" timeout 180 "$HEADLESS" "$PUAE_CORE" \
   "$out/startup-display.adf" "$ROOT/artifacts/a1200-system" 1800 \
   "$out/repeat-screen.ppm" > "$out/repeat-amiga.log" 2>&1
 fi
done
RR_RENDER_VARIANT=compact python "$ROOT/port/tests/test_startup_render_unrolled_build.py" | tee "$ROOT/logs/native-render-build-test.log"
python "$ROOT/port/tests/verify_startup_render_unrolled_experiment.py" | tee "$ROOT/logs/native-render-comparison.json"
check_delivered
