# NEXT work unit (s2327) — M5 task-ordinal pre/post lifecycle join

HYPOTHESIS-ID: m5-task-ordinal-prepost-join

## Work unit

Add one host event join that stamps the existing audio-task ordinal/row onto
the existing slot-store, key-on, descriptor, and image-stage records. Run the
retail oracle first with the s2326 whole-RDRAM, title/hangar, gate/task/status,
wait, and task-writer controls, then run stub and image arms on the same
eleven-Start route. Produce one table for every target task and destination
with signed deltas from task start, image stage, audio completion, PCM source,
PCM consumer, and slot/key-on/descriptor events. Do not change behavior.

## Competing hypotheses and discriminating measurement

- H-PreEvents-SameTask: the five pre-stage slot stores and the sentinel/key-on
  rows belong to the same audio task as the two image destinations. A task
  ordinal join will place them under the target task and show the lifecycle
  before image stage, with no missing post-stage edge.
- H-PreEvents-EarlierTick: the pre-stage rows belong to an earlier task or VI
  tick. The target task has image stage and PCM progress but no slot,
  descriptor, or key-on contract events in its own ordinal window.
- H-PostConsumer-Missing: the pre-stage rows belong to the target task, but a
  valid image completion/PCM publication is followed by no downstream slot or
  key-on event. This selects a missing post-stage consumer edge rather than an
  attribution error.
- H-CoverageInvalid: the oracle controls, both hangar phases, or the event
  stamp controls are absent; no lifecycle conclusion is admissible.

The discriminator is one table keyed by `(arm, phase, width, origin, audio
ordinal, task row, destination, stage event, completion event, PCM source and
consumer events, slot index/status, descriptor pointer, key-on tuple)` with
signed event deltas. Same-task pre rows select H-PreEvents-SameTask; rows
outside the task ordinal select H-PreEvents-EarlierTick; a same-task image/
PCM row with no later lifecycle selects H-PostConsumer-Missing; missing
positive controls select H-CoverageInvalid.

## Exact commands

Before adding the host event stamp, run the independent oracle controls and
confirm the target phase is covered. Then regenerate in the required order,
build one binary carrying all event stamps, and run:

    zsh -n scratch/agent/run_s2327_m5_task_ordinal_prepost_join.sh
    zsh scratch/agent/run_s2327_m5_task_ordinal_prepost_join.sh s2327_m5_task_ordinal_prepost_join

The launcher must retain `ROGUESQ_LOG_VI_CALLERS=1`, the M5 key-on census,
audio-task ABI/DMA/PCM controls, and the filter/voice control row. A filter or
voice null is invalid unless its positive control fires in the same arm. Use
SIGKILL for every cleanup and do not add writeback, guards, slot values, or
defaults.
