# Indexed pitched event and complete initial music tick

Two new static 68020 helpers translate the pitched event previously blocking
continuous reset at event $83, channel $28. They support genuine indexed music
channels $28–$2B, with no runtime opcode decoder, CPU interpreter, captured
state injection, or changes to earlier native helpers. The event completes
through its original channel RTS. The unchanged outer-channel helper then
completes the initial music tick.

## Interface and safety

A0 points to 2,048 bytes of original-layout RAM, A1 to the eight-byte canonical
context (big-endian PC, A/X/Y/P/SP/reserved), A2 to a journal, and A3 to a
caller-owned immutable 16KiB bank3 view for $8000–$BFFF. Buffers must be valid,
disjoint and exclusively owned. D0 returns 1 on success or -1 on inert
rejection. D1–D7/A0–A6 and context reserved are preserved; native stack is
balanced; native CCR is scratch. Original RAM effects remain ordered byte
writes, including overwritten original-stack bytes. Resource reads are bytes.
Neither helper writes APU, PPU, controller or mapper hardware.

Journal layout is count word, then address-word/value-byte/zero-kind-byte
records. Unused records are zero on success. Rejection preserves the entire
RAM, context and journal, including unused records. Both entries reject
noncanonical P (B set or U clear), D=1, wrong PC and indexes outside $28–$2B.
D is guarded because generic py65 decimal arithmetic differs from the NES;
reference raw P is never patched to force binary arithmetic.

### Duration and gate

`recovery_music_pitched_gate.s` accepts PC=$83A0 and pitched event bytes
$21–$FF excluding the seven rest encodings. Its natural boundary is PC=$83FD,
immediately before note PLA. The 10-byte journal contains one or two duration
table reads. Supported behavior includes both duration tables, zero-special
fallback, dotted-duration channel/C3 stores, duration accumulation, and the
entire eight-round multiply at $8006. Every original multiply RAM write and
JSR/PHA stack effect is retained, including SP wrap. The high product or one
is stored as the gate duration. The note operand remains on the original
stack, and all arithmetic flags surviving to the boundary are preserved.
The duration indexes are intrinsically bounded; all resource byte values are
valid data for this helper.

### Note, onset and instrument

`recovery_music_pitched_note.s` accepts PC=$83FD with a stacked note 1–31 and
uses an 18-byte journal. It handles:

- Original note pop, onset, channel $29's special activation increments, and
  the CF-controlled per-channel reset.
- Channel $28's direct inverted low-nibble pitch, and channels $29–$2B's
  octave, global and channel transposition, modulo-byte arithmetic and clamp.
- Existing-note comparisons, glide direction and pitch retention, fast
  retrigger branches, both pitch-table reads and the instrument byte at
  ($C5/$C6)+4.
- Envelope restart/activation flags, channel flags and the actual original
  RTS, reading and wrapping the caller's real stacked return address.

A read-only preflight determines whether the instrument dereference will
occur. For melodic channels it performs one nonsemantic, unjournaled octave
read when needed to determine that branch. Semantic reads occur again in
original order. Only a reached instrument byte requires its 16-bit wrapped
effective address to lie in $8000–$BFFF. Fast retrigger branches therefore
accept irrelevant out-of-window instrument pointers; other branches reject
before any mutation. All 65,536 instrument pointer values are exercised by
the declarative guard tests. Pitch indexes remain inside the fixed bank3
window even when the previous note byte wraps during ASL. The journal holds
zero to four semantic resource reads.

Host music-chain comparisons carry each exact prior native RAM/context output into the next call by reloading those bytes. This is semantic composition without state patches, not a claim of continuously resident target buffers. Separate live-buffer stage proofs and actual target execution are identified explicitly.

## Verification

All tests assemble VASM `-m68020` code and execute it with machine68k
M68EC020. They compare all 2KiB RAM, all context bytes, ordered original RAM
and resource effects, exact native resource accesses including preflight,
immutable resources, buffer guards, preserved native registers and stack
balance. Global read/write whitelists explicitly reject deliberately distant
native accesses.

- `recovery_test_music_pitched_gate_contract.py`: 16,384 ROM-free declarative
  cases plus 66,304 guard/input comparisons, including exhaustive wrong-PC
  inputs and all status/index/event byte values.
- `recovery_test_music_pitched_note_contract.py`: 16,384 ROM-free declarative
  cases plus 131,840 guard/resource comparisons, including every wrong PC,
  index/status/stacked-note byte and instrument pointer.
- `recovery_test_music_pitched_gate_rom.py` and
  `recovery_test_music_pitched_note_rom.py`: 16,384 independent actual-ROM
  cases each, separately comparing original execution and declarative results
  with native execution. Both cover all four genuine channel indexes.
- `recovery_test_music_pitched_event_composition.py`: 16,384 complete
  all-channel pitched events. Each exact gate output feeds the note helper;
  the original reference continues without reloading RAM or CPU status.
- `recovery_test_music_pitched_event_chain.py`: 256 continuous reset
  compositions through two real reference NMIs, now **65 calls to 29 distinct
  helpers**. All prior 62 outputs remain unchanged. The final calls complete
  the pitched event and run the existing outer-channel iteration to tick RTS.

The continuous gate boundary is PC=$83FD, A=$04, X=$28, Y=$00, P=$24, SP=$AA.
The event returns at PC=$8085, A=$00, X=$28, Y=$00, P=$26, SP=$AD.
The complete initial tick returns at PC=$C0F9, A=$00, X=$FF, Y=$00, P=$26,
SP=$B1. Stream pointer remains $A57C; the pending nested continuation is
preserved. This is a complete initial tick, not just a no-work isolated tick.

The helpers assemble to 504 and 862 bytes (1,366 total). Binary SHA256:

- Gate: `5a8c3bff9fcb04bb312f9705a093d1a491973e4ce2e17326ca57555be532975a`
- Note: `41cd31d71b4587b4e924cfeed5dca412019c677aae15ac7a13c9e239f000b66e`

Private Europe ROM SHA256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Run the six tests with VASM pointing to `vasmm68k_mot` and PYTHONPATH including
machine68k and py65. The two contract tests do not need py65 or the cartridge.
No cartridge, firmware, asset extract or raw execution trace is emitted into
source files.

## Next dependency and limits

The next original instruction is $C0F9's LDA $F1 (saved bank 6), followed by
five serial mapper writes beginning at $C0FB, register/status restoration and
the second NMI's RTI. The chain verifies the original instruction target and
that the earlier startup-only silent-tick/RTI helper rejects this state
inertly. That helper requires a different entry and first-NMI frame and cannot
be reused by bypassing its guards. The new proof stops before these mapper
and restoration effects.

This work does not translate subsequent nonzero-duration envelope progression,
CF callbacks, remaining music commands or audible Paula rendering. It makes
no full boot/gameplay, physical-hardware or game-speed claim. No stock-target
probe or aggregate script is changed. Only the newly named helpers, tests
and this note are added; earlier sources, delivered Z/X ADF and original
inputs remain untouched. No publication is performed.

Additional review coverage persists 64 fast-retrigger cases in each of the public and original-ROM note suites. All four channels and stack boundaries accept irrelevant out-of-window instrument pointers when the original branch makes no instrument read. Both strengthened suites pass.

## Subsequent integrated checkpoint

The helper-local limits above describe this component when introduced. The
[bounded resident runtime target](recovery_runtime_target.md) now verifies the
reset-generated idle/NMI/initial-music/RTI/task-resume path on an emulated
stock PAL A1200. Stage frame-yield compositions remain separate synthetic-entry
proofs. Public and private aggregate scripts include these helper suites.
There is still no complete native gameplay loop, audible output or speed claim.
