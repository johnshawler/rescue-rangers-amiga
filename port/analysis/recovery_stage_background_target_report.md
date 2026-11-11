# Qualified additive visible-tile stage target

The unique uninstrumented candidate is
`port/build/recovery-stage-background-v1`. No second capture was made. The frozen
stage target, profiler, older renderer and delivered Z/X disk remain unchanged.
Only the background entry/include is substituted in a generated device copy;
the original native game composition, selected background CHR base+4096, sprite
renderer using the full CHR base, hardware blanking and audio adapter are intact.

## Measured result and limits

Actual PAL stock A1200OG, 68020/AGA, 2 MiB Chip, zero Fast, cycle-exact PUAE capture
with five-plane display DMA enabled gives:

- Final redraw: 119,339 CIA ticks, 168.230241 ms.
- Frozen uninstrumented v3 control: 238,079 ticks, 335.616081 ms.
- Matched final-redraw reduction: 49.874201%.
- Allocation: 862,720 Chip bytes, 0 Fast bytes, unchanged.
- Payload: 862,552 bytes, 88 bytes larger than control; allocation rounding unchanged.
- Late completed updates: 395 of 395. This is still far above the 20 ms budget.

Whole bounded progression separately measures 53,453,641 ticks (75.352725 s),
versus 100,313,862 ticks (141.410814 s) in the matched control. This interval
includes game loading/native work, rendering and audio scheduling. The 49.874%
figure describes ONLY final redraw, not this whole progression, game frame rate,
continuous gameplay, an isolated background segment or physical Amiga hardware.
The target still stops at C77B, the loaded-stage main-loop entry.

## Exact-history and output qualification

Both captures have the same actual CIA input-change records and complete
original-replay helper/state/effect digest:
`eb7a166b893827ecf8d5bb9cb5e1b76a49b9bd3f07753ee2fd95fa70c115b625`.
They execute 14,313 helpers, 395 NMIs and 733,209 original instructions. The
comparison includes per-helper context, RAM, journal, runtime, pads/event and
ordered device effects, not merely final state. Both continuous native replays
match every original boundary and ordered effect. Target telemetry still retains
only the last journal and 256 audio records; exhaustive target boundary capture
is not claimed.

Corrected strict verification passes original final state, devices, independent
Copper and original RGB/screenshot pixels. Full final RAM/context/runtime,
nametables, palette, OAM, CHR, framebuffer and opacity bytes equal the control.
Target rejection checks pass. The additive source-only compiled suite passes
all 16 complete synthetic scroll/background/sprite frames plus adapter, input,
plan, verifier-negative and rejection tests, with ROM/oracle access denied.
A flat source-only restoration also passes the same compiled integration suite.
Standalone renderer and independent review evidence are recorded separately.

## Audio qualification, including preserved failures

Captured PCM is NOT byte-identical to the control: publication intervals changed.
Native plans/shadows are original-exact, but that is not used alone as audible
proof. The unchanged frozen phase-zero PCM verifier rejected optimized RTI380.
Its original guards leave sub-loop windows after the renderer improvement.
A separately reviewed phase-aware discriminator passes every eligible optimized
window, with the SAME guards, windows and 0.45 correlation / 0.08 margin thresholds,
equal phase search across all candidate loops, stronger rate-alias alternatives,
synthetic regressions and actual DC/channel/old-loop negatives. The independent
capture-specific anchor bound and 804 shifted-window checks establish placement
and decision robustness without moving the selected windows.

The old control remains qualified by its original frozen verifier. The stronger
new rate-alias classifier conservatively rejects that old control's mixed long
window, and this rejection is also preserved. These are explicitly different
bounded qualification methods, not a universal replacement. See the PCM and
anchor reports. No claim of NES waveform/envelope/mixing fidelity, exact phase,
small pitch-error rejection or absolute latency is made.

Important private results are stage-target-verification.json,
stage-target-replay.json, stage-target-rejections.json,
stage-background-noise-pcm.json, stage-background-anchor.json and
stage-background-comparison.json. The qualification-evidence directory preserves
the failed frozen candidate run and stronger-control rejection. Final target ADF
SHA-256 is `c9e06472f82315f36adfa2a57d4a5c8aa2deabe54d6c2dc1befcf5db3d656c9c`.
No original asset, disk, PCM, screenshot or captured RAM belongs in a public package.
