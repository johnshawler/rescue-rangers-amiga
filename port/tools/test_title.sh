#!/usr/bin/env bash
set -euo pipefail
L=$(cd "$(dirname "$0")/../.." && pwd)
T=${NES_AMIGA_TOOLCHAIN:-"$(dirname "$L")/nes-amiga-lab"}
export VASM=${VASM:-"$T/repos/vscode-amiga-debug/bin/linux/vasmm68k_mot"}
export PYTHONPATH="/tmp/nes-sprite-test-deps:/tmp/rescue-py65:${PYTHONPATH:-}"
python3 "$L/port/tests/test_native_background.py" | tee "$L/logs/test-background.log"
python3 "$L/port/tests/test_native_sprites.py" | tee "$L/logs/test-sprites.log"
python3 "$L/port/tests/test_rescue_game.py" | tee "$L/logs/test-game.log"
python3 "$L/port/tests/test_rescue_title.py" | tee "$L/logs/test-title.log"
python3 "$L/port/tests/test_rescue_title_queue.py" | tee "$L/logs/test-title-queue.log"
python3 "$L/port/tools/build_title.py" | tee "$L/logs/build-title.log"
for n in title two-player character-chip character-dale handoff; do
 joy=''; keys=''; ref="$n"
 case "$n" in two-player) joy='300:305:128';; character-chip) keys='300:305:13';; character-dale) keys='300:305:13';joy='400:405:128';; handoff) joy='300:305:128';keys='400:405:13';ref=two-player;; esac
 PUAE_MODEL=A1200OG PORT_INPUT_EVENTS="$joy" KEY_INPUT_EVENTS="$keys" RAM_OUT="$L/port/build/$n-chip-ram.bin" \
  timeout 90 "$L/scripts/headless" "$T/repos/puae/puae_libretro.so" "$L/port/build/rescue-rangers-title.adf" "$L/artifacts/a1200-system" 600 "$L/port/build/$n-amiga.ppm" > "$L/logs/amiga-$n.log" 2>&1
 python3 "$L/port/tests/verify_title.py" "$n" "$ref" | tee "$L/logs/verify-$n.log"
done
