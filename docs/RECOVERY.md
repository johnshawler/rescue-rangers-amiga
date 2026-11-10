# Rescue Rangers recovery checkpoint

The private recovery package preserves a reproducible **early title/menu source baseline**, plus
the later playable binaries. It does not recover the missing gameplay, restart,
optimized rendering, stage5D or audio source developed after the title milestone.
Those later development results must not be attributed to this source tree.

## What was recovered

- The original title milestone archive contains 51 entries, including native
  68020 title/game-primitives/renderer source, build scripts, five source-level
  test suites, captured reference fixtures and the headless emulator harness.
- Its source rebuild produces the identical title ADF, SHA-256
  `03b774d76a6b547ff6b4b3ffd71428d381247f4802a40bab1a56eb3d1ea2b475`.
- The later interactive checkpoint archive contains only README, stock and Fast
  ADFs and a screenshot. It has no gameplay source, build scripts or tests.
- The separately delivered stock Z/X ADF is intact. It differs from the earlier
  stock ADF by exactly two keyboard-map bytes: offsets 460492 and 460494.

Original input archives and delivered files were copied into a distinct recovery
area. They were not overwritten. Source archive inventory and content hashes
are supplied with the private package. All scripts and new reports are labeled as
recovery work, not as reconstruction of missing later source.

## Newly repeated checks

- 137,280 original-ROM versus assembled-68020 game-primitives cases.
- 4,592 original-ROM versus native title/menu yield intervals.
- 1,024 original PPU-queue comparisons.
- Seven background and twenty sprite cases, plus sixteen native selftests.
- Five cycle-exact PAL A1200 title/menu target scenarios, including both player
  counts, Chip, Dale and the intentional untranslated gameplay handoff. Actual
  display pixels match both the independently preserved original reference
  and the decoded Amiga framebuffer in every scenario.
- The later Z/X binary independently boots into gameplay on the rebuilt core.
  A bounded 4,500-physical-frame run completes 2,089 native updates after actual
  keyboard Start, movement, X, Z and pause/resume key events, with zero runtime
  or renderer fault and intact native stack guards. This is a boot/input smoke
  test, not a replacement for the missing full gameplay differential suite or
  a claim that each interaction was reverified against the original ROM.

No new gameplay-speed or full-game compatibility claim is made. The later
playable disks are silent and incomplete. The source baseline stops after its
menu handoff and does not contain a playable stage.

## Reproduce

Use this repository or a copy of `title-source/` from the private recovery archive. Keep that archive intact.
Supply the original European cartridge at `input/rescue-rangers-europe.nes` and
your existing A1200 Kickstart 3.1 at `artifacts/a1200-system/kick40068.A1200`.
Neither full cartridge nor firmware is included. Their required SHA-256 values
are recorded in the recovery manifest. The existing captured title fixtures are
included because they were part of the original source milestone.

Install Python dependencies py65, machine68k, NumPy and Pillow. The tested
assembler and emulator revisions are pinned in the recovery manifest. Compile
`scripts/headless.c` against the libretro headers with `-ldl` and
`-Wl,--no-as-needed -lm`. Set VASM, PUAE_CORE and HEADLESS to those tool paths;
set PYTHONPATH if the Python packages are in a private directory. Run
`bash validate_recovery.sh`.

The recovered source has not been altered to imitate the missing gameplay.
Further source work must start from this accurately identified baseline or a
newer verified source backup, if one is found. Preserve new source, tests and
provenance together in each future checkpoint.
