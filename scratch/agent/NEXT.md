# NEXT work unit (s2839) — pre-title task-field dispatch discriminator

HYPOTHESIS-ID: m5-audio-dispatch-selection

## Work unit

Run one same-build concurrent image/silent pair with the existing
`ROGUESQ_LOG_M5_FIRST_TASK=1` boundary census enabled. Keep the independent
retail whole-RDRAM control, physical `0x000A0F50` watch, and all passive M5
markers. Compare the first 16 audio task fields, route phase, dispatch arm,
and task-function pointer at the common pre-title VI 640 boundary. Do not
change dispatch behavior or any gate store.

## Competing hypotheses and discriminator

- H-selector-field: image and silent receive different task-field sequences or
  function pointers before VI 640; the selector/task staging boundary is the
  route cause.
- H-selector-only: both arms receive identical task fields and function
  pointer except for the deliberate image/stub choice; the split is after
  dispatch or scheduling.
- H-unreached: the first-task census is absent while dispatch controls remain
  positive; the task-field boundary is not reached and this route remains
  unevaluable.

The discriminator is one table keyed by arm and audio-task ordinal containing
`type`, `ucode`, `ucode_data`, `data_ptr`, `data_size`, output/yield fields,
`ucode_func`, VI width/origin, and the matching dispatch control. A field or
function-pointer divergence selects H-selector-field; identical rows reject
it; positive dispatch with no boundary rows selects H-unreached.

## Exact commands

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_M5_FIRST_TASK=1 zsh scratch/agent/run_s2839_m5_dispatch_fields.sh
grep -a -E 'positive-control|watch write|\[audtask-dispatch\]|\[audtask-first-boundary\]|\[phase\]|\[m5-gate\]|\[m5-writer\]|\[CRASH\]|\[ABORT\]' scratch/agent/s2839_m5_dispatch_fields/driver.log
```

The recipe must launch both arms from `build/`, arm the retail positive
control before interpreting the narrow watch, phase-gate target rows, and
terminate all children with SIGKILL. Pre-title nulls are valid only for the
explicit H-unreached outcome; they do not authorize a behavior change.
