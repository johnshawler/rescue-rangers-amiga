# Native input continuation checkpoint

This source-only increment follows the corrected audio/renderer checkpoint.
It adds bounded native translations of F328 targeting (helper152) and F977
candidate scanning (helper153). Earlier renderers, audio, binaries and captures
remain unchanged, so this increment has no new stock-target speed measurement.

F328 preserves the original direction choice, flags and wrapped stack effects.
F977 reads candidate data from the current immutable PRG and performs the actual
external collision calls into the already translated helper151. Neither module
uses a runtime opcode interpreter, captured execution state, replacement banks,
skipped original work or a new raw-status normalization.

Three original-first reset histories use held Right, held Right+A, and a distinct
A release/press sequence. Each reaches 22,045 accepted helper boundaries,
104 completed frames, 498 logical NMIs and 3,708 ordered APU writes, then rejects
untranslated F92B without mutation. The 240-frame goal is explicitly unmet.
The edge sequence delivers Right on frames 0–4, Right+A on 5–10, then releases A
through the original controller path. This establishes compared input delivery,
not visible jumping, pickup/throw or 104 rendered Amiga frames.

Both modules retain explicit bounds and inert unsupported states. For F977,
a cyclic candidate state exhausts the unchanged production instruction bound
and is rejected rather than reported as a supported wait or successful frame.
The authored finite suites are not exhaustive Cartesian coverage of all RAM.
See each immutable component report for the precise accepted and excluded
entry/caller/resource domains, coverage and source-only restore procedure.

Original ROM, firmware, disassemblies, private assets, generated disks/binaries,
RAM/PCM captures and later F92B development are excluded. The delivered Z/X ADF
remains unchanged. Both component freezes passed independent source-only restoration and original-first
review. The F977 review adds 224 fresh cases that cover all 59 owned instruction
PCs within the accepted domain, including the less common path into F6DC. This
is instruction coverage, not exhaustive branch-outcome or RAM-state coverage.
The component freezes retain their historical pre-review labels rather than
being rewritten after review.
