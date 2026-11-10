# Remote restore checkpoint

Verified source commit: `c8664b08299eeebfb6159198c6e0184d369109fc`.
Verified source tree: `cdcbcd7a14c7d2c6d84c82bd7d11998aee90b12a`.

A new checkout was cloned from the public GitHub repository, rather than copied from the active working directory. Only manifest-pinned private fixture files and the hash-checked supplied cartridge/Kickstart were restored locally with `tools/restore_private_inputs.py`; none was committed.

The restored checkout rebuilt title ADF SHA-256 `03b774d76a6b547ff6b4b3ffd71428d381247f4802a40bab1a56eb3d1ea2b475`, identical to the original recovered title milestone. All five private differential/component suites and all five cycle-exact PAL A1200 menu/display scenarios passed again. The new reset-RAM helper additionally passed 1,536 original-ROM/native cases, all 2,064 ordered writes per case, 1,536 completed-boundary rejections and 65,790 invalid-context rejections.

The public synthetic-only workflow also passed for this exact source commit: https://github.com/johnshawler/rescue-rangers-amiga/actions/runs/42924744537.

The commit contains 38 text source/documentation files. Cartridge, firmware, extracted assets, captured state, image references and compiled game binaries remain outside Git. Public CI cannot replace the private original-ROM and target-emulator validation; the latter requires authorized inputs.

This confirms a restorable early title/menu foundation plus a newly written isolated reset helper. It does not recover or certify the missing later gameplay/audio source, remove the title fixture dependency, or establish full-game speed.
