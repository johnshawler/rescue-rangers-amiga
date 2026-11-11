# Frozen native-startup title display on emulated stock PAL A1200

This separate milestone executes the published reset-to-C5D1 schedule of 1024
native 68020 helper calls, consumes their actual device journals, renders the
result once, and holds that image. It is not the older fixture-initialized title,
not a dynamic title/menu engine, and not gameplay. No reference RAM, nametable,
PPU state, OAM, screenshot or framebuffer is included in the target. No general
6502 interpreter runs there. The original cartridge executes only in the
independent offline oracle used to establish the bounded static schedule and
verify the result. The builder emits schedule/status constants, not oracle
state bytes; poisoning all oracle RAM/context/journal/raw-status bytes without
changing their lengths produces identical target source.

## Actual native data path

The existing diagnostic driver retains its 1024 complete journal/context
captures, first-window 256 complete RAM captures, ABI checks and stack guards.
After each relevant native helper returns, the new native consumer interprets
its genuinely produced device journal. It handles all 4301 PPU events, including
102 real $2002 reads resetting the shared $2005/$2006 latch. Resource-loader
kind-2 status reads are distinguished from kind-0 cartridge reads. No synthetic
readiness is supplied. All 385 mapper writes update one persistent MMC1 serial
latch, in original order, without resetting it between helpers.

Nametable writes resolve the current MMC1 mirroring mode. PPUADDR pairs and
increments, palette mirroring, PPUSCROLL latch and X/Y values, OAM address and
DMA rotation are consumed. All 8960 DMA bytes originate in actual helper
journals. Unknown PPU registers latch a display error. This is a bounded device
consumer, not a general PPU: it does not model dot timing, rendering-time VRAM
address changes, complete temporary-address scroll interactions, sprite-zero
hits or midframe effects. Those mechanisms do not supply this final admitted
unscrolled view. The renderer explicitly rejects final states other than the
supported CTRL90/MASK1E, zero-scroll, vertical-mirroring view with an empty
MMC1 serial latch. The actual final shared PPU latch is independently verified
zero; it is not a general display-admission guard.

At C5D1, live mapper CHR0/CHR1 select the two pattern-table views from immutable
full cartridge CHR. Neither the nametable nor OAM nor palette is loaded from a
fixture. The existing five-plane native background renderer creates opacity
and tile-cache data. The existing 8x8 sprite renderer retains flips, transparent
pixels, foreground/background and OAM priority, clipping and first-eight-per-
scanline selection. The Copper palette is generated from the live logical
palette through an explicitly declared conventional RGB approximation,
quantized to Amiga RGB4. This is not analog NES colorimetry or an RGB table
extracted from a screenshot.

## Verified target result

Two fresh emulator executions, each 1800 frames, produce byte-identical full
2 MiB Chip dumps and raw video captures. Effective logs verify A1200OG, 68020,
AGA, PAL 50 Hz, 2 MiB Chip, zero Fast/slow memory, no JIT/FPU/MMU, and cycle-exact
CPU, memory and blitter settings. No RAM_LOAD or RAM_LOAD_FRAME is used.

The inherited verifier passes all 1024 contexts/journals and mapper/latch
boundaries, all 256 captured RAM boundaries, final resident RAM/context,
resource banks, guards, ABI and stack. This new display run is one capture
window, not a claim to repeat the prior four-window regression.

An independent observer of the unaltered cartridge's original device events
computes nametables, palette, OAM, mapper/selected CHR and a per-pixel composite.
Every modeled device-state byte, all 2048 nametable bytes, all 32 palette bytes,
256 OAM bytes, 8192 selected CHR bytes and all 51200 Amiga bitplane bytes match.
The full immutable 128 KiB CHR resource is also checked. Copper mode, bitplane
DMA pointers and every palette entry are checked. The actual 720x287 video
capture matches the decoded expected RGB image exactly across the 640x256
viewport at (40,18), including the emulator's 2x horizontal pixel duplication.
The actual captured pixels were visually inspected: logo, character faces,
player options, cursor and copyright/licensing text are visible.

New tests pass 32 synthetic assembled 68020 consumer calls covering register
and stack preservation, shared latch reset, four mirroring modes, serial
continuity, increment32, palette aliasing, rotated DMA, resource filtering and
unknown-register errors. These are test inputs, never target initialization.
175 mutations of the real successful capture/configuration are rejected.
Two rebuilds reproduce all nine generated build artifacts byte-for-byte.

## Memory and timing, with limits

Payload: 514436 bytes. Boot allocation: 1283072 bytes, MEMF_CHIP|MEMF_CLEAR,
including 768376 bytes of diagnostic capture workspace and the final canary.
That leaves 814080 bytes of the 2 MiB outside this allocation. No Fast RAM.

Actual native CIA-B E-clock measurements on both executions:

- 543737 ticks for startup plus diagnostic recording/checking, about 766.5 ms.
- 55858 ticks for CHR selection and one background/sprite composition, about
  78.7 ms using the PAL E-clock rate of approximately 709379 Hz.

Display DMA is off during those measurements. Disk boot/loading time and final
Copper/palette setup are not included. This does not demonstrate 50 Hz rendering
or gameplay throughput. The final image is held; no live input, title loop,
Paula playback, streaming audio, gameplay or physical-hardware test is claimed.
The pending separate title-loop/music-command0E work is not included.

## Preservation and private outputs

Only the seven new source/test/report files plus their source manifest belong
to this milestone. Existing tracked files have no diff; no existing source,
manifest, scripts, README, branch or index was changed by this work. Other pre-existing untracked development is outside this milestone.
The delivered Z/X disk was rehashed and remains
6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17.
No commit, branch, index, publication or deployment operation was performed.

All generated files are confined to ignored port/build/startup-display-native.
The ADF, binary, generated assembly/resource files, Chip dumps, PNG and PPM are
private cartridge-bearing outputs. Firmware and ROM remain private. The source
manifest records dependency and output hashes, with no proprietary bytes.

Final private ADF SHA256:
1718c9485c760bcd3b9fbf730e45a855be57a1b10314a32d54ef90bd55b798db

## Reproduction

Set VASM, PYTHONPATH, HEADLESS and PUAE_CORE to the approved assembler,
inspection dependencies, headless frontend and PUAE core. From the repository:

```
python port/tools/build_recovery_startup_display.py
python port/tests/test_recovery_startup_display_device.py
python port/tests/test_recovery_startup_display_build.py
out="$PWD/port/build/startup-display-native"
env -u RAM_LOAD -u RAM_LOAD_FRAME -u PUAE_FASTMEM PUAE_MODEL=A1200OG \
 RAM_OUT="$out/chip.bin" "$HEADLESS" "$PUAE_CORE" \
 "$out/startup-display.adf" "$PWD/artifacts/a1200-system" 1800 \
 "$out/screen.ppm" > "$out/amiga.log" 2>&1
python port/tests/verify_recovery_startup_display.py
python port/tests/test_recovery_startup_display_rejection.py
```

The verifier requires the full actual Chip dump, effective emulator log and
actual video capture. It does not accept a synthetic positive baseline. PIL is
needed for the RGB video comparison; machine68k is needed for synthetic native
consumer tests. Existing main-source regression is deliberately not rerun here.
