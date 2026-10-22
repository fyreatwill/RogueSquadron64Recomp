# NEXT: why runModelViewerLoop (0x800C9BF0) never exits for planet asset 2/3 (levels 10/15) but does for asset 0/1 (levels 0/5)

HYPOTHESIS-ID: g1-mission-coverage-sweep

H1 exit depends on a per-asset animation/timer/model load that stalls for asset 2/3 (recomp or data bug).
H2 exit needs a button our autopilot never sends in a form the viewer reads (but level 5 exits with same keys -> weak).
H3 legit retail behaviour needing longer time than 880 s (unlikely).
Discriminator: one build logging, per frame of the viewer loop, the exit-flag slots (see subagent findings; re-derive from funcs_36.c:15160 if lost) for levels 5, 10, 15 in the same build; level 5 is the positive control.
Static references: N64Recomp/RecompiledFuncs/funcs_34.c ~6830-7250, funcs_35.c:3138, funcs_36.c:15160.
Then continue queued 17b..18b soaks.
