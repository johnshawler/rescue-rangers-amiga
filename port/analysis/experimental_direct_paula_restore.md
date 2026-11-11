# Reproducing the direct-Paula diagnostic

Start with a separate checkout of the public recovery branch at commit
a5d877137adc5229d151f01416ca7c66b510161c or later, and overlay the source-only
direct-Paula archive. The archive includes the unchanged audio-capture frontend
dependency that is not present on the public base. Install the documented native compiler, assembler and
Python dependencies. Restore the approved cartridge privately to
input/rescue-rangers-europe.nes. No generated music profile is supplied publicly.

The included profile generator observes the unchanged full title original-code
and native-code comparison. It preserves every original bus write and verifies
all 7,136 APU effects. It records logical NMI labels where known, not CPU-cycle
timestamps. Bootstrap labels remain unknown; the diagnostic's documented
snapshot reduction does not invent their original timing.

From the repository root, with VASM and PYTHONPATH configured:

    RR_SOURCE_ROOT="$PWD" RR_PROFILE_OUT="$PWD/title-apu-private.json" python port/tools/experimental_direct_paula_profile.py
    python port/tools/experimental_direct_paula_build.py title-apu-private.json

Keep the generated JSON private and out of version control. Its expected SHA256
is 5b2194214a7da982adeb963b9865698dde5b5208f6c80c2053caea828e242634.
The profile generation requires the original cartridge but no firmware or legacy
capture fixtures. Run the documented synthetic and target checks in
experimental_direct_paula_lab.md, with the approved firmware restored separately.
The builder creates private profile data, wave tables, executable and diagnostic
ADF under the ignored build directory. These are not a replacement playable disk.

The profile generator and these restore instructions were added after the
independent review of the unchanged native backend and corrected capture tests.
The backend's fidelity, phase/counter, logical scheduling and standalone timing
limits still apply.
