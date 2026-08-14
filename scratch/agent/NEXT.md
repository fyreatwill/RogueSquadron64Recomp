# NEXT work unit (s998)

HYPOTHESIS-ID: m4-zero-shade-source-consumer-join

## One work unit

Add a source/task identity to the shade-side diagnostic, then join each F5
VTXCOLOR source/payload record to the zero-shade replacement and raw-shade
records in one phase-gated capture. s997 proved the controls and payloads fire,
but raw-shade/zero-shade rows carry no source/task identity, so nearest task
order cannot distinguish exact from untouched source ownership. Do not add a
mitigation or hand-edit generated files.

Competing hypotheses and discriminating measurement:

- H-exact-zero-source: the zero-shade record's identified source has a same-run
  generated write.
- H-untouched-zero-source: its identified source has a nonzero payload and no
  same-run generated write.
- H-mixed: both source populations occur.

The discriminating measurement is a source pointer or F5 task/display-list
identity emitted on each raw-shade/zero-shade record and joined to
`[f5-state-payload]` plus generated-store rows. The generated-store, F5,
shade-DMA, write-fault, raw-shade, and zero-shade controls must all fire in the
same run; missing identity or source/raw-shade rows invalidate the result.

## Exact commands

First add the identity to the existing raw-shade diagnostic at its producer,
preserving the raw shade values. Run the fixup static candidate-count check,
then use the documented `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
cmake` order with `RS64_FIXUP_S992_GENERATED_WRITES=1`. Launch from `build/`
with the existing phase-gated LLE recipe, adding `ROGUESQ_LOG_SHADE_RAW=1`:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LOG_VTX_WRITE_FAULT=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a' zsh tools/probe.sh scratch/agent/s998_vtx_zero_source_join_20260813 180 3`

Extract phase-4/phase-6 payload, raw-shade, zero-shade, and generated-store
rows. Join using the newly emitted identity, then check whether zero-shade
records consume a source with an exact generated write or only untouched
nonzero sources. If controls or source/raw-shade identity coverage fail, make
no causal selection.
