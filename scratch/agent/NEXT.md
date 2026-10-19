Single next work unit (s5587): fold the s5584_plume_title_hold soak (N=4 LLE-trio boots held 120 s past first title origin). The loop runs it between iterations; do NOT run the game yourself.
Commands:
  ls scratch/agent/soak_results/s5584_plume_title_hold/ && cat scratch/agent/soak_results/s5584_plume_title_hold/summary
  grep -a ALIVE_AT_+120 scratch/agent/soak_results/s5584_plume_title_hold/run*.game
  grep -n s5584 scratch/agent/SOAK-RESULTS.md
Control: each titled run has an ALIVE_AT_+120 line with first!=last origin; a run without it is null.
Outcomes:
  - Any crash -> read the backtrace in run*.game (main.cpp:10190 handler), name the writer of the si_addr=0x58 deref, fix the root cause (a real code change; satisfies the pivot).
  - 0/4 crash, alive120=4/4 -> plume thread closed (<1/16 over 40 boots); write BLOCKED.md asking the human: goal met, or new target?
  - Soak still absent/pending again -> do not re-escalate; ask in BLOCKED.md why the loop is not running soak_queue.
Do NOT re-run M6 holds (closed) or the renaming sweep (exhausted s5530).
HYPOTHESIS-ID: plume-title-extended-hold
