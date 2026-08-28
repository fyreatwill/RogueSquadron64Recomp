# NEXT work unit (s2944) — batched port M4 producer/index join

HYPOTHESIS-ID: m4-accumulator-boundary-revisit

The s2943 retail ground-truth preflight passed its whole-RDRAM control and
reached title/hangar, but cannot observe RSP DMEM. Run the already-grounded
port-side join in one build/run. Do not change behavior or add a mitigation.

## Competing hypotheses and discriminator

- H-SharedSlot: producer `B00/B02/B04` rows and consumer `B74` rows align by
  task and phase, with consumer `index & 0x7F` equal to a producer slot and
  ordering showing the producer publication first.
- H-IndependentIndex: both endpoints are live but consumer index/value is
  derived independently of producer slot; repeated equality is incidental or
  comes from another state source.
- H-IrrelevantWriter: producer or consumer endpoint is absent in the qualified
  target phase, or the observed B74 value does not select the producer table.

The discriminator is one complete phase/task-keyed table of every bounded
producer row (`slot`, p0/p1/p2), consumer row (`index`, masked, selected
c0/c1/c2, source), branch result, and ordering. A positive `[f5-fetch-control]`
row in the same target phase is mandatory. Aligned producer-before-consumer
rows select H-SharedSlot; live independent rows select H-IndependentIndex;
missing/nonselecting rows select H-IrrelevantWriter. No behavior change is
authorized.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
mkdir -p scratch/agent/s2944_m4_accumulator_boundary
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_M4_INDEX=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
  PROBE_LEAVE_OK=1 zsh tools/probe.sh \
  scratch/agent/s2944_m4_accumulator_boundary 180 2
```

Require the positive-control mark before interpreting any M4 null. Record the
joined table and verdict at
`scratch/agent/s2944_m4_accumulator_boundary/RESULTS.md`.
