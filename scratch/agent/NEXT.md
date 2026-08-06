# NEXT work unit

## s397 recap

Step 1: deleted the leftover `S285_H1_8` stale-register guard in `fixup_game_funcs.py`
(N64Recomp repo) — carry-over cleanup flagged s395/s396. Verified via regen+build (clean,
isolated diff per the fixup report). Soak verification was inconclusive (4 attempts, none
reached a same-run `[hangar-loop]` positive control, all for reasons unrelated to the change —
2 pre-existing log-storm pathologies, 1 too-short hold, 1 clean-but-title-stuck run matching
already-documented input-delivery flakiness) but the change is safe by construction (pure
deletion; the surviving guard `S395_SWEEP_1` at the same address is untouched and was already
soak-verified by s395). Full detail: PORTING-STATE Session 397.

Step 2 (this iteration's planned work unit, per prior NEXT.md): ran a codebase-wide frequency
scan for the next `-0x25A4`-scale idiom class, refined twice via a backward-tracing classifier.
**Result: zero candidates of comparable magnitude anywhere in the codebase.** The two
next-highest-frequency displacements (`-0x5824`, `-0x23A8`) are both 100% the mundane
`lui`-addressed static-global idiom, confirmed by direct source read — not pointer chases at
all. This is a legitimate, well-evidenced negative result per the prior NEXT.md's own
contingency clause. Full detail: PORTING-STATE Session 397, CURRENT-TRUTH item -247.

## Decision point for this iteration: M3 needs human input to proceed past pure idiom-audit mode

The `-0x25A4` family is fully closed. A systematic frequency-scan search for the next family
(the only method sanctioned by the user directive's "systematic idiom-class audit" framing)
found nothing of comparable size. Continuing to look would need either:
(a) a genuinely different, more powerful discovery tool (e.g. a whole-function/CFG-aware
    dataflow pass that can trace a base register's origin across label/branch crossings —
    s397's classifier explicitly could NOT do this, so it's a real gap, not proof nothing
    exists), or
(b) reconfirming with the human whether M3 crash work may leave pure-idiom-audit mode (the
    user directive explicitly reserves that decision for the human), or
(c) falling back to M4 (parked correctness items, listed in CURRENT-TRUTH's Goal stack,
    never picked up this whole session run) or reopening M5 (audio, closed, needs a new lead).

**Recommended action for this iteration**: go BLOCKED and ask the human which of (a)/(b)/(c) to
pursue — OR, if avoiding BLOCKED, pick up an M4 item directly per Next-steps ordering (Step 0's
"Next-steps ordering... should decide the next M3 item, or the loop should surface BLOCKED"
language implies falling back to normal Next-steps ordering is a sanctioned alternative to
BLOCKED when M3's own next item is exhausted). The clearest concrete M4 candidate: CURRENT-TRUTH
item -6, "confirm the s53 missing-func fix at runtime" — `grep -c "\[missing-func\]"` should go
3→0, not load-gated, smallest-scoped M4 item available. If picking that up, treat it as a
genuine pivot (new HYPOTHESIS-ID) and update the "USER DIRECTIVE" section in CURRENT-TRUTH to
note the M3→M4 fallback explicitly (with the reasoning above), so a future session doesn't
silently re-litigate this decision.

**Do NOT** re-run the same frequency-scan discovery method a second time without a materially
different technique — that would be the 2nd consecutive iteration on a hypothesis already shown
exhausted, wasting a soak/session cycle for a predictable null result.

## Soak queue

`scratch/agent/soak_queue/s397_h1_8removal_verify2.sh` is queued: default `run_s327waitpump.sh`
env (RS_FREE_WALK/RS_MALLOC_WALK disabled, `HOLD_S=280` to match s395's successful recipe
timing) — a genuine attempt at a positive-control confirmation of the s397 cleanup that this
session didn't get. Read its verdict in SOAK-RESULTS.md next session and fold it into the s397
entry in PORTING-STATE.md (append, don't rewrite) whichever way it lands.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-next-family (iteration 1 of this slug closed s397 with a negative
result; per iron rule 8, do not re-run the same discovery method a 2nd time under this slug —
either pivot the slug (new discovery tool, or M4 fallback) or escalate to BLOCKED next
iteration if no clear alternative presents itself).
