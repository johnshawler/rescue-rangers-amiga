# State-driven palette NMI and queued music initialization

Additive host-only extension of the frozen first-NMI dispatcher. Starting at
the same declared FE24 boundary, eight continuous original-ROM comparisons now
complete 14 native helpers and two externally supplied logical NMIs. The native
chain reaches C0F3 after command07 initializes music. It stops there: there is
no active music tick, second RTI, subsequent palette fade, title or gameplay
claim. No generic 6502 interpreter or changing sound-stream helper is linked.

## Production design

`port/src/recovery_state_dispatch_palette.s` wraps the unchanged prefix. It
selects pending-palette work only at original PC FE8D with RAM18 nonzero, task
state RAM80=1, supported mapper state, canonical status and the palette helper's
pending-work guards. Event 0 waits inertly; event 1 invokes the frozen palette
NMI helper. The next C0BF boundary uses the existing audio-entry helper and
serial mapper implementation. That helper consumes the real queued command and
publishes five mapper writes. The frozen serial latch applies those writes in
order before another dispatch is possible.

At original PC8003/A07, only mapper control 1E, PRG3 and an empty serial latch
are admitted. The resource address is derived from the live PRG byte masked to
this cartridge's eight physical banks and multiplied by 16KiB. The original
command07 helper reads its count, pointer and channel header from that immutable
view. Other banks, control modes and partially filled latches reject before any
resource read. PRG register aliases that might map to physical bank3 are not
admitted. Arbitrary bank modes are not claimed. CHR registers need not be
restricted because these helpers do not read CHR resources.

C0F3 with RAMC9 nonzero is explicitly unsupported, preserving all state. Other
prefix states enter the frozen dispatcher directly, never by trying candidate
helpers. Production code contains no trace, helper-call schedule, reference
state, test input schedule or step counter. Diagnostic words are output only.

## ABI

All prefix obligations remain, including aligned, valid, disjoint, exclusively
owned RAM/context/journal/runtime buffers and sufficient native stack. A5 adds
a caller-owned immutable contiguous 131,072-byte PRG image, eight 16KiB banks in
physical cartridge order, without the iNES header. It must be disjoint from
writable buffers and native stack/code. The dispatcher cannot validate arbitrary
native pointers, authenticity of caller-supplied data, or concurrent mutation.
These remain caller obligations. Tests of resource pointers concern original
16-bit command-header pointers inside a valid native resource allocation, not
unsafe native addresses.

A0 RAM[2048], A1 context[8], A2 journal[8754], A4 runtime[12]. D0.b/D1.b are
logical pads, D2.l is event 0/1. Runtime tag remains D501. Successful extension
IDs are 11 (454-byte palette journal including 256 DMA bytes) and 12 (30-byte
APU journal). Result D0 is 1 advanced, 0 waiting, or FFFFFFFF unsupported/invalid.
All other D/A registers and exact native SP are preserved; native CCR is scratch.
Rejected/waiting calls do not change mutable buffers or publish effects.

## Reproducible tests

Install requirements-dev.txt and set VASM to the pinned assembler executable.
Then run from the repository root:

```
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_test_state_dispatch_palette_contract.py
python port/tests/recovery_test_state_dispatch_palette_rom.py
python port/tests/recovery_test_state_dispatch_prefix.py
python port/tests/recovery_test_state_dispatch_prefix_independent.py
```

The first test is explicitly PUBLIC and ROM-free: no cartridge file, captured
state, py65 or private comparison results are imported. Invented resource bytes
make all eight banks distinguishable. It verifies 259 successes, 3,687 inert
rejections and 31 delayed palette polls. Music tests cover all 256 original SP
positions, wraparound, varying canonical status/nesting, empty/nonempty channel
headers, both permitted header-pointer endpoints, malformed counts/pointers/
headers, return-frame corruption and wrong event/tag/bank/control/latch values.
Synthetic palette output is checked in full RAM/context, complete journal/DMA
and ordered effects. Music final RAM/context/journal and exact resource read
addresses are checked against the existing ROM-free declarative contract.

The second test is PRIVATE and requires the approved unmodified original ROM.
Its reference selector is separate from native metadata and chooses its own
control flow using original PC/RAM and the external event. The original CPU
executes to its chosen endpoint before native code is called. Neither RAM,
context, original stack nor mapper state is reloaded into a successful chain.
Only journal scratch is cleared and diagnostic output words are poisoned.
All eight runs verify full 2,048-byte RAM, context, complete ordered RAM and
journal effects, complete journals/DMA, serial mapper state and exact immutable
resource reads at every successful boundary. There are 112 total completions,
16 logical NMIs and 1,320 separate inert checkpoint probes. Neutral runs with
zero versus thirteen extra polls at both waits reach the same result. Inputs
also cover Start, Left, Right, Down/Up, A/B on separate pads and all buttons;
only the first controller sample is exercised, not repeated menu actions.
Final context is C0F3/0F/FF/0C/24/B1/A7; mapper is 1E/00/10/03, empty latch.

The shared native harness checks randomized preserved registers, exact stack
return, bounded accesses, buffer guards, unchanged code and all 128KiB resource
bytes on every call. Resource writes are forbidden by the trace. Failed and
waiting calls preserve all mutable state. Machines run sequentially because
machine68k is process-global. Independent repeated assembly matches: 4,982
bytes, SHA256 16101c9b8bc7acf83fa42368812a4a48889ed9cf7dac11c67ce16920533fda4e.

Both frozen prefix test suites pass unchanged: 77 completions each, plus the
independent suite's 21,663 boundary probes and 73 additional original-ROM
status comparisons. With portable setup guidance, the frozen prefix manifest
is SHA256
3021f189d432eff9adfc0c60b8c5601a1f654765e62975a8e92ae6c074cf74c0;
its 3,734-byte composite remains SHA256
834ab65a90c73b38a2b35ff2c13fff495970d844d2c2d235cfeb72a97218a5a5.

## Preservation and limits

This increment adds only the listed source, tests, report, results and manifest.
All 17 frozen dependencies match the extension manifest. Their production and
test bytes remain unchanged. The prefix report's setup guidance was clarified
without code changes, and the manifest records that documentation revision.

The MMC1 bit7-reset branch remains static-review-only, as in the prefix.
This is host M68EC020 logical dispatch evidence, not live Amiga timing,
interrupt adaptation, controls, display, audio output, game completion or speed.
Target execution remains unverified for this state-driven extension.
