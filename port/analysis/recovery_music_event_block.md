# First-channel instrument, control and rest event

Four new static 68020 helpers complete a coherent first-channel music event.
Actual Europe-ROM inspection identifies the remaining setup as instrument08,
control18 and control09, followed by a rest event80. The chosen boundary is
**after the original channel RTS**, at bank3 PC=$8085, before the outer
channel loop restores X. The existing $839D stream fetch is reused unchanged
before each handler. No CPU-opcode interpreter, captured-state injection,
or patch to an earlier helper is used.

## Contract

A0 is original-layout 2,048-byte RAM; A1 is an eight-byte canonical context
(big-endian PC, A/X/Y/P/SP/reserved); A2 is the resource journal; A3 is a
caller-owned immutable 16KiB bank3 window for $8000–$BFFF. Buffers must be
valid, disjoint and exclusively owned. D0 returns 1 or -1. D1–D7/A0–A6 and
context reserved are preserved; native stack is balanced; native CCR scratch.
Journal layout is count word, followed by records (address word, value byte,
kind byte zero). Unused journal records are zero on success and untouched
on rejection. All resource accesses are byte-only. No new hardware writes
occur, so these helpers have no APU/PPU/mapper journal.

All require PC=$83A0, X=$2B and canonical status (B clear, U set). All entry
SP/Y and supported canonical status combinations are accepted. Instrument08
and rest reject D=1 before resource reads or mutations: their ADC operations
are binary, and generic py65 decimal arithmetic differs from NES arithmetic.
Control18 and control09 support D=1, since neither executes ADC/SBC. Raw
original P is never patched; only the named comparison view normalizes B/U.

### Instrument08

`recovery_music_event_instrument08.s` requires A=$08 and a channel pointer
at $0753/$0757 within $8000–$BFFF. It checks the two bounded dispatch bytes
at $8493/$8494 select the statically translated $8667 target before mutation.
It translates the complete command dispatch and handler, including INC C3,
comparison against $072B, the unchanged-instrument fast return, channel
activation bits at $072F, all three original C3 rotate writes, and binary
pointer arithmetic using caller resource bytes at $8A02 followed by $8A01.

A2 is 22 bytes. Three original resource records occur on the fast path, or
five on changed instrument, in original operand/dispatch/base-byte order.
Two extra dispatch preflight reads are nonsemantic and unjournaled. Final
PC=$839D and SP is unchanged. The computed instrument pointer is stored at
C5/C6 but is not dereferenced in this slice; a future dereferencing helper
must validate its own window. Pointer $BFFF is supported and increments to
$C000; the next existing fetch rejects that out-of-window pointer.

### Control18 and control09

`recovery_music_event_command18.s` requires A=$18 and dispatch $84B3/$84B4
selecting $86A5. It writes ($0737 AND $0F) OR operand OR $30 to $0737.
`recovery_music_event_command09.s` requires A=$09 and dispatch $8495/$8496
selecting $84E1. It writes ($075B AND $F8) OR operand to $075B.

Both require the same $8000–$BFFF stream-pointer bounds, use 14-byte journals,
and record operand/dispatch-low/dispatch-high in original order, plus two
unjournaled preflight reads. Both return PC=$839D and unchanged SP, with
A equal to the result, Y=$32/$14 respectively, C=0, N/Z from the result and
V/D/I retained. All seven original stack stores and their order are retained.

### Rest event and natural channel return

`recovery_music_event_rest.s` supports all seven rest encodings
$20,$40,$60,$80,$A0,$C0,$E0. It uses a 10-byte journal. No stream pointer is
read because the event byte has already been fetched. It handles both
bounded duration tables, zero-valued special-table fallback, dotted-duration
C3 and channel-flag stores, duration accumulation at $0763, envelope-release
bits at $072F, and $076B=$FF. One or two original duration-table reads are
journaled. The supported table indexes are 0–6 and cannot escape the window.

Every original stack write is retained, including initial PHA and the nested
release JSR. The final original RTS reads the caller's stack, wraps SP at
8 bits and PC at 16 bits, and returns that PC in context rather than executing
it natively. A=$FF, Y=accumulated duration, N=1, Z=0, C/V from duration ADC,
I retained, and SP advances by two. There is no assumed or embedded caller
return address.

## Executed proof

Private Europe-ROM SHA256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.

Both tests assemble with VASM -m68020 and execute under machine68k M68EC020.
They globally whitelist every traced native read and write, including code,
resources, context, RAM, journals and native stack. Deliberate distant
unmapped reads/writes are checked against the whitelist. They verify complete
RAM/context, ordered RAM/resource effects, exact native resource reads,
immutable resources, buffer guards, preserved native registers and stack.

`port/tests/recovery_test_music_event_block.py` uses independent execution of
the actual original ROM:

- 16,384 standalone comparisons, 4,096 per new helper, including all SPs,
  canonical status combinations, random complete RAM, stream-pointer wrap,
  unchanged-instrument branches and all seven rest encodings.
- 256 semantic reset compositions, each making **30 calls to 23 distinct
  helpers**, through two actual ref.nmi() events. The host harness reloads
  each exact prior output RAM/context for the next call, without changing any
  bytes. No captured states or raw RAM/P patches. This includes all previous 22 calls unchanged and the four
  new fetch/handler pairs. The pending task continuation and nested second-NMI
  frame remain intact.
- 267,112 unsupported-input checks, covering every wrong PC, invalid A/X/P,
  all out-of-window pointer high bytes, and every malformed dispatch-byte
  alternative. Another 16,384 completed-boundary calls reject inertly.

The continuous endpoint is PC=$8085, A=$FF, X=$2B, Y=$18, P=$A4, SP=$AD,
stream pointer=$A2D1. Channel $072B=$23, $072F=$0B, $0737=$FF, $075B=$01,
$0763=$18, $076B=$FF, and instrument pointer C5/C6=$8B67. C8/C9/CA remains
$00/$02/$49. The final eight helper calls add 16 resource records and no
hardware events. A separate [private target checkpoint](recovery_music_first_channel_target.md)
now verifies the same chain with continuously live native RAM/context on the
emulated stock PAL A1200, including intermediate snapshots.

`port/tests/recovery_test_music_event_contract.py` is completely ROM-free:

- 32,768 independent declarative comparisons using synthetic resource windows,
  including all instrument operands, carry/overflow, zero-special-duration
  fallback, dotted duration, all channel flags, and stack/return-PC wrap.
- 8,192 inert rejection comparisons. It neither imports a 6502 CPU oracle nor
  reads a cartridge, asset extract, captured state or raw trace.

Run either test with VASM pointing to `vasmm68k_mot` and PYTHONPATH including
the installed `machine68k`/`py65` dependencies (py65 only for actual-ROM test).

## Remaining dependency and provenance

The next original instruction is the outer channel loop's PLA at $8085,
followed by restoring X, shifting channel flags, and processing the remaining
channels. Envelope progression, pitched-note paths and later audio output
remain untranslated; the first event happens to be a rest. This is not a
complete music tick or RTI. Instrument setup computes a pointer but does not
render instrument sound or claim audible Paula output.

The four new helpers, independent tests and private target integration are included in the public/full validation scripts. Existing helper implementations remain unchanged. Generated cartridge-bearing target artifacts stay private. Delivered Z/X ADF remains immutable. This is newly authored recovery; later playable/audio source remains lost. No complete boot, gameplay, physical-hardware or speed claim is made.
