# NEXT work unit — port jal cinematicInitializer at 0x800A62B4

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

Session 3310 selected `H-RetailLateInit`: retail holds
`0x000B0934==0` for 972 advancer calls, then
`cinematicLoopBody` `jal 0x800A62B4` stores KSEG0 `0x800D9780`
at 48.1 s. Port s3308 still skips every advancer on `$v1=0`.
Ask the port which skip keeps that jal from firing.

## Resume context

The jal is inside the already-running loop (s3307 loop-head
live). Gates immediately before it:

- `0x800A626C` `beq` after `sltu` of `0xB28($s3)` vs
  `lw 0x44($s4->+0x1904)` minus 10
- `0x800A6274` `beq $v0,$zero` on `$a0` byte
- `0x800A627C` `jal isCinematicActive` / `0x800A6288` `bne`
  skip if ptr already live (should NOT skip on the port's null)

Then `jal cinematicInitializer` at `0x800A62B4`.

## Competing hypotheses

- `H-JalUnreached`: `0x800A6260` region never executes (the
  loop body takes an earlier skip of this block).
- `H-TimePredSkip`: `0x800A626C` is always taken; the count/time
  sltu never becomes true.
- `H-FlagByteSkip`: `0x800A6274` is always taken (`$a0` byte 0).
- `H-JalFires`: `0x800A62B4` does fire (then the store/overlay
  dispatch, not the skip, is the mismatch).

`isCinematicActive` returning 1 would contradict s3308's null
word; include the `0x800A6288` row as a same-run control, not a
lead hypothesis.

## Discriminator

One port build, one 120 s run (same-binary retry if the first
launch dies at VI 320 before marks, as s3307/s3308). Table of
626C / 6274 / 6288 / 62B4 with `$v0`/`taken`. Keep s3306 loop
and s3308 advancer tables.

Silent 62B4 plus silent 6260-region selects `H-JalUnreached`.
626C `taken=1` on every printed row with 6274/62B4 silent
selects `H-TimePredSkip`. 6274 `taken=1` with 62B4 silent
selects `H-FlagByteSkip`. 62B4 n>=1 selects `H-JalFires`.
Missing mark-all / VI-640 / cinematic-entry / loop-head is
coverage-invalid.

## Exact commands

Follow `tools/apply_s3306_cinematic_loop.py` / `apply_s3308_stage_advancer.py`:
inject diagnostic marks into `funcs_27.c` (`cinematicLoopBody`),
import the same transform from `N64Recomp/fixup_game_funcs.py`,
rebuild, run from `build/` with ROM present, SIGKILL at 120 s.
Arm the existing s3306/s3308/s3305 mark-all env vars.

Require 626C/6274/6288/62B4 mark-all, s3306 7/7, s3308 6/6,
VI `640 @ 0x0066A500`, cinematic entry, loop-head. No `--press`.
No M5 Step 3. No audio/output change.
