# Bounded native gameplay and grounded jump

This checkpoint adds F92B player-contact helper154 and a narrow helper140
status-publication adapter. Every predecessor and raw helper140 implementation
remains byte-identical. Only successful helper140 publication clears the
nonphysical B convention; all real flags, RAM, stack, journals, resources,
mapper state and errors are preserved. Raw original/native output is compared
before publication, and cumulative stack/interrupt histories check the convention.

The earlier 134-frame failure remains recorded as a post-success status ABI
mismatch. It was never an unsupported rejection and has not been erased. With
the additive adapter, three genuine reset histories complete 240 host game
frames, 34,186 helpers, 634 logical NMIs and 4,977 ordered APU writes. Each
includes 3,268 raw helper140 comparisons. The independent restored edge-input
replay reproduces the goal. This is finite semantic coverage, not full gameplay.

The early A-edge history ends like Right-only because the original character
is falling during frames 0–19. The edge at frame 6 never enters the grounded
jump gate. A separate input schedule releases A through polls 0–23, presses it
on 24–29 and releases it afterward. Original and native execute the jump at
frame 25, rise 34 coordinate units from 05B4 to 0592 and land at 05B4/state0 on
frame 45. The comparison checks all 91 frame-boundary states across 90 frames,
including ascent, landing and later progression, against separate original-only
controls. No RAM, stack, bank, queue or scheduler state is injected.

The jump diagnostic adds no runtime code. Its ROM-free suite proves source
restoration, syntax and unchanged native/public contracts; the jump itself is
established by private original-first execution, not a syntax test. The early
exploratory counter discrepancy and all previous failures remain preserved.

These results do not prove rendered Amiga movement, complete pickup/throw,
real-time speed or full-game coverage. The longer stock target/audio integration
is separate ongoing work and is excluded here. The earlier measured target
costs remain unchanged; all its measured updates were late. Original cartridge,
firmware, private assets, generated disks/binaries and captures are excluded.
The delivered Z/X disk is untouched.

Immutable component reports retain their pre-review labels. Current independent
source/restore and original-first review records qualify only the bounded scopes
summarized here, not a released playable port.
