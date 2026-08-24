# NEXT work unit (s2248) — concurrent image/stub route discriminator

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one same-build concurrent A/B: the full opt-in image arm with the
field348 census, versus an audio-stub arm with the same logging and route
controls. This is the route gate before another producer census. Do not
change generated code, image writeback, consumer behavior, runtime defaults,
or any writer value.

## Competing hypotheses and discriminator

- **H-ImageArmSpecific:** the image arm dies before `1024`, while the stub
  arm reaches `1024` and `512`; the pre-phase failure is image-arm-specific.
- **H-SharedPrephaseNondeterminism:** both arms die before `1024` with
  divergent native or last-guest crash sites; the route blocker is shared
  nondeterminism, not census logging alone.
- **H-ImageArmQualifies:** the image arm reaches `1024` and `512`; its
  field348 writer/stage table becomes evaluable, regardless of the stub arm.
- **H-SharedStableRoute:** both arms reach the target phases; the image-arm
  field348 table is the only remaining discriminator.

The discriminating table is keyed by
`(arm,phase,width,origin,missing_func,crash_symbol,last_guest_pc,
field348_rows,image_stage_rows,image_dma_rows)`. Positive controls are the
startup route, one `[missing-func]`, the 640 origin `0x00696100`, title
`1024 @ 0x00790400`, and hangar `512 @ 0x006AB400`. A target-reaching image
arm resumes the five-store writer hypotheses; two route-invalid arms do not
select a writer.

## Run

```sh
(
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2248_image_census_ab 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2248_image_census_ab_driver.log 2>&1 &
  p_img=$!
  env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2248_stub_control_ab 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2248_stub_control_ab_driver.log 2>&1 &
  p_stub=$!
  wait "$p_img"; r_img=$?
  wait "$p_stub"; r_stub=$?
  print "image_rc=$r_img stub_rc=$r_stub"
)
```

Compare both driver tails and bounded marker counts with
`scratch/s73_post_a_scene/s2248_image_census_ab/run.log` and
`scratch/s73_post_a_scene/s2248_stub_control_ab/run.log`. Do not infer a
writer result unless the image arm has all target-phase and positive-control
rows.
