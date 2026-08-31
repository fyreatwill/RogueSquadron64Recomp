# NEXT work unit — trace the producer of extra port task operands

HYPOTHESIS-ID: m5-task-field-writer

Session 3483 selected the writer-operand hypothesis: retail post-store values
at `0x8009177C/0x80091784` are restricted to `0x80171CE0`/`0x80173B20` and
sizes 1/2, while port writer and enqueue rows also carry
`0x8018FB70`/size 3 and `0x8018DD30`/size 1.

Competing hypotheses and discriminating outcomes:

- `H-ProducerDivergence`: an upstream port producer stores the extra operands;
  a source-span writer row with those values selects this.
- `H-GuestTransform`: producer values match retail, then guest code transforms
  them before `0x8009177C/0x80091784`; matching producer rows plus differing
  writer rows selects this.
- `H-ObservationInvalid`: controls or the title phase fail; no conclusion is
  valid without both positive controls and title rows.

Discriminating measurement: one title-gated capture covering the complete
candidate source spans feeding the task fields, retaining the whole-RDRAM
control, task-writer control, and enqueue rows. Join producer rows to writer
rows by title origin and per-PC ordinal. Build once only if a new hook is
needed; otherwise run the existing validated route and the independent Rice
oracle together.

Expected commands: first run the Rice oracle with `--watch-write 0x0:0x800000`
and the selected source-span watches, then run the port from `build/` with
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_LOG_M5_TASK_WRITER=1`, and the existing title phase controls. Use
SIGKILL watchdog cleanup and do not compare sequential animation ordinals.
