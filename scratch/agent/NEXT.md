# NEXT work unit — retail: type-2 dispatch vs yield-publish

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3297 selected `H-RetailYieldPtrZero` and
`H-RetailYieldPtrUnpublished`: during the attract viewer,
`0x80019E04` `$v0` is always 0, `0x80019E0C` never runs,
and physical `0x00128D40` is never written. The scheduler's
only nonzero store to that word is `0x80019DC0` (`sw` of
msg+4 after `osSpTaskYield`), on type-2 dispatch
`L_80019D90`. Combined with s3295, the port's
`yieldw=0x80149470` is extra.

`L_80019D90` (`beq $v1, $s5` with `$s5=2`): if
`0x8011A8A0==0`, set it, then if `0x8011A89C==0` goto
`L_80019DCC` (idle start), else `jal osSpTaskYield`
(`0x80019DAC`) and `sw` at `0x80019DC0`.

## Competing hypotheses

- `H-RetailNoType2`: during 2.5–6.7 s, `0x80019D90` is
  silent. Retail never dispatches type 2, so the yield
  publisher is dead because its caller is dead.
- `H-RetailType2Idle`: `0x80019D90` is live and
  `0x80019DCC` is live; `0x80019DAC` / `0x80019DC0` stay
  0. Type-2 arrives while SP is idle, so no yield.
- `H-RetailType2Yields`: `0x80019DC0` executes (would
  contradict s3297's zero writes unless the store watch
  missed).
- `H-RetailCoverageInvalid`: whole-RDRAM 10000-write
  control, viewer `0x800C28F0`, or `0x800C2E00` miss, or
  no scheduler exec in 2.5–6.7 s.

## Discriminator

One independent retail Rice oracle, 25 s. Watches are
physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`.

Viewer-window 19D90=0 selects `H-RetailNoType2`.
19D90 live + 19DCC live + 19DC0=0 selects
`H-RetailType2Idle`. Any in-window 19DC0 exec selects
`H-RetailType2Yields`. Missed controls is a failed
instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

```
tools/oracle/build/rs64_oracle \
  --watch-write 0x0:0x800000 \
  --watch-write 0x00128D40:0x00128D44 \
  --watch-pc 0x80019D90,0x80019DAC,0x80019DC0,0x80019DCC,0x800C28F0,0x800C2E00 \
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll \
  --video rice
```

Log: `scratch/agent/s3298_retail_type2_yield.md` plus the
captured run log.
