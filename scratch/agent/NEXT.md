# NEXT work unit (s2187) — failing image-arm join coverage

HYPOTHESIS-ID: m5-a1-failing-image-join

## Work unit

Run one fresh image-arm recipe with the already qualified LLE/spin route and
the image arm enabled. Classify the run only if it has both a positive
`[audtask-image-join]` count and a phase-gated 640 row at origin
`0x00696100`. Use the existing runner; do not add a port instrument, rebuild,
or land a mitigation.

Exact command from the repository root:

```sh
env GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1 ROGUESQ_LOG_AUDTASK_IMAGE_JOIN=1' zsh scratch/s73_post_a_scene/run_mission_keys.sh s2187_image_cinematic 30 12
```

Watch the game launched by that script for at most 180 seconds, SIGKILL it
and its process group, and write the compact parse to
`scratch/agent/s2187_image_join.txt`. Count image joins by VI width/origin
and test interval overlap against physical `0x25A580`, `0x0CA748`,
`0x0C7B0C`, `0x165E40`, `0x0CDB58`, and `0x2231EC`. Require both positive
controls before interpreting a zero.

## Competing hypotheses and discriminator

- H-AudioDmaHitsCutscene: image joins occur at 640/`0x00696100` and at least
  one interval overlaps a named cinematic word.
- H-AudioDmaTitleHangarOnly: image joins are positive but all joins remain
  in title/hangar phases and have no named-word overlap.
- H-AudioDmaNoCinematicOverlap: image joins occur during 640/`0x00696100`
  but have no named-word overlap, separating audio-DMA timing from the
  six-word writer results.
- H-JoinCoverageFailure: either the image-join control or the required 640
  phase is absent, so the run selects coverage-only and no destination claim.

The discriminator is one same-run table of join count, VI width/origin,
interval overlap, title/hangar reach, and terminal outcome. Do not add a
copyToRAM/CIMG/DMA guard, disable `NAN_CHECK`, skip/allow cinematic loads,
or re-flip the image-arm default.
