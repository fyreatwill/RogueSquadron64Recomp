# Next: m6-mission-stall — mission is stable 426 s; move to M5 de-stub plan step
HYPOTHESIS-ID: m6-mission-stall
Fact (s5089): s5085_stall.sh in with WIN=420 -> NO_STALL at 426 s past onset, crash=0 (n=3 incl. s5086/87). 1 of 2 runs flaked in hangar (updateHangarBayScene+76424 SEGV, known family).
Step 1: treat the stall thread as closed; next work unit = next unexecuted step of docs/M5-AUDIO-PLAN.md.
Step 2 (opt, on next regen): tee fixup_game_funcs.py output, read `[s4648-replay] apply_s4296` line.
