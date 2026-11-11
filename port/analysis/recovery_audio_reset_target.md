# Opt-in stock-A1200 probe through startup audio-command return

The eighth helper has separate target-emulator coverage through `$C0F3`. Its seven original APU writes are explicit data in a new guarded journal, not Paula playback. Existing reset, first-yield and NMI-audio-entry probe binaries remain byte-identical.

## Build and target invocation

```
python port/tools/build_recovery_reset_probe.py --audio-reset
```

This exclusive mode enables the prior chain plus `AUDIO_RESET`, uses marker `CDRRAPU1`, and writes only the distinct `recovery-audio-reset-probe` output prefix. The independently guarded APU journal is 30 bytes. No inter-helper RAM/context patches are used.

New payload is 18036 bytes, allocated as 18432 bytes. New ADF SHA256:

`70923298254675c33111d6e05e13147cd926d61e9564416d7847a951ef5b5560`.

The same pinned `headless-recovered-title` frontend, `libretro-uae/puae_libretro.so`, supplied firmware and `PUAE_MODEL=A1200OG` configuration were used for 600 frames with a distinct Chip RAM dump. Verification command:

```
python port/tests/verify_recovery_reset_probe.py --audio-reset port/build/recovery-audio-reset-probe-chip.bin
```

Actual log confirms 68020, PAL, 2 MiB Chip, zero Fast RAM and CPU/memory/blitter cycle-exact settings. This is emulated stock configuration, not physical hardware.

## Executed results

All eight host original-ROM suites passed. The target verifier independently executed 13603 original instructions, including **150 bank-3 command instructions**, with actual bank-3/fixed-bank ROM and PRG-publication mapping. It injected the original logical hardware NMI at the selected first-yield boundary and stopped before executing `$C0F3`.

Target matches:

- Eight completed native helpers; all 2048 RAM bytes and eight context bytes.
- Twenty-five mapper records, 2199 PPU events, and 256 DMA-source bytes.
- All seven APU journal records, including original register addresses, full values and write markers.
- Eighteen intact buffer/stack guards and balanced native stack.
- Actual command dispatcher scratch/stack effects, channel pointer clears and original command return frame.

Twenty-one negative-verifier checks rejected changes to marker, helper count, context, channel state, dispatcher scratch/stack, APU count/address/kind, each of seven APU data bytes, both new journal guards, and use of all three earlier verifier modes.

All three earlier target dumps still verify in their original modes. Rebuilt earlier ADF hashes remain:

- Default: `840e6ff4a1403488f572b5e76e791ad3e97a4acb08f97045e312296d9a3b8225`.
- First yield: `e991d2a5c636a3001d61767ab60daaf307e96d00d290ae4b39d54c50da9d01d3`.
- NMI audio entry: `4d2ab14b1bb174838e7a7a48115bace0d78e4cf281f8edbf1a771048823ee86d`.

Stable title remains `03b774d76a6b547ff6b4b3ffd71428d381247f4802a40bab1a56eb3d1ea2b475`. No earlier helper source or delivered disk is replaced by this task.

Private evidence uses `logs/recovery-audio-reset-probe-*` and matching ignored build files. Provenance includes frontend/core/firmware/artifact hashes and checked configuration. Binaries, firmware, original cartridge data and raw Chip RAM dumps remain excluded from source publication.

## Limits and next boundary

The target proves final RAM/context and journal contents; exact interleaved write ordering is established by the independent host differential traces. This does not implement sound synthesis, Paula output, the full audio engine, subsequent bank-3 update, bank restoration, RTI, scheduler resume, gameplay or hardware speed.

The next silent-tick/RTI path was researched separately, without native implementation, in `recovery_silent_tick_rti_plan.md`. That plan explicitly identifies py65's virtual B/U status representation after RTI and its incompatibility with the existing canonical-P NMI-prefix guard. No unexplained context patch or prior-helper change has been made.
