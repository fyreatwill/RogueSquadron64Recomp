# NEXT work unit (s2236) — audit Factor 5 image input ingress

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Add one host-side diagnostic field to the existing `rs64_audio_image_stage`
probe in `src/main/main.cpp`: hash the `0x180`-byte RDRAM span addressed by
`field348 & 0x007FFFFF`, and print its FNV/nonzero/valid values beside the
existing stage-0/1 DMEM input spans and stage-2/3 output spans. This is a
measurement-only change. Keep the silent default, the opt-in image arm, task
fields, DMA arguments, completion behavior, gate, wait, slot, and consumer
unchanged.

## Competing hypotheses and discriminating measurement

- **H-ImageIngressMissing:** the `field348` RDRAM source span is nonzero but
  the stage-0/1 DMEM spans (`0xCC0`, `0x3F0`, `0x570`) are zero; the missing
  edge is the image input load or its address/endianness contract.
- **H-ImageInputZero:** both the `field348` RDRAM span and the stage-0/1 DMEM
  spans are zero; the image task receives no usable source data, so the zero
  stage-2/3 outputs are an upstream task/input contract issue.
- **H-ImageTransformLoss:** the `field348` span and at least one stage-0/1
  DMEM span are nonzero, but stage-2/3 output DMEM/DMA spans remain zero; the
  loss is inside the generated image transform or output-buffer path.
- **H-ImageNoTargetRoute:** the run lacks the title/hangar phases or the
  image ABI/DMA/break controls, so the narrow input/output nulls are not
  evaluable.

The discriminator is one phase-keyed table keyed by `(phase, width, origin,
audio ordinal, stage)` carrying `field348` address/hash/nonzero/valid,
stage-0/1 DMEM hashes/nonzero values, stage-2/3 DMA/output hashes/nonzero
values, and completion ordering. H-ImageIngressMissing is selected by
nonzero field348 with zero stage-0/1 DMEM; H-ImageInputZero by zero at both
boundaries; H-ImageTransformLoss by nonzero input and zero output; missing
route controls select H-ImageNoTargetRoute. Positive controls in the same run
are the title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, nonzero ABI
DMEM-change rows, DMA rows with `break_pc=0x1328`, and PCM boundary rows.

## Exact commands

Before building, edit only `src/main/main.cpp` with `apply_patch`: in
`rs64_audio_image_stage`, compute the masked `field348` RDRAM hash with the
existing `rs64_audio_hash_rdram` helper and add `field348_fnv`,
`field348_nz`, and `field348_valid` to the existing
`[audtask-image-stage]` line. Then build once and run one capture:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2236_image_input 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2236_image_input_driver.log 2>&1
```

Read only bounded rows after the run:

```sh
log=scratch/s73_post_a_scene/s2236_image_input/run.log
rg -a '\[audtask-image-stage\].*(phase=8|phase=10)' "$log" | tail -160
rg -a '\[audtask-image-summary\]|\[audtask-abi\]|\[audtask-dma-row\]|\[pcm-boundary-(source|consumer)|\[phase\]' "$log" | tail -240
rg -a 'CRASH|UnhandledJump|last phase|lle tasks|exit=|--- done ---' scratch/agent/s2236_image_input_driver.log | tail -80
```

No audio default flip, writeback/consumer guard, task-field rewrite, or
mitigation is authorized by any outcome.
