# NEXT work unit — retail: 19E04 yield-pointer vs 19E70 path

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3296 selected `H-RetailNoYieldStore`: during the
attract viewer, `0x80019E80` always takes (`$v0` is 0 or 2,
never 1) and `0x80019E70` never executes. Combined with
s3295, the port's yield-complete `sb` of 1 at 19E70 (after
19DFC `yieldw=0x80149470` in `0x80128D40`) is extra.
`0x80019E04` is `beq $v0, $zero, L_80019E7C` after
`lw $v0, -0x72C0($v0)` from `0x80128D40`.

## Competing hypotheses

- `H-RetailYieldPtrZero`: during 2.5–6.7 s, `0x80019E04`
  `$v0` is 0 (beq to 19E7C). Physical `0x00128D40` stays 0
  or is written only as 0. 19E70 remains silent because the
  nonzero-yield successor is dead.
- `H-RetailYieldPtrLive`: `0x80019E04` `$v0` is nonzero at
  least once in the viewer, so retail has a yield pointer
  but still does not execute 19E70 (different successor
  than the port).
- `H-RetailYieldPtrUnpublished`: `0x80019E04` runs with
  `$v0==0` and no write to `0x00128D40` in the viewer; the
  port's `0x80149470` publisher is extra.
- `H-RetailCoverageInvalid`: whole-RDRAM 10000-write
  control, title `1024 @ 0x00790400`, viewer `0x800C28F0`,
  or `0x800C2E00` miss, or no 19E04 exec in 2.5–6.7 s.

## Discriminator

One independent retail Rice oracle, 25 s, eleven-Start.
Watches are physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`.

Viewer-window 19E04 `$v0==0` on every row plus 19E70 still
0 selects `H-RetailYieldPtrZero`. Any in-window `$v0 != 0`
selects `H-RetailYieldPtrLive`. Zero writes to
`0x00128D40` with `$v0==0` selects
`H-RetailYieldPtrUnpublished` as well as Zero. Missed
controls is a failed instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

```
tools/oracle/build/rs64_oracle \
  --watch-write 0x0:0x800000 \
  --watch-write 0x00128D40:0x00128D44 \
  --watch-pc 0x80019E04,0x80019E70,0x800C28F0,0x800C2E00 \
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll \
  --video rice
```

Log: `scratch/agent/s3297_retail_yield_ptr.md` plus the
captured run log.
