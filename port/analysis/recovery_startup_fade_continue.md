# Startup fade continuation and authentic outer yield

New static native helper `port/src/recovery_startup_fade_continue.s` completes
the between-yield fade work at C2A8, including the stacked countdown,
C2AE fade-level arithmetic, the C283 source-palette copy and C28E attenuation,
and the actual C2BD RTS. A second accepted entry, C594, pushes the real C596
return address and stops at FF04 for the unchanged frame-yield helper.

The actual reset-generated startup frame contains countdown04 and caller
C593. With the original scheduler and repeated active NMIs executing in the
independent reference, the continuation takes 16 fade resumes and one outer
yield entry to reach C597/SP=BF. Fade levels advance through 10,20,30,40,50.
The reference executes 16 additional real NMIs and 100 APU writes. No audio
work is skipped and no readiness, stack, return address or raw P is patched.

## Native contract

- A0: writable original-layout RAM[2048].
- A1: eight-byte big-endian PC, A, X, Y, raw P, SP, reserved context.
- A2: writable 512-byte ordered RAM-store journal, records address.w/value.b/zero.b.
- D0: actual journal-record count, or -1 for inert unsupported entry.
- All other D/A registers preserved; native stack balanced; CCR scratch.
- Valid disjoint buffers, native code and stack are caller obligations.
- Accept only C2A8 or C594. Rejections leave RAM/context/journal fully untouched.
- Return at C2A5, the actual popped RTS target, or FF04. No scheduler/audio work
  is silently folded into a continuation. The RTS destination is unrestricted.
- One nonzero countdown writes one stacked byte; expired continuing fade writes
  67 records; expired terminating fade writes one record; C594 writes two.
- Stack accesses wrap within original page one. All raw status bytes, including
  D/B/U, are supported and preserved except original instruction-defined bits.
  Arithmetic is binary Ricoh 2A03 ADC/SBC even when D is set.
- No ROM resource access, runtime opcode decoding, PPU/APU or mapper publication
  occurs in this helper. No mapper state is changed or assumed by its code.

The assembled M68EC020 helper is 416 bytes, SHA256
`40d4153e4227460dc9fe81ce68251759b4a5d3a58b9959f772e9d333ba174b0f`.

## Verification

Set VASM to the approved `vasmm68k_mot` and PYTHONPATH to the inspection `.deps`
directory. Run these new tests independently; no aggregate was changed:

- `python port/tests/test_recovery_startup_fade_alu.py`
- `python port/tests/recovery_test_startup_fade_continue.py`
- `python port/tests/recovery_test_startup_fade_yield_chain.py`

The ALU test proves 262,144 ADC and 262,144 SBC cases against independent
bitwise full-adder truth tables, including both carry inputs and both D values.
It validates the private reference's binary arithmetic adaptation rather than
normalizing reference P around instructions.

The completed main differential run passes **205,824 standalone original-ROM
cases**, **3,490,114 exact ordered RAM stores**, and **65,534 inert rejected PCs**.
Its log is `logs/recovery-startup-fade-continue-final.log`.

The main differential test covers every raw-P/SP pair, every countdown byte,
every pair of fade-advance operands, every palette byte at every source position,
every raw-P/SP pair for C594, and every other PC as an inert rejection.
Every native invocation checks all 2KiB RAM, all eight raw context bytes,
ordered RAM stores, the complete journal including unused tail, ABI, stack,
buffer guards and global native read/write whitelists. The reused harness
also challenges distant and range-crossing accesses. It then checks 17 samples
from continuous reset-origin reference execution through C597, retaining all
actual active audio and genuine NMIs. Raw reference P and saved frames remain
untouched; this suite needs no B/U comparison normalization.

The separate composition test checks 16 live-native-buffer fade+yield pairs
(33 native calls). The first helper's actual output remains in native RAM and
context for the unchanged frame-yield helper; no reload or patch intervenes.
Complete combined ordered stores, RAM, raw contexts and journals match the
continuous reference. Final original bank6/control1E/empty latch are asserted.

The private cartridge is hash-checked before and after tests:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
No ROM bytes, captured frames, raw traces or private resources are embedded in
new source. All generated logs remain under ignored `logs/`.

## Honest boundary

The lifecycle reference executes all intermediate active music; those NMI/audio
intervals are not native in these new tests. Native pairs are independently
seeded at genuine oracle-derived boundaries, never represented as one fully
native reset-to-C597 composition. The separate
[resident startup proof](recovery_resident_startup_fade.md) now provides that
connected native composition with audio, interrupts and scheduling.
These tests do not produce a target disk, rendered title, audible output,
full boot, stage load, playable game or physical-Amiga proof.

The five files described here form a separate helper and its tests. Original
inputs and the delivered ADF remain unchanged. This is new recovery work atop
the early title baseline, not recovery of the missing later gameplay source.
