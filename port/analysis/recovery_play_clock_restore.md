# Restore the additive comparison

Read recovery_play_clock_manifest.json and copy each flat files entry to a fresh
root, checking SHA256. Include the manifest itself. No ROM, capture, emulator,
firmware, private original disassembly or PCM is in the source closure.

Run with PYTHONDONTWRITEBYTECODE=1:
python port/tests/recovery_play_clock_compare_test.py

Private reproduction (explicit authorized external inputs; new output):
PYTHONPATH=/path/to/inspection/.deps python port/tests/recovery_play_clock_compare.py \
 --capture-root /path/to/original/port/build \
 --audio-root /path/to/original/port/build/recovery-audio-clock-v2 \
 --rom /path/to/approved/rescue-rangers-europe.nes \
 --core /path/to/libretro-uae --frontend /path/to/headless \
 --output /path/to/new/comparison.json

All input evidence identities are in recovery_play_clock_evidence.json. The
program rejects changed inputs and unsupported clock/configuration. Existing
reports are pinned evidence, not writable destinations. No emulator is launched.
The output retains PENDING independent-review labeling until separate review;
review approval must be recorded separately rather than rewriting frozen output.
