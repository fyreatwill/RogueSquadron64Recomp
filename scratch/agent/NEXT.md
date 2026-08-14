# NEXT work unit (s1031)

HYPOTHESIS-ID: retail-oracle-callback-audit

Perform one bounded ground-truth audit of the archived s983 retail-oracle
callback probe. Do not build or change the recomp runtime in this unit. The
slot-SP recipe family has now produced two phase-positive no-event runs; do
not enqueue another key-schedule variant and do not reopen M4.

## Competing hypotheses and discriminator

* `H-oracle-callback-live`: the retail oracle reaches the callback and the
  whole-RDRAM positive control fires, so an address-specific watch can be
  interpreted.
* `H-oracle-callback-blocked`: the positive control fails or the callback
  path is still blocked before callback entry; no retail phase conclusion is
  allowed.
* `H-oracle-watch-discriminates`: with the positive control live, the
  address-specific watch reports a retail PC/write attribution that separates
  the s983 callback hypotheses.

Discriminating measurement: one oracle run must first show the documented
whole-RDRAM positive-control watch firing (about 1.6M events in 8 emulated
seconds), then report whether the callback is entered and, if so, the
address-specific watch's retail PC attribution. Positive control plus
callback attribution selects `H-oracle-watch-discriminates`; positive control
without callback selects a callback-path hypothesis; no positive control
makes the run invalid and selects neither.

## Exact preflight

```sh
sed -n '1,240p' tools/oracle/README.md
rg -n "callback|read_with_bp_checks|whole-RDRAM|positive" tools/oracle
git status --short
```

If the existing oracle recipe is runnable, execute exactly one run from its
documented command with a whole-RDRAM watch armed first. Capture to a path
whose final component does not begin with `.`. If the positive control fails,
stop and record the oracle as blocked; do not interpret address-specific
nulls. If the callback is live, record the PC/watch attribution and update
the ledger with the selected callback hypothesis.
