# State-driven native dispatcher: first-NMI prefix

This additive foundation runs 11 frozen static 68020 helpers from the declared
FE24/Y=0 boundary after original hardware warmup. It is not a complete title or
character dispatcher. It stops safely at the next FE8D palette-delay yield with
RAM18=FF, before the second logical NMI or scheduler scan. No existing helper,
test, report, manifest, README, aggregate, disk or deployment was edited.

## Production decisions

`port/src/recovery_state_dispatch_prefix.s` contains the production dispatcher.
Every decision uses current original PC, RAM, real mapper state or the external
logical event argument. There is no step counter, saved trace, expected context,
oracle result, scripted input schedule or target 6502 opcode decoder. Each PC
selects one helper; no speculative candidate is tried. The existing helper's
own guard rejects before game-state/journal mutation.

At FE8D, task state 1 and no pending palette work waits for an explicit NMI;
task state 4 selects the first scheduler resume. The subsequent palette work
is deliberately unsupported. No IRQ, asynchronous event or physical raster
adaptation is inferred. A caller may hold the logical NMI event until ready;
a successful event step consumes it, and rejected events remain caller-owned.

MMC1 state is native and persistent. The reset, audio-entry and silent-return
mapper journals are consumed by a native serial latch in original record order.
No expected bank is written into the mapper. Journal application finishes before
the dispatcher returns, so the next helper cannot run against stale mapper
state. Within these helpers no cartridge resources are read. Mapper effects are
journaled at their original effect positions and applied synchronously after
the helper; there is no concurrent physical bus backend. No resource-reading
helper is admitted, so immutable-bank resource selection is still future work.

## ABI and obligations

- A0: disjoint writable original RAM, 2,048 bytes.
- A1: disjoint canonical original context, 8 bytes (PC/A/X/Y/P/SP/reserved).
- A2: disjoint journal scratch, 8,754 bytes. Caller may clear this output buffer.
- A4: disjoint runtime, 12 bytes. Bytes 0..5 are MMC1 control/CHR0/CHR1/PRG/
  latch value/latch count. Words 6/8 are last helper ID/journal length, diagnostic
  outputs only. Word 10 is ABI tag D501.
- Initial runtime bytes: 0C 00 00 03 00 00 FF FF 00 00 D5 01. This is the
  declared empty-latch, fixed-last mapper obligation, not a full NES reset.
- D0.b/D1.b: decoded logical pads, A/B/Select/Start/Up/Down/Left/Right in bits 7..0.
- D2.l: 0 advance, 1 logical NMI. Other values reject inertly.
- D0 result: 1 advanced, 0 waiting, FFFFFFFF unsupported or invalid. All other
  D/A registers and exact native SP are preserved; native CCR is scratch.

Pointers must be aligned, valid, disjoint and exclusively owned with sufficient
native stack. Arbitrary invalid pointers are not safely discoverable by this
routine; these are caller obligations, not claimed runtime validation.
Unsupported/waiting returns preserve RAM, context, runtime and journal. Native
scratch-stack writes are permitted. Diagnostic words are deliberately poisoned
before each successful test step to prove they cannot carry a call schedule.

## Verification

Install requirements-dev.txt and set VASM to the pinned assembler executable.
Then run from the repository root:

```
PYTHONDONTWRITEBYTECODE=1 \
python port/tests/recovery_test_state_dispatch_prefix.py
```

The cartridge bus oracle is a separate test-only module with no native,
declarative-game-state or schedule imports. Unmodified approved ROM executes
continuously under py65, starting once at FE24. Native code starts once from
the same declared boundary. No successful-chain RAM, context, original stack or
mapper reload occurs. Before each native dispatch, a separate oracle selector chooses the expected
status, helper and reference endpoint using only the original PC/RAM and the
external event. Native helper metadata is asserted afterward and cannot select
reference flow. The independent regression additionally executes each original
slice before invoking native dispatch. Original status is untouched;
comparison canonicalizes B=0/U=1, while original saved-frame RAM matches exactly.

Seven independent runs cover neutral, Start, Left, Right, Down/Up on separate
pads and all-buttons inputs. Each reaches 11 helper completions and one logical
NMI with every 2,048-byte RAM boundary, context, combined ordered RAM/journal
effects, complete journal, 256 DMA bytes and serial mapper state equal. Neutral
runs with zero versus seven extra idle polls demonstrate that waiting does not
advance state. Register preservation is randomized on every invocation. Native
accesses are globally bounded; code and buffer guards remain unchanged.

Separate sequential machines run adversarial checkpoint fixtures after the
successful chain. Wrong PC/bank/control, nonempty latch, wrong ABI tag,
unsupported event values, wrong-boundary NMI, canonical-status and helper guards
all reject without changing buffers or emitting effects. The terminal second
NMI also rejects inertly. These fixtures do not replace the resident chain.
The machine68k core is process-global, so simultaneous machines are not used.
Two independent assemblies match.

`port/tests/recovery_test_state_dispatch_prefix_independent.py` makes the
separate review's exhaustive regression durable. Run it with the same environment
as the command above. Its seven continuous reference-selected runs cover another
77 completions, including A/B input on separate pads. Thirteen delayed polls at
each first-NMI wait are inert. It adds 21,663 boundary probes: 108 invalid event
values, 11 unexpected NMIs, 12,240 exhaustive mapper/control/nonempty-latch
variants, 6,240 unsupported PC variants, 1,024 exhaustive P-byte variants and
2,040 nonzero pending-queue variants. The P-byte probes include accepted cases;
they are not all rejection tests. Every rejected case preserves all buffers and
emits no effects. Another 73 admitted P-byte variants match independent original
ROM execution in full RAM/context and ordered effects. The test verifies all
59 prior confirmation-build dependency hashes without using the new manifest
as a source of expected game state. Results are in the adjacent independent
results JSON.

The MMC1 bit-7 serial-reset branch remains statically reviewed only. Admitted
prefix helpers never publish a bit-7 mapper write, and the dispatcher has no
public raw-journal execution entry. These tests do not claim dynamic coverage
of that internal branch or of arbitrary mapper-journal execution. Composite length is 3,734 bytes; SHA256 is
834ab65a90c73b38a2b35ff2c13fff495970d844d2c2d235cfeb72a97218a5a5.

Final original context is FE8D/00/B8/00/A4/B8/A7. Mapper is 1E/00/10/06 with
empty latch. Exact counts and input cases are in the adjacent results JSON.

## Explicit remaining coverage

This prefix does not reach title, character choice, confirmation, scene entry,
SFX, repeated controller release/repress sampling or the 900-count timeout.
Direction inputs are verified at the first poll only, not as menu actions.
The next extension needs state-driven general scheduling, palette/idle/CHR NMI
selection, active music dispatch and bank-resource selection, followed by title
and character helpers. The reviewed helper chains do not by themselves establish
that broader dispatch coverage. No new changing SFX stream code is linked.

This is host M68EC020 evidence only. No ADF, emulated Amiga target, live control,
physical hardware, display, audible output, FPS or game-completion claim is made.
