# NEXT (s7715)
HYPOTHESIS-ID: truth-census-coverage

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8.

s7714 landed tools/s7714_truth_census.py (0 unreviewed SPLIT, controls 5/5) but 164 of 810 multi-reader sites are unmodelled:
`python3 tools/s7714_truth_census.py --unmodelled | grep unmodelled | sed 's/.*: //' | sort | uniq -c` -> 93 "no call" (the s7711
site line has no `getenv("X")` token the tokenizer sees: escaped quotes in Python-embedded C, multi-line calls, macros), 19 passed
on, 17 foreign if-block, 9 no decision, 6 string pass-ons (C++17 if-init already done in s7714). One bounded change: fix the
window/tokenizer for the "no call" bucket (one pass, not per field), rerun, hand-read any NEW split (owner names -> fix like s7712-s7714, diag -> fix if src/ or REVIEWED with reason).
Hypotheses: H-clean (the newly modelled sites add no split), H-hidden (an unmodelled site hid a split; an owner name would matter
most). Controls stay 6/6; add one: a planted Python-embedded `getenv(\"ROGUESQ_PLANT\")` site must be modelled.
Stop rule: if after this pass the unmodelled residue is only string pass-ons / numeric / foreign if-blocks, CLOSE the class and take
the next G-rung or owner item from CURRENT-TRUTH Next steps (do not iterate the parser further).
Standing check after any src/ or lib/ change: `python3 tools/s7651_gate_sweep.py --jobs 2`. Owner defaults: never flip.
