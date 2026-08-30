# NEXT work unit — port: does 0x80019F1C send after SENT n=3?

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3292 selected `H-RetailSpSchedulerProducer`: every
retail viewer-window send to `0x8011A818` has
`prev_pc=0x80019F1C` inside `spTaskSchedulerThread`
(`0x80019BF4`..`0x8001A018`). The jal loads `$a0=0x8011A818`,
`$a1=0`, `$a2=0` (NOBLOCK) and is skipped when
`lbu 0x80128D44 == 0` (`L_80019F24`). Session 3291: retail's
matching recv at `0x8000C0B4` returns every time. Session 3290:
the port's SENT n=3 enters that recv and does not return.
Keep s3288 fade / s3289 SENT / s3290 inner probes; this unit
is a port instrument of the now-named retail producer.

## Competing hypotheses

- `H-PortSchedSendMissing`: after `[s3290-stall] SENT n=3` /
  `E0B4` n=41, `0x80019F1C` never fires (flag `0x80128D44`
  stays 0, or the scheduler never reaches the jal). SENT n=2
  still shows the send (positive control).
- `H-PortSchedSendLost`: `0x80019F1C` fires with
  `$a0=0x8011A818` after SENT n=3 `E0B4`, but `R0B4` still
  missing (send happens, blocking recv does not take it).
- `H-PortSchedSendBeforeRecv`: `0x80019F1C` fires after SENT
  n=3 starts and before `E0B4` (or only before SENT n=3), so
  the NOBLOCK send is a lost wakeup against an empty queue.
- `H-PortSchedCoverageInvalid`: SENT n=3 / viewer / 640 /
  `2D50` n=3 miss, or the new 19F1C/19F24 probe is silent
  while SENT n=2 still returns.

## Discriminator

One Debug port run, 30 s from `build/`, SIGKILL.
`ROGUESQ_LOG_M5_POSTWAIT=1`. Keep s3288/s3289/s3290 probes.
Add a width≥640 always-print at `0x80019F1C` (jal taken) and
`L_80019F24` (flag-zero skip), logging `$a0` and
`MEM_BU(0x80128D44)`. SENT n=2 must show a 19F1C send
(same-run positive control). Join to SENT n=3 `E0B4`.

A 19F1C send after `E0B4` n=41 with no `R0B4` selects
`H-PortSchedSendLost`. Silence at 19F1C after SENT n=3, with
n=2 still sending, selects `H-PortSchedSendMissing`. A 19F1C
send between SENT n=3 and `E0B4` selects
`H-PortSchedSendBeforeRecv`. Missed controls or a silent
probe on n=2 is a failed instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

Fixup: `tools/apply_s3293_scheduler_send.py` (also hook from
`fixup_game_funcs.py`) at `0x80019F1C` and `L_80019F24`.
Rebuild Debug. Then from `build/` with the ROM present:

```
env ROGUESQ_LOG_M5_POSTWAIT=1 ./RogueSquadron64Recomp
```

30 s, SIGKILL. Log: `scratch/agent/s3293_port_scheduler_send.md`
plus the captured run log.
