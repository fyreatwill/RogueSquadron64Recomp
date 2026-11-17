# NEXT (s7534)
HYPOTHESIS-ID: ct-maintenance

`wc -c < docs/CURRENT-TRUTH.md` = 60,142 B after s7533 (>60000) -> s7534 is a MAINTENANCE iteration (ITERATION.md Step 0):
compact CURRENT-TRUTH toward ~35 KB (migrate the closed class-audit ledger, Next steps item 21 FJ..FZ, to PROJECT-OVERVIEW.md;
prune superseded/closed items; one monotonic backlog numbering; refresh the headline). No experiments.

Fold first (any iteration): SOAK-RESULTS line for s7533_fz_levels; score with
`python3 tools/s7533_fz_score.py scratch/s7533_fz_levels l1 l7 l10 l12` (each arm: clamps>2, control=1, cas_fail=0).
cas_fail>0 on any arm = a guest store the pre-s7533 clamp would have lost (the fix already prevents it; record which level).

After maintenance: the class-audit series FJ..FZ is complete. Next rung per ITERATION.md 3c: a new idiom-class audit
(candidate: host-thread READ-modify decisions on guest bytes beyond writes, e.g. render-context / dpc_bridge decisions taken on a
guest byte the guest changes in the same window) or the G5 rename sweep.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
