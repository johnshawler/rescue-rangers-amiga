# Four-channel music data parser

Three newly authored static 68020 helpers support genuine music-channel indexes
$28 through $2B. Existing single-channel helpers, previous probes, shared
builders, aggregate scripts and delivered disks are unchanged. The new files
are standalone and have not been added to public/full validation scripts.

## Native interface

A0 is a valid 2,048-byte original-layout RAM buffer. A1 is the eight-byte
canonical context (big-endian PC, A/X/Y/P/SP/reserved). A2 is a resource
journal; A3 is a caller-owned immutable 16KiB bank3 view for $8000–$BFFF.
Buffers must be valid, disjoint and exclusively owned. D0 returns 1 on success
or -1 on inert rejection. D1–D7/A0–A6 and the context reserved byte are
preserved; native stack is balanced and CCR is scratch. RAM effects remain
byte writes in original order. Journal records are address word, value byte,
zero kind byte, preceded by a count word. Unused records are zero on success,
and the complete journal is unchanged on rejection. Resource accesses are
byte-only. There are no APU/PPU/mapper effects in these helpers.

- `recovery_music_indexed_fetch.s`: PC=$839D to $83A0, six-byte journal.
  Pointer bytes are $0728+X and $072C+X. Supports every A/Y/SP and canonical
  P, including D=1. Valid pointer range is $8000–$BFFF; an increment from
  $BFFF to $C000 is retained, and a subsequent fetch rejects the new pointer.
- `recovery_music_indexed_commands.s`: PC=$83A0 to $839D, 22-byte journal.
  Shared operand fetch, dispatch-table validation and original dispatch stack
  effects feed static handlers for commands $04/$05/$06/$07/$08/$09/$18.
  Unsupported command bytes reject before any resource access or mutation.
  Every supported dispatch target is validated before mutation, using two
  nonsemantic unjournaled preflight reads. Semantic reads remain in original
  order. Commands use three records, command05 uses four, and instrument08
  uses three or five. Command05 needs two consecutive resource bytes and
  therefore rejects a starting pointer of $BFFF. Instrument08 rejects D=1;
  the remaining setup commands accept D=1. Instrument base-pointer arithmetic
  computes C5/C6 without dereferencing the computed pointer.
- `recovery_music_indexed_rest.s`: PC=$83A0 through the original channel RTS,
  ten-byte journal. Supports all seven rest encodings $20/$40/$60/$80/$A0/
  $C0/$E0, every original SP and return address, and canonical P with D=0.
  Handles special-duration fallback, dotted duration, channel release flags,
  duration accumulation, original stack writes and wrapped RTS. It does not
  fetch a stream operand. It records one or two duration-table reads.

All three reject X outside $28–$2B and noncanonical P (B set or U clear).
Invalid PC, unsupported command/rest, unsupported D, pointer bounds and
malformed dispatch fail without changing RAM, context or journal.

## Genuine channel behavior

The original control07 tests **the full X against $01**, not X masked to its
low two bits. Every genuine music index $28–$2B therefore takes the ordinary
volume branch, including X=$29. Its CMP carry is one. The separate $01 sound
channel branch is deliberately outside this interface. Instrument08, control
04/06/09/18 and rest use the genuine indexed channel fields; command05 updates
global tempo state. Original dispatch and stack effects are shared rather
than implemented as seven separate specialized command wrappers. There is
no runtime CPU opcode interpreter, original-code decoder or generated
cartridge instruction table.

Assembled sizes with VASM -m68020 are 230 bytes for fetch, 1,308 bytes for
shared commands and 368 bytes for rest (1,906 bytes total).

Host music-chain comparisons carry each exact prior native RAM/context output into the next call by reloading those bytes. This is semantic composition without state patches, not a claim of continuously resident target buffers. Separate live-buffer stage proofs and actual target execution are identified explicitly.

## Verification

The new standalone tests assemble and execute the native code with machine68k
M68EC020. They verify complete RAM/context, ordered RAM/resource effects,
exact resource accesses (including dispatch preflight), immutable resources,
buffer guards, native register preservation and stack balance. Global native
read/write whitelists reject deliberately distant accesses.

- `recovery_test_music_indexed_contract.py`: 36,864 ROM-free declarative
  supported cases and 36,864 guard/input comparisons. Synthetic resources
  exercise all four indexes, every SP and canonical flag combination,
  instrument operands, same-instrument branches, arithmetic carry/overflow,
  stream and return-address wrap, duration fallback and channel flags.
- `recovery_test_music_indexed_rom.py`: 36,864 independent actual-ROM
  comparisons across all four indexes and nine semantic entry types. Uses
  original ROM execution rather than calling the declarative model as its
  CPU oracle. Both original and declarative results independently compare to
  native execution. Raw reference P is not modified. D is rejected for the
  translated binary ADC paths because generic py65 decimal differs from NES.
- `recovery_test_music_indexed_rejection.py`: 235,265 inert rejection
  comparisons, including exhaustive wrong-PC checks for
  all three native entries; every invalid X/P, out-of-window pointer high byte,
  unsupported command/rest, malformed dispatch byte and command05 $BFFF
  boundary across all four indexes. All rejected calls are fully inert.
- `recovery_test_music_indexed_chain.py`: 256 continuous reset compositions,
  **41 calls to 27 distinct helpers**, with two real reference NMI events.
  The prior 31 calls remain unchanged. New calls process the next channel's
  setup 04,06,07,08 followed by rest80, ending at its natural channel return:
  PC=$8085, A=$FF, X=$2A, Y=$18, P=$A4, SP=$AD, stream pointer=$A39A.
  Full RAM/context and ordered effects compare after every call, and the
  nested pending continuation is preserved. No state or raw-status patches
  are used to enter or advance this chain.

- `recovery_test_music_indexed_continuation.py`: 256 further continuous
  reset compositions using unchanged parser and outer iteration. These reach
  **62 calls to 27 distinct helpers**, through channel $29 and into $28.
  The first unsupported event is pitched note $83, fetched from the stream
  with resulting pointer $A57C. Boundary is PC=$83A0, A=$83, X=$28, Y=$00,
  P=$25, SP=$AB. Both command and rest entries reject it inertly. The original
  reference stops before executing the event; the pending nested continuation
  remains intact. No callback, envelope or unknown command was skipped.

Private Europe ROM SHA256 is
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Run the five tests with VASM set to `vasmm68k_mot` and PYTHONPATH including
machine68k and py65 (py65 and the cartridge are not needed for the contract
or rejection test). Test inputs are read locally; no cartridge, firmware,
asset extract or raw execution trace is emitted into source files.

## Remaining work and limits

The 41-call proof retains the useful second-channel-return boundary. The
additional 62-call proof processes the next channel and stops immediately
before event83 in the last channel. The next concrete dependency is the
pitched-event path beginning at $83A0, including its duration calculation and
non-rest branch at $83E9. No original effects of that event have been applied
by the new parser. Nonzero-duration envelopes, CF callbacks, other music
commands and later output also remain unsupported. This is not a complete
initial tick, RTI, audible Paula renderer or playable game. No stock-target
probe, physical-hardware test or performance claim is made for these new
helpers. Original inputs and delivered Z/X ADF remain unchanged.

## Subsequent integrated checkpoint

The helper-local limits above describe this component when introduced. The
[bounded resident runtime target](recovery_runtime_target.md) now verifies the
reset-generated idle/NMI/initial-music/RTI/task-resume path on an emulated
stock PAL A1200. Stage frame-yield compositions remain separate synthetic-entry
proofs. Public and private aggregate scripts include these helper suites.
There is still no complete native gameplay loop, audible output or speed claim.
