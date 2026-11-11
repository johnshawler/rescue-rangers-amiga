# Genuine character-menu queued video NMI

The new static 68020 helper recovery_queued_video_nmi_prefix consumes the real
RAM19 request through original C115 and continues the NMI to C0BF. The separate
resident test composes from reset with one native RAM/context initialization and
identical external Start input. It reaches A06C after the actual video request,
audio, RTI and task scheduler: 1,128 accepted helper calls, 38 original NMIs,
36 later completed audio calls, timer898, context A06C/FF/FF/FF/A4/BD/A7.
The mapper finishes at (1E,1F,1F,2,empty). RAM19 is zero because C117 consumes
it, not because the harness patches readiness. The original A06B return frame
is used by the scheduler. A06C itself has not yet been translated by this work.

The character script writes eight bytes at PPU2226 and nine at PPU2232, then
terminates on FF. The continuous comparison checks every accepted boundary,
complete RAM/context and ordered effects. Totals are 17,790 RAM writes, 4,352
PPU events, 415 mapper writes, 684 controller events, 2,416 resource reads and
274 APU writes. Composite size is 26,114 bytes, SHA256
20b158936f16e9d76cde73b44aee862657aa9749c187283b25a9809a0395b1ca.
No provisional audio01/0E/12 translation is needed for this continuation.

## Exact script semantics and bounded contract

C115 sets X=0 and stores zero at RAM19. At each command X, RAM0360+X is
address-high. Bit7 terminates before reading the remaining fields. Otherwise
RAM0361+X is address-low and RAM0362+X is initial Y. Each iteration emits
RAM0363+X to PPU2007, increments X modulo256, decrements Y modulo256 and loops
while the resulting Y is nonnegative. Thus initial Y00..80 emits Y+1 bytes,
whereas Y81..FF emits exactly one byte. Afterward X advances another three
modulo256; zero returns immediately, otherwise another command is examined.
Absolute indexed data reads can reach RAM0462. This is not a zero-page pointer
parser, conventional unsigned byte count, or assumed 24-byte-only format.

The preflight follows the exact immutable script-dependent X transitions.
Within 256 commands either a negative high byte or a zero-X end occurs, or
some X repeats and the original would never terminate. The latter is rejected
inertly before any simulated interrupt frame, RAM or journal mutation. Wrapped
X and zero-X endings are supported. There is no silent truncation. Active-video
RAM1C/1D requests also reject inertly. Genuine F0|9A video skipping retains all
requests, ignores script validity and performs only the original timer work.
No invented readiness or script terminator is inserted.

A0 addresses RAM2048; A1 context8 (PC.word,A,X,Y,rawP,SP,reserved); A2 journal
134638. Buffers, code and native stack must be valid, exclusively owned and
disjoint. The conservative bound is 256*(129+2)+59=33595 four-byte PPU/mapper
records, preceded by count.word. The DMA snapshot is fixed at offset134382,
length256. Untouched journal bytes remain unchanged. Mapper writes preserve
live F5 metadata and are applied to the caller's existing serial latch, never
reset by this helper. D0 returns 1/-1, D1-D7/A0-A6 are preserved, stack is balanced,
and native CCR is scratch. No cartridge data or general 6502 interpreter is
embedded. The helper contains explicit static translations only. It preserves
actual interrupt and wrapped JSR stack writes, CHR/palette/scroll/timer behavior
and raw architectural status. It performs no ADC/SBC or decimal arithmetic.

The large worst-case journal is deliberately a host proof contract, not an
Amiga allocation/performance recommendation. It can be reduced only with a
separately tested narrower script contract or streaming adapter.

## Verification

recovery_test_queued_video_nmi.py runs 2048 ROM-free cases, including all 256 raw
statuses/SP values, arbitrary and wrapped scripts, high counts, zero-X endings,
terminators, video-skip and unsupported requests; 352 cases reject inertly.
The --rom mode independently executes the actual NMI/C115 instructions and
checks full original RAM/context/effects against the declarative model and
native helper. It also seeds all 31 possible empty/partial MMC1 latch patterns
and compares independent serial adapters. Native tests check full journals and
untouched tails, DMA, global read/write bounds, canaries, ABI and stack balance.
The separate resident test checks immutable resources and their semantic reads.
All reference PPU status return values are randomized in isolated ROM tests.

Set VASM to the approved vasmm68k_mot and PYTHONPATH to the inspection .deps:

    python port/tests/recovery_test_queued_video_nmi.py
    python port/tests/recovery_test_queued_video_nmi.py --rom
    python port/tests/recovery_test_resident_character_video_queue.py

Private original ROM: input/rescue-rangers-europe.nes, SHA256
051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.

Only uniquely named source/tests/report/manifest are added. Existing files,
manifests, assets, ADFs, index, branches and publications are unchanged. This is
host M68EC020 evidence, not live gameplay or a stock PAL A1200 speed/display/
audio claim. The eventual target remains 2 MiB Chip and optional Fast at most 8 MiB,
with Z=B pickup/throw and X=A jump.
