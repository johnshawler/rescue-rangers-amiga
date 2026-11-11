# Recovery command07 initialization

New static 68020 semantic translation, not recovered playable/audio source.
The new helper starts at bank-3 `$8003`, A=`$07`, and returns at `$C0F3`.
The existing `recovery_nmi_audio_entry` consumes the actual queue request and
publishes bank 3 immediately before this helper. No subsequent audio tick,
sequencer interpretation, RTI, or audible Paula output is implemented here.

## Contract

`recovery_music07_command` takes:

- A0: writable 2048-byte original-layout RAM.
- A1: writable eight-byte context, big-endian PC then A/X/Y/P/SP/reserved.
- A2: writable 30-byte journal: count word then seven four-byte records
  `{address.w,data.b,kind.b}` with kind 1 for an APU write.
- A3: caller-owned read-only 16384-byte bank-3 resource view corresponding to
  original cartridge addresses `$8000–$BFFF`. The view must match the private
  Europe ROM identified below. No embedded cartridge extracts are supplied.

Buffers must be valid, disjoint, and exclusively owned during the call. The
resource view is data only; the helper never decodes or executes its opcodes.
It reads count `$8A00`, command07 pointer high/low `$8A11/$8A12`, the zero header,
and eight channel-pointer bytes. Preconditions validate count greater than 7,
pointer `$8000–$BFF7`, and a zero header before any output/RAM/context mutation.
These bounds keep all nine pointer-relative reads inside the supplied view.
Original pointer low/high bytes are stored in `$C1/$C2`; channel high/low bytes
are transferred in original order, without native pointer substitution.

Require PC `$8003`, A=7, canonical P (B clear/U set), `$CF=0`, and original RTS
frame `$C0F2` at wrapped SP+1/SP+2. All other RAM/register/status bits and every
SP are supported. This helper supports D set: this path has no decimal
arithmetic. The preceding resumed-task helper's D=0 scope restriction remains
necessary for the generic py65 SBC oracle, not an asserted NES requirement.

D0=1 success, -1 unsupported/inert. D1–D7/A0–A6 preserved; native stack balanced;
CCR scratch; context reserved byte preserved. Unsupported CF/headers/commands
are intentionally rejected, not silently cleared or reinterpreted.

## Original effects

The helper implements `$80E1` command nesting, `$80F0` command selection,
`$8152` music initialization, and `$81C0` channel reset. It retains all original
stack stores, clears `$0728–$077B` in descending order, transfers four channel
pointers, sets `$077C–$077F` sentinels only for nonempty channels, and publishes
seven original reset APU writes in order. It preserves unrelated queue/pending
state. Final A=$0F, X=$FF, Y=$0C, SP advances by two, PC=$C0F3; final N/Z reflect
the restored nesting counter, C=0, other architectural status bits retained.
These are explicit logical journals, not Amiga MMIO or an audible audio driver.

## Executed differential proof

Private input: `input/rescue-rangers-europe.nes`, SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Run `port/tests/recovery_test_music07_command.py` with VASM pointing to the
68020 assembler and py65/machine68k available on PYTHONPATH.

The assembled M68EC020 code passed:

- 2,048 standalone original-ROM comparisons: randomized RAM/registers,
  every SP/counter value, all canonical status patterns, full original stack
  stores and ordered merged RAM/APU effects.
- 256 continuous reset-to-command07 comparisons using fourteen helper calls
  and thirteen distinct helpers (request intake is called twice). Both NMIs
  use actual `ref.nmi()`. No captured state, oracle RAM edits, or raw P edits
  occur between helpers. The named architectural status view only clears
  py65's virtual B and sets U for comparison.
- The second queued07 request is actually consumed by existing intake; the
  nested task continuation remains intact. Command07 has 122 RAM writes and
  seven APU writes; composed execution stops before the next tick at `$C0F3`.
- 67,014 unsupported cases and 2,048 completed-boundary calls rejected inertly:
  all wrong PCs/commands/noncanonical statuses/nonzero CF/incorrect frame
  bytes, low resource counts, out-of-bounds pointers and every nonzero header.
- Full RAM/context/journal comparison, native register/stack checks, output
  guards, bounded execution, exact ordered byte-only resource reads, and
  unchanged resource bytes. No original assets or trace dumps are embedded.

Only the new helper, test, and this report were authored for this step. No
shared builder, verifier, probe, previous helper, public test, README, commit,
publication, or ADF change was made. Delivered Z/X ADF remains immutable.
This is host semantic evidence, not target/physical-Amiga validation. Public
source recovery is still earlier title/menu only; later playable/audio source
remains lost. No full-boot, gameplay, speed, or audible-output claim is made.
