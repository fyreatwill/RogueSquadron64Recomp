# Resume checkpoint

The s4986 narrow-lock validation completed. Its log is
scratch/agent/s4984_atomic_voice_pair_mission/run.log and its summary is in
keys.log.

# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race

Build one whole-table provenance instrument for the stale-pair rows, then run
one phase-gated armed mission soak. Record the value and phase at every
allocator publication of base/count, every mixer count/base observation, and
the s4540 argument that is classified as kind=bad. Preserve title, hangar,
mission, allocator, PCM, crash, and abort controls. Do not add a guard or
rewrite any value.

Competing hypotheses:

1. H-propagation: allocator and mixer pairs are current, but s4540 receives
   an old base through caller/register propagation. Prediction: publication
   and mixer rows agree while bad-row argument differs.
2. H-writer: the allocator publishes a stale base or count. Prediction:
   publication rows themselves contain the bad pair.
3. H-uninstrumented-reader: the instrumented count/base loads are current,
   but another reader or path generates the bad classification. Prediction:
   bad rows persist without a matching stale instrumented pair.
4. H-classifier: all observed pairs and s4540 arguments are current, so the
   bad predicate or its address classification is wrong. Prediction: bad rows
   have no stale value at any captured boundary.

Discriminator: one run must pass title and allocator controls and reach
mission. A stale publication selects H-writer; current publication and
mixer pair with stale s4540 selects H-propagation; current all-boundary rows
with bad selects H-uninstrumented-reader or H-classifier, separated by
whether an uncaptured reader marker is present. A route-null run is
unevaluable.

ORIGIN: the legitimate writer is allocateSongChannelArray, publishing count
32 and its voice-array base. This is provenance instrumentation, not a
mitigation.

Exact commands:

    python3 tools/apply_s4987_voice_pair_provenance.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s4984_atomic_voice_pair_mission.sh

The prior narrow-lock arm already showed: mission onset 180 s,
s4579-A=9, bad=8, pidma=0, crash=0, abort=0, PCM nonzero rows=146.
