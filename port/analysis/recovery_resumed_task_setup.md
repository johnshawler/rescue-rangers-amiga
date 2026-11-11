# Recovery resumed task palette setup

This is newly authored static 68020 translation, not recovery of lost playable or
audio sources. It extends the ten-helper recovery chain from `$C584` to the next
original scheduler yield at `$FE8D`, inside the palette routine. Existing source,
probes, stable builds and delivered ADFs are unchanged.

## Source-verified scope

Private Europe ROM SHA256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
The reference executes actual fixed-bank instructions, not a hand-written model.

- `$C584–$C593`: write `$E4=$88`, call `$F377` with sound command `$07`, write
  `$F8=2`, then call `$C274`. The sound queue follows the original empty-marker
  test, writing and advancing modulo eight only when the current slot is `$88`.
- `$C274–$C2A7`: set `$0F/$0D=$10`, `$9A=0`, `$0E=4`; copy 32 bytes descending
  from caller RAM `$0320–$033F` to `$0300–$031F`; descend again subtracting `$10`
  modulo 256, replacing a negative result with `$0F`. This is the original sign
  test, not an unsigned saturation approximation. All intermediate stores remain.
- Set `$18=$FF`, push delay 4 and call `$FF04`, including its `$FEF7` subroutine.
  Task zero becomes waiting state 1, timer 1, saved SP `$B8`. Stop before the
  scheduler's `$FE8D` instruction executes.

Original nested stack is retained: `$01BE/$01BF=$93/$C5` returns to `$C594`;
`$01BD=4` is the delay; `$01BB/$01BC=$A7/$C2` returns to `$C2A8`;
`$01BA/$01B9=$10/$FF` save X/Y; `$01B7/$01B8=$0E/$FF` are the consumed inner
JSR bytes. Each call's overwritten stack stores are also retained in event order.
Final A=0, X/SP=`$B8`, Y=0, C/Z=0, N=1. V is from the last SBC (palette index
zero): set for source `$80–$8F`; I is preserved. Reserved context byte is untouched.

There are **89 RAM stores** when the queue slot is occupied and **91** when empty.
No mapper, PPU, APU, controller or cartridge-resource transaction occurs in this
slice. The palette source is already in caller RAM, not an extracted or embedded
cartridge asset. The caller must preserve the prior logical bank-6 resource state.

## ABI and guarded support

`port/src/recovery_resumed_task_setup.s` exports `recovery_resumed_task_setup`:

- A0: valid writable original-layout 2048-byte RAM.
- A1: valid writable eight-byte context: big-endian PC, A/X/Y/P/SP/reserved.
- Buffers must be disjoint and exclusively owned for the synchronous call.
- A2 is preserved, unused. No journal buffer is needed because there are no
  external effects; all pending work remains explicitly represented in RAM.
- D0=1 success; D0=-1 unsupported, with RAM/context untouched. D1–D7/A0–A6
  preserved, native stack balanced, native CCR scratch.
- Require PC `$C584`, A/X/SP `$BF`, Y=8, canonical P in `$A0/$A1/$A4/$A5`,
  task selector `$91=0`, queue index `$DA<8`. Other RAM can vary.

D must be zero. The NES CPU performs binary SBC even with D set, whereas py65's
6502 executes decimal arithmetic. Rather than alter raw reference status or
pretend that comparison proves decimal-marked input, this bounded helper rejects
it inertly. This is a documented restriction compared with the preceding helper.
This narrows the oracle-tested scope; it does not imply that the game or NES
requires D=0. The continuous tests select D=0 at their original `$FE24` entry and never patch it
between helpers. No runtime general-purpose 6502 interpreter is in the native code.

## Differential verification

Run with `VASM` and py65/machine68k configured:

```
python port/tests/recovery_test_resumed_task_setup.py
```

The test assembles all eleven actual 68020 helpers and runs M68EC020 instructions.
It compares all 2048 RAM bytes, eight context bytes and the complete ordered RAM
and external-effect stream against original ROM instructions. Standalone cases
cover all palette byte values crossed with all queue-slot values, varied queue
indices, all four supported P combinations, and randomized palette/RAM with
explicit empty queue slots. Native register/stack preservation, guards, unexpected
writes, bounded execution, inert invalid calls and completed-boundary rejection
are checked.

Continuous runs use the original reset path, one real logical `nmi()`, F0 reset,
silent tick, real RTI, controller scheduler resume with varied two-pad input, then
this helper. Native RAM/context pass directly between calls without state patches.
The named `architectural_status_view` clears only py65's virtual B and sets U for
comparison. Raw py65 P is not modified, and raw saved-frame checks remain intact.

Executed result: **66,560 standalone cases, 256 continuous eleven-helper
compositions, 67,310 unsupported-input rejections and 66,560 completed-boundary
rejections passed**. Standalone cases include 65,536 palette/queue-value pairs
and 1,024 randomized empty-queue cases.

## Exact next boundary and limitations

`$FE8D` must now wait for a later event, then restore the nested continuation at
`$C2A8`, not the first task continuation `$C584`. `$18=$FF` requests palette work;
`$D9=7` and possibly a queued `$07` request audio work. These requests are preserved,
not consumed or replaced by fabricated output. Existing first-NMI and first-resume
guards are not valid for this later state. Supporting it needs new independent
translation and verification.

No next NMI, audible Paula output, playable game, full boot, title integration,
full-speed claim or physical-Amiga validation is supplied here. No publication or
commit is made by this work, and no private ROM extracts or trace snapshots are
included in the deliverable.
