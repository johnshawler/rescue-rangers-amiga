# Native 8x8 NES sprite blitter

`src/native_sprite_blitter.s` is an isolated 68020 software renderer, not a complete game port. It assembles with `vasmm68k_mot -m68020 -Fbin`. It is not connected to the boot renderer yet.

## ABI

Call `nes_draw_sprites_8x8` with:

- A0: 256 bytes of NES OAM (64 Y/tile/attributes/X entries).
- A1: 8192 bytes of currently mapped NES CHR, both pattern tables.
- A2: writable 51200-byte framebuffer, five consecutive 10240-byte planes, 40 bytes per row, 256 rows. Plane zero is the least significant palette index bit.
- A3: 7680-byte background opacity mask, 32 bytes per row for 240 NES rows, leftmost pixel in bit 7. Set bits only for *nonzero pattern pixels*, regardless of their final palette RGB. The caller must account for PPUMASK background enable and background-left clipping here.
- A4: writable 2196-byte scratch area, longword-aligned. Must not alias inputs/framebuffer; contents are destroyed.
- D0: PPUCTRL byte (bit 3 selects sprite pattern table; bit 5 requests unsupported 8x16 mode).
- D1: PPUMASK byte (bit 4 sprite enable; bit 2 sprites in left eight pixels).

D0 returns zero on success, -1 for unsupported 8x16 mode, which leaves output/scratch unchanged. D1–D7 and A0–A6 are preserved. CCR is clobbered. Maximum additional stack use is 68 bytes plus the caller's return address. All buffers must be valid for their complete stated extents.

The caller supplies a freshly drawn background each frame (including a cleared fifth plane) before drawing sprites. Otherwise old sprites remain. The NES picture occupies Amiga coordinates x=32..287, y=8..247. Borders are untouched. Sprite colors use palette indices `16 + 4 * palette + pattern_pixel`; transparent pattern zero does not write. Map the corresponding NES palette entries to Amiga colors 0..31 separately.

## Semantics and limits

- OAM Y is top minus one. Y=255 does not wrap to the first visible row. Sprites can clip at the right and bottom of the viewport.
- Both flips, four sprite palettes, transparent pixels, BG priority, and ascending OAM priority are implemented. A nontransparent low-index sprite hidden behind opaque BG still blocks later sprites at that pixel, matching NES priority selection.
- Only the first eight in-range sprites per scanline are evaluated, including transparent/offscreen-X sprites. No sprite-overflow flag or hardware overflow evaluation bug is emulated. No sprite-zero-hit or PPU timing/status behavior is implemented.
- OAM, CHR and registers are one frame snapshot. No midframe mapper, OAM, palette or PPU register changes are modeled. 8x16 mode explicitly returns an error.
- This is correctness-first per-pixel CPU code. It builds first-eight OAM lists once with at most 64*8 row visits, then performs per-pixel read/modify/write plane updates; it makes **no 50 Hz/60 Hz or 100% game-speed claim**. Emulator CPU tests are correctness tests, not stock PAL A1200 timing. Real PAL 68EC020/AGA/2 MB Chip/zero Fast measurements including display DMA and game logic are still required. Further caching/span optimization is expected.

## Integration still required

Allocate 51200 rather than 40960 Chip bytes per framebuffer, program five BPL pointers and five-plane BPLCON0, supply 32 colors, construct background opacity during tile rendering, and restore dirty background regions before each sprite pass. The existing four-plane renderer is deliberately unchanged by this module. Ensure the 40960-byte fifth-plane offset retains its 68020 long-displacement encoding. No original ROM/CHR assets are included in the module or its synthetic tests.

## Validation

`tests/test_native_sprites.py` assembles the real source and executes the binary with Musashi's M68EC020 core through `machine68k`, comparing all 51200 framebuffer bytes with a separate per-pixel NES oracle. Twenty synthetic cases cover palettes/flips/both pattern tables, eight-sprite limiting, hidden-sprite priority blocking, clipping and mask controls, rejected 8x16 mode, and random/dense OAM. It also checks preserved registers, stack, scratch bounds and unchanged source buffers.

Example setup/run (outside the checked-in project dependencies):

```sh
CC=gcc CXX=g++ python -m pip install --target /tmp/nes-sprite-test-deps machine68k
PYTHONPATH=/tmp/nes-sprite-test-deps python port/tests/test_native_sprites.py
```

Set `VASM` to an alternate assembler path if needed. Tests pass with machine68k 0.5.0. These tests execute actual machine code but model no Amiga display DMA or Chip bus contention; emulator cycle counts must not be presented as measured stock-A1200 throughput.

## Evaluation optimization

Scratch offsets: 0..31 current-row ownership mask, 32 PPUMASK, 33..35 padding, 36..275 per-row sprite counts, 276..2195 eight OAM byte offsets per row. Lists are rebuilt in ascending OAM order; out-of-range Y stops that sprite, counts are capped at eight, and transparent/left-clipped sprites still consume slots. This replaces up to 15360 range checks with at most 512 row insert attempts. The assembled-code suite still passes all 20 cases. Amiga timing must be measured independently after allocating the enlarged scratch buffer.
