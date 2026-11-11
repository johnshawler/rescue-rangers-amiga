# Newly authored stage resource initializer

This standalone static 68020 helper translates the complete bank-4 `$8000–$803E` initializer plus its fixed-bank caller `$C6B5–$C6BC` and the zero-deferred-audio branch of mapper helper `$FF53–$FF74`. It returns at `$C6BD`, directly before the existing player initializer. It is newly authored source, not recovered lost source or a playable-stage milestone.

## Exact entry and hardware obligations

Entry requires context PC `$C6B5`, RAM `$F6=0`, MMC1 PRG mode 3 (fixed last bank), and an empty serial latch. The selected initial bank can be any of the eight cartridge PRG banks. The caller must provide exclusive uninterrupted execution of this slice, and a bounded immutable 421-byte resource view corresponding to bank 4 CPU `$8193–$8337` inclusive. No code fetches, general CPU interpreter, captured state or proprietary table bytes are embedded in native source. The view is caller owned; the private actual-ROM test obtains it locally from the hash-checked input. No resource extract is delivered.

`$F6=0` is an explicit scope restriction, not proof that all stage starts take this branch. The original NMI checks bank-switch busy `$F5` at `$C0BF`; when busy it increments deferred-audio flag `$F6` at `$C0C3`. Nonzero `$F6` makes `$FF72` enter `$FF75`, select bank 3, drain the audio queue through `$8003`, call audio `$8000`, clear `$F6` at `$FFA9`, and restore the requested bank by jumping back through `$FF53`. That branch is not implemented here. The older reset-mapper analysis independently describes the same behavior. The normal non-deferred branch is covered, but no continuous title-to-stage execution has established this slice's live entry prerequisites. An adapter must not clear `$F6` or suppress real pending audio to force acceptance.

The event journal preserves all five original `$FFF0` writes in order: 4, 2, 1, 0, 0. This is a mapper effect contract, not direct Amiga hardware access. A future integration must consume these events in order with the resource-bank selection semantics. The test reference models the serial latch and verifies that only the fifth write publishes bank 4. The helper neither models nor claims asynchronous NMI injection, original instruction timing, or dummy bus cycles.

## ABI and original effects

- A0: disjoint writable 2048-byte original RAM image.
- A1: eight-byte context: big-endian PC word, A, X, Y, raw P, S, reserved.
- A2: writable 256-byte event journal. Record: big-endian address word, value byte, kind byte. Kind 0 is RAM store, 1 is resource read, 2 is mapper write.
- A3: immutable 421-byte resource view described above. Must not alias other buffers, native code or stack.
- Success: D0=37; all other native D/A registers preserved, native stack balanced, native CCR scratch. Context PC becomes `$C6BD`. Invalid PC or nonzero `$F6`: D0=-1 with buffers unchanged.

The original first JSR writes `$C6B9` high then low into page 1, the mapper helper returns, and the second JSR writes `$C6BC` into the same two stack slots. Byte wrapping is exact, including S=0. The bank-4 RTS restores the original S. All four stack writes remain in the ordered journal. The mapper helper writes `$F1/$F4=4`, increments `$F5` with byte wrap, then clears it after serial publication. The twelve resource reads initialize `$74/$75`, `$72/$73`, `$78/$79`, `$76/$77`, `$7A/$7B` and `$7C/$7D` in original order.

Every possible `$31` byte is supported as the original unsigned index, including values outside intended gameplay stage IDs; the bounded resource view covers every resulting address. A and N/Z reflect the last resource read, X equals `$31`, Y is unchanged, C is clear, V/D/I/B/unused status bits are preserved. No arithmetic with decimal adjustment occurs in this helper.

## Verification

Files:

- `port/src/recovery_stage_resource_init.s`
- `port/tests/recovery_stage_resource_harness.py`
- `port/tests/test_recovery_stage_resource_contract.py`
- `port/tests/recovery_test_stage_resource_init.py`
- `port/tests/recovery_test_stage_resource_composition.py`

The native helper assembles to 522 bytes and runs under machine68k's M68EC020 core. Tests compare every RAM/context byte, the full ordered event journal, unused journal tail, every actual native RAM store and resource read (including their interleaving), immutable resources, buffer guards, all preserved native registers and native stack balance. All native reads and writes have a global region whitelist. Nine rejected invalid-read probes include distant accesses and crossing the resource boundary; two probes reject resource writes.

The actual-ROM differential pins Europe ROM SHA-256 `051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411`, executes actual original instructions with py65, rejects unexpected reference reads/writes, and models serial mapper publication independently of native code.

The declarative contract uses invented resource bytes, RAM and context without any ROM or CPU reference. Its matrices cover every index/status pair (with every possible final A) and every stack/busy-byte pair, plus all 255 nonzero deferred flags and six wrong PCs.

The composition test executes `$C6B5 → $C6BD → $C700 → $C2A5`, using the unchanged player-init and fade-entry sources. Original and native RAM/context remain live with no patch between boundaries. Only host calling frames/journals are rearmed, and the identical immutable resource view is supplied again. The fade reference reuses the independently truth-table-tested Ricoh2A03 SBC ALU without modifying raw P.

Run all three scripts from the project root with `VASM` set to the approved `vasmm68k_mot` and `PYTHONPATH` set to the existing inspection `.deps` directory. Verified final results:

- 65,536 standalone actual-ROM cases passed; 2,424,832 ordered RAM/resource/mapper events.
- 131,333 ROM-free contract cases passed, including 261 inert invalid entries.
- 4,096 continuous three-helper compositions passed; 521,156 ordered effects.
- 262,144 independently expressed binary SBC truth-table cases passed before compositions.
- Python syntax compilation passed for all four new test/harness files.

All suites were rerun after adding interleaved actual native RAM/resource access checking and resource-boundary/write rejection probes. The [separate private target checkpoint](recovery_stage_resource_target.md) now verifies six continuous three-helper compositions on an emulated stock PAL A1200 with the same explicit entry restrictions.

## Remaining work

The nonzero deferred-audio branch, mapper/interrupt scheduler integration and entry reachability remain required before this becomes a general stage-start implementation. The composition stops before `$C2A5`'s `JSR $FF04`; frame synchronization and the rest of fade/stage loading remain untranslated. The private diagnostic does not establish continuous title-to-stage boot, full-stage rendering, audible output, stock-PAL timing or physical-hardware performance. Existing helper implementations and delivered disks remain unchanged.
