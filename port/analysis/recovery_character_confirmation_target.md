# Stock PAL A1200 default-character confirmation diagnostic

This additive private diagnostic executes the frozen static 68020 helpers from
the declared FE24 original reset-RAM entry after hardware warmup through
genuine default-character confirmation at C5F8. NES reset-vector execution
and hardware warmup are outside this diagnostic. All five independent reset runs execute all 1,196 calls across 53 reached
helper types, 40 logical NMIs and 38 later audio completions. No intermediate
RAM, context, original stack, PPU state, readiness flag or result is injected.
There is no target 6502 interpreter. This diagnostic stops before executing
the original continuation at C5F8.

## Scripted input and diagnostic schedule

This is **scripted diagnostic input, not live keyboard or joystick control**.
Controller one receives Start (10 hex) at scheduler calls 1080, 1101, 1106 and
1127, release at 1130 and 1151, then Start again at 1155 and 1192. Other scheduler
calls receive neutral input. Controller two is neutral throughout. The original
scheduler and serial-controller logic generate authentic release/repress edges;
the diagnostic does not write input RAM or clear the video queue.

The builder emits a fixed straight-line list of helper calls, determined by the
independent original-ROM oracle. Each frozen helper checks its supported PC.
Logical NMIs occur at the same observed idle boundaries as the host diagnostic,
not asynchronously from the Amiga raster clock. Native status comparisons,
D1–D7/A0–A6 preservation and exact native stack checks run after every helper.
Expected statuses can stop a failed diagnostic but cannot supply game state.

The oracle imports only standard-library modules and py65. It executes the
unaltered approved cartridge and observes instruction boundaries and effects,
without importing native code or declarative game-state models. Its first 1,024
complete results, journals, event intervals and mapper checkpoints reproduce the
previous CHR/fade oracle exactly. Two reset oracle executions are identical.
Replacing every expected RAM, context, raw-context and journal byte with poison,
while retaining sizes and diagnostic schedule, leaves every generated assembly
source byte unchanged. Expected state is used only by verification.

## Bounded capture and allocation

Windows capture full 2,048-byte RAM after calls [0,256), [256,512), [512,768),
[768,1024) and [1024,1196). Every run still executes the complete reset-to-C5F8
sequence and records all 1,196 contexts and full journals. Collectively they
cover every RAM boundary, not all snapshots from one execution. No state is
restored between windows. Each journal is unreused and has independent guards.

The queued-video helper runs at call 1107. Its entire 134,638-byte journal is
reserved and checked, including the DMA block at offset 134,382 and the unused
zero tail. The observed event count is 31, read as an unsigned word. Large
journal addresses use 68020 addressing, not truncated signed-word displacements;
none overlaps its guards or another buffer. This is not coverage of all possible
maximum-length video queues.

For windows 0–3, payloads are 365,314 bytes, capture workspaces 934,046 bytes and
boot allocations 1,299,456 bytes. Window 4 uses 364,306, 762,014 and 1,126,400
bytes respectively. Allocations include guards and sector rounding, request
MEMF_CHIP | MEMF_CLEAR, and leave at least 797,696 bytes outside the allocation
in stock 2 MiB Chip. There is no Fast-memory allocation. All code, three immutable
16 KiB cartridge resource banks, resident RAM/context, 4,096-byte native stack
and snapshots reside in that Chip allocation. Runtime pointers, pairwise buffer
separation, report separation, bounds and guards are verified.

## Actual emulated-target results

Five fresh PUAE runs each completed 1,800 frames and video callbacks. Effective
logs verify A1200OG, 68020, AGA, PAL 50 Hz, 2 MiB Chip, zero Fast/slow memory,
no FPU/MMU/JIT, and CPU/memory/blitter cycle exact. Each actual Chip dump passes:

- All 1,196 contexts, full journals and persistent mapper/latch boundaries.
- All full RAM boundaries in its window, collectively all 1,196 boundaries.
- All 10,240 DMA bytes and 49,152 immutable resource bytes.
- Final RAM/context, journal and buffer guards, helper status, ABI and stack.
- Final context C5F8/F8/00/FF/27/BF/A7; mapper 1E/1F/1F/02, empty latch.
- Timer 898, naturally consumed RAM19 and default cursor originally 28.

A sixth fresh window-0 execution passes independently and reproduces the entire
2 MiB Chip dump byte-for-byte. The original oracle executes 88,911 instructions
and observes 18,702 RAM writes, 4,372 PPU events, 435 mapper writes, 720 controller
events, 2,553 semantic resource reads and 298 APU writes. Those original event
counts are not claims of a target bus trace. RAM journals exist for the
fade/yield/menu store-journal helpers; other RAM evidence is full boundary state.

## Build, checks and preservation

The isolated build test reproduces all 29 generated files, including five ADFs,
and a second build matches them byte-for-byte. Missing/wrong ROM fails before
output creation and preserves existing outputs. All 59 build dependencies match
the exact build manifest. The test also verifies the prior preservation inventory
and the delivered Z/X disk SHA256
6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17.
The prior character-dispatch manifest and all 46 source/evidence hashes in the
CHR/fade evidence manifest remain valid. No old source, test, documentation,
manifest, capture or historical ADF was changed. The frozen title display is separate and unchanged.

Mutation-negative tests operate on successful real captures, not synthetic
positive dumps. They reject altered statuses/counts/windows, pointers, bounds,
overlap, every context byte, RAM samples at every captured boundary, journals,
guards, every DMA byte, large queue offsets, mapper writes, resources, malformed
dumps, wrong ROM, wrong modes and missing/conflicting stock configuration.
Exact test counts and capture hashes are in the new evidence manifest.

New source files:

- port/tools/build_recovery_character_confirmation_probe.py
- port/tests/recovery_character_confirmation_target_oracle.py
- port/tests/verify_recovery_character_confirmation_probe.py
- port/tests/test_recovery_character_confirmation_probe_rejection.py
- port/tests/test_recovery_character_confirmation_build.py

Private generated data is confined to ignored port/build/character-confirmation-stock.
It includes cartridge-bearing resources and must not enter a source checkpoint.
Install requirements-dev.txt in the test environment and set VASM to the pinned
vasmm68k_mot executable. Set HEADLESS and PUAE_CORE to the verified test tools.

```
python port/tools/build_recovery_character_confirmation_probe.py
# W=0,1,2,3,4, each in a new process, no RAM_LOAD or RAM_LOAD_FRAME:
env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
 RAM_OUT="$PWD/port/build/character-confirmation-stock/recovery-character-confirmation-w${W}-chip.bin" \
 "$HEADLESS" "$PUAE_CORE" \
 "$PWD/port/build/character-confirmation-stock/recovery-character-confirmation-w${W}.adf" \
 "$PWD/artifacts/a1200-system" 1800 \
 > "port/build/character-confirmation-stock/w${W}-amiga.log" 2>&1
python port/tests/verify_recovery_character_confirmation_probe.py port/build/character-confirmation-stock
python port/tests/test_recovery_character_confirmation_probe_rejection.py port/build/character-confirmation-stock
python port/tests/test_recovery_character_confirmation_build.py
```

This proves bounded emulated-target correctness and stock allocation only. It is
not physical Amiga testing, live gameplay, game speed, audible Paula output,
real-time NMI timing, alternate-character confirmation or a displayed native
character menu. The retained source-only report and manifest contain no ROM,
firmware or private generated binaries.
