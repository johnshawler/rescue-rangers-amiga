# Private resident reset-to-C597 target diagnostic

A new, separate private diagnostic passes all **533 native helper intervals**
from FE24 reset through the complete startup fade to C597 on emulated stock
PAL A1200 hardware. It calls 39 distinct helpers from the 40-entry composite.
The published 68-call target and all historical helper/probe sources remain
unchanged. This adds no gameplay continuation, Paula renderer or delivered disk.

## Resident execution and independent comparison

The generated driver initializes one original 2 KiB RAM buffer to A5 and one
CPU context to the authored reset inputs, then keeps both buffers resident.
Every helper receives the preceding helper's actual outputs. It never copies
reference/captured state back into those buffers, fabricates scheduler readiness,
changes original return frames, or skips audio. Controller inputs are both zero.
The original-ROM reference independently starts at the same authored reset and
executes continuously for **40,287 original instructions**, including **18 real
reference NMIs**. Raw reference P is never modified. Only a named architectural
comparison view clears virtual B and sets U for context comparison. Saved
original frame bytes remain exact.

The driver captures all 2 KiB RAM, eight context bytes and each complete journal
(including unused zeros and DMA bytes) after every call. D0 is checked against
the required semantic result, D1-D7/A0-A6 against their saved values, and the
native stack against its initial position. Native journals have lower and upper
16-byte guards. RAM, context, immutable bank3 resources, native stack and the
whole snapshot workspace have guards. The verifier rejects unaligned, out-of-
Chip, partially overlapping, guard-overlapping and report-overlapping pointers.
The persistent MMC1 state, including its serial latch, is independently replayed
from actual native mapper journals and compared at all 533 boundaries.

All ordered native PPU/APU/mapper/controller/resource journals and the fade/yield
RAM journals match the independent execution. All 18 DMA page snapshots match
(4,608 bytes). The reference observes 8,217 RAM writes, 2,525 PPU events, 200
mapper writes, 324 controller events, 784 semantic resource reads and 114 APU
writes. The final context is C597/A10/X10/YFF/P24/SPBF/reservedA7. The mapper
ends at control1E, CHR0=00, CHR1=10, PRG06 with an empty serial latch.

**Evidence boundary:** target snapshots prove full RAM equality after every
helper, not an instrumented trace of every target memory access. Ordered RAM
writes outside the fade/yield journals, global access whitelists and resource
preflight-read ordering are established by the separately rerun resident host
harness, using the same final helper sources. The target report explicitly marks
`target_access_trace=false`. Reference effect counts are not mislabeled as a
hardware bus trace. The verifier imports reference routines but never constructs
or executes a native host CPU to obtain expected states.

## Stock configuration and compact private artifact

The actual emulator log passes checks for A1200OG, 68020, no FPU/MMU/JIT, 2 MiB
Chip RAM, zero Fast/slow RAM, PAL 50 Hz, and CPU/memory/blitter cycle-exact modes.
The approved headless and PUAE binaries and supplied A1200 firmware were reused.
The run completed 1,800 video callbacks. That is the emulator capture window,
not 1,800 original game frames. The 533 helper calls are logical intervals, not
533 emulated frames, and execution stops at C597.

Each snapshot uses exactly 2,100 bytes plus its helper's journal capacity.
The snapshot workspace is **1,199,154 bytes**. The native payload is **175,368
bytes**, with a **1,374,720-byte** total cleared Chip allocation. Boot allocates
and clears BSS through the existing operating-system allocation contract and
reads only the sector-rounded payload. It neither stores nor loads a large
zero snapshot image from disk. The memory requirement fits the verified stock
2 MiB configuration without Fast RAM.

The private disk contains 16 KiB of cartridge bank3 data. It is explicitly
cartridge-bearing, never source-only. The builder rejects missing/wrong ROMs
before creating output. Its output directory is restricted to ignored
`port/build`. No cartridge extract, firmware or captured state is included in
these public source/report additions. Generated drivers, bank extract, binary,
ADF and Chip dump stay ignored, as do all private logs.

## Tests and preservation

- Final target verifier: all 533 RAM/context/journal comparisons passed.
- Mutation suite: 5,155 dump corruptions rejected, including every helper's
  context/RAM/journal/header and both journal guards, plus pointer/partial-alias/
  range/report overlap, stack, immutable resource and malformed dump cases.
- 18 historical cross-mode Chip dumps rejected.
- 35 changed/missing/conflicting effective-configuration log cases rejected.
- Isolated build with copied source/tests and only declared installed tools:
  all seven generated files reproduce byte-for-byte, including a second build.
- Missing and wrong cartridge builds produce no output directory.
- All 13 historical payload/ADF pairs and the frozen 68-call target independently
  rebuilt byte-identically. The strengthened preservation test checks 384
  historical and target dependency files: tracked files, historical outputs,
  supplied inputs/firmware, all five new target Python files, all 40 helper
  sources named by the builder, boot source and 19 imported in-repository Python
  reference dependencies. Explicit dependency checks cover the audio/fade
  helpers without relying on Git tracking state. Unrelated experimental files
  are excluded. Counts overlap and are deduplicated for hashing; the total
  varies with the validated workspace inventory.
  The strengthened isolated build passed with all seven generated files and
  existing payload/ADF hashes unchanged.
- Final resident host harness passed unchanged: 533 calls, 18 NMIs, 114 APU
  writes, full RAM/context/effects, ABI, DMA/journals, resources and global bounds.

The corrected active-control source used here has SHA256
`fe0b41ba934dafa2388a4fd2d5701362828b23426effe1853fc304db7920f69e`.
The final host composite is 21,468 bytes, SHA256
`a52ba0c5da9188eb1a5df40bc24eaa67e20978181beb950202c22c52464da5eb`.

Private output hashes:

- Payload: `54d7541b18e3d537fe401f3e35a0eb15e34f91aecb56bf4dd6d0b6a5657fb125`
- ADF: `67d97979cf0a789459af433d3b347d5a4abf2ef14c451a2c22f32b3d8eb8f69e`
- Chip dump: `fec542033e46c0c42ecdfe66b6ec6e7305d51b1f9367115beb677f224f24b724`
- Cartridge: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`

## Reproduction

Set VASM to the approved `vasmm68k_mot` and PYTHONPATH to the existing inspection
`.deps` directory. No undeclared source checkout or external fixture is needed.
Run `python port/tools/build_recovery_resident_fade_probe.py`. The build report
records the exact source hashes. With the approved HEADLESS and PUAE_CORE paths,
run from the repository root:

```
PUAE_MODEL=A1200OG RAM_OUT="$PWD/port/build/recovery-resident-fade-probe-chip.bin" \
  "$HEADLESS" "$PUAE_CORE" "$PWD/port/build/recovery-resident-fade-probe.adf" \
  "$PWD/artifacts/a1200-system" 1800 \
  > logs/recovery-resident-fade-probe-amiga.log 2>&1
python port/tests/verify_recovery_resident_fade_probe.py \
  port/build/recovery-resident-fade-probe-chip.bin \
  --amiga-log logs/recovery-resident-fade-probe-amiga.log
python port/tests/test_recovery_resident_fade_probe_rejection.py \
  port/build/recovery-resident-fade-probe-chip.bin \
  --amiga-log logs/recovery-resident-fade-probe-amiga.log \
  $(find port/build -name '*-chip.bin' ! -name '*resident-fade*' -printf '--old-dump %p ')
python port/tests/test_recovery_resident_fade_build.py
python port/tests/recovery_test_resident_startup_fade.py
```

Private evidence is in `logs/recovery-resident-fade-{build.json,build-tests.json,
host-final.log}` and `logs/recovery-resident-fade-probe-{amiga.log,verify.json,
rejection.json}`. The diagnostic was developed separately from the frozen 68-call target.
It is now included in the private startup validation extension after independent
review. Existing helper/probe binaries, original inputs and the delivered disk
remain unchanged. C597's JSR C14E remains outside this diagnostic. This is not continuous
gameplay, audible Paula output, a speed test or physical Amiga validation.
