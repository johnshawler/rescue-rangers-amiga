# Startup resource progress

11 November 2026. New files only; existing artifacts and source untouched.

Completed bank selection C5BB -> C5C0 via FF53. Public helper
`recovery_startup_bank_select.s` accepts PC C5BB and F6=0 only. Invalid PCs
and all 255 nonzero F6 values reject before mutation. F6 is never cleared.
A0 RAM2048, A1 context8, A2 mapper journal22; no cartridge resource needed.
Caller guarantees empty MMC1 serial latch, PRG mode 3 and exclusive buffers.
Preserves registers other than D0 and native CCR; original SP, X/Y and context
reserved byte unchanged. Raw status becomes `(P & 0x7c) | 2`. The original
wrapped JSR stack writes, F1/F4/F5 changes and five ordered mapper writes are
preserved. Journal metadata carries live F5, including overflow to zero.
No asynchronous interrupt interleaving or deferred-audio branch is claimed.

Focused tests `recovery_test_startup_bank_select.py` and `--rom` each pass
256 full-RAM randomized cases covering every raw status/SP. Public suite
also passes 65,790 inert guards (all other PCs and every nonzero F6).
Complete RAM/context, ordered RAM/mapper effects, ABI, guards, immutable
resource sentinel and global access bounds are checked against an independent
public model and the hash-verified private original.

`recovery_test_resident_startup_bank.py` continues the frozen resident video
proof without editing it. One RAM/context load at reset. F6 naturally equals
zero at C5BB on both independently running machines; mapper entry is verified
1E/00/10/06 with empty latch. 535 native calls, 18 reference NMIs, 16 later
active audio calls. Final C5C0/00/00/00/26/BF/A7, mapper 1E/00/10/02, empty
latch. Effects: 8,855 RAM, 3,620 PPU, 205 mapper, 324 controller, 784 resource,
114 APU. No pending work is cleared, no reference state is reloaded.

Next dependency is the real bank-2 loader8000 at C5C0, then setup8820 and
render enable before C5CB. The loader uses indexed pointers and counted
resource commands with page-crossing stack calls. Its actual count semantics
are signed DEC/BPL, not an unsigned length. This checkpoint does not implement
that loader or consume the subsequent live CHR requests. Host M68EC020 proof
only; no Amiga execution, delivered disk, playable game, speed or audible
output claim. Private cartridge remains private; no captured state published.
