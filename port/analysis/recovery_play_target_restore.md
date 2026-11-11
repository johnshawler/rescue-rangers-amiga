# Restore the additive five-neutral-frame stock target

Only use the existing authorized original input and firmware. Do not publish private
ROM, firmware, disassembly, extracted resources, binaries/disks, PCM or captures.

Required private input SHA256:

- input/rescue-rangers-europe.nes: 051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411
- artifacts/a1200-system/kick40068.A1200: 6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707

Activate the pinned recovery GCC14 toolchain. Set VASM to the approved
vasmm68k_mot, PYTHONPATH to the installed machine68k/py65/numpy/Pillow dependencies,
and PYTHONDONTWRITEBYTECODE=1. Keep the existing pinned PUAE core/frontend described
in recovery_stage_target_restore.md. Source-only tests need neither original input
nor firmware:

```
bash port/tools/recovery_play_target_restore.sh
```

This creates a fresh isolated tree, validates every explicitly listed flat source
hash and runs the actual compiled adapter, synthetic linked target, keyboard,
composition, rejected-error/mute and maximum capture/layout tests. No recursive
expansion of historical manifests is performed. Cartridge reads and original
oracle/py65 imports are denied during the public execution suite. Only copy the
manifest itself and its public_allowlist/dependencies entries when packaging.
The exact approved 216616-byte engine is checked inside the actual linked target.

Private fresh build and real-input capture, using a never-used output directory:

```
python port/tools/recovery_play_target_build.py --output port/build/play-target-fresh
bash port/tools/recovery_play_target_run.sh port/build/play-target-fresh 11500 '80:90:13,160:170:13,360:390:13'
python port/tests/recovery_play_target_layout_test.py port/build/play-target-fresh
python port/tests/recovery_play_target_rejection_test.py port/build/play-target-fresh
```

The runner rejects existing capture files, removes RAM-injection variables, uses
A1200OG / zero Fast, authentic CIA keyboard callbacks, full Chip capture, real PCM
and independent original/native replay. This is an intentionally bounded neutral
diagnostic, not a moving-input or playable-game release. Insufficient callback
budget fails rather than being counted as successful completion.

Successful final-layout private capture: port/build/recovery-play-target-v3.
Earlier v1 is an unexecuted development build with an absolute telemetry addressing
mistake caught before capture. v2 is a separately verified original-layout capture
with a word-aligned output buffer; its successful evidence is not substituted for
v3. The additive v3 capture buffer is long-aligned and has its own actual run.
Keep all these outputs and logs. Final-source builds must match v3 target.bin,
adapter.bin, boot.bin and target.adf before citing v3 capture evidence.

Important outputs: play-target-verification.json, play-target-replay.json,
stage-target-noise-pcm.json (unchanged baseline checker), play-target-pcm.json,
play-target-layout.json and play-target-rejections.json. Reports disclose final-only
actual screenshot coverage, retained audio ring limits, direct-Paula approximations
and late update timing. Do not overwrite earlier stage/checkpoint sources or disks.
