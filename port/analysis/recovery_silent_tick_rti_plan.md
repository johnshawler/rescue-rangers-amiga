# Bounded first silent tick and NMI return: research plan only

No native continuation is implemented by this report. The completed eighth helper ends at `$C0F3`. This research independently executes the following original-ROM path for the established synthetic startup state.

## Verified next path

`$C0F3` jumps to the NMI queue scan at `$C0DC`. The next startup slot is empty (`$DB=1`, `$DD=$88`), so `$C0F6` calls bank-3 `$8000` (JMP `$803A`).

The first silent update:

- Advances `$C0` from 0 to 4; this selects one update, not the additional update taken when the masked counter wraps to zero.
- Sets scratch `$C3=0`; with `$D0|$D1=0`, skips the active sound-stream update at `$8224`.
- With `$C8/$C9/$CA=0`, leaves accumulator `$C8` and step scratch `$C7` zero.
- With `$CF=0`, skips active-channel routine `$82B0`.
- Calls `$8363` four times. Its X transformation selects pointer pairs `$0750–$0757`; the reset command cleared these, so each call returns at `$839C` without processing notes, envelopes or writing APU registers.
- Restores `$CF`, performs the original LSR/ASL writes to `$C0`, and with `$CC & $7F=0` skips the additional envelope/tempo branch.

It returns to fixed `$C0F9`, publishes restore-bank `$F1=6` through five `$FFF0` writes, restores Y/X/A/status, and executes RTI at `$C114`.

For the established startup input, this is exactly **144 original instructions**, **26 ordered RAM stores**, **five mapper publications** and **zero APU writes**. Final bank is 6. Return context is PC=`$FE8D`, A=0, X=`$BB`, Y=0, SP=`$BB`. `$C0=4`; the interrupt frame has been consumed but its old RAM bytes remain. No resumed scheduler instruction executes in this research boundary.

Private trace evidence is retained in `logs/recovery-silent-tick-rti-research.json`. Actual bank-3 and fixed-bank bytes come from the same previously hash-verified private cartridge.

## Proposed small helper scope

A future startup-specific continuation could cover `$C0F3` through RTI, retaining every stack/scratch store and emitting the five bank-restoration records. It should reject unsupported conditions before mutation, rather than treating active music as silent.

Candidate guards to verify before implementation:

- Exact entry PC `$C0F3`, bank-3 selected and expected startup NMI stack/context.
- Valid queue read index with current slot empty; no queued command silently skipped.
- `$C0=0`, `$CF=0`, `$D0=$D1=0`, `$C8=$C9=$CA=0`, `$CC=0` and cleared `$0750–$0757` channel pointers, ensuring the observed silent branch.
- Expected restore-bank shadow and bank-busy state (startup `$F1=6`, `$F5=0`).
- Valid saved handler/interrupt frames returning to the selected `$FE8D` boundary, including their status representation.

These are a proposed deliberately narrow contract, not existing support or final guards. Active sound streams/channels, counter-wrap double update, envelope branches, arbitrary queue draining, and arbitrary interrupt return addresses remain separate work.

## Explicit status-representation compatibility issue

The existing NMI-prefix helper requires canonical context P with B=0/U=1. That is a representation invariant: the 6502 B marker is not an ordinary persistent hardware flag.

py65's PLP and RTI implementations assign:

`p = popped_status | BREAK | UNUSED`

For this startup path, the actual hardware-saved status byte is `$A4`, but py65 exposes **raw P=`$B4` after RTI**. Passing that raw byte to the existing prefix helper causes its canonical-P guard to reject. This is a real cross-boundary representation mismatch, not evidence that the NMI prefix or original stack frame was wrong.

Before implementing the next helper, choose and document a consistent ABI policy. Recommended option:

- Define an explicit architectural-status view at RTI output: preserve N/V/D/I/Z/C, set U, clear virtual B.
- Retain and assert the oracle's raw py65 result and all original pushed/popped stack bytes separately.
- Compare the native canonical context to this named oracle view. Do not mutate oracle RAM/stack, silently rewrite `ref.p`, or insert an unexplained context byte patch between helpers.
- Add a follow-on NMI test proving the canonical returned context satisfies the existing guard, while the unnormalized raw py65 byte is rejected as currently specified.

Alternatively, keep raw py65-style P at the return boundary and introduce an explicit separately tested adapter before reuse of canonical-P helpers. Changing the old prefix guard without a documented ABI decision is not proposed.

No option is implemented here. In either design, status-byte normalization must be explicit and justified as representation conversion; it must not mask a real N/V/D/I/Z/C or stack-return mismatch.

## Limits

The chosen injection point remains an explicit logical NMI at the first task yield, not a hardware-timing claim. A future successful tail would complete this bounded first NMI but would still not implement scheduler continuation, title resources, audible Paula output, gameplay or a full audio engine.
