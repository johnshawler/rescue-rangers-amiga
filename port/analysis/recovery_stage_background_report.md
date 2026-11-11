# Additive visible-tile background renderer

## Scope and algorithm

`port/src/recovery_stage_background_draw.s` preserves the exact standalone
horizontal viewport contract of `recovery_scroll_view_draw.s`. It is an additive
candidate, not a change to the frozen renderer, delivered disk, native game
composition, sprite renderer, or profiling checkpoint.

Each eight-scanline group resolves 33 consecutive world tiles starting at the
coarse origin, wrapping modulo 64. It caches their 16-bit CHR offsets on the
stack and their two palette masks in the existing scratch region. Each scanline
loads only those 33 tiles' two pattern bytes. Four explicit packed word-shift
merges emit each of the 32 viewport bytes. The extra tile is deliberately decoded
at aligned origins too, keeping one bounded path. This is not a per-pixel
renderer or a persistent dirty cache.

At an admitted visible draw, source reads are exactly 1,980 nametable bytes
(33 tile IDs and 33 attribute bytes for each of 30 groups) and 15,840 CHR bytes
(33 tiles, two planes, 240 scanlines). These are algorithmic access counts, not
hardware timing or a speedup measurement.

## ABI and bounds

The original ABI applies unchanged: A0 immutable 2,048-byte physical nametables,
A1 immutable selected 4,096-byte background CHR table, A2 five 10,240-byte planes,
A3 7,680-byte opacity, A4 256-byte scratch. D0 is exactly 0x90/0x91, D1 0x1e/0,
D2 0..255, D3 zero, D4 0x1e, all long-width validated. D0 returns 0/-1;
D1-D7/A0-A6 and normal RTS/SP are preserved, CCR unspecified. USER and supervisor
are supported. Regions must be disjoint valid RAM, inputs immutable during call.

Maximum stack below the return address is 128 bytes: 56 saved register bytes,
6 scalar-local bytes and 66 cached CHR-offset bytes. Blank/reject use 56 bytes.
All 256 scratch bytes remain sufficient, with no initialization requirement.
No NT/CHR reads or output/scratch writes occur on rejected scalar inputs.
Mask-zero software blanking clears viewport and opacity while preserving scratch
and borders. It remains distinct from the target's existing hardware-DMA blanking.

Origin is ((ctrl & 1) * 256 + scrollX) modulo 512. Viewport is x32..287,
y8..247 in five 320x256 planes. All viewport bytes are overwritten, borders
preserved, plane four zeroed and opacity is the OR of the two pattern planes.
The intentional index contract is 4 * attribute + pattern even when pattern is
zero. Palette entries 0/4/8/12 still map to the universal background color.
Vertical scrolling, partial masks, 8x16 sprites and midframe changes are not
supported. Tile/attribute/CHR edits and old sprite pixels are consumed afresh.

## Verification

The synthetic test retains the frozen independent per-pixel oracle. It compares
all 51,200 framebuffer and 7,680 opacity bytes at every 512 origin in USER and
supervisor modes, with repeated sprites and source changes. The separate
adversarial suite directly compares the assembled candidate and baseline against
that oracle at every fine shift around both nametable seams, including tile 255,
zero/full/alternating patterns and asymmetric attribute quadrants. Width-aware
traces check every complete access, exact source-read counts, guards, immutable
code/inputs, registers and stack. High-word-invalid scalar fields must be inert,
even with a blank mask. Blank scratch preservation is explicit.

The private original test replays the qualified v3 capture's actual input-change
history through original instructions, builds supported completed-NMI background
states from original device events, and compares every distinct background state
against both assembled implementations and the independent oracle in both CPU
modes. It also compares complete final stage composition using the unchanged
sprite renderer with the original-derived independent final-pixel oracle.

Standalone verification and target measurement results are recorded separately.
No host execution duration is target-speed evidence.

Completed standalone results: 1,084 synthetic calls (80 width-traced), all
512 origins in both CPU modes; 276 additional adversarial calls (all traced);
248 private original-state calls (all traced), covering all 395 admitted
completed-NMI states through 61 distinct background states, plus complete final
sprite composition. The private replay uses the original v3 actual-input
history: 14,313 helpers and 733,209 original instructions. All passed.
