# NEXT: G1 - confirm lvN follows save byte, then drive missions by forced save byte
Context (s5699): B40 = save rec[5] via applySaveSlotToMissionState at title; hangar does not select level. Queued s5699_force3/force5 soaks (loop runs them between iterations).
Hypotheses: H1 forced N => [lvinit] initMission gCurLevel=N and lvN init enters, mission plays; H2 level N init crashes/stalls (a datum per G1/G4); H3 forced value overwritten (b40w shows other pc).
Discriminator: read SOAK-RESULTS + soak_results/s5699_force*.log + scratch/agent/m6/s5699_force*/run.log: grep saveslot, b40w, lvinit initMission, crashlines, vi_stalls. Then per level: reach, fly, win; each failure = backtrace + root cause.
HYPOTHESIS-ID: g1-level-select
