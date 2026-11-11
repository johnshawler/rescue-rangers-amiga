# Native first-stage preparation and map expansion

This additive composition extends authentic C6B5 entry through the existing
player/pointer primitives, real stage fade and bank4 NMIs, fixed stage resource
and palette setup, then the separately qualified map100 region. It stops before
bank4:8040 object loading. First stage is not yet complete or playable and no
new actual target picture/timing/audio qualification is claimed.

All preceding source freezes remain unchanged. No input/capture/firmware/disk
is overwritten. Production is static68020 game logic; offline generators are
not runtime CPU decoders and never embed proprietary tables or captured state.

## ABI and added helpers

Usual RAM2048/context8/runtime12/PRG131072 ABI with long journal134638 and
4096 disjoint native scratch bytes. Codes/resources remain immutable and
registers/native SP are preserved. Standalone copied validation requires2304
bytes; composed host bounds verify the full4096 range. Target stack/allocation
must be verified independently when integrated.

-110: C6B5→C6BD, additive journal adapter over original stage pointer initializer.
  Live421-byte bank4 view8193–8337; counted journal70 containing5 mapper and12
  semantic resource events in original order. Actual RAM stores remain direct.
-111: unchanged player initializer, private scratch journal, external size0.
-112: unchanged C700 stage fade entry, external size0.
-113: unchanged fade continuation, external size0.
-114: actual stage coroutine scheduler; journal74.
-115: statically translated fixed-bank C115 direct video, C14E/C158 render
  mode, C24A clear/hide/yield, and E099 resource/palette/audio-request preparation;
  counted journal60002. Its copied-state preflight checks all dynamic accesses,
  a200000 static-instruction budget and15000 records before mutation. Only
  supported PPU writes2001/2006/2007 are admitted; fixed-ROM reads retain exact
  resource identity. Code includes original F377 audio queue insertion, not
  a mute or skipped stage music request.
-100: separately frozen stage-map region, integrated without changing its
  implementation. Explicit C14E/FF53/C115 exits and real return frames are
  consumed by the other native helpers. Actual bank0/4 changes are retained.

The additive stage dispatcher shares existing IDs33/41/42/70/79/98 for their
unchanged native operations and effects. It admits real zero-F6 mapper requests
0..7 and follows actual serial writes into runtime bank state. It never edits
F1 to fit a narrower guard. Bank0/4 main-task interrupt paths are selected
explicitly; earlier bank2/5 and startup/music bank6/3 paths retain their frozen
dispatchers. Nonempty audio queues enter the real pending-command helper rather
than being cleared. NonzeroF6 at mapper entry remains inert unsupported.

## Verified continuous histories

Composite82170 bytes, SHA256
`077273562e71a6aaf863cc05cae707e88a764f4583d5c6f312fdb7ea3f921270`.
Starting FE24 after hardware warmup with one resident native initialization:

-Default14098 calls/377 logical NMIs/2699 ordered APU writes.
-Alternate14259 calls/377 NMIs/2705 APU writes.
-Move back14500 calls/378 NMIs/2713 APU writes.

All end8040/00/0E/FF/26/B7/A7, mapper1E/0D/0D/04, before bank4 object loading.
Each completes419 map100 slices,144 original DBEC map expansions and147 fixed
helper115 boundaries. No successful state is reloaded and no mapper, readiness,
audio flag or original stack is synthesized. Real controller choices and
interstitial Start exit remain from the prior dialogue proof.

Every helper compares complete RAM/context/runtime, ordered original RAM,
resource/device/APU/controller events, full journals/DMA/tails, validation and
semantic resource reads, USER-mode native ABI, code/resource immutability and
global width-aware bounds. Combined mutated-state/event guards total14355.

Stage public contracts pass1024 cases/260 inert guards, using random synthetic
resource data and raw status/stack cases. Private contracts also pass1024/260,
including independent original C115 and render-mode instructions. Map100's
separate deeper tests and evidence remain in its author manifest/report. The
composition evidence above, not its standalone sampled-state test, establishes
whole-native arrival at map and bank4 boundaries.

## Replay

With baseline approved VASM/PYTHONPATH and PYTHONDONTWRITEBYTECODE=1:

```sh
out=$(mktemp -d port/build/recovery_bank_loader_XXXXXX)
python port/tests/recovery_bank_loader_stage_contract.py > "$out/public.log"
python port/tests/recovery_bank_loader_stage_contract.py --rom > "$out/private.log"
python port/tests/recovery_bank_loader_map_rom.py default right move_back > "$out/map.log"
```

The earlier stage-only composition can be replayed separately with
recovery_bank_loader_stage_rom.py and stops E179. Optional private terminal
snapshots require an explicitly supplied fresh RECOVERY_PRIVATE_SNAPSHOT_DIR
and exclusive-create files. They are diagnostic outputs only, never production
inputs. Do not publish snapshots, traces, resources, cartridge, firmware, disks
or audio. Manifest is the exact public source/test/report allowlist; future
116/130+ work is expressly excluded.
