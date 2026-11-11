# State-driven character menu on a stock emulated PAL A1200

Two fresh actual target executions reach and display the original character
menu, with CHIP / DALE and the cursor on CHIP. The real screenshot was opened
and visually inspected. Every captured viewport pixel agrees with the separate
original-only reference. This is a bounded new native recovery-development
milestone, not recovery of missing later playable/audio source.

## Production and milestone

The source-only builder links the frozen approved menu dispatcher and its
unchanged static native helpers. It verifies menu manifest SHA256
`db470ae116885409b124035a6e0dc879b65b3172f9a799c6b5d39b291ab53a15`
and all its listed source hashes. Its approved standalone composite remains
31,628 bytes, SHA256
`ac4b5d9cdca6da92badce8ca6ffffb1a1bc0077c0d10f77fb98c47a678f6e135`.
No interpreter, oracle import, captured RAM, precomputed device state, expected
journal, framebuffer or fixed helper sequence enters the builder or target.
PRG and CHR come directly from the explicitly hash-checked private cartridge.

The diagnostic begins with declared reset RAM poison A5 and context
FE24/17/33/00/24/FD/A7, after the original NES hardware warmup, with reset
mapper state 0C/00/00/03. This does not execute the NES reset-vector warmup. RAM, wrapped original
stack and mapper remain continuous. Inputs are scripted decoded pad bytes:
neutral until live PC first reaches A025, then Start held until the live PC
reaches A06C. A waiting dispatcher return causes the next call to receive
logical NMI event 1. Neither the original oracle nor native diagnostic uses
helper counts to select work or to reach the endpoint. A 4,096-helper safety
cap is not the expected completion count. Unsupported states fail visibly.

At first A06C the target has completed 1,091 helpers and 38 logical NMIs. Final
context is A06C/FF/FF/FF/A4/BD/A7; mapper is 1E/1F/1F/02 with empty latch. The
original queued-video work, including its DMA, was executed; RAM19 is genuinely
consumed. This is an intentional stop at a supported dispatch boundary, not an
unsupported-state rejection and not an implemented character-selection loop.

The new additive device-consumer copy preserves the frozen renderer and device
semantics but handles unsigned journal counts with a zero test before DBRA,
and routes completed helper ID48's DMA to offset 134382. Completed IDs43/47
use the existing resource-filtering device ABI. Published IDs only select how
completed effects are consumed, never which helper executes next. The full
134,638-byte journal is cleared and guarded. FFFF is expanded to 134638 only
for ID48. Journal clearing and copying use long counters; no signed-word size
or count truncation is used. The new assembled consumer tests cover 32,768 and
33,339 records, zero records and rotated ID48 DMA, in addition to prior edge
cases: 37 assembled consumer calls pass.

## Independent verification and coverage

A separate original-only interpreter chooses boundaries from original live
state and completes the reference without consulting target results. It runs
83,096 original instructions. All 1,091 complete contexts, runtime mapper/latch
records and complete published journals match, including 274 APU writes.
Target RAM coverage is explicitly limited to the first 64 full 2,048-byte
boundary snapshots and complete final RAM. No all-boundary target RAM or target
memory-access trace is claimed. All native calls preserve D1-D7/A0-A6 and exact
native SP. The lower 3,072 bytes of the guarded 4,096-byte stack stay untouched:
this is an observational upper-1-KiB usage bound, not a trace.

The independent device and per-pixel model consumes only original events.
Its retained PPUADDR low byte is now tracked rather than assuming the older
title checkpoint's zero byte. All modeled device bytes, 2,048 nametable bytes,
32 palette bytes, 256 OAM bytes, 8,192 selected CHR bytes and all 51,200 native
bitplane bytes match. There are 4,352 PPU events and 415 mapper writes. Both
full immutable 128-KiB PRG and 128-KiB CHR resources are preserved. Copper mode,
all five DMA pointers, every palette entry and FFFFFFFE terminator are checked.
The actual 720x287 video capture matches all 163,840 pixels of the 640x256
viewport at (40,18), including horizontal pixel duplication.

Both fresh target executions use A1200OG, 68020/AGA, PAL 50 Hz, 2 MiB Chip,
zero Fast/slow RAM, no JIT/FPU/MMU and cycle-exact CPU, memory and blitter.
RAM_LOAD and RAM_LOAD_FRAME are unset. Effective logs and 6,000 completed
video callbacks are checked. Full 2-MiB Chip dumps and raw captures are identical.
**6,000 frames is the fixed run/capture budget, not measured completion time.**

257 mutations of the successful capture/configuration/pixels reject, including
all 32 Copper terminator bits, queued-video sentinel and high size byte, DMA
and journal tail, bounds, guards, cross-component buffers and configuration.
Two fresh-process full builds reproduce all eight generated build files with
oracle and py65 imports forbidden. Poisoning the separate reference leaves
source unchanged. New production source has no reference/schedule argument.

## Memory and diagnostic timing

Payload: 511,286 bytes. Total MEMF_CHIP|MEMF_CLEAR boot allocation: 1,297,920
bytes, with no Fast allocation. This leaves 799,232 bytes outside that allocation
in a 2-MiB machine, not a promise that all remaining bytes are OS-free. Allocation
comprises payload, 786,432 capture-reserve bytes, a 16-byte final guard and
186 bytes rounding. Actual captures occupy 462,980 bytes, with the remaining
323,452 verified zero. Core/capture/display buffer ranges are checked disjoint.

Payload components include PRG+CHR 262,144 bytes, journal 134,638, RAM/context/
runtime 2,068, native stack 4,096, framebuffer 51,200, nametables/palette/OAM
2,336, selected CHR 8,192, opacity 7,680, tile cache 1,920 and sprite scratch
2,196. Other bytes are code, reports, Copper/palette constants, guards and
alignment. These are diagnostic costs, not a production memory budget.

Both executions measure 34,256,299 CIA-B E-clock ticks for diagnostic progression
(about 48.29 seconds at 709379 Hz), including full journal clearing, captures,
register checks and diagnostic control. CHR selection plus one background/sprite
composition takes 56,390 ticks (about 79.49 ms). Display DMA is disabled during
these intervals; boot/loading and final Copper/palette setup are excluded.
These are not gameplay FPS, real-time logical-NMI timing or optimization claims.

## Remaining work and preservation

This target test does not cover held/released/repressed character-menu input,
default confirmation, full 900-countdown timeout, Right/Left cursor changes,
live keyboard controls, audible Paula output, gameplay or physical hardware.
F379 title SFX, A07B cursor/SFX and C5F8 gameplay remain unsupported in the frozen
composition. No sound or work is skipped to reach this milestone. The Z=B/X=A
mapping and delivered disk are unchanged.

The native extension leaves its predecessor sources and delivered disk
unchanged. The manifest rehashes frozen menu and startup-display dependencies,
private predecessor artifacts and tool provenance. New private binary/resources,
ADF, dumps and screenshots are confined to ignored
`port/build/recovery_state_menu_display`. They must not be committed to the
public repository. Exact
hashes and compact results are in the adjacent manifest/results files. A private
source-only checkpoint is also preserved under that output directory.

## Reproduction

Provide the approved private ROM `input/rescue-rangers-europe.nes` (SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`) and firmware
`artifacts/a1200-system/kick40068.A1200` (SHA256
`6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707`). Install
requirements-dev.txt. Set VASM, PYTHONPATH, HEADLESS and PUAE_CORE to the approved
assembler, Python dependencies, headless frontend and PUAE core. From root:

```sh
export PYTHONDONTWRITEBYTECODE=1
python port/tools/build_recovery_state_menu_display.py
python port/tests/test_recovery_state_menu_display_build.py
python port/tests/test_recovery_state_menu_display_device.py
out="$PWD/port/build/recovery_state_menu_display"
for prefix in '' repeat-; do
  env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
    RAM_OUT="$out/${prefix}chip.bin" "$HEADLESS" "$PUAE_CORE" \
    "$out/recovery_state_menu_display.adf" "$PWD/artifacts/a1200-system" \
    6000 "$out/${prefix}screen.ppm" > "$out/${prefix}amiga.log" 2>&1
done
python port/tests/verify_recovery_state_menu_display.py
python port/tests/test_recovery_state_menu_display_rejection.py
```
