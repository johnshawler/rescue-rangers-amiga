# Independent native Z/X input validation

This additive diagnostic validates native keyboard input only. It contains no
NES ROM data, interpreter, recovered game semantics, gameplay integration, or
performance claim. The delivered game disk and frozen keyboard adapter are not
changed. No shared tools are rebuilt. The bounded menu/audio target is not changed.

## Public-source allowlist

- port/src/recovery_zx_keyboard.s
- port/src/recovery_zx_probe.s
- port/tools/recovery_zx_build.py
- port/tools/recovery_zx_run.sh
- port/tests/recovery_zx_keyboard_test.py
- port/tests/recovery_zx_poll_test.py
- port/tests/recovery_zx_verify.py
- port/docs/recovery_zx_input_validation.md

Dependencies included unchanged from the existing source checkout: `port/src/boot.s`
and `port/src/amiga_clock.s`. Neither is a changed file. Everything under
`port/build/recovery-zx`, including disk, RAM dumps, logs, firmware, and generated
verification JSON, stays private. No commit or publication was performed here.

## Contract

A0 points to a zero-initialized, aligned 12-byte caller-owned state. D0 returns
held NES bits; D1-D7 and A0-A6 are preserved. CCR is scratch. State layout:
held/raw/serial/saved-CRA bytes, acknowledgement elapsed long, event-count long.
Mapping: Z raw31 ->40, X raw32 ->80, Return44 ->10, Tab42 ->20,
Right4e ->01, Left4f ->02, Down4d ->04, Up4c ->08 (hex).
No aliases: Space and Alt are intentionally unmapped. Releases clear only the
unique mapped bit; repeated presses/releases are idempotent.

The poll function requires exclusive CIAA ICR/serial ownership after takeover,
serial input mode (CRA bit6 clear), and the existing free-running CIAB timers.
It is not OS-safe: reading ICR acknowledges all pending CIAA interrupts.
CRA is read, bit6 is temporarily set for handshake, then the saved byte is restored.
CIA readback semantics apply: force-load command bits are not persistent state.
The delay is >=64 CIAB E-clock ticks, approximately90 microseconds PAL; the
measured interval begins after asserting handshake, so write overhead increases
rather than shortens its duration. Unsigned subtraction supports timer wrap.

## Results

- 262,144 user/supervisor-mode actual machine68k 68020 executions: every256 held masks x256 rawkeys,
  repeated for all serial-byte encodings. Registers, SP, byte guards, width-aware whole-access memory-read/write
  bounds and immutable code checked; all passed.
- 512 user/supervisor-mode actual native poll executions with test-double CIA/clock: every128
  input-mode CRA values x pending/no-pending, preserving CRA exactly, handling
  clock wrap, returning mask, maintaining registers/SP and width-aware whole-access memory read/write bounds, with exact byte CIA and
  long clock accesses.
  This is a synthetic bus contract check, not hardware timing proof.
- Stock PUAE cold boot with actual libretro keyboard callbacks, not RAM injection:
  20 CIA serial events passed. Z down at tick10 ->40; X down20 ->c0;
  Z up30 ->80; X up40 ->00. Return/Tab/arrows and releases matched. Space and
  left Alt each produced serial events but no held-mask change.
- Actual CIAB acknowledgements67–78 ticks; saved CRA08 throughout. No record
  overflow; final logical tick922; target code unchanged. Live capture observes
  saved CRA, while synthetic bus tests verify the exact restoration write.
- PAL A1200OG, 68020/AGA, 2MiB Chip/0Fast, CPU/memory cycle exact, stock core.
- Initial failed capture is retained as failed-entry.log/bin: privileged SR write
  in user-mode boot entry prevented initialization. It is not counted as a pass.
  Final entry has no privileged SR access and follows custom/CIA takeover.

## Reproduction / restoration

Restore this allowlist onto the reviewed source checkout, retaining unchanged
boot.s/amiga_clock.s. Obtain local pinned tools and legally owned firmware at the
paths below; no NES ROM or private game fixture is needed. Builder requires a NEW --output directory and refuses existing paths. Capture
also refuses existing run.log/chip.bin. Build JSON records source, boot, payload
and disk hashes. Generated files are
recreated, not restored into the delivered disk. Do not run concurrently against
another worker's output directory. Set these variables to your externally provided pinned toolchain binaries and
Python dependency directory. The checkout does not distribute those binaries:

    export VASM=/path/to/vasmm68k_mot
    export PYTHONPATH=/path/to/python-dependencies
    export PYTHONDONTWRITEBYTECODE=1
    export PUAE_CORE=/path/to/pinned/puae_libretro.so
    python port/tests/recovery_zx_keyboard_test.py
    python port/tests/recovery_zx_poll_test.py
    python port/tools/recovery_zx_build.py --output port/build/recovery-zx-NEW
    bash port/tools/recovery_zx_run.sh port/build/recovery-zx-NEW

The run script checks core, unchanged frontend, and firmware SHA256 before boot.
The frontend is the pre-existing `port/build/experimental-direct-paula/headless`.
Firmware source is `artifacts/a1200-system/kick40068.A1200`.
No captured emulator state or modified core is required. The pinned existing
frontend/core binaries and assembler are required.
The actual successful command used the same args/environment as the run script;
the added script was syntax checked, not used for a redundant capture. A fresh
--output build was compared byte-for-byte to the successful payload/disk.
The legacy successful evidence remains at port/build/recovery-zx; the fresh
provenance-only rebuild is port/build/recovery-zx-rebuild-review. The two failed
entry files remain distinct and unchanged in the legacy evidence directory.

Final diagnostic ADF SHA256:
c94ac0f963ec9c56b84be1a79076145bc4af2cde046d615984939a34c2ea089b

Delivered disk rechecked unchanged:
6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17

Preserve successful and failed captures, build provenance, and source manifests
for review. If abandoning the experiment, leave its private evidence intact and
record that decision separately. Do not remove or overwrite preserved evidence
or unrelated work.
A future menu integration requires separate review of input sampling, telemetry
bounds and rendering; this diagnostic deliberately makes no such integration.
