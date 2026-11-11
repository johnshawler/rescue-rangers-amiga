#!/usr/bin/env bash
# Run a NEW output directory. No snapshots, original tools or delivered disks changed.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
B=${1:?Absolute output directory containing target.adf}
HEADLESS=${PAULA_HEADLESS:-"$ROOT/port/build/experimental-direct-paula/headless"}
CORE=${PUAE_CORE:-"$ROOT/../amiga-recovery-tools/libretro-uae/puae_libretro.so"}
test ! -e "$B/full.log"
mkdir "$B/system"
cp "$ROOT/artifacts/a1200-system/kick40068.A1200" "$B/system/"
env -u RAM_LOAD -u RAM_LOAD_FRAME -u RAM_MAP_PREFIX -u PUAE_FASTMEM PUAE_MODEL=A1200OG PCM_S16LE_OUT="$B/full-capture.s16le" RAM_MAP_PREFIX="$B/full" REPORT_MARKER=CDRPAU01 timeout 400 "$HEADLESS" "$CORE" "$B/target.adf" "$B/system" 6000 "$B/full-screen.ppm" > "$B/full.log" 2>&1
