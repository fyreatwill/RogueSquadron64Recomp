# Next work unit

HYPOTHESIS-ID: m5-retail-aux-field-join

Run one phase-gated retail/port join for the three s4936 store destinations,
with positive controls in the same run. Use the existing corrected mission
driver/oracle route; do not build a new mitigation or rewrite values.

Competing hypotheses and discriminator:

1. H-route-field: `0x800A1778` is a field in the same synth route/task state
   represented by `musyxSynthFrame` and `aspTask=0x80149470`.
2. H-independent-global: `0x800A1778` is independent global state despite the
   adjacent stores; its phase/value cadence will not join the route fields.
3. H-unresolved: one implementation or destination cannot be observed with
   the existing controls, so no ownership conclusion is possible.

The discriminating measurement is one table per phase containing, on both
sides, store order, values, and phase-qualified cadence for all three
destinations, plus positive whole-RDRAM/VI controls and the port
`musyxSynthFrame`/`aspTask` controls. H-route-field requires matching
order/value transitions; H-independent-global requires a reproducible mismatch;
H-unresolved is the only result if any control or destination is absent.

Before building, locate the existing phase-gated oracle and port join scripts
with:

    rg -n "4936|80149702|80149988|800A1778|PROBE_PHASE_WIDTH" tools scratch/agent

Batch all three destination arms into one build/run. The positive-control table
must contain whole-RDRAM writes, VI transitions, port `musyxSynthFrame` rows,
and port `aspTask=0x80149470` rows before any destination null is interpreted.
No soak is authorized until that table is specified.
