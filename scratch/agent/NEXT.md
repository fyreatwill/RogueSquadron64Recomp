# NEXT work unit — port: where does the scheduler stall after 19ED0 n=123?

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3293 selected `H-PortSchedSendMissing`: after SENT n=3 /
E0B4 n=41, jal `0x80019F1C` never fires. Same-run 19F1C n=41 at
width 640 (`a0=0x8011A818`) unblocked SENT n=2. The
`0x80128D44==0` skip (`19F24`) was silent. Last scheduler-gate
visits were `19ED0` n=122/123 with `$s2[0]=2` during SENT n=2
(path to `L_80019F50` / send `0x8011A800`), then no further
`L_80019ED0`. Keep s3288 fade / s3289 SENT / s3290 inner /
s3293 gate probes; this unit is the stall site inside
`spTaskSchedulerThread` after that last 19ED0.

## Competing hypotheses

- `H-SchedRecvBlocked`: after `19ED0` n=123, `osRecvMesg` at
  `0x80019CD0` is entered and does not return (loop waiting
  on a message that never arrives).
- `H-SchedF50SendBlocked`: the `$s2[0]!=0` path's `osSendMesg`
  at `0x80019F64` (`$a0=0x8011A800`) is entered on n=122 or
  n=123 and does not return.
- `H-SchedOtherJal`: after `19ED0` n=123 a different jal
  (`osSpTaskLoad`/`osSpTaskStartGo`/`getTimeLow32`/other send)
  is the last site and does not return; loop head
  `L_80019CC4` is not reached again.
- `H-SchedCoverageInvalid`: SENT n=3 / viewer / 640 / 19ED0
  n=123 miss, or the new loop/recv/F50 probes are silent
  while 19F1C n=41 still prints.

## Discriminator

One Debug port run, 30 s from `build/`, SIGKILL.
`ROGUESQ_LOG_M5_POSTWAIT=1`. Keep s3288/s3289/s3290/s3293
probes. Add a width≥640 always-print at `L_80019CC4` (loop
head), `0x80019CD0` recv entry+return, and `0x80019F64` send
entry+return. 19ED0 n=123 and 19F1C n=41 must still print
(same-run positive controls). Join to SENT n=3 `E0B4`.

A 19CD0 enter without return after 19ED0 n=123 selects
`H-SchedRecvBlocked`. A 19F64 enter without return on n=122
or n=123 selects `H-SchedF50SendBlocked`. Loop head silence
with some other last jal selects `H-SchedOtherJal`. Missed
controls or a silent new probe on 19F1C n=41 is a failed
instrument.

Do not add a skip, allow, restore, or wait bypass. No M5
Step 3.

## Exact commands

Fixup: `tools/apply_s3294_scheduler_stall.py` (also hook from
`fixup_game_funcs.py`) at `L_80019CC4`, `0x80019CD0`
entry+return, and `0x80019F64` entry+return.
Rebuild Debug. Then from `build/` with the ROM present:

```
env ROGUESQ_LOG_M5_POSTWAIT=1 ./RogueSquadron64Recomp
```

30 s, SIGKILL. Log: `scratch/agent/s3294_port_scheduler_stall.md`
plus the captured run log.
