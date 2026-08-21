# NEXT work unit (s2166) — retail writer of cutscene `$a2+0x50`

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2165 selected `H-RetailExecsValidPtr`: retail executes
`0x8003E944` / `0x800A87A8` at VI 640 / `0x00696100` with KSEG0
`$s1` / `$v0`. Table:
`scratch/s73_post_a_scene/s2165_cinematic_pc_oracle.txt`.

The crash-site pointers are loaded, not constants. Cutscene chain:

- `0x800A879C` `lw $v0, 0x50($a2)`  — `$a2` in `0x800C7ABC..0x800CA5F0`
- `0x800A87A0` `lw $v0, 0($v0)`
- `0x800A87A8` `lwc1 $f2, 0x44($v0)`  — retail `$v0` `0x800CA748`..

First sampled slot: `$a2=0x800C7ABC`, word at `+0x50` =
`0x800C7B0C` (physical `0xC7B0C`). That region is overlay/data,
not the `0x802xxxxx` heap, so it is the stable watch.

Ask the retail oracle who writes `0xC7B0C`. Do not S32-address,
NULL-skip, re-flip default-on, or add a wait/slot guard. Do not
rebuild the game. Oracle GPR print is already wired.

## Competing hypotheses and discriminator

- `H-RetailWriterNamed`: watch 1 takes write hits with a named
  writer PC (histogram + first logged write) at or before VI 640.
  That PC is the ORIGIN candidate for the pointer the crash load
  consumes.
- `H-PreViInit`: watch 1 write count is 0, but `--post-value-watch 1`
  (or a same-run exec at `0x800A879C` with `$a2=0x800C7ABC`) shows a
  nonzero KSEG0 word. The pointer was stored before watches arm on
  first VI (boot/DMA). Next is overlay/DMA attribution, not a guest
  store at 640.
- `H-UnstableSlotBase`: exec hits at `0x800A879C` have `$a2` outside
  `0x800C7ABC..0x800CA5F0` (or never `0x800C7ABC`). The s2165 slot
  table is run-specific; recensus `$a2` before treating a zero write
  count as "no writer".
- `H-CoverageFailure`: whole-RDRAM watch does not print the 10000
  removal line, `[gpr-ctl]` is missing, or `--vi-trace` never prints
  a 640 row. Null watch-1 counts are unevaluable.

Positive control: watch 0 whole-RDRAM 10000-callback removal,
`[gpr-ctl]`, at least one `[vi]` 640 line, and either a watch-1
write/`[hit] x` at `0x800A879C` or a post-value snapshot of watch 1.
`--pc-hist-watch 1` is the writer table; a GPR print on `0x800A879C`
must show `$a2` before treating the `0xC7B0C` watch as that slot.

s2165 heap words (`0x8025A580`..) are run-specific — do not watch
them as if they were static.

## Exact commands

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 45 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-write 0xC7B0C:0xC7B10 \
      --watch-pc 0x800A879C,0x800A87A0,0x800A87A8 \
      --first-watch 0 --pc-hist-watch 1 --post-value-watch 1 --vi-trace \
      > scratch/agent/oracle_s2166_cutscene_a2_50.log 2>&1

Do not rebuild the game. Do not flip `get_rsp_microcode`.
If a writer PC appears, do not skip/allow/guard this iteration —
name it, then a later unit asks whether the port's store is missing
or stores 0.
