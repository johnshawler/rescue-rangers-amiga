# Native first-stage completion through C77B

Frozen additive helpers 116 and 130–134 compose with the reviewed stage/map chain. Production remains static native 68020 game logic; no runtime opcode decoding or captured-state execution. The exact unsupported boundary is C77B, before the first gameplay frame. This is a host semantic milestone, not target display, playability or speed proof.

## ABI and scope

Entry: recovery_bank_loader_music_dispatch. A0 RAM2048, A1 context8, A2 counted journal134638, A4 runtime12, A5 immutable PRG131072. Native stack4096 disjoint bytes. All other existing ABI rules remain. ID116 is the separately reviewed bank4 object loader (journal60002). ID130 is the stage0 completion region (60002); ID131 genuine fade-in (0); ID132 existing fade continuation (0); ID133 real scheduler (74); ID134 stage music command0 initialization (60002). Resource records use kind0; ID134 APU records use kind1. ID130 has no external device events in its accepted current regions. Existing ID98 long NMI journal134638 and FFFF metadata sentinel remain unchanged.

Stage0 and music command0/CF0 are explicit bounded scopes. Unsupported stage indices, busy/deferred F6 mapper entry, malformed data and unsupported command branches reject inertly. No F1/runtime-bank spoofing, forced F6, suppressed audio or synthetic original stack frames are used. The native stack preflight validates before committing real RAM or journal writes. Raw flags and wrapped original stack remain byte-exact.

## Qualification

The 92408-byte composition SHA256 is 1ee9d5b9326a4016d7d28e6a54e4ab8b4260aecfddc67d3dc62a006550347184. All three continuous reset/menu/dialogue/stage histories finish at context c77b00ffffa5bfa7, mapper control1E/CHR00/CHR10/PRG05. Default:14625 helper calls,394 logical NMIs,2849 APU writes,4933 inert guards. Right choice:14786 calls,394 NMIs,2855 APU writes,4938 guards. Move-back:15027 calls,395 NMIs,2863 APU writes,5014 guards. Original runs first at every boundary; full RAM/context/runtime, ordered RAM/device/APU/controller effects, semantic resource reads and journals match. Host code/resource immutability, USER mode, width-aware read/write bounds and4096 stack guard are checked. Logical-NMI timing is not asynchronous target interrupt proof.

Finish contracts:2048 public and2048 private cases,1792 guards each, including all raw flags and stack offsets. Music contracts:769 public inert guards,256 private original cases plus768 guards. Public music tests do not claim successful arbitrary-resource execution; genuine successful music behavior is privately compared against original resource reads. Helper116 standalone coverage and independent report remain separate dependencies. No claim of exhaustive game state or target logging is made.

## Independent replay and restore

Restore every public_allowlist and dependencies entry in this manifest recursively, including JSON manifests and the stage-object SHA manifest contents, verifying SHA256 before running. Never restore cartridge, firmware, binaries, traces, audio or disks from source publication. Set VASM to an available vasmm68k_mot and provide machine68k in PYTHONPATH; set PYTHONDONTWRITEBYTECODE=1. Run python port/tests/recovery_bank_loader_finish_contract.py and python port/tests/recovery_bank_loader_music_contract.py for source-only public tests. Private authorized replay adds --rom to those commands, and runs python port/tests/recovery_bank_loader_music_rom.py default right move_back with the original input/rescue-rangers-europe.nes. Input SHA remains051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411. Generators require private input and emit only static translated logic; do not publish original resources or private generated traces.

Actual target integration must separately verify device consumers, stack depth, memory and rendering. ctrl90/mask1E/scroll0 with stage background CHR10 is expected; selected background view is CHR+4096, sprite view base. This milestone does not qualify horizontal scrolling, frame-loop gameplay, on-target audio fidelity or frame rate.
