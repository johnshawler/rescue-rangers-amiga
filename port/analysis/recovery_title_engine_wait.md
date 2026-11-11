# Resident title-engine entry and first menu resume

The new static native 68020 composition advances the original C5D1 checkpoint
through title table initialization, the live bank-2 A000 menu entry, its genuine
FF04 yield, an additional NMI with audio processing, and scheduler return to
A025. It stops before the original countdown subtraction. This is new native
translation of original game behavior, not recovery of missing later source.

## Original control flow and exact scope

C5D1 copies 30 bytes from fixed-bank D657 to 0340 in descending X order.
C5DC copies 30 bytes each from C73F and C75D into 05A0 and 05D0,
interleaved in descending Y order. C5ED sets BE/BF to 84/03, and the original
JSR at C5F5 calls A000 in live bank 2, preserving return C5F8.

A000 checks controller edge state 14: bit 10 selects confirmation, bit 20
changes the selection, and bits 03 select a direction. With none of these
bits set, the original reaches A022 and calls FF04, preserving return A025.
This is a menu wait, not an assumed initialization return. The composition
executes the actual frame yield, task scan, NMI, music call, RTI and task
resume. No ready flag, task delay, callback, stack frame or pending work is
injected, skipped or cleared to achieve the endpoint.

At A025 the next original instructions subtract one from BE/BF using Ricoh
binary SBC and loop to A000 while nonzero. Expiry sets RAM50 and RAMB8 to
one and branches to A0BB, which hides sprites before returning to C5F8.
The countdown, input-selection branches, later title update queue and subsequent
startup/gameplay are not translated by this slice.

## New helper contracts

Both helpers require exclusively owned, valid, disjoint RAM (2048 bytes),
CPU context (eight bytes: big-endian PC, A, X, Y, raw P, SP, reserved), journal,
code and native-stack buffers. A0/A1/A2 point to RAM/context/journal.
D1–D7 and A0–A6 are preserved, native stack is balanced, and native CCR is
scratch. There is no general runtime 6502 interpreter or embedded cartridge
code, table payload, captured RAM fixture or extracted artwork.

- `recovery_title_engine_tables.s`: C5D1 -> A000. A3 points to the immutable
  16384-byte fixed PRG bank 7 view. The 362-byte journal consists of count.word
  then 90 address.word/value.byte/zero.byte resource records in original
  order. It performs 94 ordered RAM stores, including both wrapped JSR stack
  writes. D0=1 success or -1 for an inert wrong-PC rejection. Reads are exactly
  D657..D674, C73F..C75C and C75D..C77A in the documented loop order.
- `recovery_title_engine_wait.s`: A000 -> FF04 only when RAM14 & 33 is zero.
  The two wrapped stack writes are recorded as address.word/value.byte/zero.byte
  in an eight-byte journal without a header. D0=2 success or -1 rejection.
  All unsupported input combinations and wrong PCs reject before changing
  RAM, context or journal. Ignored input bits CC remain permissible.

Mapping is an adapter precondition: bank2, fixed bank7, mapper control 1E,
and an empty serial latch. The helpers do not modify mapper state. The new
composition validates mapping on resource access and compares the whole mapper
snapshot after every call. Its fixed bank is loaded once and checked immutable.
No new arithmetic operation is translated here. Independent original-ROM tests
use the previously validated Ricoh binary-arithmetic reference even for D-set
status cases. No reference status byte is patched or normalized in the isolated
tests. The inherited resident comparison uses the architectural B/U view and
does not modify reference state or frames.

## Verification

- 256 synthetic table cases and 256 independent original-ROM cases cover every
  raw status byte and every SP, including page-one wrap. All 90 source reads,
  94 stores, complete RAM/context and journal match.
- 4096 synthetic and 4096 original-ROM menu cases cover all raw status bytes,
  all SP values and all 16 supported controller masks. An additional public
  256-input sweep verifies every input byte, including inert rejected branches.
- Each helper passes all 65535 invalid-PC guards. All tests validate preserved
  native registers, stack balance, buffer canaries, full journal and untouched
  tails, immutable resources, and global read/write range whitelists.
- The continuous resident proof loads RAM/context once at reset. Native and
  original execution thereafter proceed independently through all boundaries.
  No captured state is reloaded into the native machine.

Final resident result:

- 1077 helper calls, 36 real reference NMIs, 34 later active music calls.
- 17166 RAM stores, 4311 PPU events, 395 mapper writes, 648 controller events,
  2299 semantic resource reads and 254 APU writes.
- Context A025/FF/FF/FF/A4/BD/A7; BE/BF remains 84/03 before countdown.
- Mapper control 1E, CHR0=1F, CHR1=1F, PRG2 and empty serial latch.
- Compared with C5D1: 53 calls, one NMI, 655 RAM stores, 10 PPU events,
  10 mapper writes, 18 controller events, 152 resource reads and two APU writes.
- Composite size 24538 bytes, SHA256
  `0f8bd197346e72c2f577bd2528ef721dd97a86d52348cec1f9ad817157a5d112`.

The host composition uses three immutable 16384-byte resource views, 2048-byte
RAM, eight-byte context, the inherited maximum 32770-byte journal, and native
stack. This is not a stock-Amiga allocation or timing result.

## Reproduction and limits

Set VASM to the approved `vasmm68k_mot` executable and PYTHONPATH to the
inspection dependencies, then run:

```
python port/tests/recovery_test_title_engine_tables.py
python port/tests/recovery_test_title_engine_tables.py --rom
python port/tests/recovery_test_title_engine_wait.py
python port/tests/recovery_test_title_engine_wait.py --rom
python port/tests/recovery_test_resident_title_engine_wait.py
```

Private tests require Europe ROM SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
The source manifest hashes the new work and its local source dependencies.
Existing helpers, reports, target drivers, validation aggregates and ADFs are
unchanged by this work. No commit, index change, branch change or publication
is included. No displayed target title, playability, stock-speed execution,
audible Paula output or complete Amiga game is claimed. Existing unsupported
music commands, queues, callbacks and arbitrary asynchronous interrupt placement
remain explicit boundaries.
