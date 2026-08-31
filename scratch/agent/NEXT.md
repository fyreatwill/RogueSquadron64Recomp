# NEXT work unit — capture port table pointer at the load edge

HYPOTHESIS-ID: m5-output-state-contract-boundary

Session 3468 corrected the oracle configuration and measured the retail
post-store values. The independent controls passed and all candidate writers
produced ordered values, but the retail-only run cannot distinguish a source
value divergence from a different port-side table pointer.

Competing hypotheses and discriminating outcomes:

- `H-SourceWriterValue`: port and retail select the same entry, but the stored
  value differs; the port-side pointer matches the retail `0x801Bxxxx`
  selection.
- `H-TablePointerDivergence`: the port load selects a different table entry or
  pointer before the shared writer boundary.
- `H-PortObservationInvalid`: the port witness is absent or its positive
  control fails, leaving the cross-runtime join unevaluable.

Discriminating measurement: in one port run, phase-gated at title origin
`0x00790400`, record the table pointer/entry selected at the
`0x800644DC`/`0x80064524` edge, with the existing four-PC schema control and
the source-writer control. Join by phase and ordinal to the Session 3468
retail table. A matching entry with a different value selects
`H-SourceWriterValue`; a different entry selects `H-TablePointerDivergence`;
missing port rows or failed controls select `H-PortObservationInvalid`.

Work unit: add one regeneration-safe port witness at the table-load edge that
records the selected table pointer and ordinal, then build once and run the
validated LLE/spin-yield title route. Keep the four-PC schema control, title
phase gate, and existing source-writer rows in the same run. Do not alter
audio waits, slots, status handling, consumer dispatch, clear behavior, or
PCM writeback.

Exact preparation/build commands:

1. `rg -n "800644DC|80064524|source-writer|four-PC" src tools RecompiledFuncs`
2. Add the witness through the applicable fixup/instrumentation path, then
   `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Launch the existing validated title capture from `build/` with its LLE,
   spin-yield, `PROBE_PHASE_WIDTH`, and `PROBE_KEYS_FROM_PHASE=1` settings,
   writing the capture to `scratch/agent/s3469_m5_port_pointer/run.log`.
4. Parse controls and the ordered join with `rg -n "control|phase|644dc|64524|pointer|source-writer"`.

Expected outcomes: matching pointer plus divergent value selects
`H-SourceWriterValue`; a different pointer selects
`H-TablePointerDivergence`; missing rows or failed controls select
`H-PortObservationInvalid`. No mitigation or runtime behavior change is
authorized by this unit.

Evidence baseline: `scratch/agent/s3468_m5_retail_post_value/oracle-fixed.log`
and `docs/M5-S3468-RETAIL-POST-VALUE.md`.
