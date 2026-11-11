# Private active NMI and scheduler target checkpoint

A new, separately invoked private diagnostic completes the honest FE90 idle
variant: reset FE24, first NMI/silent return, original startup task setup,
genuine no-ready scheduler scan, second logical NMI from FE90, complete initial
active music tick, original bank restore/RTI to FE90, and actual saved-task
resumption at C2A8. It executes 68 native calls to 31 distinct static helpers.
The two standard controller inputs are explicitly zero (no pressed buttons).
No readiness, continuation, frame, status or queue patch advances the chain.

The three shared reset-probe sources, every existing helper/host test, all
thirteen old reset/music payload/ADF pairs, all historical dumps, standalone
player/fade/stage probes and delivered Z/X disk are unchanged. The new builder remains private and is now included in full private
validation. Public validation runs only synthetic contracts, without building
this cartridge-bearing disk. Source publication records are kept separately.

## Private artifact and driver contract

Run `python port/tools/build_recovery_runtime_probe.py` with VASM configured.
The builder hash-checks the caller-owned Europe cartridge before creating any
output. Missing and wrong cartridges fail closed. Its report declares
`proprietary_inputs=true`: this disk carries 16KiB of bank3 cartridge data
and must never be distributed or described as source-only. Driver, private
boot, extract, payload, ADF, screenshot and Chip dump are under ignored
`port/build/`; logs are ignored. Public source contains no cartridge extract,
firmware, captured frame, or raw execution trace.

The native driver uses the unchanged helper contracts and one live RAM/context
pair. A3 points at the immutable private bank3 resource. Every call checks D0,
preserves/verifies D1-D7/A0-A6 and checks the native stack returns to its initial
position. Each call records an eight-byte context, all 2KiB original RAM and
its complete journal including unused tail. Snapshots are comparison outputs,
never inputs into original state. Buffer guards surround original RAM,
context, resource, stack and the entire snapshot array. The verifier rejects
out-of-Chip, overlapping, guard-overlapping and report-alias pointers.

The separate private boot allocates 795,648 cleared Chip bytes but reads only
the 47,354-byte payload rounded to disk sectors. The 748,000-byte snapshot
workspace is cleared by the operating system allocation, not stored as a
large zero disk payload. An earlier full-zero-payload experiment did not
finish disk loading within 600 frames; the final compact payload does. This
allocation change affects no original CPU state or helper semantics.

## Actual target execution

Final run used exactly:

- HEADLESS: `/workspace/scratch/43ecf79622a5/amiga-recovery-tools/headless-recovered-title`
- PUAE_CORE: `/workspace/scratch/43ecf79622a5/amiga-recovery-tools/libretro-uae/puae_libretro.so`
- Supplied firmware directory: `artifacts/a1200-system`
- `PUAE_MODEL=A1200OG`, 600 requested frames, new runtime ADF only.

The log confirms actual CPU=68020, FPU=0, MMU=0, JIT=0; PAL 50Hz; Chip size4
(2MiB), Fast size0, bogo size0; CPU, memory and blitter cycle-exact enabled;
and successful completion of 600 runs and 600 video callbacks. The independent
verifier's optional `--amiga-log` checks these effective settings and runtime
lines, rather than trusting the launch environment alone.

Execution command, from the project root with HEADLESS and PUAE_CORE set to
the pinned paths above:

```sh
PUAE_MODEL=A1200OG RAM_OUT="$PWD/port/build/recovery-runtime-probe-chip.bin" \
  "$HEADLESS" "$PUAE_CORE" "$PWD/port/build/recovery-runtime-probe.adf" \
  "$PWD/artifacts/a1200-system" 600 "$PWD/port/build/recovery-runtime-probe.ppm" \
  > logs/recovery-runtime-probe-amiga.log 2>&1
python port/tests/verify_recovery_runtime_probe.py \
  port/build/recovery-runtime-probe-chip.bin \
  --amiga-log logs/recovery-runtime-probe-amiga.log
```

Use PYTHONPATH pointing to the inspection `.deps` directory for py65 and
machine68k imports. No physical Amiga execution is claimed.

## Independent verification

`verify_recovery_runtime_probe.py` derives expectations by executing the
hash-pinned original cartridge continuously for **16,826 instructions**. It
calls the real reference `nmi()` twice and never reloads a native output into
the reference. The original idle scan stops only after FEA3's backward jump to
FE90, not the first instruction arrival at FE90. Subsequent helper selection
follows real original PC/event state. It compares:

- All **68 full RAM snapshots** and **68 full context snapshots**.
- In original per-call order: **40 mapper, 2,248 PPU, 14 APU, 36 controller,
  and 94 resource journal records**, including all unused bytes.
- **512 DMA bytes**, original hardware/handler frames and nested task frame.
- All **16,384 immutable resource bytes**, final full RAM/context, stack and
  guards. Reference mapper remains live across every publication and ends at
  control1E, CHR0=00, CHR1=10, PRG6 with an empty serial latch.

Raw reference P remains untouched. An explicitly named architectural B=0/U=1
comparison view is used only for context comparisons; original saved frame
bytes are exact. Final no-pad state is PC=C2A8, A=10, X=10, Y=FF, P=24, SP=BC.
F6 naturally remains zero in this reset-generated case; the driver neither
forces nor clears it at return. Full snapshots compare its value after every
call. The unchanged general active-return helper separately covers all F6
values. Countdown04 and original C593 caller return remain stacked.

The frozen host proof was rerun unchanged: 256 direct 67-call chains and
256 honest idle 68-call chains pass, including native access whitelists,
ordered original RAM effects, ABI, guards and resource-read contracts. Its
controller-two input differs from this no-pad target, explaining final P20
versus target P24 without changing either oracle.

## Negative and preservation tests

`test_recovery_runtime_probe_rejection.py` starts and ends with positive
baselines. **789** dump mutations are rejected, covering all snapshots,
contexts, F6, journal/tail corruption, final RAM/context, resource, marker,
status/count, stack, guards, pointer range/partial overlap/guard overlap/exact-end boundaries and dump shape. **22**
historical cross-mode dumps in the original review workspace (the aggregate
checks all sixteen other current diagnostic dumps) are rejected, including all thirteen old
reset/music modes and standalone probes. **15** emulator-log mutations are
rejected.

`test_recovery_runtime_build.py` builds in isolated directories. All thirteen
old payload/ADF pairs match historical bytes; all thirteen historical Chip
dumps separately pass their original verifier. Eight shared source-only
modes build without a cartridge. Five old private modes plus this new private
driver reject both missing and wrong cartridges before output files. The new
private payload/ADF reproduce byte-identically in an independent directory.
The test verifies ignored private outputs and unchanged hashes for its enumerated historical artifacts, input/firmware
files and source files, including the archived title disk. The count depends
on the files present in the validation workspace. The separately preserved
delivered Z/X disk was hash-checked independently and is not a test input. Python compilation passes.

Useful private logs:

- `logs/recovery-runtime-probe-amiga.log`
- `logs/recovery-runtime-probe-verify.json`
- `logs/recovery-runtime-probe-rejection.json`
- `logs/recovery-runtime-build-tests.log`
- `logs/recovery-runtime-legacy-verifiers.log`
- `logs/recovery-runtime-frozen-host.log`

## Hashes and remaining work

- Payload: `3a6128bfba17f6f5f748cc8fd4b5f2ab29370ccefdd4d28d681711162723fe28`
- Private ADF: `928170f81ada1754563b7de20e3da2214aefd0aa8d75ad92ec1d1976f0e44528`
- Target Chip dump: `840420e13d2f3ca924f4e5aa712c0276fabf738e9ffbf2312920f1fcea681cc8`
- Europe cartridge: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`
- Bank3 resource: `01b6e72da88510e9bfa3071ba0a782cd585401d55c5bf01e7fe1a79baf22f7ab`
- Pinned headless: `eaab1fcd8e1fd86d24a16db76a6318ffe537ffe1811000716e45a365b0885848`
- Pinned PUAE: `84878d50ed9aa9419ce8876998acc45fe1e8dd1600f67f470dae8e2a037a4456`
- Supplied A1200 firmware: `6d43840d4099a74170ea0f0425b6257c3891ebcaa39c4d1840075a9ab22b5707`
- Unchanged archived title disk: `03b774d76a6b547ff6b4b3ffd71428d381247f4802a40bab1a56eb3d1ea2b475`
- Separately preserved delivered Z/X disk: `6ffec7c18b1eef69c70048fc84a0b19f0a3daf2b34d67ae98fdb3fbcc765eb17`

The next untranslated instruction is **C2A8 PLA**, followed by the
SEC/SBC countdown continuation. Subsequent active audio durations, envelopes,
callbacks, remaining commands, nonempty video queues and deferred work remain
incomplete. This is a bounded coherent target checkpoint, not a continuing
persistent runtime, full boot, reset-to-stage path, playable game, audible
Paula renderer, game-speed benchmark or physical-hardware proof. The emulator
runs 600 frames, but the diagnostic stops after its semantic checkpoint; this
does not represent 600 original gameplay frames.
