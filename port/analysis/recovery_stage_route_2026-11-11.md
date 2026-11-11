# Authentic original route into first-stage play

Read-only original-cartridge research, not native implementation or hardware proof.
Only this generic report and new private tracing files were created. Original,
existing source, historical captures and delivered disk were not modified.
The approved Europe cartridge SHA256 was checked before each run.

## Dynamically established route

A continuous original CPU run begins at the established FE24 post-warmup boundary,
with the same power-on RAM seed and register assumptions as the reviewed scene
reference. No later RAM/context/stack reload or fabricated scene entry is used.
Existing original-only boundary selection drives the prefix. FF53 is reached
after 126,160 instructions and 60 logical NMIs, with genuine bank 2, F5=F6=0,
index 0B, SP=BB and control 1E. This is not a new hardware-reset timing proof.

- FF53 completes in 17 instructions to bank 2:9003, SP=BD. It then enters 8D0A,
  calls bank 2:8000 twice, enters F3E5/fade and reaches F392 at NMI77.
  Interstitial CHR banks are both 0D. F392 calls bank 5:8000 before 92AC at NMI78.
- 92AC is a real dialogue sequence, not an automatic loader. With neutral input
  it keeps yielding, animating and processing audio. Static inspection confirms
  940D checks newly pressed A (bit 80) to advance and Start(bit 10) to exit for
  index 0B. Controller Start pulses after NMI300, on nmi modulo 120 below 30,
  legitimately leave dialogue at NMI360. Input is supplied only at the original
  scheduler controller read, through 4016/4017; game RAM is never patched.
- Return path:8D16, C60A, C63B, C645, C6B5. Actual C6B5 has stage 0,
  A=8C/X=28/Y=28/SP=BD, F5=F6=0 and mapper 1E/0D/0D/02.
- Loader: bank 4:8000 pointer initialization, C6BD player initialization, C700,
  E096 fade/yield, E099 at NMI377, C2F7/C317, E179. Its map initialization
  executes 144 calls to DBEC, switching into bank 0 for data. It then calls
  bank 4:8040 and 8090, E754, yields to E10F at NMI378, enters E176,
  bank 5:8000 and fade-in, and returns C703/C716 at NMI394.
- First C77B is at NMI394. A short neutral continuation completes four loops
  and reaches C77B five times:765,942 total instructions,398 logical NMIs.
  The dynamically reached per-frame calls include C879, bank 6:8000, D6A3,
  bank 4:8090, E9C9, bank 5:8000 and C2DC. E576 was not taken.

## Bounded movement and video requirements

A further run supplies Right with periodic A presses for 240 original loops
(241 C77B entries), completing 2,253,791 instructions and 634 logical NMIs.
The instruction ceiling is 4,000,000. No unsupported CPU-bus read/write assertion
was encountered. This establishes original control flow, not native play.

First-stage PPUCTRL is 90, mask 1E, MMC1 control 1E, CHR0=00 and CHR1=10.
No 8x16 sprite or changed CHR mode is needed on this tested route. At first C77B
scroll X/Y is 0/0. First nonzero scroll publication is at original C08B,
NMI458, after 64 loop entries, with X=2. After 240 movement loops X=166/Y=0.
PPUCTRL nametable bits remain zero throughout this short route; horizontal
scroll nevertheless samples into the adjacent nametable. This does not establish
what happens after crossing a full 256-pixel camera boundary.

Post-FF53 ordered PPU address observation counts 1,565 writes in 2000..23FF,
843 in 2400..27FF, and 384 palette writes. Control 1E means vertical mirroring,
so these two nametable pages are physically distinct. CHR bank changes must
invalidate decoded/background caches. OAM DMA and palette/nametable queues
remain active through dialogue, loading and gameplay.

Important current-source correction: recovery_state_menu_display_device.s
already allocates 2048 nametable bytes and resolves MMC1 mirroring. It does not
collapse 2400 into 2000. Historical descriptions of a 1024-byte collapsed consumer
must not be applied to this current adapter. The current live bridge/scanout
and background renderer remain unscrolled; after first accepted display a
nonzero scroll causes explicit rejection. The needed extension is scrolling
composition across both physical nametables, with safe cache keys/invalidation,
clipping and sprite coverage restoration, not merely enlarging that consumer.
The helper-ID-specific journal/DMA dispatch must still be extended for new
loader/frame helpers rather than assumed compatible automatically.

Movement adds 59 distinct call edges beyond the short neutral trace. Important
regions include fixed F000/F21E/F5A6/EA8F physics/object work, bank 6:8E15→F977
and F92B, and D6A3→D9F6/DB50 or DA50/DB90 map/camera paths feeding
E06B/DF8A/E01B and bank 0 resources. Calls into F379 also demonstrate new sound
requests. These are dynamic addresses, not a claim that every routine's full
behavior has been translated or that all movement branches are covered.

## Reuse and implementation priorities

Verified current native source already contains stage_resource_init(C6B5→C6BD),
gameplay_player_init(C6BD→C700), gameplay_fade_entry, frame_yield, general
four-task scheduler, palette/queued-video NMI machinery, startup fade helpers,
and controller/timer/OAM/PRNG primitives. Their current entry guards and ABI
must be checked against this authentic state; existence is not integration.
No existing recovery translation of DBEC/E179/E754/C879 was located in current
port/src by address/symbol search. Larger transitive regions above still require
native implementation or explicit discovery of equivalent code.

Prioritize one coherent index 0B dialogue/return (including its bank 5 work),
then one complete loader with DBEC/map resources and bank 4 object preparation,
then recurring player/camera/object/sprite regions. Keep authentic scheduler,
active audio and device publications in all three, and compare persistent
native state against this original route. Do not substitute captured state,
images, pre-cleared F6, shortened dialogue or a synthetic stage caller.

## Limits and reproduction

The private bus is the existing reference controller/MMC1/APU/PPU journal
adapter. It does not render a PPU, emulate scanlines or give hardware-cycle
accurate NMI delivery. The added strict read guard permits only 2002 and 4016/17
outside RAM/ROM. The 240-loop run observed 1,374 status reads and 5,072 reads of
each controller port including startup; no 2007 readback, sprite-hit read or
other unmodeled external read was required. Status remains the existing
constant-zero reference model. These facts do not validate PPU output pixels,
DMA timing, PAL frame speed, audio fidelity or physical collision visuals.

Post-prefix logical NMIs occur only at idle scheduler FE8D/FE90, after checking
four task slots at 80/84/88/8C. All original audio and scheduler instructions run;
no queue is muted/skipped. F6 remains zero under this scheduling policy, which
alone does not test interrupts arriving within mapper critical sections.

Private reproducibility files (not publication inputs):
port/build/recovery_stage_route_private/trace_v4.py and result_v4.json cover
strict five-entry proof; trace_v6.py, run_v6.log and result_v6.json cover the
240-loop movement/video observation. Run from the repository root:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/workspace/scratch/43ecf79622a5/rescue-recovery-inspection/.deps python port/build/recovery_stage_route_private/trace_v6.py

These scripts require the private approved input cartridge and write private
results. Preserve existing result files before rerunning, or copy script and
choose a new output filename. v1 is an earlier neutral bounded exploration;
v2 corrects scheduler slot spacing and FE90 handling. Neither is claimed as
stage success. v3 is the first successful dialogue-input/five-entry run;
v4 adds strict IO-read rejection; v5/v6 add movement/video observations.
Private JSON contains only local reference observations and must not be shipped
as runtime data. This report deliberately excludes cartridge bytes, disassembly,
large resource tables and captured state.

## Additional mapper-busy interleaving

A separate continuous run delivers one real reference NMI at the initial FF59,
after the original INC F5 and before serial mapper writes. No game state is
changed by the harness. The original NMI takes its busy branch and increments
F6. It returns to FF59, finishes the requested bank publication and enters FF75
with F6=1. Deferred audio runs, F6 is cleared by original code and the requested
bank is restored. The run still reaches five C77B entries, with 767,355 total
instructions and 398 logical NMIs. Private trace_busy.py, run_busy.log and
result_busy.json reproduce this case. This tests one critical-section interrupt
position, not all serial write positions or hardware interrupt timing.
