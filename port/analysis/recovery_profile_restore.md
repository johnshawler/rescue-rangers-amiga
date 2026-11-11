# Additive native menu cost profiling restore

Use the approved generic source checkpoint 069cdc71e453e637dccf531530b498ffe635a652
(tree b23a90fe2fe6359e7ce0cc5f8f7394a80ad4bf2a), plus the seven new source/report
files listed in recovery_profile_source_manifest.json. This is not a replacement
for any frozen implementation or delivered disk. No commit/publication is performed
by these tools. Keep all output directories private and new.

Follow recovery_menu_paula_restore.md for the pinned toolchain, approved private
ROM/firmware hashes, frontend/core hashes and source prerequisites. No prior capture
is an input. Set VASM, PYTHONPATH, PAULA_HEADLESS and PUAE_CORE as described there,
source the recovery GCC14 activate.sh, and set PYTHONDONTWRITEBYTECODE=1.

Public check without cartridge/firmware:

    python port/tests/recovery_profile_public_test.py

Private target build, capture and checks (absolute NEW output directory):

    python port/tools/recovery_profile_build.py --output "$PWD/port/build/NEW/on" --display 1
    python port/tests/recovery_profile_probe_test.py port/build/NEW/on
    python port/tests/recovery_menu_paula_adapter_test.py port/build/NEW/on
    python port/tests/recovery_menu_paula_target_rejection_test.py port/build/NEW/on
    bash port/tools/recovery_menu_paula_run.sh "$PWD/port/build/NEW/on"
    python port/tests/recovery_profile_verify.py port/build/NEW/on

Repeat in a different directory with --display 0 for the matched diagnostic control.
For the original uninstrumented control, build with --enabled 0, then use the frozen
recovery_menu_paula_verify.py rather than recovery_profile_verify.py. The disabled
path invokes the exact pinned predecessor builder without transformations. Never
run two captures into the same directory. The inherited runner explicitly clears
RAM_LOAD and related state, uses actual PCM_S16LE_OUT and 6000 callbacks. A partial
or timed-out run is not a pass. Poll the actual returned shell session to completion.

The builder SHA-pins its predecessor and applies checked unique source substitutions
in memory. Generated derivative C/device/assembly files live only in the private
output directory. The native dispatcher and 470-byte planner are checked against
their frozen byte hashes. Original source files are not edited. The device/renderer
call sites are instrumented while the actual renderer routines remain unchanged.

The profile verifier preserves every original semantic, plan, pixel, PCM and failure
assertion. One explicit difference is necessary for mutable telemetry: GCC places
the new 56-byte profile structure before mp. The verifier checks its 8-byte magic,
excludes exactly its 48 live counter bytes, and still checks every other byte in
that formerly immutable prefix. It does not waive target code checks. The original
verifier run on this target stops at that expected immutable-region assertion.

Synthetic clock tests prove accounting/register/control-flow properties only.
The public test now executes all 14 start/end probes in user mode, including CCR
and stack checks. An earlier supervisor-only check missed a privileged SR-read
in the first candidate. Its failed/resetting v1 capture is preserved privately and
is not timing or playback evidence. The corrected v2 reads CCR without privilege.

No optimized target is supplied. Profiled timings include substantial observation
cost and changed display phase. Use raw segment counts/totals/maxima plus the matched
uninstrumented whole-run control; do not subtract a mean empty probe and label that
an exact original execution time. Logical interrupts are not game FPS.
