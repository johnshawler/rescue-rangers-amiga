#!/usr/bin/env bash
set -euo pipefail
L=$(cd "$(dirname "$0")/.." && pwd)
T=${NES_AMIGA_TOOLCHAIN:-"$(dirname "$L")/nes-amiga-lab"}
mkdir -p "$L/artifacts/nes-system" "$L/logs" "$L/port/assets"
gcc -O2 -I "$T/repos/fceumm/src/drivers/libretro/libretro-common/include" "$L/scripts/headless.c" -o "$L/scripts/headless" -ldl -Wl,--no-as-needed -lm
NES_PORT_SNAPSHOT="$L/port/assets/title-snapshot.bin" NES_SNAPSHOT_FRAME=200 RAM_OUT="$L/artifacts/title-ram.bin" \
 timeout 60 "$L/scripts/headless" "$T/repos/fceumm/fceumm_libretro.so" "$L/input/rescue-rangers-europe.nes" "$L/artifacts/nes-system" 200 "$L/artifacts/title-reference.ppm" > "$L/logs/nes-title.log" 2>&1
PORT_INPUT_EVENTS='240:245:8,500:505:8,750:755:8,1000:1005:8' NES_PORT_SNAPSHOT="$L/port/assets/gameplay-snapshot.bin" NES_SNAPSHOT_FRAME=1200 RAM_OUT="$L/artifacts/gameplay-ram.bin" \
 timeout 60 "$L/scripts/headless" "$T/repos/fceumm/fceumm_libretro.so" "$L/input/rescue-rangers-europe.nes" "$L/artifacts/nes-system" 1200 "$L/artifacts/gameplay-reference.ppm" > "$L/logs/nes-gameplay.log" 2>&1
for n in two-player character-chip character-dale; do
 case "$n" in two-player) events='240:245:128';; character-chip) events='240:245:8';; character-dale) events='240:245:8,270:275:128';; esac
 PORT_INPUT_EVENTS="$events" NES_PORT_SNAPSHOT="$L/port/assets/$n-snapshot.bin" NES_SNAPSHOT_FRAME=300 RAM_OUT="$L/artifacts/$n-ram.bin" \
  timeout 60 "$L/scripts/headless" "$T/repos/fceumm/fceumm_libretro.so" "$L/input/rescue-rangers-europe.nes" "$L/artifacts/nes-system" 300 "$L/artifacts/$n-reference.ppm" > "$L/logs/nes-$n.log" 2>&1
done
python3 - "$L" <<'PY'
from PIL import Image
from pathlib import Path
import sys
L=Path(sys.argv[1])
for n in ['title','gameplay','two-player','character-chip','character-dale']:
    Image.open(L/f'artifacts/{n}-reference.ppm').save(L/f'artifacts/{n}-reference.png')
PY
