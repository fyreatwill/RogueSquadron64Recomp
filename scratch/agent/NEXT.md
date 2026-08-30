# NEXT work unit — port: type-2 idle vs yield-publish

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3298 selected `H-RetailType2Idle`: during the attract
viewer, type-2 `L_80019D90` is live (n=259, `$a0=0x80128C80`)
and every visit takes idle `L_80019DCC` (`$v0=0` at
`0x8011A89C`). `0x80019DAC` / `0x80019DC0` stay 0, matching
s3297's zero writes to `0x80128D40`. Retail type-2 never
yields because SP is idle, not because type-2 is absent.

s3295 first saw the port's extra `yieldw=0x80149470` on
19DFC n=124, after last 19ED0 n=123 still had `yieldw=0`.
The only scheduler store to that word is `0x80019DC0` on
the busy arm of `L_80019D90`. After last 19ED0 the port
also logged 1230 type-`0x02` 19CDC rows.

## Competing hypotheses

- `H-PortType2Idle`: during the viewer and around last
  19ED0, 19D90 is live and 19DCC is live; 19DAC / 19DC0
  stay 0. Same successor as retail; the extra yieldw has a
  different publisher.
- `H-PortType2Yields`: 19DC0 executes (especially in the
  gap after last 19ED0 n=123 where yieldw first becomes
  `0x80149470`). Port type-2 finds SP busy and publishes
  msg+4.
- `H-PortType2BusySkip`: 19D90 is live but 19D94 skips
  (`0x8011A8A0` already set); neither 19DCC nor 19DC0.
- `H-PortCoverageInvalid`: viewer `[m5-postwait]` entry,
  `[phase]` `640 @ 0x0066A500`, SENT n=3, last 19ED0, or
  19CDC type-`0x02` miss, or the new 19D90/19DCC/19DC0
  probes are silent at width 640.

## Discriminator

One Debug port run, 30 s from `build/`, SIGKILL.
`ROGUESQ_LOG_M5_POSTWAIT=1`. Keep s3288 fade / s3289 SENT /
s3290 inner / s3293 gate / s3294 loop / s3295 dispatch
probes. Add a width≥640 always-print at `L_80019D90`,
`0x80019DAC`, `0x80019DC0`, and `L_80019DCC`.

Viewer-window 19D90 live + 19DCC live + 19DC0=0 selects
`H-PortType2Idle`. Any 19DC0 (especially after last 19ED0
n=123, storing `0x80149470`) selects `H-PortType2Yields`.
19D90 without 19DCC/19DC0 selects `H-PortType2BusySkip`.
Missed controls is a failed instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

Fixup: `tools/apply_s3299_type2_successor.py` (also hook
from `fixup_game_funcs.py`) at `L_80019D90`, `0x80019DAC`,
`0x80019DC0`, and `L_80019DCC`. Rebuild Debug. Then from
`build/` with the ROM present:

```
env ROGUESQ_LOG_M5_POSTWAIT=1 ./RogueSquadron64Recomp
```

30 s, SIGKILL. Log: `scratch/agent/s3299_port_type2_successor.md`
plus the captured run log.
