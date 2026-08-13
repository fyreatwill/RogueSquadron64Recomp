# NEXT work unit (oracle repeatability check)

HYPOTHESIS-ID: oracle-schedule-vs-expected-320

The s778 emulator-1 A/B stayed at width 320/origin `0x6dd280` in both arms,
with positive controls. The alternate execution backend is not the missing
phase for this recipe. The next unit tests whether the remaining outcome is
timing-sensitive or consistently 320-only.

## Competing hypotheses

- H-oracle-schedule-or-timing: the later retail phase is selected only by a
  scheduling/timing condition and appears in at least one fresh identical run.
- H-oracle-expected-320: this exact headless retail/core/plugin recipe is
  consistently 320-only; the documented later phase is not reachable here.

## Discriminating measurement

Run three fresh debugger-on emulator-1 arms concurrently for 70 seconds with
the same positive whole-RDRAM watch, VI trace, PIF trace, and eleven-entry
Start schedule. Phase-gate on VI width/origin transitions. Any later width or
origin transition in any arm selects timing sensitivity; three 320-only arms
with positive controls strengthen the exact-recipe explanation.

## Commands

Use the s778 command with `--oracle-debugger 1 --oracle-emulator 1` three times
concurrently, writing separate logs under
`scratch/agent/oracle_runs/20260812_repeatability/`; kill only after the
70-second oracle completion or with SIGKILL on timeout. Record each arm's
whole-RDRAM hit count, VI count, PIF count, and width/origin transitions.
