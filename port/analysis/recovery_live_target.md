# Bounded live title/menu and scene preparation

This is new native integration over the recovered title/menu baseline, not a
recovery of the later lost playable build and not a completed game. Actual CIA
keyboard input now drives the original controller interface. Z=B, X=A, Return=
Start, Tab=Select and arrows retain their established mapping. Input is not
written into original game RAM. The original dispatcher remains byte-identical.
A guarded static helper 72 implements the original title cursor-sound return
A055→A022→JSR FF04, including both original wrapping stack writes.

With --scene, the separately reviewed scene wrapper IDs 73..78 extends genuine
character confirmation through the actual scene fade, sprite hiding, render
disable, nametable clearing and saved-bank PLA to FF53. FF53 is the explicit
stop before further bank/deferred-audio work. No level loader or gameplay after
FF53 is implemented. No instruction interpreter, captured schedule, fabricated
state or fabricated original stack drives the target.

## Bounds and display contract

This is explicitly bounded, not indefinite play. The audio adapter publishes at
most 4096 completed RTIs and retains a 256-record output ring. Exhaustion rejects,
sets limit_reason=1, drains/mutes and permanently stops; it is not success.
The runner separately limits one million successful helpers and 128 input-mask
changes. Each recorded input change contains exact helper count, pending-event
phase, completed-RTI count and held pad byte. Host replay checks those fields
against the actual original sampling boundaries.

Only the most recent journal is retained in target capture storage. Its original
count/size/helper/DMA safety checks remain; overwrite is intentional and explicit.
The earlier frozen scripted exhaustive target journal proof remains separate.
The live histories also have continuous original-first host native proof of all
RAM and ordered device effects, not an exhaustive on-target journal trace.

The display accepts the existing unscrolled 8x8 ctrl90/mask1E/MMC1-control1E
contract. Repeated rendering restores prior sprite footprints with the reviewed
conservative invalidator; CHR-bank changes invalidate all tiles. No sprite or
original device implementation changed. Real mask 0 blanks bitplane DMA and updates
both direct COLOR00 and the Copper universal backdrop using the current original
palette and declared RGB4 approximation. Before the first accepted frame,
unsupported setup modes are blanked; afterward unsupported nonblank modes fail
permanently with display error-1/runner-5. Gray/emphasis, partial-mask modes,
scrolling and 8x16 sprites are not implemented.

The measured live wait 600 history is not a 4096-update game run. The 4096 limit has
compiled synthetic-clock safety tests. Unattended title countdown 900/demo routes,
2-player confirmation and every possible key combination are not qualified; they
may reach an explicit unsupported original boundary earlier. The old v2 title
Right capture stopped authentically atA055/-1; helper 72 now covers that path.

## Final-source evidence

Pinned PUAE PAL A1200OG,68020/AGA,2 MiB Chip/zero Fast, CPU/memory cycle exact.
Final runtime is the v12 scene target, byte-identical to a v13 rebuild after
builder provenance strengthening. The builder verifies the approved scene
manifest and its source/dependency hashes. All captures are fresh boots using
real libretro keyboard callbacks, not target memory injection.

- Final title phase:1733 helpers/60 RTIs, no keys, explicit diagnostic status1.
  Final character phase:3212 helpers/110 RTIs, Start80/release90, no confirmation,
  status1. Both independently match original RAM/context/runtime, device/CHR,
  all 51,200 plane bytes and 163,840 displayed RGB pixels; screenshots were inspected.
- Alternate choice plus scene:5,366 helpers/177 RTIs, genuine FF53 context.
  Continuous native host replay matches 5,366 helper boundaries covering
  296,313 original instructions, plus every ordered RAM/device effect. Actual scene endpoint rendering is
  disabled: original backdrop index15 maps to RGB4 zero and the actual viewport
  is black. Retained framebuffer storage is separately checked against the last
  genuinely rendered RTI, not represented as a new scene picture.
- Long wait, title Right/Left, character held Right 40 RTIs, release/repress and
  move-back:19,189 helpers/617 RTIs to FF53, original character. Last 256 audio
  records match the original;361 earlier records are explicitly overwritten.
- The final-source dirty and full-invalidate captures are independently correct,
  but NOT a matched performance comparison. Both request the same RTI keyboard
  schedule and complete 5,366 helpers/177 RTIs, yet Start-release at RTI 170
  arrives at helper 5,157 versus 5,153. The original controller sample and RAM $16
  differ across 39 boundaries. No improvement percentage is claimed from them.
  Independently measured dirty/full progression is 8,395,024/15,122,025 CIA ticks.
  Last genuine render is 8,151/47,427 ticks after sprites were hidden in the scene
  fade, not title-menu rendering. The separate final character phase render is
  25,344 ticks (35.727 ms at 709,379 Hz). All 177 updates are late in both runs.
  Old audio plans continue during native work; no full-rate/game-FPS claim.
- Actual 44,100 Hz stereo PCM passes non-DC, unclipped stereo activity and terminal
  silence. Fully retained histories additionally verify initial left-only noise,
  native silence, and pulse fundamentals near 622.78/261.43 Hz against nominal
 621.83/261.11 Hz. DC, swapped stereo and substituted 1000 Hz windows reject.
  Long ring histories do not retain initial timing rows for those spectral checks.

Four Paula voices still approximate NES sound: finite noise loops, fixed stereo,
no envelopes/length/linear/sweep/DMC/nonlinear mixer, deferred loop reloads and no
within-interrupt cycle timing. Ordered original register snapshots and bounded
actual PCM checks do not establish complete NES audio fidelity.

## Tests and reproduction

Public ROM-free entrypoint: bash port/tools/recovery_live_public.sh. It requires
VASM, machine68k and the pinned GCC14 m68k toolchain. It denies original oracle
imports and cartridge/input reads, compiles the unchanged 470-byte planner and new
ring adapter, executes 4096 USER-mode publications plus rejection, then 1,024
USER-mode title continuation and 192 width-aware scanout cases. This is not an
assembler-only CI suite or hardware timing evidence.

Private setup: provide your legally owned input/rescue-rangers-europe.nes
SHA256 051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411
and artifacts/a1200-system/kick40068.A1200
SHA256 6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707.
Set VASM, PAULA_CC or PATH for pinned GCC14, PYTHONPATH for the supplied dependency
directory, and PYTHONDONTWRITEBYTECODE=1. Run from the restored repository root:

    python port/tools/recovery_live_build.py --output port/build/NEW --scene
    bash port/tools/recovery_live_run.sh "$PWD/port/build/NEW" 6000 '80:90:13,120:130:275,160:170:13'
    python port/tests/recovery_live_dispatch_test.py port/build/NEW
    python port/tests/recovery_live_rejection_test.py port/build/NEW
    python port/tests/recovery_live_ring_test.py port/build/NEW

Build and run refuse existing outputs. --stop-rti 60 or --stop-rti 110 creates a source-built
phase stop with status1, not a game-state edit. --full-redraw selects the
full-cache-invalidation diagnostic reference. Omit --scene only for the earlier C5F8 boundary.
The run script verifies pinned core/frontend/firmware hashes and reads effective
stock configuration from the actual completed emulator log. Core SHA256:
84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456.
Existing frontend SHA256:
5a6caac3c484c24a979800188070abb78c7fdbe648106fb84c5d8532e19052b1.

The final source allowlist/closure is produced by recovery_live_package.py.
Extract only generic source into a new directory, verify every manifest hash,
run the public tests before adding proprietary inputs, then supply the above
private inputs and external pinned tools to rebuild. Never publish ROM,
Kickstart, ADF, RAM, screenshots, PCM, journals, game profiles or generated assets.
The delivered rescue-rangers-stock-zx.adf is unchanged at SHA256
6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17.

## Preserved predecessor and failed evidence

Private v1/v4/v7/v11 builds failed alignment/range checks and remain preserved.
v5 was built but never run after a relocation issue was noticed; corrected v6
was used. v2 is an authentic unsupported A055/-1 capture, not successful play.
v3/v6/v8/v9/v10 are predecessor results, not relabeled as final-source proof.
The initial verifier accepted several corrupted metadata fields; its exact
source and rejected-review counterexamples are retained privately. The corrected
verifier binds pointers and executable ranges, independently replays input RTIs
and render eligibility, checks requested endpoint/status, and rejects the reported
mutations. Synthetic malformed-target tests preserve mute/drain/permanent-stop
and originating error semantics; they are not actual fault-PCM captures.
