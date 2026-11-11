# Native character-menu setup and pending video request

This separate host-only static 68020 translation advances the genuine Start
path from A05C. The original path loads X=23, copies bank2 A0C9..A0E0 in
descending order to RAM0360..0377, writes FF to RAM19, and calls FF04 with
return bytes A0/6B on the live page-one stack. No resource IDs, character
selection, queue readiness or return frames are supplied by the host.

The continuous proof starts native RAM/context exactly once at reset. Both
original controller reads and native scheduler receive external pad byte10
only after the first A025 visit. It revalidates the frozen 1077-call checkpoint
and the approved 1104-call A05C context, then executes the new setup, genuine
yield and scheduler idle scan. It stops at FE90 before the unsupported NMI.

Final matched state is FE90/00/10/00/26/FF/A7, after 1107 accepted native calls,
37 original NMIs and 35 completed later audio calls. The title timer remains
898; mapper state is (1E,1F,1F,2,empty). Ordered effects total 17477 RAM stores,
4321 PPU events, 405 mapper writes, 666 controller events, 2366 resource reads
and 266 APU writes. The composite is 25370 bytes, SHA256
 e2e55992da91ac5977a16f069ce0c33d5287404dcf2c8abd96a200eab3d079d8.

RAM19 remains FF. RAM0360..0377 equals the original resource table. RAM01BC
and RAM01BD retain 6B/A0, while the older C5F8 caller frame remains intact.
The frozen CHR NMI helper is explicitly invoked at this real boundary and
verified to reject inertly: RAM, context, journal, mapper and event/read
streams are unchanged. The original NMI tests RAM19 at C040 and calls C115
at C044 when nonzero. That queued-video work is the next required translation.
A06C character-menu input handling has not been reached natively or claimed.
Neither provisional command01 nor command0E is needed by this slice.

## Contract and tests

recovery_character_menu_setup.s accepts A05C only. A0/A1/A2/A3 address valid,
exclusively owned, disjoint RAM2048/context8/journal106/immutable bank2[16384].
Context is PC.word then A/X/Y/rawP/SP/reserved. Bank2 mapping is an adapter
precondition. D0 returns 1 or -1; all other data/address registers are preserved,
native stack is balanced and native CCR is scratch. Journal is count.word plus
24 ordered resource address.word/value.byte/zero.byte records; the eight-byte
tail remains untouched. Each semantic resource read precedes its RAM store.
No 6502 opcode interpreter or cartridge data is embedded. All 27 RAM stores,
including wrapped JSR writes, are independently observed by the test harness.

The ROM-free test uses arbitrary bank bytes and declarative copy/stack/status
semantics. It checks 4096 valid cases covering every raw status and SP, and
all 65535 invalid PCs. The private original-ROM test independently executes
the original instructions for 4096 cases, with raw flags and stack unchanged
at entry. Both compare complete RAM/context, ordered effects, complete journals
and untouched tails, immutable resources, native ABI, stack balance, canaries,
and access bounds. The setup performs no ADC/SBC; only N/Z change, including
raw B/U/D preservation. The resident proof compares state and effects at every
boundary using frozen arithmetic and audio contracts.

Reproduce with VASM set to the approved vasmm68k_mot and PYTHONPATH to the
inspection dependency directory:

    python port/tests/recovery_test_character_menu_setup.py
    python port/tests/recovery_test_character_menu_setup.py --rom
    python port/tests/recovery_test_resident_character_menu_setup.py

Private ROM is input/rescue-rangers-europe.nes, SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
Existing sources and manifests remain unchanged. No assets, ADFs, index,
branches or publications were changed. This is not live Amiga gameplay or a
stock PAL A1200 memory/speed/display/audio claim. The eventual target remains
2 MiB Chip, optional Fast at most 8 MiB, with Z=B pickup/throw and X=A jump.
