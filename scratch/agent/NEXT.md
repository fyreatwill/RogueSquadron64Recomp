# Next: m6-mission-stall — extend the post-mission window; log the replay line on next regen
HYPOTHESIS-ID: m6-mission-stall
Fact (s5086+s5087, n=2): with s4296, the keyed mission soak runs 175-186 s past onset with no stall, crash=0.
Step 1: on the next regen, tee fixup_game_funcs.py output and read the `[s4648-replay] apply_s4296` line to settle skip-vs-overwrite.
Step 2: extend the post-onset window (hold loop in scratch/agent/s5085_stall.sh) to see what ends the mission (debrief/title?). Run from repo root: `zsh scratch/agent/s5085_stall.sh in` in the background.
Note (s5088): maintenance done; CURRENT-TRUTH is 45 KB. Optional next maintenance: renumber "Next steps" backlog.
