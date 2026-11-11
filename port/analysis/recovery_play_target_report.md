# Additive stock PAL A1200 five-neutral-frame diagnostic

Author verification: PASS within the bounded scope below. This new target boots
from source plus the authorized original cartridge, runs the actual title,
character selection, dialogue exit and stage loading, then completes five genuine
neutral game frames. It is not a playable-game release, moving-input qualification
or real-time performance claim. No earlier target, frozen engine, delivered disk,
original input or firmware was changed. No captured state, instruction decoder,
reference engine, mapper/status forcing or skipped audio enters production.

## Frozen implementation and target layout

Uses the reviewed play composition 216616 bytes,
SHA256 5a3ab5ff5204b73dd1223291f42f826f634ff43eaee725c7a503684f80e317f4,
from play manifest SHA256
428fc25ff5de74f2bcd64bbb6213207c1b7c0cdc500cfe2df4cd287da9743ba2.
All native source bytes are embedded exactly once, including approved136/137/138/160
and the existing B-only canonical adapter restricted to successful150/151.
The predecessor stage source manifest remains
9a7a81f49acd1d11d93efab12feb2fd25677c4b84317774e1e96013f13b290f2.
Renderer, ordered audio shadow, title planner and finite noise08 backend are unchanged.
No optimizer or phase-aware audio path is included.

Additive integration changes the dispatch/include list, maximum helperID to160,
resource-only device-ID entries and the diagnostic endpoint. An output-only long
counter observes six C77B arrivals: the loaded-stage entry and five true loop
returns. It never changes original RAM/context/runtime. All polling still uses
real CIA keyboard state with Z=B and X=A; the successful post-load route is neutral.

The engine growth would exceed single-ADF capacity with the old262144-byte output
capture. The new last-completion buffer is135168 bytes and explicitly long-aligned.
Every admitted maximum record fits: header4 +33595 records*4 +DMA256 =134640 bytes.
Overflow/count/helper/sentinel checks remain fail-closed. The saved output remains
last-completion-only; this is not an exhaustive on-target journal trace.

Final-layout v3 payload859748 bytes, boot allocation860160 Chip bytes, zero Fast.
Payload SHA256 04ededa6ffd8556318bd4f3a7b0e19576dfe97acceaa0b2a90a86c830c1403ea.
ADF SHA256 efeaf598d52723f0cf4d3eadfac448d5b82e9fbbfd5309c49357ada3af51884f.
Actual allocation base72792, safely inside2MiB Chip. Relative offsets:
RAM424688/2048, context426768/8, journal426808/134638,
runtime561478/12, immutable PRG561522/131072, stack692626–696722/4096,
capture696756/135168, compiled audio adapter831940/24544.
All guarded regions are disjoint; 16-byte guards remain intact. Resource and native
code immutability, actual boot allocation and live pointers are checked.

## Actual final-layout v3 capture

Private directory: port/build/recovery-play-target-v3. Pinned PUAE A1200OG,
68020/AGA/PAL, cycle-exact CPU/memory/blitter, zero Fast,11500 physical callbacks.
Real KEY_TICK_EVENTS:80:90:13,160:170:13,360:390:13. No RAM injection.

14655 accepted helpers,400 logical NMIs,757491 original instructions in replay,
400 rendered updates, zero terminal error. Final contextc77b00040026bfa7.
Original-first replay confirms arrival helper sequence130,135,135,135,135,135;
five genuine scheduler138 returns atc84804040024bfa7; all post-load input samples
neutral. Continuous native replay starts from reset without loading successful
reference state. Every RAM/context/runtime and ordered RAM/resource/controller/
mapper/PPU/APU effect matches. Raw150/151 context and effects are independently
checked before B-only publication. Registers, user mode, SP, width-aware access
bounds, code/resources and guards use the reviewed Native harness.

On the actual emulated target, final RAM/context/runtime, last completed journal,
all final device state, nametables, palette, OAM, selected CHR and logical pixels
match original-derived expectations. Independent fixed RGB12/Copper verification
checks220 Copper bytes,32 colors,5 DMA pointers and163840 actual viewport RGB pixels.
This is final-state screenshot coverage, not five intermediate screenshots.
Synthetic linked composition separately covers16 fine-scroll/wrap/sprite cases.

All ordered APU writes are replayed; actual final audio shadow and the retained256
records match original-derived plans exactly. Earlier144 records have rolled out
of the ring: no exhaustive on-target timing or per-write journal claim. The earlier
short-capture spectral check is inapplicable to this400-record capture and remains
reported as such, not silently replaced by a circular oracle.

Real PCM passes global activity/clipping/silence checks, unchanged stage08 finite-loop
discrimination in4 windows (DC, swapped-channel and each old-loop negatives), plus
all five gameplay tonal windows, RTIs396–400. Each matches independent original-
derived stereo pulse fundamentals; DC, swapped channels and wrong-left-tone negatives
reject in every window. Right pulse and triangle frequencies nearly coincide here:
this does not separately prove triangle amplitude, envelope/mixing fidelity, phase
continuity or NES noise fidelity. The backend is an explicitly approximate direct-
Paula finite-loop implementation. Final terminal silence is39.690s.

## Honest measured costs

Progression to last audio publication151.303330s; all400 updates late.
Final redraw238458 CIA ticks =336.150351ms. Redraw alone is not game throughput.

Existing CIA publication records show the five gameplay intervals, from completed
NMI plan RTI395→396 through399→400:
577.073750ms,536.384641ms,536.501644ms,536.181646ms,567.045261ms;
total2753.186942ms. Each interval includes the preceding renderer and intervening
native engine/scheduler/NMI/audio work. It excludes rendering after the final
publication and does not separately attribute engine versus rendering. These five
diagnostic measurements do not establish sustained FPS or playable speed.
No extra profiling instrumentation was added.

## Source-only tests and evidence boundaries

The explicit flat closure combines the frozen stage dependencies and reviewed
play dependencies, plus additive source/tests/reports. Historical manifests are
not recursively expanded during target restoration. No private disassembly,
resource, cartridge, firmware, capture, binary, PCM or disk belongs in it.

Public tests, with cartridge/original-oracle access denied, compile the actual
adapter and full target with synthetic resources and verify the exact embedded
engine. Results include11776 planner cases/23552 USER calls;262144 keyboard cases;
1024 title continuation/256 scanout contracts; independent Copper and spectral
negative regressions;16 linked composed frames;22 actual linked rejection/mute
cases;163 capture/layout cases covering every helper maximum plus global DMA bounds.
Capture tests enforce USER-mode/full-register/SP preservation, word/long width
access containment, exact independently formed output records and all memory guards.

Private results are play-target-verification.json, play-target-replay.json,
stage-target-noise-pcm.json, play-target-pcm.json, play-target-layout.json,
play-target-rejections.json and play-target-intervals.json. See restore instructions
for isolated source-only verification and exact final-source rebuild comparison.

Retained development evidence is explicitly distinct: v1 was never run because
an absolute telemetry reference was caught before capture. v2 completed and passed
its own actual-state, native-replay and PCM checks but used word-aligned capture.
v3 is a new separate real capture after explicit long alignment and source-only
regressions. v2 pixels/timing are not cited as evidence for v3. Later report/test-
only final-source rebuilding must match all four v3 target/adapter/boot/ADF artifacts.

Broader movement, scrolling, unexercised140/160 PHP/PLP branches, longer histories,
independent target review and performance optimization remain separate work.
