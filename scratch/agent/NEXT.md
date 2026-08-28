# NEXT work unit (s2971)

HYPOTHESIS-ID: m5-route-qualification

## Unit

Perform one new M5 route-qualification investigation. Identify a previously
unwatched static handoff between the qualified retail title/hangar boundary and
the port's pre-title VI-640 stall, and first obtain an independent retail-oracle
PC attribution for that handoff before adding port instrumentation. Do not
repeat the rejected s2903 candidate PCs, broad main-text range, or the
route-invalid s2949/s2950 field probe.

## Competing hypotheses and discriminator

- H-retail-handoff: the independent oracle attributes a new PC executing the
  selected handoff during title/hangar progression.
- H-port-handoff: the oracle does not reach the handoff, so the candidate is
  not a useful boundary and must not receive port instrumentation.
- H-stale-route: the existing oracle recipe or phase classifier is stale, shown
  by a failed whole-RDRAM positive control or missing title/hangar controls.

The discriminator is the same-run retail oracle table: whole-RDRAM positive
control, title and hangar phase controls, and PC attribution at the newly
selected static handoff. Each possible outcome selects exactly one hypothesis.

## Commands

1. Run `grep -n '^## Session ' PORTING-STATE.md | tail -15`; if all 15 titles
   are sweep-scoped, perform the mandated external retail-entry or M4
   accumulator-boundary revisit instead of another sweep step.
2. Run the retail oracle with its whole-RDRAM positive control and the new
   physical watch, using SIGKILL and a capture path under
   `scratch/agent/s2971_m5_route_qualification/`.
3. Only if the oracle positively attributes the handoff, design the paired port
   measurement for the next iteration; otherwise record the negative result
   without adding runtime instrumentation.
4. Write the oracle table under `scratch/agent/s2971_m5_route_qualification/`.

Expected outcomes: a positive oracle PC attribution selects H-retail-handoff;
an otherwise healthy oracle that misses the candidate selects H-port-handoff;
and a failed positive control selects H-stale-route. Do not add port code on a
negative or stale-route result.
