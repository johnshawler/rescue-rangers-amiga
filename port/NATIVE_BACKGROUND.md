# Callable native background renderer

`nes_draw_background` in `src/native_background.s` draws dirty tiles from one NES nametable into five consecutive Amiga bitplanes. It is a callable module, with no OS, Copper, timer or display setup and no original game assets.

## ABI

- A0: readable 1024-byte nametable: 960 tile IDs followed by 64 attribute bytes.
- A1: readable 4096-byte currently selected background CHR pattern table.
- A2: writable 51200-byte framebuffer: five consecutive 10240-byte planes, each 320x256 pixels / 40 bytes per scanline.
- A3: writable 7680-byte background opacity buffer: 240 rows of 32 bytes, leftmost pixel in bit7, NES-local origin (0,0).
- A4: writable, word-aligned 1920-byte tile cache: 960 big-endian words, initialized to FFFF before first draw.

All D0-D7/A0-A6 are preserved; CCR is clobbered. A7 is restored by the ordinary RTS call convention. Additional stack use is 60 bytes plus return address. Inputs, framebuffer, opacity and cache must not overlap. Cache key is tile ID in bits0..7 plus attribute palette number in bits8..9.

Changed tiles overwrite all five planes within Amiga x32..287,y8..247. Plane4 is cleared; planes0/1 come directly from CHR; planes2/3 encode the two-bit palette number. Palette indices are `palette*4 + pattern_pixel`, including zero pixels: configure Amiga entries0/4/8/12 to the same NES universal background color. Opacity is the OR of both pattern planes regardless of palette. Borders and unchanged tiles are not touched.

## Required caller discipline

- A CHR-bank/content change requires invalidating all affected cache words (use FFFF), since the key contains no CHR generation.
- A new/cleared framebuffer or opacity buffer also requires invalidation. The cache, framebuffer and opacity must refer to the same persistent scene.
- This routine assumes background enabled with no scrolling, midframe changes or left-eight-pixel mask. Apply background mask semantics separately before sprite composition.
- Dirty background rendering alone does not erase old sprites in otherwise unchanged tiles. Prefer drawing into a pristine background framebuffer and copying it to the composition framebuffer before sprites, or restore all old sprite coverage and keep caches consistent. If drawing over an existing sprite composition, explicitly invalidate every tile touched by old sprites before this call.
- No pristine-copy synchronization helper is provided. The cache skips unchanged bytes by design, even when an external caller has modified them.

## Validation and performance

`tests/test_native_background.py` assembles the module and executes actual machine code using machine68k/Musashi M68EC020. A separate pixel oracle checks all five planes, borders, opacity, cache and preserved registers. Cases cover all attribute quadrants, unchanged rejection, dirty text-like tile edits, palette-only changes, and CHR changes with/without explicit invalidation.

Run with machine68k installed and `VASM` set if necessary:

```sh
PYTHONPATH=/tmp/nes-sprite-test-deps python port/tests/test_native_background.py
```

This is not a whole-game port or hardware performance measurement. Stock PAL A1200/AGA/2MB Chip/zero Fast throughput, including display DMA and game logic, still needs measurement.
