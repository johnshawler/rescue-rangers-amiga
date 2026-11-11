# Private first music fetch and command04 target checkpoints

Two opt-in cartridge-bearing diagnostics extend the existing continuous
command07 target path. `--music-fetch` executes fifteen calls to fourteen
distinct static helpers and stops at `$83A0`. `--music-command04` executes
sixteen calls to fifteen distinct helpers and stops at `$839D`, immediately
before the next stream-byte fetch. These are new recovery work, not recovered
later playable/audio source.

## Build and privacy

```
python port/tools/build_recovery_reset_probe.py --music-fetch
python port/tools/build_recovery_reset_probe.py --music-command04
```

Both modes require VASM and the private Europe cartridge with SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
The builder checks the complete ROM hash before extracting the same bounded
16,384-byte bank3 view used by music07. It atomically replaces the ignored,
read-only resource file. Both build reports set `proprietary_inputs=true`.
No resource bytes are embedded in public source or tests. These ADFs and
resources remain private, ignored, and ineligible as source-only deliverables.

- Fetch payload: 38,202 bytes, allocation 38,400 bytes. ADF SHA256
  `196588471dda56473b43cb82f3002fe1889db46c1507d02b65359f174a0efe78`.
- Command04 payload: 38,712 bytes, allocation 38,912 bytes. ADF SHA256
  `c8a07e3913d52e0608e191ea9562fac942cd42f09a873d1d50b75a907d5d7327`.

All nine earlier payload/ADF pairs rebuild byte-identically, including the
private music07 pair. All nine matching historical target dumps pass the
updated verifier. Isolated temporary-tree tests rebuild all eight source-only
modes without any ROM directory, preserving their bytes. Every private mode
rejects missing and wrong-hash ROMs before creating its resource or ADF.

## Actual stock target evidence

Both diagnostics executed 600 frames with pinned `headless-recovered-title`
and `puae_libretro.so`, unchanged supplied firmware, PAL A1200OG, 68020,
2 MiB Chip RAM, no Fast RAM, and CPU/memory/blitter cycle-exact configuration.
Both logs record `PASS runs=600 video_callbacks=600`. Tool/firmware identities
match the previous music07 run. Exact hashes, configuration and old artifact
hashes are retained privately in
`logs/recovery-first-music-target-provenance.json`.

```
python port/tests/verify_recovery_reset_probe.py --music-fetch port/build/recovery-music-fetch-probe-chip.bin
python port/tests/verify_recovery_reset_probe.py --music-command04 port/build/recovery-music-command04-probe-chip.bin
python port/tests/recovery_test_first_music_target.py
```

The verifier starts the original-ROM reference at the established `$FE24`
context and invokes actual `nmi()` twice. It executes 15,148 instructions to
the fetch boundary and 15,188 to the command04 boundary, including 746 and
786 bank3 instructions respectively. There are no captured-state injections,
raw P edits or reference RAM patches. The named `architectural_status_view`
only canonicalizes virtual B/U for comparison. Helper14 retains explicit D=0
scope because the generic py65 decimal ADC oracle differs from NES arithmetic.

Both checkpoints pass:

- Complete 2,048-byte RAM and eight-byte context equality, final SP `$AB`,
  final bank3. Fetch P is `$A4`; command04 P is `$26`.
- All 35 mapper, 2,248 PPU, 14 APU and 18 controller records, plus both
  256-byte DMA snapshots. Neither new helper adds hardware-write records.
- Exact six-byte fetch journal (one original resource read). Command04 also
  matches its separate fourteen-byte journal (three original resource reads),
  retaining the preceding fetch journal unchanged. Original-ROM instruction
  boundaries identify stream and dispatch-table reads in semantic order.
- All 16,384 resource bytes and their hash unchanged. The helpers' separate
  host differential tests establish byte-only native read ordering, including
  command04's two additional read-only preflight reads, which are deliberately
  not original semantic journal records.
- Explicit native D1–D7/A0–A6 snapshots around each new call, success statuses,
  balanced native stack, bounded disjoint buffers and intact guards (32 fetch,
  34 command04 guard regions).
- Preserved original second-NMI frame and nested `$C2A8` task continuation,
  consumed07 queue slot and unchanged other queued slots. The palette request
  remains consumed. No pending task or audio work is fabricated.

The reusable negative suite first requires all eleven matching positive
baselines. It then checks every new resource journal byte, every guard byte,
complete DMA snapshots, all command07 mapper/APU and controller records,
representative prior journals, RAM/context, resource headers/dispatch/stream
positions and evenly spaced resource bytes. Explicit pointer mutations test
aliases against all other buffers and both address bounds. Both directions of
every new/other-mode mismatch are rejected. Executed counts: fetch rejects 1,453 bit corruptions, 68 pointer aliases/range
violations and 20 cross-mode attempts; command04 rejects 1,503 bit corruptions,
90 pointer aliases/range violations and 20 cross-mode attempts. All eleven
positive baselines and six missing/wrong-ROM build rejections pass first.
Counts are also retained privately in
`logs/recovery-first-music-target-negative.json`.

The combined checkpoint's public suite includes the ROM-free music contracts
and all eight pinned source-only disk hashes. README and aggregate scripts
integrate these target modes and the host-only stream-fetch/command05 extension.
The target work itself did not alter existing helpers. Original inputs and the
separately delivered Z/X ADF remain unchanged.

This proves bounded semantics on an emulated stock target. It does not prove
full boot, gameplay, completion of the music tick or RTI, audible Paula,
physical-Amiga behavior or performance. Earlier title/menu source remains the
recovered source; later playable/audio source remains lost.
