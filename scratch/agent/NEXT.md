# NEXT (s7694)
HYPOTHESIS-ID: post-g6c-owner-wait-s7694

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
G6c is owner-judged (s7691 sheet; s7692 re-holds 6/6 clean; s7693 all UB gates/censuses 26/26 rc 0 on the post-G6c tree).
Step 0: CURRENT-TRUTH is ~59.7 KB, right under the 60 KB trigger: if it crosses, do maintenance (migrate s7660-s7692 G6c
detail to PROJECT-OVERVIEW).
Otherwise take the first open standing-ladder rung (3c) not waiting on the owner; candidate: G5c freeze gate on the current
binary (one long owner-recipe STANDINS=1 dd4 run, present ring, no gap >250 ms outside loads) as a queued soak with
SOAK_NEEDS_IDLE. Hypotheses: H-clean (max_gap <250 ms as in s7692) vs H-stall (a G6c spawn burst adds a >250 ms frame ->
name the stalling call from the ring).
