# NEXT work unit — join writer inputs and values for extra selector operands

HYPOTHESIS-ID: m5-task-field-writer

Session 3486 found the same pointer-word writer PC (`0x80091074`) in retail
and port, with one qualified port-only `0x8018DD30` value and no
`0x8018FB70` in the retry. The next unit must join that writer's inputs and
stored values to the selector output.

Competing hypotheses and discriminating outcomes:

- `H-WriterInputDivergence`: the same writer PC receives or stores different
  inputs across runtimes; joined writer rows with different values select it.
- `H-SharedWriterTransform`: writer inputs and stored values match, but the
  selector later differs; matching writer rows plus divergent selector rows
  select it.
- `H-ObservationInvalid`: controls or the title phase fail; no conclusion is
  valid without both positive controls and title rows.

Discriminating measurement: one title-gated oracle-and-port capture of the
`0x80091074` writer's source registers and stored value, joined to selected
`a0/a2` rows. Divergent writer inputs/values select `H-WriterInputDivergence`;
matching writer rows followed by different selector operands select
`H-SharedWriterTransform`; absent controls make the result invalid. Ground
truth already qualifies the writer PC, so add the port hook only after
preserving the same control schema.

Expected commands: run the independent Rice oracle with whole-RDRAM control,
the exact pointer-word writer PC `0x80091074`, and source-register capture;
then build the regeneration-safe port hook. Run the port from `build/` with
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1`,
`ROGUESQ_LOG_M5_TASK_WRITER=1`, and the existing title phase controls. Use
SIGKILL watchdog cleanup and do not compare sequential animation ordinals.
