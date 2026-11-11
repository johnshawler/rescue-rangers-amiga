# Native music command 12 and continuous title loop

This host-only static 68020 extension adds the original music command 12 to the
independently reviewed command 01 reset chain. It does not recover missing later
gameplay or audio source. All 104 entries in the predecessor command 01 manifest
remain byte-identical. Only newly named source, tests, report and manifest files
are added. No Git index, commits, branches, publication, assets or ADFs changed.

## Continuous result and next boundary

One native RAM/context load at reset now reaches command 13 at PC83A0 in bank 3,
context 83A0/13/2A/00/A4/F2/A7, still within an active NMI. The run completes 12513
native calls, 406 genuine original NMIs and 403 later completed audio calls.
There are 370 genuine title countdowns, taking the timer from 900 to 530, with
5 command 02, 58 command 0E, 6 command 01 and 2 command 12 calls. Ordered effects:
132701 RAM writes, 8011 PPU events, 4090 mapper writes, 7290 controller events,
21755 semantic resource reads and 3093 APU writes. Mapper state remains control
1E, CHR0/CHR1=1F/1F, PRG bank 3 and empty serial shift state. Saved return bytes
F7/C5 remain at 01BE/01BF. The composed binary is 28100 bytes with SHA256
636fde15b3f4885a2140cd7483bfc7085c2fc6288cbaebe5ee7811fe6fda606d.

The proof explicitly checks the predecessor 2318, 7038 and 10433-call checkpoints.
It never injects reference RAM/context, patches readiness/status/frame state,
skips music or queued work, or reloads native RAM after reset. Start, Select,
Right and Left use matched external pad values in original and native polling.
Each regression still reaches its previous A05C/F379 boundary at 1104 calls,
37 NMIs, two countdowns and timer 898. These input paths precede command 12.

## Derivation and contract

Original CMP04 at 8473 sends command 12 through the operand fetch at 856E,
saving the command in C4 and the fetched operand in C3. Dispatch table bytes
84A7/84A8 are F7/84. The destination 84F7 selects slot zero. TXA/CLC/ADC C2
produces Y=X. The command comparison at 850E branches to 8523, not the command
0E initialization/decrement path. Original SEC/SBC01 computes slot counter-1.

If the initial counter at 0744+X is not one, the subtraction result is nonzero.
The counter is not stored. The stream pointer, already advanced for the operand,
is advanced another two bytes at 8542 without reading those two bytes. The final
A is the low-byte addition result and Y=X. Original binary ADC supplies C/V/N/Z;
an overflow into the high pointer byte performs INC and updates N/Z accordingly.

If the initial counter is one, zero is stored in that counter. The original
JSR8551 writes wrapped stack return bytes 85/30, applies
(0730+X AND 97) OR first operand to channel state, and returns. Two further
stream fetches read the high and low destination bytes. The first is temporarily
stored in C3, the second replaces the low stream pointer, and C3 replaces its
high byte. A is the high byte and Y=0. Carry from the subtraction remains set,
overflow is clear, and N/Z follow the high byte. D/I/B/U are preserved exactly.
Decimal mode never enables BCD arithmetic on the Ricoh CPU.

Every original page-one write, including dispatch scratch and all fetch-return
addresses, is preserved in order, including wrapping SP. No APU, mapper, PPU or
controller writes are emitted by this command itself. No general 6502 opcode
interpreter is used in the native implementation.

ABI: A0=RAM2048, A1=context8, A2=journal22, A3=immutable bank3 16384 bytes.
Context is big-endian PC.word then A/X/Y/rawP/SP/reserved. Journal is count.word
and up to five address.word/value.byte/kind.byte entries, with kind zero for
resource reads. Unused journal bytes are zeroed on success. D0 returns 1 or -1
for inert rejection. D1-D7/A0-A6 are preserved and native stack balances; CCR is
scratch. Regions, code and stack must be valid, disjoint and exclusively owned.
The adapter establishes stable bank 3 mapping.

Preflight checks entry PC83A0, A12, X28..2B and dispatch bytes before any mutation.
All raw statuses and SP values are accepted. The initial stream pointer must be
8000..BFFF. If the counter equals one, it must additionally be at most BFFD,
allowing all three consumed bytes to lie within the bank. Other counter values
may start at BFFE/BFFF because the two skipped bytes are never dereferenced.
Destination pointer values are not validated here because this command only
stores them; the following fetch owns its read boundary. Resource validation
reads are 4A7 followed by 4A8, with the second omitted if the first fails. There
are no speculative operand reads. Rejection preserves RAM/context/journal.

## Verification

The ROM-free contract is independent of the assembly source. It crosses every
counter and operand, covers all 65536 initial pointers, explores bank-edge and
branch combinations, all incorrect entry PCs, commands/channels and dispatch
bytes. Result: 82279 accepted cases and 116048 inert rejections. A supplemental
Cartesian suite checks all 65536 channel-state/operand pairs on the state-change
branch. Complete RAM/context, ordered writes, journals, exact resource read order,
immutable resources, canaries, register preservation, stack balance and global
memory-access whitelists are checked on accepted and rejected cases.

Actual-ROM differential tests execute original instructions, not native-source
interpretation. They cover every mapped pointer on all four channels (65536
cases), plus all 65536 counter/raw-status pairs and actual-bank invalid command,
channel and dispatch cases (1020 inert rejections). The Ricoh binary ADC and SBC references each pass
262144 independent truth-table cases, including D set. Raw noncanonical B/U bits
and every wrapped emulated SP value are exercised. The resident proof compares
full RAM/context/effects and journals at each native boundary, plus mapper state,
DMA bytes, immutable resources and ABI/access guards.

Reproduce with VASM pointing to vasmm68k_mot and PYTHONPATH including the inspection
dependencies:

```
python port/tests/recovery_test_active_command12_contract.py
python port/tests/recovery_test_active_command12_rom.py
python port/tests/recovery_test_active_command12_adversarial.py
python port/tests/recovery_test_resident_command12_loop.py
MENU_INPUT=16 python port/tests/recovery_test_resident_command12_loop.py
MENU_INPUT=32 python port/tests/recovery_test_resident_command12_loop.py
MENU_INPUT=1 python port/tests/recovery_test_resident_command12_loop.py
MENU_INPUT=2 python port/tests/recovery_test_resident_command12_loop.py
```

Private original Europe cartridge SHA256:
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
No cartridge assets or instruction-byte dumps are added to deliverables.

This is host M68EC020 behavioral proof only. Command 13 is the next unsupported
music dependency. Complete title timeout, playable gameplay, visible target
Amiga display, audible Paula output and stock-machine speed/memory are not proven.
Separate menu-input/rendering experiments and existing asynchronous-interrupt
limits remain outside this extension.
