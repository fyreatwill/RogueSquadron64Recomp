# NEXT work unit — retail: 19E80 take vs sticky 0x8011A89F=1

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3295 selected `H-Ed0CompareSkip`: after last 19ED0
n=123, type `0x81` and `L_80019E7C` stay live (1229 each)
but `0x80019E80` always fallthroughs because `$s2[0]==1`.
`$s2` is `0x8011A89F`. The first sticky 1 appears on 19CC4
n=250 immediately after 19DFC n=124 (`yieldw=0x80149470`),
which is the yield-complete store at `0x80019E70`
(`sb $s1, -0x5761($at)`). Session 3292 already showed retail
viewer-window `0x8011A818` sends are 242/242 from
`0x80019F1C` (inside 19ED0), so retail must take 19E80.

## Competing hypotheses

- `H-RetailS2Cleared`: during 2.5–6.7 s, `0x80019E80` `$v0`
  is 0 or 2 (takes 19ED0). Physical `0x0011A89F` is written
  to 1 at `0x80019E70` and later cleared (expected clearer
  `0x80019F6C`) before the next 19E80.
- `H-RetailNoYieldStore`: viewer-window `0x80019E70` never
  stores; `0x0011A89F` stays 0/2 so 19E80 keeps taking. The
  port's yieldw=`0x80149470` path is extra.
- `H-RetailS2Stays1`: retail 19E80 `$v0` is also 1 during
  the viewer (fallthrough), so a different site must produce
  the 242 `0x8011A818` sends (would reopen s3292).
- `H-RetailCoverageInvalid`: whole-RDRAM 10000-write
  control, title `1024 @ 0x00790400`, viewer `0x800C28F0`,
  or `0x800C2E00` miss, or no 19E80 exec in 2.5–6.7 s.

## Discriminator

One independent retail Rice oracle, 25 s, eleven-Start.
Watches are physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`.

A viewer-window 19E80 census with `$v0 != 1` plus a later
clear of `0x0011A89F` selects `H-RetailS2Cleared`. Zero
19E70 stores and `$v0 != 1` selects `H-RetailNoYieldStore`.
19E80 `$v0==1` throughout 2.5–6.7 s selects
`H-RetailS2Stays1`. Missed controls is a failed instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

```
tools/oracle/build/rs64_oracle \
  --watch-write 0x0:0x800000 \
  --watch-write 0x0011A89F:0x0011A8A0 \
  --watch-pc 0x80019E80,0x80019E70,0x80019ED0,0x800C28F0,0x800C2E00 \
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll \
  --video rice
```

Log: `scratch/agent/s3296_retail_s2_gate.md` plus the
captured run log.
