# NEXT work unit — qualify the remaining M5 consumer/output contract

HYPOTHESIS-ID: m5-consumer-output-contract

The port status-03 worker/store contract is now observed at class level on a
valid hangar route. The remaining M5 Step 1 discriminator is whether the
named consumer/output path is absent or merely not joined by the current
instrumentation. Do not change a wait, slot, or status edge.

Competing hypotheses:

- `H-PortConsumerReachable`: the named consumer executes after the worker
  contract and consumes the produced voice/output state.
- `H-PortConsumerIndirectGap`: status/worker rows remain live but the named
  consumer PC stays absent; an indirect edge or output relation is missing.
- `H-PortOutputGap`: the consumer executes, but its output/PCM join is absent
  or remains zero despite live source and task controls.

Discriminating measurement: one Debug port run with host/task/PCM controls,
title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, status/worker controls,
named consumer entry rows, output-task completion rows, and PCM source and
consumer joins. Consumer entry plus matching nonzero output selects
reachability; live worker/status plus no consumer selects the indirect gap;
consumer entry with zero/missing output selects the output gap. Missing target
controls make the run invalid.

Exact phase-gated rows: `[phase] width=1024` and `[phase] width=512` are the
target controls; positive controls are `[pcm-boundary-source]`,
`[pcm-boundary-consumer]`, `[audtask-abi]`, and the existing host/filter
controls. Count only rows after the 512 transition. The discriminator rows
are `[m5-consumer-entry]`, `[audtask-image-join]`, `[audtask-join]`,
`[pcm-boundary-source]`, and `[pcm-boundary-consumer]`.

Preparation and run surface:

```sh
rg -n 'm5-consumer-entry|audtask-image-join|audtask-join|pcm-boundary' src tools scratch/agent docs/M5-AUDIO-PLAN.md
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s3373_m5_consumer_output_contract 90 0.5
```

Before building, inspect the existing regeneration-surviving consumer and
audio-task joins. Add no new field unless the existing rows cannot answer the
table. Do not change behavior or add a mitigation.
