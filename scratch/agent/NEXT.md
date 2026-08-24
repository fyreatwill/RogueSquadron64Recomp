# NEXT work unit (s2332) — M5 destination-to-slot/key-on contract

HYPOTHESIS-ID: m5-destination-slot-keyon-contract

## Work unit

Run one ground-truth-first, no-behavior-change census that joins each
qualified nonzero image stage and exact PCM source/consumer to the complete
same-task and prior-task slot/status/descriptor/key-on lifecycle. Restore a
positive filter/voice audit control in the same run before interpreting its
null. Keep the qualified Factor 5 image arm, silent control, eleven-Start
route, and `ROGUESQ_DRAIN_INLOOP_TICK=1`; do not add writeback, address
remapping, slot values, guards, defaults, or a consumer.

## Competing hypotheses and discriminating measurement

- H-SameOrdinalConsumer: the consumer exists after image completion but the
  current lifecycle join misses its task/ordinal key. A complete event table
  should show a same-ordinal post-stage slot/status/descriptor/key-on row for
  at least one exact PCM join.
- H-PriorRouteOnly: the six-row slot/key-on signature is genuinely owned by
  the prior audio ordinal. The complete table should show no same-ordinal
  post-stage row while retaining the prior signature for every target row.
- H-FilterVoiceConsumer: the downstream transition is inside the
  filter/voice path, and its previous null was unqualified. A positive
  filter/voice control plus a matching descriptor/key-on transition should
  follow the target PCM event without a same-ordinal slot-store row.
- H-CoverageInvalid: any retail whole-RDRAM/target/status/writer control,
  title/hangar phase, task/DMA/guest-receive/PCM control, or filter/voice
  positive control is absent.

The discriminator is one phase-keyed table containing `(arm, phase, origin,
audio ordinal, image stage event/completion, stage destination/length/hash/nz,
PCM source/consumer event, task begin/end/n, every generated DMA event,
slot/status/descriptor/key-on event kind/index/destination/value, signed delta
from stage and completion, same-ordinal/post-stage/prior classification,
filter/voice control, and host-boundary rows)`. Select H-SameOrdinalConsumer
only with a same-ordinal post-stage row; select H-PriorRouteOnly only with
qualified controls, no post-stage row, and the prior signature; select
H-FilterVoiceConsumer only with its positive control and a downstream
filter/voice-to-key-on join. Any missing positive control selects
H-CoverageInvalid.

## Exact commands

Create `scratch/agent/run_s2332_m5_destination_slot_keyon.sh` with the retail
oracle preflight first. Keep the whole-RDRAM positive control, physical
`0x00165000:0x0016B000` target watch, task/output/gate/wait/status watches,
title/hangar origins, named task/output writer PCs, and the eleven-Start
schedule. In both port arms retain `[audtask-abi]`, `[audtask-dma-row]`,
`[audtask-dma-range]`, image-stage/image-join, guest-receive, PCM
source/consumer, and all lifecycle/slot/status/descriptor/key-on fields.
Add only the smallest positive-control census needed to make
`[filter-voice-audit-control]` fire; do not interpret a zero filter/voice
count without that control. Run the two arms from one build with the validated
sequential input recipe if concurrent PID input again fails its phase gate.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2332_m5_destination_slot_keyon.sh
    zsh scratch/agent/run_s2332_m5_destination_slot_keyon.sh s2332_m5_destination_slot_keyon
