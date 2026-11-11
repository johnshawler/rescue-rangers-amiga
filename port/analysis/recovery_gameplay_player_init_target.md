# Standalone player-initialization target proof

New recovery source, not rediscovered playable code. The existing 340-byte helper is unchanged. This proof enters `$C6BD` synthetically and stops at `$C700`; it does not execute the preceding bank-4 initializer or the subsequent `$E096` call and is not integrated stage boot.

## Source-only target

The separate `recovery_gameplay_player_init_probe.s` and `build_recovery_gameplay_player_init_probe.py` use the existing boot loader without changing it. The builder generates six invented input fixtures, copies no cartridge bytes, reads no firmware and produces a source-only ADF. No shared reset/music probe, builder or verifier is modified.

Fixtures cover one active player, one inactive player, two active players, first inactive/second active, first active/second inactive, and both inactive. Original stack S includes 0, 1 and 255, including page-1 wrap. Context P varies, including decimal, carry and overflow bits. The exact fixture table is public in the ROM-free contract test.

The six calls preserve independent full RAM/context/journal buffers and before/after native register snapshots. The helper's D0 is the write-record count, not a success boolean. There is no count word in its journal. Expected counts are **18, 3, 33, 18, 18, 3**, totaling 93 ordered architectural RAM stores.

Payload: 20,904 bytes; rounded allocation: 20,992 bytes. ADF SHA-256:
`bdc80369cb6efdaf6953016af92b3f5458716f532c5b0c95c90d5d14f8582ee3`.

## Executed checks

- One actual 600-frame run with the pinned headless frontend and PUAE core, PAL A1200OG, 68020, 2 MiB Chip RAM, zero Fast RAM, CPU/memory/blitter cycle-exact enabled. Log confirms `PASS runs=600 video_callbacks=600`.
- `verify_recovery_gameplay_player_init_probe.py` independently executes the hash-checked Europe ROM instructions for each invented fixture. All six target RAM images, full contexts, ordered journals, untouched journal tails, original stack effects, native register snapshots and balanced native stack pointers match. Buffer bounds, non-overlap and guards pass; unused lower native stack remains untouched.
- `recovery_test_gameplay_player_init_target.py`: six positive baselines, **6,517 byte-corruption rejections, 978 pointer/alias/range rejections and two dump-size rejections**. A temporary isolated build containing only the required source files, without ROM or firmware, reproduces the payload and ADF byte-for-byte.
- `test_recovery_gameplay_player_init_contract.py`: **1,345 ROM-free cases**, using invented states and declarative effects rather than py65 or cartridge data. Full-state results, ordered architectural writes, journal counts/tails, guards and preserved native registers/stack match. Every traced native read/write is checked against explicit valid regions: helper code, STOP, RAM, context, journal and native stack. Five explicit bad-read checks reject distant/unmapped, guard and crossing addresses. No fallback allows arbitrary reads outside adjacent guards.
- The earlier 131,072 actual-ROM differential cases plus 259 inert-entry checks remain a separate host proof; this target test does not replace them.

Exact local hashes and pinned configuration are retained in the ignored `logs/recovery-gameplay-player-init-provenance.json`; negative results are in `logs/recovery-gameplay-player-init-negative.json`. The dump is a private diagnostic output, not included in source. Public code/report files contain no ROM, firmware, captured raw traces or proprietary assets.

## Reproduction

Set `VASM` to the existing approved assembler and `PYTHONPATH` to the existing `rescue-recovery-inspection/.deps` directory. Then run:

```sh
python port/tests/test_recovery_gameplay_player_init_contract.py
python port/tools/build_recovery_gameplay_player_init_probe.py
PUAE_MODEL=A1200OG RAM_OUT="$PWD/port/build/recovery-gameplay-player-init-probe-chip.bin" \
  "$HEADLESS" "$PUAE_CORE" "$PWD/port/build/recovery-gameplay-player-init-probe.adf" \
  "$PWD/artifacts/a1200-system" 600 "$PWD/port/build/recovery-gameplay-player-init-probe.ppm"
python port/tests/verify_recovery_gameplay_player_init_probe.py port/build/recovery-gameplay-player-init-probe-chip.bin
python port/tests/recovery_test_gameplay_player_init_target.py
```

The target checks logic and data on emulated hardware. They do not verify rendered gameplay, game-loop timing, performance, audible output or physical Amiga behavior. The aggregate/public scripts include this independent target and contract. Delivered media remains unchanged.
