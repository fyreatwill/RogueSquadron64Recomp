# NEXT (s7722)
HYPOTHESIS-ID: sweep-report-tools

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

s7721 closed sweep-scoring-audit (H-gap selected, small): enumerating every count token in all 196 captured gate outputs
(scratch/s7721/keys.tsv, 649 keys) found open-class words outside HOLLOW_KEYS; 19 were added (MISSING STALE RACE NEED_FIX
NEED_REVIEW UNMATCHED DEFECT UNGUARDED DISAGREE LEAK ORPHAN VIOLATION UNCOVERED FOLDED ERROR REGRESS BROKEN WRONG). Rescore
flagged 5 rc-0 gates, all already-classified, now HOLLOW_OK. New in-sweep control hol_s7721 (missing=3/race=1 -> HOLLOW).

Remaining hole: the 5 REPORT tools (s7031, s7082, s7083, s7210, s7441) are never scored at all — no exit path, no output scan.
Unit (offline, no game run):
1. For each REPORT tool: find the input it was last run on (grep PORTING-STATE for its name), run it once, save output to
   scratch/s7722/<tool>.out.
2. Decide per tool: H-report (pure table, nothing open by construction: keep REPORT with the reason) vs H-gate (the table carries
   an open-class row, e.g. unknown jal targets in s7082 or unexplained jump tables in s7083: give it a --check exit and an ARGS
   row so the sweep runs it as a gate, with a planted control).
3. Sweep ends 0 RED 0 HOLLOW, controls PASS.
Then the slug is done; take an owner item or G-rung per ITERATION 3c. Owner defaults: never flip.
