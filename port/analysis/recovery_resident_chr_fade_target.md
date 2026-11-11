# Stock PAL A1200 resident CHR and title-fade checkpoint

This private diagnostic extends the validated 533-call C597 target checkpoint
to C5D1. Four separate full-reset executions of static native 68020 routines
all execute the same 1024-call sequence. No runtime 6502 interpreter, reference
RAM or context injection, state restoration, synthetic readiness or skipped
pending work is present on the target. Cartridge CPU execution is confined to
the offline independent expected-result oracle.

## Bounded capture and stock allocation

The four runs capture complete 2048-byte RAM after calls 0–255, 256–511,
512–767 and 768–1023 respectively. Each run also captures all 1024 eight-byte
contexts and all complete variable-size journals, including their DMA payloads.
Every run initializes its resident RAM and context exactly once at reset and
executes every earlier and later native call. Each call has its own unreused,
zero-initialized journal and lower/upper canaries. No intermediate state is
loaded from an earlier run. Collectively the windows cover every RAM boundary;
they must not be described as 1024 RAM snapshots from a single execution.

Each capture workspace is 768,376 bytes. Payloads are 306,318 bytes (windows
0–2) and 306,322 bytes (window 3). The boot loader requests exactly 1,075,200
bytes with MEMF_CHIP | MEMF_CLEAR, including the snapshot tail canary and sector
rounding. This leaves 1,021,952 bytes of the stock 2 MiB outside that allocation.
The native stack is 4096 bytes, RAM is 2048 bytes, context is eight bytes, and
both immutable 16 KiB cartridge resource banks are included in the payload.
No Fast RAM is requested or configured. The complete driver, native routines,
private resources and capture workspace all reside in the one Chip allocation.

The driver retains native ABI comparisons (D1–D7/A0–A6), exact SP checks,
helper-status comparisons and completion count on every call, including calls
outside the current RAM window. Runtime report pointers are checked for
alignment, Chip bounds, pairwise overlap, report overlap and guards. Resources,
resident final state and all captured journals are checked after completion.
Mapper serial writes from all native journals are replayed without resetting
the latch between calls, then compared at every boundary to the original-ROM
mapper. The target does not drive physical NES mapper hardware.

## Actual emulated-target evidence

Each new ADF completed 1800 emulator frames with 1800 video callbacks. The
effective logs, not only requested settings, verify A1200OG, 68020, AGA,
PAL 50 Hz, 2 MiB Chip, zero Fast/slow RAM, no FPU/MMU/JIT, and cycle-exact CPU,
memory and blitter modes. All four real Chip dumps pass the verifier. A separate fresh window-0
execution also passes and reproduces its entire 2 MiB Chip dump byte-for-byte.

For every run:

- 1024 calls across 46 executed helper types reach C5D1 naturally.
- All 1024 context snapshots and journals match the original cartridge.
- All 1024 mapper/latch boundaries match; DMA coverage is 8960 bytes.
- Both resource banks, all guards, final RAM/context, ABI and stack pass.
- Logical reference NMIs: 35; original instructions: 79,077.
- Original ordered effects: 16,511 RAM writes, 4301 PPU events, 385 mapper
  writes, 630 controller events, 2147 semantic resource reads and 252 APU writes.
- Final context is C5D1/F0/F0/FF/A5/BF/A7. Final mapper is control 1E,
  CHR0=1F, CHR1=1F, PRG02, with an empty serial latch.
- Pending CHR requests 9F are genuinely consumed. RAM1A/RAM1B are zero and
  RAMF2/RAMF3 are 1F. The title fade returns with RAM0F=F0.

The oracle imports only the Python standard library and py65. It executes the
unaltered approved Europe ROM continuously, observing original instruction
boundaries, resource accesses and device writes. It does not import or execute
native code. It independently reproduces the prior oracle's first 533 complete
results, journals, mapper checkpoints and intervals. Two reset executions are
identical. Raw reference status and saved frames are untouched; comparisons
use the explicitly documented architectural B=0/U=1 status view. Decimal mode
is never set by this genuine continuous sequence.

## Validation and preservation

The new build test copies source and tests into an isolated temporary checkout.
All 23 generated outputs, including four private ADFs, reproduce byte-for-byte
there and on a second build. Missing or wrong cartridge input fails before
output creation and preserves existing outputs. The 51 build dependencies
match the exact builder manifest. The portable build test snapshots current
historical inputs itself. An optional --preservation-inventory additionally
checks an earlier inventory. The --delivered-adf option explicitly checks the
supplied historical disk against its approved SHA; when omitted, the report
says not supplied and makes no delivered-disk preservation claim. All 515 pre-existing files in the recorded
preservation inventory remained unchanged, including historical target
artifacts, input files and firmware. The previously delivered ADF remains
SHA256 6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17.

The negative suite mutates the actual successful Chip dumps, covering marker,
status/count/window, pointers, bounds, overlap, stack, every context byte,
RAM samples at every captured call, journal headers/data/guards, every DMA
byte, mapper serial writes, resources, malformed dumps and wrong cartridge.
It also rejects historical diagnostic modes and missing, changed or conflicting
stock configuration fields. Exact counts are recorded in the private
rejection.json result; no synthetic dump is accepted as a positive baseline.

## Files and reproduction

New source/test files:

- port/tools/build_recovery_resident_chr_fade_probe.py
- port/tests/recovery_resident_chr_fade_target_oracle.py
- port/tests/verify_recovery_resident_chr_fade_probe.py
- port/tests/test_recovery_resident_chr_fade_probe_rejection.py
- port/tests/test_recovery_resident_chr_fade_build.py

All generated private data is under ignored port/build/chr-fade-stock. It
contains proprietary cartridge resource bytes and must never be presented as
a source-only distribution. Build and final evidence manifests record source,
artifact, capture and log SHA256 values.

Set VASM to the approved vasmm68k_mot and PYTHONPATH to the inspection .deps
folder. Build with:

```
python port/tools/build_recovery_resident_chr_fade_probe.py
```

For each window W=0,1,2,3, start a fresh emulator process with no RAM_LOAD or
RAM_LOAD_FRAME environment value and no Fast-memory override:

```
PUAE_MODEL=A1200OG \
RAM_OUT="$PWD/port/build/chr-fade-stock/recovery-resident-chr-fade-w${W}-chip.bin" \
 "$HEADLESS" "$PUAE_CORE" \
 "$PWD/port/build/chr-fade-stock/recovery-resident-chr-fade-w${W}.adf" \
 "$PWD/artifacts/a1200-system" 1800 \
 > "port/build/chr-fade-stock/w${W}-amiga.log" 2>&1
python port/tests/verify_recovery_resident_chr_fade_probe.py port/build/chr-fade-stock
python port/tests/test_recovery_resident_chr_fade_probe_rejection.py port/build/chr-fade-stock
python port/tests/test_recovery_resident_chr_fade_build.py
# Optional: add --delivered-adf /path/to/rescue-rangers-stock-zx.adf
```

## Boundaries and non-claims

This is a bounded emulated stock-target checkpoint, not physical Amiga testing,
continuous gameplay, real-time performance, fixture-free displayed title or
audible Paula output. Logical NMI placement is a diagnostic schedule. Target
RAM snapshots prove boundary equality; this diagnostic does not claim a target
bus trace of every native RAM access. Ordered RAM writes are independently
journaled only by the fade/yield helpers. Other device/resource journals and
DMA buffers are compared in full. Host trace tests provide separate evidence.

The next untranslated original operations at C5D1 initialize tables from D657,
C73F and C75D, set BE/BF=84/03 and invoke A000 in bank 2. Nonempty unsupported
video queues, deferred work, callbacks, unsupported music commands and
arbitrary asynchronous interrupts remain outside this checkpoint. Command02
is linked but not reached or counted as exercised by these actual runs.
No existing source, test, ADF, index or branch was changed for this diagnostic.
