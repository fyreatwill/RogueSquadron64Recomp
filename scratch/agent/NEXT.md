# NEXT work unit (s986)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Extend the existing positive-controlled F5 census to sample the RDRAM bytes at
each phase-6 `0x02 VTXCOLOR` source address and the relevant `0x03 MOVEMEM`
source, then pair those values with scoped `ROGUESQ_LOG_SHADE_RAW` records in
isolated ungated LLE mode. Keep `ROGUESQ_FIX_ZERO_SHADE` unchanged.

## Competing hypotheses and discriminating measurement

- H-downstream-writer: nonzero VTXCOLOR payload reaches the F5 path, but a later writer/state conversion produces zero shade.
- H-game-state-zero: VTXCOLOR/MOVEMEM payload bytes are already zero or sentinel-valued in the zero-shade phase, identifying the game state writer as origin.
- H-payload-address: the command source addresses point outside the expected RDRAM/color data region, so the apparent nonzero update stream is an address/ownership mismatch.

Discriminating measurement: sample the payload bytes named by each positive
controlled update and compare phase-6 zero-shade values against phase-4
good-shade values. Nonzero payload with zero shade selects H-downstream-writer;
zero/sentinel payload selects H-game-state-zero; out-of-region or unstable
addresses select H-payload-address. Missing fetch/state controls invalidate the
run.

Exact commands:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LOG_F5_STATE=1 ROGUESQ_LOG_SHADE_RAW=1 ROGUESQ_FIX_ZERO_SHADE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='8:start' zsh tools/probe.sh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/runs/s986_f5_state_payload 60 0.5`

Expected result: the run reaches the 512-width positive control and emits
`[f5-state-control]` records for both opcodes. Fold the phase-tagged state and
shade classes into the ledger; do not land a mitigation from this probe.
