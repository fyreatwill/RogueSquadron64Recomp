# NEXT work unit — join port table selection to output/state values

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3469 qualified the port table-selection witness. The title and hangar
phase controls passed; the port selected the same `0x801Bxxxx` pointer family
seen in the independent Session 3468 retail baseline, including
`0x801B4F00` and `0x801B5E70`. The remaining question is whether the first
divergence is in the downstream output/state fields.

Competing hypotheses and discriminating outcomes:

- `H-OutputStateContract`: port and retail select the same entry/pointer family,
  but a downstream output/state field diverges.
- `H-LaterTableSelection`: the apparent pointer-family match hides a divergent
  entry ordinal or selection before the consumer boundary.
- `H-PortObservationInvalid`: the ordered port rows or their positive control
  are absent, leaving the join unevaluable.

Discriminating measurement: join the existing port table-selection rows and
four-PC output/state rows to the Session 3468 retail post-store rows by title
phase, selected entry, and per-entry ordinal. A matching selection with the
first divergent output/state field selects `H-OutputStateContract`; a divergent
entry/ordinal selects `H-LaterTableSelection`; missing ordered rows or failed
controls select `H-PortObservationInvalid`.

Work unit: parse and join the retained port and retail tables; no runtime
behavior changes. Keep all joins phase-gated and do not compare sequential
animated arms. Do not alter audio waits, slots, status handling, consumer
dispatch, clear behavior, or PCM writeback.

Exact preparation/build commands:

1. Parse `scratch/agent/s3469_m5_port_pointer/run_autopilot.log` and the
   retained Session 3468 retail evidence.
2. Join title rows by selected entry and per-entry ordinal, then compare the
   output/state fields.
3. Record the first divergent field and its phase/ordinal.

Expected outcomes: matching selection with a divergent output/state field
selects `H-OutputStateContract`; a divergent entry/ordinal selects
`H-LaterTableSelection`; missing rows or failed controls select
`H-PortObservationInvalid`. No mitigation or runtime behavior change is
authorized by this unit.

Evidence baseline: `scratch/agent/s3468_m5_retail_post_value/oracle-fixed.log`
and `docs/M5-S3468-RETAIL-POST-VALUE.md`.
