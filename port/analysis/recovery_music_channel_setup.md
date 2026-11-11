# Stream command06 and command07 channel setup

Actual Europe-ROM inspection identifies stream command06 at $A2C6 with operand
$96, followed by stream command07 at $A2C8 with operand $0F. Two new static
68020 helpers translate these channel-setup commands. The existing
`recovery_music_stream_fetch` is composed unchanged at its genuine $839D entry
before each command. No duplicate fetch helper or false entry is introduced.

`recovery_music_stream_command07_volume` is specifically the stream command07
volume/control handler. It is NOT the existing `recovery_music07_command`,
which initializes the queued music07 request. They have different entry
contracts and must not be substituted for one another.

## Contract and ordered effects

A0 points to original-layout 2,048-byte RAM; A1 to the eight-byte canonical
context (big-endian PC, A/X/Y/P/SP/reserved); A2 to a 14-byte resource journal;
A3 to the caller-owned immutable 16KiB bank3 view for $8000–$BFFF. All buffers
must be valid, disjoint and exclusively owned. The resource journal is a count
word followed by three records (address word, value byte, kind byte zero).
D0 returns 1 on success, -1 for unsupported input. D1–D7/A0–A6 and reserved
are preserved; native stack is balanced; native CCR is scratch.

Both helpers require PC=$83A0, X=$2B, canonical P (B clear and U set), and
A equal to their stream command. All entry SP, Y and canonical status values
are supported, including D=1: neither new helper executes ADC/SBC. The channel
pointer $0753/$0757 must be $8000–$BFFF. Pointer $BFFF is supported and advances
to $C000; a subsequent stream fetch rejects that out-of-window pointer.

Before mutations, command06 checks dispatch bytes $848F/$8490 select $84DB;
stream command07 checks $8491/$8492 select $8652. These byte-only, bounded
preflight reads are not emulated resource events. Invalid context or pointer
rejects without any resource reads. Malformed low/high dispatch bytes reject
after one/two reads. Every rejection preserves RAM, context and journal.

Success journals the operand read, dispatch low read, dispatch high read in
original order. Five native byte-only resource reads occur, including the
two preflight reads. Each command writes seven original stack bytes, retaining
original wrap and push/pop order. The operand becomes C3, the command becomes
C4, and C1/C2 end as the dispatch target. There are no APU, PPU or mapper
writes in these slices. Tests reject unexpected hardware effects.

- `recovery_music_command06`: static $84DB handler stores the operand into
  $0767 ($073C+X). A ends as the operand; Y=$0E; C=0; N/Z reflect the operand.
- `recovery_music_stream_command07_volume`: static $8652 handler follows the
  supported X=$2B branch, computes ($0737 AND $C0) OR operand OR $30, and
  stores it to $0737 ($070C+X). A ends as that result; Y=$10; C=1 from CPX.
  N/Z reflect the result. Neither helper changes V/D/I.

Both return PC=$839D with entry SP unchanged. Source contains no cartridge
asset extracts or runtime CPU-opcode fetch/decode/interpreter. Original game
stream interpretation is data processing.

## Executed differential proof

Private ROM SHA256:
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.

`port/tests/recovery_test_music_channel_setup.py` assembles all helpers with
VASM -m68020 and executes them under machine68k M68EC020 against independent
actual original-ROM py65 execution:

- 8,192 standalone comparisons, 4,096 per helper, vary full RAM, all SP
  values, all canonical statuses, Y/reserved and resource pointers including
  low-byte wrap and the final resource byte. Exact complete RAM/context,
  ordered RAM/resource effects, full native read sequence, immutable resource
  view, buffer guards, native registers and stack are checked. Original
  command06 takes 38/39 instructions; stream command07 takes 43/44.
- 256 continuous reset runs compose 22 calls to 19 distinct helpers, through
  two actual `ref.nmi()` calls and all prior 18 calls. No captured-state or
  raw RAM/P patches are used. Only comparison's named architectural status
  view normalizes virtual B/U. Prior ADC-bearing helpers retain D=0 oracle
  scope because generic py65 decimal behavior differs from NES arithmetic.
- 133,878 unsupported-input checks cover every wrong PC, unsupported A/X/P,
  out-of-window pointer high bytes and every 1,020 malformed dispatch-byte
  alternative; plus 8,192 completed-boundary calls reject inertly.

All three PASS lines were observed. The endpoint is PC=$839D, SP=$AB, channel
pointer=$A2CA, $0767=$96, $0737=$3F, and C8/C9/CA remain $00/$02/$49.
The pending $C2A8 task continuation and nested frame remain intact. The next
stream command08 at $A2CA is UNCONSUMED. Instrument/envelope setup and later
note/event processing remain to translate before completing this music tick.

The two new helper sources have independent original-ROM and ROM-free contract tests. The [private target checkpoint](recovery_music_channel_setup_target.md) now verifies their continuous composition, including command05, on an emulated stock PAL A1200. Aggregate/public validation includes these helpers. Existing helper implementations and delivered Z/X ADF remain unchanged. This is newly authored recovery; later playable/audio source remains lost. No whole tick/RTI, audible Paula, full boot, gameplay or speed claim is made.
