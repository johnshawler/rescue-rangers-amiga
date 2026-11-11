# Recovery palette-capable NMI prefix

Newly authored, bounded static 68020 translation for the explicit logical NMI
at the second task yield. This is not recovered playable or audio source. It
adds no generic 6502 interpreter and changes none of the prior helpers, stable
builds, probes, public tests, or delivered Z/X ADF.

## Source-verified boundary

Private Europe ROM SHA256:
`051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`.
Tests use actual fixed-bank ROM instructions and true py65 `nmi()`, not a
hand-written reference implementation. The event is deliberately injected
before `$FE8D`; this does not assert hardware cycle timing.

After `recovery_resumed_task_setup`, task zero waits with saved SP `$B8` and
nested continuation `$C2A8`, pending palette flag `$18=$FF`, and queued sound
`$07`. The new helper preserves the interrupted context through the original
seven hardware/handler stack stores. Its original SP becomes `$B1`. The nested
continuation and outer return bytes at `$01B9–$01BF` remain unchanged.

The handler executes the video/DMA prefix, then the actual palette path:

- `$C05D–$C05F`: X=0, clear the pending palette flag `$18`.
- `$C061–$C06C`: unused-result PPU-status read, address `$3F00`, Y=32.
- `$C06E–$C076`: publish all 32 caller RAM bytes `$0300–$031F` in ascending order.
- `$C078–$C083`: publish address bytes `$3F,0,0,0` exactly as the original does.
- `$C086–$C0BE`: second trailing status read, scroll/control/mask publication,
  frame increment and four original timer slots.

Stop before `$C0BF`, where bank-busy handling and audio dispatch begin. No bank
publication, audio dequeue, APU write, register restoration or RTI occurs in this
helper. The queue, sound shadow and logical bank-6 resource state are preserved.
Task zero becomes ready state 4/timer 0 in the composed run, but its nested
continuation has not resumed.

## ABI and guards

`port/src/recovery_palette_nmi_prefix.s` exports
`recovery_palette_nmi_prefix`.

- A0: valid writable original-layout 2048-byte RAM.
- A1: valid writable eight-byte context: big-endian PC, A/X/Y/P/SP/reserved.
- A2: valid writable 454-byte journal/resource output. Count word, 49 four-byte
  records `{address.w, data.b, kind.b}`, then 256 DMA bytes at offset 198.
- Buffers must be disjoint and exclusively owned during the synchronous call.
- Require PC `$FE8D`, canonical P (B clear/U set), control `$FF` bit 7 set,
  `$F0/$9A/$19/$1A/$1B/$1C/$1D` zero, and `$18` nonzero.
- A/X/Y/SP and remaining status bits may vary. This prefix has no decimal
  arithmetic, so D is supported here. The earlier resumed-setup helper's D=0
  restriction remains unchanged.
- D0=1 success, D0=-1 unsupported with RAM/context/output untouched.
  D1–D7/A0–A6 preserved; native stack balanced; native CCR scratch.

The records include three unused-result `$2002` reads (kind 0, data 0), and
46 writes (kind 1). Zero read data is a placeholder because the actual return
values are unused; oracle status returns vary. The DMA snapshot contains the
exact page-two bytes at publication, checked both against live native RAM and
the original bus capture. A renderer must consume this journal explicitly;
it is not Amiga MMIO, a PPU implementation, or cycle-accurate DMA.

Final PC is `$C0BF`, X=`$10`, Y=0, SP=input SP minus seven modulo 256. Final A
and C come from the fourth timer slot. Z=1/N=0 from final DEY; I=1; D/V retain
entry values; B=0/U=1. The reserved context byte is unchanged.

## Executed host proof

With `VASM` naming `vasmm68k_mot` and py65/machine68k on `PYTHONPATH`, run:

```
python port/tests/recovery_test_palette_nmi_prefix.py
```

The actual assembled M68EC020 helper passed:

- 2,048 standalone original-ROM/native comparisons. Every stack-pointer,
  palette byte, timer byte in each of four slots, nonzero request value and
  canonical status pattern is covered, plus randomized RAM/palettes/registers
  and varied PPU-status return values.
- 256 continuous twelve-helper comparisons: reset, first yield, real NMI,
  F0 reset dispatch, silent tick/real RTI, two-controller scheduler resume,
  resumed palette setup, second real NMI at nested yield, stop at `$C0BF`.
  No RAM/context/reference-status patches occur between helpers. Initial reset
  contexts have D clear because the eleventh helper requires it.
- 67,641 unsupported inputs rejected inertly: all other PCs, every invalid
  status/control value, every nonzero excluded flag value, and absent palette
  request. All 2,048 completed-boundary calls are also rejected inertly.
- Full 2048-byte RAM, full context, ordered merged RAM/hardware writes, exact
  journal and DMA data, raw seven-byte original interrupt frame, native register
  preservation, stack balance, output guards and bounded execution.

`architectural_status_view` only removes py65's virtual B and sets U for
comparison. Raw `ref.p` is never rewritten after initialization. Tests check
its virtual B after the first RTI/resume and its hardware-cleared B after the
second actual NMI, as well as the raw saved-frame bytes.

The composed stop preserves sound shadow `$D9=7` and queued `$07`, all queue
bytes, and the nested task stack. No audio output is fabricated or discarded.
The tests journal and compare mapper, APU, controller and PPU effects across
the full chain, including absence of new mapper/APU/controller events in this
prefix. This is host semantic evidence, not target-probe or physical-Amiga
validation. No full boot, gameplay, audible Paula output or performance claim.
No cartridge bytes, proprietary assets, trace dumps or built binaries are part
of these three new source/test/report files. No commits or publication made.
