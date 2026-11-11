# Opt-in stock-A1200 probe through NMI audio entry

The seven-helper probe now covers reset, first yield, an explicit modeled NES NMI entry/prefix, and fixed-bank dispatch up to bank-3 `$8003`. It stops before any banked audio instruction and neither plays audio nor completes the NMI.

## Build and reproduction

```
python port/tools/build_recovery_reset_probe.py --nmi-audio-entry
```

This distinct mode enables `FIRST_YIELD` and `AUDIO_ENTRY`, uses marker `CDRRAUD1`, and produces only `recovery-nmi-audio-entry-probe`-prefixed outputs. The flags `--first-yield` and `--nmi-audio-entry` are mutually exclusive at the command line. Default behavior remains unchanged.

Run the same pinned `headless-recovered-title` frontend, `libretro-uae/puae_libretro.so` and supplied A1200 firmware as the prior probes, with `PUAE_MODEL=A1200OG`, 600 frames, and a distinct `RAM_OUT`. Verify using:

```
python port/tests/verify_recovery_reset_probe.py --nmi-audio-entry port/build/recovery-nmi-audio-entry-probe-chip.bin
```

The source-only payload is 17544 bytes, allocated as 17920 bytes. New ADF SHA256:

`4d2ab14b1bb174838e7a7a48115bace0d78e4cf281f8edbf1a771048823ee86d`.

Both prior probe ADFs were rebuilt and remain byte-identical:

- Default: `840e6ff4a1403488f572b5e76e791ad3e97a4acb08f97045e312296d9a3b8225`.
- First yield: `e991d2a5c636a3001d61767ab60daaf307e96d00d290ae4b39d54c50da9d01d3`.

Stable title remains `03b774d76a6b547ff6b4b3ffd71428d381247f4802a40bab1a56eb3d1ea2b475`. Aggregate validation now checks all three independent probe modes; no prior delivered disk was replaced.

## Executed target proof

The pinned 600-frame run passed with logged 68020, PAL, 2 MiB Chip, zero Fast and CPU/memory/blitter cycle-exact configuration. It executes all seven native helpers with the same RAM/context and no inter-helper patches. The NMI-prefix and audio-entry journals are independently guarded, in addition to earlier outputs.

The verifier runs 13453 original instructions, injecting py65 hardware `nmi()` only at the first `$FE8D` reached after `$C574` task entry. It stops at `$8003` before fetching/executing its banked opcode. This is an explicit modeled original-NES interrupt, not a claim that an Amiga hardware interrupt fired or a NES timing proof.

Target comparisons passed:

- Seven completed helpers, all 2048 RAM bytes and eight context bytes.
- Twenty original reset mapper records plus five bank-3 publication records.
- 2188 video-clear events, one first-yield publication, ten NMI hardware events: 2199 total.
- All 256 OAM DMA source bytes, separately verified against original DMA capture.
- Sixteen intact buffer/stack guards and balanced native stack.
- Final PC=`$8003`, queued `$F0` dequeued, original JSR stack retained, and no banked audio instruction executed.

All seven host suites were rerun successfully. Both earlier target dumps still pass their original verifier modes. Nineteen negative-verifier cases rejected marker/helper-count/context changes, dequeue/index/JSR-stack changes, NMI event/count and first/last DMA corruption, both NMI guards, audio journal count/data/busy corruption, both audio guards, and use of either wrong earlier mode.

Private evidence is saved under `logs/recovery-nmi-audio-entry-probe-*` and matching ignored build outputs. Provenance records include tool/firmware/artifact hashes and checked configuration. ROM data, raw RAM dumps, firmware and generated binaries are excluded from source publication.

## Scope limits

The target dump verifies final state and resource journals; exact interleaved RAM/event ordering remains the separately executed host differential proof. Actual PPU/MMC1 effects are represented as data for future native adapters, not performed against NES hardware addresses on Amiga.

Bank-3 `$8003`, further queue processing, `$8000`, bank restoration and RTI remain untranslated. There is no full reset-to-title, audible output, playable gameplay, physical-hardware test or performance claim. Earlier hardware warmup before `$FE24` and asynchronous interrupt timing also remain outside scope.
