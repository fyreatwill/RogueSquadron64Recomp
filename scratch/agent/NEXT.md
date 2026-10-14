# Resume next work unit

HYPOTHESIS-ID: m5-step11-spin2-validation

Single bounded work unit: validate the already-qualified second MusyX wait
de-stub on the title/hangar route with both behavior arms in one build/run
wave: default `ROGUESQ_AUDIO_SPIN2_YIELD=1` and rollback
`ROGUESQ_AUDIO_SPIN2_YIELD=0`. Use the existing phase-gated recipe and retain
all passive breadcrumb controls.

Competing hypotheses:

* H-yield-safe: yielding lets the producer clear the flag and the wait returns
  without changing task/SP, slot, PCM, or route behavior.
* H-yield-causal: yielding changes a downstream audio/task/route outcome;
  select only if the arms diverge after both have valid producer/clear controls.
* H-route-invalid: either arm fails to reach title/hangar or lacks a positive
  producer/clear control, so the comparison cannot select an audio hypothesis.

Discriminating measurement: one phase-gated A/B with producer entry, flag-clear,
wait-return, task/SP completion, slot/status, nonzero PCM source/consumer, and
VI title/hangar controls. Matching complete rows select H-yield-safe; a
post-control arm divergence selects H-yield-causal; missing target phase or
missing positive control selects H-route-invalid.

Exact command:

```sh
env ROGUESQ_LOG_WAITMUSYX_SPIN2=1 zsh scratch/run_s4766_m5_a12_second_wait.sh
```

Do not rerun the s4828 startup crash capture or Step 1. If the recipe is
route-invalid, record that result and pivot to the next M5 behavior change;
do not add another diagnostic field.
