RESUME instruction: do not rerun the interrupted/finished s5565 work unit in
this checkpoint. The existing schema-v2 changes are in commit 73a55a0eb and
the known capture is a valid bounded smoke test, but remains H3 because it
lacks a port whole-RDRAM positive control and has fewer than 20 shared rows at
either mapped PC. The next iteration should add that control plus an explicit
VI/task phase join, then run one bounded hangar capture and the comparison.

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

Exact next commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j2
    env TAG=s5566_m4_port_controls XENV='ROGUESQ_LOG_M4_NORM=1 ROGUESQ_LOG_M4_Y8000=1 ROGUESQ_LOG_M4_PORT_RDRAM=1' HOLD=20 STOP=520 LATE=95 LATE_NOSTART=1 LKEY=a zsh scratch/agent/m6_god_common.sh
    python3 tools/analyze_m4_normalized.py --self-test

Resume artifacts: `src/rsp/dpc_bridge.cpp`, `tools/fixup_factor5_ucode.py`,
`tools/analyze_m4_normalized.py`, and the Session 5565 ledger entry. Do not
infer an accumulator writer or add a mitigation from the existing capture.

Ground-truth gate: the retail RSM2/RSD2 capture already qualifies whole-RAM,
VI, mapped-PC, image, and instruction-progress controls. Do not add another
port field until the port whole-RAM control and phase/task join are measured in
the same run.

HYPOTHESIS-ID: m4-normalized-boundary-schema
