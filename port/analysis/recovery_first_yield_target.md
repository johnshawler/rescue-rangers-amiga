# Opt-in first-yield stock-A1200 probe

The fifth recovery helper now has separate target-emulator coverage. This does not replace the default four-helper probe or stable title and is not a full boot or playable-game claim.

## Reproduction and isolation

`python port/tools/build_recovery_reset_probe.py --first-yield` enables the compile-time `FIRST_YIELD` variant. Output files use the distinct `recovery-first-yield-probe` prefix. Without this flag, the generated four-helper ADF remains byte-identical:

`840e6ff4a1403488f572b5e76e791ad3e97a4acb08f97045e312296d9a3b8225`.

The opt-in ADF SHA256 is:

`e991d2a5c636a3001d61767ab60daaf307e96d00d290ae4b39d54c50da9d01d3`.

Its source-only payload is 16460 bytes, allocated as 16896 bytes. It begins with the same synthetic RAM/context and passes them through all five helpers with no state patches. The added first-yield PPU journal is a separate six-byte buffer with independent guards; report marker is `CDRRYLD1`. The original marker and default report layout are unchanged.

Use the same pinned `headless-recovered-title` frontend, `libretro-uae/puae_libretro.so`, supplied A1200 firmware directory and invocation as the default probe, substituting `recovery-first-yield-probe.adf` and distinct capture filenames. Run `PUAE_MODEL=A1200OG` for 600 frames with `RAM_OUT` pointing at the new Chip RAM dump. Then:

```
python port/tests/verify_recovery_reset_probe.py --first-yield port/build/recovery-first-yield-probe-chip.bin
```

The aggregate `validate_recovery.sh` now checks both independent probe variants. No stable title or previously delivered disk was overwritten. The archived title retains SHA256 `03b774d76a6b547ff6b4b3ffd71428d381247f4802a40bab1a56eb3d1ea2b475`.

## Executed result

The 600-frame target run passed with logged 68020, PAL, 2 MiB Chip, zero Fast RAM, and CPU/memory/blitter cycle-exact settings. The target verifier independently executed 13342 original instructions and compared:

- Five completed helper calls and final boundary at the first task yield, `$FE8D`.
- All 2048 RAM bytes and eight context bytes, including original scheduler stack continuation.
- Twenty mapper records, 2188 video-clear PPU records and the separately guarded one-record first-yield PPU publication.
- Twelve intact buffer/stack guard regions and balanced native stack.

The reference must visit `$C574` before accepting `$FE8D`; the earlier scheduler visit to `$FE8D` during reset dispatch is not mistaken for completion. The independent original reference contains no state patches.

All five host differential suites were rerun and passed. The updated verifier also passed the existing four-helper target dump. Eleven negative-verifier checks passed: mutations of marker, status, helper count, context, saved task stack, new journal count/data/kind, both new journal guards, and use of the wrong default verifier mode were all rejected.

Private local evidence is saved under the `recovery-first-yield-probe` log/build prefixes, including target log, full Chip RAM dump, verifier result, negative-test report and provenance SHA256 values for frontend/core/firmware/artifacts. Raw memory dumps and binaries are excluded from the source deliverable.

## Limits

The target dump proves final RAM/context and journal contents; exact interleaved write ordering is established separately by the host differential traces. The PPU control publication is explicit data, not actual NES MMIO on Amiga. There is no asynchronous NMI execution, audio playback, continued scheduler operation, full reset-to-title generation, gameplay or hardware-performance claim. Original reset hardware warmup before `$FE24` remains untranslated. This run validates an emulated stock configuration, not physical Amiga hardware.
