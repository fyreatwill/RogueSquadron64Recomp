# NEXT work unit — retail-grounded VI selector-writer inputs

HYPOTHESIS-ID: m5-vi-selector-writer-inputs

## Single work unit

Use the independent retail oracle to attribute producer inputs leading to
selector state `[A,B,C]=[1,1,0]` for title `0x80128DA0`, then compare the same
producer callsites in the port. Instrument only the identified writers
(`setRenderViewScaleFloat`, `beginSceneRenderFrame`, and
`requestViFeatureChange`) plus `applyPendingViChanges` entry, with a
phase-keyed positive control. Do not change behavior or audio routing.

## Competing hypotheses

- H-ProducerValue: retail and port receive different flag or mask inputs.
- H-ProducerReachability: one producer callsite/path is absent in the port.
- H-OracleBoundary: producer inputs match but retail attribution is from a
  later or different state transition.
- H-Unresolved: all producer inputs and paths match.

## Discriminating measurement

The first producer-side difference, keyed to the oracle's retail title phase,
selects H-ProducerValue; a missing call/path selects H-ProducerReachability;
equal inputs with a later oracle transition selects H-OracleBoundary; complete
equality selects H-Unresolved. The positive control must visibly fire in the
same run.

## Exact commands

1. Prepare the oracle watch/attribution recipe from `tools/oracle/README.md`
   and arm its whole-RDRAM positive control.
2. Add all producer and consumer counters in one build; phase-gate at VI
   transitions and run oracle and port arms concurrently.
3. Capture to `scratch/agent/s<next>_m5_vi_selector_writer_inputs/` and record
   the complete producer-input table before selecting a hypothesis.
