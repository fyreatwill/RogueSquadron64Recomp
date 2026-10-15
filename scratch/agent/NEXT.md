# Next work unit

HYPOTHESIS-ID: voice-count-before-base-race

Retain the per-origin s4540 bad-row budget and add one phase-scoped sample of
ordinary s4540 caller rows at mission origins. Record caller `a0`, `r4`, guest
count/base, and a current/stale classification, with a bounded per-origin
sample. Preserve s4987 publication/observation rows and all route controls.
Do not add a guard, lock, or value rewrite.

Competing hypotheses:

1. H-uninstrumented-reader: mission-origin ordinary caller rows include a
   stale `a0`/pair while s4987 remains current. This identifies the stale path
   without requiring the narrow bad predicate to fire.
2. H-classifier-phase: all mission-origin caller rows are current, showing the
   old bad-row predicate is limited to pre-mission origins rather than exposing
   a mission handoff.
3. H-no-sample: the mission route is qualified but the caller does not execute
   at a sampled mission origin; the boundary remains unevaluable.

Discriminator: one run must pass title, hangar, both mission origins, allocator
and PCM controls. A bounded mission-origin ordinary-row sample joined to the
same-origin s4987 current pair selects H-uninstrumented-reader or
H-classifier-phase; no sample is unevaluable.

ORIGIN: legitimate writer is `allocateSongChannelArray`; this remains an
observation/propagation boundary, not a value-rewrite target.

Exact commands:

    python3 tools/apply_s4991_per_origin_bad_budget.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    python3 tools/apply_s4994_s4540_mission_sample.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s4984_atomic_voice_pair_mission.sh

The sampled rows must be phase/origin joined to s4987. Do not rerun the prior
run-lifetime-capped arm.
