# Segmented native menu cost checkpoint

## Result and scope

The additive profiler separates native dispatch, exact journal capture, device
handling, audio shadow/planner/wait/apply, CHR mapping, background drawing and sprite
drawing. It runs the same bounded default history from FE24 to C5F8. It adds no
interpreter, live input, gameplay, music profile or fabricated original state.
Frozen predecessor sources and the delivered disk are unchanged. There is no
optimization or speed claim in this checkpoint.

Fresh display-on and display-off instrumented stock runs pass the independent
original state/context/runtime, every ordered journal/DMA byte, final device,
bitplanes, displayed RGB pixels, completed audio shadows/plans, actual callback
PCM pitch/channel/silence checks and PCM counterexample tests. Each completes
322 native APU writes and 43 completed RTIs, with 1229 successful native helper
calls and 1272 dispatcher calls including 43 pending-event attempts. Both variants
pass all 14 complete-target failure/mute/drain/error-identity tests. Instrumented
on also passes the compiled adapter tests. The native dispatcher and planner
remain byte-exact; call-site instrumentation does not rewrite their bodies.

The freshly rebuilt uninstrumented display-on control is byte-identical to the
approved v7 ADF (506a03714a987adbac5b50ced9c2cba3f6a088f79636580ae7522a6ad3b2a6e1)
and independently passes the same original and PCM checks. Its target timings
reproduce 991535 progression ticks, 40 late publications out of 43, 91343 maximum
publication interval, and 63649 final-render ticks. This is a real fresh control,
not merely a reused baseline report.

All runs use the pinned PUAE core/frontend, stock PAL A1200OG/68020/AGA, 2 MiB
Chip, zero Fast, CPU and memory cycle exact, and normal five-plane display DMA
in the on case. Timers are chained 32-bit CIA-B at nominal 709379 Hz. No physical
hardware or whole-game frame-rate result is implied.

## Raw instrumented segment measurements

Counts are identical between on/off. Values below are total CIA ticks, with
DMA-on first and DMA-off second. These are inclusive observed bracket intervals,
not observation-free estimates.

- Native dispatch: 616854 / 525337 ticks; 1272 calls; on maximum 8369 ticks.
- Journal capture: 144134 / 126506 ticks; 1229 calls; on maximum 4488 ticks.
- Device consume: 151319 / 128726 ticks; 138 calls; on maximum 68191 ticks.
- Audio shadow journal scan: 78773 / 71322 ticks; 1229 calls; on maximum 5370 ticks.
- Audio planner: 6699 / 5743 ticks; 43 calls; on maximum 176 ticks.
- Audio wait/late-check/poll interval: 3775 / 3484 ticks; 43 calls; on maximum 98 ticks.
- Audio hardware apply: 4536 / 4075 ticks; 43 calls; on maximum 143 ticks.
- CHR selection/copy: 1866 / 1739 ticks; one call.
- Background render: 43678 / 39057 ticks; one call.
- Sprite render: 17398 / 15605 ticks; one call.

The main render cost is background drawing: 61.57ms on, followed by sprites at
24.53ms and CHR mapping at 2.63ms. Even the observed background component alone
is far beyond 20ms. Native dispatch dominates accumulated progression work;
device handling contains a single ~96.13ms observed call. Journal capture and
shadow scanning are material additional diagnostic/integration costs. The planner
and hardware apply are comparatively small. The observed wait/late-check/poll interval totals only 5.32ms, and all
instrumented updates are already late. This bucket includes clock reads and
late-check/poll overhead, not just idle waiting; it does not measure productive
audio work.

These aggregate data identify classes of work, not which individual helper caused
the worst device interval. Do not attribute that maximum to a particular helper
without additional measurement. The profiler does not claim the native dispatcher
itself has a single 96ms call. Audio shadow scan parses all counted journal entries,
including non-APU entries, but no early-out optimization is admitted here without
proving that ordered mixed-register writes remain exact.

## Observation cost and comparison limits

The on progression grows from the fresh control's 991535 to 1410761 ticks:
419226 additional ticks, about 591.0ms or 42.28%. This is measured net perturbation,
not a pure CPU timer-instruction cost: clock reads, save/restore, accounting,
additional empty probes, changed code layout/display phase and changed waiting
all contribute. It must not be presented as an optimized result.

The assembly empty segment executes 1229 times. On totals 48354 ticks, mean
39.344 ticks (55.46 microseconds), maximum 54 ticks. Off totals 40438 ticks,
mean 32.903 ticks, maximum 44 ticks. An empty bracket includes a start-probe tail,
return, call and part of the end probe; it excludes the other outside timestamp
and accounting costs. C audio intervals use a separate clock/aggregation path.
No mean empty-bracket subtraction is reported as an exact de-biased result.

Instrumented final render is 63343 ticks on versus the control's 63649, despite
additional probe work. This small phase/contention change is not an optimization.
The fresh uninstrumented off control reproduces 862746 progression ticks,
30 late updates, maximum interval 80395 ticks and final render 56614 ticks; its
full original/PCM verifier passes. Off instrumentation increases progression to
1213072 ticks, a net 350326 ticks (493.85ms, 40.61%). The off instrumented render
is 56728 ticks. Profile totals exclude some runner,
bridge, record-copy, palette/scanout and accounting instructions. The inherited mp.max_work value is also contaminated: r->published records
now before profile_add(wait), so mp.max_work includes that bookkeeping. Do not
compare that field with the frozen hardware-apply metric. Use the separately
scoped new apply bucket, with its clock-read overhead caveat. Do not blindly sum all segments
and label the result total execution time or equate logical RTIs with video FPS.

## Preservation and evidence

Private evidence resides in distinct directories:

- recovery_profile_v2/on: qualified instrumented display-on run.
- recovery_profile_v2/off: qualified instrumented display-off run.
- recovery_profile_v1/control-on: fresh uninstrumented approved control. The v1
  directory name does not mean this control contains the rejected instrumentation.
- recovery_profile_v2/control-off: fresh uninstrumented display-off control.
- recovery_profile_v1/on: rejected initial candidate, preserved. An SR-read caused
  privilege resets in the actual user-mode boot. Supervisor-only synthetic checks
  had missed this. Corrected v2 uses CCR; public tests now check user mode.
- recovery_profile_v1/off: built old candidate only, never qualified or captured.

The first v2 run of the unmodified predecessor verifier stopped on its broad
immutable-adapter-prefix assertion because the new live counters are inside that
prefix. The additive verifier now excludes exactly the 48 counter bytes in the
named 56-byte structure, checks its magic and all other prefix bytes, and retains
every original semantic/audio/pixel assertion. This was a verifier adaptation,
not a change to the captured target. No old capture was overwritten.

The instrumented payload is 811984 bytes on / 811912 off, allocation 812032 Chip
bytes in both cases, adapter extent 22604 bytes. Original control allocation is
811008 bytes. Source-only delivery excludes ROM, firmware, generated assembly,
linked binaries/disks, snapshots, audio, screenshots and detailed original traces.
The delivered disk remains SHA256
6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17.

Four-DMA finite-noise/fixed-stereo approximation limits from the predecessor still
apply. Later playable/audio source is still lost. No live-menu or gameplay
expansion, telemetry guard removal, general 6502 runtime, or full-rate continuous
rendering is part of this checkpoint. A useful next optimization study should
focus on the background/sprite renderer or repeated native/journal/device work,
with source-faithful equivalence and fresh matched target measurements.

## Independent source-only rebuild

A separate reviewer copied the 205 generic predecessor dependency paths plus the
seven profiler source/report files into an empty private directory. The public
probe test passed before any private input was supplied. Adding only the approved
cartridge, with external compiler/assembler tools, rebuilt the on ADF byte-identical
to the qualified v2 capture input:
a0516c67991eae571257a5c10459d2c6a100c0c128d97a9b9cf7da8b371d95dd.
No firmware or target capture was used for that rebuild and no extra emulator run
was performed. The older predecessor closure manifest differs from the current
approved baseline in three report/provenance files only, not implementation code.
The reviewer also reran both instrumented capture verifiers, all 28 linked-target
rejections, and independently checked all 32 CCR combinations on the probes.
