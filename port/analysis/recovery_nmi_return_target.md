# Opt-in stock-A1200 probe through the first NMI return

The ninth helper now has separate target-emulator coverage for the first startup silent tick, bank restoration and RTI. The native stop is before the resumed `$FE8D` scheduler instruction. This does not translate scheduler continuation or imply audio playback.

## Build and run

With the pinned `VASM` executable configured:

```
python port/tools/build_recovery_reset_probe.py --nmi-return
```

The exclusive option enables all nine helpers using `FIRST_YIELD`, `AUDIO_ENTRY`, `AUDIO_RESET` and `NMI_RETURN`. It uses its own `CDRRRTI1` marker, `recovery-nmi-return-probe` file prefix, and guarded 22-byte restore-bank journal. RAM/context pass directly between helpers without patches.

Payload: **18,512 bytes**, rounded allocation **18,944 bytes**. ADF SHA256:

`267303fd0d998937d45052c26063904b96f82c5c44f43b197febd19503a831ba`.

The actual run used the previously pinned `headless-recovered-title` frontend and `libretro-uae/puae_libretro.so`, supplied A1200 firmware, `PUAE_MODEL=A1200OG`, and 600 frames. The frontend/core/firmware hashes were checked against the eighth-helper provenance. The log confirms 68020, PAL, 2 MiB Chip RAM (`chipmem_size=4`), zero Fast RAM, CPU/memory/blitter cycle-exact settings, and `PASS runs=600 video_callbacks=600`.

Verification:

```
python port/tests/verify_recovery_reset_probe.py --nmi-return port/build/recovery-nmi-return-probe-chip.bin
```

## Executed results

The target verifier independently executes the supplied hash-checked cartridge, including actual bank-3/fixed-bank code and PRG-publication mapping. It injects real py65 `nmi()` at the first task yield, executes 13,747 original instructions including 271 bank-3 instructions across the command and tick, and stops at the returned `$FE8D` before executing it.

Passed comparisons:

- Nine completed native helpers, all 2048 RAM bytes and eight context bytes.
- Thirty cumulative mapper records, including the five new restore records `06 03 01 00 00`, restoring actual oracle bank 6.
- All 2199 PPU records and 256 OAM DMA source bytes.
- All seven prior command APU records. The first silent tick adds no APU writes.
- Twenty intact guard regions and balanced native stack.
- Original scratch, channel pointer and stack effects, including the retained consumed interrupt frame.

### Status is explicitly compared as an architectural view

The actual native context has **P=`$A4`**. py65 RTI exposes **raw P=`$B4`** because it restores a virtual B marker. The verifier separately asserts raw oracle P=`$B4`, hardware-saved stack P=`$A4`, handler-saved P=`$B4`, and all seven saved frame bytes. It retains the raw context and applies the named `architectural_status_view` only to the expected comparison value. This clears virtual B and sets U; N/V/D/I/Z/C compare exactly. The verifier does not assign to oracle P or RAM to force agreement. Full RAM comparison includes the original saved bytes unchanged.

The separate host suite also proves a follow-on real NMI from untouched raw oracle state, compares it with native canonical output, and verifies that the unchanged native NMI-prefix contract rejects raw virtual-B input. The target probe itself stops after the first RTI.

## Regressions and rejection checks

All four previous probe payloads **and** ADFs rebuilt byte-identically. Earlier target dumps still pass their original verifier modes. Preserved ADF hashes:

- Reset: `840e6ff4a1403488f572b5e76e791ad3e97a4acb08f97045e312296d9a3b8225`.
- First yield: `e991d2a5c636a3001d61767ab60daaf307e96d00d290ae4b39d54c50da9d01d3`.
- NMI audio entry: `4d2ab14b1bb174838e7a7a48115bace0d78e4cf281f8edbf1a771048823ee86d`.
- Audio reset command: `70923298254675c33111d6e05e13147cd926d61e9564416d7847a951ef5b5560`.

**42 negative verifier checks passed**: corruption of marker/count, context PC/P, `$C0`, saved hardware/handler status and return PC, restore count/address/busy/data and both guards, cumulative mapper/PPU/yield/NMI/entry/APU records, all seven APU values, DMA and native stack guard. These include rejecting the new dump in each of the four old modes and rejecting all four old dumps in the new mode.

Private evidence uses `logs/recovery-nmi-return-probe-*` and `logs/recovery-nmi-return-regression-*`, plus ignored build outputs. Provenance records exact frontend/core/firmware/artifact/dump/log hashes and checked settings. No private ROM, firmware, raw dump or generated disk is included in the source deliverable.

## Limits

This target probe verifies final RAM/context and all journal contents. Exact interleaved write ordering is independently established by host original-ROM differential execution. It is a bounded logical NMI, not hardware-timed interrupt cadence, scheduler execution, complete reset/title boot, audible Paula playback, the full audio engine, gameplay, full PAL speed or physical-Amiga validation. Existing helper source, title and delivered game ADFs remain unchanged.
