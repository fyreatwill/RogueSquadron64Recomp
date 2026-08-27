# NEXT work unit (s2581) — M5 image first-task stall boundary

HYPOTHESIS-ID: m5-audio-image-first-task-stall

## Single work unit

Audit and instrument the first real Factor 5 image task boundary, then run one
fresh image-only 90-second capture. Do not change runtime behavior or task,
output, gate, or wait values. Identify whether execution stalls inside the
generated image before its first return, in the host `run_task`/DMA wait around
the image, or because the first task shape is not a valid image task.

## Competing hypotheses and discriminator

- `H-ImageLoop`: the generated image enters and remains in a microcode loop
  before the generated `break 0`/return.
- `H-HostWait`: the image returns or reaches a host boundary, but the host
  task/DMA/status wait prevents the next task-contract row.
- `H-TaskShape`: the first dispatched task has a field combination that is not
  a valid Factor 5 image task, so the image's first input path cannot complete.

The discriminator is one first-task table with image entry, generated
microcode progress/return, host wait/DMA/status progress, exact task fields,
and route phase. Image progress without return selects `H-ImageLoop`; image
return/host wait progress without a task row selects `H-HostWait`; a stable
first-task field shape with no image entry/progress selects `H-TaskShape`.
Missing image dispatch or autopilot positive controls makes the capture
unevaluable.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2580_m5_image_isolated.sh s2581_m5_image_first_task_stall
```

Use the existing retail oracle positive-control recipe before adding any new
probe. Record the first-task row in `PORTING-STATE.md`; no promotion or
mitigation is authorized from a `Broke` return alone.
