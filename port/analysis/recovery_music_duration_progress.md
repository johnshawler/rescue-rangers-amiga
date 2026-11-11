# Repeated-tick channel duration preparation and progression

Two new static 68020 helpers translate the instrument preparation and duration
bookkeeping around the nonzero-duration envelope callback. They do not execute
6502 opcodes or include cartridge data. Existing helpers and shared scripts are
unchanged. These helpers do not themselves produce a disk or audible output.

## Interfaces and natural boundaries

Both accept A0 pointing at 2048 bytes of original RAM and A1 at the eight-byte
canonical CPU context. X must be $28–$2B and P must have U=1, B=0, D=0.
D0 returns 1 on success and -1 on inert rejection. D1–D7/A0–A6 are preserved,
native stack is balanced, CCR is scratch, and context reserved is preserved.
Buffers must be valid, owned, and disjoint. All original RAM stores remain
ordered byte writes, including overwritten original stack locations.

- `recovery_music_duration_prepare.s`: PC=$8374. A2 is a ten-byte resource
  journal, A3 an immutable 16KiB bank3 resource view. With a zero instrument at
  $0700+X it exits at $837F without resource reads, preserving A and producing
  the original LDY flags. Otherwise it executes the original instrument-index
  multiply/address setup and stops at $86B2, with the real $837E return frame
  on the original stack. Both original JSR frames and page-one wrapping are
  retained. Semantic reads are $8A02 then $8A01. Every table-byte value is
  accepted, including address carry and overflow. The journal uses count word
  then address-word/value-byte/zero-kind records, and unused records are zero.
- `recovery_music_duration_progress.s`: PC=$837F, after the envelope callback.
  Subtracts tempo from gate and duration, performs original gate-expiry flag
  update and its JSR stack stores when needed. It exits at $839D to fetch the
  next event on duration zero/underflow, otherwise consumes the real original
  return address at $839C. Y is preserved; no instrument state is restricted.
  It uses neither resources nor a journal and emits no hardware effects.

These are standalone bounded channel slices, not proof of repeated complete
music ticks. The intervening $86B2 envelope/APU callback is a separate required
translation. The separate [resident startup proof](recovery_resident_startup_fade.md)
now connects these helpers with authentic task and interrupt continuation. The helper does not skip an unknown callback,
clear pending audio, modify readiness, or manufacture a return destination.

## Verification

Four new tests assemble with VASM -m68020 and execute M68EC020 machine code:

- `recovery_test_music_duration_progress_contract.py`: 65,536 ROM-free
  transitions, exhaustively pairing all duration bytes and tempo bytes, with
  all four channel indexes, original SP values, and varied gate expiry.
  66,011 inert wrong-PC/status/index comparisons.
- `recovery_test_music_duration_progress_rom.py`: 65,536 independent original
  ROM executions, compared separately against declarative and native results.
- `recovery_test_music_duration_prepare_contract.py`: 65,536 ROM-free cases,
  all instrument bytes and all stack positions, varied channels/status, all
  pairs of table bytes, plus 66,011 inert guard comparisons.
- `recovery_test_music_duration_prepare_rom.py`: 65,536 independent original
  ROM instrument setups, separately compared with declarative/native results.

Comparisons cover complete RAM/context, ordered original RAM/resource effects,
resource immutability, full journal, preserved native registers, balanced native
stack, guard bytes, and a global native read/write whitelist. Deliberate distant
access probes verify the whitelist. Invalid entries preserve all caller buffers.
There are no resource or hardware effects in the duration-progress slice.

Private Europe ROM SHA256:
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
Both ROM tests recheck this input hash after execution. No trace or ROM extract
is emitted into public source. The tests use their own generated initial state
and do not assert reset/frame continuity.

Frozen binaries:

- Progress: 288 bytes, SHA256
  56a95900a05e1698bee53be8804a7cbb6a4a04f6f5aade53379aed02340c2fd1.
- Prepare: 358 bytes, SHA256
  fdcd8be0a20d0aaaa68c5a715338b06ac8b6e5e2e087c815752ad627185df3fa.

Run with VASM pointing at the approved vasmm68k_mot and PYTHONPATH containing
machine68k and py65. The two contract suites do not import py65 or need a ROM.
