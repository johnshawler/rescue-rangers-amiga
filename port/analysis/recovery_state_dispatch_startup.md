# State-driven startup through the initial title boundary

This additive dispatcher reaches original PC C5D1 through 990 native helper
completions and 35 externally supplied logical NMIs per continuous run. Eight
independent original-first runs match 7,920 helper boundaries and 2,016 ordered
APU writes. Startup video clearing, bank selection, resource loading, title
setup, real pending CHR requests and title fade-in complete without a fixed
helper schedule. This is new source implementation on the recovery baseline,
not recovery of the missing later playable/audio source.

## Production selection and boundaries

Only PC, live RAM, original wrapped stack, actual serial mapper state and the
external event choose a helper. Diagnostics are never inputs. There is no
6502 opcode interpreter, speculative helper execution, captured-state loading,
or native-output-selected reference endpoint. Unhandled states delegate to the
unchanged scheduler/palette/active/prefix chain.

New entries require tag D501, MMC1 control 1E, an empty serial latch and
canonical architectural status (B=0, U=1). Non-interrupt operations require event
zero. Resource pointers are derived from the live PRG register, masked to eight
physical banks and multiplied by 16KiB; no cached expected bank is substituted.

- Music commands 03 and 02 at 83A0 require PRG 3. Their frozen semantic helpers
  validate channels and command-table bytes before mutation. They perform the
  actual dispatch-table reads, page-one stores and channel-bit changes.
- FE8D task-zero state 4 resumes saved RTS frames C2A7, C596 or C5CD. C596
  requires PRG 6 and C5CD requires PRG 2; C2A7 is supported in either. The general
  scheduler resamples both controllers and restores the real saved stack.
  The initial frozen scheduler path still handles its original continuation.
- C2A8 countdown/attenuation uses the frozen fade helper. A terminating fade
  requires its real return frame C593 under PRG 6 or C5D0 under PRG 2. Thus it
  returns to C594 or C5D1 by consuming the original stack, not by forcing a PC.
  C594 sets up the actual FF04 call; frame yields remain genuine scheduler
  operations. Task-side paths require RAM 91=0 and RAM 80=2.
- C597 clears video state; C5BB selects PRG 2 through the original five serial
  writes. The latter requires zero F5/F6. C5C0 loads the bounded resource stream
  and C5C5 sets up palette/sprites/rendering under PRG 2. The loader rejects an
  out-of-bank stream or a stream exceeding its frozen 4,094-byte budget before
  changing mutable state. C5CB sets up the real yield, and C5CE starts fade-in.
- At FE8D under PRG 2, task-zero state 1 waits for event 1. NMI enable must be
  set and unsupported pending queues/skip conditions F0/9A/19/1C/1D must be
  zero. The CHR-capable frozen NMI consumes genuine 1A/1B requests and publishes
  their serial writes in order, together with PPU operations and OAM DMA.
  Empty audio queue entry under PRG 2 changes to PRG 3 using real writes.
  Active audio returns restore PRG 2 from F1, with the genuine FE8D interrupt
  return frame and task state 4. Existing bank-3 audio operations remain intact.

Serial mapper updates consume only published mapper-address records, in their
original order, including mixed CHR/PPU journals. No expected register is assigned
directly. Bit-7 reset handling is present but remains static-review-only here:
these admitted helper values do not exercise it.

The supported endpoint is C5D1/F0/F0/FF/A5/BF/A7, mapper 1E/1F/1F/02 with empty
serial latch. The next title-engine table operation at C5D1 is not linked; a
call there rejects inertly. This is the requested initial title boundary, not
completion of menu handling or gameplay. Command 02 is linked and covered by
public invented-state contracts; the eight reset-to-C5D1 histories do not
naturally execute it. They execute command 03 twice each.

## ABI and effects

A0 points to RAM[2048], A1 to canonical context[8], A2 to journal[32770], A4 to
runtime[12], and A5 to immutable contiguous eight-bank PRG[131072]. D0.b/D1.b
supply decoded logical pads and D2.l supplies event 0/1. D0 returns 1 advanced,
0 waiting or FFFFFFFF unsupported. D1-D7/A0-A6 and the exact native stack pointer
are preserved; native CCR is scratch.

**Journal capacity increases from 8,754 to 32,770 bytes.** Existing callers must
allocate that capacity and keep the runtime and all other buffers disjoint.
The host harness places runtime beyond the larger journal. Buffers must be
valid, aligned, exclusively owned and non-overlapping, with immutable resource
storage and at least 1KiB available native scratch stack. Unsafe pointers and
concurrent mutation remain caller obligations, not dynamically checked inputs.

New diagnostic IDs and published sizes/capacities are:

- 29 command03 /10; 30 command02 /10; 31 scheduler resume /74.
- 32 fade/outer-yield setup /0; 33 frame yield /0.
- 34 video clear /4382; 35 bank select /22.
- 36 resource loader /32770; 37 title setup /566.
- 38 title-yield entry /0; 39 title-fade entry /0.
- 40 CHR-capable NMI /494, OAM snapshot at journal offset 238.
- 41 title empty-queue entry /22; 42 title-bank active RTI /22.

RAM-only helper journals use private 512-byte native scratch. Every original
RAM store remains visible and ordered; those helpers have no hardware effects
to hide. They preserve the entire external journal. The variable resource-loader
journal preserves unused capacity, and the CHR journal preserves its unused
record gap. Resource-loader kind 2 denotes the discarded PPU-status read;
comparisons normalize its effect to a read while checking the raw journal kind
separately. Other bytes beyond published sizes remain untouched. Failed and
waiting calls preserve all mutable buffers; resource guard failures may read
immutable bytes during preflight but emit no effects.

## Reproduction and verification

From the repository root, install requirements-dev.txt and provide a working
vasmm68k_mot supporting 68020. These commands do not edit the frozen baseline:

```
python -m pip install -r requirements-dev.txt
export VASM=/path/to/vasmm68k_mot
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_state_dispatch_startup_contract.py
python port/tests/recovery_state_dispatch_startup_rom.py --rom /path/to/approved-original.nes
python port/tests/recovery_test_state_dispatch_scheduler_contract.py
python port/tests/recovery_test_state_dispatch_scheduler_rom.py --rom /path/to/approved-original.nes
```

The first command is PUBLIC and source-only. It imports public declarative
models, never a private oracle, py65 or cartridge. Every RAM/resource allocation
is invented. Its positive cases cover all 256 original SP positions, all four
music channels, varied canonical flags, preserved fields, controller bytes and
CHR state. Each added adapter is exercised. Terminal fade frames, nonterminal
attenuation/countdowns, 4,096 live fade-to-yield continuations, both title entry
helpers, CHR serial publication, and cross-page resource streams are checked.
An invented 4,093-byte resource stream passes; an over-budget stream rejects.
Invalid events, tags, serial latches, mapper controls/banks, frames, task
ownership, channels, command guards, loader pointers, queues and deferred bank
work reject without mutable changes. Full RAM/context, journal bytes, ordered
effects, exact resource-read addresses, serial mapper result, preserved native
registers, exact host SP, guard bytes and unchanged code/resources are checked.
The public suite passes 12,801 successes and 55,779 inert rejections.
The results JSON contains the per-operation counts.

The private runner requires explicit --rom and verifies SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
Its selector derives endpoints from original state before running original
instructions. Each original operation finishes before the native dispatcher is
called. The successful native chain never reloads RAM, context, original stack
or mapper state. Only journal scratch is cleared and diagnostic fields are
poisoned between calls. Negative checkpoint probes use separate machines.

All eight histories retain the 67-helper C2A8 checkpoint, 70-helper third-NMI
C0BF checkpoint, and exact 292-helper command03 boundary with 11 NMIs before
continuing to C5D1. They include neutral with zero versus 13 extra polls, Start
release, Right-to-Left, held Left, swapped Up/Down, swapped A/B and all-buttons
histories. Each run performs 35 actual controller samples, 34 active RTIs,
252 APU writes and 10,145 inert checkpoint rejections. Across the eight runs,
81,160 checkpoint rejections and eight final-boundary rejections pass. This
establishes sampling/edge behavior in startup, not live title/menu control.

The harness bounds all memory accesses, rejects resource writes and verifies
all 128KiB immutable banks after every call. Assembly repeated byte-identically:
23,586 bytes, SHA256
a071d72a986a812fb09d4cc3a38a03fad693a7ff9d2ba7fdeb69c471de0c1f19.
Both frozen scheduler public/private suites pass unchanged. Its predecessor
manifest SHA256 is
6231f7e61ade7c68e4b46dce94d0e7b56760f6660869a2a63aa4fae168f3667c;
all 74 predecessor-listed files were verified unchanged. The new manifest
includes additional frozen helper/model dependencies and hashes every new
source/test/report/result file except the manifest itself.

## Preservation and limits

The manifest records the source, harness, public/private suites and evidence
summaries, together with 107 frozen dependencies. This is additive development
on the recovered baseline, not recovery of the later missing gameplay/audio
source. The delivered Z/X ADF remains unchanged.

This is host M68EC020 logical-runtime correctness evidence. It is not an Amiga
hardware/emulator run, physical display/audio, live controls, FPS or stock-speed
claim. Ordered APU writes do not prove audible output. No cartridge bytes or captured
RAM fixtures are distributed here. Title-engine/menu/gameplay dispatch,
asynchronous interrupt timing, physical rendering and audible audio integration
remain outside this increment.
