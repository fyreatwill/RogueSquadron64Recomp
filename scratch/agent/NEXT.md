# NEXT (s7314): enforce "one game run at a time" in the loop's soak phase
HYPOTHESIS-ID: harness-one-game
Context (s7313): s7312's "stale presented frame" was a leftover game captured by `pgrep|head -1`. Iteration-side tools now use
tools/rs64_game_pid.zsh (exactly one game or nothing; test tools/s7313_pid_test/run.zsh 8/8). The loop itself is still open:
tools/agent/loop.sh run_soak_pass (lines ~264-330) launches each queued recipe with no check that a game from the iteration (or a
previous soak whose process group escaped the `kill -9 -- -$pid`) is still alive. A leftover game would double CPU load (frame-time
verdicts), steal window/key focus, and confuse any recipe that picks a pid by name.
Hypotheses:
- H-clean: no soak has ever started with a foreign game alive. Predicts: 0 hits in a retro scan of soak_results logs for
  overlapping game lifetimes (each recipe log carries its own start/end; the game logs carry pids in [startup] lines, if any).
- H-leak: some have. Predicts: >=1 soak whose window overlaps another game's lifetime.
Bounded change either way: before each recipe, `. tools/rs64_game_pid.zsh; rs64_no_foreign_game 30` and if it fails, log the pids,
SIGKILL them (the iteration has ended, so any game alive is a leftover), and note "foreign game killed" in the SOAK-RESULTS verdict line.
Also check after each recipe that its own game died (pgrep empty after the process-group kill), and log it if not.
Positive control: tools/agent/test_soak_idle_gate.sh style test: start the s7313 fake sleeper named RogueSquadron64Recomp, run one
pass of run_soak_pass on a trivial recipe, and assert the log line and that the fake was killed. Keep loop.sh changes minimal; it
re-execs itself when edited (s7235).
