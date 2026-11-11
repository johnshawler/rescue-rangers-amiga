#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$ROOT/logs" "$ROOT/port/build"
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned puae_libretro.so}"
: "${HEADLESS:?Set HEADLESS to the compiled recovered scripts/headless.c}"
for test in test_native_background test_native_sprites test_rescue_game test_rescue_title test_rescue_title_queue recovery_test_reset_ram recovery_test_reset_mapper recovery_test_reset_video recovery_test_reset_dispatch recovery_test_first_yield recovery_test_first_nmi_prefix recovery_test_nmi_audio_entry recovery_test_audio_reset_command recovery_test_silent_tick_rti recovery_test_scheduler_resume recovery_test_resumed_task_setup recovery_test_palette_nmi_prefix recovery_test_music07_command recovery_test_music_tick_fetch recovery_test_music_command04 recovery_test_music_stream_command05 recovery_test_music_channel_setup recovery_test_gameplay_player_init recovery_test_gameplay_fade_entry recovery_test_stage_resource_init recovery_test_stage_resource_composition recovery_test_music_event_block; do
 python "$ROOT/port/tests/$test.py" | tee "$ROOT/logs/recovery-$test.log"
done
# Native helper chains compared with independently executing original cartridge code.
for test in recovery_test_frame_yield recovery_test_frame_yield_composition recovery_test_general_scheduler recovery_test_general_scheduler_stage_composition recovery_test_general_scheduler_startup_composition recovery_test_idle_nmi_prefix recovery_test_idle_nmi_stage_composition recovery_test_music_channel_iteration recovery_test_music_channel_iteration_chain recovery_test_music_indexed_rom recovery_test_music_indexed_chain recovery_test_music_indexed_continuation recovery_test_music_pitched_gate_rom recovery_test_music_pitched_note_rom recovery_test_music_pitched_event_composition recovery_test_music_pitched_event_chain recovery_test_active_return_rom recovery_test_active_nmi_runtime_chain; do
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
python "$ROOT/port/tools/build_recovery_reset_probe.py" --scheduler-resume | tee "$ROOT/logs/recovery-scheduler-resume-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-scheduler-resume-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-scheduler-resume-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-scheduler-resume-probe.ppm" > "$ROOT/logs/recovery-scheduler-resume-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-scheduler-resume-probe-chip.bin" --scheduler-resume | tee "$ROOT/logs/recovery-scheduler-resume-probe-verified.json"
python "$ROOT/port/tools/build_recovery_reset_probe.py" --resumed-task-setup | tee "$ROOT/logs/recovery-resumed-task-setup-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-resumed-task-setup-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-resumed-task-setup-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-resumed-task-setup-probe.ppm" > "$ROOT/logs/recovery-resumed-task-setup-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-resumed-task-setup-probe-chip.bin" --resumed-task-setup | tee "$ROOT/logs/recovery-resumed-task-setup-probe-verified.json"
python "$ROOT/port/tools/build_recovery_reset_probe.py" --palette-nmi | tee "$ROOT/logs/recovery-palette-nmi-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-palette-nmi-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-palette-nmi-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-palette-nmi-probe.ppm" > "$ROOT/logs/recovery-palette-nmi-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-palette-nmi-probe-chip.bin" --palette-nmi | tee "$ROOT/logs/recovery-palette-nmi-probe-verified.json"
python "$ROOT/port/tests/recovery_test_palette_nmi_target.py" | tee "$ROOT/logs/recovery-palette-nmi-probe-negative.log"
# This opt-in diagnostic contains private cartridge resource data. Never publish it.
python "$ROOT/port/tools/build_recovery_reset_probe.py" --music07 | tee "$ROOT/logs/recovery-music07-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-music07-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-music07-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-music07-probe.ppm" > "$ROOT/logs/recovery-music07-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-music07-probe-chip.bin" --music07 | tee "$ROOT/logs/recovery-music07-probe-verified.json"
python "$ROOT/port/tests/recovery_test_music07_target.py" | tee "$ROOT/logs/recovery-music07-probe-negative.log"
for mode in music-fetch music-command04 music-channel-setup music-first-channel; do
 python "$ROOT/port/tools/build_recovery_reset_probe.py" --"$mode" | tee "$ROOT/logs/recovery-$mode-probe-build.log"
 PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-$mode-probe-chip.bin" \
  timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-$mode-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-$mode-probe.ppm" > "$ROOT/logs/recovery-$mode-probe-amiga.log" 2>&1
 python "$ROOT/port/tests/verify_recovery_reset_probe.py" "$ROOT/port/build/recovery-$mode-probe-chip.bin" --"$mode" | tee "$ROOT/logs/recovery-$mode-probe-verified.json"
done
python "$ROOT/port/tests/recovery_test_first_music_target.py" | tee "$ROOT/logs/recovery-first-music-target-negative.log"
python "$ROOT/port/tests/recovery_test_music_channel_setup_target.py" | tee "$ROOT/logs/recovery-music-channel-setup-target-negative.log"
python "$ROOT/port/tests/recovery_test_music_first_channel_target.py" | tee "$ROOT/logs/recovery-music-first-channel-target-negative.log"
# This independent player-initialization diagnostic uses invented source-only fixtures.
python "$ROOT/port/tools/build_recovery_gameplay_player_init_probe.py" | tee "$ROOT/logs/recovery-gameplay-player-init-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-gameplay-player-init-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-gameplay-player-init-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-gameplay-player-init-probe.ppm" > "$ROOT/logs/recovery-gameplay-player-init-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_gameplay_player_init_probe.py" "$ROOT/port/build/recovery-gameplay-player-init-probe-chip.bin" | tee "$ROOT/logs/recovery-gameplay-player-init-verified.json"
python "$ROOT/port/tests/recovery_test_gameplay_player_init_target.py" | tee "$ROOT/logs/recovery-gameplay-player-init-negative.log"
python "$ROOT/port/tools/build_recovery_gameplay_fade_entry_probe.py" | tee "$ROOT/logs/recovery-gameplay-fade-entry-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-gameplay-fade-entry-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-gameplay-fade-entry-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-gameplay-fade-entry-probe.ppm" > "$ROOT/logs/recovery-gameplay-fade-entry-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_gameplay_fade_entry_probe.py" "$ROOT/port/build/recovery-gameplay-fade-entry-probe-chip.bin" | tee "$ROOT/logs/recovery-gameplay-fade-entry-verified.json"
python "$ROOT/port/tests/recovery_test_gameplay_fade_entry_target.py" | tee "$ROOT/logs/recovery-gameplay-fade-entry-negative.log"
# Private resource-bearing stage diagnostic: never distribute as source-only.
python "$ROOT/port/tools/build_recovery_stage_resource_probe.py" | tee "$ROOT/logs/recovery-stage-resource-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-stage-resource-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-stage-resource-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-stage-resource-probe.ppm" > "$ROOT/logs/recovery-stage-resource-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_stage_resource_probe.py" "$ROOT/port/build/recovery-stage-resource-probe-chip.bin" | tee "$ROOT/logs/recovery-stage-resource-verified.json"
python "$ROOT/port/tests/recovery_test_stage_resource_target.py" | tee "$ROOT/logs/recovery-stage-resource-negative.log"
# Private bounded resident runtime: actual idle/NMI/music/RTI/task continuity.
python "$ROOT/port/tools/build_recovery_runtime_probe.py" | tee "$ROOT/logs/recovery-runtime-probe-build.log"
PUAE_MODEL=A1200OG RAM_OUT="$ROOT/port/build/recovery-runtime-probe-chip.bin" \
 timeout 90 "$HEADLESS" "$PUAE_CORE" "$ROOT/port/build/recovery-runtime-probe.adf" "$ROOT/artifacts/a1200-system" 600 "$ROOT/port/build/recovery-runtime-probe.ppm" > "$ROOT/logs/recovery-runtime-probe-amiga.log" 2>&1
python "$ROOT/port/tests/verify_recovery_runtime_probe.py" "$ROOT/port/build/recovery-runtime-probe-chip.bin" --amiga-log "$ROOT/logs/recovery-runtime-probe-amiga.log" | tee "$ROOT/logs/recovery-runtime-probe-verified.json"
old_dumps=()
for dump in "$ROOT"/port/build/recovery-*-probe-chip.bin; do
 [[ "$dump" == "$ROOT/port/build/recovery-runtime-probe-chip.bin" ]] || old_dumps+=(--old-dump "$dump")
done
python "$ROOT/port/tests/test_recovery_runtime_probe_rejection.py" "$ROOT/port/build/recovery-runtime-probe-chip.bin" --amiga-log "$ROOT/logs/recovery-runtime-probe-amiga.log" "${old_dumps[@]}" | tee "$ROOT/logs/recovery-runtime-probe-rejection.json"
python "$ROOT/port/tests/test_recovery_runtime_build.py" | tee "$ROOT/logs/recovery-runtime-build-tests.log"
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

# Private resident startup/audio extension; baseline probe outputs above are prerequisites.
bash "$ROOT/validate_resident_startup.sh"
bash "$ROOT/validate_title_chr.sh"
bash "$ROOT/validate_native_title.sh"
bash "$ROOT/validate_scene_sound.sh"
bash "$ROOT/validate_runtime_sound.sh"
bash "$ROOT/validate_state_startup.sh"
bash "$ROOT/validate_state_menu.sh"
bash "$ROOT/validate_sfx_phase.sh"
bash "$ROOT/validate_sfx_parser.sh"
bash "$ROOT/validate_sfx_event.sh"
bash "$ROOT/validate_active_sfx.sh"
