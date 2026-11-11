# Recovery fixed-bank NMI continuation to audio entry

This helper continues the proven first-NMI prefix through bank selection and queue dispatch, stopping before the first banked audio instruction. It does not execute an audio command, update audio channels, restore banking or return from NMI. Previous helpers are unchanged.

## Original path and supported boundary

Original PAL ROM SHA256: `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`. Source is fixed PRG bank 7, CPU `$C000–$FFFF`; file offset `16 + 7*16384 + address - $C000`.

`src/recovery_nmi_audio_entry.s` translates `$C0BF–$C0F2`:

- `$C0BF–$C0C1`: test bank-busy byte `$F5`; only zero is supported.
- `$C0C7–$C0D9`: publish bank 3 using five serial writes to `$FFF0`, retaining full shifted bytes `03 01 00 00 00` in order.
- `$C0DC–$C0E2`: read queue index `$DB` and current slot `$DC+index`; only an in-range index and nonempty slot are supported.
- `$C0E4–$C0EF`: PHA the command, write empty marker `$88`, increment X, update `$DB` modulo eight, then PLA the command. X is **not masked**: index 7 yields X=8 and `$DB=0`.
- `$C0F0–$C0F2`: execute original JSR semantics, pushing return address `$C0F2` high then low, and stop at bank-3 `$8003` before its opcode is fetched/executed.

The temporary PHA store occurs at the same original stack address subsequently overwritten by the JSR high byte. Both writes are preserved in order. No bank-3 bytes need to be extracted or embedded to prove this entry boundary.

## ABI and guard contract

Export `recovery_nmi_audio_entry`:

- A0: writable 2048-byte original-layout RAM.
- A1: eight-byte context `{big-endian PC word, A, X, Y, P, SP, reserved}`.
- A2: writable 22-byte mapper journal: big-endian count word followed by five `{big-endian address word, data byte, busy byte}` records.
- Valid, disjoint buffers and exclusive synchronous access are required.
- Guards: PC=`$C0BF`, `$F5=0`, `$DB<8`, and `$DC+[$DB] != $88`. All are checked before buffer or RAM mutations.
- D0=1 means bounded completion at `$8003`; D0=-1 rejects unsupported entry, busy-bank state, invalid queue index or empty slot, leaving all three buffers unchanged.
- D1–D7/A0–A6 are preserved; CCR scratch; native stack balanced.

Final original A is the queued command, X is original queue index plus one, Y unchanged, and SP is original SP minus two modulo 256. P retains V/D/I/B/U; C reflects CMP #`$88`, N/Z reflect the PLA-restored command. Reserved context byte is unchanged.

The journal records explicit logical bank publication, with zero busy byte for the guarded path. It does not write NES addresses on Amiga, execute an MMC1 emulator or silently select native audio resources. RAM `$F1` is deliberately not changed: it retains the bank that the original NMI intends to restore later, even though the publication requests temporary bank 3.

## Original-ROM proof

With `VASM` pointing to `vasmm68k_mot`, py65 and machine68k available:

```
python port/tests/recovery_test_nmi_audio_entry.py
```

The reference executes actual original fixed-bank instructions, stopping at `$8003` without executing any banked opcode. The native code is assembled for 68020 and executed by machine68k M68EC020. No source-semantic native model substitutes for machine execution.

Verified coverage:

- 2296 standalone cases: all eight queue indices crossed with all 255 supported command bytes, plus 256 varied status/SP cases using command `$F0`.
- Each case compares all RAM/context/journal bytes and the exact ten-event sequence: five mapper publications and five RAM stores (temporary PHA, queue empty marker, updated index and two JSR stack bytes).
- 256 continuous reset→first yield→explicit hardware NMI→audio-entry compositions across seven helpers. No RAM/context patches are inserted. The original oracle uses `nmi()` at the first-yield boundary, including hardware interrupt stack effects, and stops before `$8003` executes.
- Composition compares the full merged event stream, including 25 mapper publications, 2199 PPU events, OAM DMA snapshot, handler/queue RAM and original stack writes. Startup command `$F0` has been dequeued, `$DB=1`, and restore-bank shadow `$F1=6` remains unchanged.
- 2296 completed-boundary inert rejections and 66046 unsupported-input rejections: all other PCs, 255 nonzero busy values, 248 invalid indices and all eight empty-slot cases.
- Guard regions, preserved native registers, balanced stack, bounded execution, unexpected writes and full journal preservation on failure.

## Limits and next work

The busy-bank deferral path and empty-queue path to `$C0F6`/bank-3 `$8000` are rejected, not approximated. This is the supported nonempty startup branch.

At `$8003`, this helper has not executed any bank-3 audio instruction. The separate `recovery_audio_reset_command` helper now covers the guarded startup `$F0` command and its return. Other commands, further queue draining, bank-3 `$8000` update, restoration of `$F1`, register restoration and RTI remain separate work. The original interrupt frame remains active. A ready timer slot does not mean the scheduler has resumed.

The NMI is an explicit logical event at the selected `$FE8D` boundary, not timing emulation or a claim about when the NES would first interrupt. There is no complete boot, audible output, gameplay, hardware-performance or physical-Amiga claim. Original ROM/assets/dumps and generated binaries remain outside the source deliverable.
