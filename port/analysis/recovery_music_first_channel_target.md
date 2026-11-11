# Private first-channel music-event target checkpoint

`--music-first-channel` is one opt-in extension of the existing channel-setup
probe. It composes the earlier 22-call chain with four unchanged reusable
stream fetch calls and the four frozen instrument08/control18/control09/rest
helpers. It executes **30 calls to 23 distinct static 68020 helpers**, ending
naturally after the first channel's original RTS at PC=$8085, SP=$AD and
stream pointer=$A2D1. There is no runtime CPU opcode interpreter.

## Build and execution

```
python port/tools/build_recovery_reset_probe.py --music-first-channel
python port/tests/verify_recovery_reset_probe.py --music-first-channel port/build/recovery-music-first-channel-probe-chip.bin
python port/tests/recovery_test_music_first_channel_target.py
```

Use VASM pointing to `vasmm68k_mot` and PYTHONPATH including the installed
inspection dependencies. The builder requires the private Europe ROM with
SHA256 `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
It verifies the complete hash before generating any resource or payload.
Bank3 is a bounded 16,384-byte resource, atomically replaced and read-only.
The resource, payload, ADF and Chip dump are ignored private artifacts.
The build and verification reports set **proprietary_inputs=true**. This
cartridge-bearing diagnostic is never a source-only disk.

Payload size is 43,924 bytes, allocation 44,032 bytes. Private ADF SHA256:
`a7a3b83c461a40fc7e948f47e918bee25345f6083abab7275569a425d8d33dfd`.
Payload SHA256:
`7b6819e27730cb257e7b668b4b0bf65bbdf3d36483ff3ca988adf66e862a3b6a`.

Actual execution used pinned `headless-recovered-title`, `puae_libretro.so`
and the unchanged supplied firmware for 600 frames. The log confirms
`PASS runs=600 video_callbacks=600`. Configuration is PAL A1200OG, 68020,
2 MiB Chip RAM, zero Fast RAM, and CPU/memory/blitter cycle-exact. Frontend,
core and firmware hashes match the preceding channel-setup target. Private
provenance is retained in `logs/recovery-music-first-channel-target-provenance.json`.
No RAM fixture loading, CPU-state injection or oracle patching was used.

## Independent target verification

The verifier executes the actual cartridge continuously from $FE24 through
two real `ref.nmi()` events and 15,567 original instructions, including
1,165 bank3 instructions. It does not patch reference RAM or raw P. Only the
named architectural comparison view normalizes virtual B/U. Earlier
ADC-bearing helpers and the new instrument/rest helpers retain their D=0
scope because generic py65 decimal arithmetic differs from NES arithmetic.

Verified results:

- Complete final 2,048-byte RAM and eight-byte context match. Context is
  PC=$8085, A=$FF, X=$2B, Y=$18, P=$A4, SP=$AD, reserved=$A7. Original stack
  residue, second-NMI frame and pending nested $C2A8 continuation match.
- All prior 35 mapper, 2,248 PPU, 14 APU and 18 controller records match,
  as do both complete 256-byte DMA snapshots. The new event calls produce
  no additional hardware writes.
- Eight new resource journals have counts 1,5,1,3,1,3,1,1. Their 16 records
  preserve original order, giving 33 total stream/event records including
  earlier calls. The final rest journal's unused record is checked as zero.
  Bounded read-only dispatch preflights are not original semantic records;
  unchanged host suites prove their byte-only read order and inert rejection.
- All eight new context snapshots match original boundaries, in addition to
  the six earlier channel-setup snapshots. Snapshot copies do not change
  emulated RAM/context.
- Every new call checks success and preserved D1–D7/A0–A6. Native stack is
  balanced; all 33 bounded buffers are disjoint and all 66 guards intact.
  The complete immutable resource matches SHA256
  `01b6e72da88510e9bfa3071ba0a782cd585401d55c5bf01e7fe1a79baf22f7ab`.
- Channel $072B=$23, $072F=$0B, $0737=$FF, $075B=$01, $0763=$18,
  $076B=$FF, instrument pointer C5/C6=$8B67 and tempo C8/C9/CA=$00/$02/$49.

## Regression and negative verification

The new negative suite requires all thirteen matching target baselines
before any corruption. It rebuilds all twelve prior payload/ADF pairs and
requires byte identity, including the preceding channel-setup pair. It also
builds all eight source-only modes in an isolated tree without a ROM and
checks that all five private modes reject both missing and wrong-hash ROMs
before writing resources, payloads or ADFs.

The negative suite covers every new journal byte, including padding, every
new context-snapshot byte, every guard, both DMA snapshots, full controller
and command07 hardware journals, representative older journals and RAM,
dispatch/stream/table resource bytes and evenly spaced resource contents.
Every private journal/resource/snapshot pointer is aliased against every
other buffer and both invalid address bounds. Every other target mode is
rejected in both mismatch directions. Executed counts and results are
retained privately in `logs/recovery-music-first-channel-target-negative.json`.
The completed run passed 2,382 corruption rejections, 714 alias/range
rejections and 24 cross-mode rejections, after all thirteen positive
baselines, twelve byte-identical prior pairs, eight ROM-free source-only
builds and ten missing/wrong-ROM failures.

The shared probe/builder/verifier and dedicated target test implement this
opt-in integration. Existing helper implementations remain unchanged; README
and aggregate/public scripts include the new checkpoint. The original/delivered
Z/X ADF is unchanged; later playable/audio source remains lost.

The next dependency is the outer channel loop's PLA at $8085 and remaining
channels. Pitched-note paths and envelope progression remain untranslated.
This bounded emulated-target proof is not a complete music tick/RTI, audible
Paula, full boot, gameplay, physical-hardware or performance claim.
