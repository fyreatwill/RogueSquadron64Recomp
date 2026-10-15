# UNBLOCK s4959
Route 2 (satisfy locally), after route 1 showed the block's premise was wrong-scoped: the "human decision" it asked for (how to run multi-minute recipes) is already answered by the soak queue in tools/agent/ITERATION.md (loop runs recipes between iterations, 600 s cap each). The blocker itself named the fix: split x3 into three one-run soaks.
Done: scratch/agent/soak_queue/s4959_mission_run{1,2,3}.sh (self-contained, root derived via git, SIGKILL, nonzero exit on no-title/no-hangar/crash/no-mission). zsh -n syntax check passes; the soaks have NOT run yet, so there is no game result this iteration.
Risk: worst-case path timing can exceed 600 s (typical expected ~300 s); rc=137 means timeout, not a mission result. Loop runs 2 soaks/iter, so run3 lands one iteration later.
