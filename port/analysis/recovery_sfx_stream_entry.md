# Genuine SFX27 stream parameter setup

An additive static 68020 helper advances the genuine right/left single-reset path
from bank3 PC8224 to PC8006, before LDA #00 (duration-scaling multiplication). It reads
AF5C=02, AF5D=01, AF5E=01, sets duration scale D4=01 and raw duration D3=01, leaves D2=00, advances D0/D1
to AF5F, and pushes the authentic8297 return frame for JSR8006. No command was
skipped, queue cleared, or state/cursor injected. The existing805F/C0F8 frames
remain live beneath the new8297 frame. The ongoing audio NMI is not complete.

## Static coverage and contracts

Entry8224 LDA D3 and its nonzero duration path are covered through DEC D3,
DEC D5 and authentic RTS822C to8060, requiring the wrapped805F frame. The zero
duration path covers JSR8358 and the entire fetch subroutine8358..8362, including
LDY0, original resource read, low/high pointer increment and authentic return.
It covers8230 STA C4, ASL A, signed-command branch to8235, LSR C4 and loop-command
branch to8249. Signed commands and loop commands stop BEFORE those unsupported
operations, without claiming their completion. For other commands it executes
optional D4 and D2 fetches, duration fetch into D3/C1, LDA D4/STA C4 and JSR8006.
Repeated fetches are static translated sound-data operations, not a generic
6502 opcode interpreter. Each original JSR stack write remains ordered/visible.

ABI: A0 RAM2048, A1 rawcontext8 (PC.word,A,X,Y,P,SP,reserved), A2 journal18,
A3 immutable bank3[16384]. Caller must provide valid disjoint buffers and live
bank3. D0=1 accepted,FFFFFFFF rejected. D1-D7/A0-A6 and native SP preserved;
CCR scratch. Every raw Ricoh P/SP byte is supported. No decimal-mode arithmetic
is introduced. Journal contains count.word followed by address.word,value.byte,
zero.byte resource entries; untouched journal tail is preserved. No APU event
is emitted by this slice because no translated instruction writes the APU.

Zero-duration calls require pointer8000..BFFC conservatively, allowing all four
possible reads within bank3. BFFD..BFFF are deliberately inert rejections even
when a particular command would need fewer reads. Every other pointer, including
RAM, queue, state, channel, stack and hardware aliases, is rejected before any
resource access or RAM/context/journal write. Nonzero duration requires only its
actual wrapped return frame and does not access resources. Wrong PC or return
frame bytes reject inertly. Resource data is never read as host opcodes.

## Completed validation

- 82,941 independent declarative cases and 82,941 original-ROM comparisons:
  exhaustive raw P x SP (65,536), both duration branches, all256 command bytes,
  all16,381 accepted bank offsets, page crossings, maximum four-byte reads,
  synthetic zero/sign/wrap fields and original stream data. An additional1,024
  bank-tail/all-command cases explicitly cover four reads through BFFF.
- 245,250 inert rejects:65,535 wrong PCs,49,155 invalid/bank-edge pointers,
  and130,560 wrong return bytes (each byte/value at each wrapped SP).
- Each native comparison checks full RAM and raw context, complete ordered RAM
  and resource events, journal tail, exact resource-read addresses, immutable
  bank data, ABI/native stack balance, authentic native stack canaries, buffer
  guards, read/write whitelists and deliberate out-of-bound trace rejection.
- Four continuous single-reset native/original comparisons pass. Right01 and
  Left02:1,206 helpers,41 NMIs,38 completed audio returns, context800601030024F2A7,
  mapper(30,31,31,3,()). The queued request is still genuinely consumed, queue
  03038888888888888888; cursors remain88 and28 respectively. The new slice adds
  19 ordered RAM writes and three resource reads, with no hardware writes.
- Neutral00 remains1,219 helpers/41 NMIs/39 returns, A06CFFFFFFA4BDA7. Default16
  remains1,196 helpers/40 NMIs/38 returns, C5F8F800FF27BFA7. Both remain bank2.
- Four frozen predecessor continuous runs pass unchanged at composite27,542
  bytes SHA077099b2333b6d7fd264e00d0ddc8afc4d6b5830b3222583551384bff5e74de2.
- Frozen header and initialized-tail original-ROM regressions pass81,920 and
  65,536 cases respectively. Frozen declarative regressions also pass147,456
  header cases plus114,942 rejects, and65,536 tail cases plus327,414 rejects.
- All48 readable file entries in prior analysis manifests verify, including the
  approved predecessor manifest94a2d5f1d69d987e51088fd12e17375b659774b8d2d2fa4e550373148ecc7403.

New composite28,016 bytes; SHA256
98b9f24e5c552bb110cd94bee7f8204cab900175c54c6c1bcee4df094fadad50.

Run recovery_test_sfx_stream_entry.py with/without --rom and
recovery_test_resident_sfx_stream_entry.py with CHARACTER_INPUT=0,16,1,2.
Set VASM to the approved vasmm68k_mot and PYTHONPATH to inspection .deps.
Frozen tests use recovery_test_resident_sfx_header.py with the same inputs.

Only uniquely named source, tests, report and manifest were added. Existing
source/docs/tests/manifests, README, aggregate runners, Git/index, ADFs, old
checkpoints, deployment destinations and other projects were not changed.
No denied action, pending permission, or uncertain external side effect.
Host correctness only: no audible Paula, target execution, complete gameplay,
alternate-character confirmation, fifteen-pair swap, or stock-speed claim.

## Synthetic-test portability correction

The reviewed default test originally loaded the private cartridge unnecessarily.
This correction confines cartridge loading/hash verification, private reference
imports and oracle construction to --rom. Default mode calls the separate
synthetic model directly. Native assembly, resident runner and composite bytes
are unchanged; no translation scope has been added.

A fresh source-only tree contains exactly the stream assembly, stream test and
existing header harness. It has no input directory, cartridge, firmware or private
reference test modules. Running the default test there passes82,941 declarative
cases and245,250 inert rejections. This demonstrates that the public synthetic
path does not need the cartridge or private-ROM oracle modules. The existing
external machine68k dependency and approved assembler remain required.
Private --rom validation also passes82,941 cases; all four resident regressions
retain the contexts, counts and composite hash listed above.
