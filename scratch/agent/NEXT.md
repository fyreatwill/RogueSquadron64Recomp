# NEXT work unit (s2329) — M5 destination-role ground-truth join

HYPOTHESIS-ID: m5-destination-role-ground-truth

## Work unit

Run one ground-truth-first, no-behavior-change destination-role table for the
qualified Factor 5 image route and the silent control. Keep
`ROGUESQ_DRAIN_INLOOP_TICK=1`; the drain A/B is closed at capture scope. Do
not add writeback, address remapping, slot values, guards, or defaults.

## Competing hypotheses and discriminating measurement

- H-RoleSkew: the rotating image destinations have different legitimate roles;
  the stage-only and PCM source/consumer rows map to different output roles.
- H-PostStageConsumerMissing: a target image task completes and publishes a
  nonzero destination, but neither destination has a same-ordinal guest
  slot/key-on/descriptor consumer after image completion.
- H-EarlierTickOnly: all lifecycle rows remain prior-route events, and the
  destination split is only a capture/order artifact rather than a missing
  target consumer.
- H-CoverageInvalid: the independent oracle or either port arm misses the
  required title/hangar, task, image, PCM, or writer controls.

The discriminator is one table keyed by `(arm, phase, origin, audio ordinal,
row, task begin/end, data_ptr, output_buff, stage destination/length/hash/nz,
image completion, PCM source/consumer, same-ordinal lifecycle kind and signed
delta, prior-ordinal lifecycle kind, and host-boundary range)`, with the retail
writer/status rows joined by physical destination role. H-RoleSkew is selected
only if the retail and port destination-role polarity agrees;
H-PostStageConsumerMissing
is selected only if both qualified arms have a nonzero completed stage but no
same-ordinal post-stage consumer; H-EarlierTickOnly is selected if the full
role join closes and only prior-ordinal rows remain. A missing positive control
selects H-CoverageInvalid.

## Exact commands

Create `scratch/agent/run_s2329_m5_destination_role_ground_truth.sh` with the
existing oracle gate plus a new physical watch covering `0x00165000:0x0016B000`,
the status word, the task/output writer PCs, and the qualified eleven-Start
route. Run both `ROGUESQ_AUDIO_UCODE=0` and `=1` arms from one build, then:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2329_m5_destination_role_ground_truth.sh
    zsh scratch/agent/run_s2329_m5_destination_role_ground_truth.sh s2329_m5_destination_role_ground_truth

The launcher must require the oracle whole-RDRAM control, title/hangar VI
origins, named retail writer PCs, `[vi-callers-control]`, `[audtask-abi]`,
image-stage/DMA and image-join rows, `[audio-sp-route] edge=guest-receive`,
and PCM source/consumer controls in both arms. Use SIGKILL cleanup and keep
the filter/voice null unevaluable without its positive control.
