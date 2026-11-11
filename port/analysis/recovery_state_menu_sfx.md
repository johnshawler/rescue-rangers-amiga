# State-selected character menu and cursor sound

This additive native 68020 composition joins the qualified character-cursor
sound path to the state-driven title/menu dispatcher. It is host logical
correctness evidence on the early recovered source baseline, not recovered
later playable source, an Amiga menu, audible Paula output, target timing, or
gameplay. Target integration remains separate. Z=B / X=A and the delivered
disk are unchanged.

## Selection and ABI

`recovery_state_menu_sfx` selects a single helper using live PC, RAM, actual
wrapped stack, mapper control/registers/latch and event. It never consults a
reference CPU, captured state, expected output, diagnostic ID, helper schedule,
or speculative helper result. Original boundaries are retained throughout the
private continuous tests. Original instructions finish before each native call.
The once-initialized native RAM/context/mapper are never reloaded on a successful
history. Only the externally owned journal scratch and diagnostic fields are
cleared or poisoned between calls.

A0 is RAM 2048, A1 context 8, A2 journal 134638, A4 runtime 12, A5 immutable contiguous
PRG 131072. D0.b/D1.b are external decoded pads; D2.l is event. D0 returns 1
advanced, 0 waiting, or FFFFFFFF unsupported. D1-D7/A0-A6 and exact native SP are
preserved; CCR is scratch. Buffers must be valid, aligned, exclusively owned and
disjoint. At least 1 KiB native stack scratch is required. A caller with the old
startup journal allocation must not invoke this entry.

The existing runtime size word retains the explicit FFFF sentinel for ID48,
meaning 134638 bytes. Other sizes are literal. Frozen unsigned queued-video
record consumption is retained. Tests cover 33,300 and 33,339 ordered records,
real mapper CHR changes, DMA at offset 134382, untouched journal gaps and the
sentinel. This is a conservative host proof allocation, not a target memory
recommendation.

New selections require runtime tag D501, mapper control 1E, empty serial latch
and event 0. Cursor/request entries require live PRG 2 and task-zero ownership
(RAM 91=0, RAM 80=2); sound helpers require PRG 3. Pending queue consumption at
C0BF requires PRG 2 and delegates to the frozen queue helper. Its real serial
writes update the actual mapper latch/registers in order. The original PRG 6
startup route remains in the frozen fallback. New helpers retain their
individually qualified raw P/SP behavior; frozen fallbacks keep their own guards.

- ID56: A07B/F379/A086 cursor resource read, sound-ring request and yield JSR.
- ID57: 8003 with A27, sound table dispatch.
- IDs 58/59: 810D header initialization and the frozen 8151 C0=01 combined tail.
- IDs 60/61/62: 8224 stream entry, 8006/8298 duration math and 81A3 channel setup.
- ID63: 8060/807A phase dispatch; 8085 when CF/D0/D1 indicate the SFX path.
- IDs 64/65/66: 82B0/82C0 tick, 82DC mask and 830B/831B event actions.
- ID67: 8052 active control; C0F6 when CF/D0/D1 indicate the SFX path.
- ID68: separately qualified 86B2 SFX envelope for X 0..3.
- ID69: 8235 stream control, including real shutdown or odd-D7 stop at 80FB.
- ID70: PRG 2 C0BF nonempty queue consumption and actual serial mapper replay.
- ID71: new narrow 8151 return bridge when C0 is not 01.

No frozen guard was relaxed. The 46,492-byte composition assembles identically
twice, SHA256 a8a31217696f2f3d30d629adf570b9723c171d965e25f267294a55dc1534496e.
Structural disassembly checks all 13,638 instructions, 3,299 branch targets and
67 PC references. Maximum branch displacement is 11,462; maximum PC displacement
is 45,730. Twelve references use the native 68020 full-format long displacement,
not truncated signed 16 offsets. Every static target lands on an instruction
boundary inside the code image; code and all buffers remain disjoint.

## The separately qualified return bridge

The first delayed-input experiment correctly stopped at 8151 with C0=0D. The
frozen tail requires C0=01; changing that guard would not establish correctness.
The new `recovery_state_menu_sfx_tail` instead translates only the actual 8151
RTS, 80E6 DEC/RTS and empty-queue traversal to C0F6. It requires the genuine
wrapped 80E5/C0F2 frames, DB<8 and queue byte 88. It decrements the actual C0,
consumes the actual frames, preserves Y and raw status except original flags,
and stops before existing active control. It has no resource reads and only a
two-byte empty journal. It does not replace the frozen C0=01 combined tail.

Both public declarative and independent original-first bridge tests pass
131,072 accepted states and 327,158 inert rejections each. They cover every raw
P × SP, every C0 × SP, every wrong byte in each wrapped frame, invalid queue
indices/contents and every unsupported PC. These are invented states, not
successful-history captures. All RAM, raw context, ordered stores, journal
tails, registers, exact SP, code/resources and access guards are checked.

## Continuous histories

Fourteen uninterrupted histories match 59,821 accepted helper boundaries and
15,059 ordered APU writes. Separate checkpoint probes pass 20,912 inert
rejections, plus 14 terminal unsupported-state probes.

Every character history starts at FE24 after NES hardware warmup, not at the
reset vector. It retains the same C2A8 helper 67, third-NMI C0BF helper 70,
command 03 helper 292 and C5D1 helper 990 checkpoints. Start reaches the first
character dispatch at helper 1091 / NMI 38 with the video queue genuinely consumed.
Inputs are external pad samples, supplied identically to original reads and the
native scheduler. They are never used to prescribe a helper schedule.

- Delayed held Right and Left each complete 2,391 helpers / 78 NMIs. Each executes
  the genuine SFX shutdown, continues music 0E, then confirms at C5F8.
- Earlier Right and Left each complete 2,525 helpers / 83 NMIs and use the frozen
  C0=01 tail rather than the new bridge.
- Repeated Right, repeated Left, alternating and move-back histories each
  complete 3,766 helpers / 118 NMIs, including held input, release, re-press,
  multiple sound requests, two genuine shutdowns and continued music.
- Rapid release/re-press completes 2,605 helpers / 83 NMIs with four sound
  requests and one eventual shutdown; requests are not skipped to force success.
- Default confirmation completes 1,229 helpers / 43 NMIs. Neutral title input
  completes all 900 countdown decrements and 27,884 helpers / 935 NMIs.

Confirmation is verified from game state, not merely the C5F8 address. Right
selects cursor X=136, swaps the original 30-byte character table in adjacent pairs
and writes alternate-character markers 8D/8A/95/8E. Move-back and Left confirm
cursor X=40 with the original table unchanged. Original and native RAM/effects
agree on every store. Character names are not inferred from the endpoint.

Every NMI frame is checked in the actual wrapped stack, and every completed
return restores its real SP/status without removing a frame. Full ordered RAM,
resource, controller, PPU, mapper, APU and DMA effects agree at every accepted
boundary. Resource validation reads are checked separately from semantic reads.
Checkpoint rejection probes run on separate machines, never on the successful
chain. Compact results contain lossless run-length encoded controller samples,
helper counts, confirmation/shutdown evidence and hashes of detailed traces.

Title Right, Left and Select each complete 1,069 helpers / 37 NMIs, queue the
real sound request and reject without mutation at A055. That unlinked
continuation is not mistaken for a sound-completion result.

## Public and private checks

The new adapter suite passes 161,536 successes and 56,320 inert rejections.
Additional mapping/resource/boundary checks pass 60 successes and 1,845 inert
rejections. They include all raw status values and wrapped SP positions, every
mapper control value, all PRG banks relevant to the selected entry, partial
latches, invalid events/tags/ownership, pointer edges, resource signatures,
odd-D7 stopping and unsupported boundaries. The source-only audit rejects
imports of an original CPU or private oracle.

Frozen menu specifications pass against the new binary:67,840 successes and
28,928 inert rejections. Frozen music specifications pass 5,381 successes and
61,834 inert rejections. Four public and four original-first long-script cases
pass, including 4 inert waits and 32 public rejections. The unchanged standalone
startup binary separately passes 12,801 successes and 55,779 inert rejections.
That last result is deliberately not described as the old startup rejection
specification passing on the new menu composition: queued-video work is now an
admitted state.

The frozen inventory records 200 dependency files and verifies 171 hashes from
existing predecessor inventories. Frozen menu manifest SHA256 is
DB470AE116885409B124035A6E0DC879B65B3172F9A799C6B5D39B291AB53A15;
frozen stream-control manifest SHA256 is
D7DD34912262ABE8E0B4F05A2B1D563DFFD6724C4F861C9FD5E350B59D0C9465.
The original cartridge, predecessor source and verification artifacts, target
timing work and delivered disk are unchanged.

## Reproduction

From the repository root, install requirements-dev.txt and provide VASM with
68020 support.

### Public checks

These commands require no cartridge or original CPU package.

```sh
export VASM=/path/to/vasmm68k_mot
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_state_menu_sfx_audit.py
python port/tests/recovery_state_menu_sfx_contract.py
python port/tests/recovery_state_menu_sfx_edges.py
python port/tests/recovery_state_menu_sfx_tail_contract.py
python port/tests/recovery_state_menu_sfx_regression.py menu
python port/tests/recovery_state_menu_sfx_regression.py music
python port/tests/recovery_state_menu_sfx_regression.py long
python port/tests/recovery_state_dispatch_startup_contract.py
```

### Private original comparisons

These three commands require the approved cartridge and original CPU package.
Use the same VASM and PYTHONDONTWRITEBYTECODE settings as above.

```sh
python port/tests/recovery_state_menu_sfx_tail_contract.py --rom /path/to/approved-original.nes
python port/tests/recovery_state_menu_sfx_long_rom.py --rom /path/to/approved-original.nes
python port/tests/recovery_state_menu_sfx_rom.py --rom /path/to/approved-original.nes
```

Private input SHA256 is
051EA9BDA7E1AE771F4C196E5BD4B35EC8DB2B305DD3B1D26AD250F379D06411.
The continuous runner uses one 50,000-helper safety ceiling, never a successful
helper schedule. An individual named input history can be selected with
`--history right_repeat`. Detailed private traces and preserved failed attempts
are kept outside the public project; no cartridge bytes or captured-RAM fixtures
are included in these deliverables.

## Honest limits and next step

C5F8 is the post-confirmation/demo boundary, not gameplay. Odd-D7 reaches 80FB
and rejects there; 8249 and 8152 remain unsupported. Title direction/Select can
queue sound through F379 but stop at the unlinked A055 continuation. Additional
nonempty queues or unsupported 8151 frames/phases still reject atomically under
their true helper contracts. Existing qualified music commands continue through
their natural boundaries rather than being skipped or treated as SFX commands.

The next step is separate target integration using the reviewed timing contract,
owned bounded buffers and genuine controller, rendering and audio consumers.
Ordered APU writes here do not establish audible output or target real-time
performance.
