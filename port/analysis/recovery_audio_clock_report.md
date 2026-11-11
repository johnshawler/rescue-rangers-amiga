# Superseding callback-clock audio verification

## Correction and scope

The prior claim that the approximately 2.156 ms local mute/filter endpoint bound
was the TOTAL PCM-window placement uncertainty is withdrawn. It omitted an
accumulated CIA-to-callback clock-scale error. Tests of shifts around the old,
incorrectly mapped windows did not repair that omission. The earlier reports,
verifiers, successes and failures remain unchanged as superseded historical
evidence; none is relabeled as a corrected PASS.

This additive layer corrects timestamp mapping, finite-loop playback sampling,
pulse-harmonic masks and gameplay tonal frequencies together. It reads four
existing captures and writes separate results. No renderer, target, audio plan,
wave table, binary, input schedule or capture is changed. No new capture is made.
No guard, eligible RTI, minimum window length, phase search, alternative waveform,
correlation/margin threshold or tonal tolerance is selected to fit these results.

## Attested clock model

Each of the four runtime logs has boot SNDRATE 312*227*50 = 3,541,200 followed by
stable SNDRATE 313*227*50 = 3,552,550, established before the callback-format line.
The parser accepts only these supported startup values, a final stable clock,
PAL A1200OG/68020 cycle-exact configuration, 44,100 Hz/50 Hz callbacks, anti
interpolation, emulated filtering and muted drive audio. Missing, inconsistent,
unsupported, late-changing or ambiguous rates/configurations fail closed.

Production verification hashes the approved core, callback frontend and eight
relevant core source files before interpreting a log. The pinned chain is:
custom.c computes the SNDRATE clock; devices.c passes it to update_sound;
retrodep/sounddep/sound.c calculates the stored float32 sample-event interval;
audio.c schedules callbacks; cia.c defines one CIA tick per five CCK. The
multiplier is 1 and CYCLE_UNIT is 512 in this pinned implementation.

The stored scheduler interval is exactly 41,245.0234375 internal units. Preserve
that binary32 value as a rational, then multiply by 44,100/512 WITHOUT another
float32 rounding. Effective callback-domain rates are:

- CCK: 3,552,549.870300293 Hz.
- CIA: 710,509.9740600586 Hz, exactly CCK/5.

The source/runtime model is not a fitted spectral rate. 3,552,549.75 is a further
float32 roundtrip and is not the exact scheduler-derived rate. Even the logged
integer 3,552,550 and exact effective rate can produce a few different template
floor indices in longer windows, so the complete analysis uses the exact model.

The fixed signed-byte noise tables remain unchanged: their generator describes
what was compiled into the target, not a clock to use when analyzing playback.
The new classifier samples those exact existing tables at the callback-domain
CCK/160 rate. Only analysis timing/frequencies change. The inherited FFT,
normalization, waveform alternatives, equal 128 phases and strict >0.45 / >0.08
acceptance tests remain the frozen implementation's model-independent operations.

## Separate endpoint, scale correction and quantization

A terminal anchor removes a constant offset, not a rate error. For terminal
anchor tick T and earlier boundary t, the omitted nominal-model displacement was
(T-t)*(1/709379 - 1/callback_CIA). Each corrected report records this historical
error for EVERY selected boundary, separately from current uncertainty.

Leading-edge omissions at RTIs 380–383 were:

- Original stage v3: about 8.17–9.91 ms.
- Optimized stage v1: about 4.43–5.37 ms.
- Original five-frame play v3: about 12.83–14.63 ms.
- Combined five-frame play/background v1: about 7.74–8.74 ms.

The old approximately 2.15 ms endpoint argument did not cover those errors.
Correcting timestamps alone is insufficient: independent diagnostics show the
optimized stage's RTI383 still rejects with nominal-rate templates. Correcting
both domains makes all four captures pass, including the old stage control
previously rejected by the nominal stronger classifier. That old rejection is
not evidence of a changed control waveform.

Each new capture report recalculates the local endpoint bound using its own
stop/render-end telemetry, final audible periods and callback clock. The fixed
drain is 14,188 CIA ticks, not an assumed 20 ms of callback time. Two maximum
audible periods, a conservative five-stage/32-sample filter tail and one sample
of anti/endpoint quantization are included. The known nonzero final pulse,
muted drive audio, direct callback copies and no other terminal stream remain
capture-specific premises inherited from the pinned source audit.

The local endpoint bound is approximately 2.1253–2.1535 ms across the four
captures. An additional conservative allowance covers two CIA quantization
ticks, one output sample of mapping/rounding and one internal scheduler unit.
Total corrected placement uncertainty is approximately 2.1508–2.1790 ms. The
nominal-clock accumulated error is CORRECTED by the exact stable model; it is
not hidden inside this local bound. Each total is less than the unchanged
20 ms trailing guard and the tested ±100 output samples (±2.26757 ms).

All 201 integer offsets from -100 through +100 are tested for every corrected
noise window. This bounds the admission decision over the justified remaining
uncertainty; it does not select different production windows or establish
arbitrary-shift/global-latency invariance.

## Results and preserved criteria

All four immutable captures pass the corrected layer:

- recovery-stage-target-v3: 4 noise windows, minimum margin 0.272266.
- recovery-stage-background-v1: 4 noise windows, minimum margin 0.176163.
- recovery-play-target-v3: 4 noise windows, minimum margin 0.288463.
- recovery-play-background-v1: 4 noise windows, minimum margin 0.207303.

All 3,216 integer-shift classifications pass, overall minimum margin 0.175966.
Each production window rejects DC, the actual swapped channel, and all 128 phases
of each of the three old loops. All four waveforms receive equal phase search,
including the additional half/double playback-rate alternatives. The same four
eligible RTIs are used in each capture, no eligible audible window is skipped,
and the physical guards stay 110 ms leading / 20 ms trailing with minimum
2,000 samples. Corrected sample coordinates necessarily differ from the old
mis-mapped coordinates; that is a clock correction, not window fitting.

Both play captures additionally pass the same five original-derived gameplay
windows: 10 tonal windows and 30 DC/channel-swap/wrong-tone negatives. Guards
stay 110 ms leading / 30 ms trailing, minimum length stays >4,000 samples, the
stereo RMS gate stays >100 and pulse-peak tolerance stays <8 Hz. Original code
and device replay rederive the five RTIs and expected plans; they are not chosen
from the PCM. Right pulse/triangle coincidence is not an isolation proof.

The public suite passes 19 malformed/unsupported/ambiguous rate/config negatives,
changed-source rejection, exact old/new classifier parity at an equivalent
nominal rate, and 3,162 corrected-rate synthetic phase/window classifications.
Those cover all four waves, off-grid fractional phases, gain/DC, mixed filtered
pulse positives, white/random noise, tones and half/double-rate negatives.

## Performance and qualification boundaries

Raw CIA counts and matched percentage reductions are unchanged. Earlier printed
335.616 to 168.230 ms redraw numbers are nominal PAL HARDWARE-EQUIVALENT
conversions using ticks/709379, not callback PCM wall-time. This audio correction
does not silently redefine those measurements, change target timing or claim
physical-Amiga performance. Game FPS is still not established.

These results establish bounded callback-domain finite-loop/tonal evidence, not
NES waveform/envelope/mixing fidelity, exact phase, small pitch-error rejection,
independent triangle amplitude or absolute latency. Overall combined-target
qualification additionally requires its separately owned native/state/device/
pixel/runtime review. An audio PASS alone is not that complete qualification.

The exact log/RAM/PCM/screenshot/target/adapter/boot/ADF/build identities are in
recovery_audio_clock_capture_manifest.json as hashes only. No proprietary asset
is included in the source package. Corrected results live separately under
port/build/recovery-audio-clock-v2; all old report paths remain unchanged.
