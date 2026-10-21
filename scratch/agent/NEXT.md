# NEXT: [mtm] fold s5751 any-a0 backtrace soaks
Full stderr: scratch/agent/m6/s5751_mtma/run.log and _mtmb. `grep -a -A26 'BACKTRACE a0=' run.log`. Control: '[mtm] n=' lines.
Frames name the host-side caller of requestMissionTransitionMode (a0=1, ra=0 seen in s5750). Hypotheses: caller is a bool-arm function (checkComplexObjectives/setHudEnableBit4) vs a game-over/timer path (H2). Symbols may be sparse: map addresses via nm/atos on build/RogueSquadron64Recomp.
HYPOTHESIS-ID: g1-nonhealth-fail
