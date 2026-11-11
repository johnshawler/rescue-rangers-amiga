# Restore and reproduce

Preserve existing baseline files. This addition is isolated to the files listed
in `recovery_scroll_view_manifest.json`; no existing renderer, builder or disk is
replaced. Remove only these added files to undo the addition. Do not restore or
remove unrelated concurrent workers' files.

Requirements: Python 3, machine68k/Musashi with M68EC020 support and vasm Motorola
syntax assembler. Synthetic proof command, from repository root:

```sh
VASM=/path/to/vasmm68k_mot \
PYTHONPATH=/path/to/machine68k/dependencies PYTHONDONTWRITEBYTECODE=1 \
python port/tests/recovery_scroll_view_test.py
```

The test imports the frozen `port/tests/test_native_sprites.py` pixel oracle and
assembles `port/src/native_sprite_blitter.s` for repeated sprite composition.
These are read-only baseline dependencies included by hash in the manifest.
Assembler binaries are temporary and automatically removed. No cartridge,
firmware, disk, audio or capture belongs in this source deliverable. No commit,
publication or target integration is performed by this test.
