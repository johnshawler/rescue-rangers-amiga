# Source-only native menu/Paula diagnostic restore

This is an additive bounded checkpoint, not a completed game or delivered disk.
Use a separate empty directory. The source archive contains the generic dependency
closure, never cartridge/firmware/profile/event/PCM/RAM/binary data. Verify every
file's SHA256/size against recovery_menu_paula_source_manifest.json. Never overwrite
a different existing source file. Install requirements-dev.txt plus matplotlib 3.10.8
for plots, and supply the pinned VASM and m68k GCC 14 tools externally.

Privately restore only approved input/rescue-rangers-europe.nes (SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411) and
artifacts/a1200-system/kick40068.A1200 (SHA256
6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707).
No captured fixture, music profile, prior built dispatcher or RAM snapshot is needed.

    source /path/to/amiga-recovery-m68k/activate.sh
    export VASM=/path/to/vasmm68k_mot
    export PYTHONPATH=/path/to/python-dependencies
    python port/tools/recovery_menu_paula_build.py --output "$PWD/port/build/new/default-1" --history default --display 1
    python port/tests/recovery_menu_paula_adapter_test.py port/build/new/default-1
    PAULA_HEADLESS=/path/to/verified/audio-headless PUAE_CORE=/path/to/puae_libretro.so bash port/tools/recovery_menu_paula_run.sh "$PWD/port/build/new/default-1"
    python port/tests/recovery_menu_paula_verify.py port/build/new/default-1

Use new output directories, default/right_hold/move_back histories and display 0/1.
The stock target is PAL A1200OG, cycle-exact 68020/AGA, 2 MiB Chip and zero Fast.
The runner explicitly clears RAM_LOAD/RAM_LOAD_FRAME and inherited RAM_MAP_PREFIX
and PUAE_FASTMEM before setting its own output prefix. It uses actual PCM callback
capture PCM_S16LE_OUT, not AUDIO_OUT. Six thousand callbacks include floppy loading
and a long silent terminal tail; elapsed game intervals come from the target CIA-B
32-bit timer, never the total boot duration.

The already built audio frontend SHA256 is
5a6caac3c484c24a979800188070abb78c7fdbe648106fb84c5d8532e19052b1.
Its unchanged generic source port/tools/experimental_paula_headless.c is included
(SHA256 58ce7adb87e69c584cbe6cbb081d1c66632abeb7d76f9f6d312a2722ce250939).
If a fresh workstation needs that frontend built, use its original instructions;
this checkpoint did not rebuild or alter tools. Firmware and generated outputs
must stay private. The original interpreter is used only by independent host
validation, never by the target or builder.

## Synthetic adapter check without private inputs

The separate standalone wrapper needs only this generic source closure,
requirements-dev.txt and the pinned recovery GCC 14 toolchain. It does not need
VASM, cartridge, firmware, captures, profiles or a previously built target:

    source /path/to/amiga-recovery-m68k/activate.sh
    export PYTHONPATH=/path/to/python-dependencies
    bash tools/test_menu_paula_public.sh

It generates synthetic finite noise tables, compiles only the generic adapter,
entry and unchanged planner, pads its BSS and runs machine68k unit checks. The
Python audit/import hooks reject cartridge/oracle accesses within this path;
they are regression checks, not an OS sandbox. The standalone wrapper and
validate_menu_paula.sh are included unchanged in the source
closure. The final validation recipe runs both adapter and linked-target
rejection tests for every built variant.

After privately building a complete target, run its separate integration error
regressions:

    python port/tests/recovery_menu_paula_target_rejection_test.py port/build/new/default-1

These execute the actual linked target and inject malformed journal/capture state
and an existing sounding DMA state. Their synthetic clock verifies drain/control
flow, not real-core malformed-input PCM. They cover the independent-review
counterexamples, explicit loop/history/event guard errors and permanent muted stops for capture, adapter and renderer
failures. Actual valid-history output still requires the stock capture checks.
