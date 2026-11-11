#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
: "${VASM:?Set VASM to the pinned assembler executable}"
# Synthetic contracts only. No cartridge, firmware, extracted assets or ADFs.
for test in \
 recovery_test_startup_bank_select \
 recovery_test_startup_resource_load \
 recovery_test_startup_title_setup \
 recovery_test_active_command02_contract \
 recovery_test_title_fade_yield \
 recovery_test_chr_nmi_contract; do
 python "$ROOT/port/tests/$test.py"
done
