# Capture-specific PCM anchor bound

This is a placement/robustness bound for the retained optimized v1 capture, not
an absolute audio-latency measurement. The classifier's original windows,
thresholds and terminal-silence anchor are unchanged.

## Pinned implementation and endpoint

The approved PUAE binary SHA-256 is
`84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456`.
Its clean local source checkout is commit
`d366f77c60e5a5f059f129cc3773d3048306083b`. Reviewed source identities:

- sources/src/audio.c: `4f010577a1a3d8338da94aa26681ac95a813164331874b2b9f2a20661199aeb0`.
- libretro/libretro-core.c: `ba1024fdd269b6609283f719054bcaa50a33cb6425eff0be6a5d463863a74171`.
- sources/src/driveclick.c: `c265db935b3dc1f1fae49607fe99c3e8733cc56f4ac1a9955992f6e29e81c33e`.

The unchanged headless binary is SHA-256
`5a6caac3c484c24a979800188070abb78c7fdbe648106fb84c5d8532e19052b1`.
Core retro_audio_queue copies samples into the callback buffer; the frontend
writes callback samples directly to PCM, without a further resampler. Buffer
batching therefore does not add or remove samples from the captured timeline.

Actual configuration is 44,100 Hz, anti interpolation and emulated filtering.
Although floppy0sound through floppy3sound are 1 (sample types enabled), the
same full.log explicitly sets floppy_volume=100, which means mute. Core
libretro-core.c documents this convention; driveclick.c multiplies samples by
(100-volume)/100. Empty-drive fallback is also100 when disk volume is100.
Drive-click/motor samples therefore contribute exactly zero. This is an
A1200OG ADF-only boot with no CD medium or expanded sound device. The resident
native target makes no disk/CD/board I/O calls after boot; its sound output is
only the four Paula channels. The terminal tail decays normally into more than
105 seconds of continuous exact zero.

The final verified plan is periods 1011/2266/567/160 and volumes 18/20/24/0,
with pulse waveform 2 on the left and muted noise. The left pulse has nonzero
samples until explicit mute, so an earlier natural silent interval does not
supply the terminal endpoint. The last nonzero captured sample is 5,044,030.

## Conservative bound

The unchanged adapter writes zero to all four volume registers, reads its drain
start, waits at least 14,188 CIA ticks, stops DMA and records stop. Captured
render_end=53,695,118 and stop=53,709,398. Their difference minus the required
drain is 92 ticks. Consequently all pre-drain mute-write work, polling overshoot
and post-drain stop work together are bounded by 92/709379 seconds.

Core audio.c AUDxVOL stores audvol; loadper transfers it to mixvol on sample
period reload. Both high- and low-byte states call loadper while DMA is active.
We nevertheless allow TWO maximum audible periods: 2*2266/3546895 seconds.
The optional volume-counter FIR memory is shorter than this allowance.
Anti interpolation retains at most one output sample interval.

The filters are at most five positive RC stages, with cutoffs at least 6,200 Hz;
rc_calculate_a0 at 44,100 Hz gives every coefficient greater than 0.48. Start all
five hypothetical stages at 65,536, twice the maximum signed16 input. Iterate
32 zero-input samples using a slower 0.48 coefficient, a 1.000001 multiplicative
rounding allowance and 1e-8 additive allowance per stage. The final bound is
0.1916013, below 1 and thus zero after integer truncation. This covers both A500
and A1200 modeled filter chains, even though the selected machine is A1200.

The conservative sum is:

- Mute/control overhead:0.129690899 ms.
- Two maximum audible periods:1.277737289 ms.
-32 filter samples plus one output-sample quantization interval:0.748299320 ms.
- Total:2.155727507 ms.

This is below the unchanged 20 ms trailing guard, establishing interval placement.
The independent reviewer separately tested EVERY integer shift from -100 through
+100 samples, all four windows: 804 checks, all admitted. That range is
±2.267573696 ms, larger than the conservative bound. Minimum discrimination
margin was0.081727945. This independently establishes decision robustness over
the justified placement uncertainty; it is not a new window selection.

A +220-sample (~5 ms) shift conservatively rejects RTI383, as does +441 samples.
These out-of-bound sensitivity findings remain disclosed. No global latency,
waveform fidelity, arbitrary time-shift invariance or physical-hardware claim
follows from this capture-specific bound.

`port/tests/recovery_stage_background_pcm_anchor.py` reproduces the numeric
capture checks. Source/callback premises above were independently reviewed;
those implementation sources are tooling, not added to the public source closure.
