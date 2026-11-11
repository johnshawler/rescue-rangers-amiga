# General logical NMI prefix at scheduler idle

New static native 68020 translation, `recovery_idle_nmi_prefix`, accepts a logical NMI at **any original PC and stack pointer**, including the authentic FE90 boundary returned by the general scheduler. It executes the hardware frame, handler saves, applicable video/palette work and four task timers, stopping **before C0BF audio/bank dispatch**. No existing helper, builder, probe, aggregate, README or delivered ADF is changed.

## Contract

A0 is writable 2048-byte original RAM. A1 is eight-byte context: big-endian PC word, A/X/Y/raw P/S/reserved. A2 is writable 454-byte output: big-endian record count, capacity 49 four-byte records (address word, data byte, kind byte), then a 256-byte DMA snapshot at fixed offset 198. Buffers, code and host stack must be disjoint and exclusively owned during the synchronous call. D0=1 succeeds; D0=-1 rejects inertly. D1-D7/A0-A6 are preserved; host stack balances and CCR is scratch.

All interrupted PCs, stack positions and raw status bytes are accepted. The caller supplies an explicit NMI event, not an automatic event inferred from PPUCTRL or CPU cycles. PPUCTRL bit 7 is therefore not an entry restriction. The hardware frame stores actual PC high/low and status with B clear/U set; PHP stores B/U/I set, then original A/X/Y are pushed, with page-one wrapping. Raw context B clears; raw context U remains as supplied, matching the independent reference's representation of the unused bit. Frame status is always architecturally correct irrespective of raw U.

When F0 or 9A is nonzero, the original branch skips all video work and advances timers. Every queued request remains untouched, including unsupported queue/CHR requests. There are no PPU records or DMA writes in this case. Otherwise **any nonzero 19, 1A, 1B, 1C or 1D is an inert unsupported rejection**, before RAM/context/output changes. Those queues and CHR requests need their real translators, not clearing adapters. Palette request 18 is supported both absent and present. A present request publishes 32 live RAM palette bytes and clears only that consumed request, preserving original event order.

Successful video paths publish OAM DMA, scroll/control/mask, and either 10 records without a palette or 49 with one. Unused journal records remain untouched; DMA always occupies offset 198, and is untouched on video-skip. PPU-status read data zero is an explicit unused-result placeholder; actual reference return values vary. This journal describes architectural effects, not physical Amiga MMIO or a PPU implementation. No mapper/controller/APU access occurs in this slice.

The four timers follow the original states precisely: state 1 decrements its byte timer, and becomes state 4 only when that decrement reaches zero. Other states are unchanged. A zero timer wraps to 255. Final PC is C0BF, X=16, Y=0, S=entry S−7 modulo 256. Final A/C derive from the fourth timer, Z=1/N=0/I=1, and D/V retain their original values. The caller's reserved byte is unchanged.

## Verification

Run from repository root with the approved VASM path and inspection dependencies on PYTHONPATH:

- `python port/tests/test_recovery_idle_nmi_contract.py`
- `python port/tests/recovery_test_idle_nmi_prefix.py`
- `python port/tests/recovery_test_idle_nmi_stage_composition.py`

The public contract suite uses invented data and declarative state/effect operations, with no cartridge, trace or reference CPU. The private suite separately uses actual hash-pinned Europe ROM execution and real `nmi()`, bounded to the original NMI instruction range and whitelisted bus reads/writes. Both cover all 65,536 interrupted PC values, all raw status bytes, all stack positions, palette present/absent, timer underflow/expiration, and 512 video-skip cases retaining pending requests. Public rejection coverage checks every nonzero byte value at each unsupported queue/CHR field.

The native harness globally bounds every read and write, checks crossing/distant negative reads, preserves all ABI registers, checks balanced host stack, and compares full RAM/context, exact journal including unused tail, ordered merged RAM/hardware effects and DMA publication-time bytes. Python syntax compilation also passes.

The composition uses one live native RAM/context and one live reference CPU/bus through the unchanged stage resource, player, fade, frame-yield and general scheduler helpers. It performs two genuine no-ready scans, ending FE90, then invokes the real reference NMI and the new helper. No RAM/context/status patch is inserted between calls, and no captured state or continuation is supplied. Initial test inputs explicitly declare synthetic C6B5 entry, F6=0, task zero selected, inactive task slots, and empty video queues; these are not a claim that reset/title naturally generated that state. Existing stage resource mapper/view prerequisites remain in force. Actual mapper events and immutable resource reads are checked before NMI; NMI introduces no mapper effects. The waiting task becomes ready only through the actual NMI timer, and pending palette publication is consumed by the real branch.

Verified composition result: **4,096 continuous cases**, **811,717 ordered stage-prefix/NMI effects**, plus **262,144 binary SBC truth-table cases** for the preceding fade reference. Each case includes two separate scheduler scans whose ordered stores are also checked.

## Remaining boundary

C0BF must still execute bank-busy handling, queued/active audio, bank restoration and RTI before the general scheduler can resume C2A8. This helper deliberately does none of those steps. General video queues and CHR requests remain unsupported when video is enabled. No complete persistent frame, reset-to-stage flow, complete fade, rendered stage, audible output, target probe, physical-Amiga validation, cycle accuracy or performance claim is made. No proprietary extract, captured state, trace dump or binary is included in these new public files. No publication was performed.

Final standalone execution: **66,048 ROM-free accepted cases**, **1,275 inert unsupported cases**, and **66,048 independent actual-ROM cases** passed. The new helper assembles to **486 bytes**. Test logs are `logs/recovery-idle-nmi-contract.log`, `logs/recovery-idle-nmi-private.log` and `logs/recovery-idle-nmi-stage-composition.log`.

## Subsequent integrated checkpoint

The helper-local limits above describe this component when introduced. The
[bounded resident runtime target](recovery_runtime_target.md) now verifies the
reset-generated idle/NMI/initial-music/RTI/task-resume path on an emulated
stock PAL A1200. Stage frame-yield compositions remain separate synthetic-entry
proofs. Public and private aggregate scripts include these helper suites.
There is still no complete native gameplay loop, audible output or speed claim.
