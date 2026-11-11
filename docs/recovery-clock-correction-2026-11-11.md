# Corrected audio-clock evidence

The prior claim that a roughly 2.156 ms local terminal/filter bound covered all
PCM-window placement uncertainty is withdrawn. It omitted accumulated error
from using nominal PAL CIA timing to locate samples in this emulator's callback
stream. That omission affected the old phase-aware comparisons and their
interpretation of the original control. No target or recording changed.

The pinned core source and each retained runtime log establish a stable sample
scheduler with an effective callback CCK rate of 3,552,549.870300293 Hz and one
CIA tick per five CCK. The corrected validator uses the exact stored binary32
scheduler interval for timestamps, waveform sampling and tonal masks. It does
not fit a rate to the observed spectrum. Core/frontend/source and all capture
identities are checked before analysis.

Independent review of the 816-file source-only restore and the production
outputs passes. Across the four retained captures, all 16 eligible noise
windows and 3,216 bounded alignment classifications pass, as do 10 gameplay
tonal windows and 30 negative controls. Existing guards, eligibility, phase
search, correlation thresholds and alternatives are unchanged. This is bounded
finite-loop/tonal evidence, not complete NES audio fidelity, exact phase or
absolute-latency proof.

The old nominal-clock reports and failures remain unchanged. The new report
separates corrected accumulated scale error from residual endpoint and
quantization uncertainty. Raw CIA timing counts and matched percentage
reductions do not change. Legacy milliseconds use nominal PAL hardware-equivalent
conversion; callback-domain time must be labeled separately. No physical-Amiga
measurement or playable frame rate is claimed.

See [the corrective source report](../port/analysis/recovery_audio_clock_report.md)
and [its restore procedure](../port/analysis/recovery_audio_clock_restore.md).
The original game ROM, firmware, private assets, binaries, disks, captures and
PCM are excluded from this public source checkpoint.

## Combined-target comparison

The additive comparison layer was reviewed separately against manifest
c1d835732073cb44c7a52e1b9c8a2d376f7552e4743d20701941f126086eaa48.
It joins the corrected audio evidence with the already reviewed native/runtime,
ordered-device, final-display and boundary-replay evidence. It rederives full
original execution histories, verifies immutable capture/report identities,
checks model/configuration/coverage gates and suppresses every reduction
percentage if complete histories differ. It does not rerun or replace all the
pinned runtime verifiers. The frozen author report and result retain their
pre-review labels; this current summary records the subsequent review.

For the same 14,655 helpers, 757,491 original instructions and 400 logical NMIs:

- Final redraw: 119,063 versus 238,458 raw CIA ticks, a 50.0696% reduction.
- Five publication intervals: 1,356,167 versus 1,953,053 ticks, a 30.5617% reduction.
- Entire bounded progression: 59,922,010 versus 107,331,405 ticks, a 44.1710% reduction.

Both captures allocate 860,160 Chip bytes, zero Fast RAM and miss all 400 update
deadlines. The five intervals include prior rendering and intervening native
engine, scheduler, NMI and audio work; they exclude the final post-publication
redraw. These results do not establish sustained game FPS or playable speed.
The final redraw is 167.841168 versus 336.150351 ms in nominal PAL
hardware-equivalent units, or 167.574002 versus 335.615275 ms in the separately
attested callback domain. Neither is physical-Amiga or host benchmarking.

The 822-file source-only restore and comparison failure/mismatch tests are
separate from the host input extension. That extension independently reaches
104 complete frames with held Right and Right+A, then rejects untranslated
F328 without state changes. It is not a claim of 104 rendered Amiga frames.
