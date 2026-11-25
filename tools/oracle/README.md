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

**FCR31.FS (s7841):** upstream mupen emulates the FS (flush-denormals) bit only on x86/SSE. On arm64 the core
produced denormal results that real hardware (RS64 runs FCSR 0x01000800, FS=1) flushes to zero.
`patches/arm64-fcr31-fs-ftz.patch` (applied by build_core.sh) makes host FPCR.FZ follow FCR31.FS; the core
prints `[core] s7841 arm64 FPCR.FZ follows FCR31.FS: on`. `RS64_ORACLE_FTZ=0` restores the old no-flush core.
Captures taken before s7841 carry those denormals.

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
when attributing a callee. Each logged exec hit also prints `$v0`
(gpr[2]), `$s1` (gpr[17]), `$a0` (gpr[4]), and `$a2` (gpr[6]) from
`DebugGetCPUDataPtr(M64P_CPU_REG_REG)`, plus live VI width/origin.
When the watched execution is `osViSwapBuffer` (`0x80035500`), the shutdown
summary also includes a bounded unique table of `(VI origin, PREVIOUS_PC,
physical $a0 framebuffer)` rows for live width 640.
The first breakpoint of any kind prints `[gpr-ctl]` so a zero exec
count still proves the GPR instrument fired. Exec hits log past
`--hit-cap` (up to 64 printed execs) so a whole-RDRAM positive
control cannot silence them.

`--pc-phase-log ORIGIN[,ORIGIN...]` phase-gates additional watched-execution
rows to live 640-width VI origins. This keeps a high-frequency boot watch
from changing the driven route while collecting target-phase GPR returns.

`--pc-field-dump A[,B...]` records a bounded unique table at the selected
execution PCs, phase-gated by `--pc-phase-log` or `--pc-phase-log-width`. Each
row includes `$s0`, `$s1`, `MEM_W($s0+0x60)`, `MEM_BU($s0+0x22)`, `$v0`, and
`MEM_HU($s1+0x22)`, with per-PC hit and overflow summaries at shutdown.

`--pc-task-dump A` records phase-gated `OSTask` rows at execution PC
`A`. It treats `$a0` as the task pointer and reports the task ordinal,
`data_ptr`, `data_size`, output and yield fields, plus `data_ptr+0x100` and
its physical RDRAM address. `--pc-task-type N` selects the dumped type
(default `2` = audio, `1` = gfx, `0` = any). It uses the explicit
`--pc-phase-log-width` buckets when present, or the `--pc-hist-phase`
buckets otherwise, and reports invalid-pointer, type-mismatch, overflow,
and unique `(type, task_ptr, output_buff, output_buff_size)` counts at
shutdown.

`--watch-pc-range START:END` arms one execution breakpoint across a half-open
guest-PC range. It is useful when the per-PC watch list would exceed the
debugger's breakpoint capacity; each hit still reports its exact PC and GPR
fields.

`--mode-dump-pc A` selects a watched execution PC and prints each observed
640-wide mode descriptor's pointer plus both field origins and yScale values.
It is bounded to 256 printed rows and is intended for use with `--watch-pc`.
`--post-swap-table-pc A` latches a 640-wide execution at an already-watched
PC and joins it to the following VI callback when the new origin is one of the
two target 640 origins. Each joined row includes the pre-call origin, swap
caller, physical `$a0`, and the most recently dumped mode descriptor. Rows are
bounded at 256; the shutdown summary reports latched, joined, pending, dropped,
and overflow counts.

`--post-swap-any-vi` changes that join's filter to accept the next VI callback
at any width or origin. Use it only when the watched execution itself is the
phase boundary; it is a diagnostic escape hatch for transitions such as the
retail 640-to-1024 title switch.

`--vi-context-table-pc A` performs the same bounded join for the retail
`__osViNext` context at a watched 640-wide execution PC. It records the
context state, frame pointer, mode pointer, current field, both mode field
origins/yScales, and `framep + field.origin` candidates before joining to the
following target-origin VI callback. The shutdown summary reports latched,
joined, pending, dropped, and overflow counts.

For a memory watch after the global `--hit-cap` has gone silent,
`--first-watch N` prints the first hit for watch index N and
`--pc-hist-watch N` prints a bounded writer-PC histogram for that watch at
shutdown; repeat the option to collect multiple watch histograms in one run.
`--phase-origin-watch N` retains bounded write rows for watch `N` during the
512-wide hangar phase and propagates the setting to pointer targets created by
`--phase-pointer-watch`. Use it with phase snapshots when identifying whether
a pointer-backed table is also the source of a later copied record.
`--pc-hist-phase ORIGIN[:WIDTH]` adds a repeatable phase bucket keyed by VI
origin and width (default width is 640). It prints the matching VI-row count
and one writer-PC histogram per selected watch at shutdown, allowing origin
buckets to be compared in the same run.
These are useful when a positive-control watch is intentionally
first in the list and must be removed without hiding the target attribution.
`--post-value-watch N` adds a phase-gated, bounded post-store word histogram
and a final physical-range FNV/nonzero summary; repeat it to sample multiple
watches in one run. `--post-value-pc` can force a post-store sample for
selected writer PCs after the title/hangar phase gate arms.

With `--ordinal-join`, each retained target write also reports its exact store
address, instruction/effective address, source register/value, scalar mask,
and pre-store word. The retained task rows are used internally as publication
event ordinals for the nearest same-phase join.

When `--pc-task-dump` is enabled, shutdown also prints each retained task row
with its publication `event` ordinal. With `--ordinal-join`, the
`ordinal-writer-join` table aggregates nearest-task ordering by phase, watch,
writer PC, and exact effective destination; `before` and `after` are relative
to the nearest same-phase task, while `no_task` is an instrument-boundary
count.

The `post-value` rows describe the entire aligned word, including bytes the
instruction did not write. They do not establish the value written by an `sb`
or `sh`. `post-store-scalar` rows separately count the bytes written by `sb`,
aligned `sh`, and aligned `sw`, comparing them with the source register saved
before the store. `mismatch` must be zero before using these samples as store
evidence. `unsupported` counts other instructions or unaligned addresses.
These rows use the same phase gate and sampling budget as `post-value`.

Run the byte-lane regression test with:

    cc -O1 -g -Wall -Wextra -std=c11 -fsanitize=undefined \
      -I../rs64-oracle/src/mupen64plus-core/src/api \
      -o /tmp/rs64-test-store-samples tools/oracle/test_store_samples.c
    /tmp/rs64-test-store-samples

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
(s6742, angrylion video: presses at 6..56 s left it in the hangar through 110 s;
adding a press at 61 s gave the 640 phase at 79.7 s. That phase is the Star Wars
opening crawl, 640x300, buffers 0x6a2400/0x644800 + 0x500. `--fb-dump` arms on
the FIRST VI of the given width, which for 640 is the boot intro; add
`--fb-arm-after SECS` to keep dumps from arming before that time.)
Origin distinguishes the two 512 phases: `0x690xxx` is the attract demo,
`0x6abxxx` is the hangar — the same buffer pair our port reports.

Do not read a null as evidence about a phase the run never reached: the whole
64 KB around the heap freelist takes **zero** writes undriven and **3,514,738**
with this schedule.

### RSP plugin for retail-frame runs: VU-fixed cxd4 (s7816)

The retail-frame scripts (g3_menu_pair, g3_ai_gap_pair, g3_showroom_pair, g3f_retail_pan, oracle/run_m4_retail_pcs,
s7816_oracle_rsp_ab) `source tools/oracle/rsp_plugin.sh`, which loads a cxd4 with its 5 VU defects fixed (s7815: VCR,
VCH, VABS, VMRG, VMADN/VMADL clamp; CEN64 and our LLE agree on all five). Build it once with
`zsh tools/oracle/build_cxd4_patched.sh` (copies cxd4 to ../rs64-oracle-cxd4p; the rs64-oracle tree is never edited).
`RS64_ORACLE_RSP=stock` restores the old plugin, any other value is taken as a dylib path. A missing plugin exits 3.

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

`--debug-write VADDR:VALUE[:WIDTH[:ARM_S]]` writes one guest word on the first VI at WIDTH (default 320) at or after
ARM_S wall seconds. The port mirrors it with `ROGUESQ_DEBUG_WRITE=VADDR:VALUE:WIDTH:ARM_S` (fires on the VI width
change; s7820: append `:in` to fire on the first frame at WIDTH at or after ARM_S with no switch), so both arms can be put into the same state, e.g. rngSeed `80003470:1:512:85` at the mission flight switch (s6750).

`--exec-trace PC[:MAX[:PEEK]]` prints one compact `[xtrace] n vi ra peek pc= v0= a3=` row per execution of PC from
the `--debug-write` poke on (from boot without one), past `--hit-cap`; `--exec-trace-also PC` (repeatable, max 8) adds
probe PCs to the same row stream. The port mirrors it with `ROGUESQ_RAND_TRACE=<file>` (rand 0x80003430 call sites via
tools/fixup_rand_trace.py, plus the advanceNpcOnCurvedPath probes 0x8006BEC8/$a3 and 0x8006C018/$v0); align the two
with `tools/g3_rand_align.py RETAIL_LOG PORT_TXT` (s6751).

## Saves (`--save-dir`, s6800)

`--save-dir DIR` sets the Core `SaveSRAMPath`, so the game reads and writes
`DIR/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep` (512 B, 4 Kbit EEPROM).
Put a copy of the save you want there; never point it at, or copy over, the
user-wide `~/Library/Application Support/Mupen64Plus/save/` file. An empty
dir boots a fresh save (the game formats it on boot). The tools/ pair runners
use `<run>/retail/savedir`.

s6839: the oracle calls `ConfigSaveFile()` at exit, and until s6839 that persisted
the per-run `SaveSRAMPath` (and `--shot-dir`'s `ScreenshotPath`) into the
user-wide `mupen64plus.cfg`. Every later run WITHOUT `--save-dir` then silently
booted the last `--save-dir` run's EEPROM (found: s6812's save, mission selector
B40=0x0D instead of the swapped save's 2). The oracle now snapshots both values
at startup and restores them before saving, and prints `[oracle] save dir: ...`
for every run. Check that line before trusting any save-dependent result.
Scripts that copy a save over the user-wide `.eep` (the pre-s6800 route, e.g.
scratch/s6748/retail.sh) are unsafe: use `--save-dir`.

## Deterministic runs: `--det` (s7817)

By default two oracle runs of the same ROM and press schedule are NOT comparable on animated frames, for two reasons:

1. `--press`, `--hold-ms`, `--fb-dump` delays and `--secs` are wall-clock seconds, fired from host threads.
2. mupen64plus-core's `RandomizeInterrupt = True` (the default) jitters PI/SI interrupt timing with `rand()`, which the core
   seeds with `srand(time(NULL))`.

`--clock vi` makes every SEC value mean SEC*60 emulated VIs; presses and dumps fire from the VI callback on the emulator thread.
`--det-core` sets `RandomizeInterrupt = False` for the run only (the user's value is restored before the exit ConfigSaveFile).
`--det` is both. Measured: two `--det` runs gave 82/82 byte-identical 2 MB framebuffer dumps over title -> hangar; VI clock alone
still diverged from VI ~2115. `--det-video` (angrylion Parallel=False) and `--det-input` (keyboard-only Control1) also exist and
were shown NOT to be needed. Compare series with `tools/s7817_oracle_det.py A B --ctl`.

**Default since s7818:** `tools/oracle/rsp_plugin.sh` sets `ODET=(--det)` (`ORACLE_DET=0` restores wall clock + randomized
interrupts), and the retail-only launchers `tools/s7816_oracle_rsp_ab.sh` and `tools/g3f_retail_pan.sh` splice it in. The
`tools/g3_*_pair.sh` scripts do not: their port arm swaps the owner save (g3_port_capture.sh SAVE_FROM), so they cannot be run.

## Narrow watches in one frame: `--hit-vi-window A:B` (s7818)

Under `--det` the same VI is the same machine state, so a watch on a few bytes, gated to emulated VIs A..B, names the reader and
writer of one word in one frame. Hit lines then carry `vi=` and `val=` (the word at that moment).

**Self-read trap (fixed s7818):** the oracle's own `pDebugMemRead32` (every `--fb-dump` word, the `val=` sample) goes through
the core's bp-checked read handler, so before s7818 a read watch inside a dumped range fired on every dump word, attributed to
whatever guest PC was current (often a `nop`). Those hits are now counted in `[oracle] self-read hits suppressed=N` and not
attributed. Any pre-s7818 read-watch count over 0x600000-0x800000 taken with `--fb-dump` is inflated by 1 per word per dump.
Check that a hit PC disassembles to a load/store before trusting it.

## FPU registers and stack words on exec hits (s7842)

`RS64_ORACLE_FPR=0,2,20` appends ` fpr: f0=.. f2=.. f20=..` (COP1 single words, FR-mode aware via the core's regs_simple
pointers) and `RS64_ORACLE_SPW=20,74` appends ` spw: 20=.. 74=..` (guest words at $sp+off, hex) to every `--watch-pc` hit line.
Values are the state BEFORE the watched instruction executes. Used to replay a guest FP expression offline in IEEE float32
(scratch/s7842/replay.py, chase_cmp.py) and diff its operands against the port's tools/apply_s7842_chasehex.py log.

### Picture holds in VIs (s7921)

`--vi-holds N` prints `[vi-hold] vi=A..B len=L t=.. width=W origin=O pc_hits=h0->h1` for every run of >= N
consecutive VIs that show one framebuffer. An origin exactly one scanline (W*2 bytes) away from the hold's first
origin is the other interlaced field of the same buffer and does NOT end the hold (the 512 menu alternates
0x656400/0x656800 per field; without this every hold reads as a swap). `pc_hits` is the `--watch-pc` hit counter
at both ends, so a watched function can be placed inside a hold. `--hit-vi` adds `vi=<emulated VI>` to every
`[hit]` line (after prev_pc; off by default so existing parsers see unchanged lines). Positive control: the boot
holds at VI 81..88 / 89..97 (8/9 VIs, 320 wide) appear in every run. s7921 retail numbers (Start/A every 6 s from
6 s): every waitForMusyXAudioTaskDone spin (0x80091EC4 -> 0x80091F44, 8-9 VIs each) sits inside a 15-19 VI hold;
hangar entry = VI 2602..2618 (17 VIs, wait) then 2619..2741 (123 VIs, mallocCraftSelectionData at 2628).
