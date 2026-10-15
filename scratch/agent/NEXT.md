# Resume checkpoint

s4988 completed the phase-scoped provenance run. The final log is
`scratch/agent/s4984_atomic_voice_pair_mission/run.log`; its summary is in
`keys.log`. Independent retail ground truth is in
`scratch/agent/s4987_oracle_ground_truth/run.log`.

# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race

Build one caller-boundary discriminator for `s4540`: record phase/origin,
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

s4988 controls: mission onset 183 s, s4579-A=9, bad=8, pidma=0,
crash=0, abort=0, PCM nonzero rows=129. Mission publication and mixer rows
were `count=20 base=0x8018C720`, while bad rows saw `count=32
base=0x801714D0`.
