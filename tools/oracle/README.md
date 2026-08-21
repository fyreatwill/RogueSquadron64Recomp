# rs64_oracle — ask the real machine

Every "does the game really do X?" question on this project has been answered
with our own recompiled runtime as the witness. That runtime is the thing under
test, so those answers were never independent. This tool runs the **retail ROM
under mupen64plus** and reports what actually happens, giving the second source
that iron rule 4 asks for.

## Setup (once)

    tools/oracle/build_core.sh      # mupen64plus core with DEBUGGER=1 (+ binutils, brew mupen64plus)
    tools/oracle/build.sh           # the front-end

The core must be built from source: Homebrew's bottle has no `Debug*` symbols
and the oracle refuses to run against it.

## Use

    tools/oracle/build/rs64_oracle \
      --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom  ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 180 --watch-write 0x1F3CC0:0x1F3CD0

    [watch] write [0x001f3cc0,0x001f3cd0] flags=0x5 idx=0
    [hit] w addr=0x001f3cc0 pc=0x800b1234 prev_pc=0x800b1230 t=41.2s n=1
    [oracle] done: 3 hit(s) in 180.0s wall, 10794 VI (~179.9s emulated)
    [oracle] exec-prev pc=0x8000c07c prev=0x800ab0dc n=59

`--watch-pc` also prints a lifetime `exec-prev` histogram: for each
exec hit, mupen's `PREVIOUS_PC` (the jal site that transferred here;
`$ra` is prev+8). Use that instead of overlay-aliased VRAM watches
when attributing a callee.

For a memory watch after the global `--hit-cap` has gone silent,
`--first-watch N` prints the first hit for watch index N and
`--pc-hist-watch N` prints a bounded writer-PC histogram for that watch at
shutdown. These are useful when a positive-control watch is intentionally
first in the list and must be removed without hiding the target attribution.
`--post-value-watch N` adds a phase-gated, bounded post-store word histogram
and a final physical-range FNV/nonzero summary; repeat it to sample multiple
watches in one run. `--post-value-pc` can force a post-store sample for
selected writer PCs after the title/hangar phase gate arms.

Exit status: 0 = hits, 3 = clean run with zero hits, 1/2 = setup error. The
VI count is emulated frames, so a run always reports how far the *game* got,
not just how long the wall clock ran.

`--oracle-debugger 0|1` and `--oracle-emulator N` expose the core's
`EnableDebugger` and `R4300Emulator` settings (defaults: `1` and `0`, the
pure interpreter). A debugger-off run cannot produce this tool's watches,
VI trace, or PIF trace: those are debugger callbacks. `--vi-poll` instead
reads the VI registers through the core's exported `DebugMemRead32` from a
frontend thread and works with the debugger disabled. It reports its first
nonzero width plus subsequent width/origin changes; pair debugger-on runs
with `--vi-trace` as its independent control. Treat a zero VI/hit summary
without `--vi-poll` as an absent instrument, not a boot-stall result.

## Three traps, all already paid for

**Addresses are PHYSICAL.** `r4300_write_aligned_word()` masks with
`0x1ffffffc` before the handler lookup, so the address that reaches the
breakpoint check has lost its KSEG0 prefix. A watch on `0x801F3CC0` never
fires — and reports a clean zero, which reads exactly like "the game never
writes here". The tool masks inputs with `0x1FFFFFFF` so both spellings work.

**Always run a positive control.** The first version of this tool reported zero
hits on a watch covering *all of RDRAM*, which is impossible; that is how the
physical-address trap was found. Before trusting any null, point a watch at
something that must fire:

    --watch-write 0x0:0x800000     # whole RDRAM: ~1.6M hits in 8 emulated seconds

Iron rule 1 applies to the oracle exactly as it applies to our own instruments.

**`m64p_breakpoint.endaddr` is INCLUSIVE.** `lookup_breakpoint()` tests
`address <= endaddr`. `--watch-write A:B` takes B half-open like everything
else and converts on the way in; if you touch that code, keep the conversion
or every watch quietly covers one extra word and attributes hits from outside
the range you asked about.

## Driving it

    --press 8:return,14:return,20:return --hold-ms 150

attaches `mupen64plus-input-sdl` and injects keys through
`CoreDoCommand(M64CMD_SEND_SDL_KEYDOWN/KEYUP, ...)`. Keys are names
(`return z x up down left right lshift lctrl space`) or raw SDL2 keycodes.
The key-to-button mapping is whatever `[Input-SDL-Control1]` holds in the
config; `--configdir DIR` materialises it so you can read it. The default has
controller 1 plugged in keyboard mode with `Start = key(13)` (Enter).

**Input is verified end-to-end**, not just delivered: the emulator is
deterministic, so two undriven 30 s runs agree to five significant figures on
writes per frame (2891.3, 2891.3 over all of RDRAM), while a run pressing
Start four times diverges to 2903.3 — 0.4% against 0.002% run-to-run noise.
Reproduce that A/B if you ever suspect the presses stopped landing.

### The button map is scancodes, and the default config lies

`--press` sends SDL2 **scancodes**, because `mupen64plus-input-sdl` matches
incoming values against scancodes while its config records SDL1-era keysyms.
Consequences, all measured against PIF RAM with `--pif-trace`:

- Sending keycode 13 (Return, which the config maps to Start) produces
  **C-Left**, not Start. Start is scancode **40**.
- The config's `A Button = key(304)` is unreachable by any keycode at all —
  304 is an SDL1 keysym with no SDL2 equivalent. A is scancode **225**.

Use the names, which are verified: `start a b z dup ddown dleft dright
cup cdown cleft cright l r`. Each was pressed and the resulting N64 button
word read back out of PIF RAM. If you change `[Input-SDL-Control1]`, re-derive
the table with `--pif-trace` — do not assume.

### Reaching the hangar

Dummy video (`ProcessDList` is a no-op) stays at width 320 / origin
`0x006dd280` forever, even with live PIF Start presses. Attach Homebrew
Rice; Glide64MK2 also stayed at 320 (s707, s1496):

    --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
    --press 6:start,11:start,16:start,21:start,26:start,31:start,\
            36:start,41:start,46:start,51:start,56:start

Measured phase timeline (`--vi-trace`), driven vs undriven:

| Phase           | undriven   | driven          |
|-----------------|------------|-----------------|
| 320 boot        | 0.5s       | 0.8s            |
| 640 intro       | 2.1s       | 2.4s            |
| 1024 title      | 49.7s      | **17.3s**       |
| 512             | 102.2s @ `0x690800` (attract demo) | **38.4s @ `0x6ab400/800` (HANGAR)** |

The hangar holds for the rest of the run once the presses stop. Keep pressing
past ~58s and it advances out of the hangar into a 640 phase at `0x6a2900`.
Origin distinguishes the two 512 phases: `0x690xxx` is the attract demo,
`0x6abxxx` is the hangar — the same buffer pair our port reports.

Do not read a null as evidence about a phase the run never reached: the whole
64 KB around the heap freelist takes **zero** writes undriven and **3,514,738**
with this schedule.

The RSP plugin is Homebrew's `mupen64plus-rsp-hle`, which handles MusyX audio
tasks. Audio is left unattached (core dummy). Video must be Rice for any
phase past boot 320; dummy video does not complete DLs, so the cinematic
never advances. Rice still answers **memory and CPU** questions, not pixel
questions. For what the microcode is supposed to emit, read
`docs/F5-UCODE-REFERENCE.md` instead.

## Questions worth asking it

- Does the retail game ever write the heap freelist header at physical
  `0x1F3CC0`, and from what PC? (items -405..-407 assume our writeback stomps
  something the game owns; the oracle can say whether the game itself ever
  touches it.)
- Is a given address ours or the game's, for any "who corrupted this?"
  question — the class that has eaten the most sessions on this project.
- What PC writes a structure we only see the aftermath of.
