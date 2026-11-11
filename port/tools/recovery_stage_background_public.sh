#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_stage_background_test.py
python port/tests/recovery_stage_background_adversarial_test.py
