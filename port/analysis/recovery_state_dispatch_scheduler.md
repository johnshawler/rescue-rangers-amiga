# State-driven scheduler, fade and repeated active audio

This additive native dispatcher extends the frozen first-active-tick chain to
292 helper completions and 11 externally supplied logical NMIs in each of eight
continuous original-ROM runs. It performs nine genuine active RTIs, nine new
scheduler resumes with fresh controller samples, nine fade continuations and
nine frame yields. It reaches original PC 83A0 with A03 and rejects the currently
unlinked music command 03 inertly. This is new implementation using verified
recovery helpers, not recovered missing gameplay or audio source.

## Production behavior

The wrapper selects the frozen general task scheduler only at original PC FE8D,
task-zero RAM 80=4 and wrapped saved RTS frame C2A7 addressed through RAM 82. It
requires canonical status B=0/U=1, event zero, tag D501, MMC1 control 1E, exact
PRG 6 and an empty serial latch. The saved frame, not a forced endpoint write,
produces resumed C2A8. All 256 original saved-SP positions are supported. The
helper performs real controller resampling, edge detection, opposing-direction
sanitization and wrapped original-stack restoration.

C2A8 fade and C2A5 yield additionally require task-zero ownership (RAM 91=0,
RAM 80=2). Fade is bounded to its next delay: countdown-expired cases whose next
level would return (level 50 or negative) reject before mutation. Other countdown
values and nonterminal palette attenuation use the frozen helper. The frame
yield returns to FE8D, where the caller may idle and supply the next logical NMI.
Frozen idle/palette NMI helpers execute the actual pending work.

At C0BF, live RAM DB/DC selects empty versus nonempty command queue, never trial
execution. Empty-queue entry publishes five real FFF0 writes; the new native
serial latch consumes them in order before returning C0F6. It never assigns the
expected bank directly. Active phase control at C0F6/8085, instrument preparation
at 8374, envelope at 86B2 and duration progression at 837F require exact PRG 3,
control 1E and empty latch. Immutable bank addresses derive from the live PRG
register masked to this cartridge's eight physical banks, multiplied by 16KiB.
The frozen helpers validate canonical binary status, channels, callback state,
resource pointers and music tables before mutation. Guard preflight may read
valid immutable resources before rejecting; mutable buffers remain unchanged.

8085 requires saved CF00 and a genuine outer C0F8 frame, or the bounded
8051/C0F8 phase-wrapper frame. Envelope and duration returns require 837E and 8084
respectively. All frame reads wrap at original SP. Existing parser/rest/pitched
helpers remain unchanged. Other states directly enter the frozen active dispatcher.
There is no helper schedule, call counter, oracle state, generic 6502 interpreter,
speculative helper execution or native-output-selected reference endpoint.
Diagnostics are output only and are poisoned between successful test calls.

Other task scheduler modes, arbitrary saved RTS destinations, terminal fade
returns and command 03 are not admitted by this extension. There is no inference
of asynchronous interrupts or physical timing.

## ABI

The active ABI is unchanged: A0 RAM[2048], A1 canonical context[8], A2
journal[8754], A4 runtime[12], A5 immutable contiguous eight-bank PRG[131072].
D0.b/D1.b are decoded logical pads; D2.l is event 0/1. D0 returns 1 advanced,
0 waiting or FFFFFFFF unsupported. D1-D7/A0-A6 and exact native SP are preserved;
native CCR is scratch. Buffers must be valid, aligned, disjoint and exclusively
owned, with sufficient native stack and immutable resources. Unsafe pointers
and concurrent mutation are caller obligations, not dynamically validated inputs.

New diagnostic IDs / journal sizes:

- 21 scheduler resume /74 bytes, 18 ordered controller records.
- 22 fade /0; 23 frame yield /0.
- 24 empty-queue entry /22; 25 active control /0.
- 26 duration preparation /10; 27 envelope /514; 28 duration progression /0.

Fade/yield RAM-only raw journals use 272 bytes of private native stack scratch.
Their original RAM writes remain observable in order; no hardware effects are
hidden or discarded because those helpers have none. Both preserve the entire
external journal. Other calls preserve bytes beyond their published size.
Failed and waiting calls preserve all mutable buffers and emit no effects.

## Portable reproduction

Use Python with requirements-dev.txt and a working vasmm68k_mot supporting 68020.
From the repository root:

```
python -m pip install -r requirements-dev.txt
export VASM=/path/to/vasmm68k_mot
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_test_state_dispatch_scheduler_contract.py
python port/tests/recovery_test_state_dispatch_scheduler_rom.py --rom /path/to/approved-original.nes
python port/tests/recovery_test_state_dispatch_active_contract.py
python port/tests/recovery_test_state_dispatch_active_rom.py
```

The first new command is PUBLIC and ROM-free: no py65, private oracle, captured
state or cartridge is imported. All resource banks are invented and distinct.
The separate private runner requires explicit --rom and verifies SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
The inherited private regression retains its existing repository-local private
input convention. No cartridge bytes are included in this increment's files.

The synthetic suite compares full RAM/context, complete journals, ordered
RAM/controller/resource/mapper/APU effects, exact resource reads and live mapper
state with independent frozen public declarative contracts. It covers all 256
SP positions, all four audio channels, canonical status variations, randomized
preserved context, previous-controller bytes, current pads and CHR registers.
2,048 fade cases continue into 2,048 frame yields on live native buffers without
reloading state. Additional active audio cases cover empty queues, phase control,
instrument preparation, envelope stages and duration advancement. Each of the
eleven envelope resource-guard bytes is independently corrupted and rejected.
Invalid events, tags, latches, canonical statuses, task ownership, channels, frames and return
fade levels reject inertly. Every unsupported mapper control/PRG value is tested
at the scheduler and new audio boundaries. The suite passes 12,288 successes
and 143,863 inert rejections; exact counts are in the results JSON.

The private selector is independent of native metadata. It chooses reference
endpoints from original PC/RAM/event, and the original CPU completes that
operation before native dispatch. No successful-chain RAM/context/original stack
or mapper reload occurs. Only journal scratch is cleared and diagnostics poisoned.
All 2,336 successful boundaries match full RAM/context, complete ordered effects
and journals, real serial mapper state and exact immutable-resource reads. Across
the eight runs there are 24,064 checkpoint rejections and eight extra terminal
inert calls. Each run includes 40 ordered APU writes.
Each run retains the 67-helper C2A8 and 70-helper third-NMI C0BF checkpoints before
continuing through further genuine ticks, palette work and frame yields.

Eight input histories include neutral with zero versus 13 extra delayed polls,
Start release, Right-to-Left transition, held Left, swapped Up/Down and swapped
A/B on separate pads, and all buttons. There are ten genuine controller samples
per run; subsequent samples retain the selected second-pad pair. This establishes
resampling and held/released edge behavior, not title/menu control or gameplay.
Final context is 83A0/03/2B/00/A4/AB/A7, mapper 1E/00/10/03, empty latch. Command 03
rejects inertly with no resource reads. A separate original-only check follows
that command to 839D in 26 original instructions. The next adapter would need command 03's real table/resource/volume effects, not a bypass.

The harness randomizes preserved native registers on every call, checks exact
native stack return and buffer guards, bounds all accesses, rejects resource
writes and verifies unchanged code plus all 128KiB resources after each call.
Machines execute sequentially. Repeat assembly is identical; the composite is 18,952 bytes, SHA256
18229592a497e26c19c57b274c4d11072bcbb293dad9e18f4b4da1e72f4772e4.
Frozen active public/private regressions pass unchanged and their results are included.

## Preservation and limits

Only the eight scheduler-prefixed files listed in the manifest were added.
The active predecessor manifest current at finalization is SHA256
87e478126232ebb089fbff82dd369dfc69a5997417db14e29de50946027460b0.
All 67 frozen dependencies are hashed. This is new source development on the
recovered baseline, not a recovery of the missing later gameplay/audio source.
The delivered Z/X ADF remains unchanged.

This is host M68EC020 logical-runtime evidence only, not an Amiga target/emulator
test, hardware timing, physical controls/display/audio, FPS or complete-game
claim. Ordered APU writes do not establish audible output. Remaining unlinked
command 03, terminal fade returns, title flow and gameplay need further work.
Serial bit 7-reset branches remain static-review-only: admitted writes do not
exercise them.
