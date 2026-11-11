# Native music command 13 and continuous title loop

This host-only static 68020 extension implements the original music command 13
and continues the independently reviewed command 12 reset chain. All 111 files
in the predecessor manifest remain byte-identical. The predecessor manifest's
SHA256 is 1e3ed057f05b7215a1ab8e15674068fd2f37829dcb070d0a8fc518f0f0afd32e.
Only newly named source, tests, this report and a manifest are added. No existing
source, Git index, commits, branches, publication, cartridge assets or ADFs change.

## Continuous result and next dependency

One native RAM/context load at reset reaches the next unsupported music command
0F at bank 3 PC83A0, context 83A0/0F/2A/00/A4/F2/A7, inside an active NMI.
The chain completes 14584 native calls, 473 genuine original NMIs and 470 later
completed audio calls. There are 437 title countdowns, taking the timer from
900 to 463, with 6 command 02, 67 command 0E, 6 command 01, 2 command 12 and
1 command 13 calls. Ordered effects comprise 152783 RAM writes, 8681 PPU events,
4760 mapper writes, 8496 controller events, 25221 semantic resource reads and
3598 APU writes. Final mapper state is control 1E, CHR0/CHR1=1F/1F, bank 3,
with no pending serial bits. Saved return bytes F7/C5 remain at 01BE/01BF.
The composed binary is 29244 bytes, SHA256
765fa2190ec384358d1a9f48ab078bde5bca179f40a4c4a24fe4c85adccd18ff.

The continuous proof checks the preceding 2318, 7038, 10433 and 12513-call
checkpoints, comparing full RAM, context, ordered effects, journals and mapper
state at every native boundary. It performs no reference-state injection, RAM
reload, readiness/status/frame patch, or skipped audio or pending work. The live
command 13 call selects X=2A with slot counter zero, stream A3BA and channel state
08. It takes the original skip branch, exits with context 839D/BD/2A/2E/A4/F2/A7,
and advances the stream to A3BD without changing the counter or channel state.
Both branches are independently tested outside the resident trace.

Start, Select, Right and Left use identical external pad values in original and
native polling. Each still reaches its prior A05C/F379 boundary at 1104 calls,
37 NMIs, two countdowns and timer 898. These paths precede command 13 and emit
266 APU writes. No separate character-menu or rendering work is incorporated.

## Derivation and static implementation

The original CMP04 path at 8473 saves the command in C4, fetches its first operand
through 856E, and stores that operand in C3. Command 13's dispatch table bytes at
84A9/84AA select 84FB. LDA04 followed by TXA/CLC/ADC C2 chooses Y=X+4. The shared
CMP12 at 850E goes to 8523, where SEC/SBC01 tests the selected counter at 0744+Y,
which is 0748+X. This is distinct from command 12's counter at 0744+X.

If the initial counter is not one, its subtraction result is nonzero, and no
counter store occurs. The stream, already incremented for the first operand,
advances two further bytes without reading those bytes. Final Y=X+4. Final A is
the low-byte addition result. Binary ADC sets C/V/N/Z; a carry increments the
high pointer byte and replaces N/Z with that byte's flags.

If the initial counter is one, zero is stored in the selected counter. Original
JSR8551 writes wrapped return bytes 85/30 and updates channel state to
(0730+X AND 97) OR first operand. Two stream fetches then obtain high and low
jump-destination bytes. The high byte is temporarily stored in C3, the low byte
replaces the low stream pointer, then C3 replaces the high stream pointer.
Final A is the destination high byte, Y=0, C=1, V=0, and N/Z follow the high byte.
Raw D/I/B/U bits are preserved; Ricoh arithmetic remains binary even with D set.

The translation is a fixed native control flow, not a general 6502 interpreter.
It preserves all original RAM writes, including dispatch scratch and wrapped
page-one return addresses, in order. The command itself emits no APU, mapper,
PPU or controller writes. Resource journaling preserves operand-before-dispatch
read order and does not turn skipped stream bytes into reads.

## ABI and rejection contract

A0 points to RAM2048, A1 to context8, A2 to journal22, and A3 to an immutable
16384-byte bank-3 resource. Context is big-endian PC.word followed by A/X/Y/rawP/
SP/reserved. The journal has count.word and five address.word/value.byte/kind.byte
slots, with kind zero for resource reads. Unused successful journal bytes are
zero. D0 returns 1, or -1 for inert rejection. D1-D7/A0-A6 are preserved, native
stack balances, and CCR is scratch. The caller owns valid disjoint regions and
establishes stable bank-3 mapping.

Preflight validates PC83A0, command13, X28..2B, and the two dispatch bytes before
mutation. All raw statuses and emulated SP values are valid. Initial stream
pointer must be 8000..BFFF. Selected counter one additionally requires a pointer
at most BFFD, since all three bytes will be consumed. Other counters accept
BFFE/BFFF because the subsequent two bytes are skipped. Stored destination
pointers may be anywhere in the 16-bit address space: the next fetch owns that
read's bounds check. Validation resource reads are 4A9 then 4AA, with the second
omitted if the first fails. There are no speculative operand reads. Rejection
preserves RAM, context and journal exactly.

## Verification and reproduction

The ROM-free declarative model is independent of the assembly. Its suite crosses
all counters and operands, visits all 65536 initial pointers, covers branch and
bank-edge combinations, and tests all incorrect entry PCs, commands, channels
and dispatch bytes: 82279 accepted cases and 116048 inert rejections. Another
65536 cases cross channel state and operand. The slot suite crosses all 65536
selected/other-slot counter pairs and all 65536 destination pointers, the latter
with the stream at the final legal three-byte position BFFD.

Actual-ROM differential tests execute original instructions. Coverage includes
65536 mapped-pointer/channel cases, 65536 counter/raw-status pairs, 1020 actual-bank
invalid command/channel/dispatch cases, and 10240 bank-edge/counter/channel
combinations. The Ricoh binary ADC and SBC references each pass 262144 independent
truth-table cases. Raw noncanonical B/U bits and every wrapped SP are exercised.
Successful and rejected native calls check full RAM/context, ordered writes,
journals, exact resource reads, immutable bank bytes, region canaries, preserved
registers, balanced stack and global memory-access whitelists. The continuous
proof also checks NMI frames, DMA bytes and immutable mapped/fixed resources.

Use VASM pointing to vasmm68k_mot and PYTHONPATH including the inspection
machine68k/py65 dependencies:

```
python port/tests/recovery_test_active_command13_contract.py
python port/tests/recovery_test_active_command13_rom.py
python port/tests/recovery_test_active_command13_adversarial.py
python port/tests/recovery_test_active_command13_slots.py
python port/tests/recovery_test_resident_command13_loop.py
MENU_INPUT=16 python port/tests/recovery_test_resident_command13_loop.py
MENU_INPUT=32 python port/tests/recovery_test_resident_command13_loop.py
MENU_INPUT=1 python port/tests/recovery_test_resident_command13_loop.py
MENU_INPUT=2 python port/tests/recovery_test_resident_command13_loop.py
```

Private Europe cartridge SHA256:
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
No cartridge assets or instruction-byte dumps are added to deliverables.

This proves host M68EC020 behavior only. Command 0F is the next unsupported music
dependency. Full title timeout, playable gameplay, visible target Amiga display,
audible Paula output, stock-machine speed and target memory usage are not proven.
Existing asynchronous-interrupt limitations and separate input/rendering work
remain outside this extension.
