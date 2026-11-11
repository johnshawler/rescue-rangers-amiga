# Native music command 0F and full title timeout

This additive, host-only static 68020 extension implements original command 0F.
All 119 entries in the command 13 predecessor manifest remain byte-identical.
That manifest's SHA256 is
5e4fcb8117eb28a8ceb3ff39a460a0b5123bcf7fc6c96c7c2f40989c9e1bee3e.
Only newly named source, tests, this report and its manifest are added. Existing
source, aggregate scripts, README, Git index/branches/commits, publications and
preserved ADFs are not modified by this extension.

## Continuous result

One native RAM/context load at reset now reaches the complete 900-countdown
no-input title timeout, with timer zero, at the next genuine boundary C5F8.
Final context is C5F8/F8/00/FF/27/BF/A7. There are 28818 native helper calls,
935 genuine original NMIs, and 933 later completed active audio calls.
Command counts are 10 command 02, 121 command 0E, 17 command 01, 4 command 12,
2 command 13 and 1 command 0F. Ordered effects comprise 297913 RAM writes,
13301 PPU events, 9385 mapper writes, 16830 controller events, 48634 semantic
resource reads and 7136 APU writes. Final mapper state is control 1E,
CHR0/CHR1=1F/1F, bank 2, with no pending serial bits. Saved return bytes F7/C5
remain at 01BE/01BF.

The composite is 30374 bytes, SHA256
b0c694f858c94a4ab728f3ac2ad158956c4e28ab2a3eaeb32b3142cb5753e7d7.
The continuous test retains and checks the preceding 2318, 7038, 10433 and
12513-call checkpoints, and adds the reviewed 14584-call checkpoint with
context 83A0/0F/2A/00/A4/F2/A7, 437 countdowns and 3598 APU writes.
Every native boundary compares full RAM/context, ordered events, journal,
mapper state and access bounds. There are no reference-state injections,
RAM reloads, patched readiness/status/frame values, or skipped music commands.

The live command 0F enters with X=2A, stream A3C6, counter zero and operand one.
It reloads the selected counter to one, jumps the stream to A3A9, and exits
with context 839D/A3/2A/00/A4/F2/A7. The new helper itself emits no APU writes.

Start, Select, Right and Left regressions still stop at the earlier A05C/F379
boundaries after 1104 helpers, 37 NMIs, two countdowns, timer 898 and 266 APU
writes. Both implementations receive identical external pad inputs. Those
paths precede command 0F; separate character/menu/rendering work is not included.

C5F8 begins the original title-return continuation by reading B8; its branches
lead toward further mode setup. This extension stops there and does not claim
that subsequent continuation, attract/gameplay execution, or later music is
implemented.

## Derivation and native behavior

Original 8473 saves command 0F in C4, fetches its first operand through 856E,
and saves it in C3 before dispatch. Table entries 84A1/84A2 select 84FB.
That entry computes Y=X+4, selecting counter 0744+Y, which is 0748+X.
Command 0F follows the below-12 branch at 850E to 8512.

The original performs binary SEC/SBC 1 on the counter. If subtraction borrows
(initial counter zero), it reloads the first operand from C3. It always stores
the resulting counter. A nonzero result fetches destination high and low bytes
and replaces the stream pointer. A zero result advances the already-incremented
stream pointer by two without reading those skipped bytes. Channel state at
0730+X is unchanged; command 13's conditional channel-state update is absent.
Counter one always skips; counter zero reloads and may either skip or jump;
other counters decrement and jump.

The translation has fixed native control flow, with no runtime 6502 opcode
decoder. It preserves all ordered scratch, counter, stream and wrapped page-one
return writes. Stream fetch precedes dispatch-table semantic reads. On a jump,
final A is destination high and Y=0; C/V come from the binary counter subtraction
(including reload cases), and N/Z from the destination high byte. On a skip,
Y=X+4 and A is the low-byte plus-two result. ADC determines C/V/N/Z; a carry
increments the stream high byte and replaces N/Z. Raw D/I/B/U are preserved;
D never enables decimal arithmetic on the Ricoh reference.

## ABI, bounds and inert rejection

A0 points to RAM2048, A1 to context8, A2 to journal22, A3 to immutable bank3
resource16384. Context contains big-endian PC.word, then A/X/Y/rawP/SP/reserved.
The journal is count.word plus five address.word/value.byte/kind.byte records;
resource kind is zero. Unused successful journal bytes are zero. D0 returns 1
on success or -1 for inert rejection. D1-D7/A0-A6 are preserved, native stack
balances, and CCR is scratch. Caller-owned regions must be valid and disjoint;
the caller establishes stable bank-3 mapping.

Preflight checks PC83A0, command0F, X28..2B, dispatch bytes FB/84, and initial
stream pointer 8000..BFFF before mutation. All raw P and SP values are accepted.
Streams through BFFD always have enough bytes. BFFE/BFFF are accepted for
counter one, or for counter zero with a zero reload operand; all other edge
cases reject before any writes. Destination pointers themselves may be any
16-bit value; their next fetch owns the next read bounds check.

Validation reads are 4A1 then 4A2, with the second omitted on a first-byte
mismatch. Only for a valid BFFE/BFFF pointer with initial counter zero does
preflight read that first operand to decide bounds. It is immutable, and is
read again at the proper semantic fetch point if accepted. This validation
read is separately asserted, not disguised as an original semantic read.
No target bytes are read speculatively or when skipped. Rejection leaves RAM,
context and journal entirely unchanged.

## Verification and reproduction

The independent ROM-free declarative contract passes 82167 accepted cases and
116160 inert rejections. It crosses all counter/operand pairs, all 65536 initial
stream pointers, bank-edge/branch combinations, and all incorrect entry PCs,
commands, channels and dispatch bytes. Another 65536 cases cross channel state
and reload operand, ensuring channel state remains unchanged. Slot tests cross
65536 selected/other-slot pairs, all 65536 jump destinations at BFFD, and 4096
reload-operand/bank-edge/channel/skip cases at BFFE/BFFF.

Actual original-ROM differential proofs cover 65536 mapped-pointer/channel
cases, 65536 counter/raw-status pairs, 1020 actual-bank invalid command/channel/
dispatch cases, and 10240 bank-edge/counter/channel combinations. Independent
binary ADC and SBC truth tables each cover 262144 cases. Tests exercise raw
noncanonical B/U flags and all wrapped SP values. Full RAM/context, ordered
writes, exact resource reads, complete journals, immutable resources, canaries,
preserved registers, stack balance and global memory-access whitelists are
checked for both successes and rejections. The resident test also verifies
NMI frames, DMA bytes and all three immutable mapped/fixed resources.

Set VASM to vasmm68k_mot and PYTHONPATH to the inspection dependencies, then run:

```
python port/tests/recovery_test_active_command0f_contract.py
python port/tests/recovery_test_active_command0f_rom.py
python port/tests/recovery_test_active_command0f_adversarial.py
python port/tests/recovery_test_active_command0f_slots.py
python port/tests/recovery_test_resident_command0f_loop.py
MENU_INPUT=16 python port/tests/recovery_test_resident_command0f_loop.py
MENU_INPUT=32 python port/tests/recovery_test_resident_command0f_loop.py
MENU_INPUT=1 python port/tests/recovery_test_resident_command0f_loop.py
MENU_INPUT=2 python port/tests/recovery_test_resident_command0f_loop.py
```

Private Europe cartridge SHA256:
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
No cartridge assets or instruction-byte dumps are included in deliverables.

This establishes host M68EC020 behavior, not audible Paula playback, visible
target Amiga display, target RAM usage, stock-machine speed or playable gameplay.
Existing asynchronous-interrupt restrictions remain. Later playable/audio
source is still missing; this is newly reconstructed static native work.
