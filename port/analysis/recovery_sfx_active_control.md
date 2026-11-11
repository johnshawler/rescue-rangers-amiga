# Active SFX control continuation

This additive host-only native 68020 checkpoint advances the continuously running
reset history through the next active-SFX interrupt, stopping before the first
unqualified SFX envelope call. It is new recovery development from early source,
not recovery of a lost later playable implementation.

## Result and exact boundary

Right and Left both advance from C0F688030027F8A7 to 86B204021324F1A7,
with 1,246 successful helpers, 42 NMIs entered, and 39 genuine completed audio
returns. Bank 3 remains selected. The first mixed NMI completed in the frozen
predecessor; the following mixed NMI is **not complete** here.

The new helper executes the original C0F6 JSR, 8000 dispatch, phase update,
and 805D JSR, publishing 8224EF0308A4F4A7 after six ordered RAM writes.
The frozen stream helper then genuinely decrements D3 and D5 from one to zero
and consumes the 805F frame, returning 806001030826F6A7. It does not clear
queues or fabricate a return. Valid phase, music duration, music envelope,
duration progression, phase, and SFX tick helpers follow. The final tick helper
performs the instrument-pointer reads and authentic JSR to 86B2 for channel 2.
The eight successful helpers after the former boundary are
67, 60, 63, 33, 34, 35, 63, 64. They produce 123 ordered effects in total.

Neutral and confirm remain at their prior boundaries: 1,219 helpers / 41 NMIs /
39 returns / A06CFFFFFFA4BDA7, and 1,196 helpers / 40 NMIs / 38 returns /
C5F8F800FF27BFA7 respectively. All four histories begin at reset and initialize
native RAM/context once. The original CPU runs first for every successful
continuation; its result is compared, never injected into native state.

## Native contract

`recovery_sfx_active_control.s` accepts PC C0F6 or 8052, every raw status byte,
and every stack pointer. A0 addresses 2,048 RAM bytes; A1 addresses eight context
bytes; A2 addresses a two-byte journal. The buffers must be valid and disjoint.
Bank 3 must already be selected at 8000–BFFF. There are no resource, APU, or
mapper accesses in this helper. The composite verifies mapper state externally.
Unsupported PCs reject before any write, returning D0 = -1. Successful calls
return D0 = 1, clear only the journal count, and preserve D1–D7/A0–A6.

The C0 phase update uses NES binary ADC even when D is set. The raw status
D/B/U bits are retained exactly where the original instructions retain them.
The 8052 entry allows the real second phase after a wrapped 804F call. Outputs
are 8224, 8060, or the actual 80BA RTS destination. Coincidental return PCs are
published without executing a fictitious continuation. Stack accesses wrap
within page one, including SP 0 and 255. There is no opcode interpreter.

The new resident composition uses six-byte BRA.L entries because appending the
helper exceeded BRA.W reach. All predecessor sources remain unchanged.

## Verification

The standalone declarative suite covers 132,864 accepted cases and 65,534 inert
wrong-PC rejections. It includes all 256 raw P values crossed with all 256 SP
values at both entries, randomized full RAM/registers, empty/nonempty stream
pointers, all phase values, wrapped frames, and seven coincidental return PCs
for every SP. Optional `--rom` executes independent original instructions with
binary NES arithmetic and compares exact raw P, full RAM/context, and every
ordered write. The default requires no cartridge or private reference import.

The native harness checks the complete journal and untouched rejection state,
ordered writes, an empty resource-read sequence, immutable code/resources,
global read/write whitelists, native registers/SP, and buffer/stack canaries.
An isolated source-only runner copies only the new source and standalone test,
then denies ROM opens and private reference imports. Resident default invocation
runs that source-only proof; cartridge execution requires explicit `--rom`.
Continuous comparisons use the frozen architectural B/U view without modifying
actual original flags or stack contents. Standalone comparisons never normalize.

The four new continuous histories and all twelve frozen tick/parser/event
continuous regressions pass. The predecessor frozen file map and event manifest
files remain unchanged. Private traces remain outside the project; public files
contain no cartridge bytes, extracted assets, captured RAM, or music profiles.

## Reproduction

From the project root, set VASM to the pinned vasm executable and PYTHONPATH to
the installed machine68k/py65 dependencies, then run:

```sh
export PYTHONDONTWRITEBYTECODE=1
python port/tests/recovery_test_sfx_active_control_isolated.py
python port/tests/recovery_test_sfx_active_control.py --rom
for input in 0 16 1 2; do
  CHARACTER_INPUT=$input python port/tests/recovery_test_resident_sfx_active_control.py --rom
done
```

The private cartridge must be at input/rescue-rangers-europe.nes, SHA-256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
For detailed private traces, set PRIVATE_TRACE_DIR to a directory outside the
project; the runner rejects a directory within the project.

## Remaining work and limits

The exact unsupported boundary is PC 86B2, A04 X02 Y13 P24 SP F1, bank 3.
No music-only envelope helper is invoked for this SFX channel. The frozen
1,730-line music envelope body contains SFX-only paths, but its independent
model qualifies only X28–2B. At 871A, X0–3 bypasses CF/music-volume handling and
uses direct SFX publication. At 880F, SFX can take D6/D8 pitch scaling that the
music model does not exercise. A separate variant must model and validate those
paths, resource/index bounds and journal bounds, and exact raw PHP/PLP behavior
across all permitted flags and stack positions. Relaxing a guard is not proof.
This checkpoint deliberately leaves that substantial qualification separate.

No claim is made for audible Paula audio, target execution or speed on a stock
PAL A1200, playability, or completion of the second mixed NMI. The delivered Z/X
ADF, original inputs, README, aggregate scripts, repository index, and remote
publication are unchanged.
