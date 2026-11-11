# Startup video clear through C5BB

This new static 68020 slice continues the verified resident startup at C597.
It executes rendering disable C14E, OAM hiding C21E, game/object memory reset
C61A, startup camera/display fields and the C1BA video clear. It stops at C5BB,
before bank-2 selection. No existing source, helper, target builder/verifier,
aggregate script, README, delivered disk or original input was edited.

## Contract and effects

- `port/src/recovery_startup_video_clear.s`: A0 points to 2048-byte RAM, A1 to
  the eight-byte original context, A2 to a 4382-byte PPU journal. Buffers must
  be valid, disjoint and exclusively owned during invocation.
- Only PC=C597 is accepted. Other entries return D0=-1 without mutating RAM,
  context or journal. Accepted entry returns D0=1. D1-D7/A0-A6 are preserved;
  native stack is balanced; native CCR is scratch. No resource pointer used.
- Each of the four original JSRs writes its real high/low return bytes in
  original order, wrapping within page one. Each matching RTS is completed
  before the next call, preserving incoming SP. No synthetic caller frame.
- Exactly 632 ordered RAM writes and 1095 PPU events. No resource reads,
  mapper writes, controller reads, APU writes or logical NMI are performed.
- Journal format is a big-endian count word then address.word, value.byte,
  kind.byte records. Kind 0 is the PPU status read, kind 1 a register write.
  The unused status-read result is represented as zero in the comparison
  view; private tests vary the actual returned status without changing it.
- C1BA's control write preserves the original increment-mode bit. The helper
  does not silently force increment-one mode or collapse nametable addressing.
  It publishes the original PPU register stream for the caller's PPU adapter.
- Raw status bits are preserved according to original execution: exit P is
  `(entry P & 0x3c) | 2`. A=C0, X=Y=0, PC=C5BB; SP and reserved byte unchanged.
  Private reference uses the existing independently truth-table-tested Ricoh
  CPU from the fade tests. Binary ADC preserves D without temporarily clearing
  or restoring reference P; raw reference status is never patched.

## Validation

`port/tests/recovery_test_startup_video_clear.py` provides a ROM-free
independent domain model, optional `--rom` execution against the hash-checked
private original and native M68EC020 execution. Both accepted suites pass
256 randomized full-RAM cases covering every raw incoming status byte and
all 256 SP values, including wrapped stack writes. The public suite also
passes all 65535 unsupported PCs with inert rejection. Full RAM/context,
ordered RAM/PPU effects, complete journal, preserved registers/native stack,
buffer guards, immutable resource sentinel and global access bounds are checked.

`port/tests/recovery_test_resident_startup_video.py` is a new composition
based on the frozen resident-fade test. It retains that test's original
reset inputs and all boundary assertions, adding the new helper after C597.
Native RAM/context is loaded once, at reset; neither reference state nor
captured assets are injected at later boundaries. The independently running
reference executes the real original instructions continuously.

Resident result: 534 native calls, 18 real reference NMIs, 16 later active
audio calls, 8849 RAM writes, 3620 PPU events, 200 mapper writes, 324 controller
events, 784 semantic resource reads and 114 APU writes. Final context is
C5BB/C0/00/00/26/BF/A7. Mapper remains control1E, CHR0=00, CHR1=10, PRG06 with
an empty serial latch. Original NMI frame/status assertions remain intact.

Standalone helper: 342 bytes, SHA256
a6fec13d9be7da06282061ad21c12b0262c31eb678fc4552f37bc069ab18bf03.

Composite: 21814 bytes, SHA256
48c29fdf257dff19af7b75b94949f86468255c0791b933a8ac0b0af4c367ead7.

Reproduce with the project's approved VASM and inspection PYTHONPATH:

- `python port/tests/recovery_test_startup_video_clear.py`
- `python port/tests/recovery_test_startup_video_clear.py --rom`
- `python port/tests/recovery_test_resident_startup_video.py`

## Genuine next dependencies

At C5BB the original loads bank selector 2 and calls FF53. FF53 has an actual
F6 deferred-audio branch; a future integration must preserve and support that
branch, or explicitly reject unsupported entry before any mutation. It must
not clear F6 to force progress.

C5C0 sets X=2 then calls bank-2 8000. That loader reads indexed pointer tables
at 803D/8047 and then a resource command stream using zero-page 00/01. It
publishes PPU addresses and counted data runs, uses 8037 for indexed-page
crossings and stops on a zero address byte. Implement it with a real bank-2
resource view and validated bounds, not embedded cartridge tables or captured
nametable output. Count termination follows the original signed DEC/BPL
behavior; it is not simply an unsigned generic length convention.

C5C5 then calls bank-2 8820. This copies indexed palette and sprite-table data
into live RAM and requests CHR changes through 1A/1B. It must precede rendering
enable C158, the C5CB yield and fade-in. Those pending CHR requests require real
NMI consumption, alongside any live video/audio queues. Nothing in this new
slice drains or zeroes 18/19/1A/1B/1C/1D to bypass pending work.

This is host-native semantic verification, not target Amiga execution, audible
Paula output, speed evidence, a completed fixture-free title or a delivered
ADF. Logical NMIs remain scheduled at the inherited genuine idle boundaries;
this slice adds no asynchronous hardware interrupt timing claim. Public files
contain no cartridge extracts, captured states, assets or runtime 6502 decoder.
Private original SHA256 remains
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
This slice is included in the private host-test extension. It remains separate
from the 533-call stock-target diagnostic.
