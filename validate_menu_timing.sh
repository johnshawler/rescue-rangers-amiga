#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${HEADLESS:?Set HEADLESS to the verified frontend}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned core}"
mkdir -p "$ROOT/logs"
python "$ROOT/port/tools/build_recovery_menu_timing.py" | tee "$ROOT/logs/menu-timing-build.log"
python "$ROOT/port/tests/recovery_menu_timing_build_test.py" | tee "$ROOT/logs/menu-timing-rebuild.log"
python "$ROOT/port/tests/recovery_menu_timing_contract.py" | tee "$ROOT/logs/menu-timing-contract.log"
out="$ROOT/port/build/recovery_menu_timing"
for prefix in '' repeat-; do
 env -u RAM_LOAD -u RAM_LOAD_FRAME -u RAM_MAP_PREFIX -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
 RAM_OUT="$out/${prefix}chip.bin" timeout 180 "$HEADLESS" "$PUAE_CORE" \
 "$out/recovery_menu_timing.adf" "$ROOT/artifacts/a1200-system" \
 6000 "$out/${prefix}screen.ppm" > "$out/${prefix}amiga.log" 2>&1
done
python "$ROOT/port/tests/verify_recovery_menu_timing.py" | tee "$ROOT/logs/menu-timing-verify.log"
python "$ROOT/port/tests/recovery_menu_timing_rejection_test.py" | tee "$ROOT/logs/menu-timing-reject.log"
