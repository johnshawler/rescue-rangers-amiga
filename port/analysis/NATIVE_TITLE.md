# Native original title-menu coroutine

`src/native_rescue_title.s` directly translates PRG bank 2 `$A000–$A0C8`, its original embedded text data `$A0C9–$A0E0`, and fixed-bank sound-request enqueue `$F379–$F391`. The same hash-checked European ROM as `NATIVE_GAME.md` is used. See `native-title-original-disassembly.txt` for byte-level provenance.

## API and continuation boundaries

`rescue_title_step`: A0 = 2KiB original-layout game RAM, A1 = two-byte host context `{phase, original_X}`. Initialize both context bytes to zero. All D/A registers preserved; CCR scratch. The original menu is a coroutine that calls the frame scheduler `$FF04`; the native function returns at those exact yield points, without translating the old 6502 cooperative task scheduler.

- phase 0: enter original `$A000` player-count menu, initial input evaluation.
- phase 1: resume after yield `$A022`, at `$A025`; decrement the timer before checking fresh input. Returns phase 1 if still waiting.
- phase 2: resume at `$A06C`, the Chip/Dale character-selection menu. Entry is original yield `$A069`; subsequent waits are `$A086`.
- phase 3: original menu reached its RTS at `$A0C8`. It is complete. Further calls are inert. The caller must stop here until the following game's systems are translated. Do not equate this with playable gameplay.

The second context byte preserves the original X scratch value across scheduler yields, principally to retain exact `$F379` sound-queue scratch behavior. It is not a CPU emulator or instruction-stream state.

## Original user-visible behavior

Inputs are already-computed new presses in `$14`, from `rescue_update_controllers`.

- `$50=0`: one player; `$50=1`: two players.
- Select toggles player count. Right chooses two players; Left chooses one. Start takes priority over other buttons.
- The title cursor's OAM X at `$0203` is `$28` for left, `$88` for right.
- Starting two-player mode ends the menu immediately.
- Starting one-player mode fills the original PPU text queue `$0360–$0377`, marks `$19=$FF`, and yields into Chip/Dale selection. Left/Right changes its cursor; Start confirms. Choosing the right-hand character swaps 15 pairs in `$0340–$035D` and patches `$05A2/$05A4/$05A6/$05A8` with the original constants.
- Countdown `$BF:$BE` decrements each main-menu frame. Reaching zero sets `$50=1,$B8=1` and hands off to the original demonstration path. This does not mean a native demo exists.
- Completing the menu hides all 64 OAM entries by writing `$F8` to `$0200+4n`.
- Navigation queues original sound request `$27` at `$DC+[$DA]` only if the entry is empty (`$88`), advancing `$DA` modulo eight. Actual sound playback is not implemented. Original queue index precondition is `$DA` in 0..7.

## Display integration

The function changes original RAM, not Amiga display memory. Redraw the native background/sprites after relevant OAM changes. On character-selection entry, apply the original PPU command queue to the native nametable before redrawing. Queue format follows `$C119`: address high, address low, inclusive count (so payload length is count+1), then payload; a high byte with bit 7 set terminates. Do not continue into untranslated gameplay just because phase 3 was returned. Do not show a captured gameplay image as a response to Start and imply it is running.

## Executed verification

`python port/tests/test_rescue_title.py` runs 4,592 differential yield intervals, executing original ROM bytes through py65 and assembled 68020 bytes through machine68k. It covers every 256-bit-pattern input byte, both player selections, full and empty sound queues, all three active continuation phases, every countdown low byte with high bytes 0/1/255, and the captured frame-200 title RAM through two-player, Chip, Dale, and timeout sequences.

Every non-stack RAM byte (1792 bytes), both context bytes, boundary guards, preserved native registers and balanced native stack are checked. Original 6502 page-one return/temporary stack bytes are excluded from cross-architecture equality; the native routine is separately checked to leave that entire RAM page untouched. Original `$FF04` scheduler calls are yield boundaries, not executed. The sound helper is executed from its actual original bytes. No 68020 source-semantics model substitutes for machine-code execution.

This is authentic native title interaction and a bounded title-to-game handoff, not a full game port, sound implementation, PAL timing proof, or performance result.

## Exact frame-200 snapshot continuation

For a fresh menu entry use `{0,0}`. For the supplied captured frame-200 RAM, initialize the host context to `{1,$FF}` instead. The captured original task has `$82=$B9` (saved stack pointer); RAM `$01BA=$FF` is saved Y, `$01BB=$FF` is saved X, and `$01BC/$01BD=$24/$A0` are the scheduler return address, resuming at `$A025`. This is the main-menu countdown continuation. Phase 0 would not reset resources, but would omit that first countdown decrement and is not the precise snapshot continuation. The captured timer is `$02E7` (743). The end-to-end snapshot scenarios in the test use this verified context.

## Native PPU queue adapter and its proof

`src/native_rescue_title_queue.s` exports `rescue_title_apply_queue(A0=RAM,A1=1024-byte nametable)`, preserving every D/A register, CCR scratch. Invoke only when `$19` indicates a pending queue. It translates the original fixed-bank `$C115–$C139` consumer, clears `$19`, and writes the nametable directly instead of issuing PPU register writes. Its supported adapter scope is nametable addresses `$2000–$2FFF` and increment-by-one mode, collapsed into the supplied 1024-byte nametable. It is not a general PPU, CHR uploader, palette queue, or mapper implementation.

Original character-choice queue writes exactly:

- Nametable `$226–$22D`: `8C 91 92 99 A4 A4 A4 A4`.
- Nametable `$232–$23A`: `8D 8A 95 8E A4 A4 A4 A4 A4`.

There are no CHR or palette changes in this command queue. The existing title CHR supplies the glyphs.

`tests/test_rescue_title_queue.py`: PASS 1,024 comparisons of actual original 6502 `$C115` execution and assembled native 68020 execution, including 512 exact original queues over randomized RAM/nametables and 512 bounded varying queues. Checks all 2048 RAM bytes, all 1024 nametable bytes, boundary guards, register preservation, balanced stack, and the exact 17 original title tile addresses.
