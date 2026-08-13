# NEXT work unit (oracle longer-horizon phase check)

HYPOTHESIS-ID: oracle-exact-recipe-320

The s779 three-arm emulator-1 repeatability run stayed at width 320/origin
`0x6dd280` in every arm, with positive controls and all eleven Start presses.
The exact recipe is now repeatably 320-only through 70 seconds, but the oracle
README's documented undriven 512 phase begins around 102 seconds. The current
window may simply end before the claimed later phase.

## Competing hypotheses

- H-late-phase: the exact recipe reaches a later width/origin after the
  documented 102-second point.
- H-exact-recipe-only: the exact recipe remains at width 320/origin
  `0x6dd280` beyond that point.

## Discriminating measurement

Run two concurrent arms for 130 seconds with the same core, ROM, emulator-1,
all-RDRAM positive control, VI trace, PIF trace, and eleven Start schedule.
Any width/origin transition after 70 seconds selects H-late-phase; two
320-only traces with positive controls select H-exact-recipe-only.

## Commands

Use the verified s779 command twice, changing only `--secs 130`. Store
separate logs under `scratch/agent/oracle_runs/20260813_longer_phase/`; run
concurrently and kill with SIGKILL only after completion or a 160-second
timeout.
