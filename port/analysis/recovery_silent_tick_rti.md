# Recovery first silent tick and interrupt return

This is new recovery source, not recovered later gameplay/audio code. It completes one explicitly injected startup NMI through its first silent update and RTI. It stops **before the resumed scheduler instruction at `$FE8D` executes**. Existing helpers, probes, title code and delivered ADFs are unchanged by this deliverable.

## Actual original-ROM path

Private PAL cartridge SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.

The original oracle reads actual PRG bank 3 at CPU `$8000–$BFFF` (file offset `16 + 3*16384 + address - $8000`) and fixed bank 7 at `$C000–$FFFF` (offset `16 + 7*16384 + address - $C000`). Continuous tests decode the original five-write PRG publications and actually remap the lower cartridge window, including restore bank 6.

`src/recovery_silent_tick_rti.s` covers:

1. `$C0F3` jumps to `$C0DC`. Startup queue index `$DB=1` selects empty `$DD=$88`; branch to `$C0F6` calls bank-3 `$8000`, which jumps to `$803A`.
2. Store scratch `$C3=0`, advance `$C0` from 0 to 4 and take one update. `$D0|$D1=0` excludes active streams. `$C8/$C9/$CA=0` leave accumulator `$C8` and scratch `$C7` zero.
3. Save `$CF=0`, iterate X=3 down to 0. Each call to `$8363` finds its channel pointer pair zero and returns at `$839C`. Every original PHA/JSR stack store and every repeated zero store to `$CF` is retained.
4. Restore `$CF`, store `$C0=2` then 4 for the original LSR/ASL, and skip the extra branch because `$CC=0`. Return to fixed `$C0F9`.
5. Publish restore bank `$F1=6` through five `$FFF0` records with full original byte values `06 03 01 00 00`. Restore saved Y/X/A, execute the semantics of PLP/RTI and return at `$FE8D` with SP=`$BB`.

Each accepted path executes **144 original instructions**, with **26 ordered RAM stores**, **five mapper publications**, and **zero APU writes**. Original stack bytes remain in RAM after they are consumed. These are instruction-semantic events, not electrical dummy writes or a cycle-timing model.

## Deliberately narrow ABI and guards

- A0: valid writable 2048-byte original-layout RAM.
- A1: valid writable eight-byte context: big-endian PC word, A, X, Y, P, SP, reserved byte.
- A2: valid writable 22-byte mapper journal: big-endian count word and five `{address word, original data byte, busy byte}` records. Each complete record precedes its count increment.
- Buffers must be disjoint and exclusively owned during synchronous execution.
- The caller selects this static **bank-3** implementation. Bank selection is not a field in the existing context ABI, so the helper cannot inspect it. The actual-ROM tests assert bank 3 on entry and bank 6 after restoration. The native journal requires an explicit future resource adapter; it is not an MMC1 interpreter or target hardware write.

Every guard is checked before RAM/context/journal mutation:

- Entry PC=`$C0F3`, A=0, X=`$FF`, Y=`$0C`, SP=`$B4`, P=`$26` or `$2E`.
- `$DB=1`, `$DD=$88`, restore shadow `$F1=6`, busy flag `$F5=0`.
- `$C0`, `$CF`, `$D0`, `$D1`, `$C8`, `$C9`, `$CA`, `$CC` and all channel pointers `$0750–$0757` are zero.
- Original frame `$01B5–$01BB` holds saved Y=0, X=`$BB`, A=0, handler status, hardware status, return PC low `$8D`, high `$FE`.
- Hardware saved status is `$A0`, `$A4`, `$A8` or `$AC`, with D matching entry P. Handler status is hardware status OR `$34`, correctly allowing the original interrupted I bit to be either zero or one while the handler has I set.

This is stricter than an arbitrary empty-queue audio tick or an arbitrary RTI. Changing one of these conditions is not permission to approximate the corresponding active branch.

D0=1 returns the bounded completion. D0=-1 rejects unsupported input with all three buffers unchanged. D1–D7/A0–A6 are preserved, native stack is balanced and CCR is scratch. Final context is PC=`$FE8D`, A=0, X=`$BB`, Y=0, SP=`$BB`, with the original reserved byte and architectural saved status preserved.

## Explicit status representation

The native context has canonical B=0/U=1. N/V/D/I/Z/C are restored exactly from the original hardware-saved byte. B is a stack marker rather than a persistent hardware flag.

py65 PLP and RTI expose `popped_status | BREAK | UNUSED`. Consequently the common hardware-saved `$A4` becomes raw oracle P=`$B4` after RTI; all supported raw outputs are `$B0/$B4/$B8/$BC`. This is not treated as an actual flag disagreement.

The test's named `architectural_status_view` creates a comparison view with B clear and U set. It never changes `ref.p` or oracle RAM. It separately asserts raw P against the saved stack byte, and asserts that all seven original saved frame bytes remain unchanged. It compares all other context bytes and all RAM/events without normalization.

For each composed case, the untouched raw oracle context is explicitly rejected by the **unchanged** existing native NMI-prefix guard. The native canonical output is then passed directly to that helper. Separately, a second real `ref.nmi()` is invoked on the untouched raw oracle state: it clears virtual B, sets I, and pushes the correct pre-interrupt architectural status. The test executes the real handler to `$C0BF` and compares complete RAM/context/ordered events and OAM DMA. No context-byte patches are inserted between native helpers and no reference status assignment is used at this follow-on boundary.

## Reproduction and executed coverage

From the project root, with `VASM` naming `vasmm68k_mot` and `py65`/`machine68k` available:

```
python port/tests/recovery_test_silent_tick_rti.py
```

Native machine code is assembled for 68020 and executed in machine68k M68EC020. Temporary assembled binaries are automatically removed. The actual cartridge is hash-checked before use.

Passed:

- 1,024 standalone original-ROM/native cases: all 256 uniform RAM fill bytes plus 768 seeded random RAM states, with guarded startup fields installed, varied saved I/D and reserved byte.
- 256 continuous **nine-helper** reset `$FE24` → dispatch → first task yield → real hardware `nmi()` → bank-3 `$F0` command → first silent tick → bank restore → RTI paths. Native RAM/context pass directly between helpers. The oracle crosses the initial scheduler visit to `$FE8D`, reaches the task, injects NMI at the first task yield, then stops before executing the resumed `$FE8D`. No game-state patches or captured fixtures intervene.
- Complete merged ordered event stream, including 30 mapper publications across the composition and the earlier command's seven APU writes. The silent tail adds no APU write.
- 256 follow-on NMI comparisons from untouched raw oracle state and native canonical output, plus raw virtual-B context rejection by the unchanged prefix.
- 73,694 unsupported-input rejections: every other PC, wrong entry register/status/SP bytes, every unsupported value of each guarded RAM/frame byte, and pointer corruption. The alternate valid saved I bit is deliberately excluded from rejection cases.
- 1,024 completed-boundary inert rejections.
- All 2048 RAM bytes, all eight context bytes, exact journal contents, every ordered event, buffer guards, native register preservation, balanced stack, bounded execution and rejection of unexpected writes.

## Remaining work and limits

The next instruction is scheduler continuation at `$FE8D`; it is not translated by this helper. Active streams/channels, nonzero tempo/envelope branches, counter-wrap double updates, arbitrary queue draining and arbitrary interruption contexts are unsupported. The follow-on NMI proof stops at `$C0BF`; it does not imply a second full silent tick is supported because `$C0` is now 4.

This completes a bounded logical first interrupt, not hardware-timed NMI cadence, full reset hardware warmup, full boot, captured-resource removal, title integration, audible Paula playback, gameplay, frame budget, full PAL speed, target probe coverage or physical-Amiga validation. No ROM extracts, captured states, assets, traces or binaries are included in these new source deliverables.
