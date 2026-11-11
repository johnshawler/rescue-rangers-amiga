# Native music command 01 and continuous title loop

This is new host-only static 68020 development extending the independently
reviewed command 0E reset chain. It is not recovery of missing later gameplay or
audio source. Prior sources and manifests are unchanged. No opcode interpreter,
cartridge code, cartridge assets or ADF changes are introduced.

## Continuous result and next boundary

The composition loads native RAM/context once, at reset, and compares complete
state and ordered effects against continuous execution of the private original
cartridge. It revalidates the prior 2318-call command 0E checkpoint and 7038-call
command 01 checkpoint without injecting reference state, skipping music, clearing
pending work, or patching status or readiness.

The next unsupported boundary is music command 12 at PC83A0 in bank 3, still within
an active NMI. Context is 83A0/12/2B/00/A4/F2/A7. The run completes 10433 native
calls, 339 original NMIs, 336 later completed audio calls, 5 command 02 calls,
48 command 0E calls and 4 command 01 calls. There are 303 genuine title countdowns,
taking the timer from 900 to 597. Ordered effect counts are 112877 RAM writes,
7341 PPU events, 3420 mapper writes, 6084 controller events, 18373 semantic
resource reads and 2613 APU writes. Mapper control is 1E, CHR0/CHR1=1F/1F,
PRG bank 3 and empty serial shift state. Saved title return bytes F7/C5 remain
at 01BE/01BF.

The assembled composite is 26956 bytes, SHA256
b7c71d3bc87f08215f5e33002192ad7e2aa224ab9df5004be94193115e21273d.

Start, Select, Right and Left regression runs each reach their prior A05C or
F379 boundary after 1104 calls, 37 NMIs and two countdowns, timer 898. Both original
polling and native scheduler receive matching external pad bytes. These paths
stop before command 01 and are regression evidence, not command 01 reachability.

## Original behavior and native contract

Entry is PC83A0/A01 with X28..2B. Original CMP20 and CMP04 establish carry clear;
command 01 does not call stream fetch 856E. The original table dispatcher 8023
uses table 8485/8486, whose low/high bytes B9/84 lead to 84B9. LDA#40 followed by
the always-taken BNE84C6 and EOR0730,X toggles bit 40 of the channel state.
STA0730,X and RTS return through 83A7 to 839D. No stream pointer is consumed,
validated, advanced or dereferenced. A is the toggled value, X is unchanged,
Y is 04, SP returns unchanged and N/Z reflect the toggled value. Carry is clear;
V/D/I/B/U are preserved exactly, including noncanonical raw status combinations.
There is no ADC or SBC within this command. Continuous reference execution uses
the predecessor Ricoh binary ADC/SBC implementation, including when D is set.

Wrapped emulated stack writes are 83,A6, 84, 82 followed by temporary target-low B9.
The dispatch pops 82/84 into C1/C2, fetches and journals B9/84, temporarily pushes
B9, stores 84 in C2, then pops B9 into C1. The original final outer return pops
A6/83. All RAM writes, including temporary page-one stores, are preserved in
order. Command 01 itself emits no APU, mapper, PPU or controller effects.

The native ABI is A0=RAM2048, A1=context 8, A2=journal 10, A3=immutable bank 3
16384 bytes. Context is big-endian PC.word then A/X/Y/rawP/SP/reserved. Regions,
code and native stack must be valid, disjoint and exclusively owned; the adapter
must establish stable bank 3 mapping. D0 returns 1 on success or -1 on inert
rejection. D1-D7/A0-A6 are preserved; native stack balances, CCR is scratch.
Journal is count.word followed by two address.word/value.byte/kind.byte entries,
kind 0. Entry PC, command, channel and both dispatch destination bytes are checked
before any RAM/context/journal mutation. All raw P and SP bytes are accepted.
The only resource validation reads are 485 and then 486; the second is omitted
if the first fails. Accepted semantic reads repeat those two addresses in order.
Rejection leaves every RAM/context/journal byte unchanged.

## Tests and scope

The ROM-free suite checks all 256 initial channel values crossed with all 256
raw statuses, including every wrapped SP value. An additional 1024 cases exercise
each channel with each initial channel value and raw status, complementary SP
and randomized Y. This is 66560 accepted cases. The suite checks all 65535 wrong
PCs, all 255 wrong commands, 252 wrong channels and 510 incorrect dispatch bytes:
66552 inert rejections. Rejected resource reads are checked exactly.

The actual-ROM differential independently executes the original instructions
for 66560 accepted cases, comparing both native and declarative results. It also
checks 1017 inert actual-bank rejections with incorrect commands, channels and
dispatch bytes. Both suites verify full RAM/context, ordered effects, complete
journals, read order, immutable resources, canaries, register preservation,
stack balance and global memory-access whitelists. The resident composition
checks these properties at every boundary, plus mapper state and DMA journals.

Reproduce with VASM pointing to vasmm68k_mot and PYTHONPATH including the
inspection dependencies:

```
python port/tests/recovery_test_active_command01_contract.py
python port/tests/recovery_test_active_command01_rom.py
python port/tests/recovery_test_resident_command01_loop.py
MENU_INPUT=16 python port/tests/recovery_test_resident_command01_loop.py
MENU_INPUT=32 python port/tests/recovery_test_resident_command01_loop.py
MENU_INPUT=1 python port/tests/recovery_test_resident_command01_loop.py
MENU_INPUT=2 python port/tests/recovery_test_resident_command01_loop.py
```

Private Europe cartridge SHA256:
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.

This is host M68EC020 behavioral proof only. It does not prove complete title
timeout, playable gameplay, target Amiga display, audible Paula output, or
stock-machine speed/memory. Command 12, not fabricated readiness, is the next
music dependency. Existing menu/input and asynchronous-interrupt limits remain.
No Git index, commit, branch, publication or ADF was changed.
