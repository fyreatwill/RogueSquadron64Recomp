Single next unit: add the missing port whole-RDRAM positive control and an
explicit VI/task phase join to the normalized capture, then run one bounded
hangar capture and the analyzer against the qualified retail RSM2/RSD2 capture.
The s5565 capture is a valid bounded schema smoke test but remains H3; do not
infer a writer from it.

Competing hypotheses and discriminator:

1. H1: the port controls and phase/task join pass; normalized rows share both
   mapped PCs with retail at >=20 rows per PC.
2. H2: controls and shared rows pass, but a repeated lane or writer-PC mismatch
   remains in a phase/image/progress class.
3. H3: the port still cannot supply an independent control or >=20 shared rows,
   so the normalized comparison remains unevaluable.

Discriminating measurement: one bounded hangar capture must show a firing
whole-RAM control, a VI/task phase join, a nonzero monotonic task-local
instruction total at task end, a stable image ID, and both mapped PCs; then run
`python3 tools/analyze_m4_normalized.py --self-test` and the retail/port
comparison. H1/H2 require >=20 shared normalized rows per mapped PC; otherwise
select H3. Keep the legacy port logs H3.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j2
    env TAG=s5566_m4_port_controls XENV='ROGUESQ_LOG_M4_NORM=1 ROGUESQ_LOG_M4_Y8000=1 ROGUESQ_LOG_M4_PORT_RDRAM=1' HOLD=20 STOP=520 LATE=95 LATE_NOSTART=1 LKEY=a zsh scratch/agent/m6_god_common.sh
    python3 tools/analyze_m4_normalized.py --self-test

Ground-truth gate: the retail RSM2/RSD2 capture already qualifies whole-RAM,
VI, mapped-PC, image, and instruction-progress controls. Do not add another
port field until the port whole-RAM control and phase/task join are measured in
the same run.

HYPOTHESIS-ID: m4-normalized-boundary-schema
