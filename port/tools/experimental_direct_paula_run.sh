#!/usr/bin/env bash
# Private title-profile diagnostic; never publish its build directory.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
WORK=$(dirname "$ROOT")
TOOLS=${PAULA_TOOLS:-"$WORK/amiga-recovery-tools"}
PROFILE=${1:?Supply the separately verified private title APU profile JSON}
source "${PAULA_M68K_ACTIVATE:-$WORK/amiga-recovery-m68k/activate.sh}"
export VASM=${VASM:-"$TOOLS/vscode-amiga-debug/bin/linux/vasmm68k_mot"}
export PYTHONPATH="${PAULA_DEPS:-$WORK/rescue-recovery-inspection/.deps}:${PYTHONPATH:-}"
B="$ROOT/port/build/experimental-direct-paula"
mkdir -p "$B/system"
python "$ROOT/port/tests/experimental_direct_paula_test.py"
python "$ROOT/port/tools/experimental_direct_paula_build.py" "$PROFILE"
cp -n "$ROOT/artifacts/a1200-system/kick40068.A1200" "$B/system/"
gcc -O2 -I "$TOOLS/libretro-uae/libretro-common/include" "$ROOT/port/tools/experimental_paula_headless.c" -Wl,--no-as-needed -lm -ldl -o "$B/headless"
PUAE_MODEL=A1200OG PUAE_FASTMEM=0 PCM_S16LE_OUT="$B/capture.s16le" RAM_MAP_PREFIX="$B/stock" REPORT_MARKER=DIRPAU01 \
 timeout 220 "$B/headless" "${PUAE_CORE:-$TOOLS/libretro-uae/puae_libretro.so}" "$B/private-replay.adf" "$B/system" 1800 "$B/stock.ppm" > "$B/stock.log" 2>&1
python "$ROOT/port/tests/experimental_direct_paula_capture.py" "$B"
