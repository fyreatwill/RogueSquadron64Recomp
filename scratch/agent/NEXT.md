# NEXT work unit (s2496) — locate the first downstream image consumer

HYPOTHESIS-ID: m5-generated-image-downstream-join

## Single work unit

Perform one bounded provenance audit of the first post-image-stage consumer.
Use the existing retail oracle ground-truth ranges and the s2495 port log to
enumerate candidate writers/readers for the image destinations
`0x00166450..0x00169150` and `0x001798B0..0x00179A48`, then capture one
phase-keyed port table at the earliest candidate boundary. Preserve the
qualified image arm and all existing controls. Do not map through `gspTask`,
infer identity from ordering, or change task/output behavior.

## Competing hypotheses and discriminator

- H-image-consumer-writer: a named generated/runtime writer consumes an image
  destination or ordinal and produces a downstream slot, voice, PCM, or output
  state transition.
- H-image-consumer-reader-only: the image destination is written and returned,
  but no downstream consumer in the candidate set reads it before the observed
  output/PCM boundary.
- H-image-consumer-unreachable: the candidate boundary is not reached in the
  target phase despite live image-stage and return controls.

The discriminator is one table keyed by phase/origin and image ordinal with
candidate site, destination/range, read/write direction, and the first paired
downstream event or state value. A joined candidate site plus downstream event
selects the first hypothesis; live image controls with no candidate read or
state transition select the second; zero candidate rows with all controls live
selects the third. A null is invalid without the same-run positive controls.

## Exact preparation and commands

Before adding any probe, consult the independent oracle artifact and verify
its whole-RDRAM and target-range controls; do not interpret a retail null
without those controls. Inspect the candidate census with bounded searches:

```sh
rg -n "0x00166450|0x00169150|0x001798B0|0x00179A48|167350|1798B0" \
  src lib RecompiledFuncs tools/oracle scratch/agent/s2493_m5_retail_task_join
```

If a single earliest candidate boundary is identified, add all fields for the
table in one build, run the qualified `tools/probe.sh` recipe once with
`PROBE_PHASE_WIDTH=1024`, boot-relative Start presses, `PROBE_LEAVE_OK=1`,
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`,
`ROGUESQ_LOG_M5_DESCRIPTOR=1`, `ROGUESQ_LOG_M5_SCHEDULER_ID=1`, and
`ROGUESQ_LOG_M5_PORT_LOAD=1`, plus the new candidate probe. Capture under
`scratch/agent/s2496_m5_first_image_consumer/` and terminate with SIGKILL.

If static inspection cannot name one earliest candidate, do not add a
diagnostic field: record the census as a blocked discriminator and select the
highest-information static boundary for the following iteration.
