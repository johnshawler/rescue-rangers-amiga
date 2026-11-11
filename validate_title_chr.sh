#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned puae_libretro.so}"
: "${HEADLESS:?Set HEADLESS to the pinned headless frontend}"
mkdir -p "$ROOT/logs" "$ROOT/port/build"
for test in recovery_test_startup_bank_select recovery_test_startup_resource_load recovery_test_startup_title_setup recovery_test_title_fade_yield; do
 python "$ROOT/port/tests/$test.py" --rom | tee "$ROOT/logs/$test-rom.log"
done
for test in recovery_test_active_command02_rom recovery_test_repeated_command02_audio recovery_test_resident_startup_bank recovery_test_resident_startup_resources recovery_test_chr_nmi_rom recovery_test_chr_nmi_latch recovery_test_resident_title_chr_fade; do
 python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/$test.log"
done
# Private cartridge-bearing diagnostics: never distribute the generated disks.
OUT="$ROOT/port/build/chr-fade-stock"
python "$ROOT/port/tools/build_recovery_resident_chr_fade_probe.py" | tee "$ROOT/logs/recovery-resident-chr-fade-build.json"
for window in 0 1 2 3; do
 env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM \
  PUAE_MODEL=A1200OG RAM_OUT="$OUT/recovery-resident-chr-fade-w$window-chip.bin" \
  timeout 180 "$HEADLESS" "$PUAE_CORE" "$OUT/recovery-resident-chr-fade-w$window.adf" \
  "$ROOT/artifacts/a1200-system" 1800 > "$OUT/w$window-amiga.log" 2>&1
done
python "$ROOT/port/tests/verify_recovery_resident_chr_fade_probe.py" "$OUT" | tee "$ROOT/logs/recovery-resident-chr-fade-verified.json"
python "$ROOT/port/tests/test_recovery_resident_chr_fade_probe_rejection.py" "$OUT" | tee "$ROOT/logs/recovery-resident-chr-fade-rejection.json"
optional=()
if [[ -n "${DELIVERED_ADF:-}" ]]; then
 optional+=(--delivered-adf "$DELIVERED_ADF")
fi
python "$ROOT/port/tests/test_recovery_resident_chr_fade_build.py" "${optional[@]}" | tee "$ROOT/logs/recovery-resident-chr-fade-build-tests.json"
