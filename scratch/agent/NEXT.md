# Next work unit: M4 accumulator-origin witness

HYPOTHESIS-ID: m4-accumulator-origin-new-witness

M5 is closed, the generated-symbol sweep is closed at the available snapshot,
and the external-retail retry was route-mismatched. Do not repeat those units.

Run one bounded read-only M4 accumulator-origin experiment. Use the
independent retail oracle to watch the statically identified accumulator
writer/consumer PC range and the qualified hangar origin, with whole-RDRAM and
VI controls. In the same iteration run the existing port binary with the
matching phase-scoped accumulator witness and the same route controls. No
guest value rewrite or guard is allowed.

Competing hypotheses:

1. H-accumulator-retail-writer: retail writes the accumulator at the selected
   PC in qualified hangar and the port has a matching writer/order.
2. H-accumulator-port-only: retail reaches the phase but the selected writer
   is absent while the port witness fires, identifying a port-side origin gap.
3. H-accumulator-route-mismatch: either arm lacks whole-RDRAM, VI, hangar, or
   writer controls, so the origin comparison is unevaluable.

Discriminator:

- both arms pass controls and reach `0x006AB400`; matching writer PC/order
  selects H-accumulator-retail-writer;
- both arms pass controls and reach `0x006AB400`, but only the port writer
  fires, selects H-accumulator-port-only;
- any missing control or phase-qualified writer join selects
  H-accumulator-route-mismatch and authorizes no mitigation.

Exact preflight commands:

    rg -n 'accumulator|M4|writer.*PC|hangar|006AB400' docs tools scratch/agent
    sed -n '1,240p' tools/oracle/README.md
    grep -n '^## Session ' PORTING-STATE.md | tail -15

Before any build, identify the exact accumulator symbol/PC from existing
evidence and verify the oracle positive-control watch. Build all controls in
one arm, run one phase-gated comparison, and record the exact missing control
if either route fails. Do not rewrite or filter any port value.
