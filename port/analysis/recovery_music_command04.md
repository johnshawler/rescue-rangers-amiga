# First music command04 checkpoint

The continuous original-ROM run reaches `$83A0` with command `$04` fetched
from `$A2C1`; its operand is `$00` at `$A2C2`. This new static 68020 helper
completes that command and stops at `$839D`, immediately before the next
stream-byte fetch. It does not complete the tick, RTI, or audio output.

## Contract and semantics

- A0: writable original-layout 2,048-byte RAM.
- A1: writable eight-byte context: big-endian PC, A/X/Y/P/SP/reserved.
- A2: writable 14-byte resource journal: count word and three records,
  each original address word, value byte, kind byte zero.
- A3: caller-owned read-only 16KiB bank-3 resource view (`$8000–$BFFF`).

Buffers must be valid, disjoint and exclusively owned. Preconditions: PC
`$83A0`, A `$04`, X `$2B`, canonical P (B clear/U set), channel pointer
`$0753/$0757` in `$8000–$BFFF`, and resource dispatch bytes at `$848B/$848C`
selecting `$8551`. Any Y, SP, other RAM and all canonical status combinations
are supported, including D=1 because this slice performs no ADC/SBC.

All guards precede writes. Invalid context/pointer rejects without resource
reads; malformed dispatch data rejects after one or two bounded read-only
preflight reads. Rejection changes no RAM, context or journal. Successful
execution has two preflight reads plus three original semantic resource reads:
the stream operand and the two inline dispatch-table bytes. Only the three
original reads are journaled. The test separately checks the entire native
resource-read address sequence, byte-only access and immutable resource view.

The translation preserves original ordered RAM stores, seven original stack
writes, JSR/RTS and inline table push/pop effects, stream pointer increment
(including low-byte wrap), and the command's channel flag update:
`$075B = ($075B & $97) | operand`. This is statically translated game logic,
not an original CPU opcode fetch/decode loop. No cartridge asset extract is
embedded. Dispatch target guards are code-path constants.

Success returns D0=1, PC `$839D`, A=updated flags, X `$2B`, Y `$0A`, and entry
SP unchanged. C=0; N/Z describe the flag result; V/D/I are retained. C1/C2 hold
`$8551`, C3 the operand, C4 command04. The reserved context byte and native
D1–D7/A0–A6 are preserved, native stack balanced; CCR is scratch. D0=-1 means
unsupported. No APU/PPU/mapper writes occur, so no hardware-write journal is
needed. Existing task/NMI frames and the pending `$C2A8` continuation remain.

## Executed evidence

Private Europe ROM SHA256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
`port/tests/recovery_test_music_command04.py` assembles the new helper and
prior helpers with VASM/68020, executes them in machine68k M68EC020, and
compares against py65 executing the actual original ROM.

- 4,096 standalone comparisons vary RAM, flags, all SP values, all canonical
  statuses, Y/reserved and pointers throughout the bank window. Each original
  slice executes 40 instructions, or 41 on pointer low-byte wrap. Complete RAM,
  context, ordered RAM/resource effects, buffer guards, exact resource reads,
  native registers and stack are checked.
- 256 continuous reset-to-command04 comparisons make sixteen calls to fifteen
  distinct native helpers, with both NMIs entered using actual `ref.nmi()`.
  No captured-state or oracle RAM/P patches are used. The named
  `architectural_status_view` only normalizes virtual B/U for comparison.
  Earlier continuous ADC-bearing helper14 remains in its documented D=0 scope.
  The real command04 operand is zero; the nested task frame stays byte-identical.
- 66,939 unsupported cases reject inertly: every wrong PC, unsupported A/X/P,
  invalid pointer high bytes, and all 510 malformed dispatch-byte variants.
  Another 4,096 completed-boundary calls reject without mutation or reads.

Only the new helper, new host differential test and this report were authored.
No previous helpers/tests, shared target integration, README, public/aggregate
suite, commit, publication or ADF changed. These are host semantic checks,
not native Amiga runtime evidence. Delivered Z/X ADF is unchanged. Later
playable/audio source remains lost; this is new recovery. No full boot,
gameplay, speed, complete tick/RTI or audible Paula claim is made.
