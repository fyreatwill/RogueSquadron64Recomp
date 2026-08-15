# NEXT work unit (s1216)

HYPOTHESIS-ID: retail-entry-strategy

Work unit: design and run one independent retail-entry strategy after the
320-boot savestate route failed. Do not arm M4 target watches unless a later VI
width/origin phase is reached. Preserve the whole-RDRAM positive control and
PIF/VI controls in every arm.

Competing hypotheses and discriminator:

- H1: a genuinely independent entry route reaches a later VI width/origin
  phase, making the retail M4 target watches evaluable.
- H2: the route remains at width 320/origin `0x006dd280`, so it does not reach
  the intended state path.
- H3: the route disrupts whole-RDRAM or PIF/VI controls, making its null
  result unevaluable.

Discriminator: phase-gated VI width/origin plus positive-control and PIF
records in the same run. A later phase selects H1; width 320 selects H2;
missing controls selects H3.

Before implementation, identify the route and its independent ground-truth
control in `tools/oracle/README.md`; batch both A/B arms in one build/run. The
previous route and exact result are in `scratch/agent/oracle-control.log` and
`scratch/agent/oracle-state.log`.
