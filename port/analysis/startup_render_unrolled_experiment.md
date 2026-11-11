# Additive compact native renderer experiment

The accepted candidate reduces the measured frozen native-startup rendering
interval from 55,867 to 52,297 CIA-B E-clock ticks against an identically
instrumented control. This saves 3,570 ticks, 6.39%, approximately 5.03 ms at
709379 Hz. The candidate interval is approximately 73.72 ms. This remains far
outside a 20 ms PAL frame budget and is not a real-time game or gameplay claim.

The input is the actual state produced by the existing 1024-call native reset
schedule, with its real device journals and immutable cartridge graphics.
There is no injected framebuffer, fixture state, screenshot-derived data or
runtime NES CPU interpreter. No baseline source, checkpoint or ADF was edited.

## Design and retained experiments

Four isolated variants are built by
`tools/build_startup_render_unrolled_experiment.py`. The default is `compact`.
`RR_RENDER_VARIANT` selects the other retained variants:

- `baseline`: the unchanged background and sprite modules, with split timing.
- `optimized`: the initial, rejected, fully unrolled background experiment.
  This historical directory name does not indicate that it is faster.
- `paired`: two scanlines per background inner-loop iteration.
- `compact`: the paired loop plus a hoisted framebuffer tile-row address.

All three experimental variants also move the sprite row-count test ahead of
clearing its 32-byte ownership mask. A row with no selected sprites needs no
ownership data. The scratch area is explicitly destroyed by the existing ABI;
its final unused contents are not part of the contract. Occupied rows still
clear the complete mask before processing sprites.

The paired background loop performs precisely the same CHR reads, opacity
writes and five-plane writes as before. It advances pointers after two rows
instead of after every row. The compact variant additionally maintains the
framebuffer tile-row base in A2, avoiding the repeated multiply and address
construction for each dirty tile. MOVEM restores the caller's A2. Cache keys,
invalid-cache requirements, dirty-tile rejection, palette planes, transparent
pattern opacity and untouched borders are unchanged. No sprite flip, palette,
priority, clipping, first-eight selection or supported mask behavior is removed.
The startup consumer's admitted state and scroll limitations are unchanged.

Standalone assembled background sizes are 204 bytes for the baseline, 464 for
full unrolling, 244 for pairing and 236 for compact pairing. Full unrolling was
substantially slower on the target. Its larger instruction footprint is a
plausible explanation, but this experiment does not isolate cache-control
state or establish instruction-cache misses as the cause. Actual target
measurement, rather than instruction-count speculation, rejects that variant.

## Actual stock-target measurements

Each run uses A1200OG, PAL, 68020, AGA, 2 MiB Chip and zero Fast/slow memory,
with CPU, memory and blitter cycle-exact settings, and no JIT/FPU/MMU.
The effective log is checked by the inherited target verifier. No RAM_LOAD or
RAM_LOAD_FRAME is used. Display DMA is off during all measured rendering.

CIA-B E-clock ticks, in order admission/CHR, background, sprites, total:

- Instrumented baseline: 1,737; 39,002; 15,128; 55,867.
- Rejected full unrolling: 1,736; 72,538; 14,622; 88,896.
- Two-row pairing: 1,734; 37,569; 14,620; 53,923.
- Compact pairing: 1,734; 35,948; 14,615; 52,297.

The background interval improves by 3,054 ticks (7.83%). The sprite interval
improves by 513 ticks (3.39%). The original untouched baseline reported 55,858
ticks without split probes. Only the identically instrumented 55,867-tick
control is used for the improvement calculation. Timestamp reads, register
setup and boundary bookkeeping are included in the corresponding intervals;
these are useful stage measurements, not isolated instruction-only costs.
Small differences in the unchanged CHR stage are not claimed as optimization.

Two independent fresh 1800-frame executions of both the instrumented baseline
and compact candidate produce identical complete 2 MiB Chip dumps and raw
video captures within each variant, and thus identical measured timestamps.
Full unrolling and pairing each have one verified fresh execution.

No display-DMA contention result is claimed: this frozen path intentionally
renders before enabling the display. A live renderer would need a separate
contention, synchronization and frame-budget investigation. Disk loading,
Copper/palette setup and startup diagnostics are not included in rendering.

## Correctness and resource cost

The original independent per-pixel test suites are loaded read-only and run
against all four background modules and both sprite modules, each with three
random seeds: 204 actual assembled-code cases. Their independent references
check full output, opacity/cache where relevant, source preservation, ABI,
stack restoration and buffer guards. Adversarial cases include attribute
quadrants, palette-only changes, dirty-cache rejection after external writes,
CHR changes with and without invalidation, flips, transparency, hidden-sprite
priority, first-eight overflow, clipping, masks and rejected 8x16 mode.
Both baseline and candidate agree with the same independently computed output.

Every target variant passes the inherited native startup/journal/device oracle,
including all 1024 contexts/journals and 256 captured RAM boundaries. Every
51200-byte framebuffer matches both the independent original-cartridge event
oracle and the untouched frozen baseline. Every complete raw video capture
also matches the frozen baseline; the decoded expected image agrees with all
163840 RGB pixels of the actual 640x256 viewport at (40,18). Palette and Copper
pointers are checked, not inferred from a screenshot.

There are no new lookup tables, caches or runtime initialization passes. The
existing 1920-byte tile cache, 7680-byte opacity buffer and 2196-byte sprite
scratch remain unchanged. Background and sprite stack bounds remain 60 and
68 additional bytes respectively, plus the caller's return address.

Compact payload is 514508 bytes versus 514476 for the instrumented control:
32 bytes of renderer code growth. Both allocate 1283072 bytes of Chip memory.
The split-timing instrumentation itself adds 40 bytes versus the untouched
514436-byte frozen payload, including a 16-byte report record. No Fast memory
is introduced. The rejected fully unrolled payload is 514736 bytes and rounds
to a 1283584-byte allocation. These diagnostic builds retain the inherited
768376-byte capture workspace rather than presenting it as a production cost.

Two compact rebuilds reproduce all ten generated build files byte-for-byte.
Poisoning offline-oracle RAM/context/journal/raw-status bytes still leaves the
native schedule source identical. The target uses the original native consumer,
with only renderer include selection and stage timestamp probes changed.

## Preservation, private artifacts and reproduction

All baseline source/dependency/private-artifact hashes in its original manifest
and the delivered Z/X ADF hash were verified unchanged before a separate
report-only latch-wording clarification. No baseline code or private outputs
changed. This experiment made no index, branch, commit or publication changes.
The delivered Z/X SHA remains
`6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17`.

All generated assembly, cartridge resources, binaries, ADFs, Chip dumps and
screens remain private under the ignored directory
`port/build/startup-render-unrolled-experiment`. The source manifest contains
only paths, hashes and verification metadata, never proprietary bytes.

Set VASM, PYTHONPATH, HEADLESS and PUAE_CORE to the approved local tools.
From the repository, build each variant with `RR_RENDER_VARIANT=<variant>` and
`python port/tools/build_startup_render_unrolled_experiment.py`. Run the stock
headless frontend as in the frozen baseline, using each variant's
`startup-display.adf`, 1800 frames, `chip.bin`, `amiga.log` and `screen.ppm`.
For baseline and compact repeat to `repeat-chip.bin`, `repeat-amiga.log` and
`repeat-screen.ppm`. Then run:

```
python port/tests/test_startup_render_unrolled_experiment.py
python port/tests/test_startup_render_unrolled_build.py
python port/tests/verify_startup_render_unrolled_experiment.py
```

The build test defaults to compact and can verify another existing variant by
setting RR_RENDER_VARIANT. The comparison verifier requires all actual target
captures and the untouched frozen baseline, and fails if the compact candidate
is not faster than its instrumented control. The synthetic tests make no
hardware speed claim.
