# NEXT work unit (s2242) — obtain a valid field348 producer census

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Run one qualified retry of the unchanged s2241 build and candidate
instrumentation. No new code or build is needed unless the binary is missing;
the s2241 retail oracle already supplied the ground-truth producer range and
passed its positive controls. Treat any run that fails before both target
phase markers as invalid and do not infer a port writer result from it.

## Competing hypotheses and discriminator

- **H-PortWriterAbsent:** both target phases and controls fire, but no
  `[field348-candidate]` rows occur at the five statically enumerated stores.
- **H-PortWriterZero:** candidate rows hit an active source span, but all
  `value_nz=0`.
- **H-PortWriterWrongDestination:** candidate rows carry nonzero values, but
  their physical destinations miss both active spans or populate only the
  inactive origin.
- **H-PortWriterThenZero:** a nonzero candidate row overlaps the active span
  before its first matching image-stage row, followed by a zeroing clear.
- **H-CandidateInstrumentGap:** the route, ABI/DMA/image-stage/PCM controls,
  or the static 5/5 candidate coverage do not hold; the table is invalid.

The discriminating table is keyed by
`(phase,width,origin,route_ordinal,route_row,writer_pc,store_pc,addr,phys,
value,value_nz,span,store_ordinal)`, joined to the existing field348 memset
and image-stage rows. A valid null requires title `1024 @ 0x00790400`, hangar
`512 @ 0x006AB400`, the outside-span writer/memset controls, and nonzero ABI,
DMA, image-stage, and PCM controls in the same run.

## Run

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2242_field348_producers 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2242_field348_producers_driver.log 2>&1
```

The s2241 ground-truth capture is
`scratch/agent/oracle_s2241_field348_producers.log`; do not add another port
instrument before asking the oracle again.
