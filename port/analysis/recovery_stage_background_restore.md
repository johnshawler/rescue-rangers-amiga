# Reproduce visible-tile background proof

Use the existing recovery checkout and pinned vasm/Musashi tooling. Preserve the
old renderer and all existing captures. No ROM or firmware is needed for:

```
export PYTHONDONTWRITEBYTECODE=1
export VASM=/path/to/vasmm68k_mot
export PYTHONPATH=/path/to/approved/python/dependencies
bash port/tools/recovery_stage_background_public.sh
```

The private original-derived proof needs the already authorized cartridge at
`input/rescue-rangers-europe.nes` (SHA-256
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`)
and a previously qualified target capture. It reads its actual input-change
history and independently replays original instructions. It neither injects
capture state into the reference nor writes assets or snapshots:

```
python port/tests/recovery_stage_background_original_test.py port/build/recovery-stage-target-v3
```

Frozen candidate source SHA-256:
`d916fffbc90f750b96568fc85f4f069a1b6b4e8bff706cec7756b5c628c23f3e`.
Standalone assembled binary is 472 bytes, SHA-256
`b58a304b8f07c2eac9716e6337962dbd87db72443bbad7c94bb310cc25102a74`.
Old source remains SHA-256
`f008fbd4797bd6d19586fddd3496b8b107b4d2427fcb32d6ae086d0ded372b41`.

Do not publish cartridge/firmware, generated target disks, CHR/PRG, screenshots,
PCM, captured RAM or original disassembly. Target integration must remain a
separate new output, retaining the original CHR selection and sprite path. It
requires independent renderer review and actual-input/device/Copper/pixel/PCM
qualification before any performance claim. Equal final state alone is not a
matched input history, and host runtime is not Amiga performance.
