# Resident native reset through startup fade

`recovery_test_resident_startup_fade.py` now proves a complete **host-native
resident reset-to-C597 sequence**. It starts from authored reset inputs (2KiB RAM
filled A5 and FE24/17/33/00/24/FD/A7 context), not captured cartridge state.
The native RAM/context pair is loaded exactly once, before the first helper.
Every subsequent mutation comes from executed static68020 helpers. The reference
runs its own actual-ROM execution continuously from the same authored inputs.
No reference output is copied back to native RAM or context at any boundary.

## Verified outcome

- 533 native helper calls, beginning with the existing68-call reset/initial-music
  sequence and continuing through every remaining startup fade yield.
- 18 real reference NMIs: two initial NMIs and16 further active-audio NMIs.
- All16 later music calls complete, with100 APU writes during the fade,114 total
  including reset and initial music setup.
- Complete ordered totals:8,217 RAM writes;2,525 PPU events;200 mapper writes;
  324 controller events;784 semantic resource reads;114 APU writes.
-17 fade/outer-yield continuations; fade values10,20,30,40,50. Every wait uses
  the real scheduler's no-ready scan to FE90, a real NMI, timer-driven readiness,
  mapper handoffs, active audio, original frame restoration and scheduler resume.
- Final native context: C597,A10,X10,YFF,P24,SPBF,reservedA7 (hex).
  Mapper:control1E,CHR0=00,CHR1=10,PRG06,empty serial latch.
- Every helper boundary compares all2KiB RAM, all8 context bytes, ordered original
  RAM/resource/PPU/controller/APU/mapper effects and full journal buffers. DMA
  snapshots are compared at publication, with original page-two bytes intact.
- Original NMI frame bytes and original RTI raw status are independently checked.
  Raw reference P is never changed. The explicitly named architectural status
  view is comparison-only; virtual B is cleared and U set for native context.
- ABI registers, native stack, buffer guards, immutable bank3 view and global
  native access whitelists are checked throughout. New audio helper resource
  reads are compared with independent domain models, including preflight reads.
- No controller button is pressed in this end-to-end case. Broader standalone
  helper tests cover arbitrary states and registers; this is not an assertion
  that all input sequences or all reachable game states are implemented.

The composite includes40 distinct helpers. VASM `-m68020` output is21,468 bytes,
SHA256a52ba0c5da9188eb1a5df40bc24eaa67e20978181beb950202c22c52464da5eb.
It executes in machine68k M68EC020. This is not an Amiga disk or target diagnostic.

## Empty-command queue entry

The repeated NMI path naturally reaches C0BF with no queued audio command. The
older nonempty queue helper correctly rejects that state. New
`recovery_music_empty_queue_entry.s` translates the real empty branch rather
than bypassing its guard or manufacturing a command:

- A0→RAM2048,A1→context8,A2→mapper journal22. EntryPC=C0BF.
- Requires F5=0,DB<8 and DC[DB]=88. All other inputs, including all incoming P
  bytes, are accepted. Pending/invalid states reject before any mutation.
- Five ordered FFF0 writes03,01,00,00,00 with live F5 metadata establish bank3
  through the caller's persistent MMC1 state. RAM and original stack unchanged.
- Exits C0F6,A88,X=DB,Y/SP/reserved unchanged,P=(incomingP&7C)|03.
- D0=1 or -1 inert rejection. All other native registers preserved. Native stack
  balanced; CCR scratch; buffers valid/disjoint/exclusive as for other helpers.
-2048 ROM-free accepted cases,2048 independent actual-ROM cases and66,300 inert
  guards passed. The public suite needs no cartridge or py65; `--rom` adds the
  independent original execution. Full RAM/context/ordered mapper effects,
  journal, resources, ABI and access bounds are checked.
- Assembled104 bytes, SHA256
  cb3678d6a3e5a9ab63f38f3dea7fcbfad3c38076592cda75a38b8bb52175b867.

## Reproduction and unchanged work

Set VASM to the approved vasmm68k_mot and PYTHONPATH to include the existing
inspection dependencies and port/tests, then run:

- python port/tests/recovery_test_resident_startup_fade.py
- python port/tests/recovery_test_empty_queue_entry.py
- python port/tests/recovery_test_empty_queue_entry.py --rom
- python port/tests/recovery_test_repeated_active_audio.py
- python port/tests/recovery_test_repeated_active_audio.py --ticks 41

The standalone suite
retains its explicit reference-bootstrap distinction; this new resident suite
supersedes no prior test and supplies the separate reset-continuity proof.
Detailed standalone audio evidence is in `recovery_repeated_active_audio.md`.
The independent fade helper report is `recovery_startup_fade_continue.md`.

This source extends the recovered baseline with separate static helpers.
The earlier 68-call diagnostic, original inputs and delivered Z/X disk remain
unchanged. Aggregate scripts now include the reviewed startup extension.
Private Europe ROM SHA256 remains
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
No cartridge extracts, raw execution traces or captured bootstrap state are
embedded in source or reports. Native assembly contains static translated
operations, no runtime general6502 instruction fetch/decode/dispatch engine.

## Exact next boundaries and limits

At C597 the next original operation is JSR C14E. This continuation is outside
this proof. The independent standalone audio test completes41 calls and then
encounters unsupported music command02 at83A0 in call42. Nonzero CF callbacks,
pending D0/D1 paths and unsupported music commands remain guarded or explicitly
reported; nothing is cleared or skipped to force completion.

Interrupts here are explicit logical NMIs scheduled at authentic idle boundaries,
not a cycle-accurate asynchronous hardware timer. Ordered APU effects are not
rendered into Paula samples. There is no claim of audible output, physical Amiga
execution, game speed, full boot, playable gameplay or a newly delivered ADF.
The separate stock-target report establishes emulated A1200 execution of this
533-call sequence; it does not change these gameplay and audio limitations.

## Independent-review control correction

An arbitrary caller frame whose tick RTS returned8052 or8085 previously could
be followed as though it were an internal continuation. A restored nonzeroCF
could therefore reach an unsupported callback after writes. The corrected
control helper now follows at most one phase continuation, requiring either
a same-invocation generated phase call or the complete bounded wrapped
savedCF00/return8051/outerreturnC0F8 structure. Other tick RTS destinations are
returned unchanged as natural boundaries. This is structural validation, not
proven provenance. The same-invocation inactive-channel RTS remains internal.

The exact CF1 reproducer now exits8052 after four original RAM writes, withCF1
preserved and no unsupported access. Both public and original-ROM control
suites pass16,128 additional stack/near-match/caller-return regressions. The
533-call resident sequence and41-call standalone sequences reran with identical
state/event outcomes. The correction is confined to the active-control helper
and its tests; the earlier 68-call diagnostic remains byte-identical.

## Integrated validation

The public contract extension and private startup extension now exercise this
reviewed source. A separate [stock-target diagnostic](recovery_resident_fade_target.md)
verifies all 533 resident boundaries. The following video-clear slice remains
a distinct host-only proof. None of these diagnostics is integrated gameplay
or audible Paula output.
