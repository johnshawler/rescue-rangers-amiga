# State-driven first active music tick and NMI return

This additive host-only dispatcher completes the first active music tick and
returns through the original NMI frame. Eight continuous original-ROM runs each
advance 66 native helpers from FE24, including two externally supplied logical
NMIs. Final context is FE8D/00/B8/00/A4/B8/A7 and the live mapper is
1E/00/10/06 with an empty serial latch. The preceding palette/music-initialization
dispatcher and every linked helper remain unchanged.

## Production control and scope

`port/src/recovery_state_dispatch_active.s` selects semantic helpers from the
original PC, RAM, music command byte and original stack. It does not use a
schedule, diagnostic result words, call count, captured state, CPU oracle,
speculative helper trials or a generic 6502 opcode interpreter.

The extension admits C0F3 with nonzero RAM C9 for first active-channel fetch,
839D for indexed stream fetch, 83A0 for supported music commands/rests/pitched
notes, 83FD for pitched-note completion, 8085 for outer-channel iteration and
C0F9 for NMI return. At 83A0, bytes below 20 select the frozen bounded music
command dispatcher (04/05/06/07/08/09/18); bytes at least 20 select rest versus
pitched duration by their low five bits. This is music-data dispatch.

All new operations require event zero, ABI tag D501, control 1E, exact PRG3 and
an empty serial latch. The bank view is derived from the live PRG register and
the immutable eight-bank image. Aliases such as PRG11 are rejected. The frozen
helpers independently validate their canonical status, channel, stream-pointer,
queue, duration and command-table obligations before mutation. Preflight reads
of valid immutable resources may occur on rejected calls; journals and mutable
state remain unchanged.

Rest and pitched-note completion require the original channel return frame
8084. Outer iteration requires its original tick return frame C0F8. The return
adapter requires saved FE8D, RAM F1=6 and task state RAM80=4. These are explicit
bounds, not a claim to support arbitrary interrupt nesting or arbitrary
caller frames. All page-one frame reads wrap at byte SP. Return status is
restored from the saved frame with canonical B=0/U=1; other status bits are
retained. The five real FFF0 mapper writes are consumed by serial-latch logic
before dispatch returns. No expected-bank assignment substitutes for them.

## ABI

The palette ABI is unchanged: A0 RAM[2048], A1 context[8], A2 journal[8754],
A4 runtime[12], A5 immutable contiguous PRG[131072] without the iNES header.
D0.b/D1.b carry external logical pads; D2.l is the logical event. D0 result is
1 advanced, 0 waiting, or FFFFFFFF unsupported/invalid. D1-D7/A0-A6 and exact
native SP are preserved; native CCR is scratch. All pointers must identify
valid aligned, disjoint, exclusively owned allocations, with sufficient native
stack and immutable resources. Unsafe native pointers and concurrent mutation
cannot be validated by this interface. Pointer rejection tests concern original
16-bit resource addresses within valid native allocations.

New diagnostic IDs and journal sizes are: 13 tick fetch/6 bytes, 14 indexed
fetch/6, 15 indexed commands/22, 16 rest/10, 17 pitched gate/10, 18 pitched
note/18, 19 outer iteration/0 and 20 NMI return/22. Diagnostics are outputs only.
Old states enter the frozen palette dispatcher directly.

## Verification

Set VASM to a working vasmm68k_mot executable and make machine68k and py65
available to Python. From the repository root, with bytecode writes disabled:

```
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_test_state_dispatch_active_contract.py
python port/tests/recovery_test_state_dispatch_active_rom.py
python port/tests/recovery_test_state_dispatch_palette_contract.py
python port/tests/recovery_test_state_dispatch_palette_rom.py
python port/tests/recovery_test_state_dispatch_prefix.py
python port/tests/recovery_test_state_dispatch_prefix_independent.py
```

The explicitly PUBLIC synthetic suite imports no ROM, py65 or private oracle.
Invented bytes distinguish all eight resource banks. It checks 4,608 successful
transitions: 1,024 indexed command/fetch/rest cases, 1,024 pitched gates, 1,024
pitched notes, 256 tick fetches, 1,024 outer iterations and 256 RTIs. The
populations cover all four channels and all 256 original SP values, including
wraparound. Full RAM, context, ordered RAM/resource/mapper events, full journals,
exact immutable resource reads, live mapper state and diagnostic outputs are
compared with independent declarative contracts. It also tests malformed
command tables, unsupported commands/channels, stream and instrument pointers,
queue/duration/callback state, original frames, saved notes, tags, events,
canonical statuses, and every unsupported PRG/control byte at each new boundary.
The exact final rejection count is recorded in the adjacent results JSON.

The PRIVATE suite checks the approved original ROM hash before use. Its
separate selector uses only original CPU/RAM and the external event, and the
original CPU completes its chosen operation before the native invocation.
Successful chains never reload RAM, context, original stack or mapper state
from the reference. Only journal scratch is cleared and output diagnostics are
poisoned between calls. All 528 completions match full RAM/context, complete
ordered effects (including inherited PPU/DMA, APU and controller effects),
complete journals, real serial mapper state and exact resource reads. The
music tick itself has no additional APU-register writes on this first tick;
this is not an audible-audio result. There are 16 external NMIs, 5,400 separate
checkpoint rejection probes and eight additional inert terminal calls.

Neutral zero-delay and thirteen-extra-poll runs agree. Six further runs vary
Start, Left, Right, Down/Up, A/B on separate pads and all buttons, with varied
NMI delays. This covers the initial controller sample, not repeated menu input.
The harness checks randomized preserved native registers, exact native stack
return, bounded accesses, buffer guards, unchanged code and all 128KiB of
immutable resources on every call. Native machines run sequentially within
each process. Repeated assembly is identical: 9,984 bytes, SHA256
8f8942bf41426a6efd42e36c1338336db3705a054ff20d305bf1413307a1cc7d.

Both palette regressions pass unchanged: 259 synthetic successes, 3,687 inert
rejections, 31 delayed polls and eight private runs with 14 completions each.
Both frozen prefix suites pass unchanged with 77 completions each; the
independent suite also passes 21,663 boundary probes and 73 additional original
status comparisons. The dependency manifest includes the palette's current
documentation revision, SHA256
1224964117c97eb637d6d552fecb650bfa8f05dc671aaca42adf7fb45f5c24ca.

## Remaining boundary and preservation

After the completed RTI, an event-zero invocation at FE8D rejects inertly.
The frozen first-resume helper requires X/SP=BB and the C584 task frame;
this real continuation has X/SP=B8 and resumes C2A8 instead. A reference-only
check after completion independently follows that scheduler operation to C2A8
in 192 or 196 original instructions. General scheduler continuation is not
linked by this extension. Subsequent active ticks, duration/envelope updates,
palette fades, title flow and gameplay remain outside this dispatcher.

The manifest records the seven source, test and evidence-summary payloads plus
40 frozen dependencies. The dependency set preserves the previously validated
palette, prefix and semantic helpers. The serial mapper bit7-reset branch remains
static-review-only because admitted return writes never exercise it.

This is new source development on the recovered baseline. Later missing gameplay
and audio source remains unrecovered, and the delivered Z/X ADF is unchanged.
Verification is host M68EC020 logical execution only, not live Amiga interrupt
timing, controls, display, audible sound, FPS or target hardware/emulator validation.
