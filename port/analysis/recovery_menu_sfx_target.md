# Stock menu/SFX dispatcher checkpoint

Six fresh emulated stock PAL A1200 boots pass: two each for the qualified
`default`, `right_hold`, and `move_back` scripted histories. All stop at the
original C5F8 boundary. The right history confirms the alternate character;
the other two confirm the original character. This is a bounded diagnostic,
not gameplay, live keyboard input, or audible sound.

This is new recovery development from the reviewed early source. The lost
later gameplay/audio source is still unrecovered. No Paula backend is linked.
The delivered Z=B, X=A disk and all predecessor source checkpoints are unchanged.

## Genuine original state and selection

The native dispatcher selects solely from its live RAM, context, mapper, and
event state. Original-only verification starts at FE24 after NES hardware
warmup. Native state is never populated from an original snapshot, expected
result, prescribed helper list, or reference framebuffer. Caller/NMI frames,
serial mapper effects, and the original wrapped stack continue naturally.
There is no generic 6502 interpreter in the target.

- `default`: 1,229 completions, 43 logical NMIs, 91,651 original instructions,
  322 ordered APU writes. Cursor X40, original selection table hash
  d39d51409944c12c1975a92ed4e9a5ad661804060c69b0074afd3e5be1e51dd9.
- `right_hold`: 2,391 completions, 78 logical NMIs, 146,425 original instructions,
  607 APU writes. Genuine shutdown at completion 1,777 and continued music 0E
  at 2,368. Cursor X136, swapped selection table hash
  091d1cbde63fdc972a4546761e96763afe00e955d70669fa4d5ccd2050ffcc54,
  with original alternate-character markers 8D/8A/95/8E.
- `move_back`: 3,766 completions, 118 logical NMIs, 205,317 original instructions,
  922 APU writes. Shutdown at 1,992 and 3,146; eight continued 0E commands.
  Right, release, Left, release, repeated Left, and eventual confirmation
  return to X40 and the original table hash above.

The terminal PC alone is not selection evidence. Complete final RAM and the
original confirmation table/marker transformations establish the choice.

Inputs are externally defined reproducible controller-byte histories, not
live keyboard input. Start is held when the live title reaches A025. The
character-menu A06C visit counter chooses samples from a fixed input array:
`default` holds Start for visits 1–2, releases for 3–4, then presses Start;
`right_hold` adds Right at visits 5–7, releases until 40, then confirms;
`move_back` adds Left at 10–12, repeats Left at 45–47, and confirms from 80.
These labels match the previously qualified history names; `right_hold`
includes delayed press, held samples, and release. Waits are converted directly
into logical NMI events. They are not paced PAL video frames.

## What was verified on target

Each fresh run checks the complete final 2,048-byte RAM, eight-byte context,
12-byte runtime, final published journal when nonempty, guards, balanced native
SP, and unchanged lower 3,072 stack bytes. The stack observation bounds use to
the upper 1 KiB; it is not a stack trace. Immutable executable bytes, full PRG,
and full CHR are checked. The two full 2-MiB Chip dumps and raw screenshots are
identical for each history.

A bounded 262,144-byte capture retains each successful helper ID and its actual
counted four-byte journal records, plus defined DMA data. Capture lengths are
50,528 / 78,352 / 111,140 bytes. Every captured record and DMA byte equals an
independent original-only instruction replay, in order. This includes actual
APU commands and resource/mapper events. It is an audit shadow, not audible
output, and has no audio timestamps suitable for claiming playback fidelity.
Unpublished journal padding is never captured. Zero-size helpers do not read
the old journal header. The 134,638-byte journal and FFFF size sentinel remain.

The independent original event stream also reconstructs final device state,
2,048 nametable bytes, 32 palette bytes, 256 OAM bytes, both selected CHR banks,
51,200 native bitplane bytes, and all Copper setup, pointers, colors and final
WAIT bits. All match. Each actual emulator screenshot has all 163,840 viewport
RGB pixels checked, and each history was opened and visually inspected (two unique final views). CHIP / DALE are displayed with the cursor on the expected character.
This proof concerns final device state, not intermediate displayed animation.

Target coverage is final RAM/context/runtime plus every published journal/DMA,
not all-boundary target RAM capture or target memory-access tracing. Separately,
initialize-once and poison-before-every-call machine68k runs check all 14,772
RAM/context/runtime boundaries across the three histories. All journal reads
are proven to follow writes within the same call; ABI, guards and immutable
resources pass. The previous 14-history proof remains separate evidence.

Ten synthetic tests exercise the new capture adapter, including stale headers,
32768/33339/33595-record copies, FFFF, over-capacity/unknown helper rejection,
register preservation and stack balance. The isolated adapter differs only in
the final branch displacement to its test stop. Original long-script tests
also recheck full 134,638-byte native journal semantics. The verifier rejects
265 mutations of real captures, pointers, guards, immutable code, configuration,
timers, Copper and actual pixels. Two fresh-process source-only builds reproduce
all 24 generated artifacts with original-oracle and py65 imports denied.

## Code, allocation, and measured scope

The 626-byte new runner/capture adapter links the exact reviewed 46,492-byte
composition, SHA256 a8a31217696f2f3d30d629adf570b9723c171d965e25f267294a55dc1534496e.
All frozen helpers and guards are unchanged. Explicit alignment preserves the
exact 1,750-byte device/renderer/clock executable region, SHA256
85b142d8ac84d53f4f5bb6f5143b28d1a07183989b71f2aeeeacaa0a3f920bad.
Only the new adapter mapping adds helper70 → frozen mapper consumer ID7.

Payload: 788,426 bytes. MEMF_CHIP | MEMF_CLEAR allocation: **788,480 bytes**,
including the capture. Fast allocation: zero. This is a development budget,
not a gameplay memory budget. Logs verify A1200OG, PAL 50 Hz, 68020, AGA,
2 MiB Chip, zero Fast/slow RAM, no JIT/FPU/MMU, and cycle-exact CPU, memory,
and blitter. Neither firmware nor the pinned frontend/core was rebuilt.

Measured CIA elapsed ticks at 709,379 Hz, with display DMA disabled:

- Default progression including runner, device, and capture: 722,042 ticks,
  1.017850824 s. Separate CHR mapping/render: 56,394 ticks, 79.497702 ms.
- Right: 1,240,849 ticks, 1.749204586 s; render 56,350 ticks, 79.435675 ms.
- Move-back: 1,825,315 ticks, 2.573116768 s; render 56,381 ticks, 79.479376 ms.

Boot/loading and initial allocation are outside progression. Palette/Copper
setup follows the render measurement. Clock-call and report overhead remains.
These new measurements include ordered capture overhead; no predecessor timing
has been transferred. They are not CPU instruction counts, game FPS, physical
hardware timings, or demonstrated real-time input/audio cadence. Each frontend
run uses 6,000 video callbacks; that fixed budget is not completion time.

## Preserved failed candidate and limits

Independent verification caught a missing device-adapter mapping for helper70:
the native state and ordered capture were correct, but the right-selection
device shadow missed five mapper writes. The failed source, ADFs, full dumps,
screenshots and logs are preserved in the private `failed_candidate_01`
directory. The corrected mapping is tested above. An initial executable
alignment mismatch and a Python test-only bytes-type error are also retained.
Frozen helpers or renderer bytes were not changed to pass the comparison.

Independent review reproduced all six fresh boots and source-only builds,
rechecked the full contract and negative tests, and added 26 adapter edge cases
plus six device-consumer replays. Deliberately omitting helper70 reproduced the
five missing mapper writes per occurrence. No functional blocker was found.
The delivered ADF, original ROM/firmware and predecessor source are unchanged.
Live input, audio integration and C5F8 gameplay remain separate future work.
The audio-event compatibility audit qualifies planner input only; it does not
turn these captured APU records into audible sound.

## Reproduction

From the repository root, install `requirements-dev.txt` and set `VASM`,
`PYTHONPATH`, `HEADLESS`, and `PUAE_CORE` to the approved assembler, dependencies,
pinned frontend, and pinned core. Tool identities are in the manifest.
Supply only the approved private inputs:

- `input/rescue-rangers-europe.nes`, SHA256
  051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411.
- `artifacts/a1200-system/kick40068.A1200`, SHA256
  6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707.

```sh
export PYTHONDONTWRITEBYTECODE=1
python port/tools/build_recovery_menu_sfx_target.py
python port/tests/recovery_menu_sfx_target_build_test.py
python port/tests/recovery_menu_sfx_target_contract.py
python port/tests/recovery_menu_sfx_target_adapter_test.py
python port/tests/recovery_state_menu_sfx_long_rom.py \
  --rom input/rescue-rangers-europe.nes
out="$PWD/port/build/recovery_menu_sfx_target"
for history in default right_hold move_back; do
  for prefix in '' repeat-; do
    env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
      RAM_OUT="$out/$history/${prefix}chip.bin" \
      "$HEADLESS" "$PUAE_CORE" "$out/$history/recovery_menu_sfx_target.adf" \
      "$PWD/artifacts/a1200-system" 6000 "$out/$history/${prefix}screen.ppm" \
      > "$out/$history/${prefix}amiga.log" 2>&1
  done
done
python port/tests/verify_recovery_menu_sfx_target.py
python port/tests/recovery_menu_sfx_target_rejection_test.py
```

All private generated evidence stays under ignored
`port/build/recovery_menu_sfx_target/`. The manifest pins the exact added
source files, dependency hashes, input/tool identities, and verification files.
