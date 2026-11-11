# Native character dispatch and default confirmation

The new static 68020 dispatch reaches original C5F8 after genuine default-character
confirmation, continuing from reset with no RAM/context reload. The default cursor
is independently observed at 28 when A06C is first reached. The test releases Start
for a frame, then presses it through both original and native controller interfaces.
The native path takes 1,196 helper calls, 40 NMIs and 38 later audio completions;
final context is C5F8/F8/00/FF/27/BF/A7. The original A0BB sprite-clear/RTS helper
performs the final handoff. No new gameplay code at C5F8 is translated here.

Four separate reset runs compare every accepted boundary, full 2 KiB RAM, raw
architectural context, ordered effects, journals, resources and mapper state:

- No input: 1,219 calls, 41 NMIs, 39 later audio calls, four A06C visits. Context
  A06C/FF/FF/FF/A4/BD/A7 demonstrates three additional completed idle frames.
- Default confirmation: 1,196 calls, 40 NMIs, 38 later audio calls, C5F8 handoff.
- Right input 01: 1,195 calls, 40 NMIs, A07B/01/FF/01/24/BD/A7.
- Left input 02: 1,195 calls, 40 NMIs, A07B/00/FF/00/26/BD/A7.

All end with mapper (1E,1F,1F,02,empty), timer898 and genuinely consumed RAM19.
Controller two remains neutral in these resident scenarios. This is not proof of
two-player gameplay or successful alternate-character selection.

## Original control flow and precise remaining boundary

A06C tests the Start edge in RAM14 before directions. Start compares cursor RAM0203
against 28. Equal branches directly to A0BB. Otherwise A093–A0B8 swaps fifteen
pairs at RAM0340–035D using actual PHA/PLA traffic, then writes 8D,8A,95,8E at
RAM05A2/05A4/05A6/05A8 before A0BB. That complete alternate-confirm branch is
isolated-ROM tested, but is not claimed as reached continuously from reset.

No direction and no Start pushes original A088 and yields at FF04. The existing
scheduler returns to A089, whose JMP resumes A06C. Directions compute Y=RAM14&1
and stop immediately before A07B's bank-2 resource read at A0E1+Y. The ROM table
contains cursor values 28 and 88. Subsequent instructions write RAM0203, load sound
27 and JSR F379. F379 conditionally enqueues into the existing sound ring, with
STA DA only when the slot contains 88. Neither this resource-read continuation nor
that sound-queue helper is supplied by this change. No cursor is invented and no
sound queue is cleared or bypassed. This is the exact next dependency, not a tool
or permissions failure. There is no request to execute untranslated native code.

## Native contract and checks

A0 points to RAM2048; A1 to context8 (PC.word,A,X,Y,rawP,SP,reserved); A2 to an
ordered store journal196. Each four-byte record is address.word,value.byte,zero.
D0 returns store count, or -1 for unsupported PC. Only A06C and A089 are accepted.
D1–D7/A0–A6 are preserved, native stack balanced, CCR scratch. Inputs, code,
journal and native stack must be valid and disjoint, with authentic bank2 mapping.
The maximum 49 records are 45 PHA/pair stores plus four character-byte stores.
A089 needs no records and preserves every context field except PC.

All 256 raw status values, stack wraps, arbitrary cursor bytes, input combinations,
Start priority and invalid entries are exercised. CMP updates N/Z/C while preserving
V and raw D; no ADC/SBC is present and no decimal arithmetic is introduced. JSR
writes the authentic wrapped high/low return bytes. The isolated oracle uses the
existing Ricoh binary-arithmetic CPU. It runs 8,192 original-ROM cases; independent
ROM-free model/native testing runs 8,192 cases plus all 65,534 unsupported PCs,
which reject without RAM/context/journal mutation. Journals and untouched tails,
all RAM writes, ABI, canaries and global memory bounds are checked.

The new resident composition is a separate file derived from the frozen queue
proof. Its 134,638-byte queue journal stays at host 40000, below native stack
1F0000 and disjoint from bank resources at 20000/28000/30000. Every original
NMI, pending video operation, audio call, RTI and scheduler step is retained.
The composite is 26,462 bytes with SHA256
 d549ec990c024fc2ede3a3d1a8cfd5e89f61c601391f79903b666a49a05a7413.

## Reproduction and scope

Set VASM to the approved vasmm68k_mot and PYTHONPATH to the inspection .deps.
Run recovery_test_character_selection_dispatch.py with and without --rom, then
recovery_test_resident_character_selection.py with CHARACTER_INPUT=0,16,1,2.
The existing recovery_test_resident_character_video_queue.py also passes unchanged.
The private original ROM SHA256 is
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.

Only four new files plus their manifest are added. The prior queue manifest
2bfa8bdd6ff601e7af3e67d9c898a3ca7d8cbd163928472525a58f53f21c0581 and
all its covered files retain their hashes. No prior files, index, branches,
commits, assets, ADFs or publications are changed. This is new early-recovery
host M68EC020 work, not recovered later gameplay/audio source, playable gameplay,
audible output or PAL A1200 performance evidence. The target remains 2 MiB Chip,
optional Fast at most 8 MiB, Z=B pickup/throw and X=A jump.
