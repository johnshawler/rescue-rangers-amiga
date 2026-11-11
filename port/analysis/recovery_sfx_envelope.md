# SFX envelope continuation

This additive, host-only native 68020 checkpoint independently qualifies the
SFX envelope at PRG3 PC 86B2. It completes the second real mixed NMI and continues
through later cursor-sound ticks without copying reference results into native
RAM or context. It is new recovery development, not recovery of lost later
playable source. The frozen music envelope, its guard, and its contract are
unchanged.

## Continuous result

Right and Left both complete the second mixed NMI at helper 1,262, NMI 42,
and genuine completed return 40, publishing FE9000100026FFA7 with bank 2
restored. The default bounded checkpoint reaches helper 1,429, NMI 46,
return 44: five additional returns beyond the predecessor, five SFX envelope
calls, and 12 ordered direct SFX APU writes.

The longer uninterrupted probe stops honestly at 8235FE0300A5F2A7, with bank 3
selected, after 1,765 helpers, 56 NMIs entered, and 53 completed returns.
It executes 16 SFX envelopes and 34 direct SFX APU writes. The cursor sound
is still active. The next original instruction is STY $CE in the high-bit
stream-command path. That continuation is not implemented here. The probe
has a 120-NMI safety cap; it reaches this unsupported boundary first.

Both histories begin at FE24, after the original NES hardware warmup, and
initialize native RAM/context once. They do not prove the reset-vector warmup.
The original instructions run first at each successful continuation; their results
are compared, never injected. Caller frames, NMI frames, dead stack bytes,
resource state, and mapper state persist naturally. The frozen tick helper's
already-qualified 82C0 continuation is composed after the envelope's real RTS,
including its actual 85A5 return path. No envelope, command, or return is skipped.

Neutral and confirm remain at their prior boundaries: respectively 1,219 helpers,
41 NMIs, 39 returns, A06CFFFFFFA4BDA7; and 1,196 helpers, 40 NMIs, 38 returns,
C5F8F800FF27BFA7. All four default histories, both longer histories, and the
16 immediate predecessor tick, parser, event, and active-control histories pass.

## Standalone contract

`recovery_sfx_envelope.s` accepts PC 86B2, X 0–3, every raw status byte and
stack pointer, and arbitrary other RAM/context bytes subject to these guards:

- The low three bits of RAM[0704+X] must be 0–4.
- The little-endian instrument pointer at C5/C6 must be 8000–BFF8.
- Resource[892E] must be zero, bounding the pitch lookup search.
- The five dispatch pointers at 86BF–86C8 must select 86C9, 86DE, 8718,
  86FA, and 890D, respectively.

A0 addresses 2,048 RAM bytes; A1 addresses eight context bytes; A2 addresses a
514-byte journal; A3 addresses an immutable 16,384-byte bank-3 data view.
The caller supplies valid, disjoint, exclusively owned buffers and selects
PRG3. The composite additionally verifies the live mapper. D0 returns 1 on
success or -1 for rejection. D1–D7 and A0–A6 are preserved. Native CCR is scratch.

All unsupported inputs reject before any RAM, context, or journal mutation.
Successful calls clear only the journal count, append ordered resource/APU
records, and leave the unused journal tail unchanged. RAM writes, including
synthetic 6502 stack writes, remain ordered effects rather than journal records.
Every return consumes the real wrapping page-one stack. A coincidental return
PC inside this routine is published without executing a fictitious continuation.

The separate entry implements direct SFX volume publication regardless of the
music CF/CD/CC controls, all four channel mappings, clipping, triangle/noise
behavior, pitch modulation, D6/D8 scaling, signed fine pitch, glide, and
instrument phase advancement. Arithmetic is NES binary ADC/SBC even with D set.
PHP pushes the original raw flag byte with B/U set; PLP follows the original
instruction oracle's raw B/U convention. Standalone tests compare exact P,
without normalization. Continuous comparisons retain the frozen architectural
B/U view and do not modify original flags or stack bytes.

## Instruction and resource audit

All 343 static instruction annotations match the cartridge. The SFX contract
makes 323 instructions reachable, and the independent original execution suite
executes all 323. Twenty music-only instructions are excluded:
871C–872E, 8739–8749, 8754, and 8757. The audit script computes the exact set;
the intervals here denote instruction addresses, not arbitrary byte ranges.

The reachable work comprises the 86B2 stage dispatch, attack/decay/sustain/release
paths, direct publication at 8730, volume/modulation through 87A7, pitch through
8898 including 8811–882D scaling, glide through 88F0, phase advancement through
890D, and the 8006 multiply, 8023 dispatch, and 80CF APU helpers.

Every resource access has a bounded source:

- Dispatch consumes the authentic 86BE JSR frame and reads 86BF–86C8.
- Instrument accesses use offsets 0–7, hence remain inside the guarded bank.
- Envelope-rate indexing reads 890E–8A0D.
- Pitch search reads 892E–8935, at most eight times because 892E is zero.
- Glide indexes are even bytes after ASL, bounding reads to 8934–8A33.

The guard reads 892E and the ten dispatch bytes before mutation; these validation
reads are distinguished from semantic resource effects. There are no stream
commands, mapper writes, or resource writes inside this helper. Each multiply
runs exactly eight iterations. Pitch shifting runs at most seven iterations.
At most 24 semantic resource/APU records can be emitted, below the 128-record
journal capacity. Original control flow, rather than a step-limited interpreter,
determines completion. No generic 6502 interpreter is used in native code.

## Verification

The main suite covers 132,864 accepted cases and 117,754 inert rejections in
each mode. Accepted cases include every raw P/SP pair, every D6/D8 pair,
all SFX channels and stages, randomized full RAM, bank ends, page-crossing
instrument addresses, and seven coincidental return destinations at every SP.
The directed suite adds 34,448 cases: pitch/carry extremes, all 256 control bytes
crossed with 16 amplitude nibbles on all channels, and raw PHP/PLP flags with
both glide directions at stack-wrap edges.

The optional cartridge mode executes original instructions first and compares
both the independent declarative model and native implementation with full RAM,
raw context, and every ordered effect. Default tests use synthetic caller-owned
resources and require no ROM. The source-only isolation runner copies only the
new public sources/tests, denies ROM opens and private reference imports, and
runs the default suites. Native checks include complete journals and untouched
tails, immutable code/resources, register/SP preservation, canaries, and global
read/write bounds. The instruction audit checks annotated opcode semantics
against the original cartridge only when explicitly requested.

The predecessor frozen map contains 750 verified unchanged files. Public files
contain no cartridge or firmware bytes, extracted assets, music profiles, or
captured RAM. Detailed private traces and terminal snapshots are reproducible
outside the project using PRIVATE_TRACE_DIR.

## Reproduction

From the project root, set VASM to the pinned vasm executable and PYTHONPATH to
the installed machine68k/py65 dependencies:

```sh
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_test_sfx_envelope_isolated.py
python port/tests/recovery_test_sfx_envelope.py --rom
python port/tests/recovery_test_sfx_envelope_edges.py --rom
python port/tests/recovery_test_sfx_envelope_audit.py --rom
for input in 0 16 1 2; do
  CHARACTER_INPUT=$input python port/tests/recovery_test_resident_sfx_envelope.py --rom
done
for input in 1 2; do
  CHARACTER_INPUT=$input AUDIO_RETURN_CAP=118 \
    python port/tests/recovery_test_resident_sfx_envelope.py --rom
done
```

The cartridge must be input/rescue-rangers-europe.nes, SHA-256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
PRIVATE_TRACE_DIR must resolve outside the project. It retains per-call records
and an exact terminal snapshot; private inputs and traces are never published.

## Limits

The second mixed NMI and later bounded returns are host-verified. The sound's
later high-bit stream command and deactivation remain unimplemented. This does
not establish audible Paula output, real-time performance, execution on a stock
PAL A1200, or playability. The delivered Z/X ADF, original inputs, and predecessor checkpoints remain
unchanged.
