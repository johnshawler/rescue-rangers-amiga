# Rescue Rangers native Amiga port: recovery branch

This is a **recovered early title/menu source baseline**, followed by clearly
identified new work. It is not the source of the later playable development
ADFs. Later gameplay, restart, rendering-optimization and audio source has not
been recovered and is not represented here.

Target: PAL Amiga A1200, 68020, AGA and 2 MiB Chip RAM. Stock hardware is preferred;
optional Fast RAM must remain within 8 MiB. The intended architecture is static
native game-code translation and Amiga rendering, not a general NES interpreter.

## Current verified source

- Native title player-count and Chip/Dale selection, input edges, timer/random
  primitives, sound-request queue and title nametable updates.
- Native background and sprite rendering with source-independent synthetic tests.
- The title milestone rebuilds byte-for-byte to its original development ADF.
- Its menu handoff intentionally stops before untranslated gameplay. No native
  stage or audible sound is implemented by this recovered source baseline.
- A newly written, isolated reset-RAM helper matches original instructions at
  $FE24–$FE42, including all 2,064 ordered RAM writes. It is not integrated into
  title boot; hardware warmup and later startup remain incomplete.
- A separate new mapper-publication helper continues $FE43–$FE66 with an
  explicit ordered journal: 20 logical MMC1 writes plus 14 original RAM writes.
  Its 2,048 original-ROM/native cases preserve register, stack and busy-state
  semantics. This does not yet select native resources or implement audio.
- Captured initial title state remains a private development fixture. New work
  will replace that dependency with verified original reset/resource logic.

Recovery validation passed 142,896 original-ROM differential cases, 27 synthetic
renderer cases and 16 native selftests. Five cycle-exact emulated PAL A1200 menu
scenarios were pixel-exact against preserved original references and actual
Amiga display output. These are correctness results, not gameplay-speed claims.

The separately preserved later Z/X ADF is an older, silent, incomplete playable
binary. Its recovery smoke test does not imply that its source is present here.
See [recovery provenance](docs/RECOVERY.md) and the validation summary. The new helper is documented in
[the reset boundary report](port/analysis/recovery_reset_ram.md) and
[mapper-publication report](port/analysis/recovery_reset_mapper.md).

## Build and test

Install Python dependencies from `requirements-dev.txt`. Supply vasm via the
`VASM` environment variable. `bash tools/test_public.sh` runs the two synthetic
assembled-code renderer suites, restore-safety tests and reset-helper assembly
without a game ROM or firmware.

Private original-ROM tests require the hash-checked European cartridge at
`input/rescue-rangers-europe.nes`. The full title build also needs the original
private title fixture pack under `port/assets/` and `artifacts/`; firmware is
needed only for target emulation. Use `python tools/restore_private_inputs.py`
with a preserved recovery bundle and supplied inputs to install them safely.
The helper validates every included fixture and refuses to replace mismatching
existing files. `python tools/restore_private_inputs.py --help` describes inputs.

For full validation, set `VASM`, `PUAE_CORE` and `HEADLESS`, then run
`bash validate_recovery.sh`. Pinned tool revisions and hashes are recorded in
`docs/recovery-validation.json`. Compile `scripts/headless.c` against the
libretro headers with `-ldl -Wl,--no-as-needed -lm`.

Do not commit cartridge/firmware bytes, extracted game assets, captured state,
screenshots, compiled game disks or private reference dumps. The public CI uses
synthetic data only. A fresh-clone restore is checked privately with authorized
inputs; it does not make those inputs public.

This is an incomplete development project, not an official release or a claim
of full-game compatibility, full PAL speed, or physical-hardware validation.
