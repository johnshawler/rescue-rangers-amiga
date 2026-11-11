# Independent envelope domain oracle

`port/tests/recovery_music_envelope_declarative.py` is a ROM-free, structured
model of the indexed envelope path beginning at $86B2 and ending at its real
RTS destination. It is written independently from the new native translation,
using original-ROM inspection for behavior. It contains no opcode decoder,
opcode dispatch loop, original cartridge bytes, captured states, or traces.

The model accepts caller-supplied 16KiB resource data and returns complete RAM,
canonical context, and ordered semantic resource/APU/RAM events. It models
attack, decay, sustain, release and completed stages; CF APU inhibition;
triangle gating; amplitude and pitch modulation; glide convergence; and
phase advancement. Domain arithmetic explicitly retains original carry,
overflow, zero and negative status, all stack-frame stores (including dead
stores), page-one wrapping, and the real caller return address.

The companion ROM test compares 16,384 generated states against independent
actual-ROM execution, including full RAM/context and all ordered effects. The
ROM-free native contract uses synthetic resources, four indexed channels, all
five stages, varied flags and SP, and pointer endpoints $8000/$BFF8. It checks
native ABI, globally bounded memory accesses, immutable resources, and the
complete resource/APU journal. The original cartridge is never required by
the public test; py65 is not imported there.

Accepted resource contracts are a bank3 window, instrument pointer in
$8000–$BFF8, stage0–4, the five actual stage-dispatch addresses, and threshold
zero at $892E. These are semantic addresses, not embedded cartridge data.
The pointer endpoints ensure all eight instrument bytes are bounded; the
threshold ensures the original downward search terminates inside its table.
The model is an oracle, not production initial state or a replacement runtime.

New files:
- `port/tests/recovery_music_envelope_declarative.py`
- `port/tests/recovery_test_envelope_declarative_contract.py`
- `port/tests/recovery_test_envelope_declarative_rom.py`

This proof does not establish authentic reset/frame continuity, audio device
rendering, game speed, or physical hardware behavior. The separate
[resident startup proof](recovery_resident_startup_fade.md) connects this
envelope implementation with the surrounding native runtime.

Verified results: 16,384 independent actual-ROM/domain-model comparisons and
16,384 ROM-free domain-model/native comparisons passed. The public suite also
passed 117,978 inert guard cases, exhaustively covering wrong entry PCs,
unsupported status/index values, every out-of-window pointer, all nonzero
threshold bytes, each altered dispatch-table byte, and stages5–7. Each accepted
case compares exact native semantic read order after the documented preflight.

Frozen model SHA256:
e820aa7d3ed2a072362492737624a2621fb50a84c55c4d9d7b96c62713978be3.
