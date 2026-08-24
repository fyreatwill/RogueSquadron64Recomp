# NEXT work unit (s2247) — retry the qualified field348 producer census

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one more full field348 producer census with the existing image arm and
the complete five-store instrumentation. s2246 was route-invalid: two full
census arms and a low-logging image control all died before the target phases.
Do not change the image arm, writeback, consumer, runtime defaults, or writer
values. The retail whole-RDRAM/source-writer ground truth is already present
from s2237/s2241; no new instrument is needed before this retry.

## Competing hypotheses and discriminator

- **H-PortWriterPopulates:** a candidate store writes nonzero bytes into the
  active field348 span before its matching image-stage row.
- **H-PortWriterZero:** candidate stores cover the active span in the expected
  interval, but all bytes are zero.
- **H-PortWriterWrongDestination:** a nonzero candidate targets another span or
  occurs after the image-stage row.
- **H-PortWriterAbsent:** the route and static 5/5 annotation controls fire,
  but no candidate reaches either active span before its stage row.

The discriminating table is keyed by
`(phase,width,origin,field348_span,store_pc,store_ordinal,dst_guest,dst_physical,value,nonzero_bytes,store_before_stage,stage_rows)`.
Positive controls are startup, one `[missing-func]`, the 640 origin
`0x00696100`, title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, and the
two outside-span writer controls. Missing either target phase is route-invalid
and cannot select a writer hypothesis. If another pre-1024 crash occurs, the
crash PC and last guest PC are the result; do not infer a writer null.

## Run

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2247_field348_producers_retry 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2247_field348_producers_retry_driver.log 2>&1
```

Compare the bounded driver tail and exact phase/control counts with
`scratch/s73_post_a_scene/s2247_field348_producers_retry/run.log`. If the
game remains alive after the route table is fixed, terminate its identified
process group with SIGKILL and record forced termination separately.
