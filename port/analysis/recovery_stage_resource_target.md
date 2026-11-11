# Private stage-resource target proof

Newly authored recovery, not recovered lost source or a completed stage. This separate private diagnostic executes the unchanged stage-resource, player-init and fade-entry helpers continuously through `$C6B5 → $C6BD → $C700 → $C2A5` on six invented fixtures.

## Scope and inputs

Entry is synthetic `$C6B5`, with `$F6=0` (no deferred audio), an empty MMC1 serial latch, fixed-last-bank PRG mode 3 and uninterrupted execution. It does not establish genuine title-to-stage reachability, implement the nonzero deferred-audio branch, execute `$FF04`, finish fade/stage initialization or render a stage.

The actual native initializer receives a caller-owned immutable 421-byte resource view from bank 4 `$8193–$8337`. The private builder checks the Europe cartridge SHA-256 `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411` before importing fixtures or creating outputs. The diagnostic build JSON explicitly sets `proprietary_inputs=true`. Generated includes, payload, disk, RAM dump and logs remain ignored private artifacts and must not enter public source. Firmware is required only for the target run, not the isolated diagnostic build.

## New files

- `port/src/recovery_stage_resource_probe.s`
- `port/tests/recovery_stage_resource_target_fixtures.py`
- `port/tools/build_recovery_stage_resource_probe.py`
- `port/tests/verify_recovery_stage_resource_probe.py`
- `port/tests/recovery_test_stage_resource_target.py`

Only these new files and this report were added for target work. Existing helpers, reset/music infrastructure, public scripts, aggregate tests and delivered media remain unchanged.

## Target execution

A real 600-frame run completed on the pinned headless frontend/PUAE core with PAL A1200OG, 68020, 2 MiB Chip RAM, zero Fast RAM, and CPU/memory/blitter cycle-exact settings. The log confirms `PASS runs=600 video_callbacks=600`. This is emulator execution evidence, not measured gameplay performance, physical hardware or audible output.

The private payload is 56,442 bytes, rounded allocation 56,832 bytes. The private 901,120-byte diagnostic ADF SHA-256 is `12571db0d0bc65e1294e02ff3db7551d13be1996e23195ff67d45756f1596fbb`.

Each fixture has one live RAM/context, two full intermediate snapshots, three separate ordered journals, six before/after native register snapshots and four native stack-pointer snapshots. Between helper calls the probe copies state only into diagnostic snapshots; it never patches or resets live RAM/context. The same resource view remains unchanged. All buffers have verified guards, bounds and non-overlapping ranges. Original stack-page effects remain part of all three full-state comparisons.

The independent verifier executes hash-checked original cartridge instructions with a serial MMC1 bank model, verifying publication of bank 4 after the fifth mapper write. It compares complete intermediate/final RAM and context, exact ordered mapper/resource/RAM effect journals and unused tails, immutable resources, native ABI/registers, balanced native stack and untouched lower stack. The binary SBC reference reruns its 262,144-case independent truth table and preserves raw D status.

All six compositions passed. Ordered effect counts by slice are 37+18+76, 37+3+76, 37+33+76, 37+18+76, 37+18+76 and 37+3+76: 771 total. The target dump verifies the effect journals, not a cycle-level target bus trace or global instruction-level memory-access trace. The separate host proof supplies globally whitelisted native read/write and interleaved actual RAM/resource-access checks.

## Negative and isolation verification

The negative test mutates every byte of all three full RAM images, all contexts, journals, native register/metadata records, resource bytes and guards. It also tests invalid/aliased pointers, truncated/oversized dumps, and native stack guards/untouched stack. Final run rejected **48,142 byte corruptions**, **5,154 pointer/alias/bounds corruptions**, and **two dump-size corruptions**. All six positive compositions passed. The final suite also passed the complete no-output filesystem snapshots for missing/wrong cartridge and the isolated byte-identical authorized-input rebuild. Python syntax compilation passed for all four new Python files.

A clean temporary directory contains only seven source files, then receives the authorized hash-checked cartridge. It reproduces payload and ADF byte for byte without firmware or other project artifacts. Missing and wrong cartridge runs must fail before creating any file or changing any copied source file; a complete before/after file snapshot enforces that condition.

## Reproduction

Set `VASM` and `PYTHONPATH` to the approved local assembler and inspection dependencies. Run the new builder, then use:

```sh
PUAE_MODEL=A1200OG RAM_OUT="$PWD/port/build/recovery-stage-resource-probe-chip.bin" \
  "$HEADLESS" "$PUAE_CORE" "$PWD/port/build/recovery-stage-resource-probe.adf" \
  "$PWD/artifacts/a1200-system" 600 "$PWD/port/build/recovery-stage-resource-probe.ppm"
python port/tests/verify_recovery_stage_resource_probe.py port/build/recovery-stage-resource-probe-chip.bin
python port/tests/recovery_test_stage_resource_target.py
```

Private `logs/recovery-stage-resource-provenance.json` records exact tool, firmware, source, artifact and log hashes. The full validation script includes this private diagnostic. Generated cartridge-bearing artifacts are excluded from public source; existing delivered disks remain unchanged and no complete-game claim is made.
