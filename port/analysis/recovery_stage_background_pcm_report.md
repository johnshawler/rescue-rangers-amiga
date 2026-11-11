# Additive short-window PCM discrimination

The original frozen stage08 PCM verifier remains unchanged. It rejected the
optimized capture's RTI380 window: wave8 correlation 0.52174 versus old wave6
0.46196 did not meet the required 0.08 margin. This is preserved as a failed
qualification result, not silently replaced with a passing legacy result.

The optimized renderer shortened the first stage08 intervals to approximately
198 ms. The unchanged 110 ms leading and 20 ms trailing guards therefore leave
2,984/2,965/2,982 samples (about 67 ms) in RTIs380–382 and 4,130 samples in RTI383.
One 2,048-sample Paula loop at period160 lasts approximately 92.4 ms. The frozen
zero-phase spectral template is sensitive to phase for sub-loop windows.

`recovery_stage_background_noise_pcm.py` is an additive classifier. It retains
all the original selected windows, minimum 2,000-sample length, terminal-silence
alignment, guards, 80–6,000 Hz band, pulse-harmonic exclusions, FFT size and
strict correlation >0.45 / margin >0.08 thresholds. Every waveform receives the
same 128 equally spaced phases, including all three wrong finite loops. A
synthetic half-speed negative exposed ambiguity in a phase-only prototype, so
the final classifier additionally compares every waveform at half and double
rate, with exactly the same phase search. These are additional rejection
hypotheses, not weaker thresholds or selected passing windows.

The ROM-free suite passes 3,162 classifications across lengths 2,000, 2,001,
2,984, 4,096, 4,130 and 10,415. Each tests all four waveforms at 128 off-grid
fractional phases with gain/DC changes. Adversarial inputs include constant/DC,
Gaussian noise, random signs, five tones, and half/double playback rate. Positive
mixed-channel cases include pulse contamination, a low-pass filter, gain and DC.

The unchanged optimized capture passes all four eligible retained windows with
correct-wave correlations 0.81956, 0.83720, 0.82993 and 0.77093. The largest
competing correlations, including the stronger rate-alias hypotheses, are
0.68006, 0.71044, 0.68599 and 0.68374. No eligible audible window is skipped.
Every window also rejects actual swapped channels, DC, and all 128 phases of
each of the three old loops. The minimum observed margin is about 0.08719,
above the unchanged 0.08 requirement. The frozen failure remains separately
visible in qualification evidence.

This establishes bounded discrimination of the intended approximate finite loop
from the enumerated alternatives. It does not establish NES audio fidelity,
exact waveform phase, small pitch-error rejection, absolute audio latency,
envelope or mixing fidelity. The new verifier requires independent review
before being used to qualify the target performance comparison.

A cross-check on the existing v3 control is intentionally disclosed: the stronger
rate-alias classifier rejects its longer mixed RTI380 window (correct0.60200,
half-rate wave5 alternative0.61098). The original frozen classifier still passes
that control, as before. This is a conservative additional-class rejection, not
evidence of a changed control waveform. The additive classifier is therefore
not claimed as a universal replacement for the original audio verifier. Its
acceptance claim is limited to the optimized capture and the stated synthetic
coverage; both capture outcomes are retained for independent review.
