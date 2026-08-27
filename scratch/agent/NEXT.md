# NEXT work unit (s2840) — post-dispatch audio-route discriminator

HYPOTHESIS-ID: m5-audio-post-dispatch-route

## Work unit

Run one same-build concurrent image/silent pair with the existing
`ROGUESQ_LOG_M5_FIRST_TASK=1` boundary census and post-dispatch execution
markers enabled. Keep the independent retail whole-RDRAM control, physical
`0x000A0F50` watch, and all passive M5 markers. Compare the first 16 task
ordinals through image/stub return and SP completion at the common pre-title
VI 640 boundary. Do not change dispatch behavior or any gate store.

## Competing hypotheses and discriminator

- H-execution-return: the arms have identical task inputs but diverge in image
  execution return/exit or SP completion, selecting the post-dispatch bridge.
- H-scheduling: image/stub return and SP completion are identical through the
  first 16 tasks, selecting a later queue or scheduler edge.
- H-unreached: the first-task census is present but post-dispatch markers are
  absent in both arms; this bridge remains unevaluable.

The discriminator is one table keyed by arm and audio-task ordinal containing
the first-task fields, selected function pointer, image/stub enter and return,
break/exit state, SP completion, VI width/origin, and matching dispatch
control. A return/completion divergence selects H-execution-return; identical
post-dispatch rows select H-scheduling; absent post-dispatch rows select
H-unreached.

## Exact commands

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_M5_FIRST_TASK=1 zsh scratch/agent/run_s2838_m5_gate_writer.sh
grep -a -E 'positive-control|watch write|\[audtask-dispatch\]|\[audtask-first-boundary\]|\[phase\]|\[m5-gate\]|\[m5-writer\]|\[CRASH\]|\[ABORT\]' scratch/agent/s2838_m5_gate_writer/driver.log
```

The recipe must launch both arms from `build/`, arm the retail positive
control before interpreting the narrow watch, phase-gate target rows, and
terminate all children with SIGKILL. Pre-title nulls are valid only for the
explicit H-unreached outcome; they do not authorize a behavior change.
