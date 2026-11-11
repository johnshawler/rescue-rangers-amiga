#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$ROOT/logs" "$ROOT/port/build"
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned puae_libretro.so}"
: "${HEADLESS:?Set HEADLESS to the compiled recovered scripts/headless.c}"
for test in test_native_background test_native_sprites test_rescue_game test_rescue_title test_rescue_title_queue recovery_test_reset_ram recovery_test_reset_mapper recovery_test_reset_video recovery_test_reset_dispatch recovery_test_first_yield recovery_test_first_nmi_prefix recovery_test_nmi_audio_entry recovery_test_audio_reset_command recovery_test_silent_tick_rti; do
 python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/recovery-$test.log"
done
python "$ROOT/port/tools/build_recovery_reset_probe.py" | tee "$ROOT/logs/recovery-reset-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-reset-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-reset-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-reset-probe.ppm" > "$ROOT/logs/recovery-reset-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-reset-probe-chip.bin" | tee "$ROOT/logs/recovery-reset-probe-verified.json"
python "$ROOT/port/tools/build_recovery_reset_probe.py" --first-yield | tee "$ROOT/logs/recovery-first-yield-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-first-yield-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-first-yield-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-first-yield-probe.ppm" > "$ROOT/logs/recovery-first-yield-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-first-yield-probe-chip.bin" --first-yield | tee "$ROOT/logs/recovery-first-yield-probe-verified.json"
python "$ROOT/port/tools/build_recovery_reset_probe.py" --nmi-audio-entry | tee "$ROOT/logs/recovery-nmi-audio-entry-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-nmi-audio-entry-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-nmi-audio-entry-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-nmi-audio-entry-probe.ppm" > "$ROOT/logs/recovery-nmi-audio-entry-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-nmi-audio-entry-probe-chip.bin" --nmi-audio-entry | tee "$ROOT/logs/recovery-nmi-audio-entry-probe-verified.json"
python "$ROOT/port/tools/build_recovery_reset_probe.py" --audio-reset | tee "$ROOT/logs/recovery-audio-reset-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-audio-reset-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-audio-reset-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-audio-reset-probe.ppm" > "$ROOT/logs/recovery-audio-reset-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-audio-reset-probe-chip.bin" --audio-reset | tee "$ROOT/logs/recovery-audio-reset-probe-verified.json"
python "$ROOT/port/tools/build_recovery_reset_probe.py" --nmi-return | tee "$ROOT/logs/recovery-nmi-return-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-nmi-return-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-nmi-return-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-nmi-return-probe.ppm" > "$ROOT/logs/recovery-nmi-return-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-nmi-return-probe-chip.bin" --nmi-return | tee "$ROOT/logs/recovery-nmi-return-probe-verified.json"
python "$ROOT/port/tools/build_title.py" | tee "$ROOT/logs/recovery-build.log"
python - "$ROOT" <<'PY'
import hashlib,sys
from pathlib import Path
f=Path(sys.argv[1])/'port/build/rescue-rangers-title.adf'
assert hashlib.sha256(f.read_bytes()).hexdigest()=='03b774d76a6b547ff6b4b3ffd71428d381247f4802a40bab1a56eb3d1ea2b475'
print('PASS byte-identical archived title ADF')
PY
for name in title two-player character-chip character-dale handoff; do
 joy=''; keys=''; reference="$name"
 case "$name" in
  two-player) joy='300:305:128';;
  character-chip) keys='300:305:13';;
  character-dale) keys='300:305:13';joy='400:405:128';;
  handoff) joy='300:305:128';keys='400:405:13';reference=two-player;;
 esac
 PUAE_MODEL=A1200OG PORT_INPUT_EVENTS="$joy" KEY_INPUT_EVENTS="$keys" RAM_OUT="$ROOT/port/build/$name-chip-ram.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/rescue-rangers-title.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/$name-amiga.ppm" > "$ROOT/logs/amiga-$name.log" 2>&1
 python "$ROOT/port/tests/verify_title.py" "$name" "$reference" | tee "$ROOT/logs/recovery-verify-$name.log"
done
