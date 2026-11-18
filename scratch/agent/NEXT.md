# NEXT (s7561)
HYPOTHESIS-ID: regen-fidelity-drift

19b(b) CLOSED s7560: tools/regen_replay.sh scratch/s7560/replay -> "regen_replay: ok"; regen_verify 2607 same / 141 differ (= s7559 H-layout set).
Unit: 19b(d) census analyser precision (H-analyser rows found in s7560), one change, controls kept:
  1. tools/s7366_lockset_census.py: declared() treats function-local declarations and parameters with the same name as a
     file-scope container (26 s7560 H-safe-other rows: 17 `kind`, seq, spans, top, seen). Header claims locals are skipped.
  2. tools/s7363_hostarr_census.py: clamp ternary `p < N ? p : N-1` (s7535_ga_chk.cpp:57) classed B-HOST; add a CLAMP/TERN rule.
Hypotheses: H-scope-fixable (scope-aware lookup drops those rows; verdict rows become stale and can be pruned) vs H-collateral
(the scope fix also hides a real shared-container access: a global and a local with the same name in one function). Discriminator:
after the fix, re-run --check and diff the MIXED set: every row that disappears must be one of the 26 H-safe-other keys; any other
disappearance = H-collateral, revert that part. Controls: --selftest PASS + new selftest cases (local shadow -> not MIXED; global
accessed unlocked beside a same-name local in another function -> still MIXED); planted scratch/s7560/plant.cpp unbounded
subscript still OPEN; regen_replay gates still OPEN 0.
Then 19b(c): fold s7558_b40_ab when SOAK-RESULTS has it (voided 2/5 so far), then ask the owner about the B40 default.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
