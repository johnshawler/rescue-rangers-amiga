# Native music command0E and continuous title loop

This is a separate host-only static 68020 translation extending the frozen title
menu loop. It is new early recovery work, not recovery of missing later gameplay
or audio source. All predecessor sources and the public CHR checkpoint remain
unchanged. No runtime 6502 decoder, extracted cartridge code or cartridge assets
are included in these sources.

## Result and next dependency

The resident composition starts at reset, loads native RAM/context only once,
revalidates the 2318-call command0E checkpoint, and continues without reference
state injection or clearing pending work. It performs 34 command0E calls and
193 genuine title countdowns, taking the timer from 900 to 707. The next boundary
is the untranslated music command01 at PC83A0, still inside the active NMI:

- 7038 native calls, 229 real original-ROM NMIs and 226 completed later audio calls.
- 78580 RAM stores, 6241 PPU events, 2320 mapper writes, 4104 controller events,
  12714 semantic resource reads and 1794 APU writes.
- Complete context: 83A0/01/2B/00/A5/F2/A7.
- Mapper: control1E, CHR0/CHR1=1F/1F, bank3, empty serial shift state.
- The title caller return bytes F7/C5 remain at 01BE/01BF. The bank2 title return
  destination remains saved while music executes in bank3.
- Composite: 26368 bytes, SHA256
  951c4f617ba1b1923cd3f7d3baa9ce88fe7b6714d4c74f3c886a317085d840a5.

Separate Start, Select, Right and Left runs still reach the previously established
A05C or F379 boundaries after 1104 calls, 37 NMIs and two countdowns (timer898).
Actual external pad bytes feed both original controller polling and native
scheduler inputs; RAM/controller state is not injected. These inputs reach their
boundary before command0E, so they are regression checks rather than command0E
reachability evidence.

## Original behavior and translation contract

Entry is PC83A0/A0E with X28..2B. The dispatch at 8473 saves command0E in C4,
calls the original 856E stream fetch, and saves its count operand in C3. The
8023 table dispatch reads 849F/84A0 and transfers to 84F7. These table bytes are
validated against the expected destination before any emulated state is changed.
They are read from the supplied immutable bank, never embedded as a ROM table.

The loop slot is RAM0744+X. Its old value is decremented with binary SBC; if the
old value was zero, the operand replaces the underflow result. A nonzero result
fetches two more stream bytes, first destination high then destination low, and
sets the stream pointer to that destination. A zero result advances the pointer
by two without reading those skipped bytes. A zero operand with a zero counter
therefore takes the skip branch. Final N/Z sometimes come from pointer increment,
not from A; carry and overflow are preserved or replaced at the actual arithmetic
boundaries. Raw D, B and U bits are not normalized.

All page-one wrapped pushes and pops are performed in order: outer call return
83A6, operand-fetch return847B, dispatch return8482, temporary target low byte,
and on the looping branch the fetch returns8533/8538. The outer return reaches
839D through the translated fixed control flow. SP wraps naturally and returns
to its entry value. Stream fetches update C1/C2, Y, pointer low/high and status
exactly as the original. The stream destination is not artificially constrained;
any next unsupported fetch is the next helper's responsibility.

The native helper accepts A0=RAM2048, A1=context8, A2=journal22 and A3=immutable
bank3 (16384 bytes). Context is big-endian PC.word, A/X/Y/rawP/SP/reserved. All
regions, code and native stack must be valid, disjoint and exclusively owned.
The adapter must establish bank3 with stable mapper state. D0 returns 1 on success
or -1 on inert rejection; D1-D7 and A0-A6 are preserved, native SP balances, and
native CCR is scratch. Journal is count.word followed by address.word/value.byte/
kind.byte records, with kind0 for resource reads. Accepted unused journal bytes
are zeroed. Rejected RAM, context and all journal bytes remain unchanged.

Initial stream pointer must be in 8000..BFFF. Looping reads require its next two
bytes to remain in that bank. Pointers BFFE/BFFF are accepted for safe skip cases,
including the zero-counter/zero-operand case; in that last edge case preflight
reads the operand before accepting. Rejection performs only its specified guard
reads. Semantic reads remain separately journaled and ordered with RAM writes.
No APU or mapper writes occur within this helper itself.

## Verification

The ROM-free model describes the counter transition, pointer changes, stack
stores and flags without decoding instruction streams. It crosses all 256
counter values with all 256 operand values, covers every 16-bit stream pointer,
all raw status and SP bytes, all valid channels, explicit bank-edge combinations,
all 65535 wrong PCs, all wrong command/channel values and every incorrect target
byte. The final ROM-free run passes 82167 accepted cases and 116160 inert rejections.
The test checks complete RAM and context, ordered effects, full journals,
validation and semantic resource reads, immutable resources, canaries, native
ABI, stack balance and global access whitelists.

The private differential executes the original cartridge through py65 with an
explicit Ricoh binary ALU. Its inherited SBC and new ADC implementation each
pass 262144 independently expressed full-adder cases (all operands, carry inputs
and both D states). No status bit is cleared or patched to obtain agreement.
All 16384 bank pointers are tested in each of the four channels: 65536 cases,
including eight unsafe edge rejections. The 65528 accepted cases compare original
execution to both the declarative model and assembled native code.

The continuous proof compares full state, ordered effects, resource reads,
mapper snapshots, journals, DMA, ABI and bounds at every native boundary.
The frozen 92-file title-menu manifest and 85-file title-engine manifest were
verified unchanged after development. No existing file, Git index/commit/branch,
publication, asset or ADF is modified.

Reproduction, with VASM set to the approved vasmm68k_mot and PYTHONPATH set to
the inspection dependencies:

```
python port/tests/recovery_test_active_command0e_contract.py
python port/tests/recovery_test_active_command0e_rom.py
python port/tests/recovery_test_resident_command0e_loop.py
MENU_INPUT=16 python port/tests/recovery_test_resident_command0e_loop.py
MENU_INPUT=32 python port/tests/recovery_test_resident_command0e_loop.py
MENU_INPUT=1 python port/tests/recovery_test_resident_command0e_loop.py
MENU_INPUT=2 python port/tests/recovery_test_resident_command0e_loop.py
```

Private Europe cartridge SHA256:
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
Temporary native outputs use temporary directories; Python caches remain ignored.
This proves host-side behavior only, not target Amiga gameplay, audible Paula
output, display correctness, stock-machine speed/memory or complete title timeout.
The next work is command01, not fabricated title readiness. Existing input/menu
resource boundaries and asynchronous-interrupt limitations remain.
