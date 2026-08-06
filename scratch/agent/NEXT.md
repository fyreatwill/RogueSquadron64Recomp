# NEXT work unit

## s398 recap (MAINTENANCE iteration)

Step 0 of ITERATION.md fired (`wc -c docs/CURRENT-TRUTH.md` = 60,119, over the 60,000 trigger). This
iteration compacted CURRENT-TRUTH: migrated the closed s389-397 M3 idiom-audit arc (items -239..-247)
to a new `docs/PROJECT-OVERVIEW.md` §14, tightened several other already-short sections (Overturned
conclusions, Dead ends, Method traps, the closed -226..-230/-231..-238 items), and fixed a stale
cross-reference. Result: 60,119 → 40,131 bytes, 653 → 452 lines, net -200 lines per
`git diff --numstat` — meets the ADVANCED maintenance threshold exactly. No experiment ran (Step 0
mandates maintenance-only). Full detail: PORTING-STATE Session 398.

Also folded in the queued soak verdict `s397_h1_8removal_verify2` (SOAK-RESULTS.md:
`20260806-120424 | rc=2 | 495s` → `NO_POSITIVE_CONTROL`, hangar scene not reached) — inconclusive,
doesn't change the safe-by-construction verdict on the s397 `S285_H1_8` deletion.

## Decision point for the NEXT (non-maintenance) iteration: unchanged from s397

The strategic question s397 raised is still open and this maintenance pass did not resolve it — it
only made the ledger legible again. Quoting s397's own recommendation (still current):

The `-0x25A4` family is fully closed. A systematic frequency-scan search for the next family found
nothing of comparable size. Continuing to look would need either:
(a) a genuinely different, more powerful discovery tool (e.g. a whole-function/CFG-aware dataflow pass
    that can trace a base register's origin across label/branch crossings — the s397 classifier
    explicitly could NOT do this, so it's a real gap, not proof nothing exists), or
(b) reconfirming with the human whether M3 crash work may leave pure-idiom-audit mode (the user
    directive explicitly reserves that decision for the human), or
(c) falling back to M4 (parked correctness items, listed in CURRENT-TRUTH's Goal stack, never picked
    up this whole session run) or reopening M5 (audio, closed, needs a new lead).

**Recommended action for the next non-maintenance iteration**: go BLOCKED and ask the human which of
(a)/(b)/(c) to pursue — OR, if avoiding BLOCKED, pick up an M4 item directly per Next-steps ordering.
The clearest concrete M4 candidate: CURRENT-TRUTH item -6, "confirm the s53 missing-func fix at
runtime" — `grep -c "\[missing-func\]"` should go 3→0, not load-gated, smallest-scoped M4 item
available. If picking that up, treat it as a genuine pivot (new HYPOTHESIS-ID) and update the "USER
DIRECTIVE" section in CURRENT-TRUTH to note the M3→M4 fallback explicitly, so a future session doesn't
silently re-litigate this decision.

**Do NOT** re-run the frequency-scan discovery method a second time without a materially different
technique — that would repeat an already-exhausted hypothesis for a predictable null result.

## Soak queue

Empty as of this session — no new soak was queued (maintenance iteration, no experiment run). Check
`scratch/agent/soak_queue/` at next session start in case the loop or a prior session queued something
not reflected here.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-next-family (unchanged from s397 — still 1 iteration old under this slug,
since s398 was a maintenance iteration, not an experiment iteration, and doesn't count against iron
rule 8's 3-consecutive-iteration budget). Next non-maintenance iteration should pivot the slug (new
discovery tool, or M4 fallback) or escalate to BLOCKED if no clear alternative presents itself.
