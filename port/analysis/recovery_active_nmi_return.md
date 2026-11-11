# Active NMI return and authentic scheduler resumption

New static 68020 helper `recovery_active_nmi_return.s` implements the actual
straight-line C0F9 through C114 sequence: load saved bank F1, five inline FFF0
mapper writes separated by four accumulator shifts, pop Y/X/A, consume handler
status, then restore original status and PC with RTI. It does not call FF53.
There is **no F6/deferred-audio branch in this original tail**. All F6 values
are accepted and preserved. The helper does not read, clear or execute pending
deferred work; returning with that work still pending matches the original.

The previous startup-only `recovery_silent_tick_rti.s` remains unchanged. No
existing helper, test, probe, builder, aggregate, README or disk is edited.
No publishing is performed.

## Native contract

A0 points to writable 2048-byte original-layout RAM; A1 to eight-byte context
(big-endian PC, A/X/Y/P/SP/reserved); A2 to a 22-byte mapper journal. Buffers,
code and host stack must be valid, disjoint and exclusively owned. D0 returns
1 on success or -1 on inert rejection. D1-D7/A0-A6 are preserved, host stack
balances, native CCR is scratch. Unsupported PC (anything but C0F9) rejects before any buffer mutation, including unused journal bytes.

All incoming register/status bytes, all original stack positions, all saved
frame bytes, and all F1/F5/F6 bytes are supported. The five full mapper data bytes
are F1 shifted right by zero through four positions, not hardcoded bank6.
Each record is address word FFF0, original data byte, live F5 busy byte. The
complete record precedes its count publication. All original RAM remains
unchanged. Seven saved frame bytes are actually read with page-one wrap;
there is no manufactured return address or frame. RTI does not increment PC.
The intermediate handler PLP byte is read, then fully superseded by hardware
frame status. Final A/X/Y, original SP+7 and return PC come from the live frame.

The output status has architectural B=0/U=1; N/V/D/I/Z/C exactly match the
original hardware-saved status. All initial raw status bytes are accepted,
including decimal mode: this tail has no ADC/SBC. The caller's reserved byte
is unchanged.

## Mapper obligations and effects

The eight-byte CPU context does not encode MMC1 state. The caller must supply
fixed bank7 at C000 (PRG mode3), route each journal entry through its live mapper
state, and retain latch/control/bank state across calls. The helper does not
reset a latch or silently switch a resource view. Production code is static
native translation, not an MMC1 or CPU interpreter.

The private standalone adapter verifies all F1 bytes, including bit7 reset
writes, and live partial latches of length zero through four. Bit7 resets the
serial latch and ORs control with 0C; it is never miscounted as a data bit. With
an empty latch and F1<128, five writes commit F1&31. This 128KiB cartridge maps
lower PRG through the low three bank bits; PRG bit4's RAM-enable state is also
retained by the test adapter. An F1 with bit7 set resets the latch on its first
write and leaves four serial bits pending, without committing a new PRG bank.
These are supported exact effects, not a guarantee that arbitrary F1 values
represent a sensible saved bank. A nonempty entry latch is preserved and
advanced honestly. Non-mode3 mapping is outside the caller contract.

In the continuous reset compositions, actual initialization establishes
control=1E, PRG=3 and an empty latch before C0F9; the live saved F1=6 publishes
06,03,01,00,00, yielding bank6 and an empty latch. Both reference and native
journal adapters track every control/CHR/PRG publication in original order.

Host music-chain comparisons carry each exact prior native RAM/context output into the next call by reloading those bytes. This is semantic composition without state patches, not a claim of continuously resident target buffers. Separate live-buffer stage proofs and actual target execution are identified explicitly.

## Verification

Run from project root with VASM pointing at the approved `vasmm68k_mot`, and
PYTHONPATH including the inspection dependencies:

- `python port/tests/test_recovery_active_return_contract.py`
- `python port/tests/recovery_test_active_return_rom.py`
- `python port/tests/recovery_test_active_nmi_runtime_chain.py`

Results:

- 131,072 ROM-free declarative accepted cases: every saved status at every
  stack position, all incoming P, all F1/F5/F6 bytes, and every return PC.
- 65,535 inert rejection cases: every other entry PC.
- 131,072 independent actual-ROM executions, separately matched to native
  execution and the declarative model. The reference permits only original
  instruction-range, F1 and page-one reads and FFF0 writes.
- 256 direct reset chains: all existing 65 calls complete the real active
  initial music tick, then new tail and general scheduler make **67 calls**,
  ending at authentic C2A8.
- 256 idle-boundary reset chains: **68 calls**. After resumed task setup, the
  general scheduler performs an honest no-ready scan at FE8D, returning FE90
  with SP=FF and task zero still waiting. The generalized idle NMI prefix
  enters from FE90, real timer processing readies the task, the full active
  music tick completes with tail SP=F8, live RTI returns to FE90, and the
  scheduler resumes C2A8. No state patches, readiness fabrication, skipped NMI,
  captured context injection or rewritten return frame is used.

Both compositions retain two actual reference `nmi()` calls, complete RAM,
context and ordered event comparisons, immutable resource checks, mapper
state agreement and nested original task frames. Case zero's final native
context is PC=C2A8, A=10, X=10, Y=FF, P=20, SP=BC (hex); controller inputs vary
across the 256 cases. Bank6/control1E/empty latch hold at the continuation.

Native tests execute VASM M68EC020 code in machine68k, preserve ABI registers,
check balanced bounded stack and buffer guards, and whitelist global reads
and writes including deliberate distant/crossing negative checks. Standalone
native RAM reads are checked in exact order: F1, five F5 metadata
reads, then all seven frame bytes. Any native RAM write fails the harness.

The private test uses a named `architectural_rti_status_view` solely for
comparison. The composition retains its named `architectural_status_view`.
Neither changes raw `ref.p`. Raw reference P is independently asserted equal
to hardware-saved byte OR 30, and original saved bytes are checked unchanged.

Private Europe cartridge SHA256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
The assembled helper is **134 bytes**, SHA256:
`5322d77a48eeeebe98630d5eda9c64e7412a24ec953d282b81256ab9b8225688`.
No cartridge data, captured frame, firmware or trace extract is embedded in
these source files. Original input is hash-checked before and after tests.

## Exact next dependency and limits

C2A8's next instruction is PLA, followed by SEC/SBC #1 and the fade-wait
countdown branch. Its actual stacked countdown is 04. This continuation is
not implemented by this tail or these tests. Later repeated active audio
updates still require nonzero-duration/envelope/callback paths and remaining
music command support. General nonempty video queues and deferred mapper/audio
work also remain outside this completed slice.

This is a complete bounded active NMI-to-scheduler integration, including a
real idle-boundary variant, not a complete persistent runtime, full boot or
playable game. No audible-output, game-speed, cycle-accuracy, physical-Amiga,
new ADF or target-probe claim is made.

## Subsequent integrated checkpoint

The helper-local limits above describe this component when introduced. The
[bounded resident runtime target](recovery_runtime_target.md) now verifies the
reset-generated idle/NMI/initial-music/RTI/task-resume path on an emulated
stock PAL A1200. Stage frame-yield compositions remain separate synthetic-entry
proofs. Public and private aggregate scripts include these helper suites.
There is still no complete native gameplay loop, audible output or speed claim.
