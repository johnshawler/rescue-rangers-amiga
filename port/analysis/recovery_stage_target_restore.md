# Restore and reproduce the additive stage target

Use an existing authorized recovery checkout. Do not download a game ROM or
firmware from an unverified source. Never publish generated disks, cartridge
bytes, extracted assets, screenshots, PCM or state traces.

Required private inputs:

- `input/rescue-rangers-europe.nes`, SHA-256
  `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
- `artifacts/a1200-system/kick40068.A1200`, SHA-256
  `6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707`.

Use the existing pinned m68k GCC14 activation script, vasm, Python dependencies
(machine68k, py65, numpy and Pillow), PUAE core and headless frontend. The core
SHA-256 is `84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456`.
The existing frontend at `port/build/experimental-direct-paula/headless` must have
SHA-256 `5a6caac3c484c24a979800188070abb78c7fdbe648106fb84c5d8532e19052b1`.
The run script checks these and the firmware before starting.

From the repository root, with `VASM`, `PYTHONPATH` and the activated C compiler
configured, set `PYTHONDONTWRITEBYTECODE=1`. Public tests need no private inputs:

```
bash port/tools/recovery_stage_target_public.sh
```

The public test compiles the actual adapter and full linked target with synthetic
resources, and rejects cartridge/original-oracle access. This is separate from
the older assembler-only aggregate. The unchanged scroll renderer has its own
full 512-origin suite at `port/tests/recovery_scroll_view_test.py`.

For the private stock capture, choose a new output directory:

```
python port/tools/recovery_stage_target_build.py --output port/build/stage-fresh
bash port/tools/recovery_stage_target_run.sh port/build/stage-fresh 11000 '80:90:13,160:170:13,360:390:13'
python port/tests/recovery_stage_target_rejection_test.py port/build/stage-fresh
```

The builder checks the frozen finish manifest, flat reviewed source closure (without recursively expanding historical manifests),
exact 92,408-byte native composition and unchanged title planner bytes. The build
contains no original-code oracle or captured state. The runner refuses existing
capture paths, disables RAM injection variables, sets A1200OG / zero Fast, uses
real KEY_TICK_EVENTS, and captures descriptor-backed Chip memory and PCM. It then
runs final original state/pixel checks, continuous native actual-input replay
and stage08 finite-loop PCM discrimination. Capture duration is a physical
callback budget, not a game-frame count; insufficient duration is a failure.

The retained successful development run is `port/build/recovery-stage-target-v3`.
The final-source rebuild is `port/build/recovery-stage-target-v4` and must match
v3 target/adapter/boot/ADF bytes before using the same capture as evidence.
The v3 ADF SHA-256 is
`4c14710a3bd3677a39c6f98f9963baae7dbad9dc5b3c494c2a26398596240955`.
Source-only changes to reports and test coverage do not alter the target image.
Keep `recovery-stage-target-v1` (incomplete physical duration) and v2 (genuine
noise08 fail-closed stop) separate, with their original logs and dumps.

Important private results are `stage-target-verification.json`,
`stage-target-replay.json`, `stage-target-noise-pcm.json` and
`stage-target-rejections.json`. See the report for explicit ring-retention,
audio approximation, instrumentation and speed limitations. No other projects,
legacy target, firmware, cartridge or delivered disk should be overwritten.

The verifier-only review correction adds independent Copper/RGB checks and
source-only paired-palette/screen and short-spectral regressions. Re-run the same
commands against the existing v3 capture; do not recapture or change its runtime.
Corrected private logs are `verification-corrected.log`, `replay-corrected.log`,
`noise-pcm-corrected.log` and `public-corrected.log`. Prior verifier source and
reports are retained under `pre-review-verifier/` with their old hashes.

For packaging, copy only the explicit `public_allowlist` and `dependencies` keys
from `recovery_stage_target_manifest.json`, plus that manifest itself. Never
expand embedded historical manifests. No original disassembly or unrelated
legacy experimental Paula files belong in this closure. A fresh allowlist-only
restore must pass the public suite and regenerate the identical target bytes.
