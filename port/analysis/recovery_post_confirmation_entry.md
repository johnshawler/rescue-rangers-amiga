# Native post-confirmation scene entry

The default character-confirmation path now continues from its genuine C5F8
handoff to C274, before scene-entry palette fading. This is a bounded new static
68020 game-code translation, not recovered later gameplay source. It adds three
native helper calls and eight original ordered RAM writes to the frozen proof.

## Continuous execution evidence

One reset, one resident native RAM/context pair, no captured-state injection:

- C5F8/F8/00/FF/27/BF/A7 after 1,196 calls. RAM B8 is genuinely zero.
- 9000/0B/00/FF/25/BD/A7 after 1,197 calls. RAM31 becomes 0B and the
  original JSR return C609 is pushed high then low.
- F3C9/0B/00/FF/25/BB/A7 after 1,198 calls. Original return 9002 is pushed.
- C274/02/00/FF/25/B8/A7 after 1,199 calls. The genuine RAMF1 value 02 is
  saved with PHA, then original JSR return F3CE is pushed high then low.

The final stack bytes at 01B9–01BF are CE F3 02 02 90 09 C6. These are checked
against the continuous original-ROM execution, not injected into either machine.
The sequence retains 40 NMIs, 38 later audio completions, all video operations,
controller reads, RTIs and scheduler steps. Final mapper is
(1E,1F,1F,02,empty); timer is 898 and RAM19 is zero. Total observed effects:
18,710 RAM writes, 4,372 PPU events, 435 mapper writes, 720 controller events,
2,553 semantic resource reads and 298 APU writes.

The unchanged release-one-frame/repress Start procedure is retained. Other new
composition runs reproduce the frozen boundaries exactly:

- Neutral: 1,219 calls, 41 NMIs, 39 audio completions, A06C/FF/FF/FF/A4/BD/A7.
- Right: 1,195 calls, 40 NMIs, 38 audio completions, A07B/01/FF/01/24/BD/A7.
- Left: 1,195 calls, 40 NMIs, 38 audio completions, A07B/00/FF/00/26/BD/A7.

All four frozen character-selection scenarios were also rerun successfully.
Alternate live selection remains unproved; A07B still needs its resource/SFX work.

## Contract and isolated verification

Only C5F8, bank-2 9000 and fixed F3C9 are accepted. C5F8 with nonzero RAMB8
loads RAMBD, writes RAM31, and performs original C60E JSR to C63B. That branch
is covered by isolated original-ROM tests, not claimed as reached from reset.
C60A and other continuations remain unsupported.

A0 points to RAM2048; A1 to eight-byte PC.word/A/X/Y/rawP/SP/reserved;
A2 to a 12-byte ordered store journal. Each record is address.word/value.byte/zero.
D0 returns 2 or 3 stores, or -1 for an unsupported entry before any mutation.
D1–D7/A0–A6 are preserved; native stack is balanced; native CCR is scratch.
Buffers, code and native stack must be valid and disjoint; bank-2 mapping is a
caller precondition for 9000. No indexed resource access or variable bound is
introduced. All 65,533 unsupported PCs reject inertly, including untouched journal.

Independent declarative contracts and assembled native execution cover 8,192
cases, including all 256 raw status values, every stack position, wraparound,
both C5F8 branches and arbitrary saved-bank bytes. Another 8,192 cases compare
the native helper and independent model with the private original-ROM oracle.
LDA changes only N/Z; JSR/PHA preserve raw status. Every full RAM/context result,
ordered write, journal tail, ABI register, canary and global memory bound is
checked. The resident test also compares all resources and mapper state at every
accepted boundary, retaining predecessor semantic-effect journals.

The 57-helper composite is 26,744 bytes, SHA256
0d5a8b0c8c90024b0f8d28955b56eac1fc6a3575ec0dda7fb834793323733218.
This test uses host M68EC020, not a stock Amiga timing claim.

## Exact next boundary

C274 starts the scene-transition palette-fade setup: initialize fade controls,
copy the current palette and attenuate it before yielding through C2A5. A prior
C700-specific helper includes this logic, but its entry and nested caller stack
are different. It is deliberately not invoked with a fabricated PC/return chain.
A future bounded continuation must add an authentic C274 entry and compose the
existing frame/audio/scheduler/fade paths, eventually returning to F3CF.
C63B remains the independent nonzero-B8 branch boundary. No next-boundary
instruction is executed by this new native helper.

## Reproduction and preservation

Set VASM to the approved vasmm68k_mot and PYTHONPATH to the inspection .deps.
Run port/tests/recovery_test_post_confirmation_entry.py with and without --rom.
Run port/tests/recovery_test_resident_post_confirmation.py with CHARACTER_INPUT
0,16,1,2. The private ROM hash remains
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.

This work adds only its source, two tests, this report and its manifest. It did
not edit predecessor helpers/manifests, README, aggregate scripts, Git index,
commits, checkpoint or ADF, and did not publish. The frozen character-selection
manifest and all four of its covered files still match their recorded hashes.
Concurrent unrelated music work is outside this slice and its dependency manifest.

No proprietary ROM, firmware or assets are included in these new source files.
This is scene-entry control-flow recovery, not playable gameplay, audible output,
or target performance evidence. Later playable/audio source remains missing.
