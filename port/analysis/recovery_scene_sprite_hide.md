# Native scene sprite hiding and frame yield

The continuous native recovery now reaches F3D5 before JSR C14E, after the
original sprite-hiding routine and its real one-frame yield. This is newly
derived source and host-only proof, not recovered later playable/audio source,
playable gameplay, audible output, or evidence of Amiga target speed.

## Exact new coverage

The static 68020 helper accepts F3CF and F3D2 only:

- F3CF executes the JSR C21E caller, pushing F3 D1 on the original wrapped
  6502 stack. C21E loads X from RAM97, compares it with 04 and, for X=04,
  writes F8 to OAM0200. It then writes F8 at 0200+X, advancing X by four
  until X wraps to zero. The original RTS reads the actual caller frame and
  returns to F3D2. A=F8, X=00, Y unchanged; N=0, Z=1, C=(initial X>=4),
  and raw V/D/I/B/U preserved. SP returns to its starting value.
- F3D2 pushes F3 D4 and stops at FF04 with A/X/Y/rawP unchanged and SP
  decremented twice. The existing, unchanged FF04 frame-yield helper executes
  next, followed by the genuine scheduler, NMI, video and audio routines.

RAM97 must be divisible by four for F3CF. Otherwise the original INX sequence
never reaches zero, so those inputs reject before any mutation. This is a
bounded translation contract, not a claim to terminate the original infinite
loop. F3D2 imposes no RAM97 restriction. There is no generic opcode interpreter,
new resource access, synthetic return, audio skip or captured-state injection.

A0 points to RAM2048, A1 to context8 (PC.word/A/X/Y/rawP/SP/reserved), A2 to
journal264. Journal records are address.word/value.byte/zero with no header.
D0 returns the store count (3–66 for F3CF, 2 for F3D2), or -1 on inert reject.
D1–D7/A0–A6 are preserved, native stack is balanced and CCR is scratch. Buffers,
code and native stack must be valid and disjoint. Indexed accesses are bounded.

## Continuous proof

One genuine reset and one resident native RAM/context pair, with the frozen
release-one-frame/repress Start input sequence:

- F3CF/50/10/FF/27/BA/A7: 1,668 calls, 56 logical NMIs, 54 audio completions.
- F3D5/00/00/FF/26/BA/A7: 1,693 calls, 57 logical NMIs, 55 audio completions.

Final stack bytes 01B9–01BF are D4 F3 02 02 90 09 C6. The saved bank 02 remains
pending its original later PLA. Mapper is (1E,1F,1F,02,empty), timer is 898,
RAM19 is zero, and all 32 live palette bytes remain 0F. Cumulative effects are
25,379 RAM stores, 4,698 PPU events, 605 mapper writes, 1,026 controller events,
3,457 semantic resource reads and 450 APU writes. Every accepted boundary
compares full RAM/context, ordered effects and journals, mapper state,
resources, ABI registers, canaries and global memory bounds.

Neutral/Right/Left frozen scenarios reproduce 1,219/1,195/1,195 calls at
A06C/A07B/A07B. All four predecessor scene-palette composition scenarios were
also rerun unchanged with their approved 26,986-byte binary/hash. Alternate
live selection at A07B and nonzero-B8 C63B remain unsupported.

## Adversarial proof and identities

The independent declarative test runs 131,072 assembled-native accepted cases:
every raw-status × stack-position pair for each accepted entry, random other
RAM/context bytes, every terminating RAM97 offset for F3CF, and all RAM97
values for F3D2. A separate 131,072-case run compares against the original
private ROM as well. Cases include both stack wrap positions, exact ordered
stores, unchanged journal tails, raw status, full RAM/context, ABI and memory
bounds. All other 65,534 PCs and all 192 nonterminating RAM97 values reject
inertly, totaling 65,726 rejection tests.

The helper assembles to 226 bytes, SHA256
 e88fc3161ff89fdbc605d781cd0a49ede1a0dadba364e21dd324ed611b318e37.
The 59-helper composite is 27,216 bytes, SHA256
 ec548d8df9256ff1774671a43b74f3eb2fafa35ecbbf59f08fd81bcc9cf52ea0.
Execution is host M68EC020, not target hardware.

## Next boundary and reproduction

No instruction at F3D5 executes. Its JSR C14E increments RAMF0, clears RAMFE
and writes zero to PPU2001 to disable rendering. Subsequent F3D8 preparation
and C1BA nametable work, saved-bank restoration, and bank-2 scene loading are
still to be derived. Rendering disable is not claimed in this slice.

Set VASM to the approved vasmm68k_mot and PYTHONPATH to inspection .deps.
Run port/tests/recovery_test_scene_sprite_hide.py normally and with --rom.
Run port/tests/recovery_test_resident_scene_sprite.py with CHARACTER_INPUT
16,0,1,2; run the unchanged recovery_test_resident_scene_palette.py with the
same values for regressions. Private ROM SHA256 is recorded in the manifest.

Only five uniquely named files were added. All 371 pre-existing files in
port/src, port/tests and port/analysis were checked unchanged against a pre-work
snapshot, including the approved predecessor manifest. The manifest records
these frozen dependency hashes. No Git index, commit, branch, publication,
aggregate, README, ADF, old checkpoint or other project was changed. No private
ROM or proprietary assets are included. Later playable/audio source is still
missing.
