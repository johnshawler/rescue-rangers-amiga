# Private channel-setup target checkpoint

`--music-channel-setup` is one opt-in extension to the existing command04
probe. It composes reusable stream fetch, command05, the same fetch,
command06, the same fetch, and stream-command07-volume. The latter is NOT
the earlier queued `recovery_music07_command` initialization helper.
The checkpoint executes 22 calls to 19 distinct static 68020 helpers and
stops at PC $839D, SP $AB, channel pointer $A2CA. The next command08 remains
unconsumed. No existing helper source or contract test was changed.

## Build and private inputs

```
python port/tools/build_recovery_reset_probe.py --music-channel-setup
python port/tests/verify_recovery_reset_probe.py --music-channel-setup port/build/recovery-music-channel-setup-probe-chip.bin
python port/tests/recovery_test_music_channel_setup_target.py
```

Set VASM to the installed vasmm68k_mot and PYTHONPATH to the inspection
`.deps` directory. This mode requires the private Europe ROM with SHA256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
The full hash is checked before generating any resource or payload. The
same bounded 16,384-byte bank3 resource is atomically replaced and made
read-only. The report sets `proprietary_inputs=true`; the resource, payload,
ADF and Chip dump are ignored private artifacts, never source-only output.

Payload size is 41,052 bytes, allocation 41,472 bytes. ADF SHA256:
`d867ea57ef950fde0e975653d94127aee207d2e07753a81d20871e972b3aed60`.
All eleven prior payload/ADF pairs rebuild byte-identically, and all eleven
matching historical Chip dumps pass the updated verifier. Eight source-only
modes also rebuild identically in an isolated tree with no ROM directory.
All four private modes reject both absent and wrong-hash ROMs before writing
resource, payload or ADF.

## Actual stock target execution

One actual run used pinned `headless-recovered-title`, `puae_libretro.so`
and unchanged supplied Kickstart firmware for 600 frames. The log records
`PASS runs=600 video_callbacks=600`. Configuration is PAL A1200OG, 68020,
2 MiB Chip RAM, zero Fast RAM, CPU/memory/blitter cycle-exact. Hashes match
the previous first-music target tools/firmware. Full provenance is retained
privately in `logs/recovery-music-channel-setup-target-provenance.json`.

The independent verifier executes the actual cartridge continuously from
$FE24 through two actual `ref.nmi()` events and 15,350 original instructions,
including 948 bank3 instructions. It neither patches reference RAM/raw P
nor injects captured state. The named `architectural_status_view` only
normalizes virtual B/U for comparison. Earlier ADC helpers retain their
D=0 oracle scope; the new channel commands introduce no ADC/SBC requirement.

Verified target results:

- Complete final 2,048-byte RAM and eight-byte context match, including
  original stack residue, preserved second-NMI frame and nested $C2A8 task
  continuation. Final P=$25, bank3; $0767=$96, $0737=$3F, C8/C9/CA=$00/$02/$49.
- All prior 35 mapper, 2,248 PPU, 14 APU and 18 controller records match,
  together with both complete 256-byte DMA snapshots. The new six calls
  add no hardware journal effects.
- Six separate new resource journals match counts 1,4,1,3,1,3, or 13 new
  records. Including the original fetch and command04 gives 17 total.
  Command05's four records and command06/volume07's three records retain
  operand/dispatch read ordering. Read-only dispatch preflights are not
  original semantic journal records. Host helper tests separately prove
  byte-only native read order, immutable resources and rejection contracts.
- Six eight-byte context snapshots match independent original boundaries.
  Probe snapshots copy comparison data without changing emulated RAM/context.
- Every new call checks preserved D1-D7/A0-A6 and success status. Native
  stack is balanced; all 24 bounded buffers are disjoint and all 48 guard
  regions intact. The complete resource remains unchanged, SHA256
  `01b6e72da88510e9bfa3071ba0a782cd585401d55c5bf01e7fe1a79baf22f7ab`.

## Negative validation

The new reusable negative suite requires all twelve matching positive target
baselines before any corrupted input. It checks every new journal and
intermediate-context byte, all guards, both DMA snapshots, complete prior
command07 mapper/APU and controller journals, representative older journal
bytes, RAM and final context, resource dispatch/stream bytes and evenly
spaced resource contents. Each private resource/journal/snapshot pointer is
aliased against every other buffer and both invalid address bounds. Every
other mode is rejected in both mismatch directions. Exact executed counts
are 1,881 corruption rejections, 300 alias/range rejections and 22 cross-mode
rejections, retained in `logs/recovery-music-channel-setup-target-negative.json`.

The initial target work also passed the existing public suite and eight source-only ADF hashes. Integration now adds the channel contracts and the separate source-only player-initialization probe to public and full validation.

This is newly authored recovery, not recovered later playable/audio source.
The original/delivered Z/X ADF is unchanged; later playable/audio source
remains lost. This bounded emulated-target proof makes no full tick, RTI,
audible Paula, full boot, gameplay, physical-hardware or performance claim.
Existing helper implementations remain unchanged; README and aggregate/public scripts document and validate this checkpoint.
