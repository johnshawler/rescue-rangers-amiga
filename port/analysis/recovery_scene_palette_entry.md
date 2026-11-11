# Native scene-entry palette fade

Newly derived static 68020 translation now takes the authentic C274 scene entry
through the complete fade-out and returns to F3CF, with the original nested
caller stack. This is source recovery progress, not recovered later playable or
audio source, playable gameplay, audible output, or target-speed evidence.

## Exact coverage

The new helper accepts only C274 and stops at C2A5 before its JSR. It writes
fade controls 0F=10, 0D=10, 9A=00, 0E=04; copies 32 palette bytes from 0320–033F
to 0300–031F in descending order; subtracts 10 from every copied byte using
Ricoh binary SBC semantics, clamping negative results to 0F; stores FF to 18;
and pushes delay 04 on the original wrapped stack. There are exactly 70 ordered
RAM stores. No new hardware or resource access is introduced by this entry.
The preceding F3CE return remains on the stack, rather than being fabricated.

The existing unchanged C2A8 fade continuation, C2A5 frame yield, task scheduler,
NMI, video and audio helpers then run normally. The scene-only continuation
samples are 10 three times, 20 four times, 30 four times, 40 four times, and
50 once; the final sample returns through the genuine RTS to F3CF. Sixteen
logical NMIs and sixteen audio completions occur during this scene fade.

## Continuous original-ROM and assembled native proof

One reset, one resident native RAM/context pair, no state reload or captured
state injection. The frozen release-one-frame/repress Start procedure remains:

- C274/02/00/FF/25/B8/A7 at 1,199 native calls, 40 NMIs, 38 audio completions.
- F3CF/50/10/FF/27/BA/A7 at 1,668 calls, 56 NMIs, 54 audio completions.

All 32 live palette bytes end at 0F. Stack bytes 01B9–01BF retain
CE F3 02 02 90 09 C6, with SP now BA and the saved bank 02 still pending its
later PLA. The mapper remains (1E,1F,1F,02,empty), RAM19 is zero and timer is
898. Cumulative effects: 25,025 RAM writes, 4,688 PPU events, 595 mapper writes,
1,008 controller events, 3,420 semantic resource reads and 444 APU writes.
Every accepted boundary compares the complete RAM, architectural context,
ordered effects, journals, resources, mapper state, ABI and memory bounds.

The new composition also reproduces the frozen neutral/Right/Left boundaries:
1,219/1,195/1,195 calls respectively, at A06C/A07B/A07B. All four original
post-confirmation composition scenarios were separately rerun and pass with the
unchanged 26,744-byte predecessor composite and its approved SHA256.
Alternate live selection is still unsupported at A07B, not proved by isolated
entry cases. Nonzero-B8's C63B path remains outside this slice.

## Native contract and adversarial verification

A0 points to valid RAM2048, A1 to context8 (PC.word/A/X/Y/rawP/SP/reserved),
A2 to a valid 280-byte journal. Each of 70 journal records is
address.word/value.byte/zero. D0 returns 70, or -1 on unsupported PC with no
mutation. D1–D7/A0–A6 are preserved, native stack is balanced and CCR is scratch.
Code, buffers and native stack must be valid and disjoint. All indexed access is
constant-bounded; every one of the other 65,535 PCs rejects inertly, including
an untouched journal. Raw status preserves D/I/B/U, binary SBC computes C/V,
and final LDA 04 supplies N/Z. No opcode interpreter or substituted return exists.

Independent declarative contracts test 8,192 assembled-native cases. A separate
8,192-case run also compares the original private ROM, including all 256 raw
status values, all stack positions and wraparound, all final palette operands,
random other palette/RAM/context bytes, every ordered store, ABI registers,
canaries and global memory bounds. Decimal-set inputs use the existing explicit
Ricoh binary oracle. These are isolated adversarial cases, not live menu claims.

The entry assembles to 238 bytes, SHA256
0b35f83dbcef5defd5d50c3212a4dac9eb740be37b2a027b74ccf9c8e55e35d9.
The 58-helper composite is 26,986 bytes, SHA256
29dd307aeb83a5c618239cc925a02f1b3d88e852686f13fc23d1f32201c33196.
Execution uses host M68EC020, not Amiga timing or audio-output validation.

## Remaining boundary and reproduction

No instruction at F3CF is executed: its JSR C21E begins the sprite-hiding
routine using RAM97 and OAM 0200. Further scene preparation, yields, saved-bank
restoration and bank-2 scene loading remain to be derived with genuine control
flow. The new scope deliberately stops at that unsupported boundary.

Set VASM to the approved vasmm68k_mot and PYTHONPATH to inspection .deps.
Run port/tests/recovery_test_scene_palette_entry.py both normally and --rom.
Run port/tests/recovery_test_resident_scene_palette.py with CHARACTER_INPUT
16,0,1,2. Rerun port/tests/recovery_test_resident_post_confirmation.py with the
same four inputs for frozen regressions.

Only five uniquely named source/test/report/manifest files were added. All
pre-existing source, test and analysis files were checked byte-for-byte against
a pre-work snapshot; the approved predecessor manifest and its four files also
remain unchanged. No Git index, commits, publication, aggregate scripts, README,
ADF, old checkpoint or other projects were changed. No proprietary ROM or
assets are included. Later playable/audio source remains missing.
