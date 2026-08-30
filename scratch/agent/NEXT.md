# NEXT work unit — port: which recv-dispatch skips the 19ED0 gate?

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3294 selected `H-SchedLoopAliveNoEd0`: after last
19ED0 n=122 the F50 send returned and loop head `19CC4`
continued through n=4045 while SENT n=3 blocked in E0B4.
Zero further 19ED0/19F1C. `L_80019ED0` is reached from
`L_80019E7C` (type `0x81` path `L_80019DFC` when yielded-task
word `0x80128D40` is zero) only if `$s2[0] != 1`. At SENT n=3
the live loop already shows `19CC4` n=248 `s2b0=0x01`. Keep
s3288 fade / s3289 SENT / s3290 inner / s3293 gate / s3294
loop probes; this unit is the dispatch after recv return.

## Competing hypotheses

- `H-NoType81`: after last 19ED0, recv returns but the type
  byte at `0x80019CDC` is never `0x81` (loop eats 0/1/2 and
  jumps to `19CC4`).
- `H-Type81YieldBusy`: type `0x81` arrives, `L_80019DFC`
  runs, but `0x80128D40` is nonzero so the yield-restart path
  is taken instead of `L_80019E7C`.
- `H-Ed0CompareSkip`: `L_80019E7C` runs, but `$s2[0]==1` so
  `0x80019E80` does not take `L_80019ED0`.
- `H-DispatchCoverageInvalid`: SENT n=3 / 19F1C n=41 /
  19CC4 after last 19ED0 miss, or the new
  type/19DFC/19E7C/19E80 probes are silent at width 640.

## Discriminator

One Debug port run, 30 s from `build/`, SIGKILL.
`ROGUESQ_LOG_M5_POSTWAIT=1`. Keep s3288/s3289/s3290/s3293/s3294
probes. Add a width≥640 always-print at the type-byte load
(`0x80019CDC`), `L_80019DFC`, `L_80019E7C`, and the
`0x80019E80` taken vs fallthrough. 19F1C n=41 and 19CC4 n=248+
must still print (same-run positive controls). Join to SENT
n=3 `E0B4` and last 19ED0.

A live type census with zero `0x81` after last 19ED0 selects
`H-NoType81`. Type `0x81` plus `19DFC` without `19E7C`
selects `H-Type81YieldBusy`. `19E7C` plus fallthrough at
`19E80` (`$s2[0]==1`) selects `H-Ed0CompareSkip`. Missed
controls or a silent new probe on 19CC4 n=248+ is a failed
instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

Fixup: `tools/apply_s3295_scheduler_dispatch.py` (also hook
from `fixup_game_funcs.py`) at `0x80019CDC`, `L_80019DFC`,
`L_80019E7C`, and `0x80019E80` taken vs fallthrough.
Rebuild Debug. Then from `build/` with the ROM present:

```
env ROGUESQ_LOG_M5_POSTWAIT=1 ./RogueSquadron64Recomp
```

30 s, SIGKILL. Log: `scratch/agent/s3295_port_scheduler_dispatch.md`
plus the captured run log.
