# SFX tick entry checkpoint

This is new static native 68020 recovery development from the early source,
not recovery of lost later gameplay/audio source. The target remains a stock
PAL A1200. Host tests make no speed, target-execution, audible-audio, or
playability claim. This deliberately narrow checkpoint is preserved separately
from the subsequent command-mask milestone.

## Contract and implementation

`recovery_sfx_tick_entry.s` accepts bank 3 PC 82B0 or 82C0 with X in 0..3,
any raw status byte, and any wrapped 6502 SP. Other PCs/channels are rejected
before RAM, context, or journal writes. The caller owns valid, disjoint buffers:
A0 RAM 2048, A1 context 8 (PC word, A, X, Y, P, SP, reserved), A2 journal 30,
and A3 immutable bank 3 resource view 16384. D0 returns 1 or FFFFFFFF;
D1-D7/A0-A6 are preserved, native SP is balanced, and CCR is scratch.

The entry reads the channel instrument, optionally executes 867C instrument
pointer preparation with its real 82B7 JSR frame, and branches according to
C0. It stops before the command parser at 82DC or the envelope at 86B2,
leaving the real 82BF frame for the latter. It does not call the frozen music
envelope helper with an unsupported SFX channel. The 82C0 continuation handles
D3/D5 gating, channel-one duration decrement, state gating and 859B completion,
then pops and publishes the actual caller return without following a coincidental
PC match. Binary ADC follows the NES CPU even when the saved decimal bit is set.

Instrument table reads are journaled as resource events. All writes, including
wrapped and dead stack stores, retain their order. Accepted calls overwrite only
the used journal prefix; rejects leave the entire journal unchanged. No APU,
mapper, controller or PPU effects occur. There is no runtime opcode interpreter.

## Evidence

Standalone: 147,456 original-instruction cases, 147,457 declarative cases and
194,558 inert rejects pass. The full declarative/reject suite also passes in an
isolated source/test-only copy with cartridge opens and private reference imports
denied by an audit hook. Tests cover every raw P/SP pair at both entries,
all instrument/control values, duration/flag branches, all unsupported PCs,
and every unsupported X at every SP. They compare full RAM, raw context,
ordered effects, resource reads, journal prefix and untouched tail, immutable
resources/code, register ABI, native stack/canaries, guards and access bounds.

The continuous harness is additive to the frozen phase-dispatch harness.
Right and Left advance from 1,214 to 1,215 helpers, 41 NMIs and 38 completed
returns, reaching 82DC02020025F3A7. The live instrument is empty, so this
particular entry adds no writes or resource events. It does not complete the
pending mixed NMI. The original 8079 and C0F8 frames remain live.
Neutral and confirmation retain their prior 1,219/1,196 helper checkpoints.
All four new continuous inputs and all four frozen phase-dispatch regressions
pass. The continuous comparison normalizes architectural P by clearing B and
setting U; actual stack bytes are never normalized. Standalone comparisons
instead retain every raw P bit, including D/B/U.

Standalone binary: 884 bytes, SHA256
b0d1ffec8d307d1898f99d5807b6e0733930dedbe22303bcd4b64d6afe1a6456.
Composite: 30,850 bytes, SHA256
f5a6e0391238771e8334ca2948cb0672d09dbe7c20c15d03082d4d25098ec7a2.
The preservation inventory verifies all 482 predecessor files unchanged.

## Reproduction

From the repository root, set VASM to an installed vasmm68k_mot executable,
make machine68k available on PYTHONPATH, and set PYTHONDONTWRITEBYTECODE=1.

- `python port/tests/recovery_test_sfx_tick_entry.py`
- `python port/tests/recovery_test_sfx_tick_entry.py --rom`
- `CHARACTER_INPUT=0 python port/tests/recovery_test_resident_sfx_tick_entry.py`
- Repeat the continuous command with CHARACTER_INPUT=16, 1 and 2.
- Repeat all four inputs with recovery_test_resident_sfx_phase_dispatch.py.

Only explicit --rom and continuous tests need the private cartridge,
input/rescue-rangers-europe.nes, SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
No cartridge bytes, extracted resource files or captured RAM are included.
No predecessor, README, aggregate script, Git/index, repository publication,
ADF, or other project was changed. The separate command-mask helper extends
82DC; 86B2 remains unsupported for SFX channels.
