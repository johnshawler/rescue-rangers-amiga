# Reviewed recovery progress, 11 November 2026

This source checkpoint preserves independent, reproducible steps toward the
native Amiga port. The previously lost later gameplay/audio source has not been
recovered. These are new translations built on the recovered early baseline.
Original cartridge, firmware, decoded assets, captures and generated disks are
not part of this repository.

## Qualified components

- Five neutral native game frames: original-first continuous host histories,
  including a different character choice, match state, stack, flags, mapper and
  ordered effects. Source manifest: `recovery_bank_loader_play_manifest.json`,
  SHA-256 `428fc25ff5de74f2bcd64bbb6213207c1b7c0cdc500cfe2df4cd287da9743ba2`.
- Actual five-frame stock target: clean 775-file restore, identical target,
  adapter, boot and ADF rebuild, real CIA input, five genuine scheduler returns,
  final original-derived Copper/pixels and bounded PCM checks pass. Manifest:
  `recovery_play_target_manifest.json`, SHA-256
  `692e107746150e252302d871a5c34e775d0107b4f109b4b8daf1decc8e6897dd`.
  It uses 860,160 Chip bytes and zero Fast RAM. Five publication intervals total
  2.753 seconds; they include prior rendering and intervening engine/audio work,
  but exclude final post-publication rendering. Final redraw is 336.150 ms.
  All 400 updates are late. Only the final screenshot was verified.
- Separate optimized stage display: clean 709-file restore and exact rebuild
  pass. Complete input/helper/state/effect histories match the previous control.
  Final redraw is 168.230 ms versus 335.616 ms, a 49.874% reduction with display
  DMA enabled. Allocation remains 862,720 Chip bytes, zero Fast RAM, with all
  395 updates late. Manifest: `recovery_stage_background_target_manifest.json`,
  SHA-256 `f7fbd4e6df09238450ec18fc593e22215e25b17a1863b109f15311a904ea8cb6`.
- Held-input host prefix: both Right and Right+A histories complete 19 frames
  before pending sound command 10. Raw object-helper status is independently
  checked before explicit B-only publication to the existing ABI. The terminal
  unsupported rejection is inert and does not consume or suppress the sound.
  Manifest: `recovery_bank_loader_input_manifest.json`, SHA-256
  `f81afc810d774e1688b69488c636cc39fd114a6ee6d6751d566b3e62d0bad51e`.

These targets are separate. Their combined optimized gameplay runtime is not
qualified here. The held-input result proves sampled controls and original
semantics, not visible jumping or pickup/throw. No full-game, sustained frame
rate, hardware or NES audio-fidelity claim is made. Original inputs, frozen
checkpoints and the previously delivered Z/X ADF remain unchanged.

The optimized stage audio check uses equal phase searches and explicit wrong
wave/rate alternatives, with a conservatively bounded 2.156 ms alignment error.
The frozen verifier's rejection of the optimized capture, the stronger
classifier's rejection of the old control and sensitivity at +5 ms remain
recorded. This is narrow finite-loop discrimination, not universal playback
qualification or exact latency measurement.

## Reproduction

From the checkout, configure the documented pinned assembler and Python
dependencies. These source-only checks need no game ROM or firmware:

- `bash port/tools/recovery_bank_loader_play_public.sh`
- `bash port/tools/recovery_bank_loader_input_public.sh`
- `bash port/tools/recovery_stage_background_public.sh`

With the pinned GCC14 cross-toolchain additionally configured:

- `bash port/tools/recovery_play_target_public.sh`
- `bash port/tools/recovery_stage_background_target_public.sh`

Private original comparisons and captures require the user's authorized inputs
and the matching restore instructions in `port/analysis`. Never publish those
inputs or resulting private artifacts. The frozen author reports may say that
independent review was pending; that review subsequently passed for the exact
manifest hashes listed above. Later pending-command translation and other
unreviewed development are excluded from this checkpoint.
