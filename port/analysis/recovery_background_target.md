# Background-only stock-target optimization

An additive candidate preserves the dirty renderer's full ABI and scene semantics
while reducing the measured uninstrumented final-render interval by 9.55% with
five-plane display DMA active and 10.67% with display DMA off. The original
renderer, all prior experiments, the profiler, and the delivered disk are untouched.
No sprite, dispatcher, journal, audio or input implementation is changed.

## Implementation and proof

`recovery_background_single_read.s` pairs two scanlines per loop and hoists the
framebuffer tile-row base, following the existing compact experiment. It additionally
reads each CHR high-plane byte only once, holding it in D5 for the plane-1 write and
opacity OR. D5's palette value is no longer needed after D1/D2 are constructed.
All eight rows and all five planes still receive the same writes for every dirty
tile, including clearing sprite plane 4. No work is skipped for a dirty tile.

The cache key, unchanged-tile rejection, attribute quadrants, viewport/borders,
opacity, and explicit caller CHR invalidation contract are unchanged. In particular,
CHR changes without invalidation intentionally retain the old cached output, and
external framebuffer edits in unchanged tiles are intentionally preserved. Registers
D0–D7/A0–A6 are preserved, the routine returns normally in user or supervisor mode,
and additional stack use remains 60 bytes. There are no new tables, buffers or
runtime initialization passes. The module is 236 bytes versus the original 204.

The public test loads the SHA-pinned original test read-only and preserves its
independent per-pixel reference. It executes actual assembled baseline/candidate
code for seven dirty/unchanged/attribute/CHR/new-buffer cases, three random seeds,
and both user/supervisor modes: 84 cases pass. Width-aware traced reads and writes remain entirely within the ABI regions,
assembled code and return sentinel; writes are limited to the three writable
buffers or 60-byte saved-register stack region. Unchanged cases perform no output
writes. Full buffers, cache, opacity, code/NT/CHR immutability, all registers, stack
return and buffer/stack guards are checked. Every test-source substitution asserts
uniqueness so a drifting predecessor cannot silently omit the added checks. These host tests do
not provide timing evidence.

Both actual fresh candidate captures pass the unchanged original target verifier:
1229 completed helper calls, 43 logical RTIs, 322 native APU writes, original
RAM/context/runtime, every ordered journal and DMA byte, final device state,
all five bitplanes, displayed RGB pixels, completed shadows/plans and actual
callback PCM pitch/stereo/silence checks. DC-only, swapped-channel and wrong-tone
counterexamples reject. All 14 complete-target failure/mute/drain/error-identity
regressions pass for each build, and compiled adapter unit tests pass on the on
build. The comparison additionally establishes byte-identical adapter, sprite and
clock modules, nametables, palette, OAM, selected CHR, final framebuffer, opacity,
cache, sprite scratch, screenshot and all 43 completed audio payloads versus the
matched uninstrumented controls. Live timestamps and relocated addresses are not
asserted identical.

## Actual CIA measurements

The pinned frontend/core use PAL A1200OG, 68020/AGA, 2 MiB Chip, zero Fast, and CPU
and memory cycle exact. Every capture completed all 6000 callbacks normally. The
chained 32-bit CIA-B clock is nominally 709379 Hz. Neither candidate nor control
contains segment probes. No host instruction count or instrumentation subtraction
is used. Each candidate mode has one actual fresh run; no physical-hardware claim
or run-to-run variance estimate is made.

- Display on: control 63649 ticks (89.725 ms), candidate 57569 (81.154 ms), saving
  6080 ticks / 8.571 ms / 9.5524%.
- Display off: control 56614 ticks (79.808 ms), candidate 50573 (71.292 ms), saving
  6041 ticks / 8.516 ms / 10.6705%.

These are complete final CHR/background/sprite render-call intervals, not isolated
background costs. Attribution is to the whole background-only candidate change;
there is no ablation claim for the single-read subchange. The prior fully unrolled
experiment was substantially slower; it was not repeated or adopted here.

On progression is 991307 ticks versus control 991535, with 40 of 43 updates late
and maximum publication interval 91034 versus 91343. Off progression remains
862746 ticks, 30 late updates, maximum interval 80395. Those small differences in
unchanged work can follow layout/display phase and are not claimed as optimized
progression. Audio payloads agree, but PCM timing/sample streams need not be exact
copies because publication times differ. Each actual capture independently passes
the audio oracle.

The 81.154 ms display-on final render remains far above a 20 ms frame budget. This
is still one final render of the scripted FE24-to-C5F8 menu, not continuous rendering,
live input, playable gameplay, a completed port, or a frame-rate result. Finite-noise
and fixed-stereo audio approximation limits and all 256-RTI/capture guards remain.

## Memory and provenance

On payload is 811008 bytes, allocation 811520; off payload 810936, allocation 811008.
Both grew 32 payload bytes versus their controls. The on allocation increases one
512-byte block because the existing guard/rounding crosses a boundary; off remains
unchanged. Adapter extent remains 22336 bytes, existing buffers/stack unchanged.
No CPU/memory configuration adjustment is used to obtain the result.

Private fresh capture evidence: `port/build/recovery_background_v2/on` and `off`.
`port/build/recovery_background_v3_buildproof/public-bounds-test.log` records the
final 84 width-aware synthetic cases. The v3 build-proof on/off directories contain
new source-only rebuilds byte-identical to the respective captured v2 ADFs. The
builder also assembles a same-layout frozen reference, using the original renderer
plus 32 padding bytes. Every linked byte before and after the background routine
must equal that reference. This includes relocated device/runner references and
all sprites, clock, audio, resource and data bytes; the full old device hash is not
simply waived in favor of a length assertion. `comparison-on.json` and
`comparison-off.json` record exact SHA256 provenance of candidate and reused control
ADF, linked payload, complete Chip capture, PCM, raw screen, log and verifier report.
The controls are the already qualified fresh uninstrumented profiler controls:
`port/build/recovery_profile_v1/control-on` and
`port/build/recovery_profile_v2/control-off`. They were read, not rerun or modified.
Their on/off render timing matches the frozen menu/Paula checkpoint. Controls are
not instrumented merely because their parent folder contains the word profile.

The first `recovery_background_v1/on` build stopped before producing an ADF at an
incorrect expected device-extent assertion (expected 1786, actual 1782). The assertion
was corrected to the measured assembly extent; no behavior changed, and that partial
build was never executed or qualified. The successful new v2 directories did not
overwrite it. Nonfatal plotting cache warnings in on verification did not prevent
completion; off used writable cache directories.

Delivered disk SHA256 remains
6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17.
No commits/publication, README changes, aggregate updates or private artifact delivery
were performed. See the separate restore recipe and source-only allowlist manifest.

## Independent review

A separate reviewer reproduced the strengthened 84-case public test and both full
original/PCM verifiers on private capture copies, all 28 linked-target failure
cases, and both candidate/control comparisons. Twenty-eight additional adversarial
assembled cases using boundary tile IDs, uniform/alternating CHR patterns and
permuted palettes passed. The review found no semantic defect. An isolated generic
source closure plus only the approved cartridge rebuilt the display-on ADF exactly,
including the strengthened same-layout isolation assertions. No additional emulator
capture was needed or claimed by that review. Review evidence remains private under
`/workspace/scratch/43ecf79622a5/background-independent-review`.
