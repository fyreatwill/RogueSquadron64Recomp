# Resume s4994 mission-origin caller discriminator

HYPOTHESIS-ID: voice-count-before-base-race

This is a checkpoint resume. The previous retry did not run the experiment:
`tools/apply_s4994_s4540_mission_sample.py` is absent, and no s4994 build or
run artifact exists. Do not rerun the s4993 recipe as an experiment. First
restore or author the regeneration-preserved, bounded phase-scoped sample of
ordinary s4540 caller rows, recording caller `a0`, `r4`, guest count/base, and
current/stale status only at mission origins. Preserve the per-origin bad-row
budget, s4987 publication/observation rows, and all route controls; add no
guard, lock, rewrite, or mitigation.

Competing hypotheses:

1. H-uninstrumented-reader: mission-origin ordinary rows include a stale pair
   while s4987 remains current.
2. H-classifier-phase: all sampled mission-origin rows are current, so the old
   bad predicate is phase-limited.
3. H-no-sample: the qualified route does not execute the sampled caller at a
   mission origin.

Discriminator: after the instrument exists, one qualified run with a bounded
mission-origin sample joined to s4987 selects H-uninstrumented-reader or
H-classifier-phase; no sample is unevaluable.

Resume commands:

    test -e tools/apply_s4994_s4540_mission_sample.py
    python3 tools/apply_s4994_s4540_mission_sample.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s4984_atomic_voice_pair_mission.sh

ORIGIN: `allocateSongChannelArray` remains the legitimate writer; the boundary
is unexplained and is not a value-rewrite target.
