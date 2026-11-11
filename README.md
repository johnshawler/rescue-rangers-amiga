# Rescue Rangers native Amiga port: recovery branch

This is a **recovered early title/menu source baseline**, followed by clearly
identified new work. It is not the source of the later playable development
ADFs. Later gameplay, restart, rendering-optimization and audio source has not
been recovered and is not represented here.

Target: PAL Amiga A1200, 68020, AGA and 2 MiB Chip RAM. Stock hardware is preferred;
optional Fast RAM must remain within 8 MiB. The intended architecture is static
native game-code translation and Amiga rendering, not a general NES interpreter.

## Current verified source

The newest isolated [resident startup diagnostic](port/analysis/recovery_resident_chr_fade_target.md)
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
