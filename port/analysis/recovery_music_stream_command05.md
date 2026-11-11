# Reusable channel stream fetch and command05 checkpoint

Actual Europe-ROM inspection and continuous execution show that the next
stream command after command04 is $05 at $A2C3, with operands $02 and $49.
Two new static 68020 translations advance through it and stop at $839D,
before the following stream fetch. Existing helper14 is not reused at an
incorrect entry or patched: the new stream helper has its own $839D entry.

## Shared ABI and bounds

A0 points to original-layout 2,048-byte RAM; A1 to eight-byte canonical context
(big-endian PC, A/X/Y/P/SP/reserved); A2 to the helper's resource-read journal;
A3 to a caller-owned, read-only 16KiB bank3 view for original $8000–$BFFF.
All buffers must be valid, disjoint and exclusively owned. Journal layout is
count word followed by address word, value byte, kind byte zero records.
D0 returns 1 on success or -1 on unsupported input. D1–D7/A0–A6 and context
reserved are preserved, native stack balanced, native CCR scratch.

Both helpers require X=$2B and canonical P (B clear, U set). Every canonical
status, entry SP and entry Y is supported, including D=1: neither new slice
contains ADC/SBC. Generic py65 decimal behavior remains relevant only to
prior ADC-bearing helpers; continuous composition retains their D=0 scope.
All original stores, including stack stores and wrap order, are translated
explicitly. No CPU opcode fetch/decode/interpreter exists. Stream command
and operand bytes are game data. Public source embeds no cartridge assets.
No APU/PPU/mapper writes occur in either slice, so no hardware journal is
needed; the ordered effects test rejects any unexpected hardware event.

## recovery_music_stream_fetch.s

Entry PC=$839D. Any A and other RAM are supported. The channel pointer at
$0753/$0757 must be $8000–$BFFF; all guards precede writes and resource reads.
Journal size is six bytes, recording exactly one byte-only resource read.
JSR $856E writes two original stack bytes, copies the channel pointer to
C1/C2, fetches one byte and increments the channel pointer. Low-byte wrap
increments the high byte, including $BFFF to $C000 (the next helper will
reject that new out-of-window pointer). Success returns PC=$83A0, A=the
fetched byte, Y=0, X and SP unchanged; N/Z describe the last pointer INC,
and C/V/D/I are retained. Unsupported input is inert with no resource reads.

## recovery_music_command05.s

Entry PC=$83A0, A=$05. Pointer must be $8000–$BFFE so both operand reads fit.
Dispatch-table bytes at $848D/E must select the statically translated $84CD
handler. These two bounded read-only preflight reads occur before any
mutation and are not emulated resource events. Malformed low/high target
bytes reject after one/two reads; invalid context or pointer rejects before
any resource read. Rejection leaves RAM/context/journal unchanged.

Journal size is 18 bytes. Success records four original resource reads in
order: first operand, dispatch low byte, dispatch high byte, second operand.
There are six native resource reads including preflight, all byte-only.
The helper translates the dispatch stack push/pop effects, both stream
fetches, and the handler's ordered C8=0, CA=second operand, C9=first operand
writes. C3 holds the first operand, C4=$05, and C1/C2 retain the second
operand's original address. The channel pointer advances twice. Nine
original stack writes occur, with final SP equal to entry SP. Success returns
PC=$839D, A=second operand, Y=first operand, X unchanged, C=0, N/Z from the
first operand's LDY, and V/D/I retained.

## Executed host differential proof

Private ROM SHA256:
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.

`port/tests/recovery_test_music_stream_command05.py` assembles all helpers
with VASM's 68020 target and executes native code in machine68k M68EC020.
The independent py65 oracle executes the actual original ROM.

- 8,192 standalone comparisons (4,096 per new helper) vary complete RAM,
  all SP values, canonical statuses, Y/reserved, fetch A, and resource
  pointers, including low-byte wrap. Exact complete RAM/context, ordered
  RAM/resource effects, full read sequence, byte-only resource access,
  immutable resources, buffer guards, native registers and stack are checked.
  The stream slice takes 10/11 original instructions; command05 takes 51/52.
- 256 continuous reset runs compose eighteen calls to seventeen helpers,
  using two real `ref.nmi()` events, without captured-state or raw RAM/P
  patches. The named `architectural_status_view` normalizes only virtual B/U
  for comparison. The original oracle remains continuous through both new
  slices. C8/C9/CA become $00/$02/$49, pointer becomes $A2C6, PC=$839D,
  SP=$AB. The pending $C2A8 task continuation and nested frame remain intact.
- 133,114 unsupported cases reject inertly: every wrong PC for both helpers,
  unsupported X/A/P, out-of-window pointers, command05's unsafe $BFFF
  pointer, and all 510 malformed dispatch-byte alternatives. Another 8,192
  completed-boundary calls reject without mutation or resource reads.

Run with VASM set to the installed vasmm68k_mot and PYTHONPATH pointing to
rescue-recovery-inspection/.deps. All three PASS lines were observed.

Only two new source files, this new test and this report were authored.
No old helper/test, shared target probe/builder/verifier, README, public or
aggregate tests, commit, publication or ADF was changed by this worker.
Other workers own shared integration changes. Delivered Z/X ADF is immutable.
This is newly authored recovery; later playable/audio sources remain lost.
Host semantic proof is not native Amiga runtime proof. No full tick/RTI,
audible Paula, complete boot, gameplay or speed claim is made.
