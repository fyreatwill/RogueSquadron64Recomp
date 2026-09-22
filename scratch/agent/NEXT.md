# Next work unit: qualify the DMEM predecessor join, then identify the producer

HYPOTHESIS-ID: m5-zero-dmem-producer

S3694 added the predecessor fields but did not produce a valid target table.
Retail controls passed. The first paired port run omitted
`ROGUESQ_LLE_UNGATED=1`; the corrected pair qualified only the silent arm,
and the real arm's target source callback remained absent through a recurring
audio-pump stall. The final real-arm retry reached title and hangar but its
DMEM/source positive control did not fire. Do not interpret this as a null
producer result.

Competing hypotheses remain:

- `H-ZeroDMEMProducer`: the port creates zero payload in DMEM before DMA.
- `H-DMEMJoinMismatch`: the zero payload belongs to another route or DMEM
  lifetime, not the observed hangar DMA row.
- `H-RetailSourceIsDifferent`: retail writer PCs use a source path the port
  does not reproduce.

Discriminator: one target-phase table covering the source-range DMA rows,
with the immediate DMEM predecessor fields and route identity. The DMEM
source control and a target source-row control must both fire first. A same-
route predecessor selects `H-ZeroDMEMProducer`; a contradictory route join
selects `H-DMEMJoinMismatch`; no corresponding port producer alongside the
retail writer PCs selects `H-RetailSourceIsDifferent`; absent target rows are
unevaluable.

Run the existing retail oracle control before any new build. Then use the
already-built binary from `build/` with the validated real arm:

```sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 \
ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_AUTOPILOT=3:start,6:start,9:start,12:start,16:a,20:a \
ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ROGUESQ_LOG_M5_SOURCE_WRITER=1 \
ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_INPUT_WRITER=1 \
./RogueSquadron64Recomp
```

Require both `[m5-rsp-source-hook-control]` and target
`[m5-dmem-source-control]`/`[m5-source-range-writer]` rows. If the latter
still does not fire while VI 1024 and 512 do, investigate the audio-pump
route boundary as the next M5 unit; do not add another join field.
