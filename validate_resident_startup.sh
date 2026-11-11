#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$ROOT/logs" "$ROOT/port/build"
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned puae_libretro.so}"
: "${HEADLESS:?Set HEADLESS to the pinned headless frontend}"
# Extension to validate_recovery.sh, which first builds/verifies the baseline
# probes. Those current outputs are explicit inputs to preservation/cross-mode tests.
for mode in reset first-yield nmi-audio-entry audio-reset nmi-return scheduler-resume resumed-task-setup palette-nmi music07 music-fetch music-command04 music-channel-setup music-first-channel gameplay-player-init gameplay-fade-entry stage-resource runtime; do
 for suffix in bin adf chip.bin; do
  file="$ROOT/port/build/recovery-$mode-probe.$suffix"
  [[ "$suffix" != chip.bin ]] || file="$ROOT/port/build/recovery-$mode-probe-chip.bin"
  if [[ ! -f "$file" ]]; then
   printf 'Missing baseline output: %s. Run validate_recovery.sh first.\n' "$file" >&2
   exit 2
  fi
 done
done
for test in recovery_test_startup_fade_continue recovery_test_startup_fade_yield_chain recovery_test_music_duration_prepare_rom recovery_test_music_duration_progress_rom recovery_test_active_envelope_rom recovery_test_envelope_declarative_rom recovery_test_active_control_rom recovery_test_active_command03_rom recovery_test_resident_startup_fade recovery_test_resident_startup_video; do
 python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/recovery-$test.log"
done
python "$ROOT/port/tests/recovery_test_empty_queue_entry.py" --rom | tee "$ROOT/logs/recovery-empty-queue-rom.log"
python "$ROOT/port/tests/recovery_test_startup_video_clear.py" --rom | tee "$ROOT/logs/recovery-startup-video-rom.log"
python "$ROOT/port/tests/recovery_test_repeated_active_audio.py" --ticks 41 | tee "$ROOT/logs/recovery-repeated-active-audio-41.log"
# Private cartridge-bearing diagnostic. Never distribute this generated disk.
python "$ROOT/port/tools/build_recovery_resident_fade_probe.py" | tee "$ROOT/logs/recovery-resident-fade-build.json"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-resident-fade-probe-chip.bin" \
 timeout 180 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-resident-fade-probe.adf" "$ROOT/artifacts/a1200-system" 1800 > "$ROOT/logs/recovery-resident-fade-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_resident_fade_probe.py" "$ROOT/port/build/recovery-resident-fade-probe-chip.bin" --amiga-log "$ROOT/logs/recovery-resident-fade-probe-amiga.log" | tee "$ROOT/logs/recovery-resident-fade-probe-verified.json"
old_dumps=()
for dump in "$ROOT"/port/build/recovery-*-probe-chip.bin; do
 [[ "$dump" == "$ROOT/port/build/recovery-resident-fade-probe-chip.bin" ]] || old_dumps+=(--old-dump "$dump")
done
python "$ROOT/port/tests/test_recovery_resident_fade_probe_rejection.py" "$ROOT/port/build/recovery-resident-fade-probe-chip.bin" --amiga-log "$ROOT/logs/recovery-resident-fade-probe-amiga.log" "${old_dumps[@]}" | tee "$ROOT/logs/recovery-resident-fade-probe-rejection.json"
python "$ROOT/port/tests/test_recovery_resident_fade_build.py" | tee "$ROOT/logs/recovery-resident-fade-build-tests.json"
