# Resume checkpoint

The prior attempt did not complete the planned caller-boundary discriminator.
The existing artifact `scratch/agent/s4984_atomic_voice_pair_mission/run.log`
does establish the route-qualified provenance split recorded for s4988:
mission publication/mixer rows were `20/0x8018C720`, while four stale
`s4540` rows were `32/0x801714D0` with `a0=0x801724C0`. Its `keys.log` has
mission onset 183 s, `ctl_arm=1`, `s4579A=9`, `bad=8`, `pidma=0`, crash=0,
abort=0, and PCM-positive rows=129. The independent control artifact is
`scratch/agent/s4987_oracle_ground_truth/run.log`; it passed whole-RDRAM and
the watched voice-pair control, but did not reach title/hangar in that short
oracle run. Do not treat this checkpoint as a new hypothesis selection.

# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race

Resume the caller-boundary discriminator: record phase/origin,
`ctx->r31`, `ctx->r4`, and the guest count/base immediately at each bad row,
and join it to the nearest same-origin `s4987` mixer/publication row in the
same run. Preserve title, hangar, mission, allocator, PCM, crash, and abort
controls. Do not add a guard or rewrite any value.

Competing hypotheses:

1. H-propagation: the bad boundary's caller/register state carries an old
   base. Prediction: same-origin mixer/publication is current while `s4540`
   caller state is old.
2. H-uninstrumented-reader: another reader supplies the stale pair before
   `s4540`. Prediction: caller state identifies a different reader/call path.
3. H-classifier: the bad predicate is wrong despite current caller and pair.
   Prediction: all same-origin values are current at the boundary.

Discriminator: one run must pass title and allocator controls and reach both
mission origins. A route-null run is unevaluable.

ORIGIN: legitimate writer is `allocateSongChannelArray`; the defect is an
observation/propagation boundary, not yet explained.

Exact commands:

    python3 tools/apply_s4988_s4540_boundary.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s4984_atomic_voice_pair_mission.sh

If the fixup script is absent, stop and restore/create the regeneration-
preserved instrument before running; do not substitute the old atomic-pair
run as the discriminator.

s4988 controls: mission onset 183 s, s4579-A=9, bad=8, pidma=0,
crash=0, abort=0, PCM nonzero rows=129. Mission publication and mixer rows
were `count=20 base=0x8018C720`, while bad rows saw `count=32
base=0x801714D0`.
