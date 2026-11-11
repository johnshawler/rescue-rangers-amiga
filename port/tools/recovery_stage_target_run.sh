#!/usr/bin/env bash
# Private fresh stock capture. Events are keyboard callbacks, never RAM inputs.
set -euo pipefail
cd "$(dirname "$0")/../.."
B=$(realpath "${1:?New built output directory}")
N=${2:-11000}
EVENTS=${3:-80:90:13,160:170:13,360:390:13}
[[ ! -e "$B/full.log" && ! -e "$B/full-CHIP.bin" && ! -e "$B/full-capture.s16le" && ! -e "$B/system" ]] || { echo 'Refusing existing capture' >&2; exit 2; }
CORE=${PUAE_CORE:-"$PWD/../amiga-recovery-tools/libretro-uae/puae_libretro.so"}
HEADLESS="$PWD/port/build/experimental-direct-paula/headless"
check() { echo "$1  $2" | sha256sum -c -; }
check 84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456 "$CORE"
check 5a6caac3c484c24a979800188070abb78c7fdbe648106fb84c5d8532e19052b1 "$HEADLESS"
check 6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707 artifacts/a1200-system/kick40068.A1200
mkdir "$B/system"
cp artifacts/a1200-system/kick40068.A1200 "$B/system/"
env -u RAM_LOAD -u RAM_LOAD_FRAME -u KEY_INPUT_EVENTS -u RAM_OUT \
 PUAE_MODEL=A1200OG PUAE_FASTMEM=0 KEY_TICK_EVENTS="$EVENTS" \
 PCM_S16LE_OUT="$B/full-capture.s16le" RAM_MAP_PREFIX="$B/full" REPORT_MARKER=CDRCLIV1 \
 timeout 900 "$HEADLESS" "$CORE" "$B/target.adf" "$B/system" "$N" "$B/full-screen.ppm" > "$B/full.log" 2>&1
python port/tests/recovery_stage_target_verify.py "$B"

python port/tests/recovery_stage_target_replay.py "$B"
python port/tests/recovery_stage_target_noise_pcm.py "$B"
