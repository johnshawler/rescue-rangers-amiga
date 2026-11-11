# Additive native stage-map expansion

This source-only module translates fixed-bank stage-map initialization, not a
6502 interpreter or captured-effects player. It does not publish or launch an
emulator. Frozen sources, input cartridge, existing build outputs, delivered disk
and other projects remain unchanged. Parent integration and independent review
are separate work.

## Scope and control-flow contract

Helper ID 100 is reserved for `recovery_stage_map_region`. The static generator
covers C235–C246 (object reset), DBEC–DD09 (map/queue expansion), DF8A–E046
(metatile expansion and pointer construction), E06B–E095 (map-row pointer), and
E179–E1EA (stage-map orchestration). No instruction or asset bytes are embedded.
Generation privately checks the approved cartridge SHA256. The committed native
source is directly assemblable without a cartridge or Python dependency.

Admitted original PCs: E179, E17C, E1D3, E1E4, E1E7, E1EA, DBEC, DC5C, DC5F,
DF97 and E028. Calls within scope execute natively with original 6502 stack
pushes/pops. Calls outside scope exit with the original target PC and pushed
return address, not a manufactured return:

- E179 calls C14E; its next entry is E17C.
- E025 calls FF53; its next entry is E028.
- DF94 calls FF53; its next entry is DF97.
- DBEC's direct-video tail jumps to C115. The authentic caller return is E1D3
  on the tested stage initialization route. The original stack remains intact.
- E1E1 calls FF53; its next entry is E1E4.
- E1E4/E1E7 call bank 4:8040/8090; reentries are E1E7/E1EA.
- An RTS to a PC outside the statically translated return-site set exits at that
  exact PC. The tested outer return is E106.

C14E/C115/FF53 and bank 4 object preparation are explicit dependencies. Neither
F5 nor F6 is cleared or altered to permit mapper reuse. The mapper dependency
must handle or reject nonzero deferred-audio state honestly. The map module
contains no interrupt scheduling, NMI, audio, PPU or mapper shortcuts.

## Memory, journal and resources

A0 points to 2048 RAM bytes; A1 to the eight-byte original context
(PC big-endian word, A, X, Y, raw P, SP, reserved); A2 to a 60002-byte counted
journal; A4 to the common 12-byte runtime/mapper record; A5 to immutable 131072
PRG bytes. The larger shared journal allocation is sufficient. Runtime byte 0
must be 1E, mapped bank byte 3 must be below 8, serial-state word 4 must be zero,
and magic word 10 must be D501. Runtime metadata is not changed by this module.

Journal records are big-endian CPU address word, value byte, kind byte 0. They
represent semantic PRG data reads only, in order, with a leading word count and
15000-record limit. RAM writes are real byte writes, observed separately by the
common test journal adapter. The module does not truncate or suppress effects.
No special 65535 journal-size sentinel is required for helper 100.

Fixed C000–FFFF reads resolve to PRG bank 7; mapped 8000–BFFF reads resolve using
runtime bank 3. Each CPU address is masked to its actual 16-bit width. RAM
0000–1FFF mirrors to 000–7FF. IO reads/writes are rejected; the direct-video
consumer must execute in its own helper. Every external resource offset is
bounded by the guarded bank and CPU address ranges. All native memory tracing
checks the full access width, not only its starting address.

The expansion reads fixed orientation/mask/step tables at DD12–DD19,
E04F–E05A, E05B–E06A; stage row indices through ($32),Y; map cells through
($26),Y; four-byte metatile definitions through ($00),Y; attributes from BEE0,X;
and tile quadrants from BAE0/BBE0/BCE0/BDE0,X. These are live immutable resource
reads, never embedded table contents. E01B requests bank 0 or 1 according to
stage resource bank, then DF8A requests the stage's bank in RAM36. On the tested
first-stage route those resource selections use bank 0.

RAM effects include original zero-page traversal and pointer state, wrapped
6502 stack bytes, temporary tile quadrants 0140–014F, video queue packets in
0360 onward with their original FF terminator, metatile/collision data at
0600 onward, attribute cache at 0780 onward, object initialization arrays, and
stage/scroll bookkeeping. DBEC preserves the original F0-dependent direct-video
versus queued path. Parent video consumption must preserve the generated queue
and original PPU writes. This module generates authentic data, not images.

## Atomic rejection and execution cost

D0=1 means completed slice; D0=-1 means inert public rejection. D1–D7,
A0–A6 and native SP are preserved. Raw original flags, including noncanonical
bits, and byte-wrapping original SP are retained. Arithmetic is binary 2A03
arithmetic regardless of raw decimal flag. Target execution stays in USER mode.

Each accepted call first copies RAM/context into 2060 bytes of native stack,
then validates the exact native logic with a bounded 200000-operation budget
and journal count. The second pass publishes real RAM/context/journal effects.
Resources, RAM/context and mapper metadata must remain unchanged between passes;
interrupting writers are not allowed. Buffers/code/resources/stack must be
mutually disjoint. At least 2304 native stack bytes are required, within the
current dedicated 4096-byte allocation. Scratch writes never touch caller RAM
or journal. A failed preflight returns -1 without changing caller data. Resource
reads on a rejected validation may still occur; they are immutable, not effects.

This doubles logic execution and semantic resource reads. It is a correctness
checkpoint, not an optimization, target-speed result or claim of full PAL FPS.

## Validation and reproduction

Set VASM to the approved vasmm68k_mot executable, PYTHONDONTWRITEBYTECODE=1 and
PYTHONPATH to the private py65/machine68k dependency directory. From repo root:

    python port/tests/recovery_stage_map_test.py
    python port/tests/recovery_stage_map_test.py --rom

The public run assembles the source, rejects all 65525 nonentry PCs, checks 256
raw-flag/stack-wrap JSR cases, unsupported IO atomic rejection and mapper/control/
serial/magic rejection. Every native call checks USER mode, register preservation,
full-width memory bounds, guard bytes and code/resource immutability.

The private run starts the original reference continuously at FE24 using the
established reset assumptions, then menu/controller Start input, dialogue and
stage setup to E179 at logical NMI377. Every fixture is a genuinely reached
original entry, never a manually patched stage. It compares 421 complete native
slices through E106: all RAM, raw context, ordered RAM/resource effects, twice
all semantic resource reads (preflight and commit), journal tail preservation,
and the guards above. This includes 144 DBEC expansions, 6042 semantic resource
reads total and at most 41 journal records in one accepted slice.

This is standalone genuine-entry differential coverage. Original-only execution
runs dependencies between slices; those states are host test fixtures only.
It does not demonstrate whole-native reachability or target integration. The
parent must run its persistent native chain and compare actual dependency
composition. The reference uses logical idle NMIs and an ordered CPU-bus journal,
not PPU hardware timing, audio fidelity, raster proof or game-frame-rate proof.

## Source-only allowlist and restore

Only these additive files belong to this module:

- port/src/recovery_stage_map_region.s
- port/tools/recovery_stage_map_generate.py
- port/tests/recovery_stage_map_test.py
- port/analysis/recovery_stage_map_report.md
- port/analysis/recovery_stage_map_manifest.sha256

Do not publish input ROMs, generated binaries, trace snapshots or private build
files. To restore this work, remove only these five files (and parent-owned
integration references if later added); do not reset/clean the shared checkout.
To regenerate the assembly privately, run recovery_stage_map_generate.py and
verify deterministic output, then rerun both test modes. The baseline identities
provided for this task are public9b4f5d81/localbf7807e; other workers' additive
extensions in the shared checkout are not changed by this module.
