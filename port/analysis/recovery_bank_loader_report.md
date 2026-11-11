# Native bank restoration and interstitial resource preparation

New static 68020 code extends the real menu/scene chain from FF53 through
bank2 resource loading, OAM backup, palette/CHR requests, rendering enable and
fade-in to F392. It does not complete the interstitial, stage loader or gameplay.
No later lost source is recovered. No existing source or delivered disk changed.

## ABI and exact scope

`recovery_bank_loader_dispatch` prepends the frozen scene dispatcher. The ABI
remains RAM2048 A0, context8 A1, journal134638 A2, runtime12 A4 and immutable
PRG131072 A5. Native scratch stack remains at least1KiB. All registers except
D0 and host flags are preserved; execution is USER-mode safe. No CPU interpreter,
profile schedule, captured RAM or synthetic original stack enters production.

Helper IDs/journal byte sizes:

- 79/22: FF53 original five mapper writes and wrapped RTS, F6=0 only.
- 80/6: 9003 OAM/object backup and actual first resource-loader JSR.
- 81/32770: original bank2 8000 loader, live X and original RTS destination.
- 82/0: 9034 second loader call with original X=8 and JSR frame.
- 83/154: 9039/9041 index0B palette/CHR/OAM preparation to F3E5.
- 84/6: F3E5 actual render-enable and yield setup.
- 85/0: F3EE fade-in entry with actual F3F0 return frame.
- 86/0: frozen fade continuation, selected by actual F3F0 enclosing frame.
- 87/74: frozen scheduler, selected by actual F3ED saved frame.
- 88/0: F3F1 saved-bank PLA to FF53.
- 89/0: 910C index0B continuation to F392.

RAM-only helpers use private scratch rather than publish a fictitious device
journal. Existing completed-RTI IDs do not change. No new target adapter or
on-target timing is claimed here.

Generalized loader81 preserves live X, original semantic table/stream reads,
all page-one stores, signed-count behavior and Y/page progression. Before any
mutation it validates the complete stream remains within its immutable16KiB
bank and uses at most4094 bytes including terminator. Its journal distinguishes
resource reads(kind0), PPU writes(kind1) and discarded PPU status reads(kind2).
Resource validation reads are not original semantic reads and are checked
separately. No resource bytes are embedded in these public files.

Standalone restore79 supports every raw status and wrapped stack. The wrapper
qualifies only bank2 mode1E, empty serial latch, task0/canonical physical flags
and requested bank2. F6 nonzero rejects inertly; it is never cleared or muted.
The accepted F6=0 state arises in uninterrupted original-first histories, not a
patch. A separate original-only investigation shows a busy interrupt can create
F6=1: that is an explicitly unsupported interleaving, not evidence the branch
may be ignored. Native dispatch has no asynchronous interrupt inside a helper.

Prefix80 rejects SP<2B before mutation because OAM backup can overwrite the
8D0A return frame there. The genuine entry has SP=BD. This conservative guard
is deliberate rather than silently assuming the copied bytes. Assets83 and
tail89 support actual stage index0B only. Other stage/demo paths remain bounded.

## Final-source proof

Composite:50,166 bytes, SHA256
`4d4aa6a3bc1688dcb33c5cfb02891fb18b34919e6d731bb590c96ea6ded00976`.
Three continuous original-first histories start at FE24 after hardware warmup:

- Default:2,212 helper calls,77 logical NMIs,597 ordered APU writes.
- Right/alternate:3,410 calls,112 NMIs,863 APU writes.
- Right then back:4,790 calls,152 NMIs,1,216 APU writes.

All end at F392/08/F0/FF/25/B9/A7 with mapper1E/0D/0D/02, and qualify real
character markers, cursor and table state. Every boundary compares full RAM,
context, runtime mapper, ordered RAM/device/APU/controller/resource effects,
semantic native resource reads, complete poisoned/zero journal tails, preserved
registers/SP, memory bounds and immutable code/resources. The three runs also
pass3,704 mutated-state/event inert rejections. Full host effects evidence is
not exhaustive on-target journaling or actual keyboard timing.

Standalone public and private original-instruction cases each cover1,493
successful complete-state/effects cases across raw status and stack positions.
Public cases also cover562 inert guards including invalid stream pointers and
bounds; private cases cover555 guards. The public generalized-loader cases
cover all256 signed counts and page crossings. Separate composite guards and
fade-entry tests supplement these; consult their retained command output.

Exact current unsupported boundary:F392, before bank5 sprite preparation.
No interstitial dialogue, later stage resources, scrolling, collision, input
response during play or playable stage is claimed. Existing bounded Paula
output and stock2MiB performance limits remain unchanged until target testing.

## Restore and independent replay

Use fresh output directories; no command below overwrites existing captures:

```sh
export VASM=/workspace/scratch/43ecf79622a5/amiga-recovery-tools/vscode-amiga-debug/bin/linux/vasmm68k_mot
export PYTHONPATH=/workspace/scratch/43ecf79622a5/rescue-recovery-inspection/.deps
export PYTHONDONTWRITEBYTECODE=1
out=$(mktemp -d port/build/recovery_bank_loader_XXXXXX)
python port/tests/recovery_bank_loader_contract.py > "$out/public.log"
python port/tests/recovery_bank_loader_guards.py > "$out/guards.log"
# Private approved cartridge required below:
python port/tests/recovery_bank_loader_contract.py --rom > "$out/private.log"
python port/tests/recovery_bank_loader_guards.py --rom > "$out/private_guards.log"
python port/tests/recovery_bank_loader_rom.py default right move_back > "$out/histories.log"
```

Private cartridge SHA256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
No cartridge, firmware, generated assets/state/traces/audio/disks belong in a
publication. The source manifest lists the exact public addition allowlist and
frozen dependency hashes. No Git index, commit or publication is performed.
