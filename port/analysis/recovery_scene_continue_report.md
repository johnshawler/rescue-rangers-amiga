# Native scene preparation with active sound

New static 68020 work continues the authentic F3D5 boundary through render
disable and nametable clearing to FF53. An additive state-selected dispatcher
joins it to the unchanged active-SFX startup/menu runtime, including both actual
character choices. No later lost gameplay/audio source is recovered here.
This is host semantic evidence, not stage loading completion, gameplay, target
speed, audible qualification or a new development disk.

## Exact boundary and effects

`recovery_scene_continue_prepare` accepts F3D5 only. It executes the original
JSR C14E, incrementing F0, setting FE=0 and publishing PPU2001=0. It executes
F3D8's A=20/X=0/Y=0 preparation and JSR C1BA, including its status read,
PPUCTRL write, 1,024 zero nametable writes and 64 zero attribute writes. It
then executes the original PLA of the saved bank and stops before FF53.
The two JSR frames leave their actual original page-one stores; no captured
stack or fabricated entry state is installed. The final bank value comes from
the live wrapped stack. The helper neither writes F6 nor performs mapper or
APU work. FF53's bank publication and possible deferred audio remain unsupported.

A0 is RAM2048; A1 is context8 (PC.word/A/X/Y/rawP/SP/reserved); A2 is a
4,382-byte journal. The journal contains count.word=1095, then ordered
address.word/value.byte/kind.byte PPU records. The unused status-read value is
zero and kind=0; writes use kind=1. D0 returns 1 or -1 on inert rejection.
D1-D7/A0-A6 and native SP are preserved. Code, buffers and stack must be valid,
aligned where necessary, and disjoint. All RAM indexing stays within 2 KiB.
Raw D/I/B/U are preserved; final N/Z follow PLA, C/V are clear.

## Active-SFX composition and integration ABI

`recovery_scene_continue_dispatch` falls through to the unchanged
`recovery_state_menu_sfx`, and uses its existing RAM/context/runtime12,
immutable PRG131072, journal134638 and at-least-1-KiB scratch-stack ABI.
Selection uses live PC, mapper and RAM, never diagnostics or a recorded schedule.
The runtime magic remains D501. The helper IDs are:

- 73: existing post-confirmation entry, zero external journal.
- 74: existing scene palette entry, zero external journal.
- 75: existing sprite hide/yield entry, zero external journal.
- 76: existing fade continuation with actual enclosing F3CE return frame,
  zero external journal.
- 77: existing scheduler resuming the actual F3D4 saved frame, 74-byte
  controller journal.
- 78: new preparation helper, 4,382-byte PPU journal.

ID72 is reserved for the separate live-title worker. It is not implemented or
validated by this module. No completed-RTI IDs change. RAM-only helpers use
private native scratch; no external journal is changed for those calls. All
new paths require canonical physical status, bank2/mode1E, empty mapper latch,
no injected NMI event and the existing task-zero contracts. Unsupported branches
reject before externally visible mutation. Existing idle/NMI/music/SFX processing
continues normally during all 17 scene yields. No sound is muted or skipped.

To integrate, prepend the new dispatcher and append its four source dependencies
listed by `recovery_scene_continue_harness.SOURCES`, then call the new entry
instead of the frozen SFX entry. Keep the complete long journal, use the helper
IDs above for journal interpretation, and stop at FF53. A live title wrapper can
fall through to this wrapper. This report does not claim that target integration
has been performed. The live-title code and its own ID72 need separate review.

## Proof

The final user-mode M68EC020 composite is 47,894 bytes, SHA256
`4caa9b1c3a472f33b20636b43302eb3439bfd35faa137d3d4469c89716413fff`.
The new preparation helper is 246 bytes, SHA256
`2437bed5022a70cee51695fe2479575c07629105eacf44166a5ba44cb7b4c7af`.

Three original-first continuous runs begin at FE24 after hardware warmup with
one resident native RAM/context initialization. No successful-state reload or
captured trace drives the native code:

- Default character: 1,726 calls, 60 logical NMIs, 474 ordered APU writes.
- Right/alternate character: 2,891 calls, 95 NMIs, 709 APU writes.
- Move right then back: 4,266 calls, 135 NMIs, 1,067 APU writes.

All end at context FF53/02/00/00/24/BB/A7 with mapper (1E,1F,1F,02,empty).
They compare complete RAM and context at every boundary, ordered RAM/device
and resource effects, full journals including poisoned/zero tails, mapper
state, resource reads, preserved registers, canaries, global memory bounds and
user-mode execution. Original and alternate selection include real cursor,
table and character-marker checks. The three histories also reject 3,174
mutated runtime/input cases inertly. These are scripted logical input histories,
not live Amiga keyboard tests.

The standalone public contract checks 2,048 assembled-native cases covering all
raw statuses and stack positions, plus all 65,535 other PCs rejecting inertly.
A separate private 2,048-case run compares the real original instructions.
The wrapper contract checks 107 inert guards and 256 user-mode preparation
cases covering all stack positions and every F6 value, including preservation
of nonzero deferred-audio state. This does not implement deferred audio.

## Restore and test

Use the toolchain and pinned Python environment already used by the SFX tests:

```sh
export VASM=/workspace/scratch/43ecf79622a5/amiga-recovery-tools/vscode-amiga-debug/bin/linux/vasmm68k_mot
export PYTHONPATH=/workspace/scratch/43ecf79622a5/rescue-recovery-inspection/.deps
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_scene_continue_prepare_test.py
python port/tests/recovery_scene_continue_contract.py
# Private cartridge required only below:
python port/tests/recovery_scene_continue_prepare_test.py --rom
python port/tests/recovery_scene_continue_rom.py default right move_back
```

The private input is `input/rescue-rangers-europe.nes`, SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Never publish it, generated resources, full execution reports, captured state or
traces. For retained logs use `mktemp -d port/build/recovery_scene_continue_XXXXXX`
and redirect each command to a fresh filename. The tests assemble only into
new temporary directories; they never overwrite old captures or build disks.
The manifest records the explicit public source allowlist and dependency hashes.

Only uniquely named recovery_scene_continue files were added. No existing source,
README, aggregate, Git index, commit, publication, emulator session or delivered
Z/X ADF was changed by this work. No ROM, firmware or game assets are in these
public files. No additional Fast RAM requirement is introduced; actual stock
A1200 allocation/performance is unmeasured and remains a separate qualification.

The next authentic boundary is FF53, then the bank2 return at 9003 and scene
resource work through 8D0A. Supporting F6=0 must be based on genuine state;
nonzero F6 requires its actual deferred-audio path or an explicit inert stop.
First stage and playable frame work remain substantially beyond this slice.
