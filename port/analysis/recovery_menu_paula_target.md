# Measured native menu/Paula checkpoint

## Scope and result

A separate native target now feeds actual counted, ordered journals into persistent
4000..400F/4015 shadow state. The unchanged compiled experimental_direct_paula_plan
is called only after actual native RTI completions. Three bounded scripted
histories reach C5F8, with original RAM/context/runtime, selection, every journal
and DMA byte, final device state, five bitplanes and actual displayed RGB pixels
verified against an independent original-code oracle. No captured stream/profile,
prescribed helper schedule, original interpreter or fabricated game state supplies
the target. The original proof begins at FE24 after hardware warmup. There is no
live keyboard input, gameplay after C5F8, or completed-game claim.

Private v6 actual callback captures pass non-DC playback, left/right routing,
original-derived pulse pitch, native silent interval, and terminal zero output.
Default: 322 writes / 43 completed RTIs. Right-hold: 607 / 78. Move-back: 922 / 118.
The right selection confirms the alternate cursor/table; default and move-back
confirm the original table. First two completed RTIs remain silent. Initialization
is all-zero shadow/enable 0 plus muted noise 07, not invented audible register state.
4015 is honored; 4017 reads remain controller 2 and writes reject. DMC writes,
unsupported planner states, counts above 33595, short nonzero header sizes and
FFFF size outside helper 48 fail closed. No guard is weakened to admit a plan.

RTI IDs are semantically grounded: 8 invokes recovery_silent_tick_rti, which
restores the original saved frame and FE8D return; 20 and 42 invoke
recovery_active_nmi_return, which reads the original stack frame and restores
PC/status/registers. All completed plans independently match original-derived
snapshots. Non-RTI writes never publish, including accepted but unsafe transients.
Within-interrupt writes are reduced to a final snapshot, not cycle-timestamped.

## Timing and active display contention

Measured on pinned PUAE, stock PAL A1200OG/68020/AGA, 2 MiB Chip/zero Fast, CPU and
memory cycle exact. A chained 32-bit CIA-B counter uses nominal 709379 Hz. It does
not wrap at the isolated probe's 16-bit timer limit. Every update waits for a
minimum 14188 ticks (about 20 ms) since the preceding publication. Late work is
published once when ready, not burst-replayed to catch up. Logical interrupts
are not video frames, and PAL NES/Amiga rates are not equated.

For matched default histories, DMA-off/on respectively:

- Whole native progression including journal capture, device handling, shadow,
  planner, hardware apply and waits:862746/991535 ticks (1.21620/1.39775s).
- Completed updates already later than 14188 ticks:30/40 of 43.
- Maximum interval including bootstrap before first publication:80395/91343 ticks
  (113.33/128.76 ms). Subsequent exact intervals are retained privately.
- Final CHR mapping/native rendering call:56614/63649 ticks (79.81/89.73 ms).
- Maximum hardware-plan application plus surrounding clock reads:94/112 ticks
  (132.51/157.88 microseconds). This excludes shadow parsing, planning, waits,
  runner, rendering and capture. It is not backend CPU utilization.

Display-on right-hold:1728239 progression ticks,73 late updates of 78,
63505 render ticks. Move-back:2563616 ticks,113 late of 118,63242 render ticks.
The allocation is811008 Chip bytes for all four variants, zero Fast; the on
payload is810976 bytes, off810904 bytes. It includes the original134638-byte journal,
262144-byte journal output capture,256x56-byte audio output records,4096-byte
native stack,22336-byte linked audio adapter extent (code/waves/state/records),
ROM-derived resources and renderer storage. This is payload allocation, not
whole-machine free memory or host capture storage.

Display-on means a real Copper/five-plane DMA scanout from initialization, with
initially blank diagnostic planes. Only ONE final native render occurs. The game
is not being rendered every logical interrupt; the measured89.73 ms final render
alone rules out a20 ms concurrent render budget. During long native work, Paula
continues the previous plan, which is continuous output but a deferred audio
update, not an underrun-free full-rate game. No CPU-speed/FPS/physical-hardware
claim is made. Boot loading is excluded from CIA progression timing.

## Actual audio and stop validation

All comparisons use actual 44100 Hz stereo 16-bit callbacks from the already built
pinned audio frontend, not successful custom-register writes alone. The first
original-derived audible interval is noise-only on the left, with exactly zero
right output. A following native silent interval is exactly zero. Completed RTIs
18–19 provide isolated pulse 1 left / pulse 2 right: nominal 621.8259 / 261.1083 Hz from
their plans, measured strongest non-DC peaks 622.7806 / 261.4265 Hz in an approximately
149 ms Hann window (native resolution 6.72 Hz). Zero padding is not extra resolution;
these are bounded pitch/channel checks, not exact tuning or all-SFX fidelity.

Actual waveforms/spectra and final screenshots were visually inspected. PCM has
no saturated samples, both active sides have substantial AC RMS, and final output
is exactly stereo zero for at least 79.69 seconds in every v6 capture. Negative PCM
copies reject DC-only output, swapped stereo and a substituted 1000 Hz pulse-window
tone. Original PCM remains unedited. Host machine68k tests execute the actual
compiled adapter and check ordered overwrites, stale zero-size journal isolation,
RTI-only publication, enable 0 mute, unsupported-state failure,4017 read/write
handling and invalid journal bounds. Their synthetic clock is test-only, never
production timing evidence.

The first v3 target exposed a real pinned-PUAE stop failure: immediately disabling
DMA after writing zero volumes held a nonzero constant output (1024,-1365). That
failed RAM/PCM remains private and was not overwritten. The corrected terminal
shutdown sets all volumes zero, allows 14188 CIA ticks of DMA drain, then disables
all four audio DMA channels. The last original-derived shadow/plan is preserved;
shutdown is a separate backend operation. Corrected actual PCM validates zero
output after drain. This is an observed emulator behavior, not a universal DAC
claim. v1/v2 failed builds, the short incomplete boot, v3 failed mute capture,
v4 pre-guard results and source-restore failures are preserved in distinct folders.

The private right-selection preview is an unchanged-sample WAV excerpt, not
normalized, resynthesized or sped up. Source frames[1614105,1743346),129241frames,
2.93063492 seconds, include 200 ms lead and 400 ms clean tail. WAV SHA256:
218f494efbaa7e4155561be0d30854013c7dc6b406b7be8e73af2884d752896c.
Raw PCM SHA256 669a2d45e7fa2661d245d41f612758765fc445366047c3b9be5877128c1860a6.
Keep original-derived audio, screenshots, profiles, plans, ROM, firmware, RAM and
disks private; only generic source and factual measurements belong in publication.

## Preserved code and limits

Frozen dispatcher46492 bytes SHA256 a8a31217696f2f3d30d629adf570b9723c171d965e25f267294a55dc1534496e.
Frozen device/renderer/clock1750 bytes SHA256 85b142d8ac84d53f4f5bb6f5143b28d1a07183989b71f2aeeeacaa0a3f920bad.
The470-byte compiled planner is byte-identical to the earlier isolated probe,
SHA256 33eaebe81eb97ba518ce3def0ae33bb5db1201745018e4c4c77d5f01a5a64996.
Planner source unchanged SHA256 5c5be6ac34df5fc7d9b72a081343abc262c762d8b67b142c9e585e6a24080420.
Mapper helper 70 still maps to frozen device consumer 7. Full journal FFFF sentinel,
counted records and ordered writes are retained. Predecessor sources, shared tools and the delivered disk remain unchanged. Delivered disk SHA256 remains
6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17.

Four DMA voices use finite 2048-byte noise loops and fixed stereo. Approximation
limits persist: no hardware envelopes/length/linear/sweep/DMC/nonlinear mixer;
finite noise repetition/DC bias and phase discontinuities; up to about 92.4 ms loop-reload
latency; no genuine within-interrupt event timestamps or exact NES phase. Final
state/pixels and exact ordered effects are verified, not all target RAM boundaries.
There is no subjective authenticity claim. Source-only restoration instructions
and a generic dependency-closure packager accompany this checkpoint.

## Prior fresh restore result (v5)

The prior 202-file generic-source closure was restored into an empty private directory.
Only the approved cartridge and firmware were added; VASM, GCC, Python packages
and the pinned core/frontend were external tools. The regenerated default-on ADF
and fresh 6000-callback run's full Chip RAM, raw PCM and screenshot were all
byte-identical to v5. The independent original/device/pixel/audio verifier and
compiled-adapter negative tests passed there. Restore packaging first exposed
missing static-wrapper/dynamic-model dependencies; those failed attempts remain
preserved and the successful closure explicitly includes them. Later additions
only strengthen immutable-code/hash checks and package/report provenance; they
do not change the target bytes. This is a source-and-input restore, not replay
from captured target fixtures.


## Independent-review correction and v6 qualification

The preserved independent review found two complete-target defects outside the
valid histories: the capture_journal guard stopped before the audio adapter,
leaving existing sound running; and invoking C mute before saving D0 corrupted
the originating error. The v5 archive and successful/failed evidence are retained.

Only the additive integration changes: its generated capture guard now routes
through permanent muted failure with error -3, maintaining the predecessor code's
20-byte span/alignment. The failed label saves D0 before C mute. Capture failure
cannot return to successful execution. Adapter rejection retains -4, and a native
renderer failure retains its display-report -1 while propagating runner error -5.
All paths drain zero-volume DMA before disabling it. Audio stage 3 means shutdown
completed, not global success; the runner and display error reports remain
mandatory when judging success.

Eleven complete linked-target fault cases pass: oversized count, invalid helper,
helper 48 missing FFFF sentinel, capture capacity, capture capacity including DMA,
failed errors -4 and -1, adapter unsupported state, adapter invalid FFFF sentinel,
adapter short header, and renderer rejection. Each begins with sounding volume
words and DMA enabled, checks zero-volume writes, at least 14188 synthetic CIA
ticks before DMA disable, retained error identity, immutable executable bytes,
and a permanent stop that issues no later writes. This CPU-level injected-state
proof is not a real-core malformed-input PCM capture. It complements, rather
than replaces, the earlier adapter-only tests and actual valid-history audio.

Four fresh v6 stock captures repeat default DMA-off/on, right_hold/on and
move_back/on. All original-state, journal, snapshot, plan, display and actual PCM
checks pass. The measured progression/maximum interval/final render/application
values above are unchanged from v5. All four raw PCM streams and screenshots
remain byte-identical to their v5 counterparts; the new target code and Chip RAM
are not claimed identical. The newly extracted right-selection WAV consequently
has the same exact sample range and hash, and distinct v6 provenance files.
The public synthetic wrapper is unchanged. The validation recipe now runs
complete-target rejection tests after adapter tests in each variant;
this changes no runtime bytes.

## v6 source-only restore result

The corrected source closure contains 205 files: the earlier 202-file closure,
the new complete-target rejection test and two validation wrappers.
Every size/hash was verified after extraction into an empty directory. The public
synthetic test passed before any cartridge or firmware was supplied. After adding
only those approved private inputs, fresh source rebuilt the v6 default-on ADF
byte-identically, passed all 11 complete-target negative cases and a new 6000-callback
stock capture/verification. Its full Chip RAM, PCM and screenshot also equal the
v6 default-on evidence byte-for-byte. Final freeze changes after that restoration
are report/provenance fields and the validation-only wrapper update,
not runtime or test implementation code. The final
source archive is distinct from the preserved v5 archive.


## v7 diagnostic-only correction

The v6 review confirmed safe muting but identified three guards that could store
stale D0, including successful status 0, on failure. The integration now assigns
-6 to exhausted loop budget, -7 to input-history overflow, and -8 to a repeated
pending-event rejection. Existing -1/-3/-4/-5 error identities remain unchanged.
Four rebuilt variants pass 14 complete linked-target fault cases, including these
three actual comparison/branch paths starting with D0=0. Each retains its explicit
negative error, mutes/drains/disables DMA and remains permanently stopped.

This is a 19-byte diagnostic-only change from v6 in every variant. Exactly three
conditional branch displacement words may change, at payload ranges [170,172),
[260,262),[320,322), and 14 previously unreachable padding bytes [634,648) become
failure-code stubs. Byte 170 happens to remain equal. All pre-existing symbol
addresses and payload extents are identical. Frozen dispatcher/device/planner,
resources, adapter, successful-path instruction sizes and addresses are unchanged.
The conditional branches retain their opcodes/widths and remain untaken during
valid histories. The explicit layout comparison rejects ANY other changed byte.

Accordingly, prior v6 valid-history audio/state/pixel/contention results remain
applicable as baseline evidence, not newly captured v7 results. Only default-on
received a fresh source-only build/capture; the other three v7 variants
are rebuilt and checked structurally and with complete-target fault tests, not
recaptured. One interrupted v6 validation capture has no final RAM/verifier result and is expressly NOT a playback pass. All prior
archives/captures, including that partial evidence, remain untouched.


### v7 fresh result and precise evidence reuse

The 205-file v7 source closure was verified in an empty restore directory. The
public synthetic wrapper passed before any private inputs were added. With only
approved ROM/firmware plus external tools, the default-on build matched the
separate v7 build byte-for-byte, all 14 complete-target fault cases passed, and
one new 6000-callback stock capture completed and passed the original-state,
journal, completed-plan, device/pixel and actual PCM verifier. The new guard
suite also rejects a private copy of v6 at loop_budget_guard with observed 0 versus
required -6, demonstrating that the regression catches the reviewed defect.

Fresh default-on remains 991535 progression ticks, 40 deferred updates of 43,
91343 maximum interval ticks, 63649 final render ticks and 112 maximum hardware-apply
ticks. Its raw PCM and screenshot are byte-identical to v6 default-on. New full
Chip RAM SHA256 11bf7332d5f587ca62387070a26c697c3d7250146243888701330ba023f552e4.
New default-on ADF SHA256 506a03714a987adbac5b50ced9c2cba3f6a088f79636580ae7522a6ad3b2a6e1.
The historical right-selection WAV remains explicitly a v6 capture, with its
previous exact range/hash; no new v7 right-selection recording is claimed.
Prior v6 DMA-off/right-hold/move-back measurements are retained baseline results,
supported by the exact 19-byte error-only change proof, not relabeled fresh runs.
Final changes after the successful source-only restore are report/provenance only.

## Final independent review

The corrected checkpoint is approved within the stated bounded scope. Independent
checks confirmed the exact 19-byte error-only delta across all four variants,
all 56 complete-target rejection cases, the 205-source restore and identical
default-on rebuild. The original stop/mute and error-identity counterexamples
now pass. Existing playback evidence is reused only where the report explicitly
identifies it; the interrupted capture is excluded.
