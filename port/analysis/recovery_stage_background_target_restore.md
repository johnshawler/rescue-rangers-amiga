# Reproduce the additive background target

Read the standalone, PCM, anchor and target reports first. Use the pinned GCC14,
vasm, machine68k, py65, NumPy and approved inputs from the stage target restore
recipe. Set PYTHONDONTWRITEBYTECODE=1. The public integration proof needs no ROM:

```
bash port/tools/recovery_stage_background_public.sh
bash port/tools/recovery_stage_background_target_public.sh
OPENBLAS_NUM_THREADS=1 python port/tests/recovery_stage_background_noise_test.py
```

Restore only the explicit public_allowlist and dependencies of
recovery_stage_background_target_manifest.json, plus that manifest itself.
This is a flat closure: do not recursively expand historical manifests. It must
contain no original disassembly, unrelated experimental_paula source, private
asset, generated disk, screenshot, PCM or RAM capture.

For an independently authorized future capture, choose a fresh output directory:

```
python port/tools/recovery_stage_background_build.py --output port/build/background-fresh
bash port/tools/recovery_stage_background_run.sh port/build/background-fresh
```

The frozen runner deliberately invokes the original frozen PCM verifier. Its
known short-window rejection is preserved, so this command can stop nonzero
AFTER state/pixels and full replay have passed. Do not hide the failure or rename
an additive result to look like a frozen-verifier pass. For the qualified v1
capture, no recapture is necessary. Complete the separately reviewed checks:

```
python port/tests/recovery_stage_target_rejection_test.py port/build/recovery-stage-background-v1
OPENBLAS_NUM_THREADS=1 python port/tests/recovery_stage_background_noise_pcm.py port/build/recovery-stage-background-v1
python port/tests/recovery_stage_background_pcm_anchor.py port/build/recovery-stage-background-v1
python port/tests/recovery_stage_background_compare.py port/build/recovery-stage-background-v1
```

The comparison requires the specifically named additive PCM/anchor reports for
the candidate and the original frozen PCM report for v3. It calculates a
reduction only when full input/helper/state/effect histories match. Different
future timings, audio settings or endpoint behavior require fresh qualification;
the capture-specific anchor argument must not be assumed globally.

Build/capture never overwrites an existing output. The approved ROM remains
SHA-256 051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411;
firmware remains 6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707.
The delivered rescue-rangers-stock-zx.adf stays unchanged at
6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17.
