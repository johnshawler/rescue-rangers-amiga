# Genuine grounded jump investigation

No native runtime source changed. This additive diagnostic proves why the earlier early-A routes matched Right, then verifies an accepted jump and landing using the frozen222722-byte composition.

## Why the early press did not jump

The original reset progression has active player0 (RAM04D0=80), inactive player1 (04D1=00), and global control-inhibit counter6D=0. On frame0, the original state0 handler calls its vertical/collision routine and changes action54 to1. The player remains in this initial airborne/falling state through frame19; vertical position RAM0510/0520 progresses from0574 to the floor05B4.

The early A press is genuinely delivered: controller poll5 produces RAM14=80 on frame6, with held RAM16=81. But action1 does not enter the state0 C96B jump-edge gate. State0 resumes after landing on frame20, when the early edge is gone. Holding A from the first poll similarly creates its only rising edge before landing. An independent original-only control comparison proves the entire first90-frame X/Y/action trajectory for the early-edge route equals Right-only, not just the terminal state.

The actual entry conditions were observed, not manufactured: C879 sees6D=0; C8D8 sees player0 active; C8EE dispatches by action54; C940 rechecks that action remains0 after vertical processing; C96B reads edge RAM14 bit80. Further original checks use RAM0420 and0348 and any carried-object state. These addresses are reported as observed fields rather than assumed grounded flags.

## Accepted jump and native comparison

A is released through polls0–23. Original controller input becomes Right+A81 for polls24–29, then returns to Right01. On frame25/NMI419, player0 is active and action0, edge RAM14=80, held16=81, field0420=3 differs from0348=5, and collision-result10=3. Original execution reaches C9A9, writes jump velocity0687 to0550/0560, sets action54=1 and executes the normal vertical routine. No RAM, stack, mapper, audio queue or scheduler state is injected.

The separate full native/original history passes90 completed frames from reset:21073 helper calls,484 logical NMIs,3602 ordered APU writes and7026 inert mutation guards. The90-frame goal is true; there is no unsupported boundary. Every helper still compares full context/RAM/runtime, ordered RAM/resource/device effects and journals. The private diagnostic additionally compares all91 frame-boundary player-state samples against a separate original-only run.

The observed vertical trajectory is05B4 (1460) before acceptance,05AE on frame26, minimum0592 (1426) on frames31–32, then05B4/action0 again on frame45. That is an upward displacement of34 game-coordinate units followed by a landing. The Right-only control stays at05B4 throughout frames25–45. Both original and native also match the recorded horizontal position and velocity fields. This establishes an actual jump in game-state physics, not merely delivery of an input bit. It does not establish rendered target motion or real-time performance.

No additional translation was necessary: the accepted jump path was already in the frozen action/physics regions. No extension beyond240 frames was needed; the new action comparison is explicitly limited to90 frames, including landing and subsequent progression.

## Evidence and reproducibility

Private original traces are port/build/recovery_bank_loader_jump_proofs_92Gjvl/{early,grounded,right_control}/result.json. comparison.json contains the concise asserted result. The native comparison is port/build/recovery_bank_loader_jump_native_oKd60J, including run.log, trajectory.json, exact controller history, per-RTI audio states and terminal snapshots. The earlier exploratory trace directory is preserved; its first draft counted C848 rather than the frozen C77B frame boundary. That diagnostic counter was corrected before all three final original traces were rerun into fresh directories and compared against the native history. No frozen runtime or earlier test was changed.

With approved private ROM and PYTHONPATH, create a new root directory and run:

- python port/tests/recovery_bank_loader_jump_probe.py NEW_ROOT/early 5 90
- python port/tests/recovery_bank_loader_jump_probe.py NEW_ROOT/grounded 24 90
- python port/tests/recovery_bank_loader_jump_probe.py NEW_ROOT/right_control 9999 90
- Create a separate empty NATIVE_ROOT, set RECOVERY_PRIVATE_SNAPSHOT_DIR=NATIVE_ROOT and run python port/tests/recovery_bank_loader_jump_rom.py default.
- python port/tests/recovery_bank_loader_jump_compare.py NEW_ROOT NATIVE_ROOT

The original probe creates its destination and refuses an existing one. Native output writes use exclusive creation. Only controller input is varied; all runs begin at the established FE24 reset entry and execute original reset/menu/loader progression.

For the source-only restore, set approved VASM and machine68k PYTHONPATH, then run bash port/tools/recovery_bank_loader_jump_public.sh. It hash-restores this small diagnostic layer and all409 frozen predecessor files, checks diagnostic syntax without executing private imports, rebuilds the unchanged222722-byte native composition (SHA2565b2bcd0b303084522b208b0f03ca45c2e16dabddbc46cd37263a62d4064e1850), and reruns the3584+512 public status/negative cases with cartridge/oracle imports denied. The jump itself requires the private original-first replay; a ROM-free syntax check is not presented as jump proof.

There were no target/emulator, renderer, audio-backend, delivered-disk, asset, publication or old-checkpoint changes. No new status adaptation was introduced. Independent review of this diagnostic result remains appropriate before expanding claims.
