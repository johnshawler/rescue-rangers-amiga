# Native title countdown and input dispatch

This separate host-only static 68020 extension continues the frozen 1077-call
A025 checkpoint. It is new translation of original behavior, not recovery of
missing later gameplay or audio source. The earlier files are unchanged.

## Meaningful results and next boundaries

The default continuous proof performs 42 genuine A025 decrements, taking BE/BF
from 900 to 858, with actual scheduler yields, controller polling, NMIs and
music processing between title iterations. It stops at the next untranslated
music command: PC83A0, A=0E. It does not skip this command, replace queued work,
clear flags, or fabricate a title-ready state. At that boundary the music bank
is correctly bank3 inside the still-active NMI; the title bank remains the
saved bank2 return destination. CHR0/CHR1 remain 1F/1F and the original title
caller return bytes F7/C5 remain at RAM01BE/01BF, representing return C5F8.

Default final result:

- 2318 native helper calls, 78 real original-ROM NMIs, 75 completed later audio
  calls, and three command02 calls. The last NMI is still in progress.
- 31652 RAM stores, 4731 PPU events, 810 mapper writes, 1386 controller events,
  4410 semantic resource reads and 601 APU writes.
- Complete context 83A0/0E/2A/00/A4/F2/A7; mapper (1E,1F,1F,3,empty).
- Composite 25238 bytes, SHA256
  72b56974cc282a80508e7041d5257b3048a0f8007a92a4da103622d0bf260ebb.

Independent runs supply authentic external pad input after the first A025
visit. Both original controller reads and native scheduler arguments receive
identical pad bytes; no controller RAM, stack, flags or task state is injected.
Each run reaches its first new input boundary after 1104 calls, 37 NMIs,
35 completed later audio calls, and two decrements (timer898):

- Start (10 hex) reaches A05C, before the original character-menu resource
  copy. Context A05C/00/FF/FF/27/BD/A7, 17441 RAM stores.
- Select (20 hex) and Right (01 hex) reach F379, before sound27 queueing.
  Context F379/27/88/FF/25/BB/A7, 17445 RAM stores.
- Left (02 hex) also reaches F379, with X=28 and the other context bytes equal
  to the Select run. Both wrapped JSR writes preserve return A055.
- Each input run also matches 4321 PPU events, 405 mapper writes, 666 controller
  events, 2342 resource reads and 266 APU writes. Mapping remains bank2.

F379 queue handling, A055 continuation, A05C character-menu table loading and
music command0E are explicit next boundaries. No end-to-end timeout is claimed:
the genuine default path encounters command0E before the 900-frame timer expires.
The isolated timeout and sprite-return paths are nevertheless exhaustively
checked against the original, without representing them as resident reachability.

## Helpers and contracts

All helpers require valid, exclusively owned, disjoint RAM2048, context8,
journal, code and native-stack regions. Context is big-endian PC.word followed
by A/X/Y/rawP/SP/reserved. A0/A1/A2 select RAM/context/journal. D0 returns the
ordered RAM-store count, or -1 for inert wrong-PC rejection. D1-D7 and A0-A6
are preserved; native stack is balanced and native CCR is scratch. Journal
records are address.word/value.byte/zero.byte, with no header; unused bytes
are untouched. Bank2 is an adapter precondition. There are no resource reads,
mapper changes, embedded cartridge code/data, or runtime 6502 interpreter.

- recovery_title_menu_countdown.s: A025 to A000 or A0BB. Journal16; two stores
  normally, four on expiry. Uses binary Ricoh SBC even with raw D set, including
  propagated borrow, overflow and preserved raw B/U bits. Zero timer wraps to
  FFFF rather than forcing expiry.
- recovery_title_menu_dispatch.s: A000 to FF04, F379, A05C or A0BB. Journal16;
  zero, two or four stores. Handles all 256 input bytes with original Start,
  Select and direction priority, including combinations and arbitrary RAM50.
  Genuine page-one-wrapped JSR pushes are journaled in order.
- recovery_title_menu_exit.s: A0BB hides 64 sprites and executes RTS through
  the live wrapped stack. Journal256; exactly 64 ordered stores. It preserves
  the original final X=0, A=F8, N=0, Z=1 and other raw flags. The destination
  comes from actual RAM, not a forced C5F8 return.

## Verification and reproduction

The synthetic suite models timer arithmetic as whole 16-bit state transitions,
input selection as declarative priorities and sprite clearing as an ordered
set of output addresses. It does not decode ROM or native instruction streams.
The private suite independently executes the original cartridge using the
validated Ricoh binary-arithmetic CPU reference; neither raw status nor stack
frames are normalized or patched in isolated comparisons.

Each suite checks 77824 valid cases: all 65536 timer values plus 4096 varied
raw-status/stack/input cases per helper. Every status byte and SP is covered,
including wrap. The public suite also checks all 65535 wrong PCs per helper
(196605 inert guards total). Tests compare all RAM, all eight context bytes,
ordered stores, entire journals and untouched tails, native ABI, stack balance,
canaries and global access whitelists. No new resource reads are permitted.
The resident test loads native RAM/context exactly once, at reset, and compares
all state, ordered effects, resources, mapper snapshots, journals, DMA and ABI
at every boundary. It explicitly revalidates the frozen A025 checkpoint before
continuing. Existing asynchronous-interrupt and unsupported-audio limitations
remain in force.

Set VASM to the approved vasmm68k_mot and PYTHONPATH to inspection dependencies:

```
python port/tests/recovery_test_title_menu_loop.py
python port/tests/recovery_test_title_menu_loop.py --rom
python port/tests/recovery_test_resident_title_menu_loop.py
MENU_INPUT=16 python port/tests/recovery_test_resident_title_menu_loop.py
MENU_INPUT=32 python port/tests/recovery_test_resident_title_menu_loop.py
MENU_INPUT=1 python port/tests/recovery_test_resident_title_menu_loop.py
MENU_INPUT=2 python port/tests/recovery_test_resident_title_menu_loop.py
```

Private input is Europe ROM SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
No assets, ADFs, existing sources, index, branch or publications are changed.
No target Amiga gameplay, audible output, display, stock-machine memory/speed,
or Z=B/X=A gameplay integration is claimed. Eventual user key preference
remains Z for B pickup/throw and X for A jump; this host proof changes no keys.
