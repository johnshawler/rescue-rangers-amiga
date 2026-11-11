# Genuine SFX27 header initialization and return to the SFX tick

Two additive static 68020 helpers advance the authentic right/left path from
bank3 PC810D through sound-header initialization, both nested RTS returns,
the empty queue check and the next audio-tick entry. The new substantive boundary
is bank3 PC8224, before LDA D3, at the beginning of the SFX stream routine.
No runtime 6502 interpreter, injected cursor/state/queue, skipped sound command,
forced queue clear, new ADF, publication or deployment is involved.

## Covered original instructions

recovery_sfx_header_initialize covers 810D through 814F, ending at 8151 before
RTS when the header is nonzero. It reads the resource at C1/C2 with Y=0, increments
X, writes C4, compares the seven-bit priority with CE, preserves the rejected
priority path, updates CE, conditionally clears D7, initializes D6 from the
header sign, updates D7 on the signed-header path, advances C1/C2 with page carry,
copies the pointer to D0/D1, clears D2..D5, and clears 0727 down through 0700.
The equality condition at 811C uses the preceding CMP result, not the value of A:
STA CE does not change 6502 flags. Zero headers stop at 8152 before music setup.
The last-bank-byte case may advance the stored pointer to C000; no subsequent
resource read is performed. All original ordered RAM writes remain observable.

recovery_sfx_initialized_tail covers 8151 RTS, 80E6 DEC C0, 80E8 RTS,
C0F3 JMP C0DC, C0DC..C0E2 empty-queue check, C0F6 JSR8000, 8000 JMP803A,
803A..804D phase setup, 8052..805D nonbusy/nonzero-pointer path and JSR8224.
It requires C0=1, nonzero D0/D1, DB<8 with the indexed queue entry88, and the
actual wrapped 80E5/C0F2 return frames. These bounded preconditions match the
continuous SFX27 initialization path. It does not translate other busy/phase or
nonempty-queue paths. It consumes both original frames and writes the new
C0F8 and 805F frames in original order. These operations are not a generic RTS
or opcode interpreter. The already-supported tick helpers require a zero SFX
pointer and cannot be reused with the newly initialized AF5C pointer.

## Continuous single-reset results

All four original-ROM and assembled-native executions retain a single RAM/context
initialization, original external controller inputs, scheduler/NMIs, prior music,
full RAM/context and every ordered RAM, PPU, APU, mapper and resource event.

- Right01: cursor88; 1,205 helpers, 41 NMIs, 38 completed later audio returns;
  final context 8224FF0304A4F4A7, mapper (30,31,31,3,()).
- Left02: cursor28; same helper/NMI/audio counts, final context and mapper.
- Neutral00: unchanged 1,219 helpers, 41 NMIs, 39 audio returns;
  A06CFFFFFFA4BDA7, bank2.
- Default confirmation16: unchanged 1,196 helpers, 40 NMIs, 38 audio returns;
  C5F8F800FF27BFA7, bank2.

Both directions read the genuine header0F at AF5B and advance the stream pointer
to AF5C. CE=0F, C0=04, D2..D5=0. The queue remains 03038888888888888888.
The completed header return clears the busy increment, then the next original
tick phase update sets C0=04. The new C0F8/805F return frames remain live at
PC8224. The audio NMI is still incomplete. The exact next unsupported instruction
is 8224 LDA D3; D3=0 leads toward JSR8358 at 822D and genuine stream reading.
No SFX stream command has been decoded here, and no alternate-character
confirmation or fifteen-pair swap is claimed continuously reachable.

Composite: 27,542 bytes; SHA256
077099b2333b6d7fd264e00d0ddc8afc4d6b5830b3222583551384bff5e74de2.

## Contracts and completed verification

Both helpers use A0 RAM2048, A1 raw context8 (PC.word,A,X,Y,P,SP,reserved),
A2 journal, and D0=1 accepted / FFFFFFFF rejected. D1-D7/A0-A6 are preserved;
native SP is balanced; CCR is scratch. Buffers must be valid and disjoint.
The header helper uses A3 immutable bank3[16384] and requires the live bank3
mapping, PC810D, Y=0, and C1/C2 in8000..BFFF. It publishes one original resource
read in journal6 (count.word,address.word,value.byte,zero.byte), with no preflight
resource read. The tail has journal2 containing zero and no resource accesses.
Every raw P/SP value is supported; rejected calls are inert including journals.
All RAM aliases/out-of-bank resource pointers are rejected before resource access.

Passed tests:

- Header: 147,456 declarative cases, 81,920 original-ROM cases and 114,942 inert
  rejections. Covers exhaustive raw P x SP, all16,384 resource offsets, all256x256
  synthetic header/priority pairs, every wrong PC, every nonzero Y and every
  out-of-bank/aliased pointer. Boundary coverage includes page and bank-end
  carry, zero header, priority below/equal/above, header sign, prior D6 sign,
  X wrap, raw reserved status bits and reserved context byte.
- Return/tick tail: 65,536 declarative and 65,536 original-ROM cases, plus
  327,414 inert rejections. Covers exhaustive raw P x SP, all queue indices,
  pointer sign, every wrong PC/C0/queue byte, invalid DB, zero stream pointer,
  and every wrong value in every return-frame byte at every wrapped SP.
- Every accepted comparison checks full RAM/raw context, complete ordered RAM
  and hardware events, journals and tails, actual resource reads/immutability,
  native register ABI, memory read/write whitelists, buffer guards and authentic
  native stack canaries. Bounds tests also deliberately reject invalid accesses.
- Four new continuous runs pass and compare every accepted boundary, mapper
  snapshot, ordered effects and resource accesses. New continuous runner seeds
  native stack canaries before every helper and verifies them afterward.
- Four unchanged predecessor continuous runs pass, preserving their 26,980-byte
  SHA4530c81299c7a6c2bc4799fdcada9a50b2ddf7b11568f2b571daec1d95871706.
- Unchanged predecessor dispatch/dequeue synthetic and ROM tests pass: 8,192
  cases each plus131,869 inert rejections.
- Predecessor manifest SHA1cbabbc4b0c7cc85a5befcd885403fec098c016567970de5150624470e14c227
  and all42 readable entries across existing analysis manifests verify.

Set VASM to the approved vasmm68k_mot and PYTHONPATH to the inspection .deps.
Run recovery_test_sfx_header_initialize.py and recovery_test_sfx_initialized_tail.py,
each with and without --rom. Run recovery_test_resident_sfx_header.py with
CHARACTER_INPUT=0,16,1,2. Frozen checks use recovery_test_pending_sfx27_dispatch.py
with/without --rom and recovery_test_resident_pending_sfx27.py with those four inputs.

Only uniquely named new source/test/report/manifest files were added. Existing
source/tests/docs/manifests, README, aggregate runners, Git/index, checkpoints,
ADFs, deployment destinations and other projects were not changed. No operation
was denied or remains pending. This is host correctness only: not audible Paula,
full gameplay, target execution or stock-speed proof.
