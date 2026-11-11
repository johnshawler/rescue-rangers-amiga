# Opt-in stock-A1200 resumed task setup probe

This newly authored eleventh helper has a separate opt-in target test. It starts
from the established synthetic `$FE24` context, runs the prior ten helpers and
then the resumed task setup, stopping at the nested palette-delay `$FE8D` yield.
No delivered title/game disk is changed.

## Build and actual target run

```
python port/tools/build_recovery_reset_probe.py --resumed-task-setup
python port/tests/verify_recovery_reset_probe.py --resumed-task-setup port/build/recovery-resumed-task-setup-probe-chip.bin
```

The exclusive option enables `RESUMED_TASK_SETUP` and all prior stages. It uses
unique marker `CDRRSET1` and output prefix `recovery-resumed-task-setup-probe`.
It adds no journal: this slice operates entirely on original RAM. All prior
journals, DMA snapshot and their guard regions remain independently checked.
RAM/context flow directly between helpers without patches. The new mode also
snapshots and compares D1–D7/A0–A6 around helper eleven on the target; failure
cannot report successful completion. Final native stack balance is checked.

Payload **19,484 bytes**, rounded allocation **19,968 bytes**. ADF SHA256:
`052dbe2f97730d822931cbd988793be985aa7f0804bd51d3292284a70312b048`.

The final payload was actually run for **600 frames** with the pinned
`headless-recovered-title` frontend, `libretro-uae/puae_libretro.so` and unchanged
supplied A1200 firmware. SHA256 values match the preceding target provenance:

- Frontend: `eaab1fcd8e1fd86d24a16db76a6318ffe537ffe1811000716e45a365b0885848`.
- Core: `84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456`.
- Firmware: `6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707`.

`PUAE_MODEL=A1200OG`; log confirms 68020, PAL, 2 MiB Chip RAM, no Fast RAM,
and CPU/memory/blitter cycle-exact settings, with
`PASS runs=600 video_callbacks=600`.

## Continuous original-ROM comparison

The verifier executes **14,384 actual original instructions**, using the same
hash-checked private cartridge, actual bank mapping and one logical py65 `nmi()`.
There are 271 bank-3 audio-command/tick instructions. It passes:

- Eleven completed helpers, all 2048 original RAM bytes and eight context bytes.
- Thirty mapper records, 2199 PPU records, seven APU records, eighteen controller
  records for no pressed buttons, and all 256 OAM DMA source bytes.
- Twenty-two guard regions, balanced native stack and the new helper's target
  register-preservation check.
- Exact nested stack, pending palette flag `$18=$FF`, sound request `$D9=7`,
  waiting task state, delay and `$C2A8` continuation.

At real RTI the verifier records the untouched raw context and original seven-byte
interrupt frame, with P=`$B4` and restored bank 6. It checks the legitimate scheduler
stack overwrites at `$C584` before letting task setup overwrite those locations.
It never changes raw oracle P or inserts state patches. Final raw py65 P=`$B4`
compares with native `$A4` using the named architectural view, clearing only virtual
B/setting U. All actual arithmetic flags are exact.

The synthetic initial status already has D=0. The helper explicitly rejects D=1
because generic py65's decimal SBC differs from the NES's binary arithmetic even
when D is set. This narrows the verified scope, not a requirement imposed by the
original game. No subsequent flag normalization or state patch is used.

## Regressions and negative checks

All six earlier payload binaries and ADFs rebuild byte-identically to the frozen
checkpoint, including scheduler-resume ADF
`bc3b564980423790d874a5c5c686eb2aa365b6f0c97f3b7e2706f8eb23e660ae`.
All six existing target dumps pass their matching verifier modes. **500 corruption checks and twelve cross-mode rejections passed**. Checks cover new marker, status/count,
stack pointer, full context/controller journal, palette source/destination bytes,
queue/task/continuation RAM, earlier journals/APU data, all DMA bytes and both
guards of every buffer. Both directions of every old/new mode mismatch are tested.

Private evidence is under `logs/recovery-resumed-task-setup-*` and ignored build
artifacts. Exact ADF/dump/log and tool/firmware hashes are in the private provenance
record. No firmware, ROM extracts, dumps or generated disks are public deliverables.

## Limits

Target checks final RAM, journals and buffers; exact ordered RAM/effect interleaving
is separately proved by the host differential suite. Pending palette/audio work
is left intact and unconsumed at `$FE8D`, SP `$B8`, continuation `$C2A8`.
A future NMI/resume needs new translation, not reuse of first-NMI guards. This is
not full boot, gameplay, Paula playback, cycle-accurate NES interrupt scheduling,
physical-Amiga validation or a full-speed claim.
