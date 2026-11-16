# NEXT (s7454)
HYPOTHESIS-ID: harness-inits-restart

Class DJ (offline + fake-log controls): recipe pass criteria that cannot tell a same-process mission restart from a relaunch.
Datum: s7449_argck_levels L4 failed `grep -q inits=1` with inits=2, alive_at_end=1, crashlines=0; between [initMission]
call#1 and call#2 the log has endMissionCleanup <- mainGameLoop (game ended and re-inited the mission in one process).
m6_god_common.sh's `inits=` counts [initMission] lines, and its comment says "a relaunch adds one" - two meanings, one number.
Step 1: in m6_god_common.sh summary, add `launches=<n>` (process starts by the harness) and `mission_restarts=<n>`
(same-process [initMission] call#>=2 or endMissionCleanup lines), keep inits= unchanged. Controls: synthetic logs
(1 launch + 2 initMission calls -> launches=1 mission_restarts=1; 2 launches each call#1 -> launches=2 mission_restarts=0).
Step 2: grep every soak_queue/done recipe of s7152+ for `inits=1`; classify which ones mean "no relaunch" (should check
launches=1) vs "no restart". Fix the live templates only (recipes are one-shot).
Hypotheses: H-none (no live recipe template depends on inits=1), H-few, H-many. Discriminator: count of live templates.
If H-none, close in one session and take the next ladder rung per ITERATION.md 3c.
