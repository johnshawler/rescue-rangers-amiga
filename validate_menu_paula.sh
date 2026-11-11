#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
: "${PAULA_HEADLESS:?Set PAULA_HEADLESS to the pinned audio-capture frontend}"
: "${PUAE_CORE:?Set PUAE_CORE to the pinned core}"
# Requires the separately pinned m68k GCC14/binutils, plus plotting dependencies.
mkdir -p "$ROOT/port/build"
container=$(mktemp -d "$ROOT/port/build/menu-paula-validation.XXXXXXXX")
for spec in default:0 default:1 right_hold:1 move_back:1; do
 history=${spec%:*}; display=${spec#*:}; out="$container/$history-$display"
 python "$ROOT/port/tools/recovery_menu_paula_build.py" --output "$out" --history "$history" --display "$display" | tee "$container/$history-$display-build.log"
 python "$ROOT/port/tests/recovery_menu_paula_adapter_test.py" "$out" | tee "$container/$history-$display-adapter.log"
 python "$ROOT/port/tests/recovery_menu_paula_target_rejection_test.py" "$out" | tee "$container/$history-$display-rejections.log"
 bash "$ROOT/port/tools/recovery_menu_paula_run.sh" "$out"
 python "$ROOT/port/tests/recovery_menu_paula_verify.py" "$out" | tee "$container/$history-$display-verify.log"
done
printf 'Private integrated playback evidence: %s\n' "$container"
