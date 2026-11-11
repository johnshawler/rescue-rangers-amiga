#!/usr/bin/env bash
# Independent private capture, no ROM, no RAM injection, no shared rebuild.
set -euo pipefail
cd "$(dirname "$0")/../.."
B="${1:?Pass NEW diagnostic build output directory from --output}"
B="$(realpath "$B")"
[[ ! -e "$B/run.log" && ! -e "$B/chip.bin" ]] || { echo "Refusing to overwrite capture" >&2; exit 2; }
: "${PUAE_CORE:?Set pinned stock puae_libretro.so path}"
HEADLESS="$PWD/port/build/experimental-direct-paula/headless"
check() { echo "$1  $2" | sha256sum -c -; }
check 84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456 "$PUAE_CORE"
check 5a6caac3c484c24a979800188070abb78c7fdbe648106fb84c5d8532e19052b1 "$HEADLESS"
check 6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707 artifacts/a1200-system/kick40068.A1200
mkdir -p "$B/system"
cp artifacts/a1200-system/kick40068.A1200 "$B/system/"
env -u RAM_LOAD -u RAM_LOAD_FRAME -u RAM_MAP_PREFIX -u KEY_INPUT_EVENTS \
 PUAE_MODEL=A1200OG PUAE_FASTMEM=0 \
 KEY_TICK_EVENTS='10:30:122,20:40:120,50:60:13,70:80:9,90:100:275,110:120:276,130:140:274,150:160:273,170:180:32,190:200:308' \
 RAM_OUT="$B/chip.bin" REPORT_MARKER=CDRCLIV1 \
 timeout 180 "$HEADLESS" "$PUAE_CORE" "$B/input-probe.adf" "$B/system" 1000 > "$B/run.log" 2>&1
python port/tests/recovery_zx_verify.py --output "$B"
