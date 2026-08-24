# NEXT work unit (s2249) — three-arm C88/image interaction discriminator

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent three-arm route test: the opt-in image with
C88=`1`, the opt-in image with C88=`0`, and the silent stub with C88=`1` as
the qualified route control. Keep the common census, phase gates, and
`ROGUESQ_SPIN_YIELD=1` in every arm. Do not change generated code, image
writeback, consumer behavior, runtime defaults, or any writer value.

## Competing hypotheses and discriminator

- **H-ImageIntrinsic:** both image arms die before title while the stub reaches
  title `1024` and hangar `512`; the failure is intrinsic to the opt-in image
  route and is independent of C88.
- **H-C88ImageInteraction:** image+C88=`1` dies before title but image+C88=`0`
  reaches a target phase or the full route; C88 changes the image arm's fate.
- **H-ImageRouteNondeterminism:** the two image arms diverge in crash symbol,
  last guest PC, or target qualification; the image route remains unstable and
  the C88 split does not select a causal interaction.
- **H-ImageQualifies:** an image arm reaches title and hangar with the positive
  controls; that arm's image-stage and field348 table becomes evaluable.

The discriminating table is keyed by
`(arm,c88,phase,width,origin,missing_func,crash_symbol,last_guest_pc,
field348_rows,image_stage_rows,image_dma_rows)`. Positive controls are
startup, one `[missing-func]`, the 640 origin `0x00696100`, title
`1024 @ 0x00790400`, and hangar `512 @ 0x006AB400`. A writer conclusion is
invalid unless the corresponding image arm has all target-phase controls and
non-null census rows.

## Run

```sh
(
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2249_image_c88_1 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2249_image_c88_1_driver.log 2>&1 &
  p_img1=$!
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2249_image_c88_0 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2249_image_c88_0_driver.log 2>&1 &
  p_img0=$!
  env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2249_stub_c88_1 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2249_stub_c88_1_driver.log 2>&1 &
  p_stub=$!
  wait "$p_img1"; r_img1=$?
  wait "$p_img0"; r_img0=$?
  wait "$p_stub"; r_stub=$?
  print "image_c88_1_rc=$r_img1 image_c88_0_rc=$r_img0 stub_c88_1_rc=$r_stub"
)
```

Compare the three driver tails and bounded marker counts with their
`scratch/s73_post_a_scene/s2249_*/run.log` files. If both image arms are
route-invalid, do not repeat the field348 census; classify the C88 split from
the crash/phase table and move only then to the next discriminator.
