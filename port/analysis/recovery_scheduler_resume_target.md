# Opt-in stock-A1200 scheduler-resume probe

The tenth native helper now has separate target-emulator coverage through the
first scheduler resumption. It polls explicitly supplied standard-controller
snapshots `(0,0)` (no pressed buttons) and stops **before `$C584` executes**.
This is new recovery code, not recovered later playable-source development.

## Build and run

With VASM configured:

```
python port/tools/build_recovery_reset_probe.py --scheduler-resume
```

This exclusive option enables all prior stages plus `SCHEDULER_RESUME`, uses
marker `CDRRRES1` and output prefix `recovery-scheduler-resume-probe`, and adds an
independently guarded 74-byte controller journal. The report stores its pointer
at offset 64. After the ninth helper, only native input arguments D0/D1 are set
to zero. Original RAM/context pass directly between all ten helpers, unpatched.

Payload: **19,040 bytes**, rounded allocation **19,456 bytes**. ADF SHA256:

`bc3b564980423790d874a5c5c686eb2aa365b6f0c97f3b7e2706f8eb23e660ae`.

The actual run used the pinned `headless-recovered-title` frontend and
`libretro-uae/puae_libretro.so`, supplied A1200 firmware, `PUAE_MODEL=A1200OG`
and **600 frames**. Frontend/core/firmware hashes match the ninth-stage
provenance. The target log confirms 68020, PAL, 2 MiB Chip RAM
(`chipmem_size=4`), zero Fast RAM and CPU/memory/blitter cycle-exact settings,
with `PASS runs=600 video_callbacks=600`.

```
python port/tests/verify_recovery_reset_probe.py --scheduler-resume port/build/recovery-scheduler-resume-probe-chip.bin
```

## Executed target comparison

The verifier executes the hash-checked original cartridge from synthetic reset,
including actual bank mapping and a real logical py65 `nmi()` at the existing
chosen first-yield boundary. It runs **13,943 original instructions**, including
271 bank-3 audio-command/tick instructions, then stops before the resumed task.

Passed:

- Ten completed helpers, all 2048 original RAM bytes and eight context bytes.
- Eighteen controller records: two strobe writes and sixteen interleaved serial
  reads. The decoder supplies zero for both pads and no expansion input.
- Thirty mapper, 2199 PPU and seven APU records, plus all 256 OAM DMA source bytes.
- Twenty-two intact buffer guard regions and balanced native stack.
- Original task selection, ready-to-running state, scratch/controller bytes,
  original JSR stack stores and consumed continuation bytes.

At the post-RTI boundary, the verifier retains the untouched raw oracle context
and separately asserts the complete seven-byte interrupt frame, raw P=`$B4`,
hardware-saved P=`$A4`, handler-saved P=`$B4`, and restored bank 6. It then executes
the scheduler directly, without rewriting status or any RAM. The scheduler's
real JSR overwrites `$01BA/$01BB` with `$CF/$FE`; all original stack contents
are compared at the final boundary.

Final native P is `$A4`, raw py65 P is `$B4`. The existing named
`architectural_status_view` clears virtual B/sets U only in the comparison
value. N/V/D/I/Z/C are compared exactly. No oracle P or RAM patches are used.

## Regressions and negative verification

All five earlier payload binaries **and ADFs** rebuild byte-identically:

- Reset: `840e6ff4a1403488f572b5e76e791ad3e97a4acb08f97045e312296d9a3b8225`.
- First yield: `e991d2a5c636a3001d61767ab60daaf307e96d00d290ae4b39d54c50da9d01d3`.
- NMI audio entry: `4d2ab14b1bb174838e7a7a48115bace0d78e4cf281f8edbf1a771048823ee86d`.
- Audio reset: `70923298254675c33111d6e05e13147cd926d61e9564416d7847a951ef5b5560`.
- NMI return: `267303fd0d998937d45052c26063904b96f82c5c44f43b197febd19503a831ba`.

All five prior target dumps pass their matching verifier modes. **169 corruption
checks and ten cross-mode rejections passed**. Negative checks
cover each controller-journal byte, every context byte, marker, helper count,
status, native stack pointer, original controller/task/interrupt/continuation
RAM, both guards of every buffer, earlier journal records, all seven APU values
and DMA. Cross-mode checks reject the new dump in every earlier mode and each
earlier dump in the new mode.

Private evidence uses `logs/recovery-scheduler-resume-probe-*`,
`logs/recovery-scheduler-resume-regression-*` and ignored build artifacts.
The provenance records exact frontend/core/firmware/ADF/dump/log hashes and
checked settings. No firmware, cartridge, raw dumps or generated disks are
included in the public source deliverable.

## Limits

The target checks final buffers and journal contents; full ordered RAM/controller
interleaving is independently covered by the 66,560-case host differential
suite and 256 continuous compositions. This is a logical, bounded recovery
slice, not a platform keyboard adapter, hardware-timed input/NMI cadence, full
boot, gameplay, Paula playback, speed claim or physical-Amiga validation.
The next task instruction at `$C584` remains untranslated and unexecuted here.
