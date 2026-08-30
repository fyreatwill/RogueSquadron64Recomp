# NEXT work unit — port: who leaves SP busy at first yielding type-2

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3299 selected `H-PortType2Yields`: after last 19ED0
n=123, the first type-2 (`19D90 n=83`, `$a0=0x80128C80`)
takes `0x80019DAC` / `0x80019DC0` and stores
`yieldw=0x80149470` because `0x8011A89C==1`. Pre-last-19ED0
type-2 was idle (`19DCC n=82`, `sp89c=0`). 19D94S=0.
Retail (s3298) never takes 19DC0.

In the same join, `19CDC n=247` is type `0x01`
(`$a0=0x80128CE0`) between last 19ED0 and the first
19DC0. Scheduler stores to `0x8011A89C` include idle-start
`0x80019DD4` (`sb $s1, -4($s3)`) and clearer `0x80019FE4`
(`sb $zero, -0x5764($at)`).

## Competing hypotheses

- `H-Type1StartsSp`: the type-1 handler after last 19ED0
  idle-starts SP (or equivalent) and leaves `89C==1` for
  the next type-2.
- `H-IdleStartUncleared`: last 19DCC n=82's `0x80019DD4`
  store of 1 is still live; `0x80019FE4` does not run in
  the gap.
- `H-Other89CWriter`: some other PC writes 1 into
  `0x8011A89C` in the gap (not 19DD4 / not type-1).
- `H-BusyCoverageInvalid`: viewer `[m5-postwait]` entry,
  `[phase]` `640 @ 0x0066A500`, SENT n=3, last 19ED0, first
  19DC0, or the new 19DD4 / 19FE4 / type-1 probes are
  silent at width 640.

## Discriminator

One Debug port run, 30 s from `build/`, SIGKILL.
`ROGUESQ_LOG_M5_POSTWAIT=1`. Keep s3288 fade / s3289 SENT /
s3290 inner / s3293 gate / s3294 loop / s3295 dispatch /
s3299 type-2 probes. Add a width≥640 always-print at
`0x80019DD4`, `0x80019FE4`, and type-1 dispatch
(`0x80019CF0` / `L_80019D10`).

Type-1 live in the gap + 19DD4 after it + 19FE4 silent
before first 19DC0 selects `H-Type1StartsSp`. 19DD4 only
on last 19DCC and 19FE4 silent selects
`H-IdleStartUncleared`. 89C becomes 1 with neither
selects `H-Other89CWriter`. Missed controls is a failed
instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

Fixup: `tools/apply_s3300_sp_busy_writer.py` (also hook
from `fixup_game_funcs.py`) at `0x80019DD4`, `0x80019FE4`,
and type-1 `L_80019D10`. Rebuild Debug. Then from `build/`
with the ROM present:

```
env ROGUESQ_LOG_M5_POSTWAIT=1 ./RogueSquadron64Recomp
```

30 s, SIGKILL. Log: `scratch/agent/s3300_port_sp_busy_writer.md`
plus the captured run log.
