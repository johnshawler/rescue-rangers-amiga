# CHR-request NMI prefix

`recovery_chr_nmi_prefix.s` is a new static native 68020 translation of the
original hardware NMI entry and C000–C0BF prefix, including calls to FF1F and
FF39. It does not interpret cartridge opcodes. Existing helpers are unchanged.

## Public contract

A0 points to 2048-byte RAM, A1 to the eight-byte big-endian PC/A/X/Y/raw-P/SP/
reserved context, and A2 to a 494-byte journal. Buffers, code and native stack
must be valid, disjoint and exclusively owned. D0 returns 1 on success or -1
for an unsupported video queue without mutation. D1–D7/A0–A6 and native stack
balance are preserved; native CCR is scratch. Every incoming PC, SP and raw
status byte is accepted. No cartridge resource view or runtime ROM is needed.

If F0 or 9A is nonzero, original video skipping leaves every request pending.
Otherwise nonzero 19, 1C or 1D rejects before any mutation. Requests 1A and 1B
are independently optional; nonzero values are masked to five bits, stored
in F2/F3, sent as five successive shifted accumulator values to BFFF/DFFF,
and then cleared at the original instruction's position. Wrapped page-one
JSR writes C04F/C058 remain visible. The hardware interrupt and PHP/PHA frame,
palette request, DMA snapshot, PPU operations and timer suffix remain ordered.
No audio, RTI, callback or deferred-work processing is included.

Journal format: big-endian count word, up to 59 records of address.word,
value.byte, kind.byte. A mapper address (BFFF or DFFF) carries live F5 metadata;
PPU records use kind 0 for unused status reads and kind 1 for writes. DMA is
256 bytes at offset 238, captured before its publication record. Unused
records and skipped DMA remain untouched. The helper writes serial events,
not mapper state: the caller must apply them to its existing serial latch,
including any partial initial latch. With an empty latch and both requests
9F, each produces values 1F,0F,07,03,01 and CHR0/CHR1 become 1F/1F. PRG and
control are unchanged. With a partial latch no such final-bank assumption
is valid.

## Validation

The ROM-free contract exhausts all 65,536 ordered CHR-request byte pairs,
also covering every PC and every raw status/SP value, with randomized full
RAM and registers. Another 512 cases exercise genuine video skipping with
pending work retained. All 765 nonzero unsupported-queue singleton cases
are inert. The independent actual-ROM suite uses the same input distribution,
executes the unmodified original instructions against a bounded bus and
varies the otherwise unused PPU status value. It never patches reference
status. Both suites compare all RAM/context, ordered RAM/PPU/mapper effects,
complete journal including untouched tail, DMA, native ABI, canaries and
read/write access whitelists. No semantic cartridge data reads occur.

Run using approved VASM and machine68k/py65 PYTHONPATH:

- `python port/tests/recovery_test_chr_nmi_contract.py`
- `python port/tests/recovery_test_chr_nmi_rom.py`

The original-ROM test requires Europe cartridge SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
This is host native-code correctness evidence, not Amiga execution, displayed
output, target performance, Paula audio, playable-game or disk-image evidence.

The public suite passed 66,048 successful cases plus 765 inert guards. The
assembled helper is 594 bytes, SHA256
85ee6fe0e56a05c251f8be64c94059524268dabe3fe90d070c517f7753947786.

`python port/tests/recovery_test_chr_nmi_latch.py` additionally passed 496
seeded mapper cases (992 continuous NMIs). It covers every one of the 31
empty/partial serial-latch bit patterns, eight request pairs, and both video
processing and skipping. Original bus writes feed an integer shift/count
adapter; native journal writes feed an independent list-of-bits adapter.
Each starts with matching randomized mapper registers and retained latch.
There is no latch reset, request repair or native RAM/context reload between
the two NMIs. Both adapters agree after each interrupt, including preserved
partial latch and requests on genuine video skipping.

The independent original-ROM suite also passed all 66,048 cases.
