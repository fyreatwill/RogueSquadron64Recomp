# NEXT work unit — redesign the M5 route phase join

HYPOTHESIS-ID: m5-port-route-boundary

Session 3229 watched retail caller, reapply entry, reapply call, and return in
one run. The whole-RDRAM control passed; all four fired once in order at 640
origin `0x00790A00`, and the return row matched the port's `audio-return` row
at `0x0066A500`. The exact `0x00790500` bucket is not a sufficient join key.
See `scratch/agent/s3229_m5_route_return_oracle.md` and `.log`.

## Competing hypotheses

- `H-PhaseAlias`: `0x00790500` and `0x00790A00` are the same transition under
  VI/display-mode rotation, so retail and port can join by a normalized
  transition key.
- `H-PhaseDifferentEdge`: the origins are distinct display-mode edges and the
  port row is not the retail caller transition.
- `H-PortSequenceMissing`: after a normalized join, the port has no matching
  caller-to-return sequence even though retail does.

## Discriminator

Use the already-grounded retail sequence, then make one phase-gated port
capture keyed by the same VI transition rather than an exact origin suffix.
Record the first transition containing the four route PCs/rows and its
immediately preceding/following VI origin, with a whole-RDRAM positive control
in the same run. `H-PhaseAlias` is selected if normalized retail and port
transitions have the same caller/entry/call/return order and values;
`H-PhaseDifferentEdge` if the surrounding VI edge or sequence differs;
`H-PortSequenceMissing` only if the normalized port window has no matching
sequence. Do not add audio/task counters until one outcome selects the phase
relationship.

## Exact start

Before building port instrumentation, inspect the existing phase transition and
route rows with `rg -n '\\[(phase|m5-route|audio-return)'` in the two validated
port logs and use `scratch/agent/s3229_m5_route_return_oracle.log` as ground
truth. Then define one bounded, transition-keyed port capture and run both
audio arms together; the discriminator is the normalized sequence, not a
stopwatch or exact origin. Keep the same route, `ROGUESQ_LOG_ALL=1`, and phase
width 640.
