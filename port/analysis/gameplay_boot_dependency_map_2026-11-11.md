# First-stage boot dependency map

Read-only investigation, 11 November 2026. Only this new report was written. No implementation, existing report, fixture, delivered disk or other project was changed. The Europe ROM was read locally and its SHA-256 verified as `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`. This document contains conclusions and address references, not cartridge extracts or execution traces.

## Principal conclusion

Do not connect the title phase-3 flag directly to $C6B5. The menu's original bank-2 $A0C8 return belongs to the call at fixed-bank $C5F5 and continues at $C5F8. Normal player start first runs an additional bank-2 $9000 sequence with $31=$0B. Only after its return at $C60A, resetting $31 to zero, and calls through $C63B and $C645 does $C614 call $C6B5. The timeout/demo branch instead copies $BD to $31 and joins at $C60E. The synthetic stage chain establishes neither branch's real entry state.

The current title executable itself restores captured RAM and uses captured nametable/CHR/OAM resources. Its two-byte menu coroutine deliberately excludes the original page-one stack from equivalence and returns inert phase 3. Consequently an authentic stack-preserving reset-to-title-to-stage chain cannot be obtained simply by appending the newer helpers to that executable. Retain the verified menu behavior, but implement the original caller/yield continuation and startup resource generation. Do not fabricate the missing original caller stack from the snapshot.

## Evidence strength

- Inspected source, tests and reports establish the recovered title scope, the reset/two-NMI/music prefix and synthetic stage composition contracts. Reported historical counts were not rerun in this planning task.
- Targeted disassembly of the hash-checked cartridge established the call edges and continuation PCs below. These are static control-flow facts, not a full dynamically observed boot trace.
- No new reference reset-to-gameplay execution, stage screenshot, target test or audio recording was produced. Live bank, task, flag and resource prerequisites remain to be measured from continuous execution.

## Concrete control-flow dependencies

### 1. Reach the real title caller without captured state

The verified startup prefix begins at $FE24 after earlier hardware warmup, dispatches to $C574, yields at $C581 and resumes $C584. The second nested palette yield is not the title entry. Finish its active NMI/music work and general scheduler resumption so the original nested palette operation can finish. The next main-task continuation after the outer $C594 yield is $C597.

The remaining pre-menu sequence includes rendering disable $C14E, OAM cleanup, reset of game/object memory via $C61A, display/camera variables, $C1BA video work, bank-2 selection via $FF53, bank-2 $8000 resource loading with X=2, bank-2 $8820, rendering enable $C158, the $C5CB yield (resume $C5CE), fade-in $C26E, character/setup table reads and countdown initialization, then $C5F5 calling bank-2 $A000. These operations must generate the RAM/resources formerly supplied by the title fixtures.

Preserve the original menu yield/resume semantics: $A022 returns to $A025; $A069/$A086 resume at $A06C/$A089 respectively in the original stream. The recovered phase-2 abstraction combines character-menu evaluation and is not an original-PC scheduler frame. Preserve its user-visible behavior without treating its two-byte host context as an original CPU context.

### 2. Complete the real post-menu sequence

$C5F8 selects normal start versus demo. Normal start: $C603 sets interstitial index $0B; $C607 calls bank-2 $9000; $C60A restores first-stage index zero; $C60E calls $C63B; $C611 calls $C645; $C614 calls $C6B5. $C63B clears four counters; $C645 sets HUD/OAM state with player-selection-dependent handling. Neither can be assumed already performed by the standalone player initializer.

Bank-2 $9000 is substantial, not a one-instruction wrapper: its static dependencies include $F3C9, $8D0A, bank-2 $8000 resource loading, indexed CHR/palette requests, $F3E5, $F392, $92AC and $8D16 before its return. Index-dependent branches also exist. Inspect actual index-$0B execution to identify required transitive branches; do not skip this sequence because the eventual stage index is zero. The demo path has different data and should be a separate acceptance case.

### 3. Turn the synthetic stage prefix into a complete stage load

Reusable prefix: $C6B5 -> bank-4 $8000 -> $C6BD player setup -> $C700 -> $E096 -> $C247 -> $C274 -> $C2A5 -> $FF04 -> $FE8D. This is already a meaningful bounded composition, but not an entire loader.

Resume the saved fade frame at $C2A8, execute its delay iterations and attenuation loop through $C2BD, and return through the real stack to $C24A. Then execute object reset $C235, OAM hide $C21E and the tail yield at $C250. Its eventual return continues $E099, not $C703.

$E099 onward loads stage-indexed geometry/camera/bank/music data; requests audio through $F377 when not in demo; calls $C2F7 and $C317; calls $E179 and $E754; enables display via $C158; and yields at $E10C, resuming $E10F. For first stage zero the special stage-$0D setup is not selected. The tail at $E176 enters $C253: stage zero selects bank 5 and calls its $8000, then enters fade-in $C26E. Only its actual completion returns through the outstanding $E096 call to $C703. Position snapshots finish at $C716; the caller then executes $C617 and enters the main loop at $C77B.

$E179 is another substantial dependency: it resets object/display/camera state and fills the initial map via the $DBEC loop. For stage zero its tail selects bank 4 and calls $8040 and $8090. The existing bank-4 $8000 pointer initializer does not implement these operations. $E754, $DBEC, their indexed resources, and the bank-5 $8000 object/sprite path need separate discovery and translation as part of one loader milestone.

### 4. Reach an actual playable frame

The main-loop entry is $C77B. For the ordinary unpaused branch, static calls include $C879, bank-6 $8000, $D6A3, bank-4 $8090, conditional $E576, $E9C9, bank-5 $8000 and PRNG $C2DC. It yields at $C845, resumes $C848 and normally loops via $C85E to $C77B. These call edges are not proof of which internal routines are reached for first-stage input. Establish a continuous first-stage trace before assigning detailed collision/player/object subroutines. A first rendered stage can precede a playable one; label them separately.

## Shared machinery that must become coherent

### Scheduler and interrupts

The $FE8D scheduler supports four task slots, readiness scanning, fresh-task entry (state 8), saved-stack resume, task-zero controller polling at $FECD and X/Y restoration at $FED0-$FED4. The existing scheduler-resume helper guards one specific startup frame ending at $C584; it is not valid for the fade frame at $C2A8 or menu frames. Generalize the finite original scheduler paths rather than rewriting RAM to satisfy that helper.

$FF04 saves wait state/count and the original stack; timer processing at $C0A1 advances waiting tasks. The new frame-yield helper only saves that state and stops at $FE8D. Execution must allow actual logical NMI readiness, interrupt stack preservation and resumption without manufacturing return frames or clearing pending state. Add interrupt interleaving tests around mapper busy sections, not just uninterrupted helper calls.

NMI branches needed beyond narrow prefixes include queues $1C/$1D/$19 via $C119, CHR bank requests $1A/$1B via $FF1F/$FF39, palette publication $18, scroll/control registers, OAM DMA, timers, sound queue drain, active audio tick and bank restoration. The original $F5 busy path can increment $F6; $FF75-$FFAA subsequently services deferred audio before restoring the requested PRG bank. The stage initializer's $F6=0, PRG mode 3 and empty serial-latch prerequisites must arise naturally or its missing branch must be supported. Clearing $F6 is not an integration strategy.

### Resources and native rendering

Use explicit mapper/resource views with ordered publication and well-defined CHR/nametable/palette/OAM ownership. The existing title queue consumer supports a single collapsed 1024-byte nametable and increment-by-one mode only. The existing background renderer draws an unscrolled 32x30 tile surface; its dirty key contains tile number and attribute palette, not CHR-bank identity. CHR changes require invalidation. Stage camera/scroll and multi-nametable semantics cannot be assumed from the static title adapter.

The sprite renderer is useful existing native code for 8x8 sprites, OAM ordering and priority, but explicitly rejects 8x16 mode. Verify the actual stage control modes. Wire stage-produced OAM, palettes, CHR selections and map updates to real Amiga output, including removal of old sprite coverage and cache invalidation, rather than substituting an image. Rendering tests must validate changed banks, scrolling, clipping, priority and palette transitions with synthetic fixtures and private reference comparisons.

### Audio

Queueing requests or journaling APU writes is not sound. Complete all dynamically reached setup/stream commands, remaining channel iterations, pitched events, duration/envelope/modulation progression and callbacks, then the active tick's original return and NMI bank/context restoration. Indexed helpers currently visible cover fetch, selected commands and rests, not all these behaviors. A separate native audio engine must translate the resulting APU state over time into Paula/DMA output, with pitch, envelope, noise and any actually used DPCM path handled. Test both register/state equivalence and captured audible waveform/output. Do not silently suppress title/navigation/stage requests to make boot advance.

## Recommended coherent milestones

1. **One persistent reset/frame runtime.** Finish active NMI return, general four-task scheduling, mapper/deferred-audio semantics and palette delays with one live original context. Acceptance: continuous reset-to-post-startup continuation, repeated yields and input polling, no RAM patches/captured state. Keep original warmup boundary explicit until implemented.
2. **Fixture-free title and authentic handoff.** Complete startup resources and menu caller integration, then the normal bank-2 $9000 sequence through $C614. Acceptance: reset-generated title, Chip/Dale/two-player choices and real $C6B5 entry state observed against reference, including bank/stack/$F6 provenance.
3. **One complete stage loader and first native picture.** Consume the existing stage prefix, finish fade/load/fade-in through $C716/$C77B, and implement the resource/video adapter needed by that path. Acceptance: first-stage scene rendered from live generated resources, matching reference state and actual display; explicitly not yet playable.
4. **One complete interactive stage frame loop.** Translate the actually reached $C77B-$C85E paths and transitive player/object/map work. Acceptance: repeated frames with movement/jump, collision and camera behavior from real inputs, including pause and two-player scenarios only when implemented. Report unsupported branches, not silent skips.
5. **Audible end-to-end output.** Develop the native synthesis/backend in parallel with milestones 1-4, but gate completion on continuous music/effects across title, handoff and stage, correct NMI return and actual audible output. Keep timing/performance measurements separate from semantic correctness.

These milestones deliberately retain coherent original sequences rather than multiplying isolated one-boundary helpers without an integration owner. Static native translation remains the intended architecture; a reference CPU may be used privately for testing, not as the production game runtime.

## Local evidence consulted

README.md; port/src/title.s; native_rescue_title.s; native_rescue_game.s; native_background.s; native_sprite_blitter.s; recovery_gameplay_frame_yield.s; indexed music helper headers; port/tests/test_rescue_game.py; and analysis reports NATIVE_TITLE.md, NATIVE_GAME.md, recovery_scheduler_resume.md, recovery_stage_resource_init.md, recovery_gameplay_fade_entry.md, recovery_gameplay_frame_yield.md, recovery_music_channel_iteration.md. Historical report statements that a newer helper is absent should be read at their original boundary, not as a current inventory. Other unfinished changes were not modified or validated by this investigation.
