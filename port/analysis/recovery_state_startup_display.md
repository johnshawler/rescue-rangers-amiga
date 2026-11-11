# State-driven native startup displayed on stock emulated A1200

A new, separate diagnostic boots on an emulated stock PAL 68020/AGA machine,
executes the reviewed native state-driven startup dispatcher, consumes its
actual journals with the unchanged native display device, renders the initial
title with the unchanged baseline background/sprite renderers, and holds it.
Two fresh executions pass. The entire 51,200-byte framebuffer and every one of
the 163,840 RGB pixels in the actual captured viewport match an independent
original-cartridge/device replay. The logo, character faces, player choices,
cursor and copyright/licensing text were visually inspected.

This is not a replacement playable disk, menu/gameplay engine, live-controls
implementation, physical-hardware test or integrated audio system. It is new
additive source on the recovery baseline, not recovery of missing later source.
The compact renderer experiment is not linked or measured here.

## Production control and data provenance

The builder imports no original-cartridge oracle or 6502 interpreter. It emits
one bounded native loop, not an oracle-generated sequence of helper calls.
Only the dispatcher's actual PC, RAM, wrapped original stack, mapper state and
supplied event determine execution. The reviewed dispatcher and all of its
helper sources are included unchanged. Its final manifest is pinned to
`9f167ea54fef8786e18558b809980ebe0ea0019568d249a1f11a4b1a40b6905a`.
The standalone dispatcher composite remains 23,586 bytes, SHA256
`a071d72a986a812fb09d4cc3a38a03fad693a7ff9d2ba7fdeb69c471de0c1f19`.

Initial conditions are the declared reset diagnostic's RAM poison A5, context
FE24/17/33/00/24/FD/A7 and reset MMC1 state 0C/00/00/03, not captured RAM.
Immutable PRG and CHR are extracted directly from the explicitly hash-checked
private cartridge. No reference RAM, device state, nametable, palette, OAM,
framebuffer or screenshot enters the target. Manifest hashes are checked for
source integrity; reference results are never used to construct control flow.

Pads are always decoded neutral. A dispatch return of zero causes the external
diagnostic to supply logical event 1 on its next call; otherwise event is zero.
These are scripted logical NMIs, not live controls, asynchronous physical NMIs
or a real-time scheduling claim. The loop stops only after the native dispatcher
rejects at actual PC C5D1, with a 4,096-completion safety cap. It does not stop
because it reaches the expected 990 count. Unsupported states fail visibly.

After successful calls, published helper IDs translate to the existing device
consumer's helper-ID ABI. This translation only chooses journal interpretation,
including resource filtering and DMA offsets; it never chooses the next helper.
The device consumes genuine serial mapper/PPU/DMA records in order. Its persistent
mapper is independent of the dispatcher's runtime mapper and is verified against
the original replay. APU journals are captured for comparison, not played.
The frozen device's bounded PPU model and final-view admission restrictions
remain exactly as documented in `recovery_startup_display_native.md`.

The original-only oracle is separate from the builder. It independently chooses
boundaries from original CPU/RAM/mapper/event state, executes original 6502
instructions, and records all original effects before examining target dumps.
The existing read-only device/per-pixel reference consumes this new original
event stream. It does not consume native output to generate expected state.
The frozen 1,024-call diagnostic is only an optional final-output comparison;
none of its helper schedule or captured state is used by the new build or oracle.
990 versus 1,024 helper boundaries is not evidence of a speed improvement.

## Actual target evidence

Both executions start from a fresh emulator process and run 1,800 frames, with
RAM_LOAD and RAM_LOAD_FRAME unset. Their effective logs are checked for A1200OG,
68020, AGA, PAL 50 Hz, 2 MiB Chip, zero Fast/slow RAM, no JIT/FPU/MMU, and
cycle-exact CPU, memory and blitter. Each completed run reports 1,800 video
callbacks. Both complete 2 MiB Chip dumps and both raw video captures are
byte-identical.

The target records and verifier checks:

- 990 successful native helper completions, 35 logical NMIs, all 990 complete
  contexts, all 990 runtime mapper/latch/diagnostic records, and every published
  journal byte against 77,717 original instructions, including 252 APU writes.
- Complete RAM at the first 64 successful boundaries and final RAM. Final context
  is C5D1/F0/F0/FF/A5/BF/A7 and mapper is 1E/1F/1F/02, empty serial latch.
- Every native dispatcher call preserves D1-D7/A0-A6 and exact native SP. The
  4 KiB native stack has guards; its lower 3 KiB remain untouched in both captures.
  This is an observational upper-1-KiB stack bound, not a target memory-access
  trace. All RAM/context/journal/runtime/resource/stack/capture guards pass.
- Journal capacity is 32,770 bytes and all buffers are disjoint. Before calls,
  journal scratch is cleared and diagnostic fields are poisoned. The final
  unsupported call leaves final RAM/context and architectural mapper intact.
- Full immutable 128 KiB PRG and 128 KiB CHR are preserved. Every final modeled
  device byte, 2,048 nametable bytes, 32 palette bytes, 256 OAM bytes and 8,192
  selected CHR bytes match the independent original-event replay.
- All 4,301 PPU events and 385 mapper writes produce the same final device result.
  All 51,200 bitplane bytes match the independent per-pixel composition. Copper
  mode, bitplane pointers and all palette entries are checked. The actual
  720x287 capture matches the expected 640x256 viewport at (40,18) exactly,
  including horizontal pixel duplication.

The existing frozen diagnostic's complete framebuffer and raw video are also
identical to the new result. This comparison is supplemental: correctness does
not depend on having an old capture. No claim is made to capture every target
intermediate RAM state or ordered target RAM write. The reviewed host dispatcher
suite's all-boundary RAM/effect evidence remains a separate prior result.

Two rebuilds reproduce all eight generated build files byte-for-byte. Both
complete builds succeed in fresh Python processes with every oracle and py65
import forbidden. Poisoning the separate expected-result function leaves target
source unchanged. The new builder has no expected-state or schedule argument.
253 mutations of the real successful dump, configuration and actual viewport
pixel are rejected, including bounds, markers, statuses, guards, buffer contents,
capture sizes, Copper configuration, truncated/extended dumps and hardware
settings. The unchanged device suite also passes its 32 assembled consumer calls.

## Copper terminator verification hardening

Independent review confirmed the target result and 33 additional adversarial
checks, but found an inherited verification omission: the old display checker
did not assert the four Copper terminator bytes at offsets 216 through 219.
The actual captured terminator was already correct. The new state-startup
checker now explicitly requires `FF FF FF FE`, after the frozen display checker
returns. The frozen old checker, target generator, native code, ADF and captures
are unchanged. A durable test flips each of the 32 individual terminator bits
and requires rejection specifically for the terminator check. Together with
the original 221 cases, 253 malformed-input tests pass.

The reviewed eight-file source checkpoint with manifest SHA256
`aa9fd8acc376ca26ed69677be27b2dcbf7793c40bdf7c0c23c1af9d4629fdecb`
and all of its original private artifacts were preserved separately under
`port/build/recovery_state_startup_display-reviewed-v1` before any edit.
Both original captures were reused, not rerun or regenerated. Their full
verification and captured-pixel comparisons pass with the hardened checker.
The payload, ADF, Chip dumps and raw video hashes listed below are unchanged.
This revision changes only the new verifier, rejection test, report, results
and manifest; it does not alter the scope or claim gameplay, audio or speed.

## Memory and timing accounting

Payload is 401,294 bytes. Boot uses the unchanged MEMF_CHIP|MEMF_CLEAR allocator
with 1,187,840 bytes total, leaving 909,312 bytes outside that allocation in the
2 MiB machine. There is no Fast allocation. The total comprises the payload,
786,432 reserved diagnostic capture bytes, a 16-byte final guard, and 98 bytes
of allocation rounding. Captures actually occupy 314,780 bytes; the remaining
471,652 capture bytes are verified zero.

Within the payload, PRG+CHR resources occupy 262,144 bytes; journal 32,770;
RAM/context/runtime 2,068; native stack 4,096; framebuffer 51,200; nametables,
palette and OAM 2,336; selected CHR 8,192; background opacity 7,680; tile cache
1,920; sprite scratch 2,196. The remaining 26,692 bytes contain code, reports,
Copper/palette constants, alignment and guards. These are diagnostic costs,
not a claimed production-memory budget.

Both executions measure 7,891,321 CIA-B E-clock ticks for startup including
journal clearing, capture, register checks and diagnostic control, approximately
11.12 seconds at 709379 Hz. CHR selection plus one baseline background/sprite
composition measures 56,323 ticks, approximately 79.4 ms. Display DMA is off
through both intervals; disk boot/loading and final Copper/palette setup are
excluded. Repeated 32,770-byte journal clearing and diagnostics heavily affect
the startup interval. These measurements are not game FPS, real-time NMI timing,
a rendering optimization comparison or a 20 ms PAL-frame claim.

## Preservation and private artifacts

Only the new `recovery_state_startup_display`-named source/test/report/result/
manifest files were added. No existing source, report, manifest, README,
aggregate script, Git index, branch or publication operation was changed.
All 84 source/dependency/private-artifact entries in the frozen startup-display
manifest were rehashed unchanged. The final startup-dispatch manifest and its
listed dependencies are verified during every new build. The delivered Z/X disk
was also rehashed unchanged: 901,120 bytes, SHA256
`6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17`.

Generated source, private resources, binary, ADF, Chip dumps and captures are
confined to ignored `port/build/recovery_state_startup_display`. They contain
private cartridge-derived data and are not distribution artifacts. No capture
or disk was published. Firmware and ROM remain private.

Exact hashes:

- Private ADF: `54b75d44864e8278315386a1deecb70039291f98b38ad524f99e43e4dce07261`.
- Payload: `6dae0ce85eac54f81bb1dc04324146a76590f83a150a068781701747fe5b0a4a`.
- Either full Chip dump: `dfcbfac7e210b3d1c697ecdfd9fd210ab0f11aec5f5e8d393dcd6d87203e6911`.
- Either raw video capture: `eb8b664ccf0d3fdce732ec3a2a4917a0d2b9da50216f421f005aa7e17449682f`.

## Portable reproduction

Provide the approved cartridge at `input/rescue-rangers-europe.nes` (SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`),
and approved A1200 firmware at `artifacts/a1200-system/kick40068.A1200`.
Install `requirements-dev.txt`. Set VASM, PYTHONPATH, HEADLESS and PUAE_CORE to
the approved assembler, Python dependencies, headless frontend and PUAE core.
From the repository root:

```sh
export PYTHONDONTWRITEBYTECODE=1
python port/tools/build_recovery_state_startup_display.py
python port/tests/test_recovery_state_startup_display_build.py
out="$PWD/port/build/recovery_state_startup_display"
for prefix in '' repeat-; do
  env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
    RAM_OUT="$out/${prefix}chip.bin" "$HEADLESS" "$PUAE_CORE" \
    "$out/recovery_state_startup_display.adf" \
    "$PWD/artifacts/a1200-system" 1800 "$out/${prefix}screen.ppm" \
    > "$out/${prefix}amiga.log" 2>&1
done
python port/tests/verify_recovery_state_startup_display.py
python port/tests/test_recovery_state_startup_display_rejection.py
python port/tests/test_recovery_startup_display_device.py
```

The verifier requires both real dumps, logs and video captures. Builds require
no previous diagnostic fixtures. PIL supports captured-pixel verification;
py65 supports only the separate original reference, and machine68k supports
the inherited public helper/consumer harness. No target CPU interpreter is used.
