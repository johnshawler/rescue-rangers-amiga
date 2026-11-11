#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
python port/tests/recovery_audio_clock_test.py
