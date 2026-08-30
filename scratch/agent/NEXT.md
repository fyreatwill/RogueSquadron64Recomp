# NEXT work unit — retail: does type-1 start gspTask / write 89C?

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3300 selected `H-Type1StartsSp`: after last 19ED0
n=123, 19FE4 n=123 clears `0x8011A89C`, then type-1
`19CDC n=247` (`$a0=0x80128CE0`) takes `L_80019D10` with
`sp89c=0`, starts `gspTask` `0x800377C8` at `0x80019D58`,
and `0x80019D34` (`sb $s1, 0($s4)`, `$s4=0x8011A89C`)
leaves `89C==1` for the next type-2. 19D78=0. After first
19DC0, 19FE4 never reruns (19ED0 abandoned).

Retail (s3298) type-2 always idle-starts (`19D90=19DCC`,
19DC0 exec=0). Unknown: whether retail type-1 at the
attract viewer starts the same `gspTask` / writes 89C,
and if so who clears it before type-2.

## Competing hypotheses

- `H-RetailType1StartsSp`: viewer-window `0x80019D10` and
  `0x80019D58` are live (`$a0=0x800377C8` at 19D58);
  `0x80019D34` execs; type-2 still idle-starts (19DCC), so
  a clearer (`0x80019FE4` or equivalent) or ordering keeps
  89C=0 for type-2.
- `H-RetailType1Absent`: `0x80019D10` is silent in the
  viewer window. Type-1 never runs, so 89C stays 0.
- `H-RetailType1BusySkip`: `0x80019D10` is live but
  `0x80019D78` is live and `0x80019D58` is 0 (does not
  start SP / does not write 89C).
- `H-RetailCoverageInvalid`: whole-RDRAM 10000-write
  control, viewer `0x800C28F0`, return `0x800C2E00`, or
  s3298's 19D90/19DCC idle pair miss.

## Discriminator

One independent retail Rice oracle, 25 s. Watches are
physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`. No `--press`.

19D10+19D58 live in the viewer window + 19DCC still 1:1
with 19D90 selects `H-RetailType1StartsSp`. 19D10 silent
selects `H-RetailType1Absent`. 19D10 live, 19D78 live,
19D58=0 selects `H-RetailType1BusySkip`. Missed controls
is a failed instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

```
tools/oracle/build/rs64_oracle \
  --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom  ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x80019D10,0x80019D34,0x80019D58,0x80019D78,0x80019FE4,0x80019DCC,0x800C28F0,0x800C2E00 \
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll
```

Log: `scratch/agent/s3301_retail_type1_sp.md` plus the
captured run log.
