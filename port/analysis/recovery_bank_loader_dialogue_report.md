# Authentic interstitial dialogue through stage-loader entry

Additive static native68020 work continues the reviewed911C endpoint through
original bank2 dialogue, its genuine yields, navigation sound and video work,
then restores OAM/object slots and completes the fixed-bank preparation before
C6B5. This is the first continuously established authentic stage-loader entry
in this source line. It is not a completed stage, displayed stage or gameplay.

The generated production code contains native labels and statically resolved
control flow for known routines, not a runtime opcode decoder or general6502
interpreter. Offline generators read the approved private original only to
produce native instruction translations. Game tables/text remain in the
immutable cartridge view and are read semantically at runtime. No captured
state/profile/table bytes drive execution.

## Contract

The usual A0 RAM2048/A1 context8/A2 journal134638/A4 runtime12/A5 PRG131072 ABI
continues. Reserve4096 bytes disjoint native scratch stack. Copied-state preflight
uses2048 temporary RAM bytes plus context and bounded native frames. Native
USER mode, preserved registers/SP, memory bounds and immutable resources are
checked. The original shared RAM/context/resource input must not change during
both passes. Validation resource reads are separate from the committed original
semantic reads and are checked as a complete additional pass.

- ID96: bank2 dialogue92AC–94B5; journal60002. Accepted entries92AC,9475,9478,
  947B,947E. Stage0B only. Genuine external calls return at F379 or FF04; the
  final original RTS reaches911F. Internal JSR/RTS frames are never fabricated.
- ID97: original scheduler with authentic94xx saved-frame checks; journal74.
- ID98: original NMI video prefix admitting finite1C/1D/19 queues in original
  order, then CHR/palette/scroll/timers. Journal134638, sizeFFFF sentinel and
  DMA offset134382, exactly the existing long-video convention. Before visible
  effects, all active scripts must terminate and total at most33500 queue
  events. Unsupported loops/budget fail inertly. Video-skip preserves queued
  requests exactly rather than clearing them.
- ID99: real911C call,911F restore/return, and C60A stage-entry setup through
  C6B5; journal60002. Its semantic resources include the original fixed-bank
  HUD/OAM table. Actual player/character state affects its output.

ID96/99 use a200000-static-instruction per-pass bound and15000 journal records.
Invalid CPU IO resource pointers and exhausted validation bounds reject without
externally observable mutation. These are diagnostic acceptance bounds, not
claims that arbitrary future game data is supported. Earlier nonzeroF6 mapper
restrictions remain unchanged. The new code does not mute or skip audio.

## Final-source evidence

Composite66504 bytes, SHA256
`f76c08628587d9c1a5761946af6a673f8076215a959c0bd417b4e16f80ce4234`.

Three uninterrupted original-first histories begin at FE24 after hardware
warmup and use one native initialization with no successful-state reload:

- Default:12773 calls,360 logical NMIs,2564 ordered APU writes.
- Alternate/right:12934 calls,360 NMIs,2570 APU writes.
- Right then back:13085 calls,361 NMIs,2573 APU writes.

Each releases Start after reaching911C, waits through actual dialogue, then
supplies Start only through original controller sampling when NMI>300 and
NMI modulo120<30. Thus the first requested pulse is at360. No dialogue counter,
input-edge RAM, stack or bank is patched. The final alternate context is
C6B5/2A/28/28/25/BD/A7; the other two are C6B5/8C/28/28/A4/BD/A7. All have
mapper1E/0D/0D/02, stage0 and genuinely preserved F6=0.

Every helper compares complete RAM/context/runtime, original ordered RAM,
device/APU/controller/resource effects, full journal including tails and DMA,
preflight/semantic reads, code/resource immutability, native ABI and bounds.
The three histories also pass13057 mutated-state/event inert rejections.
Logical original-first host execution is not actual keyboard/Amiga timing.

Public static-region tests pass768 raw-status/wrapped-stack JSR cases and65787
inert guards including every unsupported PC, other stage indices and an IO
resource pointer. Private original-instruction slices pass1536 cases. New
combined-NMI public and private suites each pass2048 full-state/effect/journal
cases, including96 inert rejections, all raw statuses and wrapped stack
positions, arbitrary queue scripts, pending requests, DMA and partial mapper
latches. The private slices supplement rather than replace continuous proof.

## Replay and delivery limits

Use approved VASM and machine68k/py65 environment from the baseline restore
recipe. Fresh output commands:

```sh
out=$(mktemp -d port/build/recovery_bank_loader_XXXXXX)
python port/tests/recovery_bank_loader_dialogue_contract.py > "$out/public.log"
python port/tests/recovery_bank_loader_dialogue_nmi_test.py > "$out/nmi.log"
python port/tests/recovery_bank_loader_dialogue_contract.py --rom > "$out/private.log"
python port/tests/recovery_bank_loader_dialogue_nmi_test.py --rom > "$out/private_nmi.log"
python port/tests/recovery_bank_loader_dialogue_rom.py default right move_back > "$out/histories.log"
```

Generators are private offline regeneration tools and require the hash-checked
cartridge; ordinary public tests need neither cartridge nor reference CPU.
Do not publish input ROM/firmware, resource extracts, trace/state logs, disks or
audio. Manifest allowlist contains only this addition, with prior frozen
manifest dependencies. Existing sources, disk and public baselines remain
unchanged. No new on-target allocation, rendering, audible-output or speed
qualification is claimed. Native stage loading afterC6B5 remains separate work.
