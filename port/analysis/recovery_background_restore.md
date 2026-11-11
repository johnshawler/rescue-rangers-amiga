# Restore the additive background-only candidate

Start from the approved generic source checkpoint remote
cd6d8336f8de8ca7072d068064d6d6bcc0eaf02e (matching local
df66f1235cf2d201b8e06fa899000529fc6e8fb2, tree
2b3fc8a7aa4645094d816e04f736b5aa8faf159b), then add only the files in
recovery_background_source_manifest.json. Do not replace the frozen renderer.
Follow recovery_menu_paula_restore.md for dependencies, pinned external tools and
approved private inputs. No previous capture is an input to the build. The builder
pins the frozen predecessor, whose dependency checks pin the original device,
background and sprite sources, and substitutes only the background include in a
private generated device file. The exact native dispatcher and compiled planner
remain SHA-pinned by the inherited build. A separately assembled same-layout
frozen renderer plus 32 padding bytes must match every linked payload byte outside
the candidate background routine. Outputs must use NEW directories.

    source /path/to/amiga-recovery-m68k/activate.sh
    export VASM=/path/to/vasmm68k_mot
    export PYTHONPATH=/path/to/rescue-recovery-inspection/.deps
    export PYTHONDONTWRITEBYTECODE=1
    export MPLCONFIGDIR=/tmp/rr-background-mpl
    export XDG_CACHE_HOME=/tmp/rr-background-cache
    python port/tests/recovery_background_public_test.py

That public test needs neither cartridge nor firmware. Then privately restore only
the approved input/rescue-rangers-europe.nes and A1200 firmware as described in the
predecessor recipe. Supply the pinned existing frontend/core through PAULA_HEADLESS
and PUAE_CORE. The runner clears RAM_LOAD and uses PCM_S16LE_OUT, not AUDIO_OUT.

    python port/tools/recovery_background_build.py --output "$PWD/port/build/NEW/on" --display 1
    python port/tests/recovery_menu_paula_adapter_test.py port/build/NEW/on
    python port/tests/recovery_menu_paula_target_rejection_test.py port/build/NEW/on
    bash port/tools/recovery_menu_paula_run.sh "$PWD/port/build/NEW/on"
    python port/tests/recovery_menu_paula_verify.py port/build/NEW/on

Repeat in NEW/off with --display 0. Poll the actual capture session to exit zero;
a partial capture is never a pass. The frozen verifier is unchanged, no telemetry
exceptions or semantic waivers are required. The target capture runner refuses an
existing full.log; the builder refuses an existing output directory.

The independently verified existing uninstrumented controls may be reused with
exact provenance, as in this checkpoint. Compare each candidate only with the
corresponding display setting, same default content and pinned target configuration:

    python port/tests/recovery_background_compare.py port/build/NEW/on port/build/recovery_profile_v1/control-on --output port/build/NEW/comparison-on.json
    python port/tests/recovery_background_compare.py port/build/NEW/off port/build/recovery_profile_v2/control-off --output port/build/NEW/comparison-off.json

The comparison refuses to overwrite its output and does not write the controls.
On a fresh machine without the old controls, rebuild each with the frozen
recovery_menu_paula_build.py in new directories, capture and independently verify
as above, then pass those paths to the comparison. Never label an unexecuted or
unverified rebuild as a measured control.

Keep all ROM/firmware/resources/generated assembly, linked files, disks, complete
RAM dumps, audio, screens, logs and original-derived detailed verification reports
private. Only the generic source/test/build/report files in the manifest belong
in a source-only checkpoint. No input-only Z/X work is integrated here.
