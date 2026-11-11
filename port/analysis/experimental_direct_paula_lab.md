# Experimental direct-Paula frame-state diagnostic

## Result

Four real Paula DMA voices run an isolated, approximate title-profile replay on
stock PAL A1200OG: 68020 CPU and memory cycle-exact, AGA, 2 MiB Chip RAM, zero Fast
RAM. All 935 scheduled logical frames completed with zero rejected snapshots.
This is **not integrated native game audio**, not an exact APU, and not proof of
concurrent game performance. The delivered game disk and established checkpoints
are unchanged. No runtime 6502 interpreter is used.

Instrumented native planner plus custom-register update costs:

- 944 updates total: initial setup, eight synthetic blocks, 935 replay frames.
- Maximum 157 CIA E-clock ticks: 221.32 microseconds, 1.107% of a 20ms frame.
- Mean 174.40 microseconds. CIA E-clock nominally 709379Hz.
- Complete synthetic plus replay interval: 1334 CIA TOD ticks, about 26.68s.
  The intended sequence is 400+935 PAL frame waits; startup/TOD quantization
  explains why this coarse duration is not a cycle-timestamp claim.
- 32768 bytes allocated in Chip RAM; payload file 22752 bytes; complete linked
  memory extent 24800 bytes including 2048-byte stack. Immutable noise consumes
  6144 bytes; private frame states consume 14960 bytes; pulse/triangle 64 bytes.
  These components are contained within, not additional to, the32768-byte
  allocation. Loaded code/data/profile bytes are22752; stack/BSS extends this to
  24800; the remaining7968 bytes are reserved slack. Firmware/OS boot memory,
  trackdisk buffers and emulator/host capture storage are not included. This is
  a payload allocation measurement, not a claim of total system free memory.

These are emulated-target observations, not host timings. Timer reads use stable
high/low/high reads to avoid torn CIA counter values. Measurement includes timer
instrumentation but excludes the polling wait. The probe busy-waits between
frames, so its overall CPU utilization is not 1.107%. Display DMA is disabled,
there is no concurrent game work, interrupt integration, or physical-hardware
measurement. This specialized DMA update cost is meaningful independently; it
is not a direct comparison with other PCM implementations whose workloads and
fidelity differ, and is not a full-speed game claim.

## Evidence and scheduling

The private profile was independently inspected against its generator and log.
The unchanged complete comparison logged 28818 native helper calls, 935 reference
NMIs, 900 countdown visits and 7136 ordered APU effects. Its generator records
writes only from the reference bus being compared, and explicitly labels
pre-bootstrap NMI positions unknown. This work does not rerun that comparison.

- Profile SHA256: 5b2194214a7da982adeb963b9865698dde5b5208f6c80c2053caea828e242634.
- Generator SHA256: 9fa70196a3b70a6ba967c5af5ca67fa982355907fa2fdcbed4622615e8eb8f4d.
- Log SHA256: 559bce51a6b560817c480447cf2e46e41df9d7f0b2eee53505564cc3646f00e3.
- Underlying comparison source SHA256 recorded by the profile:
  85ddd9ea8780dc7ef33a06c097c85e3f0625119177c03f7627604fc41a6c4505.

Builder assertions recheck 7136 writes, constant-volume AND length-halt bits,
sweep08, triangle control00/FF, status0F, absent DMC writes, monotonic known NMI
labels, and audible frame-final timer ranges166..280,333..595,140..595.
Fourteen bootstrap writes have unknown timing and are applied before frame zero.
The initial noise selection is a synthetic muted07 default until the first write.

Events are consumed in source order into final register snapshots per logical
NMI. Empty logical frames retain their preceding state. Snapshots0..934 are
applied once per Amiga vertical blank. **Within-frame intermediate writes are
collapsed, not replayed at invented CPU times.** NES PAL frame rate and Amiga PAL
frame rate are not identical. Bootstrap phase, reference CPU-cycle timestamps,
and exact APU frame-sequencer state are unavailable. This diagnostic therefore
cannot validate original cycle-accurate register scheduling or audible equality
with the NES recording. Source-order snapshot reduction is the supported subset.

## Hardware mapping and deliberate approximations

AUD0=pulse1(left), AUD1=pulse2(right), AUD2=triangle(right), AUD3=noise(left).
Each DMA voice loops immutable Chip RAM. Pulse loops have8 samples and all four
duty patterns; triangle has32 steps. Integer periods approximate nominal clocks
1662607Hz NES PAL CPU and3546895Hz Paula. For timer t, pulse period is rounded
64(t+1)/15, triangle32(t+1)/15. Across the verified timer intervals, worst pitch
quantization is1.134,0.553 and2.596 cents respectively, before emulator clock
normalization. Captured FFT bins are not exact-pitch measurements.

The PAL noise table is4,8,14,30,60,88,118,148,188,236,354,472,708,944,1890,3778
CPU cycles per LFSR step. Thus07=148,0D=944 and81=short mode with8 cycles.
The short-mode step rate is207825.875Hz, far beyond normal Paula DMA bandwidth.
It must not be mapped naively to one Paula sample per LFSR step.

The builder instead box-integrates a15-bit LFSR at nominal rational clock ratios
into2048 signed8-bit samples per noise selection, played at period160 (about
22.168kHz). Taps1/6 are used for long/short mode, initial seed1. Every loop starts
from an independent seed; state is not carried across selections or loop wraps.
The finite92.385ms loop has endpoint/phase discontinuity, artificial periodicity,
and only a box filter, not ideal bandlimiting. Short-mode93/31-step behavior
depends on actual prior state, so the seeded loop is not universally equivalent.
Noise validation proves this defined approximation, not authentic noise fidelity.

Pointer/length changes are applied to the next DMA reload without forced restart.
Pulse duty and noise transitions therefore have loop-dependent latency (up to
approximately92.4ms for noise). Period and volume writes are immediate register
updates, not calibrated NES-phase events. No sweep, envelopes, length counters,
triangle linear counter, high-timer phase reset, delayed4017, IRQ/status reads,
or DMC is implemented. Triangle00/FF is an immediate mute/gate shortcut. Disabled
channels mute but the DMA oscillator continues. Re-enabling does not reproduce
NES length-counter semantics. There is no nonlinear NES mixer: independent Paula
voices have fixed stereo placement and simple linear volume scaling. A generic
APU journal cannot safely be routed through this API.

The adapter rejects unsupported constant/halt/control/sweep/noise states and
unsupported enable bits atomically. Audible periods below124 reject; muted
periods below124 clamp safely. Caller owns frame-state storage and output state.
Hardware setup belongs only to the standalone boot probe, which owns custom
chips and CIA timer A; it must not be transplanted into an OS task unchanged.

Hardware references consulted: [NESdev noise](https://www.nesdev.org/wiki/APU_Noise),
[NESdev PAL clocks](https://www.nesdev.org/wiki/PAL_video),
[NESdev APU](https://www.nesdev.org/wiki/NES_APU), and Commodore's
[Audio Hardware chapter](https://www.amigarealm.com/computing/knowledge/hardref/ch5.htm).
Direct NESdev page retrieval returned403; indexed source excerpts supplied the
PAL noise table and clock references. The hardware manual supports looping DMA,
nominal PAL clock and conservative period124 minimum. The implementation uses160
for noise, safely above that floor.

## Validation and private captures

`experimental_direct_paula_test.py` executes actual compiled M68EC020 planner
instructions:1600 synthetic cases,436 atomic rejections, preserved registers,
stack balance and output guards. An independent CPU-cycle prefix-integral noise
oracle matches all6144 generated noise bytes. These are host functional tests,
not target cycle measurements.

The strengthened stock capture verifier checks runtime stage, memory size,
CPU/memory timing configuration, immutable deployed wave/state bytes, individual
stereo channels, all-on and silence. It now distinguishes total RMS (including
DC) from mean-subtracted AC RMS. Total RMS alone is not audible loudness and would
incorrectly accept constant DC as working audio. Every isolated active voice must
have AC RMS above100; opposite sides and silence must be exactly zero. The entire
raw capture must contain no saturated int16 samples.

Measured DC / AC RMS values in the isolated active side are:

- Pulse1:0.81 /2428.26; pulse2:1.24 /2428.09.
- Triangle:1.95 /1173.34.
- Noise07:430.89 /1803.97; noise0D:1451.27 /2022.77.
- Noise81:1678.55 /198.28. Its total RMS1690.22 is overwhelmingly DC, not a
 1690-RMS audible noise signal. This short-mode approximation is nonconstant,
 but strongly biased and materially limited.

The pinned core's callback gain4/3 and configured volume give pulse/noise
unfiltered extrema±2560 and triangle±1920. Noise81's generated wave18..64 instead
gives expected bounds720..2560. Observed extrema: pulses and long noise±2560;
triangle±1918; noise81 1336..2132. Filtering reduces the short-mode AC swing.
Bounds allow two PCM units of rounding. Pulses, triangle and long noise must also
reach90% of their expected signed extrema, preventing arbitrary attenuation from
passing. Combined left/right extrema±5120/±4478 fit bounds±5120/±4480. No clipping
was found, and both silent channels are exactly zero. These are expected bounds
for this pinned emulator/frontend configuration, not universal physical DAC gains.

Half-second Hann windows show coarse pulse1/2 peaks440Hz and triangle220Hz,
versus nominal440.309/220.154Hz. Finite-loop harmonic tests use the six strongest
non-DC generated-wave harmonics per noise mode. They normalize all18 lines using
one shared clock inferred from the separate pulse1 capture, not an independently
fitted noise frequency. Pulse1 peak is440.92598Hz, giving an effective spectrum
normalization clock3552099.69Hz. This calibration describes emulator output;
it does not replace the nominal clocks in the backend or timing measurements.

For precision, the waveform harmonic index is a dimensionless multiple of the
2048-sample loop frequency. The capture FFT bin index is also dimensionless;
frequency in Hz is bin*44100/262144. Zero-padding yields0.16823Hz bin spacing,
but the half-second window still has2Hz native frequency resolution. Every
selected line must have a local peak within2Hz of its normalized expectation
and exceed1% of that noise block's strongest spectral magnitude. All18 pass;
maximum error1.31596Hz. Detailed indices, Hz and errors are retained in JSON.
For example, noise81 harmonic206 appears at2233.39691Hz versus2233.07048Hz
expected. Its generated strongest harmonic413 is attenuated by output filtering.
Negative validation checks also reject three deliberately corrupted in-memory
captures: constant-DC noise81, a saturated sample, and a wrong1000Hz noise81 tone.
No original raw capture was edited for these checks.
These assertions verify the known finite-loop approximation, not broad-spectrum
noise quality, NES phase behavior, or authentic NES noise fidelity.

Actual emulator callbacks are saved as `synthetic-blocks.wav` and
`private-title-replay.wav`, alongside raw stereo capture and JSON verification.
The title audio is profile-derived PRIVATE material. No subjective listening or
claim that every original instrument/SFX is faithful is made. Floppy sound is
muted (`floppy_volume=100` in this frontend means100 percent attenuation).

## Reproduce and restore

From the repository root, with the existing recovered cross-toolchain and tools:

    bash port/tools/experimental_direct_paula_run.sh /private/path/verified-title-apu-profile.json

The default sibling locations are `amiga-recovery-m68k`, `amiga-recovery-tools`,
and `rescue-recovery-inspection/.deps`; the runner supports PAULA_TOOLS,
PAULA_M68K_ACTIVATE, PAULA_DEPS, PAULA_CC, VASM and PUAE_CORE overrides. Required
private firmware is `artifacts/a1200-system/kick40068.A1200`. Existing `boot.s`
and `experimental_paula_headless.c` are read-only dependencies. The latter is
compiled to a separate private executable; no original frontend is changed.

All generated traces, wave headers, captures, binaries, firmware copies, emulator
RAM and disks stay in ignored `port/build/experimental-direct-paula/`. Never share
that directory wholesale. Private replay ADF SHA256:
41703d3e7b2ce23e582dc7435d72ec16bb1167ddac5ee359772396baaabc460e.
It is a diagnostic, not a replacement game disk.

`experimental_direct_paula_manifest.json` enumerates only new generic source,
test, build and report files. The original source and full24-artifact private experiment are preserved in
`port/build/experimental-direct-paula-checkpoint-v1/` before validation changes.
The corrected source-only handoff is preserved separately in
`port/build/experimental-direct-paula-checkpoint-v2/`. Only the capture verifier
and this report changed; existing probe/ADF/rawPCM and WAV bytes are unchanged.
The source-only tar archive includes those files
and the manifest, never private generated material. Restore into an empty staging
directory, verify each size/hash, then compare destination paths. Stop rather
than overwrite a different existing file. No Git/index changes or publication
are part of this experiment.

Next steps require authentic timestamp acquisition, explicit counter/phase
semantics, a lower-latency noise switching strategy, and integration into a game
VBL/audio scheduler before measuring simultaneous graphics/game/audio cost.
