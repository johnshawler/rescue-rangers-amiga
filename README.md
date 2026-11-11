# Rescue Rangers native Amiga port: recovery branch

This is a **recovered early title/menu source baseline**, followed by clearly
identified new work. It is not the source of the later playable development
ADFs. Later gameplay, restart, rendering-optimization and audio source has not
been recovered and is not represented here.

Target: PAL Amiga A1200, 68020, AGA and 2 MiB Chip RAM. Stock hardware is preferred;
optional Fast RAM must remain within 8 MiB. The intended architecture is static
native game-code translation and Amiga rendering, not a general NES interpreter.

## Current recovery checkpoint

The [corrected audio verification](port/analysis/recovery_audio_clock_report.md)
supersedes the earlier total PCM-window alignment claim. Independent source and
runtime audit found that the emulator callback clock differs from nominal PAL
hardware. The additive verifier corrects both timestamp mapping and signal
frequencies. All four unchanged captures pass, with the same thresholds and
negative controls. Earlier reports and failed tests remain preserved. Printed
legacy milliseconds are **nominal PAL hardware-equivalent** conversions, not
measured physical-Amiga performance or callback wall-time.

The [five-neutral-frame target](port/analysis/recovery_play_target_report.md)
continues from reset through title selection, dialogue and stage loading into
five authentic gameplay frames. Its stock PAL A1200 emulator capture uses
860,160 Chip bytes and zero Fast RAM. Five publication intervals total 2.753
seconds in nominal PAL-equivalent units, and every update is late. The
[optimized stage target](port/analysis/recovery_stage_background_target_report.md)
reduces matched final redraw by 49.874%, with five-plane display DMA active and
zero Fast RAM. This is redraw cost, not game FPS or playable speed.

The [longer native host continuation](port/analysis/recovery_bank_loader_player_status_report.md)
now completes a bounded 240-frame goal for three genuine controller histories,
with original state and ordered effects retained. A separate
[grounded-jump investigation](port/analysis/recovery_bank_loader_jump_report.md)
compares 90 frames and proves matching original/native ascent and landing after
a correctly timed A press. Earlier A presses occurred during the initial fall
and were ignored by the original game. These are native game-state results,
not rendered target movement, playable speed or full-game completion. See the
[current gameplay checkpoint](docs/native-gameplay-checkpoint-2026-11-11.md).

The [combined optimized five-frame comparison](port/analysis/recovery_play_clock_report.md)
now joins separately reviewed runtime evidence with the corrected audio gates
and complete matched original execution histories. In this bounded diagnostic,
final redraw costs 50.070% less and the five publication intervals cost 30.562%
less in raw CIA ticks than the original-renderer control. Both still miss every
update deadline. Historical frozen reports retain their original pending or
failed labels; the [current correction summary](docs/recovery-clock-correction-2026-11-11.md)
records the superseding evidence and limits. No replacement game disk is released.
The delivered Z/X disk and all original inputs remain unchanged.

## Earlier preserved title/menu checkpoint

The new [bounded live integration](port/analysis/recovery_live_target.md) uses real
CIA keyboard input for title/character selection and continues the authentic
scene preparation through rendering disable, nametable clear and saved-bank
restore to FF53. Z=B, X=A, Return=Start, Tab=Select and arrows are wired through
the original controller interface. FF53 remains an explicit loader stop, not a
playable stage. The later lost gameplay source has not been recovered.

Final-source stock-emulator captures verify the visible title and character
menu, both choices, held/released/repressed input and a 617-update long path.
Original state, ordered effects, displayed pixels and bounded actual PCM checks
pass independent review. Allocation is 815,616 Chip bytes with zero Fast RAM.
The character-menu redraw measures 35.727 ms, and all 177 updates in the shorter
scene run miss the 20 ms interval. This is not full PAL speed or game FPS.
The final dirty/full scene captures differ in controller sampling and are not a
matched performance comparison. Audio fidelity and later gameplay remain limited.

The reviewed [sprite-footprint invalidator](port/analysis/recovery_redraw_contract.md)
restores old sprite coverage before repeated composition without changing the
frozen sprite renderer. The [scene continuation](port/analysis/recovery_scene_continue_report.md)
preserves genuine stack, mapper, video and audio behavior through FF53. Assembly-only
public checks run with `bash tools/test_redraw_public.sh` and
`bash tools/test_live_scene_assembly_public.sh`. The dedicated ROM-free compiled
adapter checks use `bash port/tools/recovery_live_public.sh` with the pinned GCC14
toolchain. These are separate from actual target capture validation.

This live diagnostic has explicit helper, input-log and audio limits; title
900-countdown/demo paths, two-player confirmation and arbitrary key combinations
are not fully qualified. All limit/error stops mute and drain audio. Original
inputs, historical captures and the delivered Z/X disk remain unchanged.

### Preserved host-stage-loading checkpoint

The additive [stage-loading sequence](port/analysis/recovery_bank_loader_finish_report.md)
continues through authentic dialogue, all 144 map expansions, object spawning,
stage-music initialization and fade-in to C77B, the first stage's main-loop entry.
Three continuous original/native histories match complete state and ordered
effects, with 394 or 395 logical NMIs. The separate map and object modules have
bounded, inert preflight checks and source-only reproduction tests.

This is a loaded-stage semantic checkpoint, not a completed gameplay update.
It has not yet replaced the stock title/menu diagnostic described above, and
no new target-speed or audible-output claim is made. Public checks use
`bash tools/test_stage_load_public.sh`; the original cartridge is required only
for separate private original-instruction comparisons. The delivered disk stays
unchanged.

### Earlier preserved checkpoints

The new [stage-loading foundation](port/analysis/recovery_stage_foundation.md)
extends the host-verified native chain beyond FF53 through the bank-2 resource
loader, fade, bank-5 object update, real NMI/audio work and return to 911C.
Three continuous original/native histories and independent adversarial tests
pass. The object translation uses a bounded, inert preflight before committing
changes. A separate full-redraw renderer passes all 512 horizontal origins
across two physical nametables. These additions are not yet integrated into the
stock target or a playable stage, and have no target-speed measurement.
Source-only checks run with `bash tools/test_stage_foundation_public.sh`.

The additive [background-only variant](port/analysis/recovery_background_target.md)
reduces the measured final render from 89.725 to 81.154 ms with display DMA on
(9.55%), and from 79.808 to 71.292 ms with it off (10.67%). Fresh uninstrumented
stock captures preserve original state, pixels and audio checks. The display-on
allocation is 811,520 Chip bytes with zero Fast RAM. This remains one final menu
render, well above a 20 ms budget, not continuous gameplay or a frame-rate result.
The frozen renderer and delivered disk stay unchanged. Public equivalence checks
run with `bash tools/test_background_public.sh`.

The additive [cost profiler](port/analysis/recovery_profile_target.md) identifies
background drawing as the largest part of the final render: 61.57 ms background,
24.53 ms sprites and 2.63 ms CHR copying in the instrumented display-on run.
Matched fresh controls reproduce the earlier timings. Instrumentation itself
adds about 42% to progression time, so these are diagnostic measurements, not
an optimization or a game-speed result.

The separate [Z/X input probe](port/docs/recovery_zx_input_validation.md) verifies
actual Amiga CIA serial presses and releases, including simultaneous Z=B and X=A.
It also covers Return, Tab and arrows. This is input-only validation, not yet
integration into the menu/gameplay loop. Public tests for both additions run with
`bash tools/test_profile_input_public.sh`; no game ROM or firmware is required.

The unchanged baseline [native menu/Paula diagnostic](port/analysis/recovery_menu_paula_target.md)
now plays actual native title/menu writes through four Paula DMA voices. Original
state and ordered effects match for both character choices and move-back; real
stereo captures verify bounded pitch/channel checks, native silence and clean
shutdown. Allocation is 811,008 Chip bytes and zero Fast RAM. Independent fault
regressions cover muted permanent stops and explicit error codes.

This is still scripted development, not full-rate gameplay. With active five-plane
scanout, the default path has 40 of 43 completed updates already beyond its 20 ms
minimum interval, and its single final render takes 89.73 ms. Earlier scanout uses
blank diagnostic planes. Audio continues its previous plan during long work;
that is not timely per-frame updating. At that predecessor checkpoint, live keyboard, later gameplay and accurate
NES synthesis remained unfinished. The delivered Z/X disk is unchanged.

Dedicated pinned GCC14 tests run with `bash tools/test_menu_paula_public.sh` using
synthetic data only. `bash validate_menu_paula.sh` runs the four private stock
capture variants and complete-target fault tests; it also needs matplotlib 3.10.8,
the approved inputs, and the pinned audio frontend/core. These C-toolchain checks
are separate from the assembler-only public aggregate. See the
[restore recipe](port/analysis/recovery_menu_paula_restore.md) for exact inputs and
limits. Generated audio, disks and state remain private.

The earlier [stock menu/SFX diagnostic](port/analysis/recovery_menu_sfx_target.md)
confirms both characters on the emulated stock PAL A1200, including moving
right then back left. Six fresh boots match complete final native state,
ordered device/audio journals and every captured viewport pixel. Independent
review reproduces those results. It uses 788,480 Chip bytes and no Fast RAM.
Its inputs and interrupts are scripted, audio was not attached, and execution stops
at C5F8 before gameplay. Timings include capture overhead with display DMA off;
they are diagnostic measurements, not game FPS. The old delivered Z/X disk is
unchanged.

A separate [audio-event compatibility audit](port/analysis/recovery_menu_audio_compatibility.md)
checks 15,059 original/native writes and all 1,966 completed-interrupt snapshots
from 14 histories against the unchanged compiled Paula planner. Every completed
snapshot passes with explicit muted noise initialization. Intermediate write
states can reject, so the integration must accumulate ordered writes and
update only at genuine completion boundaries. This is input-domain evidence,
not audible integration, faithful synthesis or real-time performance.

The earlier [state-driven character-menu display](port/analysis/recovery_state_menu_display.md)
now reaches and renders CHIP / DALE with the cursor on CHIP on an emulated stock
PAL A1200. Two independent fresh executions match all 1,091 contexts and
published journals, the first 64 full RAM boundaries plus final RAM, and every
captured viewport pixel. It allocates 1,297,920 Chip bytes and zero Fast RAM.
Inputs and logical interrupts are scripted; it stops at the first A06C menu
boundary. This is not an interactive selection loop, audible audio or gameplay.
Diagnostic timing includes journal clearing and captures, not game FPS.

A separate [minimally instrumented menu diagnostic](port/analysis/recovery_menu_timing.md)
removes those validation clears and captures while preserving the exact helper
and rendering code. Two fresh stock runs match final original state and every
viewport pixel, using 511,488 Chip bytes and zero Fast RAM. Progression takes
534,491 CIA ticks (0.753463 s); CHR mapping plus one render takes 56,381 ticks
(79.479376 ms), with display DMA disabled. These are separate, unscheduled
diagnostic intervals, not game FPS. Full boundary and poisoned-journal checks
run separately outside the measured path. This is diagnostic-overhead reduction,
not a gameplay or rendering optimization claim.

The additive [state-driven menu dispatcher](port/analysis/recovery_state_dispatch_menu.md)
now follows genuine Start input into character selection, consumes the queued
video work, and handles held/released/repressed Start to confirm the default
character. Ten uninterrupted original-first host comparisons match 65,195
native boundaries and 16,702 ordered APU writes. Neutral and ignored-A paths
each complete all 900 countdowns and the full title music sequence. This is
host logical-runtime evidence, not live input, target rendering or audible
sound. Title selection SFX at F379, character cursor/SFX at A07B and gameplay
after C5F8 remain outside this composition. Its 134,638-byte journal capacity
and size sentinel are documented; old callers must not use their smaller
startup journal with this new entry.

A newer [state-selected menu/SFX composition](port/analysis/recovery_state_menu_sfx.md)
joins genuine cursor movement, sound shutdown and continued music to the native
dispatcher. Fourteen original-first host histories match 59,821 boundaries and
15,059 APU writes, including delayed, repeated and alternating input. Both
original- and alternate-character confirmation are verified through actual
cursor, table and character-marker state, not merely the terminal PC. A separate
narrow return bridge handles delayed input without relaxing the older tail's
guard. The full long journal and size sentinel remain required. This composition
has the separate scripted stock-target qualification above. Live Amiga input
remains unimplemented; audible qualification is the newer bounded diagnostic. Gameplay at C5F8 and the title-direction continuation at A055 remain
unsupported, along with the documented SFX dispatch limits.

The new [state-driven startup display](port/analysis/recovery_state_startup_display.md)
executes 990 native operations selected from live game state, completes startup
resource loading and fade-in, then draws the title on an emulated stock PAL A1200.
Two fresh runs match the independent original-code/device replay and every
captured viewport pixel. It allocates 1,187,840 bytes of Chip RAM and zero Fast RAM.
It uses neutral input and 35 scripted logical NMIs, then holds the title. It is
not an interactive game, an audio integration, or a speed measurement. The old
fixed-schedule display remains preserved separately.

An isolated [direct-Paula audio experiment](port/analysis/experimental_direct_paula_lab.md)
replays 935 title-frame register snapshots through four hardware DMA voices.
Independent stock-configured emulator capture verifies the tones, finite noise
loops and channel separation. Instrumented backend updates peak at 221.32 us
with display DMA off and no concurrent game workload. Its 32 KiB Chip allocation
excludes OS/boot memory. This is an approximation with frame-final snapshots,
noise bias and simplified phase/counter handling, not integrated game audio or
NES fidelity. [Reproduction instructions](port/analysis/experimental_direct_paula_restore.md)
regenerate the private profile from the approved cartridge; no music data is
included in the repository. Its dedicated C-toolchain checks are separate from
the assembler-only public aggregate. The new compatibility audit is also
separate: run `bash validate_menu_audio_compatibility.sh` with the m68k C
toolchain available. Generated event streams and plans remain private.

The new [stock character-confirmation diagnostic](port/analysis/recovery_character_confirmation_target.md)
executes 1,196 native calls on the emulated PAL 68020/AGA A1200. Five complete
Amiga resets collectively verify every full-RAM boundary, with zero Fast RAM and
a maximum 1,299,456-byte Chip allocation. Its declared original-code start is
FE24 after hardware warmup. It uses fixed diagnostic scheduling and scripted
controller release/repress, not live controls, displayed menus or game-speed evidence.

The separate [fixture-free native startup display](port/analysis/recovery_startup_display_native.md)
now draws a frozen title from the real native startup's video state on the
emulated stock A1200. Original-ROM device replay matches every framebuffer byte
and captured viewport pixel. It builds from the cartridge and firmware without
the legacy fixture archive. It has no live menu input, gameplay or audible sound.

An additive [compact renderer experiment](port/analysis/startup_render_unrolled_experiment.md)
saves 6.39% against its identically instrumented control, but still takes about
73.72 ms with display DMA off. This is an isolated rendering measurement, not a
real-time game result. Its allocation remains 1,283,072 bytes of Chip RAM with
zero Fast RAM. The original display and delivered Z/X disk remain unchanged.

New host-native comparisons separately cover the complete [title/music timeout](port/analysis/recovery_music_command0f_loop.md):
900 countdowns, 28,818 calls and 935 logical NMIs. Default character confirmation
continues through [scene fading and sprite hiding](port/analysis/recovery_scene_sprite_hide.md)
to F3D5. Genuine Left/Right input now completes [SFX channel reconfiguration](port/analysis/recovery_sfx_channel_reconfigure.md)
and authentic returns to 8060 without skipping the queued sound. Rendering
disable at F3D5 remains untranslated. New [SFX phase/dispatch translation](port/analysis/recovery_sfx_phase_dispatch.md)
continues genuine phase accumulation, channel-3 music processing and the
channel-2 SFX call to 82B0, preserving the still-pending NMI and real return
frames. Independent original-instruction checks pass; this is host correctness,
not completed SFX playback or integrated audio. The new
[SFX tick entry and command parser](port/analysis/recovery_sfx_command_mask.md)
then performs genuine instrument/channel changes and reaches event action 831B
after 1,216 helpers. It preserves the pending NMI and real caller frames, with
62 new RAM writes and 13 resource reads on the cursor path. Independent raw
status/stack and original-instruction tests pass. The subsequent
[SFX event action](port/analysis/recovery_sfx_event_action.md) now returns to
the real caller and allows the frozen helpers to complete the first mixed
music/SFX NMI: 1,231 helpers, 41 logical NMIs and 39 completed returns, with
bank 2 restored. New [active-SFX control](port/analysis/recovery_sfx_active_control.md)
then carries the following interrupt through genuine countdown and mixed
processing to envelope 86B2: 1,246 helpers, 42 logical NMIs and 39 returns.
The separate [SFX envelope](port/analysis/recovery_sfx_envelope.md) now completes
that second mixed interrupt and follows both Left and Right histories through
53 genuine returns. It qualifies direct SFX publication, pitch scaling and raw
status-stack behavior without changing the frozen music guard. The longer
histories execute 1,765 helpers and 16 SFX envelopes before stopping at the
untranslated high-bit stream command at 8235; the sound remains active. These
original-code proofs begin at FE24 after hardware warmup. The subsequent
[SFX stream control](port/analysis/recovery_sfx_stream_control.md) now follows
genuine sound shutdown and 22 more completed returns in both cursor-direction
histories. It reaches 2,442 helpers, 78 logical NMIs and 75 returns. The endpoint
is an intentional composition stop before music command 0E, whose existing
helper separately accepts that state. The odd-D7 header path still stops at
80FB. Full audio integration, alternate-character confirmation and gameplay
remain unfinished. This is host evidence, not audible output, reset-vector
warmup or Amiga game-speed validation.

The [state-driven startup dispatcher](port/analysis/recovery_state_dispatch_startup.md)
completes resource loading, genuine CHR requests and title fade-in through C5D1.
Eight original-first histories each match 990 native operations and 35 logical
NMIs. C5D1 title-engine/menu processing remains outside this frozen startup
entry and is supplied by the separate menu dispatcher above. Its
32,770-byte journal and 1 KiB native scratch stack are caller requirements.
Helper boundaries differ from the old fixed-schedule probes, so the lower call
count is not a speedup. Full host correctness and the bounded target evidence
are reported separately.

Run tools/test_native_title_public.sh, tools/test_scene_sound_public.sh,
tools/test_runtime_sound_public.sh, tools/test_state_startup_public.sh and
tools/test_state_menu_public.sh, tools/test_sfx_phase_public.sh and
tools/test_sfx_parser_public.sh, tools/test_sfx_event_public.sh and
tools/test_active_sfx_public.sh for
ROM-free contracts. Their corresponding private extensions are
validate_native_title.sh, validate_scene_sound.sh, validate_runtime_sound.sh and
validate_state_startup.sh, validate_state_menu.sh, validate_sfx_phase.sh and
validate_sfx_parser.sh, validate_sfx_event.sh and validate_active_sfx.sh.
The new startup/display extension needs only the
approved private cartridge and firmware, not old captured fixtures.

An earlier isolated [resident startup diagnostic](port/analysis/recovery_resident_chr_fade_target.md)
reaches $C5D1 through 1,024 native helper calls and 35 logical NMIs. Four
independent full-reset stock A1200 runs collectively capture every complete RAM
boundary while each checks every context and journal. Maximum diagnostic
allocation is 1,075,200 bytes of Chip RAM with zero Fast RAM. Genuine pending
CHR requests are consumed and title fade-in completes. This remains diagnostic
startup validation, not an integrated playable game, displayed native boot,
audible music or a performance measurement. The later playable source is still
unrecovered. See the [host proof](port/analysis/recovery_title_chr_fade.md) and
[separate command02 music tests](port/analysis/recovery_repeated_command02_audio.md)
for their distinct coverage and remaining boundaries.

- Native title player-count and Chip/Dale selection, input edges, timer/random
  primitives, sound-request queue and title nametable updates.
- Native background and sprite rendering with source-independent synthetic tests.
- The title milestone rebuilds byte-for-byte to its original development ADF.
- Its menu handoff intentionally stops before untranslated gameplay. No native
  stage or audible sound is implemented by this recovered source baseline.
- A newly written, isolated reset-RAM helper matches original instructions at
  $FE24–$FE42, including all 2,064 ordered RAM writes. It is not integrated into
  title boot; hardware warmup and later startup remain incomplete.
- A separate new mapper-publication helper continues $FE43–$FE66 with an
  explicit ordered journal: 20 logical MMC1 writes plus 14 original RAM writes.
  Its 2,048 original-ROM/native cases preserve register, stack and busy-state
  semantics. This does not yet select native resources or implement audio.
- New video-clear and first-dispatch helpers extend the bounded path to $C574.
  A continuous original-ROM comparison covers all four helpers, including
  2,188 ordered PPU events, without inserting captured game state between them.
  They remain separate from the stable title and stop before the first task.
- A [separate stock-A1200 probe](port/analysis/recovery_reset_probe.md) executes
  those four helpers and matches all original RAM, context and journal records.
- An opt-in [first-yield probe](port/analysis/recovery_first_yield_target.md)
  adds the task prefix, sound-request enqueue and saved continuation. All five
  helpers match the original through the first yield.
- An opt-in [NMI audio-entry probe](port/analysis/recovery_nmi_audio_entry_target.md)
  injects one logical NMI at the chosen first-yield boundary and follows the handler
  to the bank-3 sound-request entry. It matches RAM, interrupt stack, timer,
  mapper, PPU and OAM DMA results. This probe stops before banked audio executes.
- An opt-in [audio-reset probe](port/analysis/recovery_audio_reset_target.md)
  additionally executes the native startup mute/reset command. Its seven APU
  register writes match the original as explicit data. Sound synthesis, Paula
  playback, the subsequent tick/NMI return and scheduler resumption remain outside it.
- An opt-in [NMI-return probe](port/analysis/recovery_nmi_return_target.md)
  completes the first silent tick, restores the original bank and interrupt
  context, and stops before the scheduler resumes. Its canonical status ABI
  preserves all physical flags while explicitly distinguishing py65's virtual B bit.
- An opt-in [scheduler-resume probe](port/analysis/recovery_scheduler_resume_target.md)
  continues through task selection and complete standard-controller polling,
  preserving all eighteen serial-input records and the original task stack.
  Ten helpers reach $C584 before the resumed task.
- An opt-in [resumed-task setup probe](port/analysis/recovery_resumed_task_setup_target.md)
  adds native sound-request enqueue and palette preparation through the next
  nested scheduler yield. Eleven helpers preserve the pending palette and audio
  requests, which still need later interrupt support. This slice guards D=0 to
  avoid generic py65 decimal arithmetic differing from the NES CPU.
- An opt-in [palette-NMI probe](port/analysis/recovery_palette_nmi_target.md)
  follows the second logical interrupt through palette publication and timer
  updates. Twelve helpers preserve the real nested interrupt frame, all 49 new
  video events and a second OAM snapshot; queued music remains unconsumed.
- An opt-in [private music-initialization probe](port/analysis/recovery_music07_target.md)
  consumes the queued command and initializes its channel pointers. Fourteen
  calls use thirteen distinct helpers; the subsequent music tick is not run.
  This diagnostic contains a private cartridge resource view and must not be
  distributed as a source-only disk.
- Separate [private fetch and command04 probes](port/analysis/recovery_first_music_target.md)
  now verify the first music-byte fetch and command on the emulated stock A1200.
  They stop before $83A0 and $839D, using fifteen and sixteen calls respectively.
  Full original state, resource reads, original frames and hardware journals match.
- New [reusable fetch and command05 helpers](port/analysis/recovery_music_stream_command05.md)
  preserve the next command's tempo updates. The
  [private channel-setup target](port/analysis/recovery_music_channel_setup_target.md)
  now continues through commands06 and07 on the emulated stock A1200, with
  twenty-two calls to nineteen helpers. Six intermediate contexts, full state
  and seventeen resource-read records match. The subsequent
  [private first-channel event target](port/analysis/recovery_music_first_channel_target.md)
  now completes instrument/control setup and the first rest event through the
  original channel return: thirty calls, twenty-three helpers and thirty-three
  resource records. The later resident runtime probe below completes the remaining channels
  and initial active tick; the further resident fade target below verifies repeated
  ticks. Audible playback remains incomplete.
- A separate new [player-initialization helper](port/analysis/recovery_gameplay_player_init.md)
  matches 131,072 original-ROM cases. Its
  [source-only stock-target probe](port/analysis/recovery_gameplay_player_init_target.md)
  verifies six invented states, including inactive players and stack wrap.
  It enters $C6BD synthetically and stops before $C700. A new
  [source-only fade-entry target](port/analysis/recovery_gameplay_fade_entry_target.md)
  continues the same live state through the first palette attenuation pass,
  including raw decimal status and original nested call frames.
- A [private stage-resource target](port/analysis/recovery_stage_resource_target.md)
  now starts earlier at $C6B5, initializes bank-4 pointers and composes player
  setup plus fade entry. It requires no deferred audio ($F6=0), an empty mapper
  latch and PRG mode3. Live title-to-stage entry, deferred-audio handling, frame
  synchronization and remaining stage loading are still incomplete. All stage
  probes stop before $FF04 synchronization and are not integrated gameplay.
  The title and delivered playable disk remain unchanged.
- A new [bounded resident runtime target](port/analysis/recovery_runtime_target.md)
  runs reset, first silent NMI, actual FE90 idle scan, second NMI, the complete
  initial music tick, bank restore/RTI and genuine saved-task resumption at
  $C2A8. The emulated stock A1200 runs 68 native calls with resident RAM/context.
  All 68 full state snapshots, 40 mapper, 2,248 PPU, 14 APU, 36 controller and
  94 resource records plus 512 DMA bytes match continuous original execution.
  Its private diagnostic carries cartridge data and must not be distributed.
- New general scheduler, frame-yield and idle-NMI helpers also compose with the
  synthetic stage initialization without fabricating readiness. Indexed music
  commands, rest/pitched events and the active interrupt return now have
  exhaustive synthetic and original-ROM checks. Those original helper-local boundaries remain useful regressions. The newer
  resident startup target below implements the fade countdown and repeated
  active envelopes, while callbacks, nonempty video queues and authentic
  title-to-stage loading remain incomplete.
- A [private resident startup-fade target](port/analysis/recovery_resident_fade_target.md)
  now continues from reset through $C597: 533 native calls, 18 logical NMIs,
  16 subsequent music calls and 114 APU writes in total. The emulated stock PAL
  A1200 matches all 533 full RAM/context snapshots, ordered hardware/resource
  journals and 4,608 DMA bytes. Its cleared Chip allocation is 1,374,720 bytes.
  Target snapshots are distinguished from the host harness's per-access trace.
  Corrected active-control guards also pass 16,128 arbitrary-return regressions.
- Separate [resident host video setup](port/analysis/recovery_startup_video_clear.md)
  extends the same native state to $C5BB in 534 calls. It implements rendering
  disable, OAM/object/camera initialization and nametable/attribute clearing.
  This additional slice is host-tested, not included in the 533-call Amiga
  diagnostic. Bank-2 resources, deferred audio and later CHR/video work remain.
- [Repeated music tests](port/analysis/recovery_repeated_active_audio.md) cover
  41 standalone calls per sequence before unsupported command02. They include
  envelopes, duration changes and command03, with explicit CF-callback guards.
  Register journals are not sound playback: no integrated Paula renderer,
  audible game output, gameplay-speed result or new playable disk is supplied.
- Captured initial title state remains a private development fixture. New work
  will replace that dependency with verified original reset/resource logic.

Recovered title baseline validation passed 142,896 original-ROM differential cases, 27 synthetic
renderer cases and 16 native selftests. Five cycle-exact emulated PAL A1200 menu
scenarios were pixel-exact against preserved original references and actual
Amiga display output. These are correctness results, not gameplay-speed claims.

The separately preserved later Z/X ADF is an older, silent, incomplete playable
binary. Its recovery smoke test does not imply that its source is present here.
See [recovery provenance](docs/RECOVERY.md) and the validation summary. The new helper is documented in
[the reset boundary report](port/analysis/recovery_reset_ram.md) and
[mapper-publication report](port/analysis/recovery_reset_mapper.md), plus the
[video-clear](port/analysis/recovery_reset_video.md) and
[first-dispatch](port/analysis/recovery_reset_dispatch.md) reports.

## Build and test

Install Python dependencies from `requirements-dev.txt`. Supply vasm via the
`VASM` environment variable. `bash tools/test_public.sh` runs the two synthetic
assembled-code renderer suites, restore-safety tests, a synthetic twelve-helper
contract regression, synthetic music/stage/runtime-helper contracts (including
inert rejection and boundary checks), repeated-audio/fade/video contracts, and
ten source-only probe assemblies
without a game ROM or firmware.

Private original-ROM tests require the hash-checked European cartridge at
`input/rescue-rangers-europe.nes`. The full title build also needs the original
private title fixture pack under `port/assets/` and `artifacts/`; firmware is
needed only for target emulation. Use `python tools/restore_private_inputs.py`
with a preserved recovery bundle and supplied inputs to install them safely.
The helper validates every included fixture and refuses to replace mismatching
existing files. `python tools/restore_private_inputs.py --help` describes inputs.

For full validation, set `VASM`, `PUAE_CORE` and `HEADLESS`, then run
`bash validate_recovery.sh`. This includes eighteen separate emulated-target diagnostics, negative
dump/build-gate checks and five title-display scenarios. The appended
`validate_resident_startup.sh` extension expects the baseline probe outputs
produced earlier in the full script. For synthetic extension tests alone, run
`bash tools/test_resident_startup_public.sh`.
Pinned tool revisions and hashes are recorded in
`docs/recovery-validation.json`. Compile `scripts/headless.c` against the
libretro headers with `-ldl -Wl,--no-as-needed -lm`.

Do not commit cartridge/firmware bytes, extracted game assets, captured state,
screenshots, compiled game disks or private reference dumps. The public CI uses
synthetic data only. A fresh-clone restore is checked privately with authorized
inputs; it does not make those inputs public.

This is an incomplete development project, not an official release or a claim
of full-game compatibility, full PAL speed, or physical-hardware validation.
