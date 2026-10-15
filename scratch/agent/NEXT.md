# Next work unit: new external-retail boundary discriminator

HYPOTHESIS-ID: external-retail-entry-new-witness

The generated-symbol sweep is closed at the available snapshot. M5 is closed,
and the M3 indirect-call class is closed. Do not repeat either audit.

Run one bounded, read-only design/ground-truth experiment for the parked
external-retail boundary: use an independent retail PC watch at the first
port-side `0x800903F0` consumer boundary, with whole-RDRAM and VI controls,
then compare it to the qualified Rice port route. The instrument must include
the positive controls in the same run before a null is interpreted.

Competing hypotheses:

1. H-retail-boundary-live: retail reaches the consumer with the same route
   family, but the prior watch missed the exact boundary.
2. H-retail-design-dead: retail legitimately never reaches that consumer for
   the relevant voice kind, while the port-only hit is an invalid port state.
3. H-route-mismatch: the retail and port arms do not reach the same phase,
   making the consumer comparison unevaluable.

Discriminator:

- whole-RDRAM and VI controls fire, the route reaches title/hangar, and a
  phase-qualified retail PC row at the consumer selects H-retail-boundary-live;
- controls and route fire but the retail PC row remains absent while the
  independent kind/flag controls match selects H-retail-design-dead;
- any missing control, title/hangar phase, or kind/flag join selects
  H-route-mismatch and authorizes no mitigation.

Exact preflight commands:

    rg -n '800903F0|retail.*watch|whole-RDRAM|VI control|oracle' tools/oracle docs scratch/agent
    sed -n '1,240p' tools/oracle/README.md
    grep -n '^## Session ' PORTING-STATE.md | tail -15

Before any build, verify the oracle recipe and positive-control watch. Build
all controls in one arm, run one phase-gated comparison, and do not rewrite or
filter any port value. If the oracle cannot reach the qualified route, record
the exact missing control and leave the boundary parked.
