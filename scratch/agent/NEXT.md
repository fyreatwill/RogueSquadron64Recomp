# NEXT work unit (s1032)

HYPOTHESIS-ID: retail-oracle-callback-audit

Implement one bounded change to the oracle tool, then run one retail capture.
Do not build or change the recomp runtime. The slot-SP recipe family has now
produced two phase-positive no-event runs; do not enqueue another key-schedule
variant and do not reopen M4.

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

Discriminating measurement: the modified tool must visibly fire the
whole-RDRAM positive control, remove only that watch at a documented threshold,
and leave the freelist watch armed. A later freelist hit with a retail PC
selects `H-oracle-watch-discriminates`; positive control with no later target
hit is an unevaluable phase/path result; no positive control invalidates the
run. The removal threshold must be observable in the log.

## Exact preflight

```sh
sed -n '1,240p' tools/oracle/README.md
rg -n "callback|read_with_bp_checks|whole-RDRAM|positive" tools/oracle
git status --short
```

1. Read the oracle source's watch-arm/update code and add a narrow, logged
   removal of watch index 0 after 10,000 whole-RDRAM callbacks. Do not remove
   or alter watch index 1. Build with `tools/oracle/build.sh`.
2. Run exactly one capture from the documented command, using the same core,
   ROM, datadir, RSP/input plugins, whole-RDRAM watch first, freelist watch
   second, and Start schedule. Capture to a path whose final component does
   not begin with `.`.
3. Require the positive-control and removal markers before interpreting any
   freelist result. Use SIGKILL if the bounded run must be stopped.
