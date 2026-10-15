# RESUME s4997 mission-origin caller discriminator with route-qualified driver

HYPOTHESIS-ID: voice-count-before-base-race

Resume state: the regeneration-preserved sample exists at
`tools/apply_s4994_s4540_mission_sample.py`, is registered in
`tools/fixup_game_funcs_vendored.py`, and built successfully. The attempted
validation reached title/hangar and pre-mission `0x00656400`, but not either
mission origin (`mission_onset_t=-1`); crash markers were present. The arm and
s4987 controls fired, so the diagnostic is live, but the run selected nothing.
The checkpoint iteration is closed without rerunning it. On the next
iteration, run exactly the route-qualified driver below once with no code or
instrumentation changes.

Competing hypotheses:

1. H-uninstrumented-reader: a mission-origin ordinary row is stale while
   s4987 remains current.
2. H-classifier-phase: all mission-origin ordinary rows are current, so the
   old bad predicate is phase-limited.
3. H-no-sample: the qualified route does not execute the sampled caller at a
   mission origin.

Discriminating outcomes:

- A bounded `status=stale` row at `0x00690400` or `0x00620400` selects
  H-uninstrumented-reader / propagation boundary.
- Mission-origin rows all `status=current` select H-classifier-phase.
- No mission-origin rows after title, hangar, mission, arm, observation, and
  PCM controls remain unevaluable as H-no-sample/route failure; do not treat
  the zero as evidence about the writer.

Exact next command:

    test -e tools/apply_s4994_s4540_mission_sample.py
    grep -q 'apply_s4994_s4540_mission_sample.py' tools/fixup_game_funcs_vendored.py
    env ROGUESQ_LOG_S4539=1 zsh scratch/agent/s4958_after_6a2900.sh

Capture title, hangar, both mission origins, s4540 arm, s4987 observations,
mission onset, crash/abort markers, and PCM controls. ORIGIN:
`allocateSongChannelArray` remains the legitimate writer; this is an
unexplained observation/propagation boundary, not a value-rewrite target.
