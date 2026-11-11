# State-driven title menu and default-character confirmation

The additive native dispatcher continues the frozen C5D1 startup checkpoint
through genuine title initialization, sampled menu inputs, character-menu
resource loading, its queued-video NMI, and default-character confirmation.
Ten uninterrupted original-first histories match 65,195 native helper boundaries
and 16,702 ordered APU writes. This is new native translation on the early
recovery baseline, not recovery of the missing later playable/audio source.

## Continuous results

Every history retains C2A8 after 67 helpers, third-NMI C0BF after 70 helpers,
command 03 after 292 helpers/11 NMIs, and the exact C5D1/F0/F0/FF/A5/BF/A7
checkpoint after 990 helpers/35 NMIs with mapper 1E/1F/1F/02 and empty latch.
Neither reference nor native RAM, context, wrapped stack or mapper is reloaded
on the successful chain after reset. Only journal scratch is cleared and the
unused diagnostic fields are poisoned between calls.

- Start reaches first character dispatch A06C/FF/FF/FF/A4/BD/A7 after
  1,091 helpers/38 NMIs. RAM19 is zero because original queued-video work
  consumes it, not because the host clears it. Held Start, two released
  character frames and a new Start press then reach C5F8/F8/00/FF/27/BF/A7
  after 1,229 helpers/43 NMIs. The original sprite-clear RTS consumes C5F7
  from the actual wrapped stack. There is no translated gameplay at C5F8.
- Right and Left after the same held/released character history reach A07B
  after 1,228 helpers/43 NMIs, with respective contexts
  A07B/01/FF/01/24/BD/A7 and A07B/00/FF/00/26/BD/A7. This is before the cursor
  resource read and sound request. No sound is bypassed.
- Released character input remains at A06C after 1,227 helpers/43 NMIs and
  five completed character-dispatch visits. This is an intentional test stop
  at an admitted boundary, not an unsupported-state claim.
- Start held during startup, released for title samples, then repressed
  reaches first A06C after 1,155 helpers/40 NMIs and default confirmation
  after 1,311 helpers/45 NMIs.
- Title Right, Left and Select each reach F379 after 1,068 helpers/37 NMIs.
  The sound 27 queue operation is deliberately not linked in this increment.
- Neutral and ignored A input each complete all 900 genuine countdown decrements,
  then return to C5F8/F8/00/FF/27/BF/A7 after 27,884 helpers/935 NMIs. The timer
  is zero and original timeout writes set RAM50/RAMB8 to 1. Each run produces
  7,136 ordered APU writes. Commands 0E/01/12/13/0F execute 121/17/4/2/1 times
  respectively. The former command 0E boundary remains an asserted checkpoint
  at 2,241 helpers/78 NMIs with timer 858, before the genuine continuation.
  Neither music commands nor queued work are skipped.


Controller inputs are external decoded pad bytes supplied identically to
original controller reads and the native scheduler. Holding, release, re-press,
neutral, ignored bits and direction histories use genuine edge sampling.
Controller two is neutral in continuous runs; invented-state contracts vary
both controllers. This is not two-player gameplay or live keyboard integration.

## Production selection and contract

The new entry is recovery_state_dispatch_menu. Selection uses PC, live RAM,
the original wrapped stack, actual serial mapper registers/latch and event 0/1.
Diagnostic IDs and sizes never select work. The production source contains no
fixed helper schedule, generic 6502 interpreter, speculative helper trials,
reference feedback, captured states or resource payloads. Unhandled entries
route to the unchanged startup/scheduler/active/palette/prefix chain.

New operations require tag D501, control 1E, empty serial latch and canonical
status B=0/U=1. Menu operations require PRG2; music commands require PRG3.
Task-side operations require task-zero ownership
RAM91=0 and state RAM80=2. Only event 0 is admitted outside the NMI boundary.
Fixed resource reads use bank 7 under the validated mapper mode; character
resources use the live PRG register to derive the bank view.

- ID43 C5D1: frozen title-engine table helper, 362-byte resource journal.
- ID44 A025: frozen countdown helper, external journal unchanged.
- ID45 A000: frozen title input helper, external journal unchanged. Start,
  Select and direction priority remain the original semantics.
- ID46 A0BB: frozen sprite-hide/RTS helper, external journal unchanged;
  the real return frame must be C5F7.
- ID47 A05C: frozen character-table/yield helper, 106-byte journal with
  its unused tail preserved. It writes the genuine RAM19 request.
- ID48 FE8D: frozen queued-video NMI, 134,638-byte capacity, DMA snapshot
  at offset 134,382. Requires task-zero state 1, NMI enable and nonzero RAM19;
  unsupported F0/9A/1C/1D conditions reject. Event 0 waits inertly. Event 1
  validates the finite script before mutation, executes it and preserves all
  original CHR, palette, timer and interrupt work. Published mapper-address
  records update the real serial latch/registers in order.
- ID49 A06C/A089: frozen character dispatch/resume helper, external journal
  unchanged. The alternate-confirm branch is covered in invented states;
  it is not claimed continuously reachable here because the cursor/SFX path
  remains unlinked.
- ID50 FE8D: frozen general scheduler, 74-byte controller journal, admitted
  only for task-zero state 4 and actual saved frames A024/A06B/A088. It samples
  both controllers and restores the actual saved stack.
- IDs 51/52/53/54/55 at 83A0 select frozen music 0E/01/12/13/0F helpers from
  actual A and PRG3, with journal sizes 22/10/22/22/22. Their existing channel,
  table-signature and bounded-operand preflights run before mutable writes.
  They preserve counted loops, channel changes, pointer jumps and stack traffic;
  no title/audio task state is injected. Resources derive from live PRG3.

A0 RAM2048, A1 context 8, A2 journal, A4 runtime 12 and A5 immutable contiguous
PRG131072 retain their meanings. D0.b/D1.b are logical pads and D2.l is event.
D0 returns 1 advanced, 0 waiting or FFFFFFFF unsupported. D1-D7/A0-A6 and the
exact native SP are preserved; native CCR is scratch. RAM-only helper journals
use private 512-byte native scratch while every RAM store remains observable.

**The caller must now allocate 134,638 bytes for the journal, keep runtime and
resources disjoint from it, and provide at least 1 KiB native scratch stack.**
The existing runtime diagnostic size is a word: FFFF means 134638 for ID48
only. All other IDs retain literal sizes. This is an explicit sentinel, not a
truncated capacity. The frozen startup entry/ABI/files are unchanged. Old
callers must not call the new entry with the old journal allocation. Valid,
aligned, exclusively owned and nonoverlapping buffers remain caller obligations.
The generous journal is a host-proof bound, not a target-memory recommendation.

## Verification and reproduction

From the repository root, install requirements-dev.txt and set VASM to a
working vasmm68k_mot with 68020 support. Public contracts need no cartridge,
py65 or private imports; private differential testing requires an explicit path.

```
python -m pip install -r requirements-dev.txt
export VASM=/path/to/vasmm68k_mot
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_state_dispatch_menu_contract.py
python port/tests/recovery_state_dispatch_menu_music_contract.py
python port/tests/recovery_state_dispatch_menu_long_contract.py
python port/tests/recovery_state_dispatch_menu_rom.py --rom /path/to/approved-original.nes
python port/tests/recovery_state_dispatch_menu_long_rom.py --rom /path/to/approved-original.nes
python port/tests/recovery_state_dispatch_startup_contract.py
```

The public menu suite passes 67,840 successes and 28,928 inert rejections;
the music-adapter suite passes 5,381 successes and 61,834 inert rejections.
The frozen startup public suite passes unchanged with 12,801 successes and
55,779 inert rejections. All 114 predecessor-listed files retain their hashes.

Public invented-state coverage includes all 256 SP positions for each new
adapter, all 256 menu input bytes, all canonical flags, alternate/default
character confirmations, both controllers, all 65,536 countdown values,
varied finite scripts and rejected nonterminating scripts. The separate music
adapter suite covers all 256 SP positions and all canonical status values across all four channels for
all five commands, counter branches, page crossings, safe bank-edge skips,
unsafe operand reads, invalid pointers and resource-signature mismatches. It checks full
RAM/context, complete journals and unused tails, exact ordered resource/PPU/
APU/mapper/controller/DMA effects, resource-read addresses, native registers,
exact SP, canaries, immutable code/resources and access bounds. Invalid events,
tags, status, mapping, partial latches, task ownership, return frames, video
queues and unbounded scripts reject inertly. Waiting calls preserve buffers.

The private selector chooses each endpoint from original state before original
instructions execute; original execution completes before native execution.
All 10 histories compare every accepted boundary. Inert checkpoint probes run
on separate machines at every 31st helper count (including intervening waits)
plus the final eight calls: 22,364 checkpoint rejections pass, plus nine
unsupported-final-state probes.
No negative probe mutates the successful chain. The compact results file includes lossless run-length encoded
input samples, per-helper totals, endpoints, retained checkpoints and SHA256
hashes of detailed boundary traces. The private runner regenerates the full
trace on standard output; the detailed run output is not distributed. Private ROM SHA256 is
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.

The composite assembles byte-identically twice: 31,628 bytes, SHA256
ac4b5d9cdca6da92badce8ca6ffffb1a1bc0077c0d10f77fb98c47a678f6e135.
The manifest records new files and frozen dependencies, including predecessor
startup manifest SHA256
9f167ea54fef8786e18558b809980ebe0ea0019568d249a1f11a4b1a40b6905a.
All predecessor-listed files are checked unchanged. No earlier source, tests,
reports, manifests, aggregate scripts, README, Git/index, deployment, assets or
delivered ADF were edited.

## Unsigned record-count regression

The queued-video journal count is an unsigned word. A signed-negative check
following its decrement incorrectly omitted mapper replay above 32,768 records.
The adapter now tests for zero before decrementing, then uses DBRA for the
complete unsigned count. The earlier candidate is superseded; its source and
manifest are retained separately for regression comparison. Frozen predecessors
are unchanged because their admitted small journals cannot reach this range.

Four public invented long scripts and four independent original-ROM cases
produce 33,300 or 33,339 records, with both CHR requests, optional palette work,
zero/randomized RAM and wrapped stack positions. They compare complete RAM,
context, ordered effects, full journal and untouched gaps, DMA and real mapper
state. Every corrected case ends with runtime 1E03070200000030FFFFD501, including
actual CHR registers 03/07. The original CPU executes 166,518 or 166,690
instructions per case. The public suite also checks four inert waits and
32 invalid-event/latch/tag/queue rejections. The same four cases reproduce the
incorrect CHR registers 1F/1F with the preserved earlier binary.

The native harness execution ceiling is now 10,000 batches of 1,000 emulated
cycles, sufficient for these finite scripts. No bounds, ABI, canary, resource
immutability, journal or stack checks were removed. This is a test budget,
not a target execution-time claim. All regular suites are rerun on the corrected
composite; the long-script checks are separate from continuous reset histories.

## Exact remaining boundaries and limits

F379 title selection sound, A07B character cursor/SFX and post-confirmation
C5F8 remain inert rejection boundaries of this composition.
Semantic helpers for some of these operations exist separately, but they are
not yet admitted by this state-driven adapter. No command, queue or sound is
skipped to make progress. The 900-countdown route is proved logically, but
subsequent demo/gameplay dispatch is not linked.

This is host M68EC020 logical-runtime correctness evidence, not an Amiga
hardware/emulator run, physical rendering/audio, target timing, FPS or playable
game claim. Ordered APU writes do not establish audible Paula output. There
are no cartridge bytes or captured-RAM fixtures in these deliverables. Live
controls remain unintegrated; eventual Z=B and X=A mapping is unchanged and
the delivered ADF is untouched.
