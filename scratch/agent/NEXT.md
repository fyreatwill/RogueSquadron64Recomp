# NEXT: fold g1_lvl10long / g1_lvl15long soak verdicts (viewer auto-advance at ~790 s, s5942)

HYPOTHESIS-ID: g1-mission-coverage-sweep

H1 viewer exits via G2 timer at ~790-850 s and mission reaches flight (levels 10/15 then pass (a)).
H2 exit completes but post-viewer path fails/stalls (new datum to root-cause).
H3 lvl15 timer is even longer / different gate.
Read scratch/agent/SOAK-RESULTS.md tail; then scratch/agent/m6/g1_lvl10long/run.log: grep 'mv-ship-arm|throttle-ret|origin=0x00?69'. 
Optional speed-up: add a ROGUESQ env in the fixup (s5705 force-unlock site, tools/fixup_game_funcs_vendored.py:38012) that also sets bit asset+1 of byte 0x8013A663 so G1 fires instantly; verify against lvl5 control.
Then continue G1: remaining levels (b) holds, (c)/(d).
