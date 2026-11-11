# SFX event action and genuine NMI return

This is new native 68020 recovery development, not recovery of the lost later
playable/audio source. The preferred target remains a stock PAL A1200. These
are host correctness results, not target execution, speed, audible Paula audio,
playability, or full-game completion claims. The delivered Z/X disk is unchanged.

## Coherent checkpoint

Both Right and Left now execute their real SFX event, return to the original
807A caller, process the remaining music channels with frozen helpers, and
complete the pending mixed NMI through its genuine C0F8 frame and RTI. They end
at FE9000100026FFA7 after 1,231 helpers, 41 NMIs and 39 completed audio returns,
with mapper bank 2 restored. No reference state is injected into this chain.

The new helper alone advances 831B3A023A25F3A7 to 807A20020424F5A7, adding
16 ordered RAM writes and three resource reads. It performs real gate-duration,
pitch-register and instrument-restart state changes. This nonzero event makes
no direct APU write. Completing the remaining channels and NMI adds, relative
to the parser checkpoint, 123 RAM writes, 28 resource events, five mapper writes
and four APU writes in total. Those four APU writes come from the frozen music
helpers; they are not claimed as an audible SFX implementation.

Neutral remains A06CFFFFFFA4BDA7 after 1,219 helpers / 41 NMIs / 39 returns.
Confirmation remains C5F8F800FF27BFA7 after 1,196 helpers / 40 NMIs / 38 returns.
All four new continuous cases and all twelve frozen parser, tick-entry and
phase-dispatch continuous regressions pass.

## Native helper contract

The new static helper accepts bank 3 entry PC 830B or 831B with X in 0..3.
A0 addresses 2,048 bytes of RAM, A1 the eight-byte raw CPU context, A2 a 14-byte
journal, and A3 an immutable 16,384-byte bank 3 resource view. These valid
buffers must be disjoint and exclusively owned. D0 returns 1 on success or
FFFFFFFF on inert rejection. D1-D7/A0-A6 and native SP are preserved; native
CCR is scratch. The reserved context byte is unchanged.

Unsupported PCs or channels are rejected before writes. At 831B with a
nonnegative Y, preflight checks that the effective 16-bit wrapped C5/C6 + 4
instrument read lies in 8000..BFFF. Other event paths do not read that pointer.
Pitch reads are bounded by the original clamp and SFX channel range. Preflight
makes no physical resource reads. Unsupported requests leave RAM, context and
the whole journal untouched. Source branch 85E2 is always taken after CPX 28
because preflight established X <= 3; its unreachable fallthrough is not an
accepted execution path.

The translation covers the zero-event action 830B..8318 and its 80BB..80CE
silencing/RTS tail, nonzero action 831B..8357, gate helper 85A6..85D5 including
its complete 8006..8022 multiply, SFX pitch path 85D6..85E2 and 8622..863A,
and restart/RTS paths 863C..8651. It does not execute the music-only 85E4..8621
path. It is fixed native control flow, not a generic 6502 interpreter.

Every JSR, saved event byte, wrapped-stack push/pop and final RTS is preserved.
The final return address is read from the real emulated stack and published;
it is never inferred from a coincidental PC or replaced with a predetermined
caller. Helpers called internally are completely translated and tested. Binary
NES arithmetic is used even with raw D set. Raw B/U/D bits are not normalized
by standalone tests. Continuous tests retain the frozen architectural B/U
comparison convention without altering real stack bytes.

Nonnegative events perform the real duration/gate setup, note clamp and pitch
resource lookup, then inspect the instrument restart byte. Negative events
follow their actual channel-specific gate/restart path. Zero events perform
the actual channel-control update and one journaled APU silencing write.
No envelope is bypassed: this event slice does not call 86B2. SFX envelope
86B2 remains explicitly unsupported, and the continuous test stops rather than
invoking the frozen music envelope with an SFX channel.

The journal contains a big-endian count followed by four-byte records:
address word, value byte, and kind byte (0 resource, 1 APU). At most three
records are used. The entire unused journal tail is preserved. This slice
consumes no event-stream bytes; parser stream-end checks remain in the frozen
predecessor and its regression suite.

## Verification

The standalone suite passes 77,825 accepted cases and 114,938 inert rejects,
both declaratively and against independently executed original instructions.
Original instructions run first and stop at the executed final RTS instruction,
not at a destination predicted by the native or declarative implementation.
The default source/test pair also passes unchanged in a two-file isolated copy
with cartridge opens and private-reference imports denied.

Coverage includes every raw P/SP pair, every event byte and SFX channel,
wrapped stack boundaries, coincidental return addresses matching internal PCs,
page crossing, effective pointer bank limits, every unsupported PC/channel,
and every out-of-bank effective instrument pointer. The harness checks full
RAM and raw context, ordered RAM/resource/APU effects, complete journals and
untouched tails, exact resource read sequence, immutable resource/code bytes,
native registers/SP/canaries, buffer guards and global access whitelists.
Deliberate out-of-range trace probes must fail. There are no mapper effects
inside the new helper. The continuous harness verifies mapper effects and
remaining hardware effects across the complete chain.

The source-only suite requires machine68k and an installed vasmm68k_mot.
From the repository root, set VASM to that executable, make machine68k available
on PYTHONPATH, and set PYTHONDONTWRITEBYTECODE=1. Run:

- `python port/tests/recovery_test_sfx_event_action.py`
- `python port/tests/recovery_test_sfx_event_action.py --rom`
- `CHARACTER_INPUT=0 python port/tests/recovery_test_resident_sfx_event_action.py`
- Repeat with CHARACTER_INPUT=16, 1 and 2.
- `CHARACTER_INPUT=1 NEXT_TICK_BOUNDARY=1 python port/tests/recovery_test_resident_sfx_event_action.py`
- Repeat the next-tick probe with CHARACTER_INPUT=2.
- Repeat inputs 0, 16, 1 and 2 for recovery_test_resident_sfx_command_mask.py,
  recovery_test_resident_sfx_tick_entry.py and recovery_test_resident_sfx_phase_dispatch.py.

Only explicit --rom and continuous tests need private
input/rescue-rangers-europe.nes, SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
For isolation, copy only the new .s and standalone .py files into corresponding
port/src and port/tests folders outside the project. Execute the copied test
as main under an audit hook denying .nes or /input/ opens and imports beginning
recovery_test_, recovery_music_ or verify_recovery_.

PRIVATE_TRACE_DIR optionally writes full comparison traces for helpers 64..66
outside this project; an in-project destination is rejected. These private
traces are not public artifacts and are never inputs to the successful chain.
The helper-66 full RAM/context/effect/read trace hashes are
93f85448996dc83dbae3dc2e9a82a88c51f619272a093ab647b4edb2d7a18a77 (Right)
and 966d587f79dcc4c581e2189b7f76d8769a2f0b744cc2a143c8008445ae6e2544 (Left).

Standalone binary: 1,876 bytes, SHA256
0e1a928c5f69c08d578e297b6f4f7768d154797a975cfe0a1830f8421ed78eb7.
Composite: 34,442 bytes, SHA256
a7b58a5eb95852f549d7ae1c834e7735792ff0bda9776ea479203b1fc0648891.

## Exact remaining boundary

The normal milestone deliberately stops immediately after the verified mixed
NMI return at FE90. An additional uninterrupted next-tick probe resumes the
scheduler, enters the next NMI, and reaches fixed-bank PC C0F6, with raw
context C0F688030027F8A7 and PRG bank 3 selected at 8000..BFFF, after
1,238 helpers, 42 NMIs and 39 completed returns. The frozen music-only control
helper is called there and proven to reject atomically because SFX state is
active. This is the next unsupported dispatch entry. Original code would execute
C0F6 JSR $8000, then 8000 JMP $803A, and finally 805D JSR $8224 when active
SFX applies. No original instruction beyond that native
boundary is smuggled into the successful chain. SFX envelope 86B2 is a separate
remaining unsupported routine, not the next boundary reached by this probe.

The frozen inventory verifies 737 predecessor files unchanged. The delivered
ADF is unchanged. Public artifacts contain no cartridge/firmware byte arrays,
extracted assets, captured RAM or music profiles.
