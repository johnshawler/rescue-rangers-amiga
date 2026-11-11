# First music-active channel fetch checkpoint

New static 68020 semantic translation in `recovery_music_tick_fetch.s` starts
at fixed-bank `$C0F3` with bank3 resources selected and stops at `$83A0`, immediately after the first channel's
stream-byte fetch returns. It does not interpret the fetched command, finish
the music tick, return through RTI, or produce audible Paula output. Actual-ROM
inspection showed the whole first tick/RTI spans 1,504 original instructions
and multiple sequencer/event routines, so this is an explicit subdivision.

## Contract and implemented operations

- A0: writable original-layout 2,048-byte RAM.
- A1: writable eight-byte context: big-endian PC, A/X/Y/P/SP/reserved.
- A2: writable six-byte resource-read journal: count word followed by original
  address word, byte value, kind byte zero. Success has exactly one record.
- A3: caller-owned read-only 16KiB bank-3 view, corresponding to `$8000–$BFFF`
  of the private Europe ROM. No cartridge assets are embedded in source.

Buffers must be valid, disjoint and exclusively owned. All preconditions are
checked before writes or resource reads: PC `$C0F3`; canonical P (B clear,
U set), D clear; queue index `$DB` at most seven and selected slot `$88`;
`$C0` in {0,4,8}; `$D0/$D1/$CF` zero; first channel duration `$0763` zero;
first channel pointer `$0753/$0757` in `$8000–$BFFF`. Other RAM, all entry
A/X/Y values and every SP are supported. Unsupported states reject inertly.
D=0 is the generic py65 decimal-ADC oracle scope, not a NES game requirement.

The helper explicitly translates the empty queue check, JSR into bank-3 update,
phase advancement, tempo accumulator and carry propagation, channel-selection
stack pushes, pointer setup and one byte fetch through original `$856E` logic.
All original RAM stores retain their order, including eight stack writes and
low/high pointer increment on wrap. The returned context has PC `$83A0`,
A=fetched byte, X=$2B, Y=0, SP=entry SP minus six modulo 256. N/Z describe the
pointer increment, V describes the second tempo ADC, C=0, and I is retained.
The outstanding original JSR frame is retained, ready for later continuation.
The resource journal records the actual original address, not a native pointer.
No native code fetches/decodes original CPU opcodes or dispatches opcodes.

D0=1 on success, -1 unsupported. D1–D7/A0–A6 and the context reserved byte are
preserved; native stack balanced; CCR scratch. No mapper/APU/PPU writes occur
in this bounded slice. Existing NMI frames, queued work and task continuation
remain intact, including the pending `$C2A8` continuation.

## Executed differential evidence

Private ROM SHA256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Test: `port/tests/recovery_test_music_tick_fetch.py`, using VASM's 68020 target,
machine68k M68EC020 and py65 executing the actual original ROM.

- 4,096 varied standalone comparisons: randomized RAM, tempo operands,
  registers and reserved bytes; all SP values and canonical D=0 statuses;
  three supported phase values; pointers across the full resource window,
  including low-byte wrap. Exact complete RAM/context and ordered RAM/resource
  effects, single byte-only resource read, unchanged resource bytes, buffer
  guards, preserved native registers and balanced native stack are checked.
- 256 continuous reset-to-fetch comparisons use fifteen calls to fourteen
  distinct helpers. Both NMIs are real `ref.nmi()` entries. Reset, initial
  silent tick/RTI, scheduler resume, task setup, palette NMI, command07 intake,
  command07 initialization and first music-byte fetch compose without captured
  state patches. Raw oracle RAM and P are not edited after initial setup.
  The named architectural status view only removes virtual B and sets U.
- 67,727 unsupported entries and 4,096 completed-boundary calls reject without
  changing RAM/context/journal or reading the resource view. Rejections cover
  all wrong PCs, unsupported statuses/phases, nonempty queue, invalid queue
  indexes, pending alternate audio paths, nonzero duration and invalid pointers.

These are host semantic checks, not native Amiga execution or rendering proof.
Only this new helper, new differential test and report were authored. No prior
helper/test, shared probe/builder/verifier, README, public synthetic tests,
aggregate script, commit, deployment or ADF was changed. Delivered Z/X ADF is
immutable. This is newly authored recovery; later playable/audio source remains
lost. No full boot, gameplay, speed, full tick, RTI or audible output claim.
