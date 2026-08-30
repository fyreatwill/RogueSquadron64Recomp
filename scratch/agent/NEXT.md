# NEXT work unit — retail 626C/6274/6288/62B4 path into jal 0x800A62B4

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

Session 3311 selected `H-FlagByteSkip`: port `cinematicLoopBody`
always takes `beq 0x800A6274` (`$a0=0`) while count at
`0xB28($s3)` is 0..148 vs limit-10=1190, so `jal 0x800A62B4`
never fires. Retail Session 3310 fires that jal at 48.1 s.
Ask retail which skip it takes into the jal.

## Resume context

MIPS in `cinematicLoopBody`:

- `0x800A626C` `beq $v1,$zero → 627C` after `sltu` (taken when
  count >= limit-10; **bypasses** the flag check).
- `0x800A6274` `beq $v0,$zero → 62EC` on `$a0` byte (taken
  skips the jal). Port: always taken.
- `0x800A6288` `bne` after `isCinematicActive` (taken skips
  the jal if the pointer is already live).
- `0x800A62B4` `jal cinematicInitializer`.

## Competing hypotheses

- `H-RetailTimeBypass`: 626C stays `taken=0` until ~48 s, then
  `taken=1` (count >= limit-10), 6274 silent on that window,
  6288 not taken, 62B4 fires. Port flag skip is hardware-like
  until the time threshold; the port-only stop is never
  reaching count 1190.
- `H-RetailFlagSet`: 6274 `taken=0` (`$a0!=0`) before the
  time threshold, then 62B4 fires. Port `$a0=0` is then the
  mismatch (controller / `0x800B0B1C`).
- `H-RetailJalOther`: 62B4 fires without 626C/6274/6288
  describing the path (unexpected predecessor).
- `H-CoverageInvalid`: missing 10000-write, `[gpr-ctl]`, VI
  `640 @ 0x0066A500`, cinematic entry, or 62B4 itself.

## Discriminator

One independent retail Rice 90 s run. Watch exec of
626C / 6274 / 6288 / 62B4 plus cinematic entry and
`0x800AF4B8`. Detail those PCs so `$v0`/`$v1`/`$a0` print.
Whole-RDRAM write watch is the positive control.

62B4 n>=1 plus 626C `taken=1` on the last pre-jal window
with 6274 silent/`taken=1` never on a fall-through row
selects `H-RetailTimeBypass`. 6274 `taken=0` (`$a0!=0`)
on a row that continues to 62B4 selects `H-RetailFlagSet`.
62B4 without those predecessors selecting either path
selects `H-RetailJalOther`. Missing whole-RDRAM / VI-640 /
entry / 62B4 is coverage-invalid.

## Exact commands

Follow `scratch/agent/s3310_retail_b0934_writer/run.sh`:

```
tools/oracle/build/rs64_oracle
  --core .../libmupen64plus.dylib
  --rom  .../rogue_squadron.z64
  --video .../mupen64plus-video-rice.dylib
  --watch-write 0x0:0x800000
  --watch-pc 0x800A5D80,0x800A626C,0x800A6274,0x800A6288,0x800A62B4,0x800AF4B8
  --detail-watch on 626C,6274,6288,62B4,AF4B8
  --secs 90 --hit-cap 20000 --vi-trace --vi-poll
```

No `--press`. No port build. No M5 Step 3. No audio/output
change. Require 10000-write, `[gpr-ctl]`, VI
`640 @ 0x0066A500`, cinematic entry `0x800A5D80`, and 62B4.
