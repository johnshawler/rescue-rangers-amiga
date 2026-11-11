# Phase accumulation and authentic mixed-channel dispatch

This additive static 68020 checkpoint continues the genuine bank 3 sound path
from PC 8060 after channel reconfiguration. It accumulates the binary phase,
pushes the actual saved mask, visits the music side of channel 3, and dispatches
SFX channel 2 with the original nested return address. It does not complete the
pending NMI. This is new recovery development, not restoration of the missing
later playable/gameplay/audio source.

## Native contract

`recovery_sfx_phase_dispatch.s` accepts PC 8060, PC 807A with X in 0..3, or
PC 8085 with a stacked channel in 0..3. Unsupported PCs or channels reject
before modifying RAM, context, journal, or external state. No assumptions about
CF, D0/D1, phase values, caller return address, or raw status bits are imposed.
All 256 emulated stack positions and all raw flags, including D, are supported.
Arithmetic implements the Ricoh binary ADC behavior even when D is set.

A0 addresses 2,048 bytes of RAM, A1 the eight-byte raw context
(PC word, A, X, Y, P, SP, reserved), A2 a 30-byte journal, and A3 the immutable
bank buffer. Buffers must be valid and disjoint. This helper never reads A3 and
has no direct APU, mapper, PPU, controller, or resource effects. Accepted calls
clear only the journal count word; all 28 unused bytes remain unchanged.
D0 returns 1 or FFFFFFFF for inert rejection. D1-D7 and A0-A6 are preserved;
native SP is balanced and CCR is scratch.

The translation covers 8060..80BA and the music-channel entry 8363..8372,
including its empty-channel return at 839C. It publishes genuine semantic
boundaries at 82B0, 8374, or 839D, or the actual popped caller return address.
It never automatically follows a coincidental return-address match. The SFX
call writes the original 8079 frame; the music call writes the original 8084
frame and saved channel. All RAM writes, including dead/wrapped stack stores
and shifts, retain their original order. The binary arithmetic support and
control structure were derived from the frozen active-control translation;
its restrictive CF/D0/D1 and canonical-status preflight was not reused.
There is no generic 6502 interpreter in the production assembly.

## Continuous cartridge evidence

Right and Left each advance from the frozen 1,209-helper checkpoint to
1,214 helpers, 41 NMIs, and 38 completed audio returns. The final raw context is
82B000020427F3A7. The five added invocations are phase dispatch, frozen music
duration preparation, frozen envelope processing, frozen duration progress,
and phase dispatch again. They add 87 ordered RAM writes, 12 resource events,
and 2 APU writes. The new dispatch helper itself contributes nine RAM writes
across its two calls and no resource or hardware effects.

The original C0F8 frame remains at 1F7/1F8. The saved mask is at 1F6 and the
live 8079 frame is at 1F4/1F5. CF is now 01 after genuine channel iteration;
C7 is 02, C8 is F9, C0 is 05, D5 is 01, and D0/D1 is AF60. The frozen music
helper naturally changes C1/C2 to A600. The queue remains
03038888888888888888. Cursor positions remain 88 for Right and 28 for Left.
No native state is loaded from the reference after the one initial reset state.
Original instructions run first, then native results are compared independently.

Neutral remains at A06CFFFFFFA4BDA7 after 1,219 helpers, 41 NMIs and 39 returns.
Confirmation remains at C5F8F800FF27BFA7 after 1,196 helpers, 40 NMIs and
38 returns. All four additive continuous runs and all four frozen immediate
predecessor continuous runs pass. The new continuous harness prints compact
per-helper counts and SHA256 hashes of full RAM, raw context, ordered effects,
and native resource-read traces. Full traces can be reproduced privately from
the hash-verified cartridge; none are embedded in public artifacts.

Standalone native binary: 1,050 bytes, SHA256
cb7e7bee3588c5722827c80af3adaaee02347aa992bdd9b89ac9c08077c9dfab.
Composite: 29,962 bytes, SHA256
98918823d2ea9f5cfed5d6dd7472981af9b94626198be6a35517a01ec0e95fe2.
Frozen predecessor composite: 28,908 bytes, SHA256
45f5bf0ec7395adfaf1d324db22c377f1d65c33cba358b942e6102aa05b43b7b.
All 476 files inventoried before this work remain byte-identical.

## Test scope and reproduction

The standalone suite compares full RAM and raw context, every ordered RAM
write, wrapped stack bytes, resource immutability, absence of resource reads,
journal count and untouched tail, ABI registers, native stack balance and
canaries, buffer guards, and global read/write bounds. Deliberate out-of-range
trace probes must fail. The declarative contract and production assembly are
separate. Private `--rom` mode runs the independent original instructions first
and then checks both the contract and the assembled helper.

The final standalone suite passes 274,433 declarative accepted cases and
194,557 inert rejects. The complete default suite also passes in an isolated
copy containing only the new source/test pair, with cartridge opens and all
private reference imports denied by a Python audit hook. All 274,432 private
accepted cases pass against the original instructions.

Coverage includes every raw P/SP combination for all three entry points,
every pair of low-byte phase operands with high-byte carry edge cases, and
every mask/channel combination across active, empty, and disabled music paths.
Reject coverage exhausts unsupported PCs and every unsupported channel at
every SP for both continuation entries.

Set VASM to an installed `vasmm68k_mot` executable, make `machine68k` available
on PYTHONPATH, and set PYTHONDONTWRITEBYTECODE=1. Run from the repository root:

- `python port/tests/recovery_test_sfx_phase_dispatch.py`
- `python port/tests/recovery_test_sfx_phase_dispatch.py --rom`
- `CHARACTER_INPUT=0 python port/tests/recovery_test_resident_sfx_phase_dispatch.py`
- Repeat the continuous command with CHARACTER_INPUT=16, 1, and 2.
- Run `recovery_test_resident_sfx_channel_reconfigure.py` with the same four inputs.

Default standalone execution uses only the new assembly and Python test and
does not import private reference modules or open the cartridge. The private
mode and continuous suites require `input/rescue-rangers-europe.nes`, SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.

## Remaining boundary

The exact next unsupported instruction is bank 3 PC 82B0, `LDY $0700,X`, with
X=2 in both continuous cursor runs. This starts SFX channel ticking and may
call instrument and envelope processing. The helper does not skip this path or
force the pending sound command or queue to finish. Host correctness is not
proof of target execution, stock A1200 speed, integrated Paula audio,
playability, or full-game completion. No README, aggregate validation script,
Git/index, publication, resource profile, captured RAM, or delivered Z/X ADF
was changed.
