# Private command07 target probe

`--music07` is an opt-in, cartridge-bearing diagnostic. It executes fourteen
helper calls using thirteen distinct static helpers, including a second call
to the existing request-intake helper. It stops at the second `$C0F3`, after
queued07 is consumed and initialized, before the subsequent audio tick.

## Private resources and build

Run `port/tools/build_recovery_reset_probe.py --music07` with VASM configured.
This mode requires the private Europe cartridge, SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
The builder verifies that hash before extracting a 16384-byte bank3 data view
under ignored `port/build`, writes it read-only, and includes it only as data.
Its report explicitly sets `proprietary_inputs=true`. All eight earlier modes
remain source-only and do not load this input or include this resource.
An isolated temporary-tree test rebuilt all eight byte-identically without any
input directory; music07 rejected both missing input and a wrong cartridge hash
before creating its private resource or ADF.

The resulting `recovery-music07-probe.adf` is **private**, not a source-only
build and not a deliverable for publication. Resource bytes are not embedded
in public source, tests, or this report. The caller-owned resource contract,
validated pointer bounds, and static translation are documented in
`recovery_music07_command.md`; no runtime instruction decoder is added.

Payload size is 37,694 bytes, rounded allocation 37,888 bytes. Private ADF SHA256:
`fc8256d7d2fd1b21c22daa9151321d9438b343b655c6656e1cdceb188a34445a`.

## Executed target proof

The actual diagnostic passed 600 frames on pinned `headless-recovered-title`
and `puae_libretro.so`, stock PAL A1200OG, 68020, 2 MiB Chip RAM, no Fast RAM,
CPU/memory/blitter cycle-exact configuration, with unchanged supplied firmware.
The target log records `PASS runs=600 video_callbacks=600`. Exact provenance
and hashes are retained privately in `logs/recovery-music07-probe-provenance.json`.

Verify with:

```
python port/tests/verify_recovery_reset_probe.py --music07 port/build/recovery-music07-probe-chip.bin
python port/tests/recovery_test_music07_target.py
```

The continuous original-ROM reference executes 15,086 instructions, including
690 bank3 instructions across both NMIs. It starts at the established `$FE24`
context, calls actual `nmi()` twice, and reaches the second `$C0F3` without
captured-state injection, reference RAM patches, or raw status edits.
`architectural_status_view` only canonicalizes virtual B/U for comparison.
The preceding setup helper still deliberately requires D=0 for its generic
py65 arithmetic oracle; that is not a claim about NES decimal arithmetic.

Passed comparisons include:

- Actual target step counter 14, thirteen distinct helpers, all 2048 RAM bytes
  and eight context bytes; SP=$B1, final native/raw P=$24, final bank3.
- 35 mapper records, 2,248 PPU records, 14 APU records, 18 controller records,
  and both DMA snapshots (512 bytes). These include the unchanged prior
  49-record palette publication, five new bank-selection records and seven
  new command initialization APU writes.
- Target register snapshots around both new calls, balanced native stack,
  30 intact buffer guards, valid nonoverlapping buffer ranges, and exact
  resource bytes/hash over the entire 16384-byte view. Exact ordered resource
  reads and RAM/hardware interleaving are separately checked by host tests.
- Original second-NMI frame and nested `$C2A8` continuation preserved; queued07
  is consumed through actual original request intake, with other queue slots
  preserved. The palette flag remains consumed. No pending effect is fabricated.

All eight previous payload/ADF pairs rebuilt byte-identically and their old
matching dumps pass. The reusable negative test first checks all nine positive
baselines, then rejects bit-corrupted reports/buffers/resources, explicit
alias/out-of-range resource/journal pointers, and both directions of all eight
old/new mode mismatches. Executed counts are recorded in the private negative
report: 1,155 bit-corruption rejections, 18 explicit pointer alias/range
rejections, and 16 cross-mode rejections after nine positive baselines.
It checks every new mapper/APU journal byte, representative resource
bytes including header/bounds, prior journals/DMA, RAM, context and all guards.

Only the opt-in probe, builder, verifier, new negative test and this report are
changed in this integration. No prior helpers/tests, README, aggregate/public
scripts, commits, publication, or delivered Z/X ADF are changed. Public recovered
source remains earlier title/menu only; later playable/audio source remains
lost. This is new recovery work and emulated-target semantic evidence, not
full boot, gameplay, audible Paula playback, physical-Amiga or speed validation.
