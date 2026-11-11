# Resident title CHR consumption and fade-in

The new static native 68020 composition advances the reviewed C5CB boundary
through the original title yield, genuine CHR-request processing, all ensuing
music and scheduler calls, and title fade-in. It stops at C5D1 before the next
original table initialization. No existing helper, driver, aggregate script,
README, prior manifest, source checkpoint or disk image is changed.

## New native contracts

All helpers require valid, disjoint, exclusively owned RAM (2048 bytes), CPU
context (eight bytes: big-endian PC, A, X, Y, raw P, SP, reserved), journal,
code and native-stack buffers. A0, A1 and A2 identify the first three buffers.
D1–D7/A0–A6 and native stack balance are preserved; native CCR is scratch.
No source embeds cartridge code, captured initialization state or extracted
assets. There is no general runtime CPU interpreter.

- `recovery_title_yield_entry.s`: C5CB -> FF04. Writes the original JSR return
  bytes C5/CD to wrapped page-one addresses and leaves all other game state
  and raw status intact. D0=2 ordered RAM stores, journal size eight bytes.
  Every other PC returns -1 with RAM, context and journal unchanged.
- `recovery_title_fade_entry.s`: C5CE -> C2A5 through C26E. Pushes C5/D0,
  initializes attenuation 30, increment F0, four-frame delay and video enable,
  copies and attenuates the live palette, publishes its genuine request, and
  pushes the delay. D0=72 ordered stores, journal capacity 512 bytes. Binary
  Ricoh subtraction applies even with D set. Every other PC rejects inertly.
  Both helpers use address.word/value.byte/zero.byte records without a count
  header; unused journal bytes remain untouched.
- `recovery_chr_nmi_prefix.s`: logical hardware interrupt from any incoming
  PC through C0BF. Its complete 494-byte mixed mapper/PPU journal contract,
  original wrapped frame, DMA snapshot at +238, raw status and guarded video
  queues are documented in `recovery_chr_nmi_prefix.md`.

The new composition reuses existing scheduler, frame yield, fade continuation,
resource, palette, audio and RTI translations. Command02 dispatch is available
using the reviewed new helper, but the genuine run to C5D1 does not reach it.
It is not invoked speculatively or counted as covered by this composition.

## Public and independent original-ROM tests

`recovery_test_title_fade_yield.py` passes 8192 ROM-free cases and 131070 inert
PC guards. `--rom` independently executes the unmodified cartridge for 8192
cases. Every raw status byte, every SP, wrapped JSR/PHA addresses and all 256
palette input values are represented. Comparisons cover all RAM and context,
ordered RAM stores, complete journal and untouched tail, preserved native
registers, stack balance, buffer canaries and global read/write whitelists.
The reference uses the independently binary-arithmetic-validated Ricoh CPU;
no standalone reference status byte is patched or normalized.

The separate CHR prefix suites exhaust the 65536 ordered request pairs and
exercise skipped video, unsupported queues and exact mapper/PPU/DMA order.
See their report for counts and additional serial-latch coverage.

## Continuous resident proof

`recovery_test_resident_title_chr_fade.py` loads native RAM/context exactly
once at original reset. The native and original machines then proceed
independently through every helper boundary. Two immutable resource banks
are loaded once and remain checked; no reference output is loaded into native
state. Every original NMI frame, RTI, scheduler iteration and audio call is
executed, not simulated by clearing flags or advancing a frame counter.
The inherited composition uses the architectural B/U comparison view for
virtual status bits; it does not patch the original machine or saved frames.

Verified terminal results:

- 1024 native helper calls and 35 real reference NMIs.
- 33 later active audio calls, in addition to bootstrap music processing.
- 16511 ordered RAM writes, 4301 PPU events, 385 mapper writes,
  630 controller events, 2147 semantic resource reads and 252 APU writes.
- Context C5D1/F0/F0/FF/A5/BF/A7; original SP remains BF.
- Mapper control 1E, CHR0=1F, CHR1=1F, PRG02 and an empty serial latch.
- RAM1A=RAM1B=00, RAMF2=RAMF3=1F. Only the original FF1F/FF39 routines
  consume the genuine requests 9F. Each serial sequence is 1F,0F,07,03,01.
- Title fade-in returns naturally with RAM0F=F0. It is not a fabricated
  ready state or an assumed elapsed duration.

Compared with C5CB, this adds 487 helper calls, 17 NMIs, 6436 RAM writes,
326 PPU events,180 mapper writes,306 controller events,867 semantic resource
reads and 138 APU writes. The first new NMI updates both CHR banks while
retaining live mapper history. NMI audio switches PRG to 3 and original RTI
restores PRG 2; neither the adapter nor the test resets the latch.

The composite is 24234 bytes (SHA256
8545e453a1ccb58ba4f60900d752709b6f5a2a8ac50cf4de413c77ea61357637),
with 2048-byte RAM, 8-byte context, the existing maximum 32770-byte journal,
two 16384-byte immutable resource views and native stack. This is a host proof,
not a stock-Amiga allocation design or measured target execution.

## Exact next boundary and limits

At C5D1 the original next operations copy 30 bytes from D657 into 0340, then
30 bytes each from C73F/C75D into 05A0/05D0, set BE/BF=84/03, and call A000
in live bank 2. Those operations are not translated by this work. Nonempty
video queues 19/1C/1D, deferred work, unsupported music commands, callbacks,
and arbitrary asynchronous interrupt placement remain explicit boundaries.
No callback, audio tick, queue, CHR request or pending work is discarded.

Tests require approved VASM and inspection PYTHONPATH. Private tests verify
Europe cartridge SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
No new ADF, target execution, fixture-free displayed title, playability,
real-time performance or audible Paula output is claimed. No commit or
publication is part of this source-only work.
