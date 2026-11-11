# Standalone continuous player/fade-entry target proof

Newly authored native recovery, not recovered lost source or a playable-stage milestone. The existing 340-byte player initializer and new 282-byte fade-entry helper are unchanged. The five-file host milestone is frozen.

## Exact execution scope

Six invented fixtures enter synthetically at `$C6BD`, execute the unchanged player helper to `$C700`, then execute the fade-entry helper to `$C2A5`. The live original RAM and context buffers are never reset or patched between calls. Separate snapshots retain the complete intermediate RAM/context, and separate journals retain each slice's original architectural stores. Capturing snapshots reads original state without changing it.

This does not execute the preceding bank-4 `$8000` initialization. It stops before `$FF04` frame synchronization, with the original nested call stack and fade-loop PHA still live. It does not finish `$E096`, run `$C703`–`$C716`, load/render a full stage or establish a frame loop.

## Source-only target

The new builder generates six public invented fixtures using `recovery_gameplay_fade_target_fixtures.py`. Inputs cover one/two-player active and inactive combinations, original stack wrap/boundary values 0, 1, 5, 6, 7 and 255, and raw status values including D=1. Palette values exercise negative-result replacement, carry and signed overflow boundaries.

Each fixture has separate live RAM/context, intermediate RAM/context snapshots, first and second journals, and before/after native register snapshots for both calls. Native stack pointers are recorded before, between and after the calls. All buffers have guards and verified non-overlapping ranges.

The source-only payload is **39,080 bytes**, with **39,424 bytes** rounded allocation. The separate 901,120-byte ADF SHA-256 is:

`34a4f6073e9b7eeef1597bc3ebde27fabef6ace085dcbc48cbc5addf77dbfcda`

The builder reads no cartridge or firmware. It uses the existing unchanged boot loader. No existing player, music or reset probe/builder/verifier is edited.

## Executed verification

- One actual **600-frame PAL A1200OG** run with the pinned headless frontend and PUAE core. Confirmed 68020, 2 MiB Chip RAM, zero Fast RAM, and CPU/memory/blitter cycle-exact settings. Log reports `PASS runs=600 video_callbacks=600`.
- Independent target verifier executes hash-checked actual Europe ROM instructions for each fixture, retaining reference RAM/registers/stack continuously through both boundaries. It uses the host proof's independently implemented Ricoh 2A03 binary SBC ALU and reruns its **262,144-case bitwise full-adder truth-table proof**. It does not clear D or normalize original status at either boundary.
- All six intermediate and final full RAM images, complete contexts, journals and untouched tails match. Original stack-page effects, both sets of native register snapshots, balanced native stack and buffer guards/ranges/non-overlap pass. Unused lower native stack remains untouched.
- Ordered architectural record counts are **18+76, 3+76, 33+76, 18+76, 18+76, 3+76**, totaling **549**. These are journaled architectural writes, not cycle-level dummy bus writes or a hardware bus capture.
- Negative verification rejects **32,401 byte corruptions**, **2,544 pointer/alias/range corruptions** and **two dump-size corruptions**. Byte checks include every byte of all records, both full RAM images, both contexts, both journals and their guards for every fixture; native stack guards and untouched lower stack are checked separately.
- A clean temporary directory containing only six required source files, with no ROM or firmware, reproduces both payload and ADF **byte-for-byte**.
- The earlier host results remain separate: 73,728 standalone actual-ROM cases, 4,096 continuous compositions and 10,758 ROM-free declarative cases, with globally whitelisted traced native reads/writes. Target dump comparison does not claim to provide an instruction-level target access trace.

Exact private tool/firmware/payload/dump/log hashes and configuration are recorded in ignored `logs/recovery-gameplay-fade-entry-provenance.json`; negative results are in `logs/recovery-gameplay-fade-entry-negative.json`. No firmware, cartridge, proprietary asset or captured trace is added to public source.

## Reproduction

Set `VASM` and `PYTHONPATH` to the existing approved assembler/dependencies, and `HEADLESS`/`PUAE_CORE` to the pinned frontend/core, then run from the project root:

```sh
python port/tools/build_recovery_gameplay_fade_entry_probe.py
PUAE_MODEL=A1200OG RAM_OUT="$PWD/port/build/recovery-gameplay-fade-entry-probe-chip.bin" \
  "$HEADLESS" "$PUAE_CORE" "$PWD/port/build/recovery-gameplay-fade-entry-probe.adf" \
  "$PWD/artifacts/a1200-system" 600 "$PWD/port/build/recovery-gameplay-fade-entry-probe.ppm"
python port/tests/verify_recovery_gameplay_fade_entry_probe.py port/build/recovery-gameplay-fade-entry-probe-chip.bin
python port/tests/recovery_test_gameplay_fade_entry_target.py
```

## Remaining work

Integration must preserve the live `$C2A5` context and original nested stack, implement real frame synchronization and the remaining fade/call chain, and establish the missing earlier stage-initialization prerequisites. This standalone target adds no gameplay, speed, audio or full-stage claim. Public/full validation includes this separate source-only target. No physical-hardware run or modification of prior delivered artifacts is claimed.
