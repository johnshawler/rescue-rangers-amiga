# Persistent composed-background redraw contract

This additive 124-byte assembled module preserves the frozen background and sprite
renderers. It does not optimize sprite drawing and has no timing claim by itself.

Call order for each admitted unscrolled 8x8 snapshot:

1. Before first use, fill all 960 cache words with FFFF using
   `recovery_redraw_invalidate_all` (A4 points to 1920 writable bytes).
2. Call `nes_draw_background` with persistent framebuffer, opacity and tile cache.
3. Call `nes_draw_sprites_8x8` with the current complete OAM snapshot.
4. On successful sprite return, call `recovery_redraw_invalidate_oam` with A0
   pointing to that same 256-byte OAM and A4 pointing to the background tile cache.
   Do this before modifying OAM or beginning the next background call.

Both new functions preserve D0-D7/A0-A6 and use ordinary RTS; CCR is clobbered.
The OAM function needs 60 extra stack bytes; full invalidation needs 12, excluding
caller return address. Cache must be word-aligned, writable and nonaliasing with
OAM, code, stack and other scene buffers. OAM is read-only. There is no return
status or new persistent storage. The sprite renderer's D0 result is preserved.

Postdraw invalidation marks every tile intersecting each clipped 8x8 OAM bounding
box, not merely visible pixels. OAM Y=255 does not wrap; Y>=239 has no visible
rows. X is unsigned and clips at 256; Y clips at 240. At most four cache words
per visible sprite are written, with duplicates allowed. Disabled, transparent,
overflow and behind-background sprites are conservatively included. This makes
the next background call restore every pixel any old sprite could have touched,
including all five planes. Subsequent sprite drawing retains the exact frozen
priority, transparency and first-eight-per-line semantics. Old OAM need not be
retained because its footprint is already encoded as invalid cache words.

Each framebuffer/opacity/cache triple is one persistent render context. Invalidate
all before reusing a new/cleared/context-switched target, after any external edits,
or when selected background CHR or its contents change. NT/attribute changes are
already detected by the background cache key. Sprite-only CHR and OAM changes need
no extra invalidation because previous footprints were marked unconditionally.
RGB palette changes require updating hardware color registers; indexed bitplane
values do not encode RGB and are unchanged. NT attribute palette-index changes
are detected normally. Ensure prior successful sprite draws used the postdraw
hook; when adopting an already-composed framebuffer of unknown history, invalidate
all first. On error or interrupted composition, invalidate all before resuming.

Scrolling, background disable/left-eight clipping, 8x16 sprites and midframe state
changes are NOT implemented by this helper. Full invalidation does not make them
supported. Reject unsupported render contexts as the existing display gate does.
Unscrolled alternate nametable selection requires selecting the right NT pointer
and full context invalidation. A future scrolling renderer needs its own mapping
and clipping contract. Double buffering needs one cache/opacity triple per target.

Existing sprite behavior: the first eight vertically in-range OAM entries count,
even if transparent or X-clipped. Lower OAM index wins each nontransparent pixel
before background-priority testing, so a sprite hidden behind opaque BG still
blocks later sprites. Left-eight clipping follows PPUMASK bit2; sprite enable
follows bit4. No overflow flag, sprite-zero hit or pixel-timing emulation is added.

## Source-only validation

`port/tests/recovery_redraw_public_test.py` assembles actual 68020 code and uses
Musashi via machine68k. Both user and supervisor modes pass 2048 batched OAM tests
covering all 65536 possible X/Y byte pairs per mode. An independent pixel-enumeration
footprint oracle checks exact resulting cache words, not just a superset. Batched
coverage is not an exhaustive proof over all possible 256-byte OAM arrangements.
160 sequential composed frames are compared with SHA-pinned, separately authored
background and sprite per-pixel oracles that freshly draw all background tiles.
Cases include unchanged repeats, moving/removing sprites, dense overflow/overlap,
flips, both pattern tables, clipping, masks, attributes, CHR changes and new targets.
Every call traces width-aware memory access bounds, preserves registers/SP, guards
stack and checks code/input immutability and complete framebuffer/opacity/cache.
Synthetic correctness checks do not measure stock-Amiga time or display contention.
