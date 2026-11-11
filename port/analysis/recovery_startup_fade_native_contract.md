# ROM-free startup fade CI contract

New test: `port/tests/test_recovery_startup_fade_native_contract.py`.
No existing source, report, private test, aggregate or helper was edited.
The test hashes the five completed fade-deliverable files before and after
execution and asserts they are unchanged.

Run from the repository root with VASM set to the approved assembler and
PYTHONPATH including the inspection `.deps` directory:

```
python port/tests/test_recovery_startup_fade_native_contract.py
```

The test imports only the shared ROM-free native execution harness. It does
not import py65, read a cartridge or captured resource, or depend on a private
oracle. Its independent declarative state/effect model uses integer signed
ranges for arithmetic overflow rather than the helper's bitwise flag logic.
All original RAM, raw context and reserved byte, ordered store records and
unused journal tail are compared. The native harness checks register ABI,
stack balance, guards and global read/write bounds.

Verified results:

- 16,493 accepted synthetic cases.
- 1,280 distinct unsupported PCs rejected without mutation.
- 343,866 exact ordered RAM stores.
- 2,048 explicit stacked-FFFF to PC0000 RTS regressions, covering both the
  equal50 and negative-level termination branches, every raw status byte,
  and SP FC/FD/FE/FF so countdown and return-byte reads cross page-one wrap.
- 11 explicit negative access checks, including distant reads/writes,
  cross-buffer widths, code writes and native-stack boundary crossing.
- Five frozen deliverable hashes unchanged; Python compilation passes.

Coverage includes every raw status byte, every stack position plus explicit
wrap-edge cross products, every countdown byte, every delay reload byte,
C594 outer-yield setup, palette source values around subtraction/overflow
boundaries in every palette slot, and fade-level addition/termination
boundaries. This bounded suite intentionally does not repeat the expensive
private exhaustive ROM matrix. It adds no target/runtime/gameplay claim.

Full result: ignored `logs/recovery-startup-fade-native-contract.log`.
