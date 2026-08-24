# NEXT work unit (s2246) — five-store field348 producer census

HYPOTHESIS-ID: m5-image-output-contract-attribution

## Work unit

Run one qualified port capture with the existing image arm and the complete
field348 producer instrumentation from s2241. The s2245 no-log A/B qualified
both arms through title and hangar, so this capture is now allowed to collect
the five scalar-store candidate table. Do not change the image arm, writeback,
consumer, or runtime defaults.

## Competing hypotheses and discriminator

- **H-PortWriterPopulates:** after the active `rs_memset` initialization and
  before the matching image-stage row, one or more of the five annotated
  stores writes nonzero bytes into the active `field348` span. This identifies
  the port producer and its ordering edge.
- **H-PortWriterZero:** the five-store rows cover the active span and occur in
  the expected interval, but all values are zero. This confirms the producer
  path is present while selecting a zero-payload/value-boundary explanation.
- **H-PortWriterWrongDestination:** a nonzero candidate fires, but its guest
  or physical destination does not match the active `field348` span, or it
  occurs only after the image-stage row. This selects destination/order
  mismatch rather than an absent producer.
- **H-PortWriterAbsent:** the qualified controls fire but no candidate store
  reaches either active span before its image-stage rows. This selects a
  missing producer or an instrument-coverage gap; the static 5/5 annotation
  control must be present before treating it as evidence.

The discriminating table is keyed by
`(phase,width,origin,field348_span,store_pc,store_ordinal,dst_guest,dst_physical,value,nonzero_bytes,store_before_stage,stage_rows)`,
with separate title and hangar rows. Positive controls are the common startup
markers, one `[missing-func]` marker, the exact 640 route marker, title
`1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, and the two outside-span
writer controls. A run that misses 640 or either target phase is route-invalid
and cannot select a writer hypothesis.

## Run

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2246_field348_producers 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2246_field348_producers_driver.log 2>&1
```

Compare the bounded driver tail and exact phase/control counts with
`scratch/s73_post_a_scene/s2246_field348_producers/run.log`. If the game or
driver remains alive after the route table is fixed, terminate the identified
process group with SIGKILL and record forced termination separately from a
driver exit.
