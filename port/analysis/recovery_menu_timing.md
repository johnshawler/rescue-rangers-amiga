# Character-menu timing with validation outside the measured path

Two fresh stock emulated PAL A1200 executions reach the same first character
menu as the frozen diagnostic. Both show CHIP / DALE with the cursor on CHIP.
All 163,840 visible viewport pixels match the separate original-only reference;
the screenshot was also opened and visually inspected. Full 2-MiB Chip dumps
and raw screenshots are identical across the two boots.

This is **diagnostic-overhead reduction**, not a gameplay speed-up. Static
translated helpers, device consumer, renderer and clock code are unchanged.
It is new recovery work from the early source, not recovery of the lost later
playable/audio source. There is no generic 6502 runtime in the target.

## Separate timing intervals

Each fresh execution reports, at the declared PAL CIA E-clock rate of
709,379 ticks per second:

- State-driven progression: 534,491 ticks, **0.753463240 seconds**. This includes
  all 1,091 helper completions, 38 scripted logical NMI deliveries, dispatcher,
  runner counters/control and completed device-journal consumption.
- CHR bank selection plus one complete background/sprite composition:
  56,381 ticks, **79.479376 milliseconds**.

These are measured CIA elapsed ticks, not directly measured 68020 instruction
cycles. No CPU-cycle counter or physical-hardware measurement is claimed.
Custom display DMA is disabled throughout both intervals. Boot/loading and
one-time initial buffer setup are outside progression; final palette conversion
and Copper setup occur after the render interval. The clock-read overhead and
small report/setup work surrounding the calls remain. No per-helper timing is
inferred. The two intervals are reported separately, not converted to game FPS.

The old validation-heavy target measured 34,256,299 progression ticks and
56,390 render ticks. Its large repeated clears and captures explain why its
48.29-second progression is not a gameplay benchmark. The nine-tick difference
in rendering is an observation with unchanged code, not a rendering optimization
claim. Both programs are unscheduled diagnostics: a dispatcher wait immediately
causes the next call to receive a logical NMI. Thirty-eight such NMIs are not
38 display frames, nor a demonstrated real-time cadence. Each emulator run uses
a fixed 6,000-video-callback capture budget; this is not completion time.

## What changed, and what did not

The new 370-byte runner initializes the same RAM poison A5, context
FE24/17/33/00/24/FD/A7 and mapper 0C/00/00/03. Original comparisons start at FE24
**after** NES hardware warmup; they do not execute reset-vector warmup. RAM,
original wrapped stack and mapper state remain continuous. Scripted pad bytes
are neutral until live PC A025, then Start is held. First live PC A06C ends the
run. A 4,096-completion cap is only a safety limit, never a helper schedule.

The journal retains its full 134,638-byte capacity and is initialized to zero
once in the payload. There is no per-helper full-journal clear. Each frozen
helper establishes its own count and live entries before reading them; device
consumption uses that count, and fixed DMA locations remain valid. Unpublished
journal padding can retain old bytes and is explicitly not treated as an output.
This target removes all per-boundary snapshot copying and per-call diagnostic
register/stack comparisons. Final state, status, counters, stack pointer and
buffer guards remain available for independent post-run checks.

No helper, original work, queued-video DMA, APU command, renderer or device
consumer was removed or rewritten. The helper composition is exactly 31,628
bytes, SHA256 ac4b5d9cdca6da92badce8ca6ffffb1a1bc0077c0d10f77fb98c47a678f6e135.
Those bytes occur unchanged inside the target. The 1,750-byte device/renderer/
clock executable region also matches the predecessor byte for byte, SHA256
85b142d8ac84d53f4f5bb6f5143b28d1a07183989b71f2aeeeacaa0a3f920bad.

## Verification, with its boundaries

The independent original-only reference executes 83,096 original instructions.
Both stock target captures match complete final 2,048-byte RAM, eight-byte
context A06C/FF/FF/FF/A4/BD/A7, runtime mapper 1E/1F/1F/02 with empty latch, and
all 74 live bytes of the final journal. The original run includes 274 APU writes;
these are retained command semantics, not audible output. Device state, 2,048
nametable bytes, 32 palette bytes, 256 OAM bytes, 8,192 selected CHR bytes,
51,200 native bitplane bytes, Copper pointers/palette/terminator and full immutable
PRG/CHR resources match. Original events include 4,352 PPU events and 415 mapper
writes. Native SP is balanced and lower 3,072 stack bytes remain zero, an
observational upper-1-KiB bound rather than a stack trace.

Separate, unmeasured machine68k executions verify **every one of 1,091** full
RAM/context/runtime boundaries and all live journal records and DMA bytes
against the original. One run initializes the journal once and reuses it; the
other poisons all 134,638 bytes with 69 before every call. Both pass. All 10,936
journal reads per run are traced and shown to follow writes within that same
call. Register preservation, guards, immutable code and resources are also
checked. This is separate native-helper evidence, not an all-boundary stock
capture or a stock-target memory-access trace. It directly tests that removed
clearing is not a hidden input contract.

The verifier rejects 256 mutations of real capture contents, bounds, guards,
configuration, timer ranges and pixels, including all 32 individual Copper
terminator bits. Two fresh-process full builds reproduce all eight generated
build files with oracle and py65 imports denied. No captured initial fixture, reference result,
prescribed helper list or framebuffer enters the production build.

Logs confirm A1200OG, 68020, AGA, PAL 50 Hz, 2 MiB Chip, zero Fast/slow RAM,
no JIT/FPU/MMU, and cycle-exact CPU/memory/blitter. RAM_LOAD and RAM_LOAD_FRAME
are unset. Both frontend processes exit successfully and report 6,000 completed
runs/video callbacks. No physical hardware is covered.

## Code and memory accounting

Payload is 510,966 bytes. MEMF_CHIP | MEMF_CLEAR allocation is **511,488 bytes**:
payload plus 16 spare bytes and 506 bytes of rounding. No Fast allocation and
no capture workspace remain. The predecessor allocated 1,297,920 bytes,
including a 786,432-byte capture reserve. The new allocation leaves 1,585,664
bytes outside it on a 2-MiB machine, not a guarantee of OS-free memory.

Payload breakdown:

- Runner 370; frozen helpers 31,628; device/renderer/clock code 1,750 bytes.
- Immutable PRG plus CHR 262,144; journal 134,638; RAM/context/runtime 2,068.
- Native stack 4,096; frame 51,200; nametables/palette/OAM 2,336.
- Selected CHR 8,192; opacity 7,680; tile cache 1,920; sprite scratch 2,196.
- Remaining reports, constants, Copper, guards and alignment: 748 bytes.

This is still a bounded development allocation, not a production game budget.

## Preservation and next boundary

The dependency map freezes the source/test corpus at public checkpoint
ad4ac8f77a7046ef68d51a01f779f646522f226a, tree
97ed8544e99a61861605ec70e46b216487f33861. The original ROM, firmware,
predecessor artifacts and delivered stock Z/X disk remain unchanged; their
hashes are rechecked in the manifest. Private diagnostic outputs are under
ignored port/build/recovery_menu_timing, including a source-only checkpoint copy.

This is not live keyboard input, character-selection progression, audible Paula
output or gameplay. F379 title SFX, A07B cursor/SFX and C5F8 gameplay remain
unsupported in the frozen composition. Existing Z=B/X=A behavior and the
delivered disk remain untouched. The next technical boundary is to isolate renderer cost or implement the next
original-source boundary with independent semantic tests before extending the
game loop.

## Reproduce

From repository root, provide the approved private cartridge and firmware:

- input/rescue-rangers-europe.nes, SHA256
  051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
- artifacts/a1200-system/kick40068.A1200, SHA256
  6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707.

Install requirements-dev.txt, and set VASM, PYTHONPATH, HEADLESS and PUAE_CORE
to the approved assembler, Python dependencies, frontend and emulator core.
Tool hashes are in the manifest. No tool rebuild is required.

```sh
export PYTHONDONTWRITEBYTECODE=1
python port/tools/build_recovery_menu_timing.py
python port/tests/recovery_menu_timing_build_test.py
python port/tests/recovery_menu_timing_contract.py
out="$PWD/port/build/recovery_menu_timing"
for prefix in '' repeat-; do
  env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
    RAM_OUT="$out/${prefix}chip.bin" "$HEADLESS" "$PUAE_CORE" \
    "$out/recovery_menu_timing.adf" "$PWD/artifacts/a1200-system" \
    6000 "$out/${prefix}screen.ppm" > "$out/${prefix}amiga.log" 2>&1
done
python port/tests/verify_recovery_menu_timing.py
python port/tests/recovery_menu_timing_rejection_test.py
```
