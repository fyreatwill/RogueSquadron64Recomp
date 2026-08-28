# NEXT work unit (s2946) — port-side route-state handoff match

HYPOTHESIS-ID: m5-route-state-repair

M5 remains the strategic priority. Match the oracle-qualified candidate range
`0x80019C00..0x8001A000` in the port using one batched probe and the existing
phase/positive-control gates. Do not change behavior or de-stub audio in this
unit.

## Competing hypotheses and discriminator

- H-RouteState: the port reaches the candidate with a different phase-keyed
  handoff/return state than retail, explaining the route stop.
- H-RouteInput: port and retail handoff state match; input/timing remains the
  route difference.
- H-RouteAbsent: the port never executes the candidate before its stop.

The discriminator is a phase-keyed table for candidate PC/caller, return
value, `$s1/$a0/$a2`, and the route-state words corresponding to the oracle's
`a1/a2` families, with `[f5-fetch-control]` as the same-run positive control.
Target-phase rows with a port/retail state mismatch select H-RouteState;
matching rows select H-RouteInput; zero candidate rows with a firing control
select H-RouteAbsent. A missing control invalidates the run.

## Exact work

Locate the existing phase-gated port probe and add the complete candidate table
in one build. Run the Debug binary from `build/` with its established 180 s
route recipe and capture to
`scratch/agent/s2946_m5_route_state/RESULTS.md`. Build every candidate field
in the same binary; do not run one field at a time.
