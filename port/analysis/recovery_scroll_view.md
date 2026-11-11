# Additive horizontal background viewport

`port/src/recovery_scroll_view_draw.s` contains only generic native 68020 code.
It does not replace a frozen renderer or change a builder, disk, or game state.
It is a correctness foundation for the independently observed genuine first-stage
horizontal scrolling, not an integrated stage or a performance result.

## ABI

Call `recovery_scroll_view_draw` with:

- A0: immutable 2048 bytes, physical NT0 followed by distinct physical NT1.
- A1: immutable 4096-byte **selected background pattern table**. The caller
  resolves CHR banks and PPUCTRL bit4. This is not the sprite renderer's complete
  8192-byte pattern view.
- A2: writable five contiguous 10240-byte 320x256 bitplanes (51200 bytes).
- A3: writable 7680-byte 256x240 background opacity, MSB-left.
- A4: writable 256-byte scratch; no initialization needed or persistent cache.
- D0: long PPUCTRL, exactly $90 or $91 (8x8 sprites, horizontal NT selection).
- D1: long PPUMASK, exactly $1e or zero.
- D2: long scroll X, 0..255 inclusive.
- D3: long scroll Y, exactly zero.
- D4: long MMC1 control, exactly $1e (vertical nametable mirroring).

D0 returns zero on success, -1 for unsupported input. D1-D7/A0-A6 are preserved,
CCR clobbered; normal RTS restores SP. The renderer uses 62 stack bytes beyond
the four-byte return address on its rendering path (56 saved registers plus six
local bytes), 56 on blank/reject paths. Stack must be word-aligned. All regions
must be disjoint, with ordinary readable/writable RAM and immutable inputs during
the call. Invalid pointers/aliases are caller errors, not checked modes.

Unsupported scalar parameters cause no output or scratch writes and no NT/CHR
reads. Validation precedes the mask-zero path too. No vertical scrolling,
PPUCTRL vertical NT selection, 8x16 sprites, grayscale, emphasis, left-eight
mask, partial masks or midframe changes are admitted.

## Exact output contract

World origin is `((PPUCTRL & 1)*256 + scrollX) % 512`. Each output pixel samples
that world X plus screen X, modulo 512, at unchanged Y. Each physical nametable
provides its own tiles and attribute quadrants. Word shifts merge adjacent tile
bytes separately for the four indexed-color planes. Attribute bits therefore
remain correct across tile and NT boundaries, even for transparent pattern
pixels. Pattern bytes OR together produce opacity; attribute bits never do.

All viewport bytes at Amiga x32..287/y8..247 are overwritten each call. Plane4
is zero there. Borders outside the viewport remain byte-identical. The index is
`4*attribute_palette + pattern_pixel`, including zero pattern pixels; Amiga
palette entries 0/4/8/12 must map to the universal background color. Opacity is
one precisely for nonzero two-bit CHR pixels.

Mask zero deterministically clears viewport and opacity while preserving borders
and scratch. This optional software buffer policy is **not** NES retained-buffer
hardware behavior. Existing live DMA/backdrop blanking may bypass the renderer
and keep its previous planes, as before.

There is no dirty cache and no generation counter. Every draw consumes current
NT, attribute, CHR, origin and existing border bytes, fully restoring the viewport
over old sprite compositions. The existing sprite renderer can then draw into
these planes with this opacity. It is safe to change neighboring tiles,
attributes, CHR, coarse/fine scroll or framebuffer between calls. Do not invoke
the old dirty background renderer afterward with a stale cache.

## Synthetic proof and limits

The test assembles actual source with vasm and runs Musashi M68EC020 in USER and
supervisor modes. Its independent oracle selects each world pixel using division
and individual pattern bits, then packs destination planes; it does not reuse
the native adjacent-byte merge. It compares all 51200 framebuffer bytes including
borders, and all 7680 opacity bytes for every 512 horizontal origin in both modes.
Selected seam/fine positions, all rejects, blanking and repeated sprite rounds
have width-aware memory-access tracing. All calls check immutable inputs/code,
registers/SP and guards. Random synthetic NT/CHR include transparent tiles and
varied attribute quadrants. Repeated composition uses the unchanged native sprite
module and independent sprite oracle with source changes between redraws.

No original assets are required. These tests do not measure target throughput,
display DMA interaction, original game state or audible behavior. No target
capture has been produced by this module. Any integration must first independently
qualify the original state, select the correct live CHR view, retain existing
error/backdrop semantics, and then measure actual PAL hardware/emulator intervals.
