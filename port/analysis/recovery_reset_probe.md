# Native A1200 reset-boundary probe

This separate source-only disk executes the four new recovery helpers on an
emulated stock PAL A1200. It does not replace the title or delivered gameplay
disks and does not contain game graphics, captured state, cartridge or firmware.

`port/tools/build_recovery_reset_probe.py` builds a distinct
`port/build/recovery-reset-probe.adf` from the existing generic boot loader and
new `recovery_reset_probe.s`. The probe begins with synthetic RAM filled with
`$A5` and context `$FE24`, A=`$17`, X=`$33`, Y=0, P=`$24`, SP=`$FD`. It passes the
same RAM/context through RAM reset, mapper publication, video clear and first
task dispatch. No state patches are inserted between calls. It stops at `$C574`
before executing that task, and leaves a report and both event journals in Chip
RAM. Ten guards surround the five buffers; the private native stack is checked
for balance. The visible green background is only a diagnostic indicator, not
a game screen or the primary test result.

`verify_recovery_reset_probe.py` reads the actual emulated Amiga Chip RAM dump.
It executes the original cartridge instructions independently from the same
synthetic starting state through `$C574`, then compares all 2,048 RAM bytes,
eight context bytes, 20 mapper records and 2,188 PPU records. It also verifies
the four completed helper calls, guarded buffer bounds and native stack.
The host reference executes 13,299 original instructions for this input.
The target dump checks final state and journal contents. Exact interleaved
RAM-write ordering is separately established by the host differential traces;
it is not inferred from the final target dump.

The corrected probe passed a 600-frame run using the pinned PUAE core, supplied
A1200 Kickstart 3.1, `PUAE_MODEL=A1200OG`, 2 MiB Chip and no Fast RAM. Its payload
is 16,166 bytes, allocated as 16,384 bytes. Probe ADF SHA-256 is
`840e6ff4a1403488f572b5e76e791ad3e97a4acb08f97045e312296d9a3b8225`.
The first diagnostic attempt used a privileged SR write at boot entry and did
not enter the helpers. That instruction was removed, matching the proven
title's custom-interrupt/DMA shutdown. Failed local evidence is retained.

Run `bash validate_recovery.sh` with the documented private inputs and tool
environment for the complete source and target regression. Public CI builds
the probe from source but does not have the cartridge or firmware needed for
this private original-ROM/target comparison.

This proves the bounded native path on the target emulator. Original hardware
warmup before `$FE24`, the `$C574` task, asynchronous interrupts, actual resource
mapping, title generation, gameplay and sound remain outside this probe. No
gameplay speed or physical-hardware validation is claimed.
