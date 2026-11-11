# Stock first-stage loaded display

This additive target reaches the original first-stage loaded boundary C77B on
an emulated stock PAL A1200 and displays the original stage. It does not execute
the subsequent gameplay frame. The older live target, frozen native modules,
ROM, firmware and delivered Z/X disk remain unchanged.

## Qualification

The v3 fresh boot uses the pinned cycle-exact PAL A1200OG, 68020/AGA, 2 MiB Chip,
zero Fast configuration. The boot requests MEMF_CHIP | MEMF_CLEAR, allocating
862,720 bytes. Captured relocation base is 72,792; every payload region fits
inside Chip RAM. Original RAM, context, journal and resource guards remain intact,
and terminal SP equals the end of the 4,096-byte native stack.

Actual CIA keyboard callbacks, not game-RAM writes, drive Start at completed-RTI
ranges 80–90, 160–170 and 360–390. The target records exact helper/event/RTI/input
boundaries. Original-code replay uses those captured boundaries, rather than the
requested keyboard schedule. Z=B, X=A, Return=Start, Tab=Select and arrows retain
the reviewed keyboard mapping.

- Target status 0 at context `c77b00ffffa5bfa7`: 14,313 successful native helpers
  and 395 completed logical NMIs.
- Independent original replay executes 733,209 instructions. Continuous native
  host replay matches every RAM/context/runtime boundary and ordered effect.
  Final target RAM/context/runtime and last counted journal also match.
- Original-event device replay matches nametables, palette, OAM, mapper/device
  state and selected CHR. Every 51,200 bitplane byte and every 163,840 displayed
  RGB pixel matches. The captured stage screenshot was visually inspected.
- All 256 retained audio records match original completed snapshots and plans;
  139 earlier ring records were overwritten intentionally. This is not exhaustive
  on-target journal retention. Actual stereo PCM has AC RMS approximately
  1,387.57 / 1,878.63 and 39.334 seconds of terminal silence.

The frozen native composition is 92,408 bytes, SHA-256
`1ee9d5b9326a4016d7d28e6a54e4ab8b4260aecfddc67d3dc62a006550347184`.
Its independent live-title helper 72 remains outside that composite. The native
host composition with that helper is 92,550 bytes and is checked separately.

## Display and device integration

The reviewed horizontal renderer performs a full redraw, followed by the
unchanged sprite compositor. Background uses selected CHR+4096 (stage bank 16),
sprites selected CHR base (bank 0). The target retains 2,048 nametable bytes,
51,200 plane bytes, 7,680 opacity bytes and 2,196 scratch bytes. The background
uses only the first 256 scratch bytes before sprites reuse the buffer.

The renderer admits ctrl90/91, mask1E, horizontal scroll0–255, vertical scroll0,
MMC1 control1E and 8x8 sprites. Sixteen complete-linked synthetic frames verify
cross-nametable composition, distinct CHR banks, fine scroll, first-eight sprite
selection, register preservation and bounded mutations in user and supervisor
modes. The actual stock C77B capture is ctrl90/scroll0; no moving-stage hardware
scrolling claim is made. Mask0 really disables display DMA and updates the
universal backdrop. Other post-initialization modes fail closed.

New device routing consumes mapper helper79, mixed resource/PPU helpers81/110/115,
PPU helpers78/84, and long NMI98 through the existing long-DMA consumer. Semantic
resource-only and controller-only journals do not become PPU writes. Helper98
retains the FFFF size sentinel and DMA offset134382. The full journal remains
134,638 bytes; new generated-region journals are 60,002 bytes. No helper, mapper,
queued-video, audio or interrupt operation is skipped to reach C77B.

## Stage audio extension and failures retained

v1 ended after 8,000 physical callbacks at logical NMI346, before the requested
third Start. It displayed genuine interstitial dialogue but was incomplete.
Its 11,770 completed boundaries were independently replayed successfully.

v2 exposed genuine stage noise register08 outside the title planner's accepted
07/0D/81 domain. It permanently muted/stopped with runner-4 at the 380th NMI,
after 13,904 native helpers. Its exact actual-input replay passes. This failed
capture remains preserved; it is not relabeled as success.

v3 adds only noise08 to a separate wrapper around the unchanged title planner.
The wrapper preserves all input registers and old accepted output bytes; all
other title guards remain. PAL noise08 is period188 in long LFSR mode. Appended
wave8 is a generated 2,048-byte signed finite loop at Paula period160, DMA length
1,024 words. Old wave5/6/7 remain unchanged. The frozen title planner's assembled
470 bytes retain their reviewed SHA-256. Original completed-state coverage through
stage loading confirms08 is the only new audible noise value. Reset's unwritten,
muted noise register retains the existing declared initialization to07.

Four actual captured stage08 windows discriminate the new finite loop from each
old loop after excluding pulse harmonics. New-loop correlations are about
0.521–0.565, versus at most0.413 for an old loop. DC, swapped channels and all old
loop substitutions fail the same test. Alignment is derived from terminal DAC
silence and the measured mute drain; transition guards are explicit. This is
finite-loop discrimination, not sample-exact timing or NES audio fidelity.

Four approximate Paula voices still lack faithful NES envelope, length, linear,
sweep, DMC, nonlinear mixing and noise-loop behavior. Audio plans publish only
at completed native RTIs and persist while slow native work runs.

## Measured limits

With display DMA contention enabled, progression spans 100,313,862 CIA E-clock
ticks, 141.410814 seconds at709,379Hz. All395 updates are late. The longest
publication interval is2,207,560 ticks. The final CHR mapping and complete redraw
span238,079 ticks, approximately335.62ms. These are instrumented diagnostic
intervals, not game FPS, full PAL speed or a controlled optimization comparison.
Physical Amiga hardware has not been tested. No gameplay or playable-game claim
is made.

## Source-only checks

The public suite denies cartridge reads and original-oracle imports, compiles
with the pinned GCC14 toolchain and assembles a complete target with synthetic
zero resources. It covers 1,024 title continuations, 256 scanout cases, 262,144
keyboard cases, 11,776 planner cases / 23,552 user-mode planner calls, explicit
08 DMA-pointer/length/period/volume checks, 16 linked composed frames and
22 fail-closed complete-target fault cases. The faults include both long-journal
sentinels, helper/count/capacity limits, input/audio exhaustion, invalid device
modes and permanent drain/mute/error retention. Synthetic clocks are not timing
measurements. Private captures, PCM, disks, state and game assets are excluded
from the public source manifest.

## Independent-review verifier correction

Independent review found two checker defects, not a target rendering failure.
The original screenshot check derived RGB colors from the captured Copper list,
so paired corruption of that list and the screenshot could pass. The corrected
checker derives all 32 palette register/value pairs from the independently
original-verified palette and fixed declared RGB12 table. It also checks every
Copper setup word, all five bitplane pointers and the terminator. Expected RGB
pixels now come from the original-verified frame and that independent palette,
never the captured target colors. A paired all-magenta Copper/screenshot
counterexample and individual Copper-word corruptions must fail.

A pixel-function import also shadowed the audio-plan list in the <=256-RTI
spectral path. The import now has a distinct name, and the production spectral
branch has a source-only synthetic 20-RTI PCM regression, including its DC,
swapped-channel and wrong-tone negatives. This does not add short-history
hardware-capture coverage. The 395-RTI v3 capture continues to use its separate
retained-plan and stage08 PCM checks.

The pre-correction verifier was preserved byte-identically to its prior source
manifest, together with prior reports/logs, under the private v3
`pre-review-verifier` directory. Runtime, disk, capture and timing bytes were not
changed to remedy these checker defects. Corrected verification and replay logs
have separate names. The standalone independent reviewer had also confirmed all
32 actual v3 Copper colors and the complete actual-input replay before this fix.

## Packaging scope correction

The initial broad historical-manifest traversal over-collected research inputs.
The release closure is now a flat, reviewed generic-source allowlist. Original
ROM disassemblies and unrelated legacy experimental Paula files are excluded;
their workspace originals are neither read for this build nor deleted. A
historical manifest's references do not authorize importing additional files.
The builder verifies only the explicit approved closure, while retaining its
pinned finish-manifest, native-composite and title-planner byte checks. This is a
packaging/provenance correction, not a runtime or capture change.
