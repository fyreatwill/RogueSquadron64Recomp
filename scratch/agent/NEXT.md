Single next work unit: read the s5581_plume_lle4_a / _b verdicts (SOAK-RESULTS.md tail + scratch/agent/soak_results/s5581_plume_lle4_{a,b}/summary), fold into ledger. FIRST check not a null: duration >100 s and summary has run-N last-origin lines with real origins.

Context: s5580 (LLE trio, no lldb) = 4/4 titles, 0 crash marks (213 s) -> LLE trio confirmed as the title-route ingredient (two sources: s5453/s5463 recipes + s5580). Cumulative N now 4; s5581 adds 8 -> N=12.

H1: a CRASHMARK/BREADCRUMB appears in a run -> read that run's .game log tail for the si_addr=0x58 backtrace context; then write an lldb variant (see done/s5463_plume_title8_a_*.sh for the attach pattern) and loop until it recurs, take the real backtrace, name the writer.
H2: 12/12 titles, no crash -> crash rate < ~1/12 under this recipe (kill-at-title ends each run early; the SIGSEGV may occur later in the title/hangar phase) -> extend the recipe to hold 60 s past title before kill.
H3: titles drop (<3/4) -> title-route flaky; diff against s5580.
Recipe hygiene: line 2 of every recipe = zsh re-exec guard.

HYPOTHESIS-ID: m6-title-plume-lldb
