# Opt-in stock-A1200 palette NMI probe

The new `--palette-nmi` mode runs twelve static helpers from the established
synthetic `$FE24` context through the second explicit logical NMI, stopping
before `$C0BF` bank/audio dispatch. It publishes the pending palette through an
explicit journal and preserves queued sound `$07` and nested continuation
`$C2A8`. This is newly authored recovery translation, not recovered lost source.

## Build and target verification

```
python port/tools/build_recovery_reset_probe.py --palette-nmi
python port/tests/verify_recovery_reset_probe.py --palette-nmi port/build/recovery-palette-nmi-probe-chip.bin
python port/tests/recovery_test_palette_nmi_target.py
```

The option is mutually exclusive with the seven earlier modes. It enables all
prior stages plus `PALETTE_NMI`, uses unique marker `CDRRPAL1`, and writes only
`recovery-palette-nmi-probe` outputs. A new guarded 454-byte buffer contains
49 PPU records and the second 256-byte OAM source snapshot. The target snapshots
D1–D7/A0–A6 around helper twelve and rejects any register change; the verifier
also checks balanced native stack and both guards of every buffer.

Payload: **20,546 bytes**, rounded allocation **20,992 bytes**. ADF SHA256:
`a0027f8fb69546e64d67a3d9172a90e0389efd26164db14051000eb2dade6cdc`.

The actual ADF passed **600 frames** with pinned `headless-recovered-title`,
`libretro-uae/puae_libretro.so`, and unchanged supplied firmware. The log confirms
`A1200OG`, PAL, 68020, 2 MiB Chip RAM, no Fast RAM, CPU/memory/blitter cycle-exact
settings, and `PASS runs=600 video_callbacks=600`. Exact tool, firmware, ADF,
dump and log hashes are retained in private provenance under
`logs/recovery-palette-nmi-probe-provenance.json`.

## Continuous original-ROM comparison

The verifier executes **14,642 actual original instructions**, including 271
bank-3 command/tick instructions from the first NMI, using the hash-checked
private cartridge. It injects real `nmi()` twice: at the first yield and at the
later nested palette yield. RAM/context flow directly between native helpers;
the original reference is never patched. Initial D=0 remains appropriate for
the preceding setup helper's guarded arithmetic scope.

Passed checks:

- Twelve completed helpers, all 2048 original RAM bytes and eight context bytes.
- Thirty mapper records, 2,248 PPU records (49 from this prefix), seven APU
  records, eighteen controller records and both DMA snapshots (512 bytes).
- Twenty-four guard regions, native stack balance, and helper-twelve register
  preservation on the emulated target.
- Original stack before the second NMI, exact seven-byte hardware/handler
  frame afterward, preserved `$C2A8` continuation, SP `$B1`, bank 6, ready
  task-zero state, consumed palette flag `$18=0`, and queued sound `$07` intact.

At the first RTI the untouched raw py65 P is `$B4`. The second actual NMI
clears virtual B itself, and final raw/native P is `$26`. The named
`architectural_status_view` only clears virtual B/sets U for comparison;
it does not modify the oracle. Palette bytes and all prior journals are
checked against actual ROM effects, not synthesized expected output.

## Regression and negative coverage

All seven earlier payload binaries and ADFs rebuild byte-identically to their
frozen checkpoint. Their existing seven target dumps pass matching verifier
modes. **958 corruption checks and 14 cross-mode rejections passed.** The
corruption test changes marker/status/helper count, stack pointer,
context, controller journal, palette request/source/destination, task and queue
RAM, nested/interrupt stack, all bytes of the new journal and second DMA,
all bytes of the first DMA, prior journal/APU samples, and every buffer guard.
Both directions of each old/new mode mismatch must fail. Exact executed counts
are recorded in the private negative-test report.

Only the probe, builder and verifier receive opt-in changes. Prior helpers,
prior host tests, aggregate/public scripts, README and delivered Z/X ADF are
unchanged by this work. No commits or publication were made.

## Limits

Target comparison verifies final state, journals and guards. Exact ordered
RAM/hardware interleaving is separately proved by the host differential test.
Logical NMI events are deliberately selected boundaries, not cycle-accurate
NES interrupt timing. No bank/audio dispatch after the second NMI is claimed;
queued sound `$07` remains pending. No full boot, gameplay, audible Paula,
physical-Amiga validation or full-speed claim. No ROM/firmware extracts, asset
dumps or built disks are included in public source.
