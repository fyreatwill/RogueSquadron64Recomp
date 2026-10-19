Single next unit: replace the port normalized-row progress ordinal with an
observed task instruction counter and add a phase-scoped row cap, then run one
new hangar capture and the analyzer against the qualified retail RSM2/RSD2
capture. Do not compare the current 5.6M-row log as if its progress field were
retail instruction count.

Competing hypotheses and discriminator:

1. H1: the port task loop exposes a real instruction count; normalized rows
   share both mapped PCs with retail at >=20 rows per PC and lane distributions
   agree.
2. H2: real task progress is available and shared rows form, but a repeated
   lane or writer-PC mismatch remains in a phase/image/progress class.
3. H3: the port cannot expose an independent instruction count or positive
   control, so the normalized comparison remains unevaluable.

Discriminating measurement: one bounded hangar capture must show a nonzero,
monotonic task-local instruction total at task end, a stable image ID, both
mapped PCs, and the whole-RAM/VI/mapped-PC controls; then run
`python3 tools/analyze_m4_normalized.py --self-test` and the retail/port
comparison. H1/H2 require >=20 shared normalized rows per mapped PC; otherwise
select H3. Keep the legacy port logs H3.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j2
    env TAG=s5564_m4_port XENV='ROGUESQ_LOG_M4_NORM=1 ROGUESQ_LOG_M4_Y8000=1' HOLD=20 STOP=520 LATE=95 LATE_NOSTART=1 LKEY=a zsh scratch/agent/m6_god_common.sh
    python3 tools/analyze_m4_normalized.py --self-test

Ground-truth gate: do not add another port field until the retail RSM2/RSD2
contract and its whole-RAM, VI, and mapped-PC controls are available for the
same comparison.

HYPOTHESIS-ID: m4-normalized-boundary-schema
