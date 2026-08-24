# NEXT work unit (s2235) — join retail task output to the port image stage

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Run one qualified port image-arm capture using the existing generated
instrumentation. Keep the default silent arm unchanged. Phase-gate the driven
route at title `1024` and retain the first-target/hangar rows. Join, per audio
task ordinal and phase, the image-stage rows, `data_ptr+0x100`/DMA ranges,
image completion, host writeback, and PCM source/consumer rows against the
selected retail task-output writer/destination rows from s2234. This is a
measurement-only run; no task-field rewrite, writeback, consumer guard,
audio default, gate, wait, slot, or voice change is authorized.

## Competing hypotheses and discriminating measurement

- **H-PortTaskOutputMatch:** the image arm's stage/DMA output reaches the same
  task-output span represented by the retail post-target rows, with matching
  destination/range and completion ordering; the exact PCM ring is populated
  by a later consumer or separate writer.
- **H-PortImageDirectPCM:** an image stage or its immediate DMA/host boundary
  joins directly to the exact PCM ring and its PCM source/consumer hash; the
  retail task-output rows are control data rather than the image output edge.
- **H-PortContractGap:** image DMEM/DMA/break/SP controls are positive, but
  neither stage→task-output nor stage→PCM joins for the same ordinal close;
  the missing edge remains in the image/output contract.
- **H-PortNoTargetRoute:** the image run fails to reach the required phases or
  lacks a same-run positive control, making all narrow nulls unevaluable.

The discriminator is one phase-keyed table with rows keyed by
`(audio ordinal, phase, width, origin)` and carrying: task fields and source
hash; DMEM change; every nonzero DMA range; image stages 0–3 and their
destination/field values; image break PC and SP completion; host writeback
range/hash; PCM source and consumer address/count/hash; and route phase.
Compare stage/DMA/writeback ranges with retail's selected post-target rows at
`0x171F70:0x173DB4`, and compare PCM rows with the exact retail ring
`0x166450:0x169450`. The positive controls are nonzero image ABI/DMEM/DMA
rows, `break_pc=0x1328`, SP completion, PCM boundary rows, and all three route
phases. A task-output join selects H-PortTaskOutputMatch; an ordinal/hash
stage-to-PCM join selects H-PortImageDirectPCM; positive task controls with
both joins absent selects H-PortContractGap; missing controls selects
H-PortNoTargetRoute.

## Exact command

No build is required: use the current build carrying the image-stage, ABI,
DMA, host-boundary, and PCM-boundary witnesses. Run from the repository root
with the route driver; `env` keeps the permission prefix match intact.

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2235_image_join 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2235_image_join_driver.log 2>&1
```

Read only bounded result rows:

```sh
log=scratch/s73_post_a_scene/s2235_image_join/run.log
grep -a -n -E '\[audtask-(abi|dma-row|dma-range|image-stage|image-stage-row|image-join|image-summary|image-consumer-only)|\[pcm-boundary-(source|consumer)|\[m5-host-boundary|\[sp\].*complete|\[phase\]' "$log" | tail -240
grep -a -n -E 'CRASH|UnhandledJump|last phase|lle tasks|exit=|--- done ---' scratch/agent/s2235_image_join_driver.log | tail -80
```
