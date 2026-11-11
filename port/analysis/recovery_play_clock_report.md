# Corrected-clock combined comparison companion

This additive layer supersedes the audio gates/anchor labels in the frozen
recovery_play_background_compare.py without modifying that file, captures,
targets, or historical PCM failures. Both inputs require the exact separately
reviewed corrected-clock reports. No nominal PCM report serves as a gate.
Independent review of this new comparison layer is pending.

The companion pins the 9 original capture identities plus target symbols,
original/state/device/Copper/pixel verification and complete boundary replay
reports. It checks those hashes before and after execution, reattests tool
sources, core/frontend, stable SNDRATE and configuration, and checks corrected
report identities, full model, window/threshold coverage and placement bound.
This composes existing immutable verification evidence; it does not pretend to
rerun every runtime verifier. It independently regenerates complete original
helper histories from the approved ROM and actual input events, including all
RAM/context/journal/runtime-check bytes and ordered events. Final byte equality
alone cannot enable percentages. It rereads publication and final-render raw
CIA records. The progression field comes from the pinned runtime verifier.

Both captures have 14,655 helpers, 757,491 original instructions, 400 NMIs and
five gameplay updates. Full history SHA256:
367afea1533b7089d23dcc50d8787748e70d39dfab3d18ff92474d847e722544.
Final RAM/context/runtime, nametables/palette/OAM/CHR/frame/opacity agree.
Both remain zero Fast and 400/400 updates late.

Candidate versus control raw CIA ticks:
- Final redraw: 119063 versus 238458; reduction 50.0696139362%.
- Five publication intervals: 1356167 versus 1953053; reduction 30.5616898261%.
- Entire bounded progression: 59922010 versus 107331405; reduction 44.1710373585%.

Percentages are computed only from matched-history raw ticks. Nominal PAL
hardware-equivalent conversion uses 709379 CIA Hz: final redraw 167.841168 ms
versus 336.150351 ms. Separately labeled callback-domain conversion uses the
source/runtime-attested 710509.9740600586 CIA Hz: 167.574002 versus 335.615275 ms.
Neither is a host benchmark or a physical-hardware execution measurement.
The five intervals include prior rendering and native engine/scheduler/NMI/
adapter work, exclude the final post-publication renderer and do not establish
sustained FPS. Audio remains approximate finite-loop discrimination and selected
tonal peaks, not envelope/mixing/triangle isolation, phase continuity or NES
fidelity. Prior nominal conclusions/failures remain historical evidence.

Source-only tests reject 32 component/model/config/coverage/criteria failures,
changed/missing evidence, and matched-history final-state disagreement. Four
independent complete-history mutations suppress every reduction percentage.
Fresh output is mandatory; writes into frozen capture directories are refused.
