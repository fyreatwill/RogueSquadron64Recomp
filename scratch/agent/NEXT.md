# NEXT work unit — audit the pre-title route-state publication edge

HYPOTHESIS-ID: m5-port-route-boundary

Session 3225 selected `H-PortStateBoundary`: the independent retail oracle
reached title 1024, but both same-build port arms stopped at 640 origin
`0x0066A500` despite matching six input edges, continued recv progress, and
identical route-state output ending with `target=0`.

## Competing hypotheses

- `H-PortInputBoundary`: the port's internal autopilot schedule or phase-
  relative input handling diverges from the retail route before title.
- `H-PortStateBoundary`: a non-input title/state publication differs before
  the first 1024 VI transition.
- `H-PortSchedulerBoundary`: host scheduling or queue progress prevents the
  same route transition despite valid input/state evidence.

## Competing hypotheses

- `H-StateWriterAbsent`: the expected pre-title state publication has no live
  writer in the port's executed path.
- `H-StateWriterWrongValue`: a live writer runs but publishes a value that
  legitimately differs from the retail state transition.
- `H-StateOrdering`: the right publication exists, but the route consumer
  observes it before/after the required ordering edge.

## Discriminator

Perform one bounded static writer/consumer audit around the existing
`m5-route-state` callsites and the route-state guest fields they report. First
ask the retail oracle for a positive control plus PC-attributed writes to the
candidate physical fields; only then grep the port's guest stores and consumer
ordering. A unique executed writer with a retail-matching value and an explicit
consumer edge selects `H-StateOrdering`; a writer with a differing value
selects `H-StateWriterWrongValue`; no corresponding writer selects
`H-StateWriterAbsent`. If the oracle watch cannot be armed and positively
validated, stop before adding port instrumentation.

No build is authorized until the oracle field watch has a positive control.
Do not infer target-phase audio nulls while 1024 is absent.

## Exact start

Use `tools/oracle/build/rs64_oracle` with the same core/ROM/Rice paths as
Session 3225, `--watch-write 0x0:0x800000 --hit-cap 3 --vi-trace`, and a
candidate route-state field watch once its physical address is identified.
Require the whole-RDRAM positive-control threshold and retail title 1024.
Then run one grep/static audit of the matching guest stores and consumer
callers. If a runtime capture is needed, build once and use both audio arms
concurrently with the Session 3225 environment and SIGKILL watchdog.
