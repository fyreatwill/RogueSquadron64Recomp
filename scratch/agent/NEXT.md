# Resume s4995 mission-origin caller discriminator with route-qualified driver

HYPOTHESIS-ID: voice-count-before-base-race

The sample is now regeneration-preserved and built, but the s4984 retry did
not reach a mission (`mission_onset_t=-1`), so its zero mission rows are not a
result. Run the known route-qualified s4958 driver once with the current
binary and `ROGUESQ_LOG_S4539=1`; do not change the sample or add a guard,
lock, rewrite, or mitigation. Capture title, hangar, mission origin, s4540
arm, s4987 observations, and PCM controls.

Competing hypotheses:

1. H-uninstrumented-reader: a mission-origin ordinary row is stale while
   s4987 remains current.
2. H-classifier-phase: all mission-origin ordinary rows are current, so the
   old bad predicate is phase-limited.
3. H-no-sample: the qualified route does not execute the sampled caller at a
   mission origin.

Discriminating outcomes:

- Any bounded `status=stale` row at `0x00690400` or `0x00620400` selects
  H-uninstrumented-reader / propagation boundary.
- Mission-origin rows all `status=current` select H-classifier-phase.
- No mission-origin rows after title+hangar+mission controls remain
  H-no-sample/route failure and require another route driver, not a conclusion.

Resume commands:

    test -e tools/apply_s4994_s4540_mission_sample.py
    grep -q 'apply_s4994_s4540_mission_sample.py' tools/fixup_game_funcs_vendored.py
    env ROGUESQ_LOG_S4539=1 zsh scratch/agent/s4958_after_6a2900.sh

ORIGIN: `allocateSongChannelArray` remains the legitimate writer; the boundary
is unexplained and is not a value-rewrite target.
