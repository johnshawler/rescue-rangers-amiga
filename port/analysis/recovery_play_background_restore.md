# Restore the unqualified optimized five-frame candidate

Status is deliberately blocked by stage08 PCM discrimination. Source restoration
and matching target bytes do not turn it into a qualified target. Keep both earlier
approved targets and the delivered disk unchanged. Never publish private inputs,
disks, PCM, screenshots, captured RAM or extracted resources.

Use the pinned GCC14/vasm and machine68k/py65/numpy/Pillow setup described by
recovery_play_target_restore.md. Set PYTHONDONTWRITEBYTECODE=1 and preferably
OPENBLAS_NUM_THREADS=1 for the spectral tests. Public source-only restoration:

```
bash port/tools/recovery_play_background_restore.sh
```

This checks only explicit flat hashes, creates a fresh tree and runs the compiled
combined synthetic target plus unchanged phase-aware synthetic regressions. It
never recursively expands historical manifests or reads original inputs/oracles.

Private asset-bearing build requires the authorized original ROM SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411 separately:

```
python port/tools/recovery_play_background_build.py --output port/build/new-output
```

The preserved actual capture is port/build/recovery-play-background-v1.
Do not recapture merely to seek a passing classifier. If later explicitly running
a fresh capture, recovery_play_background_capture.sh uses the same CIA schedule
and pinned stock settings; it will exit nonzero at a frozen PCM failure. Preserve
that log. No altered core or manual state injection is supported.

Recheck the existing capture, with its directory as B, using these independent
commands (expected failures are intentional and must not be reported as PASS):

```
python port/tests/recovery_play_target_verify.py B
python port/tests/recovery_play_target_replay.py B
python port/tests/recovery_stage_target_noise_pcm.py B
python port/tests/recovery_play_target_pcm.py B
python port/tests/recovery_play_target_intervals.py B
python port/tests/recovery_stage_background_noise_pcm.py B
python port/tests/recovery_play_background_noise_audit.py B
python port/tests/recovery_play_background_anchor.py B
python port/tests/recovery_play_background_history.py B --control port/build/recovery-play-target-v3
python port/tests/recovery_play_target_layout_test.py B
python port/tests/recovery_play_target_rejection_test.py B
```

Frozen noise rejects380; phase-aware noise rejects383. The diagnostic noise audit
writes all windows with statusFAIL then exits1. Anchor writes endpoint-bound PASS
but overall robustness FAIL, then exits1. History reports HISTORY_MATCH_ONLY,
not qualification. The full comparison gate requires successful noise/anchor
results and must refuse this candidate. No speedup percentage is released.

For a restored tree, pass --tool-root to the pinned libretro-uae source/binary
folder and --frontend to the pinned existing headless binary when running the
anchor check. Its core/source fingerprints and final-plan premises are checked
again for this capture, not assumed from the older optimized-stage capture.

Final-source restored rebuilding must match the retained v1 target.bin,
adapter.bin, boot.bin and target.adf exactly. Preserve source-only/final-build
logs separately. The public package is exactly recovery_play_background_manifest.json
and its public_allowlist/dependencies files. All capture/evidence directories
remain private and excluded.
