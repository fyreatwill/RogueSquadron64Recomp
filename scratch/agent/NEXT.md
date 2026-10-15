# Resume checkpoint

The s4990 caller-boundary run was route-qualified: title, hangar, both mission
origins, `ctl_arm=1`, `s4579A=9`, PCM-positive rows=149, crash=0, abort=0.
The new fields fired on four bad rows, but all four were at origins
`0x644D00`/`0x6A2900`; the mission-origin s4987 rows remained current at
`20/0x8018C720`. The run-lifetime bad-row cap prevented the required join.

# Next work unit

HYPOTHESIS-ID: voice-count-before-base-race

Change only the s4540 bad-row diagnostic budget to reset on each committed
origin, so the same run can capture up to four bad rows per origin. Preserve
the existing phase/origin, `r31`, `r4`, guest count/base, s4987 publication and
observation rows, and all route controls. Do not add a guard, lock, or value
rewrite.

Competing hypotheses:

1. H-propagation: a mission-origin bad boundary carries an old pair while the
   same-origin mixer/publication rows are current. Prediction: bad caller state
   is old and same-origin s4987 is `20/0x8018C720`.
2. H-uninstrumented-reader: another reader supplies the stale pair before
   s4540. Prediction: same-origin bad caller state identifies a distinct path
   or stale propagation boundary.
3. H-classifier: the bad predicate is wrong. Prediction: same-origin boundary
   values are current and agree with s4987.

Discriminator: one run must pass title, hangar, both mission origins, allocator
and PCM controls. A mission-origin bad row with a same-origin s4987 join is
required; if none fires, the result is unevaluable.

ORIGIN: legitimate writer is `allocateSongChannelArray`; the defect is an
observation/propagation boundary, not yet explained.

Exact commands:

    python3 tools/apply_s4988_s4540_boundary.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s4984_atomic_voice_pair_mission.sh
