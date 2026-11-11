#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${HEADLESS:?Set HEADLESS to the verified frontend}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned core}"
mkdir -p "$ROOT/logs"
python "$ROOT/port/tools/build_recovery_menu_sfx_target.py" | tee "$ROOT/logs/menu-sfx-target-build.log"
python "$ROOT/port/tests/recovery_menu_sfx_target_build_test.py" | tee "$ROOT/logs/menu-sfx-target-rebuild.log"
python "$ROOT/port/tests/recovery_menu_sfx_target_contract.py" | tee "$ROOT/logs/menu-sfx-target-contract.log"
python "$ROOT/port/tests/recovery_menu_sfx_target_adapter_test.py" | tee "$ROOT/logs/menu-sfx-target-adapter.log"
python "$ROOT/port/tests/recovery_state_menu_sfx_long_rom.py" --rom "$ROOT/input/rescue-rangers-europe.nes" | tee "$ROOT/logs/menu-sfx-target-long.log"
out="$ROOT/port/build/recovery_menu_sfx_target"
for history in default right_hold move_back; do
 for prefix in '' repeat-; do
  env -u RAM_LOAD -u RAM_LOAD_FRAME -u RAM_MAP_PREFIX -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
  RAM_OUT="$out/$history/${prefix}chip.bin" timeout 180 "$HEADLESS" "$PUAE_CORE" \
  "$out/$history/recovery_menu_sfx_target.adf" "$ROOT/artifacts/a1200-system" \
  6000 "$out/$history/${prefix}screen.ppm" > "$out/$history/${prefix}amiga.log" 2>&1
 done
done
python "$ROOT/port/tests/verify_recovery_menu_sfx_target.py" | tee "$ROOT/logs/menu-sfx-target-verify.log"
python "$ROOT/port/tests/recovery_menu_sfx_target_rejection_test.py" | tee "$ROOT/logs/menu-sfx-target-reject.log"
