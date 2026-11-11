# Outer music-channel iteration

The new static 68020 helper `recovery_music_channel_iteration.s` translates
bank3's outer loop from the original PLA at $8085. It handles restoring the
logical channel index, shifting CF, every remaining inactive-channel skip,
C0's channel-suppression flag, and entry into the next active zero-duration
channel. The natural active-channel boundary is $839D, immediately before
the stream fetch JSR. This is deliberately index-general rather than returning
a captured endpoint. The other supported outcome is the original tick RTS,
including the complete CC/CD phase accumulation and saturation tail.

## Contract and boundaries

A0 points to 2,048-byte original-layout RAM; A1 points to the eight-byte
big-endian PC/A/X/Y/P/SP/reserved context. Valid, disjoint, exclusively owned
buffers are required. No A2 journal or A3 resource is used. The helper returns
D0=1 on success or -1 on inert rejection. D1-D7/A0-A6 and context reserved
are preserved, native stack is balanced and CCR is scratch. All RAM writes,
including dead original stack stores, remain byte writes in original order.
There are no resource, APU, PPU, controller or mapper effects in this slice.

Entry requires PC=$8085, canonical P (B clear/U set), D=0, and a stacked
logical channel index 0..3 at page1[(SP+1) modulo256]. Entry A/X/Y, all SPs
and all remaining architectural flags are unrestricted. The stacked index,
not entry X, selects the remaining loop. Success supports remaining logical
channels 2,1,0, producing indexed X=$2A,$29,$28 respectively. CF is shifted
for each completed channel and restored from its saved stack byte at tick
return. Tick RTS pops its actual original stack return address and wraps it
at 16 bits; no caller return address is embedded.

A read-only preflight walks only the remaining relevant channel decisions.
It rejects, before any RAM/context write, a visited CF low-bit callback
($82B0) or an active channel with nonzero duration ($8374 envelope/countdown
path). A channel suppressed by C0 bit1 need not have zero duration. Decisions
after the next active zero-duration channel are outside this call and do not
cause rejection. D=1 is explicitly unsupported because the tail contains
binary NES ADC operations and the generic CPU oracle has decimal arithmetic.

## Executed proof

Tests use VASM -m68020 and machine68k M68EC020. Native machine code is 624
bytes. Every traced native read/write is globally whitelisted, including code,
context, RAM and native stack; deliberately distant reads/writes must reject.
Tests check complete RAM/context, ordered RAM effects, disjoint-buffer guards,
all preserved registers and native stack balance. No runtime opcode decoder
or CPU interpreter exists in the native helper.

- `recovery_test_music_channel_iteration.py`: 16,384 independent actual-ROM
  comparisons, with 12,523 original tick returns and 3,861 next-channel
  fetch boundaries. Reference raw P is not modified. Private Europe cartridge
  SHA256 is `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
- `recovery_test_music_channel_iteration_contract.py`: 16,384 independent
  declarative comparisons without cartridge, 6502 CPU oracle, extracts or
  captured state. Covers all SP values and restored channel indexes,
  architectural flag combinations, skip chains, phase accumulation and
  saturation. Another 66,782 unsupported-input comparisons verify complete
  inert rejection, including every wrong PC, invalid status/index, callback
  branches, and every nonzero active duration.
- `recovery_test_music_channel_iteration_chain.py`: 256 continuous semantic
  reset compositions, now **31 calls to 24 distinct static helpers**, through
  two real reference NMIs. The prior 30 outputs feed the new helper unchanged;
  the reference runs continuously with no RAM or raw-status patches. All
  earlier journals, full RAM/context and original ordered effects compare.
  The new helper traverses 22 original instructions and ends at
  PC=$839D, A=$00, X=$2A, Y=$18, P=$26, SP=$AB, next stream pointer=$A391.
  The nested pending continuation is unchanged. The old X=$2B stream helper
  is explicitly tested to reject this new endpoint inertly.

The chain harness is a new standalone derivative of the previous event-block
proof. Existing tests and shared probes/builders/verifiers remain untouched.
Run each with VASM set to `vasmm68k_mot` and PYTHONPATH including machine68k
and py65 dependencies (py65 is not needed for the declarative test).

## Next dependency

Generalized stream fetch must support X=$28..$2B, using low pointer at
$0728+X, high pointer at $072C+X and the unchanged original fetch semantics
at $856E. The current actual chain needs X=$2A, pointer bytes $0752/$0756.
Its next event is command04, so the following dispatch/command04 path also
needs index-general support at X=$2A; the old X=$2B-only helper cannot be
silently reused. Every further handler must independently validate its
channel indexes and bounded caller-owned bank3 reads. CF callbacks, nonzero
duration/envelope progression and pitched events remain untranslated.

No full music tick from the current reset chain, RTI, audible Paula output,
complete boot/gameplay, physical-hardware execution or performance result is
claimed. This helper's supported isolated no-work cases do complete their
original tick RTS. It has not yet been integrated into a stock-target probe.
Delivered Z/X ADF, originals and old helper implementations are unchanged.
No cartridge, firmware, extract or raw trace is added to public source.

## Subsequent integrated checkpoint

The helper-local limits above describe this component when introduced. The
[bounded resident runtime target](recovery_runtime_target.md) now verifies the
reset-generated idle/NMI/initial-music/RTI/task-resume path on an emulated
stock PAL A1200. Stage frame-yield compositions remain separate synthetic-entry
proofs. Public and private aggregate scripts include these helper suites.
There is still no complete native gameplay loop, audible output or speed claim.
