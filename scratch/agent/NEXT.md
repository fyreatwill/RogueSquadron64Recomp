# NEXT work unit (s2184) — instrumented failing image-DMA cinematic run

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

Run one fresh `ROGUESQ_AUDIO_UCODE=1` soak using the existing
`ROGUESQ_LOG_ALL=1` audio-task instrumentation, but classify the result only
if the same log has both the 640 cinematic phase and an image-DMA positive
control. The s2183 census found two completing logs with title/hangar-only
joins, while the older failing s2179 log had no image-DMA rows at all.

Use the self-contained soak recipe pattern from
`scratch/agent/soak_queue/done/s2181_image_vec3_f2_20260823-121351.sh`, with a
new tag `s2184_image_dma_cinematic`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LOG_ALL=1`, and
`ROGUESQ_LOG_CUTSCENE_A2_50=1`. Launch through
`zsh scratch/s73_post_a_scene/run_mission_keys.sh <tag> 30 12`, watchdog for
180 seconds, and SIGKILL the game and driver. Do not rebuild.

## Competing hypotheses and discriminator

- `H-AudioDmaHitsCutscene`: `[audtask-image-join]` has a positive control and
  a 640 / `0x00696100` or `0x00696600` row whose `[dest,dest+len)` overlaps
  one of the six named cutscene physical words.
- `H-AudioDmaTitleHangarOnly`: positive-control joins exist, but all are
  1024 / `0x00790400` or 512 / `0x006AB400`, with no 640 image join.
- `H-AudioDmaElsewhere`: positive-control joins exist at 640, but no interval
  overlaps a named cutscene word.
- `H-CoverageFailure`: the run reaches 640 but has zero image joins anywhere;
  this is an instrumentation/coverage result, not a no-DMA result.

The discriminating measurement is one same-run table of image-join counts by
`(phase,width,origin)` plus interval overlap against:
`0x25A580`, `0x0CA748`, `0x0C7B0C`, `0x165E40`, `0x0CDB58`, and `0x2231EC`.
Require `[audtask-image-join] n>0` as the positive control before selecting
any destination hypothesis. If the run fails before title/hangar, report
coverage separately and do not infer a cinematic writer.

Do not S32-address, NULL-skip, re-flip default-on, skip/allow the lwc,
transform, or extract jal, disable `NAN_CHECK`, or add a copyToRAM/CIMG/DMA
writeback guard. If an interval overlaps, identify its writer before any
mitigation.
