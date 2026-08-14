# NEXT work unit (s1033)

HYPOTHESIS-ID: retail-oracle-callback-audit

Run one bounded retail-oracle phase-reachability capture using the validated
threshold-removal tool. Do not build or change the recomp runtime. The slot-SP
recipe family has now produced two phase-positive no-event runs; do not enqueue
another key-schedule variant and do not reopen M4.

## Competing hypotheses and discriminator

* `H-oracle-callback-live`: the retail oracle reaches the callback and the
  whole-RDRAM positive control fires, so an address-specific watch can be
  interpreted.
* `H-oracle-callback-blocked`: the positive control fails or the callback path
  is still blocked before callback entry; no retail phase conclusion is
  allowed.
* `H-oracle-watch-discriminates`: after the positive-control watch is removed,
  the address-specific watch reports a retail PC/write attribution that
  separates the s983 callback hypotheses.
* `H-oracle-phase-blocked`: the documented Start schedule still leaves retail
  at width 320, so the target watch cannot yet answer the hangar question.

Discriminating measurement: one run must visibly show the positive-control
threshold/removal marker, every injected Start and its PIF-visible button edge,
and VI width/origin transitions. A freelist hit after removal selects
`H-oracle-watch-discriminates`; a validated run reaching width 512 at hangar
origin with no hit selects a retail null; a validated run stuck at width 320
selects `H-oracle-phase-blocked`; no positive-control/removal marker invalidates
the run.

## Exact preflight

```sh
sed -n '1,240p' tools/oracle/README.md
rg -n "callback|read_with_bp_checks|whole-RDRAM|positive" tools/oracle
git status --short
```

1. Use the existing built `tools/oracle/build/rs64_oracle`; do not change source
   unless the phase control itself is disproven. Run one capture with the same
   core, ROM, datadir, RSP/input plugins, whole-RDRAM watch first, freelist watch
   second, and documented Start schedule, capturing to
   `scratch/agent/oracle_s1033_capture.log`.
2. Require the positive-control/removal markers and PIF-visible Start edges
   before interpreting the phase or freelist result. Use SIGKILL if a manual
   bounded stop is needed.
