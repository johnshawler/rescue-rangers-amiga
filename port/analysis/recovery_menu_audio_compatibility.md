# Menu and title event compatibility with the experimental Paula planner

The unchanged compiled 68020 planner accepts all 1,966 completed-interrupt
snapshots from 14 qualified title/menu histories, provided the audio shadow is
initialized explicitly as described below. This qualifies its **input domain**,
not audible output, faithful NES synthesis, target cadence, or concurrent game
performance. No Paula backend has been attached to the new menu diagnostic.

## Continuous original/native evidence

The collector observes the original bus while the frozen state-driven native
comparison checks the same ordered effects and live game state. It begins at
FE24 after NES hardware warmup. It records actual original NMI entry and opcode
40 RTI completion, rather than guessing a frame label from a caller's counter.
The first two bootstrap interrupts are included and finish with real RTIs.
All 15,059 APU writes occur between entry and RTI. There are no unclosed entries,
post-RTI audio writes, or audio writes before the first observed NMI.

Histories are right/left held, early and repeated directions, alternating,
move-back, rapid, default, neutral, and three title-direction/select cases.
These retain their existing scope: three title cases stop at unsupported A055;
the others stop at C5F8. This is not coverage of later gameplay or every sound.
The original/native code comparison is completed before the planner test runs
in a separate process. The planner does not influence game execution.

Only 4000–4008, 400A–400C, 400E–400F and 4015 are written in these histories,
with unused addresses inside those ranges absent. No DMC registers or 4017
frame-control writes occur. Observed 4017 reads are the second controller port,
not APU status. No APU-status reads occur. These observations apply only to the
qualified post-warmup paths, not omitted NES warmup or future gameplay.

The sweep bytes remain 08, triangle control is 00/FF, envelope/control registers
use halted constant volume, and enable writes are 0F. Noise periods/modes remain
07, 0D and 81. Audible frame-final timer ranges are pulse one 166–280, pulse two
78–595, and triangle 140–595. Cursor SFX therefore expands pulse two beyond the
old title-only 333–595 range, but remains inside the unchanged planner's safe
Paula period bounds. No guard was loosened.

## Initialization and update boundary

Use a zeroed 16-byte register shadow and enable=0, with a documented synthetic
muted-noise period 07 until the first actual 400E write. Process every ordered
write into the shadow, including 4015, but produce a hardware plan only when a
genuine logical interrupt completes. This sentinel is a host-backend safety
choice, not a claim about original NES power-on register state.

Without the sentinel, the first two completed, silent snapshots in every
history reject because 400E has not been written: 28 expected rejections. With
it, all 1,966 completed snapshots pass, and both initial snapshots remain fully
muted. The first actual noise period is 0D in interrupt three. Within that
interrupt the original writes nonzero noise volume immediately before its
first period write. This **intermediate** state must not be presented to Paula
using the sentinel. At completed-interrupt boundaries, noise is never audible
before the actual period has arrived.

Calling the planner after every register write is not a substitute: the 15,059
transient-state calls include 135 atomic rejections, covering initialization and
partially updated audible timers. All of those rejections leave the destination
plan untouched. Additionally, 461 interrupts write a register more than once,
and 406 change its value during the interrupt. Frame-final snapshots necessarily
collapse these changes. The collector records instruction ordinals only, not
CPU-cycle timestamps. Passing a snapshot test does not make that loss inaudible.

## Compiled-code check

The real M68EC020 planner is compiled freestanding and exercised in machine68k.
The 18,991 calls comprise every ordered-write snapshot and both raw and safe
variants of every real-RTI snapshot. All accept/reject decisions and accepted
period/volume/wave plans match the integer contract; all 163 expected rejections
are atomic. Callee-saved registers, stack return, immutable input/code and
output guards are checked. This is host functional execution, not a benchmark.
The existing independent synthetic/noise and emulator audio qualifications of
the isolated backend remain separate evidence.

Backend source SHA256:
5c5be6ac34df5fc7d9b72a081343abc262c762d8b67b142c9e585e6a24080420.
Native dispatcher SHA256:
a8a31217696f2f3d30d629adf570b9723c171d965e25f267294a55dc1534496e.
Compiled planner text SHA256 with the pinned recovery GCC toolchain:
7f879c9a02855fbe398a0a98f5c3ae3d7626de8965c991fc3bbf4bedb8b747c9.

## Integration decision and remaining qualification

The planner can be reused unchanged for these completed-frame states. The old
935-frame/7,136-event profile builder cannot be used unchanged: it hardcodes a
title-only profile and narrower timer assumptions. Nor should the standalone
probe's whole-machine setup or hardcoded enable=15 be copied into the target.
A separate integration must own a persistent shadow, consume actual counted
journals, detect the reviewed native RTI completions, initialize/mute DMA safely,
and honor actual enable writes. It must reject an unsupported plan without
publishing a partial hardware update, then report the unsupported state.

That integration still requires on-target audio capture, cadence and underrun
checks, mixer/channel verification, state regression and memory/CPU measurements
with the renderer running. Input-domain compatibility alone supplies none of
those results. PAL NES and Amiga video rates must not be assumed identical.

The backend remains approximate: no sweep, hardware envelope/length/linear
counter emulation, high-timer phase resets, frame-counter IRQ/delay behavior,
DMC or nonlinear mixing. Four Paula voices use fixed stereo placement and
finite noise loops with DC bias, artificial repetition and phase discontinuities.
Noise loop reload can delay changes by about 92.4 ms. The 81 noise case has very
low AC content despite substantial total RMS. These limitations persist even
when every input snapshot is accepted.

## Reproduction and private data

Install `requirements-dev.txt`; set `VASM` to the pinned assembler and put the
recovery m68k GCC/binutils on PATH, or set `PAULA_CC`. Supply the hash-checked
European cartridge privately. No firmware is needed for this host-only audit.
Choose a new output directory for each run; existing evidence is not replaced.

```sh
out="$PWD/port/build/menu-audio-audit-$(date +%Y%m%d-%H%M%S)"
python port/tests/recovery_menu_audio_events.py \
  --rom input/rescue-rangers-europe.nes --output "$out"
python port/tests/recovery_menu_audio_compatibility.py --profiles "$out"
```

The first command writes private original event streams. The second compiles
into a new planner subdirectory and writes private per-frame plans plus summary
results. Do not publish those streams, plans, cartridge data, audio captures or
binaries. Only generic test source, factual results and hashes belong in the
public checkpoint. The original cartridge, firmware, delivered Z/X disk and
predecessor source are unchanged. Lost later gameplay/audio source remains lost.
