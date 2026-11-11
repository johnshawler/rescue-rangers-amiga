# Stage-loading foundation checkpoint

This checkpoint is new work on the recovered early-source branch. It does not
recover the later lost gameplay or audio source, and it does not replace the
delivered Z/X disk. The stock target remains the separately qualified live
title/menu and scene-preparation diagnostic ending at FF53.

## Reviewed native progression

The new bank-loader chain begins at the genuine FF53 call. It performs the
original bank-2 resource loading and fade, reaches F392, invokes the native
bank-5 object region, executes real bank-aware NMI/audio work and returns to
bank-2 address 911C. Mapper state follows the actual ordered serial writes;
bank and pending-event state are not fabricated to satisfy old guards.

Author continuous tests cover default, alternate-character and move-back
histories. An independent rapid history matches 3,653 helper calls, 118 logical
NMIs, 912 APU writes and 216,616 original instructions through 911C. Independent
bridge tests add 1,610 accepted randomized comparisons, 438 rejected cases and
587 integration guard mutations. These are host-side semantic tests, not an
Amiga performance measurement or cycle-accurate NES timing proof.

The reviewed bank-2 baseline and object bridge have separate exact manifests:

- `recovery_bank_loader_manifest.json`: helpers 79–89, through F392.
- `recovery_bank_loader_object_manifest.json`: helpers 90–95, through 911C.
- `recovery_object_region_manifest.json`: bounded bank-5 object translation.
- `recovery_scroll_view_manifest.json`: standalone horizontal renderer.

The composed native binary through 911C is 56,836 bytes, SHA256
`f1433927f4a44f3baa8c4b02d6c72edbc56a3b2fc06f74e51dbd7033f9e770fd`.
Its dedicated native scratch stack must be at least 2,304 bytes; host composition
was tested with 4,096 bytes. The already published target also reserves 4,096,
but this alone is not target-integration validation.

## Bounded object update

The bank-5 region 8000–81DF is statically translated to 68020 assembly. Internal
calls and returns retain original semantics. A scratch-state first pass checks
the complete call before publishing RAM/context effects. Each pass has a
200,000 translated-instruction budget and 15,000 external-resource-read limit.
Invalid pointers, unsupported return destinations and exhausted budgets reject
without publishing partial state. Inputs must remain unchanged between passes.
Disjoint valid caller buffers and the documented 60,002-byte journal are required.

Public validation includes all raw status/stack cases and every unsupported
16-bit entry PC. Budget tests first prove their control fixtures succeed, then
prove the reduced budget causes rejection. Original-driven isolated object tests
cover 242 calls across a continuous reference route and 4,096 synthetic branch
probes. Those isolated calls do not mean the entire surrounding gameplay route
has been translated.

## Standalone horizontal rendering

The new full-redraw renderer reads both physical 1 KiB nametables with vertical
mirroring and a selected 4 KiB background CHR window. It handles all 512 horizontal
origins, preserving borders and recomputing opacity for sprite composition.
Its 1,084 assembled calls include every origin in USER and supervisor modes,
80 width-aware traced cases and repeated sprite composition. Independent review
adds 58 traced seam, rejection, source-selection and sprite cases plus a clean
restore. Vertical scroll, 8x16 sprites and other unsupported PPU modes reject.
No speed benefit or integrated stage display has been measured.

## Reproduce and limits

Install `requirements-dev.txt` and select the pinned VASM toolchain documented
by this repository. From a clean source-only checkout, set `VASM` and run:

```
bash tools/test_stage_foundation_public.sh
```

This wrapper exercises the five new public contract suites while rejecting
private cartridge/firmware reads and original-CPU oracle imports. These Python
hooks are regression checks, not an operating-system sandbox. Private
original-comparison tests separately require the approved cartridge and are
never part of the public input set. Source generators use that cartridge only
offline; production helpers do not fetch or interpret 6502 opcodes at runtime.

The nonzero deferred-bank-interrupt path remains unsupported. The reference
trace in `recovery_stage_route_2026-11-11.md` describes later stage dependencies,
not native completion. Dialogue, stage map/object loading, integrated scrolling,
live gameplay and their stock timing need subsequent checkpoints. No game ROM,
firmware, asset table, generated disk, capture or audio file is included here.
